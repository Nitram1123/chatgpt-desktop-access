"""Audit source metadata and a built NVDA add-on archive."""

import argparse
import ast
import re
import zipfile
from pathlib import Path

from build_addon import packageData, packageFiles


FORBIDDEN_SOURCE = (
	"import sqlite3", "import requests", "import numpy", "import yaml",
	"gesture=", '"kb:enter"', "script_enter", "script_openAddFilesAndMore",
	"script_openModelSelector", "script_openChangePermissions",
	"script_openEmbeddedBrowserNavigator", "script_readEmbeddedBrowserPageSummary",
	"script_showEmbeddedBrowserSnapshot", "script_openEmbeddedBrowserExternally",
	"script_returnToChatGPTPrompt", "script_showEmbeddedBrowserHelp",
	"class CodexEmbeddedBrowserOverlay",
)


def manifestVersionMatches(text, version):
	"""Match a manifest version from either LF or CRLF archive content."""
	return bool(re.search(rf"(?m)^version = {re.escape(version)}\r?$", text))


def audit(projectRoot, packagePath, version):
	projectRoot = Path(projectRoot).resolve()
	packagePath = Path(packagePath).resolve()
	assert packagePath.name == f"chatGPTDesktopAccess-{version}.nvda-addon", "public package filename mismatch"
	pythonPaths = tuple(
		path for path in projectRoot.rglob("*.py")
		if "__pycache__" not in path.parts
		and "outputs" not in path.relative_to(projectRoot).parts
	)
	for path in pythonPaths:
		ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
	plugin = (projectRoot / "globalPlugins/codexStatusAnnouncer/__init__.py").read_text(encoding="utf-8")
	core = (projectRoot / "globalPlugins/codexStatusAnnouncer/core.py").read_text(encoding="utf-8")
	manifest = (projectRoot / "manifest.ini").read_text(encoding="utf-8")
	build = (projectRoot / "build.ps1").read_text(encoding="utf-8")
	changelog = (projectRoot / "changelog.md").read_text(encoding="utf-8")
	assert f'ADDON_VERSION = "{version}"' in plugin, "source version mismatch"
	assert re.search(r"(?m)^import re$", plugin), "regular-expression runtime dependency is not imported"
	assert manifestVersionMatches(manifest, version), "manifest version mismatch"
	assert re.search(r'(?m)^author = "?.+<[^<>\s]+@[^<>\s]+>"?$', manifest), "manifest author email missing"
	assert re.search(r"(?m)^url = https://.+$", manifest), "manifest HTTPS homepage missing"
	assert re.search(r"(?m)^docFileName = readme\.md$", manifest), "manifest documentation field missing"
	assert re.search(r"(?m)^minimumNVDAVersion = 2023\.1\.0$", manifest), "minimum stable NVDA compatibility mismatch"
	assert re.search(r"(?m)^lastTestedNVDAVersion = 2026\.3\.0$", manifest), "tested stable NVDA compatibility mismatch"
	assert re.search(r"(?m)^updateChannel = None$", manifest), "stable package update channel mismatch"
	assert f'[string]$Version = "{version}"' in build, "build default version mismatch"
	assert f"## {version}" in changelog, "changelog version heading missing"
	assert "Adds assignable focus- and browse-mode actions" not in manifest, "stale gesture changelog in manifest"
	if version in {"2026.2.11", "2026.2.12"}:
		assert "Attach files or connect apps" in manifest, "current attachment workaround missing from manifest changelog"
		assert "one-time speech and Braille hint" not in manifest, "removed attachment hint remains in manifest changelog"
	chatGPTAppModule = (projectRoot / "appModules/chatgpt.py").read_text(encoding="utf-8")
	gesturePairs = re.findall(r'"kb:control\+([0-9])": "([A-Za-z0-9]+ChatMessage)"', chatGPTAppModule)
	assert len(gesturePairs) == 10, "expected ten configurable recent-message default gestures"
	assert len({digit for digit, scriptName in gesturePairs}) == 10, "duplicate recent-message gesture"
	assert len({scriptName for digit, scriptName in gesturePairs}) == 10, "recent-message actions must be independent"
	assert '"kb:NVDA+alt+v": "toggleVoiceMode"' in chatGPTAppModule, "voice-mode default gesture missing"
	assert '"kb:NVDA+alt+m": "toggleMicrophoneMute"' not in chatGPTAppModule, "conflicting microphone default gesture remains"
	assert "def script_toggleMicrophoneMute(self, gesture):" in chatGPTAppModule, "assignable microphone action missing"
	assert "def script_toggleConversationMode(self, gesture):" in chatGPTAppModule, "assignable mode-switch action missing"
	assert '"kb:NVDA+`": "toggleConversationMode"' in chatGPTAppModule, "mode-switch default gesture missing"
	assert '_runToolkitCommand("_openConversationModeSelector")' in chatGPTAppModule, "mode-selector action is not connected"
	assert "class AppModule(appModuleHandler.AppModule)" in chatGPTAppModule, "commands are not app scoped"
	assert 'APP_MODULE_ALIASES = (("codex", "chatgpt"),)' in plugin, "Codex app-module alias missing"
	assert "appModuleHandler.registerExecutableWithAppModule(executableName, appModuleName)" in plugin, "Codex app-module alias is not registered"
	assert "appModuleHandler.unregisterExecutable(executableName)" in plugin, "Codex app-module alias is not unregistered"
	assert not (projectRoot / "appModules/codex.py").exists(), "redundant Codex app-module shim remains"
	assert "__gestures" not in plugin, "application commands must not be bound by the global plugin"
	assert not re.search(r"^\s*def script_\w+\(", plugin, re.MULTILINE), "commands must be app scoped"
	assert "gesture.send()" not in plugin + chatGPTAppModule, "application commands must not emulate keys outside ChatGPT"
	assert "def _migrateApplicationGestureMappings():" in plugin, "existing gesture assignments are not migrated"
	assert "_conversationScanInfo(self._buffer)" in plugin, "unbounded conversation polling returned"
	assert "Unrelated global mappings are never moved." in changelog, "gesture migration is missing from changelog"
	assert plugin.count('label=_("&Open usage and credits")') == 1, "combined Support usage control missing"
	assert "&Check Codex usage statistics" not in plugin, "obsolete Check usage control remains"
	assert "&Buy Codex usage credits" not in plugin, "obsolete Buy credits control remains"
	assert chatGPTAppModule.count('@script(description=_("Open ChatGPT usage and credits"))') == 1, "combined usage action missing"
	assert "def script_openUsageCredits(self, gesture):" in chatGPTAppModule, "legacy credits gesture compatibility missing"
	assert '"announceEmbeddedBrowserProgress": "boolean(default=True)"' in plugin, "browser load setting missing"
	assert "BROWSER_LOAD_SETTLE_MILLISECONDS = 1500" in plugin, "browser settle timer missing"
	assert "BROWSER_BUSY_FALLBACK_MILLISECONDS = 30000" in plugin, "browser busy fallback missing"
	assert 'self._embeddedBrowserNotice(_("Loading page"))' in plugin, "browser load-start message missing"
	assert 'self._embeddedBrowserNotice(_("Loading complete"))' in plugin, "browser load-complete message missing"
	assert "def event_stateChange(self, obj, nextHandler):" in plugin, "native browser busy-state event missing"
	eventHooks = plugin[plugin.index("\tdef event_gainFocus"):]
	assert "_startEmbeddedBrowserScan" not in eventHooks, "normal browser events can start a page scan"
	assert "_rememberEmbeddedBrowserObject" not in eventHooks, "normal browser events retain obsolete navigator objects"
	assert "codexHistorySourceSignature(codexRoot)" in plugin, "Codex history metadata is reread every scan"
	assert 'self._chatHistoryCaches = {"chatgpt": (), "codex": ()}' in plugin, "mode-specific recent history missing"
	assert 'self._archivedChatHistoryCaches = {"chatgpt": (), "codex": ()}' in plugin, "mode-specific archived history missing"
	assert "fieldMode = conversationModeFromSwitchControl(" in plugin, "authoritative mode-switch control is not scanned"
	assert "mode = _switchControlMode(obj)" in plugin, "mode-control event does not use selector semantics"
	assert "handler.MTAThreadQueue.put_nowait(probe)" in plugin, "mode verification can block NVDA's main thread"
	assert 'self._queueConversationModeProbe("requested mode selector", openSelector=True)' in plugin, "mode selector does not use the UI Automation worker"
	assert "pattern.QueryInterface(UIAHandler.IUIAutomationExpandCollapsePattern)" in plugin, "native mode-menu Expand pattern missing"
	assert "control.SetFocus()" in plugin, "native mode selector is not focused before opening"
	assert "def _selectConversationModeMenuItem" not in plugin, "mode selector still selects a menu item automatically"
	assert "_pendingConversationModeSwitch" not in plugin, "automatic mode-switch state is still present"
	assert "pendingProbe != activationProbe" in plugin, "native mode events can invalidate a requested selector open"
	assert "def _eventBelongsToRetainedConversationBuffer" in plugin, "stale mode-control event guard missing"
	assert "if not self._eventBelongsToRetainedConversationBuffer(obj):" in plugin, "mode controls can revive a closed session"
	assert "for candidate in (root, obj):" in plugin, "popup handles can override the conversation window"
	assert "if not self._conversationWindowIsAvailable(candidateWindowHandle):" in plugin, "closed buffers can reattach"
	assert "pollTimer = self._timer" in plugin, "poll callbacks do not retain their owning timer"
	assert "if self._timer is pollTimer and pollTimer is not None:" in plugin, "poll callbacks can overwrite an earlier scheduled timer"
	assert "def _fallbackExternalWindowHandle(self, excludedProcessId):" in plugin, "closed-window fallback focus is missing"
	assert "winUser.GW_HWNDNEXT" in plugin, "fallback focus does not inspect remaining app windows"
	assert "processId != excludedProcessId" in plugin, "fallback focus can reactivate the closed ChatGPT process"
	assert "self._recoverFocusAfterConversationClose(closedProcessId)" in plugin, "closed process is not excluded from focus recovery"
	assert "now - self._lastRejectedBufferLogAt >= 30.0" in plugin, "closed-buffer diagnostics are not rate limited"
	assert "logSnapshot, self._lastDeferredHistoryLog" in plugin, "history deferral diagnostics are not rate limited"
	assert "protectBrailleReading=False" in plugin, "explicit mode-switch feedback can disruptively disappear in browse mode"
	assert 'self._queueConversationModeProbe("history mode verification")' in plugin, "history does not verify its mode"
	assert "if not self._conversationModeObserved:" in plugin, "unverified history mode is trusted"
	assert "self._conversationModeObserved = True" in plugin, "authoritative mode precedence is not retained"
	assert "CHAT_HISTORY_MODE_SETTLE_SECONDS = 0.75" in plugin, "mode-specific history settle delay is missing"
	assert "CHAT_HISTORY_SNAPSHOT_CONFIRM_SECONDS = 0.25" in plugin, "history snapshot confirmation is missing"
	assert "chatHistorySnapshotDecision(" in plugin, "settled history decision is not applied"
	assert "loadActiveCodexThreadTitles(codexRoot)" in plugin, "unified Recents list is not classified with the Codex index"
	assert "self._modeSpecificRecentChatTitles(scanMode, recentSnapshot)" in plugin, "mixed recent entries can reach a mode cache"
	assert "CHAT_HISTORY_EXPANSION_MAX_PAGES = 20" in plugin, "recent history expansion is not bounded"
	assert 'button = self._recentHistoryShowMoreButton(mode)' in plugin, "native Recents expansion is missing"
	assert 'self._showChatHistoryDialog(mode)' in plugin, "expanded history is not presented"
	assert "if not self._chatHistoryCacheCurrent.get(mode, False):" in plugin, "unsettled chat history can still open"
	assert 'if source == "archived" and mode == "codex":' in plugin, "archived history source is not mode-specific"
	assert plugin.count("not isChatHistoryInterfaceText(") == 2, "history interface controls are not filtered from both lists"
	assert 'usageNotice = usageLimitNotice(" ".join(usageEvidence), _)' in plugin, "missed usage-alert events have no buffer fallback"
	assert "isResponseCompletionMarkerText(plainText)" in plugin, "plain response-completion text is not scanned"
	assert "responseCompletionScanMarker(" in plugin, "completed-response scans do not distinguish new answers"
	assert 'r"\\b(?P<percent>\\d{1,3}(?:\\.\\d+)?)\\s*%\\s*usage\\s+remaining"' in core, "zero-percent usage banner is not recognized"
	for interfaceLabel in ("add credits", "upgrade", "update", "dismiss usage alert", "usage consumed"):
		assert f'"{interfaceLabel}"' in core, f"history account-control filter missing: {interfaceLabel}"
	assert r're.fullmatch(r"\d{1,3}% usage remaining", text)' in core, "usage-alert history boundary missing"
	assert 'if not recentsSeen and plainText.casefold() == "recents":' in plugin, "recent history region can restart inside a conversation"
	assert plugin.count("inRecents = inArchived = False") >= 3, "conversation boundaries do not close both history regions"
	assert 'title=_("{agent} chat history").format(agent=agentName)' in (
		projectRoot / "globalPlugins/codexStatusAnnouncer/chatHistoryDialog.py"
	).read_text(encoding="utf-8"), "history dialog does not identify the active mode"
	assert re.search(r'(?m)^summary = "ChatGPT Desktop Access for NVDA"$', manifest), "public display name mismatch"
	assert re.search(r"(?m)^url = https://github\.com/jcoffin1/chatgpt-desktop-access$", manifest), "public repository mismatch"
	assert (projectRoot / "locale/chatGPTDesktopAccess.pot").is_file(), "translation template missing"
	packagedPaths = tuple(packageFiles(projectRoot))
	combinedSource = "\n".join(path.read_text(encoding="utf-8") for path in packagedPaths if path.suffix == ".py")
	for forbidden in FORBIDDEN_SOURCE:
		assert forbidden not in combinedSource, f"forbidden source found: {forbidden}"
	expected = tuple(path.relative_to(projectRoot).as_posix() for path in packagedPaths)
	with zipfile.ZipFile(packagePath) as archive:
		names = tuple(archive.namelist())
		assert archive.testzip() is None, "archive CRC failure"
		assert len(names) == len(set(names)), "duplicate archive entries"
		for required in ("manifest.ini", "readme.md", "changelog.md", "LICENSE.txt"):
			assert required in names, f"required package file missing: {required}"
		assert not any(name.endswith(".pot") for name in names), "developer translation template packaged"
		assert not any(
			name.startswith("globalPlugins/codexStatusAnnouncer/sounds/") and name.count("/") == 3
			for name in names
		), "obsolete un-tiered sound packaged"
		assert names == expected, "archive layout or ordering mismatch"
		for path in packagedPaths:
			archiveName = path.relative_to(projectRoot).as_posix()
			assert archive.read(archiveName) == packageData(path), f"stale packaged content: {archiveName}"
		assert not any("__pycache__" in name or name.endswith((".pyc", ".pyo")) for name in names), "cache file packaged"
		packagedManifest = archive.read("manifest.ini").decode("utf-8")
		assert manifestVersionMatches(packagedManifest, version), "packaged manifest mismatch"
		assert sum(name.endswith(".wav") for name in names) == 51, "sound inventory mismatch"
	return len(pythonPaths), len(expected)


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("package")
	parser.add_argument("version")
	args = parser.parse_args()
	root = Path(__file__).resolve().parents[1]
	pythonCount, entryCount = audit(root, args.package, args.version)
	print(f"Audit valid: {pythonCount} Python files; {entryCount} archive entries")
