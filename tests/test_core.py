import importlib.util
import ast
from collections import deque
import gettext
import json
import math
import os
from pathlib import Path
import re
import struct
import sys
import tempfile
import unittest
import wave


CORE_PATH = Path(__file__).parents[1] / "globalPlugins" / "codexStatusAnnouncer" / "core.py"
PROJECT_ROOT = Path(__file__).parents[1]
PLUGIN_PATH = CORE_PATH.parent / "__init__.py"
CHAT_DIALOG_PATH = CORE_PATH.parent / "chatHistoryDialog.py"
SOUND_OUTPUT_PATH = CORE_PATH.parent / "soundOutput.py"
CLICK_GENERATOR_PATH = PROJECT_ROOT / "tools" / "generate_click_sounds.py"
ACCESSIBILITY_FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "chatgpt_accessibility_snapshots.json"
ADDON_STORE_METADATA_PATH = PROJECT_ROOT / "tools" / "addon_store_metadata.py"
AUDIT_PATH = PROJECT_ROOT / "tools" / "audit_addon.py"
BUILD_PATH = PROJECT_ROOT / "tools" / "build_addon.py"
RELEASE_WORKFLOW_PATH = PROJECT_ROOT / ".github" / "workflows" / "release.yml"
TRANSLATION_TEMPLATE_PATH = PROJECT_ROOT / "locale" / "chatGPTDesktopAccess.pot"
BROWSER_ACCESS_PATH = CORE_PATH.parent / "browserAccess.py"
CHATGPT_APP_MODULE_PATH = PROJECT_ROOT / "appModules" / "chatgpt.py"
SPEC = importlib.util.spec_from_file_location("codex_status_core", CORE_PATH)
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)
STORE_SPEC = importlib.util.spec_from_file_location("codex_store_metadata", ADDON_STORE_METADATA_PATH)
storeMetadata = importlib.util.module_from_spec(STORE_SPEC)
STORE_SPEC.loader.exec_module(storeMetadata)
BUILD_SPEC = importlib.util.spec_from_file_location("codex_package_builder", BUILD_PATH)
packageBuilder = importlib.util.module_from_spec(BUILD_SPEC)
BUILD_SPEC.loader.exec_module(packageBuilder)
BROWSER_ACCESS_SPEC = importlib.util.spec_from_file_location("codex_browser_access", BROWSER_ACCESS_PATH)
browserAccess = importlib.util.module_from_spec(BROWSER_ACCESS_SPEC)
BROWSER_ACCESS_SPEC.loader.exec_module(browserAccess)
AnnouncementHistory = core.AnnouncementHistory
ChatMessageAccumulator = core.ChatMessageAccumulator
ChatMessageFieldCollector = core.ChatMessageFieldCollector
firstStatusLabel = core.firstStatusLabel
statusMessage = core.statusMessage
brailleStatusMessage = core.brailleStatusMessage
statusDetails = core.statusDetails
redactSensitive = core.redactSensitive
elapsedSeconds = core.elapsedSeconds
formatElapsedDuration = core.formatElapsedDuration
completedTextDelta = core.completedTextDelta
outputActions = core.outputActions
tonePattern = core.tonePattern
nextBusyState = core.nextBusyState
pollDelay = core.pollDelay
bufferInspectionDue = core.bufferInspectionDue
conversationWindowShouldDetach = core.conversationWindowShouldDetach
brailleTypingGestureCommitsText = core.brailleTypingGestureCommitsText
isBrailleTypingGestureIdentifier = core.isBrailleTypingGestureIdentifier
isPromptSubmissionGestureIdentifier = core.isPromptSubmissionGestureIdentifier
isConversationNavigationGestureIdentifier = core.isConversationNavigationGestureIdentifier
promptSubmissionGestureShouldStart = core.promptSubmissionGestureShouldStart
shouldPreserveBrailleComposition = core.shouldPreserveBrailleComposition
coalescedPollDelay = core.coalescedPollDelay
shouldReplaceScheduledPoll = core.shouldReplaceScheduledPoll
shouldPlayContinuousWorkingClick = core.shouldPlayContinuousWorkingClick
shouldSuppressRoutineBraille = core.shouldSuppressRoutineBraille
shouldSuppressNativeConversationUpdate = core.shouldSuppressNativeConversationUpdate
focusStateTransition = core.focusStateTransition
attachmentMenuItemLabel = core.attachmentMenuItemLabel
isCodexPromptLabel = core.isCodexPromptLabel
userMessageNumber = core.userMessageNumber
userMessageSubmissionTransition = core.userMessageSubmissionTransition
confirmedUserMessageSubmission = core.confirmedUserMessageSubmission
isStopControlLabel = core.isStopControlLabel
stopControlTransition = core.stopControlTransition
shouldSuppressDuplicate = core.shouldSuppressDuplicate
shouldLogDiagnosticSnapshot = core.shouldLogDiagnosticSnapshot
responseCompletionTransition = core.responseCompletionTransition
isResponseCompletionMarkerText = core.isResponseCompletionMarkerText
responseCompletionScanMarker = core.responseCompletionScanMarker
shouldFinalizeResponseCompletion = core.shouldFinalizeResponseCompletion
isTaskCompletionLabel = core.isTaskCompletionLabel
intermediateCompletionCategory = core.intermediateCompletionCategory
isKnownNonStatusButton = core.isKnownNonStatusButton
isChatHistoryInterfaceText = core.isChatHistoryInterfaceText
isChatHistoryConversationBoundary = core.isChatHistoryConversationBoundary
soundKey = core.soundKey
categoryOutputActions = core.categoryOutputActions
announcementPriority = core.announcementPriority
changelogForDisplay = core.changelogForDisplay
viewerTitleMatches = core.viewerTitleMatches
previewSelection = core.previewSelection
formatCustomAnnouncement = core.formatCustomAnnouncement
loadArchivedThreads = core.loadArchivedThreads
loadActiveCodexThreadTitles = core.loadActiveCodexThreadTitles
uniqueThreadLabels = core.uniqueThreadLabels
semanticStatusKey = core.semanticStatusKey
shouldSuppressSemanticDuplicate = core.shouldSuppressSemanticDuplicate
duplicateChannelActions = core.duplicateChannelActions
formatCommandSpeech = core.formatCommandSpeech
promptControlKind = core.promptControlKind
repairConfigurationValues = core.repairConfigurationValues
mergeSupportedAppNames = core.mergeSupportedAppNames
conversationModeFromDocumentNames = core.conversationModeFromDocumentNames
conversationModeFromSwitchLabel = core.conversationModeFromSwitchLabel
conversationModeFromSwitchControl = core.conversationModeFromSwitchControl
chatHistorySnapshotDecision = core.chatHistorySnapshotDecision
modeSpecificRecentChatTitles = core.modeSpecificRecentChatTitles
chatTitleMatches = core.chatTitleMatches
chatActionMatches = core.chatActionMatches
voiceControlKind = core.voiceControlKind
chatMessageShortcutIndex = core.chatMessageShortcutIndex
chatMessagesFromTokens = core.chatMessagesFromTokens
isChatMessageTrailingUiText = core.isChatMessageTrailingUiText
codexThreadUrl = core.codexThreadUrl
codexHistorySourceSignature = core.codexHistorySourceSignature
isChatOptionsLabel = core.isChatOptionsLabel
isPermissionDecisionLabel = core.isPermissionDecisionLabel
isPermissionPromptText = core.isPermissionPromptText
usageLimitNotice = core.usageLimitNotice
pluginInstallProgress = core.pluginInstallProgress
currentActivitySummary = core.currentActivitySummary
backgroundActivityName = core.backgroundActivityName
looksLikeCodexConversation = core.looksLikeCodexConversation
looksLikeBlankCodexConversation = core.looksLikeBlankCodexConversation
pendingChatTitle = core.pendingChatTitle
pluginProgressBusyTransition = core.pluginProgressBusyTransition
supersedesResponseCompletionCandidate = core.supersedesResponseCompletionCandidate


class StatusMessageTests(unittest.TestCase):
	def test_codex_history_source_signature_and_runtime_cache_avoid_repeated_disk_reads(self):
		with tempfile.TemporaryDirectory() as temporaryDirectory:
			root = Path(temporaryDirectory)
			missingSignature = codexHistorySourceSignature(root)
			indexPath = root / "session_index.jsonl"
			indexPath.write_text("first\n", encoding="utf-8")
			firstSignature = codexHistorySourceSignature(root)
			self.assertNotEqual(missingSignature, firstSignature)
			with indexPath.open("a", encoding="utf-8") as indexFile:
				indexFile.write("second\n")
			secondSignature = codexHistorySourceSignature(root)
			self.assertNotEqual(firstSignature, secondSignature)
			(root / "archived_sessions").mkdir()
			self.assertNotEqual(secondSignature, codexHistorySourceSignature(root))

		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = {
			node.name: node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in {
				"_activeCodexThreadTitles", "_modeSpecificRecentChatTitles",
			}
		}
		sourceSignature = [1]
		diskReads = []
		infoLogs = []
		namespace = {
			"Path": Path, "os": os,
			"codexHistorySourceSignature": lambda root: sourceSignature[0],
			"loadActiveCodexThreadTitles": lambda root: diskReads.append(root) or ("Codex task",),
			"modeSpecificRecentChatTitles": modeSpecificRecentChatTitles,
			"log": type("Log", (), {
				"info": staticmethod(lambda *args, **kwargs: infoLogs.append(args)),
				"debugWarning": staticmethod(lambda *args, **kwargs: None),
			}),
		}
		exec(compile(ast.Module(body=list(methods.values()), type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class CacheSubject:
			_activeCodexTitlesCache = ()
			_activeCodexTitlesSourceSignature = None
		cacheSubject = CacheSubject()
		self.assertEqual(("Codex task",), namespace["_activeCodexThreadTitles"](cacheSubject))
		self.assertEqual(("Codex task",), namespace["_activeCodexThreadTitles"](cacheSubject))
		self.assertEqual(1, len(diskReads))
		sourceSignature[0] = 2
		namespace["_activeCodexThreadTitles"](cacheSubject)
		self.assertEqual(2, len(diskReads))

		class ClassificationSubject:
			def __init__(self): self._recentClassificationSummaries = {"chatgpt": None, "codex": None}
			def _activeCodexThreadTitles(self): return ("Codex task",)
		classificationSubject = ClassificationSubject()
		logCount = len(infoLogs)
		namespace["_modeSpecificRecentChatTitles"](
			classificationSubject, "chatgpt", ("ChatGPT chat", "Codex task"),
		)
		namespace["_modeSpecificRecentChatTitles"](
			classificationSubject, "chatgpt", ("ChatGPT chat", "Codex task"),
		)
		self.assertEqual(logCount + 1, len(infoLogs))

	def test_embedded_browser_accessibility_classification_is_conservative(self):
		self.assertTrue(browserAccess.isEmbeddedBrowserContainerText("Browser", ""))
		self.assertTrue(browserAccess.isEmbeddedBrowserContainerText("", "WebView preview"))
		self.assertFalse(browserAccess.isEmbeddedBrowserContainerText("Codex", "main conversation"))
		self.assertTrue(browserAccess.isEmbeddedBrowserContainerRole("pane"))
		self.assertFalse(browserAccess.isEmbeddedBrowserContainerRole("button"))
		self.assertFalse(browserAccess.isEmbeddedBrowserContainerRole("menu"))
		self.assertFalse(browserAccess.isEmbeddedBrowserDocumentStructure("menu", "document"))
		self.assertTrue(browserAccess.isEmbeddedBrowserDocumentStructure("heading", "document", "document"))
		self.assertEqual("Example page", browserAccess.embeddedBrowserTitle("  Example   page  "))
		self.assertEqual("", browserAccess.embeddedBrowserTitle("Embedded browser"))

	def test_embedded_browser_uses_native_navigation_without_a_command_layer(self):
		plugin = PLUGIN_PATH.read_text(encoding="utf-8")
		appModule = CHATGPT_APP_MODULE_PATH.read_text(encoding="utf-8")
		for command in (
			"openEmbeddedBrowserNavigator", "readEmbeddedBrowserPageSummary",
			"showEmbeddedBrowserSnapshot", "openEmbeddedBrowserExternally",
			"returnToChatGPTPrompt", "showEmbeddedBrowserHelp",
		):
			self.assertNotIn(f"script_{command}", plugin + appModule)
		self.assertNotIn("class CodexEmbeddedBrowserOverlay", plugin)
		self.assertNotIn('"enhanceEmbeddedBrowser"', plugin)
		self.assertNotIn('"rememberEmbeddedBrowserLocations":', plugin)
		self.assertNotIn('"announceEmbeddedBrowserFocus"', plugin)
		self.assertNotIn('"announceEmbeddedBrowserTitles"', plugin)
		self.assertIn('"announceEmbeddedBrowserProgress": "boolean(default=True)"', plugin)
		self.assertIn("BROWSER_LOAD_SETTLE_MILLISECONDS = 1500", plugin)
		self.assertIn("BROWSER_BUSY_FALLBACK_MILLISECONDS = 30000", plugin)
		self.assertIn('self._embeddedBrowserNotice(_("Loading page"))', plugin)
		self.assertIn('self._embeddedBrowserNotice(_("Loading complete"))', plugin)
		eventHooks = plugin[plugin.index("\tdef event_gainFocus"):]
		self.assertNotIn("_startEmbeddedBrowserScan", eventHooks)
		self.assertNotIn("_rememberEmbeddedBrowserObject", eventHooks)

	def test_embedded_browser_loading_announces_once_and_completes(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = {
			node.name: node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in {
				"_scheduleEmbeddedBrowserLoadComplete", "_startEmbeddedBrowserLoading",
				"_completeEmbeddedBrowserLoading", "_resetEmbeddedBrowserProgress",
			}
		}
		class Timer:
			def __init__(self): self.stopped = False
			def Stop(self): self.stopped = True
		class Wx:
			calls = []
			@classmethod
			def CallLater(cls, delay, callback, *args):
				cls.calls.append((delay, callback, args))
				return Timer()
		namespace = {
			"wx": Wx,
			"BROWSER_LOAD_SETTLE_MILLISECONDS": 1500,
			"BROWSER_BUSY_FALLBACK_MILLISECONDS": 30000,
			"_settings": lambda: {"announceEmbeddedBrowserProgress": True},
			"_": lambda text: text,
			"log": type("Log", (), {"info": staticmethod(lambda *args, **kwargs: None)}),
		}
		exec(compile(ast.Module(body=list(methods.values()), type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			def __init__(self):
				self._embeddedBrowserLoadTimer = None
				self._embeddedBrowserLoadGeneration = 0
				self._embeddedBrowserLoadingPercent = None
				self._embeddedBrowserLoading = False
				self._embeddedBrowserBusySeen = False
				self._embeddedBrowserLoadIdentity = ""
				self._embeddedBrowserCompletedIdentity = ""
				self._embeddedBrowserPageTitle = ""
				self._embeddedBrowserProgressBuckets = {}
				self.notices = []
			def _embeddedBrowserNotice(self, message): self.notices.append(message)
			def _scheduleEmbeddedBrowserLoadComplete(self, busy=False):
				return namespace["_scheduleEmbeddedBrowserLoadComplete"](self, busy)
			def _completeEmbeddedBrowserLoading(self, generation=None):
				return namespace["_completeEmbeddedBrowserLoading"](self, generation)
		subject = Subject()
		namespace["_startEmbeddedBrowserLoading"](subject, "page:one", "Example", True, False)
		namespace["_startEmbeddedBrowserLoading"](subject, "page:one", "Example", True, False)
		self.assertEqual(["Loading page"], subject.notices)
		self.assertEqual(1500, Wx.calls[-1][0])
		namespace["_completeEmbeddedBrowserLoading"](subject)
		self.assertEqual(["Loading page", "Loading complete"], subject.notices)
		self.assertFalse(subject._embeddedBrowserLoading)
		namespace["_startEmbeddedBrowserLoading"](subject, "page:two", "Slow", True, True)
		self.assertEqual(30000, Wx.calls[-1][0])
		namespace["_resetEmbeddedBrowserProgress"](subject)
		self.assertFalse(subject._embeddedBrowserLoading)
		self.assertEqual("", subject._embeddedBrowserLoadIdentity)

	def test_embedded_browser_object_rejects_browser_menu_and_accepts_nested_document(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		functions = [
			node for node in tree.body
			if isinstance(node, ast.FunctionDef) and node.name in {"_roleName", "_isEmbeddedBrowserObject"}
		]
		namespace = {
			"_isChatGPTObject": lambda obj: True,
			"_isCodexPromptObject": lambda obj: False,
			"promptControlKind": lambda name: "",
			"isEmbeddedBrowserContainerText": browserAccess.isEmbeddedBrowserContainerText,
			"isEmbeddedBrowserContainerRole": browserAccess.isEmbeddedBrowserContainerRole,
			"isEmbeddedBrowserDocumentStructure": browserAccess.isEmbeddedBrowserDocumentStructure,
		}
		exec(compile(ast.Module(body=functions, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Object:
			def __init__(self, role, name, parent=None):
				self.role = role
				self.name = name
				self.parent = parent
			@property
			def description(self):
				raise AssertionError("browser focus detection queried UIA help text")
		outerDocument = Object("document", "ChatGPT")
		browserMenu = Object("menu", "Browser", outerDocument)
		self.assertFalse(namespace["_isEmbeddedBrowserObject"](browserMenu))
		innerDocument = Object("document", "Sign in to GitHub · GitHub", outerDocument)
		heading = Object("heading", "Sign in to GitHub", innerDocument)
		self.assertTrue(namespace["_isEmbeddedBrowserObject"](heading))
		self.assertFalse(namespace["_isEmbeddedBrowserObject"](browserMenu))

	def test_embedded_browser_detection_prefilters_prompt_and_status_objects(self):
		plugin = PLUGIN_PATH.read_text(encoding="utf-8")
		self.assertIn('if _isCodexPromptObject(obj) or promptControlKind(getattr(obj, "name", "")):', plugin)
		self.assertIn("obj._codexEmbeddedBrowserDetected = False", plugin)
		chooseStart = plugin.index("\tdef chooseNVDAObjectOverlayClasses(self, obj, clsList):")
		chooseEnd = plugin.index("\n\tdef __init__(self):", chooseStart)
		chooseBody = plugin[chooseStart:chooseEnd]
		self.assertIn("promptControlKind(", chooseBody)
		self.assertNotIn("_isEmbeddedBrowserObject(", chooseBody)
		self.assertNotIn("CodexEmbeddedBrowserOverlay", chooseBody)

	def test_prompt_overlay_disables_only_generic_newline_announcement_script(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		overlayNode = next(
			node for node in tree.body
			if isinstance(node, ast.ClassDef) and node.name == "CodexPromptEditableTextOverlay"
		)
		overlayNamespace = {}
		exec(compile(ast.Module(body=[overlayNode], type_ignores=[]), str(PLUGIN_PATH), "exec"), overlayNamespace)
		overlayClass = overlayNamespace["CodexPromptEditableTextOverlay"]
		self.assertFalse(overlayClass.announceNewLineText)
		self.assertFalse(hasattr(overlayClass, "__gestures"))

		pluginClass = next(
			node for node in tree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		chooseMethod = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "chooseNVDAObjectOverlayClasses"
		)

		class RoleStub:
			BUTTON = "button"
			COMBOBOX = "combobox"
			EDITABLETEXT = "editableText"
			DOCUMENT = "document"

		namespace = {
			"Role": RoleStub,
			"_isChatGPTObject": lambda obj: True,
			"_isCodexPromptObject": lambda obj: bool(getattr(obj, "isPrompt", False)),
			"promptControlKind": lambda name: "",
			"CodexPromptControlOverlay": object,
			"CodexPromptEditableTextOverlay": overlayClass,
			"CodexEmbeddedBrowserOverlay": object,
			"_settings": lambda: {"enhanceEmbeddedBrowser": False},
			"_embeddedBrowserKind": lambda obj: "",
		}
		exec(compile(ast.Module(body=[chooseMethod], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		prompt = type("Object", (), {"role": RoleStub.EDITABLETEXT, "isPrompt": True})()
		classes = []
		namespace["chooseNVDAObjectOverlayClasses"](object(), prompt, classes)
		self.assertEqual([overlayClass], classes)

	def test_embedded_browser_progress_is_bucketed_and_scoped(self):
		self.assertEqual(
			("loading page", 47, 40),
			browserAccess.embeddedBrowserProgress("Loading page", "47%"),
		)
		self.assertEqual(
			("loading page", 100, 100),
			browserAccess.embeddedBrowserProgress("Loading page", "100 percent"),
		)
		self.assertEqual(("loading page", None, None), browserAccess.embeddedBrowserProgress("Loading page"))
		self.assertEqual(("loading page", 5, 10), browserAccess.embeddedBrowserProgress("Loading page", "5"))
		self.assertIsNone(browserAccess.embeddedBrowserProgress("Downloading model"))

	def test_embedded_browser_focus_tracking_is_silent_and_resets_load_state_on_exit(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in tree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_updateEmbeddedBrowserFocus"
		)
		namespace = {
			"_isEmbeddedBrowserObject": lambda obj: obj.browser,
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			def __init__(self):
				self._embeddedBrowserFocused = False
				self.resetCount = 0
			def _resetEmbeddedBrowserProgress(self): self.resetCount += 1
		subject = Subject()
		browser = type("Object", (), {"browser": True})()
		conversation = type("Object", (), {"browser": False})()
		namespace["_updateEmbeddedBrowserFocus"](subject, browser)
		namespace["_updateEmbeddedBrowserFocus"](subject, browser)
		self.assertTrue(subject._embeddedBrowserFocused)
		self.assertEqual(0, subject.resetCount)
		namespace["_updateEmbeddedBrowserFocus"](subject, conversation)
		self.assertFalse(subject._embeddedBrowserFocused)
		self.assertEqual(1, subject.resetCount)

	def test_runtime_imports_include_required_helpers(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		self.assertIn(
			"re",
			{
				alias.name
				for node in tree.body
				if isinstance(node, ast.Import)
				for alias in node.names
			},
		)
		coreImport = next(
			node for node in tree.body
			if isinstance(node, ast.ImportFrom) and node.module == "core"
		)
		self.assertIn("soundKey", {alias.name for alias in coreImport.names})

	def test_package_builder_normalizes_text_but_preserves_binary_data(self):
		with tempfile.TemporaryDirectory() as tempDir:
			textPath = Path(tempDir) / "module.py"
			binaryPath = Path(tempDir) / "sound.wav"
			textPath.write_bytes(b"first\r\nsecond\rthird\n")
			binary = b"RIFF\r\n\x00\rdata"
			binaryPath.write_bytes(binary)
			self.assertEqual(b"first\nsecond\nthird\n", packageBuilder.packageData(textPath))
			self.assertEqual(binary, packageBuilder.packageData(binaryPath))

	def test_package_builder_includes_docs_and_only_current_tiered_sounds(self):
		paths = tuple(path.relative_to(PROJECT_ROOT).as_posix() for path in packageBuilder.packageFiles(PROJECT_ROOT))
		for required in (
			"manifest.ini", "readme.md", "changelog.md", "LICENSE.txt",
			"locale/fr/LC_MESSAGES/nvda.mo", "locale/fr/manifest.ini",
		):
			self.assertIn(required, paths)
		self.assertEqual(67, len(paths))
		self.assertIn("globalPlugins/codexStatusAnnouncer/attachmentDiagnostics.py", paths)
		self.assertIn("globalPlugins/codexStatusAnnouncer/attachmentMenuDialog.py", paths)
		self.assertEqual(51, sum(path.endswith(".wav") for path in paths))
		self.assertIn("appModules/chatgpt.py", paths)
		self.assertNotIn("appModules/codex.py", paths)
		self.assertNotIn("globalPlugins/codexStatusAnnouncer/browserNavigatorDialog.py", paths)
		self.assertFalse(any(path.startswith("globalPlugins/codexStatusAnnouncer/sounds/") and path.count("/") == 3 for path in paths))
		self.assertFalse(any(path.endswith(".pot") for path in paths))
		self.assertFalse(any(path.endswith(".po") for path in paths))

	def test_french_catalog_translates_generated_labels_and_durations(self):
		translate = gettext.translation("nvda", PROJECT_ROOT / "locale", languages=["fr_CA"]).gettext
		self.assertEqual("Archiver le chat", translate("Archive chat"))
		self.assertEqual((("123", "Tâche archivée 123"),), uniqueThreadLabels((("123", ""),), translate))
		label = "Running command: git for 12 seconds"
		self.assertIn("12 secondes", core.standardFullMessage(label, translate))
		self.assertIn("12 secondes", core.minimalProfileMessage(label, translate, profile="informative"))

	def test_release_workflow_publishes_and_rechecks_only_the_audited_public_package(self):
		workflow = RELEASE_WORKFLOW_PATH.read_text(encoding="utf-8")
		self.assertIn('tags: ["v[0-9]*.[0-9]*.[0-9]*"]', workflow)
		self.assertIn("contents: write", workflow)
		self.assertIn(".\\build.ps1 -PythonPath python", workflow)
		self.assertIn('$package = "outputs/chatGPTDesktopAccess-$manifestVersion.nvda-addon"', workflow)
		self.assertIn("python tools/build_addon.py $reproduction", workflow)
		self.assertIn("fetch-depth: 0", workflow)
		self.assertIn("git merge-base --is-ancestor $env:GITHUB_SHA origin/main", workflow)
		self.assertIn("Release tag must point to a commit already present on main", workflow)
		self.assertIn("gh release create", workflow)
		self.assertIn("gh release view", workflow)
		self.assertIn("already exists; preserving it for verification", workflow)
		self.assertIn("Release must contain exactly one NVDA add-on asset", workflow)
		self.assertIn("--pattern $publishedAsset", workflow)
		self.assertIn("gh release download", workflow)
		self.assertIn("python tools/audit_addon.py $downloaded $manifestVersion", workflow)
		self.assertNotIn('"outputs/codexStatusAnnouncer-$manifestVersion.nvda-addon"', workflow)

	def test_settings_page_controls_have_distinct_access_keys(self):
		plugin = PLUGIN_PATH.read_text(encoding="utf-8")
		pageLabels = {
			"General": (
				"Enable &speech announcements", "Enable &braille flash messages",
				"&Redact likely secrets and personal path names in Full mode",
				"Test current announcement outputs (&T)",
			),
			"Speech and Braille": (
				"Active speech &detail:", "Profile used for &Full speech:",
				"Profile used for &Minimal speech:", "Full speech command &punctuation:",
				"Maximum Full speech command &length:",
				"Braille detail (&B), independent of speech:",
				"Review selected profiles (&S): {summary}",
				"Keep &conversation reading stable for speech and Braille during live updates",
				"Allow &urgent permission and failure announcements to interrupt current speech",
				"&Reset speech profile settings",
			),
			"Sounds": (
				"Play a sound for task &completion or failure",
				"Play &progress sounds for enabled announcements", "Progress sound style (&J):",
				"Click volume (&Z):", "Play a continuous &Working sound while ChatGPT or Codex is busy",
				"Working sound &interval (milliseconds):",
				"&Delay before repeating Working sounds (milliseconds):",
				"Play a distinct sound when a prompt is &submitted",
				"Play sounds when ChatGPT or Codex &monitoring becomes active or inactive",
				"Test command progress sound (&K)",
			),
			"Activity Output": (
				"Background progress &interval (seconds):", "Maximum background activity (&minutes):",
				"Announce a recurring background progress &pulse", "Activity &category:",
				"&Enable this activity category", "Output &route for this category:",
			),
			"Wording and Preview": (
				"Preview action (&V):", "Announcement &text (blank uses built-in):",
				"&Restore built-in announcement", "Preview selected &sound",
				"Preview selected s&peech",
			),
			"Browser Access": (
				"Announce when embedded browser pages start and finish &loading",
			),
			"Advanced": (
				"Idle compatibility &polling interval (milliseconds):",
				"Supported application &names, comma separated:",
				"Enable sanitized dia&gnostic logging",
			),
			"Support": (
				"&Open usage and credits",
				"View current release &notes…", "View complete release &history…",
				"Save sanitized support &report…", "&Export add-on settings…",
				"&Import add-on settings…",
			),
		}
		for page, labels in pageLabels.items():
			mnemonics = []
			for label in labels:
				self.assertIn(label, plugin, f"{page}: {label}")
				marker = label.index("&")
				mnemonics.append(label[marker + 1].casefold())
			self.assertEqual(len(mnemonics), len(set(mnemonics)), page)
		self.assertNotIn("&Check Codex usage statistics", plugin)
		self.assertNotIn("&Buy Codex usage credits", plugin)

	def test_usage_dashboard_is_one_visible_action_with_legacy_credits_compatibility(self):
		plugin = PLUGIN_PATH.read_text(encoding="utf-8")
		self.assertIn('CHATGPT_USAGE_URL = "https://chatgpt.com/settings/usage"', plugin)
		self.assertIn("wx.LaunchDefaultBrowser(CHATGPT_USAGE_URL)", plugin)
		tree = ast.parse(plugin)
		pluginClass = next(
			node for node in tree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = {
			node.name: node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef)
		}
		self.assertIn("script_openUsageStatistics", methods)
		self.assertIn("script_openUsageCredits", methods)
		self.assertTrue(methods["script_openUsageStatistics"].decorator_list)
		self.assertFalse(methods["script_openUsageCredits"].decorator_list)
		self.assertIn('description=_("Open ChatGPT usage and credits")', plugin)
		legacyBody = ast.get_source_segment(plugin, methods["script_openUsageCredits"])
		self.assertIn("self.script_openUsageStatistics(gesture)", legacyBody)

	def test_speech_and_braille_page_identifies_active_and_independent_profiles(self):
		plugin = PLUGIN_PATH.read_text(encoding="utf-8")
		self.assertIn("Speech uses one active profile at a time.", plugin)
		self.assertIn("Minimal — uses the Minimal speech profile below", plugin)
		self.assertIn("Full — uses the Full speech profile below", plugin)
		self.assertIn("Selected speech profile: {detail} — {profile}.", plugin)
		self.assertIn("Selected Braille detail: {braille}, independent of speech.", plugin)
		self.assertIn("control.Bind(wx.EVT_CHOICE, self._onProfileSettingChanged)", plugin)
		self.assertIn("self.profileSummaryButton.Bind(wx.EVT_BUTTON, self._onReviewProfileSummary)", plugin)
		self.assertGreaterEqual(plugin.count("self._updateProfileSummary()"), 4)

		pluginTree = ast.parse(plugin)
		panelClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "CodexStatusAnnouncerSettingsPanel"
		)
		method = next(
			node for node in panelClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_selectedProfileSummary"
		)
		namespace = {
			"VERBOSITY_CHOICES": ("minimal", "full"),
			"_": lambda value: value,
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)

		class Choice:
			def __init__(self, selection): self.selection = selection
			def GetSelection(self): return self.selection
		class Subject:
			verbosity = Choice(0)
			fullSpeechProfile = Choice(2)
			minimalSpeechProfile = Choice(1)
			brailleDetail = Choice(0)

		subject = Subject()
		self.assertEqual(
			"Selected speech profile: Minimal — Balanced. "
			"Selected Braille detail: Concise, independent of speech.",
			namespace["_selectedProfileSummary"](subject),
		)
		subject.verbosity.selection = -1
		subject.fullSpeechProfile.selection = -1
		subject.brailleDetail.selection = -1
		self.assertEqual(
			"Selected speech profile: Full — Developer. "
			"Selected Braille detail: Full, independent of speech.",
			namespace["_selectedProfileSummary"](subject),
		)

	def test_manifest_version_audit_accepts_lf_and_crlf_archives(self):
		tree = ast.parse(AUDIT_PATH.read_text(encoding="utf-8"))
		function = next(
			node for node in tree.body
			if isinstance(node, ast.FunctionDef) and node.name == "manifestVersionMatches"
		)
		namespace = {"re": __import__("re")}
		exec(compile(ast.Module(body=[function], type_ignores=[]), str(AUDIT_PATH), "exec"), namespace)
		for lineEnding in ("\n", "\r\n"):
			manifest = lineEnding.join(("name = codexStatusAnnouncer", "version = 2026.2.2", ""))
			self.assertTrue(namespace["manifestVersionMatches"](manifest, "2026.2.2"))
			self.assertFalse(namespace["manifestVersionMatches"](manifest, "2026.2.3"))

	def test_activity_settings_editor_preserves_each_category(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		panelClass = next(
			node for node in tree.body
			if isinstance(node, ast.ClassDef) and node.name == "CodexStatusAnnouncerSettingsPanel"
		)
		methods = [
			node for node in panelClass.body
			if isinstance(node, ast.FunctionDef) and node.name in {
				"_activityCategoryDisplay", "_refreshActivityCategoryDisplay",
				"_storeActivityCategory", "_loadActivityCategory", "_onActivityCategoryChanged",
				"_onActivitySettingChanged",
			}
		]
		namespace = {
			"OUTPUT_MODE_CHOICES": ("all", "speech", "sound", "braille", "off"),
			"_": lambda value: value,
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Check:
			def __init__(self, value=False): self.value = value
			def IsChecked(self): return self.value
			def SetValue(self, value): self.value = value
		class Choice:
			def __init__(self, selection=0): self.selection = selection
			def GetSelection(self): return self.selection
			def SetSelection(self, selection): self.selection = selection
			def SetString(self, index, value): self.lastString = (index, value)
		class Subject:
			pass
		for name in (
			"_activityCategoryDisplay", "_refreshActivityCategoryDisplay",
			"_storeActivityCategory", "_loadActivityCategory", "_onActivityCategoryChanged",
			"_onActivitySettingChanged",
		):
			setattr(Subject, name, namespace[name])
		subject = Subject()
		subject._activityCategories = (
			("announceThinking", "thinking", "Thinking"),
			("announceCommands", "command", "Commands"),
		)
		subject._categoryEnabledValues = {"announceThinking": True, "announceCommands": False}
		subject._categoryOutputValues = {"thinking": "all", "command": "speech"}
		subject._outputModeLabels = ("all enabled channels", "speech only", "sound only", "braille only", "off")
		subject._activityCategorySelection = 0
		subject.activityEnabled = Check(False)
		subject.activityOutput = Choice(2)
		subject.activityCategory = Choice(1)
		subject._onActivityCategoryChanged(None)
		self.assertFalse(subject._categoryEnabledValues["announceThinking"])
		self.assertEqual("sound", subject._categoryOutputValues["thinking"])
		self.assertEqual((0, "Thinking: disabled; sound only"), subject.activityCategory.lastString)
		self.assertFalse(subject.activityEnabled.IsChecked())
		self.assertEqual(1, subject.activityOutput.GetSelection())
		subject.activityEnabled.SetValue(True)
		subject.activityOutput.SetSelection(4)
		subject._storeActivityCategory()
		self.assertTrue(subject._categoryEnabledValues["announceCommands"])
		self.assertEqual("off", subject._categoryOutputValues["command"])
		self.assertEqual((1, "Commands: enabled; off"), subject.activityCategory.lastString)

	def test_addon_store_metadata_matches_manifest_and_package(self):
		manifest = (PROJECT_ROOT / "manifest.ini").read_text(encoding="utf-8")
		expectedVersion = storeMetadata._manifestValue(manifest, "version")
		expectedVersionNumber = storeMetadata._versionObject(expectedVersion)
		with tempfile.TemporaryDirectory() as tempDir:
			package = Path(tempDir) / f"chatGPTDesktopAccess-{expectedVersion}.nvda-addon"
			package.write_bytes(b"deterministic test package")
			url = (
				f"https://github.com/jcoffin1/chatgpt-desktop-access/releases/download/"
				f"v{expectedVersion}/chatGPTDesktopAccess-{expectedVersion}.nvda-addon"
			)
			metadata = storeMetadata.generate(PROJECT_ROOT, package, url)
		self.assertEqual("codexStatusAnnouncer", metadata["addonId"])
		self.assertEqual(expectedVersion, metadata["addonVersionName"])
		self.assertEqual(expectedVersionNumber, metadata["addonVersionNumber"])
		self.assertEqual({"major": 2026, "minor": 2, "patch": 0}, metadata["lastTestedVersion"])
		self.assertEqual(url, metadata["URL"])
		self.assertEqual(64, len(metadata["sha256"]))
		self.assertEqual("ChatGPT Desktop Access for NVDA", metadata["displayName"])
		self.assertEqual("https://github.com/jcoffin1/chatgpt-desktop-access", metadata["homepage"])
		self.assertEqual([], metadata["translations"])
		self.assertEqual(storeMetadata._manifestValue(manifest, "changelog"), metadata["changelog"])
		if expectedVersion in {"2026.2.11", "2026.2.12"}:
			self.assertIn("Attach files or connect apps", metadata["changelog"])
			self.assertNotIn("one-time speech and Braille hint", metadata["changelog"])
		self.assertEqual(
			"* First change.\n* Second change.",
			storeMetadata._manifestValue(
				'changelog = """* First change.\n* Second change."""\nversion = 1.0',
				"changelog",
			),
		)
		self.assertNotIn("What to test", metadata["changelog"])
		for text in (
			"AI", "artificial intelligence", "AI-generated", "generated by ChatGPT",
			"written by OpenAI", "Co-authored-by: Example",
		):
			with self.subTest(publicText=text), self.assertRaises(ValueError):
				storeMetadata._validatePublicText(text)

	def test_every_nvda_event_hook_is_exception_isolated_and_continues_the_chain(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in tree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		eventMethods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name.startswith("event_")
		]
		self.assertGreaterEqual(len(eventMethods), 7)
		for method in eventMethods:
			if method.name == "event_caret":
				# This hook must run before NVDA's object-level caret handler, which
				# would otherwise flush the first cell of the next contracted word.
				tryNode = next(node for node in method.body if isinstance(node, ast.Try))
				self.assertTrue(tryNode.finalbody, method.name)
				self.assertTrue(any(
					isinstance(node, ast.Call)
					and getattr(node.func, "id", "") == "nextHandler"
					for node in ast.walk(tryNode.finalbody[0])
				), method.name)
				continue
			if method.name == "event_liveRegionChange":
				# This hook deliberately withholds only ordinary streamed Response
				# updates while browse-mode reading protection is active. Every other
				# live-region event must continue through NVDA's native handler.
				self.assertTrue(any(
					isinstance(node, ast.Call)
					and getattr(node.func, "id", "") == "nextHandler"
					for node in ast.walk(method)
				), method.name)
				self.assertIn("shouldSuppressNativeConversationUpdate", ast.unparse(method))
				continue
			self.assertIsInstance(method.body[0], ast.Expr, method.name)
			self.assertIsInstance(method.body[0].value, ast.Call, method.name)
			self.assertEqual("nextHandler", getattr(method.body[0].value.func, "id", ""), method.name)
			self.assertTrue(any(isinstance(node, ast.Try) for node in method.body[1:]), method.name)

	def test_empty_prompt_focus_does_not_infer_a_submission(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in tree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "event_gainFocus"
		)
		class Roles:
			EDITABLETEXT = "edit"
			SECTION = "section"
		class Object:
			def __init__(self, role, isPrompt=False, hasText=False):
				self.role = role
				self.isPrompt = isPrompt
				self.hasText = hasText
		class Subject:
			def __init__(self):
				self._promptHadText = True
				self._pendingUserMessageIncrease = True
				self.submissions = 0
				self.polls = 0
				self.modeConfirmations = 0
				self._attachmentMenuActiveAt = 0.0
			def _rememberConversationWindowFromEvent(self, obj): return True
			def _updateAppFocusState(self, obj): return None
			def _rememberEmbeddedBrowserObject(self, obj): return False
			def _updateEmbeddedBrowserFocus(self, obj): pass
			def _announceEmbeddedBrowserTitle(self, obj): pass
			def _rememberBuffer(self, obj): pass
			def _resumeAttachmentSourceFocus(self): pass
			def _scheduleConversationEntryCorrection(self, obj): return False
			def _schedulePopupDialogFocus(self, obj): pass
			def _announceUsageLimit(self, obj): return False
			def _confirmConversationModeAfterSelector(self, obj):
				self.modeConfirmations += 1
				return False
			def _noteAttachmentMenuControl(self, obj, focused=False): return False
			def _announceAttachmentMenuSelection(self, obj, speak=True): return False
			def _resetAttachmentMenuTracking(self): self._attachmentMenuActiveAt = 0.0
			def _schedulePoll(self, *args, **kwargs): self.polls += 1
			def _trackPromptDraftState(self, obj):
				self._promptHadText = obj.hasText
				return False
		namespace = {
			"Role": Roles,
			"_isCodexPromptObject": lambda obj: obj.isPrompt,
			"_isChatGPTObject": lambda obj: True,
			"promptControlKind": lambda name: "",
			"log": type("Log", (), {"debugWarning": staticmethod(lambda *args, **kwargs: None)})(),
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		subject = Subject()
		namespace["event_gainFocus"](subject, Object(Roles.SECTION), lambda: None)
		self.assertTrue(subject._promptHadText)
		self.assertTrue(subject._pendingUserMessageIncrease)
		namespace["event_gainFocus"](subject, Object(Roles.EDITABLETEXT, True, False), lambda: None)
		self.assertFalse(subject._promptHadText)
		self.assertEqual(0, subject.submissions)
		self.assertEqual(2, subject.polls)
		self.assertEqual(2, subject.modeConfirmations)

	def test_chat_commands_are_truly_app_scoped_and_configurable(self):
		plugin = PLUGIN_PATH.read_text(encoding="utf-8")
		appModule = CHATGPT_APP_MODULE_PATH.read_text(encoding="utf-8")
		appTree = ast.parse(appModule)
		appClass = next(
			node for node in appTree.body
			if isinstance(node, ast.ClassDef) and node.name == "AppModule"
		)
		self.assertEqual("appModuleHandler.AppModule", ast.unparse(appClass.bases[0]))
		gestureAssignment = next(
			node for node in appClass.body
			if isinstance(node, ast.Assign)
			and any(isinstance(target, ast.Name) and target.id == "__gestures" for target in node.targets)
		)
		gestures = ast.literal_eval(gestureAssignment.value)
		self.assertEqual(15, len(gestures))
		self.assertEqual("announceChatTitle", gestures["kb:NVDA+shift+c"])
		self.assertEqual("toggleVoiceMode", gestures["kb:NVDA+alt+v"])
		self.assertEqual("reportOrSwitchComposerMode", gestures["kb:NVDA+alt+w"])
		self.assertEqual("reportComposerAttachments", gestures["kb:NVDA+alt+a"])
		self.assertNotIn("kb:NVDA+alt+m", gestures)
		self.assertEqual("toggleConversationMode", gestures["kb:NVDA+`"])
		self.assertNotIn("kb:NVDA+alt+shift+r", gestures)
		for digit in "1234567890":
			self.assertIn(f"kb:control+{digit}", gestures)
		# NVDA's user gesture map is class-based. Keeping every binding and script
		# on the app module means both defaults and reassignments resolve only when
		# the ChatGPT/Codex app module is the focused application's module.
		globalClass = next(
			node for node in ast.parse(plugin).body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		globalNames = {node.name for node in globalClass.body if isinstance(node, ast.FunctionDef)}
		self.assertNotIn("getScript", globalNames)
		self.assertFalse(any(name.startswith("script_read") and name.endswith("ChatMessage") for name in globalNames))
		self.assertNotIn("script_toggleVoiceMode", globalNames)
		self.assertNotIn("script_toggleMicrophoneMute", globalNames)
		browserScripts = {
			"script_openEmbeddedBrowserNavigator", "script_readEmbeddedBrowserPageSummary",
			"script_showEmbeddedBrowserSnapshot", "script_openEmbeddedBrowserExternally",
			"script_returnToChatGPTPrompt",
		}
		appNames = {node.name for node in appClass.body if isinstance(node, ast.FunctionDef)}
		self.assertIn("script_toggleConversationMode", appNames)
		self.assertIn('_("Open and focus the ChatGPT and Codex mode selector")', appModule)
		self.assertIn('_runToolkitCommand("_openConversationModeSelector")', appModule)
		self.assertTrue(browserScripts.isdisjoint(appNames))
		self.assertNotIn("gesture.send()", plugin + appModule)
		self.assertIn('APP_MODULE_ALIASES = (("codex", "chatgpt"),)', plugin)
		self.assertIn(
			"appModuleHandler.registerExecutableWithAppModule(executableName, appModuleName)",
			plugin,
		)
		self.assertIn("appModuleHandler.unregisterExecutable(executableName)", plugin)
		self.assertFalse((PROJECT_ROOT / "appModules" / "codex.py").exists())

	def test_existing_app_command_gesture_customizations_are_migrated_safely(self):
		pluginSource = PLUGIN_PATH.read_text(encoding="utf-8")
		tree = ast.parse(pluginSource)
		function = next(
			node for node in tree.body
			if isinstance(node, ast.FunctionDef) and node.name == "_migrateApplicationGestureMappings"
		)
		class FakeGestureMap:
			def __init__(self):
				self.entries = {
					"globalPlugins.codexStatusAnnouncer.GlobalPlugin": {
						"toggleVoiceMode": "kb:NVDA+shift+v",
						"readMostRecentChatMessage": ["kb:control+shift+1", "kb:control+alt+1"],
						"openChatHistory": "kb:NVDA+alt+o",
						"None": ["kb:control+1", "kb:NVDA+alt+x"],
					},
					"appModules.chatgpt.AppModule": {
						"readMostRecentChatMessage": "kb:control+shift+1",
					},
				}
				self.removed = []
				self.added = []
				self.saveCalls = 0
			def export(self): return self.entries
			def remove(self, gesture, module, className, script):
				self.removed.append((gesture, module, className, script))
			def add(self, gesture, module, className, script):
				self.added.append((gesture, module, className, script))
			def save(self): self.saveCalls += 1
		userMap = FakeGestureMap()
		namespace = {
			"inputCore": type("InputCore", (), {
				"manager": type("Manager", (), {"userGestureMap": userMap})(),
				"normalizeGestureIdentifier": staticmethod(lambda gesture: gesture.casefold()),
			})(),
			"APP_SCOPED_SCRIPT_NAMES": (
				"readMostRecentChatMessage", "toggleVoiceMode", "toggleMicrophoneMute",
			),
			"APP_SCOPED_DEFAULT_GESTURES": ("kb:control+1", "kb:NVDA+alt+v"),
			"log": type("Log", (), {"debugWarning": staticmethod(lambda *args, **kwargs: None)})(),
		}
		exec(compile(ast.Module(body=[function], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		self.assertEqual(4, namespace["_migrateApplicationGestureMappings"]())
		self.assertEqual(1, userMap.saveCalls)
		self.assertEqual(4, len(userMap.removed))
		self.assertIn(
			("kb:nvda+shift+v", "appModules.chatgpt", "AppModule", "toggleVoiceMode"),
			userMap.added,
		)
		self.assertIn(
			("kb:control+alt+1", "appModules.chatgpt", "AppModule", "readMostRecentChatMessage"),
			userMap.added,
		)
		self.assertIn(("kb:control+1", "appModules.chatgpt", "AppModule", None), userMap.added)
		self.assertNotIn(
			("kb:nvda+alt+x", "appModules.chatgpt", "AppModule", None),
			userMap.added,
		)
		self.assertFalse(any(item[-1] == "openChatHistory" for item in userMap.removed))

	def test_voice_control_labels_are_exact_and_do_not_match_speaker_controls(self):
		for label, expected in (
			("Start voice chat", "start"), ("Start voice mode", "start"),
			("Stop voice chat", "stop"), ("End voice chat", "stop"),
			("Leave voice mode", "stop"), ("Exit voice mode", "stop"),
			("Mute microphone", "mute"), ("Mute mic", "mute"),
			("Unmute microphone", "unmute"), ("Unmute mic", "unmute"),
		):
			self.assertEqual(expected, voiceControlKind(label), label)
			self.assertTrue(isKnownNonStatusButton(label), label)
		for label in ("Mute speakers", "Unmute speakers", "Voice chat", "Microphone", "Mute"):
			self.assertEqual("", voiceControlKind(label), label)

	def test_voice_actions_report_transition_then_confirmed_result(self):
		plugin = PLUGIN_PATH.read_text(encoding="utf-8")
		tree = ast.parse(plugin)
		pluginClass = next(
			node for node in tree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in {
				"_activateVoiceControl", "_confirmVoiceControlAction",
			}
		]
		messages = []
		namespace = {
			"_pressControl": lambda obj: obj.doAction(),
			"api": type("Api", (), {"getFocusObject": staticmethod(lambda: object())})(),
			"_isChatGPTObject": lambda obj: True,
			"ui": type("Ui", (), {"message": staticmethod(messages.append)})(),
			"_": lambda text: text,
			"VOICE_CONTROL_CONFIRMATION_ATTEMPTS": 2,
			"VOICE_CONTROL_CONFIRMATION_DELAY_MS": 500,
			"wx": type("Wx", (), {"CallLater": staticmethod(lambda *args: object())})(),
			"log": type("Log", (), {
				"info": staticmethod(lambda *args, **kwargs: None),
				"debugWarning": staticmethod(lambda *args, **kwargs: None),
			})(),
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)

		class Control:
			def __init__(self): self.activated = 0
			def doAction(self): self.activated += 1
		control = Control()
		class Subject:
			def __init__(self):
				self._pendingVoiceControlConfirmation = None
				self._voiceControlConfirmationTimer = None
			def _cancelVoiceControlConfirmation(self):
				self._pendingVoiceControlConfirmation = None
			def _voiceControlObject(self, wantedKinds):
				if "mute" in wantedKinds:
					return control, "mute"
				return control, "unmute"
			def _scheduleVoiceControlConfirmation(self, kind):
				self._pendingVoiceControlConfirmation = (kind, 0)
		subject = Subject()
		namespace["_activateVoiceControl"](subject, ("unmute", "mute"))
		self.assertEqual(1, control.activated)
		self.assertEqual(["Muting microphone"], messages)
		self.assertEqual(("mute", 0), subject._pendingVoiceControlConfirmation)
		namespace["_confirmVoiceControlAction"](subject)
		self.assertEqual(["Muting microphone", "Microphone muted"], messages)
		self.assertIsNone(subject._pendingVoiceControlConfirmation)

	def test_voice_control_search_prefers_current_state_and_exact_button_role(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in tree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in {
				"_voiceControlFromObject", "_voiceControlObject",
			}
		]

		class Object:
			def __init__(self, name, role="button", parent=None, states=()):
				self.name = name
				self.role = role
				self.parent = parent
				self.states = states
		start = Object("Start voice chat")
		stop = Object("Stop voice chat")
		muteSpeakers = Object("Mute speakers", role="togglebutton")
		pressedMute = Object("Mute microphone", role="togglebutton", states={"pressed"})

		class Position:
			def __init__(self): self.NVDAObjectAtStart = None
			def find(self, label, reverse, caseSensitive):
				self.NVDAObjectAtStart = {
					"Stop voice chat": stop,
					"Start voice chat": start,
					"Mute microphone": muteSpeakers,
				}.get(label)
				return self.NVDAObjectAtStart is not None
		class Buffer:
			def makeTextInfo(self, position): return Position()
		class Subject:
			_buffer = Buffer()
			def _rememberBuffer(self, focus): pass

		namespace = {
			"api": type("Api", (), {
				"getFocusObject": staticmethod(lambda: Object("Do anything", role="editabletext")),
				"getFocusAncestors": staticmethod(lambda: ()),
			})(),
			"voiceControlKind": voiceControlKind,
			"_roleName": lambda obj: obj.role,
			"State": type("State", (), {"PRESSED": "pressed", "CHECKED": "checked"}),
			"VOICE_CONTROL_SEARCH_LABELS": (
				("stop", "Stop voice chat"), ("start", "Start voice chat"),
				("mute", "Mute microphone"),
			),
			"textInfos": type("TextInfos", (), {"POSITION_LAST": "last"})(),
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		subject = Subject()
		subject._voiceControlFromObject = lambda obj, wanted: namespace["_voiceControlFromObject"](
			subject, obj, wanted,
		)
		control, kind = namespace["_voiceControlObject"](subject, ("stop", "start"))
		self.assertIs(stop, control)
		self.assertEqual("stop", kind)
		control, kind = namespace["_voiceControlObject"](subject, ("mute", "unmute"))
		self.assertIsNone(control)
		self.assertEqual("", kind)
		control, kind = namespace["_voiceControlFromObject"](
			subject, pressedMute, ("unmute", "mute"),
		)
		self.assertIs(pressedMute, control)
		self.assertEqual("unmute", kind)

	def test_release_metadata_and_requested_chat_message_gestures_are_consistent(self):
		manifest = (PROJECT_ROOT / "manifest.ini").read_text(encoding="utf-8")
		version = storeMetadata._manifestValue(manifest, "version")
		plugin = PLUGIN_PATH.read_text(encoding="utf-8")
		appModule = CHATGPT_APP_MODULE_PATH.read_text(encoding="utf-8")
		readme = (PROJECT_ROOT / "readme.md").read_text(encoding="utf-8")
		chatDialog = CHAT_DIALOG_PATH.read_text(encoding="utf-8")
		soundOutput = SOUND_OUTPUT_PATH.read_text(encoding="utf-8")
		self.assertIn(f"version = {version}", manifest)
		self.assertIn('summary = "ChatGPT Desktop Access for NVDA"', manifest)
		self.assertIn(f'ADDON_VERSION = "{version}"', plugin)
		self.assertIn('DEFAULT_SUPPORTED_APP_NAMES = "chatgpt,codex"', plugin)
		self.assertIn("not _isConversationObject(obj)", plugin)
		self.assertIn("url = https://github.com/jcoffin1/chatgpt-desktop-access", manifest)
		self.assertIn("docFileName = readme.md", manifest)
		self.assertIn("minimumNVDAVersion = 2023.1.0", manifest)
		self.assertIn("lastTestedNVDAVersion = 2026.2.0", manifest)
		self.assertIn("updateChannel = None", manifest)
		self.assertIn('"protectBrailleReading": "boolean(default=True)"', plugin)
		self.assertIn('conf["protectBrailleReading"], self._appFocusState', plugin)
		self.assertIn("actualDelay = coalescedPollDelay(", plugin)
		self.assertIn("shouldReplaceScheduledPoll(self._nextPollAt, requestedDeadline)", plugin)
		self.assertIn('log.debugWarning("ChatGPT Desktop Access speech output failed"', plugin)
		self.assertIn('log.debugWarning("ChatGPT Desktop Access Braille output failed"', plugin)
		self.assertIn('log.debugWarning("ChatGPT Desktop Access tone output failed"', soundOutput)
		self.assertIn("def safeBeep(frequency, duration):", soundOutput)
		self.assertIn("safeBeep as _safeBeep", plugin)
		self.assertIn('log.debugWarning("ChatGPT Desktop Access could not cancel speech for an urgent message"', plugin)
		self.assertIn('redactSensitive(message) if conf["redactSensitive"] else message', plugin)
		self.assertIn("or not _isChatGPTObject(obj):", plugin)
		self.assertIn("previousValues = {", plugin)
		self.assertIn("backgroundActivityName(self._activeCategory, self._latestFullMessage)", plugin)
		self.assertIn("self._schedulePopupDialogFocus(obj)", plugin)
		self.assertIn("self._focusPopupDialog", plugin)
		self.assertIn("if not _isChatGPTObject(obj):", plugin)
		self.assertIn("self._pluginProgressOwnedBusy.discard(expiredIdentity)", plugin)
		self.assertIn('Role.PROGRESSBAR or not _isChatGPTObject(obj)', plugin)
		self.assertIn('self._setBusy(False, "prompt superseded plugin installation")', plugin)
		self.assertNotIn("obsolete Codex Status Announcer loaded", plugin)
		self.assertNotIn("Adds assignable focus- and browse-mode actions", manifest)
		self.assertIn('default=\'full\'', plugin)
		self.assertIn("fullSpeechProfile", plugin)
		self.assertIn("default='developer'", plugin)
		self.assertIn("minimalSpeechProfile", plugin)
		self.assertIn("default='balanced'", plugin)
		self.assertIn("brailleDetail", plugin)
		self.assertIn("interruptUrgentSpeech", plugin)
		self.assertIn("__gestures = {", appModule)
		for digit, scriptName in zip("1234567890", (
			"readMostRecentChatMessage", "readSecondMostRecentChatMessage",
			"readThirdMostRecentChatMessage", "readFourthMostRecentChatMessage",
			"readFifthMostRecentChatMessage", "readSixthMostRecentChatMessage",
			"readSeventhMostRecentChatMessage", "readEighthMostRecentChatMessage",
			"readNinthMostRecentChatMessage", "readTenthMostRecentChatMessage",
		)):
			self.assertIn(f'"kb:control+{digit}": "{scriptName}"', appModule)
			self.assertIn(f"def script_{scriptName}", appModule)
		self.assertIn('"kb:NVDA+alt+v": "toggleVoiceMode"', appModule)
		self.assertNotIn('"kb:NVDA+alt+m": "toggleMicrophoneMute"', appModule)
		self.assertIn("def script_toggleMicrophoneMute", appModule)
		self.assertIn('"kb:NVDA+`": "toggleConversationMode"', appModule)
		self.assertIn("class AppModule(appModuleHandler.AppModule)", appModule)
		self.assertIn('APP_MODULE_ALIASES = (("codex", "chatgpt"),)', plugin)
		self.assertIn("appModuleHandler.registerExecutableWithAppModule", plugin)
		self.assertIn("appModuleHandler.unregisterExecutable", plugin)
		self.assertNotIn("gesture.send()", plugin + appModule)
		self.assertNotIn("_setChatMessageShortcutBindings", plugin)
		self.assertNotIn('"kb:enter"', plugin)
		self.assertNotIn("script_enter", plugin.casefold())
		self.assertTrue(CHATGPT_APP_MODULE_PATH.exists())
		self.assertFalse((PROJECT_ROOT / "appModules" / "codex.py").exists())
		self.assertIn("default **Interact with math content** command", readme)
		self.assertIn("has no default gesture", readme)
		inputGestures = readme.split("## Input gestures", 1)[1].split("## Embedded browser access", 1)[0]
		self.assertIn("### Recent-message review", inputGestures)
		self.assertIn("### Voice mode", inputGestures)
		self.assertIn("### Chat history", inputGestures)
		for paragraph in inputGestures.split("\n\n"):
			if paragraph.startswith(("#", "-")):
				continue
			self.assertLessEqual(len(" ".join(paragraph.splitlines())), 700)
		self.assertNotIn("gesture=", plugin + appModule)
		self.assertNotIn("self._chatHistoryDialog.ShowModal", plugin)
		self.assertIn('label=_("Recent chats:")', chatDialog)
		self.assertIn('label=_("Archived chats:")', chatDialog)
		self.assertIn("self.recentList", chatDialog)
		self.assertIn("self.archivedList", chatDialog)
		self.assertIn("self.recentList.Bind(wx.EVT_CONTEXT_MENU, self._onContextMenu)", chatDialog)
		self.assertIn("self.archivedList.Bind(wx.EVT_CONTEXT_MENU, self._onContextMenu)", chatDialog)
		self.assertIn("self._showChatActionMenu(selection)", chatDialog)
		self.assertIn("self._retryDirectChatAction", plugin)
		self.assertIn('_("Pin or unpin chat")', chatDialog)
		self.assertIn('_("Archive chat")', chatDialog)
		self.assertIn('chosen.append("pin")', chatDialog)
		self.assertIn('chosen.append("archive")', chatDialog)
		self.assertNotIn('"focusActions"', chatDialog + plugin)
		self.assertIn("_pressControl(actionButton)", plugin)
		self.assertIn("self._scheduleUnarchiveButtonFocus()", plugin)
		self.assertIn('position.find("Unarchive and open"', plugin)
		self.assertIn("message = _completeChangelogMessage()", plugin)
		self.assertIn("_showBrowseableMessageAtTop(", plugin)
		self.assertIn('CURRENT_RELEASE_NOTES, _("ChatGPT Desktop Access — what\'s new")', plugin)
		self.assertIn('scriptCategory = _("ChatGPT Desktop Access")', plugin)
		self.assertIn('self._lastSpeechMessage', plugin)
		self.assertIn('self._lastBrailleMessage', plugin)
		self.assertIn('version=ADDON_VERSION', plugin)
		self.assertNotIn("Unable to load the complete startup changelog", plugin)
		self.assertNotIn("import sqlite3", CORE_PATH.read_text(encoding="utf-8"))
		self.assertIn("_repairConfiguration()", plugin)
		self.assertIn("script_runCompatibilitySelfTest", plugin)
		self.assertIn("script_copyLatestFullProgress", plugin)
		self.assertIn("_onExportSettings", plugin)
		self.assertIn("_onImportSettings", plugin)
		self.assertIn("_loadControlsFromConfiguration", plugin)
		self.assertIn("settings file exceeds 1 MB", plugin)
		self.assertIn("_onResetSpeechSettings", plugin)
		self.assertIn("_onRefresh", chatDialog)
		self.assertIn("wx.Notebook(self)", plugin)
		self.assertIn('self._addPage(_("Activity Output"))', plugin)
		self.assertIn('self._addPage(_("Browser Access"))', plugin)
		self.assertIn('self._addPage(_("Advanced"))', plugin)
		self.assertIn('self._addPage(_("Support"))', plugin)
		self.assertNotIn('self._addPage(_("Advanced and Support"))', plugin)
		self.assertIn("_activityCategoryDisplay", plugin)
		self.assertIn("for index in range(len(self._activityCategories)):", plugin)
		self.assertIn('defaultFile="chatgpt-desktop-access-settings.json"', plugin)
		self.assertIn("_onSaveSupportReport", plugin)
		self.assertIn("script_saveSupportReport", plugin)
		self.assertNotIn("script_openAddFilesAndMore", plugin)
		self.assertNotIn("script_openModelSelector", plugin)
		self.assertNotIn("script_openChangePermissions", plugin)
		self.assertNotIn("_boundedDescendants", plugin)
		self.assertIn("class CodexPromptControlOverlay", plugin)
		self.assertNotIn("class CodexEmbeddedBrowserOverlay", plugin)
		self.assertNotIn("def script_showEmbeddedBrowserHelp", plugin)
		self.assertIn("def event_stateChange", plugin)
		self.assertIn('self._embeddedBrowserNotice(_("Loading page"))', plugin)
		self.assertIn('self._embeddedBrowserNotice(_("Loading complete"))', plugin)
		self.assertIn("chooseNVDAObjectOverlayClasses", plugin)
		self.assertIn("_codexNativeDescription", plugin)
		self.assertNotIn("could not enhance a prompt control", plugin)
		self.assertIn("_chatHistoryActionTimer", plugin)
		self.assertIn("chatTitleMatches(title", plugin)
		self.assertIn("unrecognized buttons: count=%d, lengths=%s", plugin)
		self.assertNotIn('unrecognized buttons: %s", list(snapshot)', plugin)

	def test_restricted_nvda_runtime_does_not_require_known_optional_modules(self):
		source = "\n".join(
			path.read_text(encoding="utf-8")
			for path in CORE_PATH.parent.glob("*.py")
		)
		for forbiddenImport in ("import sqlite3", "import requests", "import numpy", "import yaml"):
			self.assertNotIn(forbiddenImport, source)

	def test_semantic_duplicate_suppression_ignores_cosmetic_wording_changes(self):
		self.assertEqual("editing code", semanticStatusKey("Editing file"))
		self.assertEqual("editing code", semanticStatusKey("Editing code"))
		self.assertTrue(shouldSuppressSemanticDuplicate("Editing file", "Editing code", 0.5))
		self.assertFalse(shouldSuppressSemanticDuplicate("Running tests", "Editing code", 0.5))
		self.assertFalse(shouldSuppressSemanticDuplicate("Editing file", "Editing code", 1.5))

	def test_braille_detail_is_independent_of_speech_verbosity(self):
		label = "Running shell command: rg -n status globalPlugins"
		self.assertEqual("Running command", brailleStatusMessage(label, detail="concise"))
		self.assertEqual("Running command", brailleStatusMessage(label, detail="informative"))
		self.assertEqual(label, brailleStatusMessage(label, detail="full"))
		self.assertEqual(label, brailleStatusMessage(label, detail="invalid"))

	def test_speech_duplicate_does_not_hide_distinct_braille_detail(self):
		result = duplicateChannelActions(
			"Running command", "Running shell command: rg one", "Running command",
			"Running shell command: rg two", 0.2, 0.2,
		)
		self.assertEqual({"speech": True, "braille": False}, result)

	def test_send_calls_real_braille_message_path_when_speech_is_disabled(self):
		pluginSource = PLUGIN_PATH.read_text(encoding="utf-8")
		function = next(
			node for node in ast.parse(pluginSource).body
			if isinstance(node, ast.FunctionDef) and node.name == "_send"
		)
		calls = []
		class Speech:
			def speakMessage(self, message):
				calls.append(("speech", message))
			def cancelSpeech(self):
				calls.append(("cancel", None))
		class Handler:
			def message(self, message):
				calls.append(("braille", message))
		namespace = {
			"outputActions": lambda speak, speechOff, showBraille, sounds, tone: {
				"speech": bool(speak), "braille": bool(showBraille), "tone": False,
			},
			"_speechIsOff": lambda: False,
			"_settings": lambda: {"interruptUrgentSpeech": True},
			"speech": Speech(),
			"braille": type("Braille", (), {"handler": Handler()})(),
			"_playProgressSound": lambda *args: None,
		}
		exec(compile(ast.Module(body=[function], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		namespace["_send"]("short speech", False, True, brailleMessage="complete braille command")
		self.assertEqual([("braille", "complete braille command")], calls)
		calls.clear()
		namespace["_send"]("Permission required", True, False, priority="urgent", interruptUrgent=False)
		self.assertEqual([("speech", "Permission required")], calls)
		calls.clear()
		namespace["_send"]("Permission required", True, False, priority="urgent", interruptUrgent=True)
		self.assertEqual([("cancel", None), ("speech", "Permission required")], calls)

	def test_command_speech_punctuation_and_length_controls(self):
		self.assertEqual(
			("rg files pipe sort redirect to output.txt", False),
			formatCommandSpeech("rg files | sort > output.txt", "enhanced", 240),
		)
		literal, shortened = formatCommandSpeech("one && two", "literal", 240)
		self.assertEqual("one ampersand ampersand two", literal)
		self.assertFalse(shortened)
		short, shortened = formatCommandSpeech("x" * 100, "normal", 40)
		self.assertTrue(shortened)
		self.assertLessEqual(len(short), 41)

	def test_prompt_toolbar_control_names_are_classified_without_conversation_search(self):
		self.assertEqual("files", promptControlKind("Add files and more"))
		self.assertEqual("files", promptControlKind("Attach files"))
		self.assertEqual("permissions", promptControlKind("Change permissions"))
		self.assertEqual("model", promptControlKind("Select model"))
		self.assertEqual("model", promptControlKind("Model and reasoning"))
		self.assertEqual("model", promptControlKind("GPT-5.6 Developer"))
		self.assertEqual("model", promptControlKind("GPT-6 Astra Light"))
		self.assertEqual("model", promptControlKind("6.1 Sol Light"))
		self.assertEqual("model", promptControlKind("6 Sol Max"))
		self.assertEqual("model", promptControlKind("Astra Light"))
		self.assertEqual("model", promptControlKind("o4-mini"))
		self.assertEqual("", promptControlKind("Adding GPT-6 model support"))
		self.assertEqual("", promptControlKind("Investigating model selector"))
		self.assertEqual("", promptControlKind("Send"))

	def test_attachment_menu_item_labels_require_active_popup_context(self):
		self.assertEqual(
			"Upload from computer",
			attachmentMenuItemLabel(True, "menuItem", "Upload from computer"),
		)
		self.assertEqual("Upload files", attachmentMenuItemLabel(True, "button", "Upload files"))
		self.assertEqual(
			"Take screenshot",
			attachmentMenuItemLabel(
				True, "button", "Add files and more", "Take screenshot",
				"Opens file and attachment options",
			),
		)
		self.assertEqual(
			"Connect cloud storage",
			attachmentMenuItemLabel(True, "list item", "", "", "Connect cloud storage"),
		)
		self.assertEqual("", attachmentMenuItemLabel(False, "menuItem", "Upload from computer"))
		self.assertEqual("", attachmentMenuItemLabel(True, "separator", "Upload from computer"))
		self.assertEqual("", attachmentMenuItemLabel(True, "button", "Add files and more"))

	def test_attachment_menu_selection_feedback_is_scoped_and_deduplicated(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in tree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methodNames = {
			"_resetAttachmentMenuTracking", "_noteAttachmentMenuControl",
			"_attachmentMenuSelectionState", "_attachmentMenuLabel",
			"_attachmentMenuContextActive",
			"_announceAttachmentMenuSelection",
		}
		methods = {
			node.name: node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in methodNames
		}
		class Clock:
			now = 100.0
			@classmethod
			def monotonic(cls): return cls.now
		class States:
			EXPANDED = "expanded"
			COLLAPSED = "collapsed"
			SELECTED = "selected"
			FOCUSED = "focused"
		outputs = []
		channels = []
		settings = {"speech": True, "braille": True}
		def send(message, speak, showBraille, *args, **kwargs):
			outputs.append(message)
			channels.append((speak, showBraille))
		namespace = {
			"time": Clock,
			"State": States,
			"_isChatGPTObject": lambda obj: bool(getattr(obj, "inChatGPT", True)),
			"promptControlKind": promptControlKind,
			"attachmentMenuItemLabel": attachmentMenuItemLabel,
			"_roleName": lambda obj: getattr(obj, "role", ""),
			"ATTACHMENT_MENU_ARM_SECONDS": 5.0,
			"ATTACHMENT_MENU_TIMEOUT_SECONDS": 60.0,
			"ATTACHMENT_MENU_DUPLICATE_SECONDS": 0.35,
			"ATTACHMENT_MENU_STALE_EXPANSION_SECONDS": 1.25,
			"_": lambda text: text,
			"_settings": lambda: settings,
			"_send": send,
			"log": type("Log", (), {"debug": staticmethod(lambda *args, **kwargs: None), "info": staticmethod(lambda *args, **kwargs: None)}),
		}
		exec(
			compile(ast.Module(body=list(methods.values()), type_ignores=[]), str(PLUGIN_PATH), "exec"),
			namespace,
		)
		class Subject:
			def __init__(self):
				self._attachmentMenuActiveAt = 0.0
				self._attachmentActivationAt = 0.0
				self._attachmentInputCandidateAt = 0.0
				self._attachmentInputCandidateWindowHandle = 0
				self._attachmentSourcePendingButton = None
				self._attachmentMenuLastClosedAt = 0.0
				self._attachmentMenuButtonFocusedAt = 0.0
				self._lastAttachmentMenuItem = ""
				self._lastAttachmentMenuItemAt = 0.0
				self._attachmentDiagnostics = type("Diagnostics", (), {
					"noteButtonFocused": lambda self, button: None,
					"noteButtonActivated": lambda self, button, reason: None,
				})()
		for name in methodNames:
			setattr(Subject, name, namespace[name])
		class Object:
			def __init__(self, role, name="", value="", states=()):
				self.role = role
				self.name = name
				self.value = value
				self.description = ""
				self.states = set(states)
				self.inChatGPT = True
		def _scheduleAttachmentSourceFocus(self, button, now):
			self._attachmentFocusRequests = getattr(self, "_attachmentFocusRequests", 0) + 1
		def _cancelAttachmentSourceFocus(self):
			self._attachmentActivationAt = 0.0
			self._attachmentSourcePendingButton = None
		Subject._scheduleAttachmentSourceFocus = _scheduleAttachmentSourceFocus
		Subject._cancelAttachmentSourceFocus = _cancelAttachmentSourceFocus
		subject = Subject()
		button = Object("button", "Add files and more", states=(States.COLLAPSED,))
		self.assertTrue(subject._noteAttachmentMenuControl(button, focused=True))
		self.assertEqual(100.0, subject._attachmentMenuButtonFocusedAt)
		button.states = {States.EXPANDED}
		self.assertTrue(subject._noteAttachmentMenuControl(button))
		self.assertEqual([], outputs)
		self.assertEqual(1, subject._attachmentFocusRequests)
		self.assertTrue(subject._noteAttachmentMenuControl(button))
		self.assertEqual([], outputs)
		self.assertEqual(1, subject._attachmentFocusRequests)
		self.assertFalse(subject._noteAttachmentMenuControl(
			Object("button", "Upload files", states=(States.SELECTED,)),
		))
		item = Object("menuitem", "Upload from computer", states=(States.SELECTED,))
		self.assertTrue(subject._attachmentMenuSelectionState(item))
		self.assertTrue(subject._announceAttachmentMenuSelection(item))
		self.assertEqual("Upload from computer, menu item", outputs[-1])
		Clock.now = 100.1
		self.assertTrue(subject._announceAttachmentMenuSelection(item))
		self.assertEqual(1, len(outputs))
		Clock.now = 100.2
		settings.update(speech=False, braille=True)
		self.assertTrue(subject._announceAttachmentMenuSelection(
			Object("menuitem", "Take screenshot", states=(States.SELECTED,)),
		))
		self.assertEqual("Take screenshot, menu item", outputs[-1])
		self.assertEqual((False, True), channels[-1])
		Clock.now = 100.3
		settings.update(speech=True, braille=False)
		self.assertTrue(subject._announceAttachmentMenuSelection(
			Object("menuitem", "Connect cloud storage", states=(States.SELECTED,)),
		))
		self.assertEqual((True, False), channels[-1])
		Clock.now = 161.0
		self.assertFalse(subject._announceAttachmentMenuSelection(item))
		self.assertEqual(0.0, subject._attachmentMenuActiveAt)
		# If Chromium omits expanded state, a named item focused immediately after
		# the Add files button still establishes a short, bounded popup context.
		Clock.now = 200.0
		button.states = {States.COLLAPSED}
		subject._noteAttachmentMenuControl(button, focused=True)
		Clock.now = 201.0
		self.assertTrue(subject._announceAttachmentMenuSelection(item))
		button.states = {States.COLLAPSED}
		subject._noteAttachmentMenuControl(button)
		self.assertEqual(0.0, subject._attachmentMenuActiveAt)
		self.assertEqual(201.0, subject._attachmentMenuLastClosedAt)
		self.assertEqual(0.0, subject._attachmentMenuButtonFocusedAt)
		self.assertFalse(subject._announceAttachmentMenuSelection(item))
		previousOutputCount = len(outputs)
		Clock.now = 201.6
		button.states = {States.EXPANDED}
		subject._noteAttachmentMenuControl(button)
		self.assertEqual(previousOutputCount, len(outputs))
		self.assertEqual(0.0, subject._attachmentMenuActiveAt)
		Clock.now = 203.0
		button.states = {States.EXPANDED}
		subject._noteAttachmentMenuControl(button)
		self.assertEqual(previousOutputCount, len(outputs))
		plugin = PLUGIN_PATH.read_text(encoding="utf-8")
		self.assertIn("def event_selection(self, obj, nextHandler):", plugin)
		self.assertIn("def event_selectionWithIn(self, obj, nextHandler):", plugin)
		self.assertIn("self._announceAttachmentMenuSelection(obj)", plugin)
		focusHook = plugin[plugin.index("\tdef event_gainFocus"):plugin.index("\n\tdef event_foreground")]
		self.assertLess(
			focusHook.index("self._resetAttachmentMenuTracking()"),
			focusHook.index("self._announceAttachmentMenuSelection(obj, speak=False)"),
		)

	def test_attachment_source_focus_requires_explicit_activation_and_exact_native_menu(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin")
		methodNames = {
			"_cancelAttachmentSourceFocus", "_isAddFilesButton", "_attachmentButtonIsCurrent",
			"_noteAttachmentActivationGesture", "_attachmentSourceMenuObject",
			"_captureAttachmentActivationFromQueuedGesture",
			"_focusAttachmentSourceMenu", "_scheduleAttachmentSourceFocus",
			"_resumeAttachmentSourceFocus",
			"_noteAttachmentMenuControl",
		}
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in methodNames
		]
		class Clock:
			@staticmethod
			def monotonic(): return 100.0
		class States:
			EXPANDED = "expanded"
			COLLAPSED = "collapsed"
		class Object:
			def __init__(self, role, name, states=()):
				self.role = role
				self.name = name
				self.states = set(states)
				self.inChatGPT = True
				self.parent = None
				self.focused = False
			def setFocus(self): self.focused = True
		class Position:
			def __init__(self, obj): self.NVDAObjectAtStart = obj
			def collapse(self): pass
			def updateCaret(self): self.NVDAObjectAtStart.caretUpdated = True
			def find(self, text, reverse=False, caseSensitive=False):
				return text == "Attach files or connect apps" and reverse
		class Buffer:
			passThrough = False
			def __init__(self, caret, source):
				self.caret = caret
				self.source = source
			def makeTextInfo(self, position):
				return Position(self.caret if position == "caret" else self.source)
		class API:
			focus = None
			navigator = None
			@classmethod
			def getFocusObject(cls): return cls.focus
			@classmethod
			def setNavigatorObject(cls, obj): cls.navigator = obj
		class Timer:
			def __init__(self, callback, args):
				self.callback = callback
				self.args = args
				self.stopped = False
			def Stop(self): self.stopped = True
		class WX:
			@staticmethod
			def CallLater(delay, callback, *args):
				self.assertEqual(180, delay)
				return Timer(callback, args)
		button = Object("button", "Add files and more", (States.EXPANDED,))
		source = Object("menubutton", "Attach files or connect apps")
		prompt = Object("edit", "Do anything")
		API.focus = prompt
		namespace = {
			"CHATGPT_PROMPT_EDITOR_CLASS": core.CHATGPT_PROMPT_EDITOR_CLASS, "MODE_SWITCH_BUTTON_LABELS": core.MODE_SWITCH_BUTTON_LABELS, "SOURCES_MENU_BUTTON_NAME": core.SOURCES_MENU_BUTTON_NAME, "ADD_FILES_BUTTON_NAME": core.ADD_FILES_BUTTON_NAME,
			"time": Clock, "State": States, "api": API, "wx": WX,
			"textInfos": type("TextInfos", (), {"POSITION_CARET": "caret", "POSITION_LAST": "last"}),
			"_roleName": lambda obj: obj.role,
			"_isChatGPTObject": lambda obj: bool(getattr(obj, "inChatGPT", False)),
			"_isCodexPromptObject": lambda obj: getattr(obj, "name", "") == "Do anything",
			"_isVirtualBufferDocument": lambda buffer: True,
			"promptControlKind": promptControlKind,
			"isPromptSubmissionGestureIdentifier": isPromptSubmissionGestureIdentifier,
			"ATTACHMENT_ACTIVATION_WINDOW_SECONDS": 1.5,
			"ATTACHMENT_MENU_STALE_EXPANSION_SECONDS": 1.25,
			"ATTACHMENT_SOURCE_FOCUS_DELAY_MILLISECONDS": 180,
			"ATTACHMENT_POPUP_RETRIES": 6,
			"ATTACHMENT_POPUP_RETRY_MILLISECONDS": 150,
			"ATTACHMENT_POPUP_SETTLE_ATTEMPTS": 4,
			"log": type("Log", (), {
				"debug": staticmethod(lambda *args, **kwargs: None),
				"debugWarning": staticmethod(lambda *args, **kwargs: None),
				"info": staticmethod(lambda *args, **kwargs: None),
			}),
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			def _logAttachmentButtonPress(self): pass
			def _readAttachmentPopupOptions(self, buffer): return ()
			def __init__(self):
				self._buffer = Buffer(button, source)
				self._conversationWindowHandle = 10
				self._appFocusState = True
				self._attachmentActivationAt = 0.0
				self._attachmentInputCandidateAt = 0.0
				self._attachmentInputCandidateWindowHandle = 0
				self._attachmentSourcePendingButton = None
				self._attachmentSourceFocusTimer = None
				self._attachmentMenuActiveAt = 0.0
				self._attachmentMenuLastClosedAt = 0.0
				self._attachmentMenuButtonFocusedAt = 0.0
				self._lastAttachmentMenuItem = ""
				self._lastAttachmentMenuItemAt = 0.0
				self._attachmentDiagnostics = type("Diagnostics", (), {
					"noteButtonFocused": lambda self, button: None,
					"noteButtonActivated": lambda self, button, reason: None,
				})()
			def _conversationWindowIsAvailable(self, handle): return handle == 10
			def _conversationWindowOwnsForeground(self, handle): return handle == 10
			def _attachmentPopupAnchor(self, buffer): return None
		for method in methods:
			setattr(Subject, method.name, namespace[method.name])
		subject = Subject()
		subject._noteAttachmentMenuControl(button)
		self.assertIsNone(subject._attachmentSourceFocusTimer)
		subject._attachmentMenuActiveAt = 0.0
		subject._attachmentMenuLastClosedAt = 99.8
		subject._noteAttachmentActivationGesture(("br(hims):dot8",))
		self.assertEqual(100.0, subject._attachmentActivationAt)
		self.assertIs(subject._attachmentSourcePendingButton, button)
		subject._noteAttachmentMenuControl(button)
		timer = subject._attachmentSourceFocusTimer
		self.assertIsNotNone(timer)
		self.assertEqual(0.0, subject._attachmentActivationAt)
		timer.callback(*timer.args)
		self.assertTrue(source.focused)
		self.assertTrue(source.caretUpdated)
		self.assertIs(API.navigator, source)
		# Hardware input is first marked on winInputHook. The exact expanded
		# Add files state promotes that marker on NVDA's main thread.
		hardware = Subject()
		hardware._attachmentInputCandidateAt = 100.0
		hardware._attachmentInputCandidateWindowHandle = 10
		button.states = {States.COLLAPSED}
		hardware._noteAttachmentMenuControl(button)
		self.assertEqual(100.0, hardware._attachmentInputCandidateAt)
		button.states = {States.EXPANDED}
		hardware._noteAttachmentMenuControl(button)
		self.assertIsNotNone(hardware._attachmentSourceFocusTimer)
		self.assertEqual(0.0, hardware._attachmentInputCandidateAt)
		self.assertEqual(0, hardware._attachmentInputCandidateWindowHandle)
		hardware._attachmentSourceFocusTimer.callback(*hardware._attachmentSourceFocusTimer.args)
		self.assertTrue(source.focused)
		wrongWindow = Subject()
		wrongWindow._attachmentInputCandidateAt = 100.0
		wrongWindow._attachmentInputCandidateWindowHandle = 11
		wrongWindow._noteAttachmentMenuControl(button)
		self.assertIsNone(wrongWindow._attachmentSourceFocusTimer)
		stale = Subject()
		stale._attachmentInputCandidateAt = 98.0
		stale._attachmentInputCandidateWindowHandle = 10
		stale._noteAttachmentMenuControl(button)
		self.assertIsNone(stale._attachmentSourceFocusTimer)
		# If the main-thread queue runs before Chromium moves the caret, it
		# retains the exact button even without an expanded-state event.
		queued = Subject()
		queued._attachmentInputCandidateAt = 100.0
		queued._attachmentInputCandidateWindowHandle = 10
		queued._captureAttachmentActivationFromQueuedGesture(("kb(laptop):space",), 100.0, 10)
		self.assertIs(queued._attachmentSourcePendingButton, button)
		self.assertEqual(0.0, queued._attachmentInputCandidateAt)
		# A later navigation gesture cancels an unexecuted redirect.
		subject._attachmentMenuActiveAt = 0.0
		subject._noteAttachmentActivationGesture(("kb(laptop):space",))
		subject._noteAttachmentMenuControl(button)
		later = subject._attachmentSourceFocusTimer
		subject._noteAttachmentActivationGesture(("kb(laptop):downArrow",))
		self.assertTrue(later.stopped)
		self.assertIsNone(subject._attachmentSourceFocusTimer)
		# Similar controls and another app must never receive redirected focus.
		wrongTarget = Object("button", "Files and folders")
		other = Subject()
		other._buffer = Buffer(button, wrongTarget)
		other._noteAttachmentActivationGesture(("kb(laptop):enter",))
		other._noteAttachmentMenuControl(button)
		otherTimer = other._attachmentSourceFocusTimer
		otherTimer.callback(*otherTimer.args)
		self.assertFalse(wrongTarget.focused)
		API.focus = Object("edit", "Other application")
		API.focus.inChatGPT = False
		another = Subject()
		another._noteAttachmentActivationGesture(("kb(laptop):enter",))
		self.assertEqual(0.0, another._attachmentActivationAt)
		API.focus = prompt
		typing = Subject()
		typing._promptFocused = True
		typing._buffer.passThrough = True
		typing._buffer.makeTextInfo = lambda position: self.fail(
			"Typing Space in the prompt must not inspect Chromium's browse caret"
		)
		typing._noteAttachmentActivationGesture(("kb(laptop):space",))
		self.assertEqual(0.0, typing._attachmentActivationAt)
		# A browse-mode Enter can precede the add-on attaching the virtual buffer.
		# The exact expanded event must be retained until that buffer arrives.
		unattached = Subject()
		unattached._buffer = None
		unattached._promptFocused = True
		# Chromium has already moved the browse caret back to the prompt.
		prompt.treeInterceptor = Buffer(prompt, source)
		API.focus = prompt
		unattached._noteAttachmentActivationGesture(("kb(laptop):enter",))
		self.assertEqual(100.0, unattached._attachmentActivationAt)
		unattached._noteAttachmentMenuControl(button)
		self.assertIs(unattached._attachmentSourcePendingButton, button)
		self.assertIsNone(unattached._attachmentSourceFocusTimer)
		unattached._buffer = prompt.treeInterceptor
		unattached._resumeAttachmentSourceFocus()
		self.assertIsNone(unattached._attachmentSourcePendingButton)
		unattached._attachmentSourceFocusTimer.callback(
			*unattached._attachmentSourceFocusTimer.args
		)
		self.assertTrue(source.focused)
		# No Chromium state-change event is required when Enter itself identified
		# the exact Add files button and a later focus event attached the buffer.
		withoutStateEvent = Subject()
		API.focus = prompt
		prompt.treeInterceptor = withoutStateEvent._buffer
		withoutStateEvent._noteAttachmentActivationGesture(("kb(laptop):enter",))
		self.assertIs(withoutStateEvent._attachmentSourcePendingButton, button)
		withoutStateEvent._resumeAttachmentSourceFocus()
		self.assertIsNotNone(withoutStateEvent._attachmentSourceFocusTimer)

	def test_configuration_repair_covers_choices_numbers_booleans_and_strings(self):
		values = {
			"outputCommands": "invalid", "workingClickStartDelayMs": -1,
			"maximumBusyMinutes": "bad", "speech": "false", "braille": "invalid",
			"supportedAppNames": 42,
		}
		repaired = repairConfigurationValues(
			values,
			{"outputCommands": (("all", "off"), "all")},
			{"workingClickStartDelayMs": (0, 10000, 750), "maximumBusyMinutes": (1, 240, 60)},
			(("speech", True), ("braille", True)),
			(("supportedAppNames", "chatgpt"),),
		)
		self.assertEqual("all", values["outputCommands"])
		self.assertEqual(750, values["workingClickStartDelayMs"])
		self.assertEqual(60, values["maximumBusyMinutes"])
		self.assertFalse(values["speech"])
		self.assertTrue(values["braille"])
		self.assertEqual("chatgpt", values["supportedAppNames"])
		self.assertEqual(len(repaired), len(set(repaired)))

	def test_required_chatgpt_and_codex_app_hosts_survive_custom_settings(self):
		self.assertEqual("chatgpt,codex", mergeSupportedAppNames("chatgpt"))
		self.assertEqual("chatgpt,codex,customhost", mergeSupportedAppNames("CustomHost,CHATGPT"))

	def test_conversation_document_modes_exclude_nested_browser_documents(self):
		self.assertEqual("chatgpt", conversationModeFromDocumentNames(("ChatGPT",)))
		self.assertEqual("codex", conversationModeFromDocumentNames(("Codex",)))
		self.assertEqual("", conversationModeFromDocumentNames(("Purchase credits", "ChatGPT")))
		self.assertEqual("", conversationModeFromDocumentNames(("Settings",)))
		self.assertEqual("codex", conversationModeFromSwitchLabel("Switch mode, current mode: Codex"))
		self.assertEqual("chatgpt", conversationModeFromSwitchLabel("Switch mode, current mode: ChatGPT"))
		self.assertEqual("chatgpt", conversationModeFromSwitchLabel("Current mode: ChatGPT"))
		self.assertEqual("codex", conversationModeFromSwitchLabel("Switch mode: Codex"))
		self.assertEqual("", conversationModeFromSwitchLabel("ChatGPT"))
		self.assertEqual("", conversationModeFromSwitchLabel("Switch mode"))

	def test_mode_selector_probe_avoids_chromium_state_reads_on_prompt_events(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_switchControlMode")
		namespace = {
			"_roleName": lambda obj: obj.role,
			"conversationModeFromSwitchControl": conversationModeFromSwitchControl,
			"State": type("State", (), {"EXPANDED": "expanded", "COLLAPSED": "collapsed"}),
		}
		exec(compile(ast.Module(body=[function], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Prompt:
			name = "Do anything"
			role = "editabletext"
			@property
			def states(self): raise AssertionError("prompt states must not be read")
		self.assertEqual("", namespace["_switchControlMode"](Prompt()))
		class ModelButton:
			name = "Model and reasoning"
			role = "button"
			@property
			def description(self): raise AssertionError("model button is not a mode selector")
		self.assertEqual("", namespace["_switchControlMode"](ModelButton()))
		class ExplicitSelector:
			name = "Switch mode, current mode: Codex"
			role = "button"
			@property
			def description(self): raise AssertionError("explicit selector should not read description")
			@property
			def states(self): raise AssertionError("explicit selector should not read states")
		self.assertEqual("codex", namespace["_switchControlMode"](ExplicitSelector()))
		selector = type("Selector", (), {
			"name": "Switch mode", "description": "Current mode: Codex",
			"role": "button", "states": {"collapsed"},
		})()
		self.assertEqual("codex", namespace["_switchControlMode"](selector))

	def test_runtime_conversation_mode_accepts_both_modes_but_rejects_embedded_web_content(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		functions = [
			node for node in pluginTree.body
			if isinstance(node, ast.FunctionDef) and node.name in (
				"_roleName", "_conversationModeForObject", "_isConversationObject",
			)
		]
		namespace = {
			"_isChatGPTObject": lambda obj: bool(getattr(obj, "supportedApp", True)),
			"conversationModeFromDocumentNames": conversationModeFromDocumentNames,
			"isEmbeddedBrowserContainerText": browserAccess.isEmbeddedBrowserContainerText,
			"isEmbeddedBrowserContainerRole": browserAccess.isEmbeddedBrowserContainerRole,
		}
		exec(compile(ast.Module(body=functions, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class RoleName:
			def __init__(self, name): self.name = name
		class Object:
			def __init__(self, role, name="", parent=None, description="", supportedApp=True):
				self.role = RoleName(role)
				self.name = name
				self.parent = parent
				self.description = description
				self.supportedApp = supportedApp
		chatgptDocument = Object("document", "ChatGPT")
		codexDocument = Object("document", "Codex")
		self.assertEqual("chatgpt", namespace["_conversationModeForObject"](Object("button", "Thinking", chatgptDocument)))
		self.assertEqual("codex", namespace["_conversationModeForObject"](Object("button", "Thinking", codexDocument)))
		embeddedDocument = Object("document", "Purchase credits", chatgptDocument)
		self.assertFalse(namespace["_isConversationObject"](Object("button", "Buy", embeddedDocument)))
		self.assertFalse(namespace["_isConversationObject"](Object("button", "Thinking", chatgptDocument, supportedApp=False)))

	def test_conversation_event_accepts_rebuilt_main_buffer_but_rejects_embedded_browser(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin")
		method = next(node for node in pluginClass.body if isinstance(node, ast.FunctionDef) and node.name == "_eventUsesConversationBuffer")
		namespace = {
			"_isChatGPTObject": lambda obj: True,
			"_isConversationObject": lambda obj: bool(getattr(obj, "conversation", False)),
			"_isCodexPromptObject": lambda obj: bool(getattr(obj, "prompt", False)),
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		currentBuffer = object()
		subject = type("Subject", (), {"_buffer": currentBuffer})()
		rebuiltConversation = type(
			"Object", (), {"conversation": True, "prompt": False, "treeInterceptor": object(), "parent": None},
		)()
		embeddedBrowser = type(
			"Object", (), {"conversation": False, "prompt": False, "treeInterceptor": object(), "parent": None},
		)()
		self.assertTrue(namespace["_eventUsesConversationBuffer"](subject, rebuiltConversation))
		self.assertFalse(namespace["_eventUsesConversationBuffer"](subject, embeddedBrowser))

	def test_failed_settings_save_rolls_back_the_complete_import(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		panel = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "CodexStatusAnnouncerSettingsPanel"
		)
		method = next(
			node for node in panel.body
			if isinstance(node, ast.FunctionDef) and node.name == "_onImportSettings"
		)
		with tempfile.TemporaryDirectory() as directory:
			settingsPath = Path(directory) / "settings.json"
			settingsPath.write_text(json.dumps({"speech": False, "verbosity": "minimal"}), encoding="utf-8")
			class Dialog:
				def __enter__(self): return self
				def __exit__(self, *args): return False
				def ShowModal(self): return 1
				def GetPath(self): return str(settingsPath)
			class Wx:
				ID_OK = 1
				FD_OPEN = 2
				FD_FILE_MUST_EXIST = 4
				FileDialog = lambda *args, **kwargs: Dialog()
			class ConfManager:
				spec = {"codexStatusAnnouncer": {"speech": "", "verbosity": ""}}
				def __init__(self): self.saveCalls = 0
				def save(self):
					self.saveCalls += 1
					if self.saveCalls == 1:
						raise OSError("simulated save failure")
			confManager = ConfManager()
			values = {"speech": True, "verbosity": "full"}
			loaded = []
			messages = []
			namespace = {
				"wx": Wx, "Path": Path, "json": json, "CONFIG_SECTION": "codexStatusAnnouncer",
				"config": type("Config", (), {"conf": confManager})(), "_settings": lambda: values,
				"_repairConfiguration": lambda: (), "_": lambda text: text,
				"log": type("Log", (), {"error": lambda *args, **kwargs: None, "debugWarning": lambda *args, **kwargs: None})(),
				"ui": type("Ui", (), {"message": lambda self, message: messages.append(message)})(),
			}
			exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
			instance = type("Panel", (), {"_loadControlsFromConfiguration": lambda self: loaded.append(True)})()
			namespace["_onImportSettings"](instance, None)
			self.assertEqual({"speech": True, "verbosity": "full"}, values)
			self.assertEqual(2, confManager.saveCalls)
			self.assertEqual([True], loaded)
			self.assertEqual(["Settings could not be imported"], messages)

	def test_chat_action_requires_exact_normalized_accessible_title(self):
		self.assertTrue(chatTitleMatches(" My   task ", "my task"))
		self.assertTrue(chatTitleMatches("My task", "", titleFoundInsideButton=True))
		self.assertFalse(chatTitleMatches("My task", ""))
		self.assertFalse(chatTitleMatches("My task", "Open My task menu"))
		self.assertFalse(chatTitleMatches("", ""))

	def test_chat_options_button_labels_are_specific(self):
		self.assertTrue(isChatOptionsLabel("Open conversation options"))
		self.assertTrue(isChatOptionsLabel("Project chat options"))
		self.assertTrue(isChatOptionsLabel("More"))
		self.assertFalse(isChatOptionsLabel("Add files and more"))
		self.assertFalse(isChatOptionsLabel("Change permissions"))

	def test_direct_chat_actions_match_only_pin_and_archive_controls(self):
		self.assertTrue(chatActionMatches("pin", "Pin chat"))
		self.assertTrue(chatActionMatches("pin", "Unpin chat"))
		self.assertTrue(chatActionMatches("archive", "Archive chat"))
		self.assertFalse(chatActionMatches("archive", "Archive project"))
		self.assertFalse(chatActionMatches("pin", "Pin message"))

	def test_missing_direct_chat_action_stops_after_bounded_retries(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_retryDirectChatAction"
		)
		class Button:
			name = "Selected chat"
			def setFocus(self): pass
		class Subject:
			def __init__(self):
				self._pendingDirectChatAction = ("Selected chat", "archive", "codex", 0)
				self._conversationMode = "codex"
				self._conversationWindowHandle = 1234
				self._chatHistoryActionTimer = object()
			def _conversationWindowIsAvailable(self, handle): return True
			def _chatButtonObject(self, title): return Button()
			def _namedChatActionButton(self, button, action): return None
		timers = []
		messages = []
		namespace = {
			"wx": type("Wx", (), {"CallLater": staticmethod(lambda *args: timers.append(args) or object())}),
			"ui": type("Ui", (), {"message": staticmethod(messages.append)}),
			"log": type("Log", (), {
				"debugWarning": staticmethod(lambda *args, **kwargs: None),
				"info": staticmethod(lambda *args, **kwargs: None),
			})(),
			"_": lambda text: text,
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		Subject._retryDirectChatAction = namespace["_retryDirectChatAction"]
		Subject._conversationWindowOwnsForeground = lambda self, handle: True
		subject = Subject()
		for _ in range(12):
			namespace["_retryDirectChatAction"](subject)
		self.assertIsNone(subject._pendingDirectChatAction)
		self.assertEqual(11, len(timers))
		self.assertEqual(["The selected chat action could not be completed"], messages)

	def test_direct_archive_invokes_native_action_and_invalidates_history(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_retryDirectChatAction"
		)

		class ChatButton:
			def __init__(self): self.focused = 0
			def setFocus(self): self.focused += 1

		class ActionButton:
			name = "Archive chat"
			def __init__(self): self.actions = 0
			def doAction(self): self.actions += 1

		chatButton = ChatButton()
		actionButton = ActionButton()
		messages = []
		scheduled = []
		namespace = {
			"_pressControl": lambda obj: obj.doAction(),
			"ui": type("Ui", (), {"message": staticmethod(messages.append)}),
			"log": type("Log", (), {
				"debugWarning": staticmethod(lambda *args, **kwargs: None),
				"info": staticmethod(lambda *args, **kwargs: None),
			})(),
			"_": lambda text: text,
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)

		class Subject:
			def __init__(self):
				self._pendingDirectChatAction = ("Selected chat", "archive", "codex", 0)
				self._chatActionRetryTimer = object()
				self._conversationMode = "codex"
				self._conversationWindowHandle = 1234
				self._chatHistoryCacheCurrent = {"chatgpt": True, "codex": True}
				self._pendingChatHistorySnapshots = {"chatgpt": None, "codex": ("stale",)}
				self._pendingChatHistorySnapshotAt = {"chatgpt": 0.0, "codex": 12.0}
				self._bufferDirty = False
			def _conversationWindowIsAvailable(self, handle): return True
			def _chatButtonObject(self, title): return chatButton
			def _namedChatActionButton(self, button, action):
				self.resolved = (button, action)
				return actionButton
			def _schedulePoll(self, **kwargs): scheduled.append(kwargs)
			def _conversationWindowOwnsForeground(self, handle): return True

		subject = Subject()
		namespace["_retryDirectChatAction"](subject)
		self.assertEqual(1, chatButton.focused)
		self.assertEqual((chatButton, "archive"), subject.resolved)
		self.assertEqual(1, actionButton.actions)
		self.assertIsNone(subject._pendingDirectChatAction)
		self.assertFalse(subject._chatHistoryCacheCurrent["codex"])
		self.assertIsNone(subject._pendingChatHistorySnapshots["codex"])
		self.assertEqual(0.0, subject._pendingChatHistorySnapshotAt["codex"])
		self.assertTrue(subject._bufferDirty)
		self.assertEqual([{"delay": 250, "requestInspection": True}], scheduled)
		self.assertEqual(["Archive chat requested"], messages)

	def test_direct_chat_action_is_cancelled_after_mode_or_window_change(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_retryDirectChatAction"
		)
		messages = []
		namespace = {
			"ui": type("Ui", (), {"message": staticmethod(messages.append)}),
			"_": lambda text: text,
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)

		class Subject:
			_pendingDirectChatAction = ("Selected chat", "archive", "codex", 3)
			_chatActionRetryTimer = object()
			_conversationMode = ""
			_conversationWindowHandle = 1234
			def _conversationWindowIsAvailable(self, handle): return True
			def _chatButtonObject(self, title):
				raise AssertionError("a stale chat action must not touch the old buffer")
			def _conversationWindowOwnsForeground(self, handle): return True

		subject = Subject()
		namespace["_retryDirectChatAction"](subject)
		self.assertIsNone(subject._pendingDirectChatAction)
		self.assertEqual(
			["Chat action cancelled because the ChatGPT view changed or closed"],
			messages,
		)

	def test_starting_direct_chat_action_cancels_an_old_retry_timer(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_startDirectChatAction"
		)
		class Timer:
			def __init__(self): self.stopped = False
			def Stop(self): self.stopped = True
		class Subject:
			def __init__(self):
				self.oldTimer = Timer()
				self._conversationWindowHandle = 1234
				self._chatActionRetryTimer = self.oldTimer
				self._pendingDirectChatAction = None
				self._conversationMode = "codex"
				self.retryCount = 0
			def _retryDirectChatAction(self): self.retryCount += 1
		namespace = {}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		subject = Subject()
		namespace["_startDirectChatAction"](subject, "Selected chat", "archive")
		self.assertTrue(subject.oldTimer.stopped)
		self.assertIsNone(subject._chatActionRetryTimer)
		self.assertEqual(("Selected chat", "archive", "codex", 0), subject._pendingDirectChatAction)
		self.assertEqual(1, subject.retryCount)

	def test_permission_prompt_and_decision_labels_are_narrow(self):
		self.assertTrue(isPermissionPromptText("Permission required. Allow this command? Deny"))
		self.assertTrue(isPermissionPromptText("This action requires your approval"))
		self.assertFalse(isPermissionPromptText("Change permissions"))
		self.assertTrue(isPermissionDecisionLabel("Allow once"))
		self.assertTrue(isPermissionDecisionLabel("Deny and tell Codex what to do"))
		self.assertFalse(isPermissionDecisionLabel("Change permissions"))

	def test_usage_limit_notice_uses_the_observed_error_and_rejects_settings_text(self):
		observed = (
			"You've hit your usage limit. Upgrade to Pro "
			"(https://chatgpt.com/explore/pro), visit "
			"https://chatgpt.com/codex/settings/usage to purchase more credits "
			"or try again at 9:45 PM."
		)
		self.assertEqual(
			"Usage limit reached. You can upgrade to Pro, purchase more credits in "
			"ChatGPT usage settings, or try again at 9:45 PM.",
			usageLimitNotice(observed),
		)
		self.assertEqual(
			"Usage limit reached. You can try again in 12 minutes.",
			usageLimitNotice("You have reached your weekly usage limit. Try again in 12 minutes."),
		)
		self.assertEqual(
			"Usage limit reached. Check ChatGPT usage settings for reset details.",
			usageLimitNotice("Not enough credits"),
		)
		percentageBanner = (
			"0% usage remainingDismiss usage alert Resets every week · "
			"Next reset is on Sep 10 at 5:25 PM Usage consumed Add credits Upgrade"
		)
		self.assertEqual(
			"Usage limit reached. You can upgrade your plan, purchase more credits in "
			"ChatGPT usage settings, or try again on Sep 10 at 5:25 PM.",
			usageLimitNotice(percentageBanner),
		)
		self.assertEqual(
			"Usage limit reached. You can purchase more credits in ChatGPT usage settings.",
			usageLimitNotice("100% usage consumed. Add credits"),
		)
		self.assertEqual("", usageLimitNotice(percentageBanner.replace("0%", "6%")))
		self.assertEqual("", usageLimitNotice("Open usage limits and credits settings"))
		self.assertEqual("", usageLimitNotice("Usage remaining: 20 percent"))
		self.assertEqual(("", ""), statusDetails(observed))
		translationTemplate = TRANSLATION_TEMPLATE_PATH.read_text(encoding="utf-8")
		self.assertIn('msgid "Usage limit reached"', translationTemplate)
		self.assertIn('msgid "purchase more credits in ChatGPT usage settings"', translationTemplate)

	def test_usage_limit_notice_stops_working_feedback_and_is_announced_once(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in tree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_applyUsageLimitNotice"
		)

		class Logger:
			def info(self, *args, **kwargs): pass

		class Subject:
			def __init__(self):
				self._pluginProgressOwnedBusy = {"plugin"}
				self._pendingResponseCompletionAt = 12.0
				self._pendingUserMessageIncrease = True
				self._stopControlVisible = True
				self._promptHadText = True
				self._lastScannedLabel = "Working"
				self._lastLabel = "Working"
				self._latestResponseMarker = 123
				self._responseMarkerInitialized = True
				self._busy = True
				self._active = True
				self._activeCategory = "working"
				self._usageLimitActive = False
				self._lastUsageLimitNotice = ""
				self._latestMessage = "Working"
				self._latestFullMessage = "Working"
				self.spoken = []
				self.states = []

			def _setBusy(self, busy, reason):
				self._busy = bool(busy)
				self.states.append((bool(busy), reason))

			def _speakOnce(self, *args, **kwargs):
				self.spoken.append((args, kwargs))

		namespace = {"log": Logger()}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		subject = Subject()
		notice = "Usage limit reached. You can try again at 9:45 PM."
		self.assertTrue(namespace["_applyUsageLimitNotice"](subject, notice))
		self.assertFalse(subject._busy)
		self.assertFalse(subject._active)
		self.assertEqual("attention", subject._activeCategory)
		self.assertEqual(set(), subject._pluginProgressOwnedBusy)
		self.assertEqual(0.0, subject._pendingResponseCompletionAt)
		self.assertFalse(subject._promptHadText)
		self.assertEqual("", subject._lastScannedLabel)
		self.assertEqual("", subject._lastLabel)
		self.assertIsNone(subject._latestResponseMarker)
		self.assertFalse(subject._responseMarkerInitialized)
		self.assertEqual([(False, "usage limit reached")], subject.states)
		self.assertEqual(1, len(subject.spoken))
		self.assertEqual("urgent", subject.spoken[0][1]["priority"])
		self.assertTrue(namespace["_applyUsageLimitNotice"](subject, notice))
		self.assertEqual(1, len(subject.spoken))

	def test_split_usage_limit_popover_is_bounded_and_unrelated_events_are_local(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in tree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in {
				"_usageLimitTextFromObject", "_usageLimitObjectIsPopup", "_announceUsageLimit",
			}
		]
		namespace = {
			"_isChatGPTObject": lambda obj: True,
			"_roleName": lambda obj: obj.role,
			"re": re,
			"usageLimitNotice": usageLimitNotice,
			"_": lambda text: text,
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)

		class Object:
			def __init__(self, name="", role="section", parent=None):
				self.name = name
				self.value = ""
				self.description = ""
				self.role = role
				self.parent = parent
				self.firstChild = None
				self.next = None

		dialog = Object(role="dialog")
		message = Object("You've hit your usage limit.", parent=dialog)
		upgrade = Object("Upgrade to Pro", role="button", parent=dialog)
		credits = Object("Purchase more credits", role="button", parent=dialog)
		retry = Object("Try again at 9:45 PM.", parent=dialog)
		dialog.firstChild = message
		message.next = upgrade
		upgrade.next = credits
		credits.next = retry

		class Subject:
			def __init__(self):
				self.notices = []

			def _usageLimitTextFromObject(self, obj):
				return namespace["_usageLimitTextFromObject"](self, obj)

			def _usageLimitObjectIsPopup(self, obj):
				return namespace["_usageLimitObjectIsPopup"](self, obj)

			def _applyUsageLimitNotice(self, notice):
				self.notices.append(notice)
				return True

		subject = Subject()
		self.assertTrue(namespace["_announceUsageLimit"](subject, message))
		self.assertEqual(
			"Usage limit reached. You can upgrade to Pro, purchase more credits in "
			"ChatGPT usage settings, or try again at 9:45 PM.",
			subject.notices[0],
		)

		percentageDialog = Object(role="dialog")
		remaining = Object("0% usage remaining", parent=percentageDialog)
		reset = Object("Next reset is on Sep 10 at 5:25 PM", parent=percentageDialog)
		addCredits = Object("Add credits", role="button", parent=percentageDialog)
		upgradePlan = Object("Upgrade", role="button", parent=percentageDialog)
		percentageDialog.firstChild = remaining
		remaining.next = reset
		reset.next = addCredits
		addCredits.next = upgradePlan
		percentageSubject = Subject()
		self.assertTrue(namespace["_announceUsageLimit"](percentageSubject, addCredits))
		self.assertEqual(
			"Usage limit reached. You can upgrade your plan, purchase more credits in "
			"ChatGPT usage settings, or try again on Sep 10 at 5:25 PM.",
			percentageSubject.notices[0],
		)

		class LocalOnlySubject(Subject):
			def _usageLimitTextFromObject(self, obj):
				raise AssertionError("unrelated events must not walk ancestors")

		self.assertFalse(namespace["_announceUsageLimit"](LocalOnlySubject(), Object("Working")))

	def test_plugin_install_progress_is_scoped_parsed_and_bucketed(self):
		self.assertEqual(
			("plugin", 37, 30),
			pluginInstallProgress("Installing plugin 37%"),
		)
		self.assertEqual(
			("connector", 100, 100),
			pluginInstallProgress("Connector installation 100 percent"),
		)
		self.assertEqual(
			("plugin", None, None),
			pluginInstallProgress("Plugin installation in progress"),
		)
		self.assertEqual(
			("plugin", 100, 100),
			pluginInstallProgress("Plugin installation complete"),
		)
		self.assertIsNone(pluginInstallProgress("Downloading model 50%"))

	def test_current_activity_summary_covers_silent_background_periods(self):
		self.assertEqual("Running Outlook test", currentActivitySummary(True, "tool", "Running Outlook test", 45))
		self.assertEqual("Codex is still using tools, 45 seconds", currentActivitySummary(True, "tool", "", 45))
		self.assertEqual("Codex is still running commands", currentActivitySummary(True, "command", "", 0))
		self.assertEqual("Codex is idle", currentActivitySummary(False, "other", "", 0))
		self.assertEqual("Codex is still working, 3 minutes 20 seconds", currentActivitySummary(True, "working", "", 200))
		self.assertEqual(
			"ChatGPT is still thinking, 12 seconds",
			currentActivitySummary(True, "thinking", "", 12, agentName="ChatGPT"),
		)

	def test_elapsed_duration_uses_speech_friendly_units(self):
		self.assertEqual("0 seconds", formatElapsedDuration(0))
		self.assertEqual("59 seconds", formatElapsedDuration(59))
		self.assertEqual("1 minute", formatElapsedDuration(60))
		self.assertEqual("1 minute 25 seconds", formatElapsedDuration(85))
		self.assertEqual("3 minutes 20 seconds", formatElapsedDuration(200))
		self.assertEqual("1 hour 1 minute 1 second", formatElapsedDuration(3661))

	def test_background_activity_names_preserve_file_work_without_claiming_finished_work_continues(self):
		self.assertEqual("Editing code", backgroundActivityName("file", "Editing code: core.py"))
		self.assertEqual("Checking files", backgroundActivityName("file", "Checking files"))
		self.assertEqual("Processing", backgroundActivityName("file", "Reading finished"))
		self.assertEqual("Command", backgroundActivityName("command", "Running command"))
		self.assertEqual("Checking files", backgroundActivityName("command", "Reading file core.py"))
		self.assertEqual("File operations", backgroundActivityName("file", ""))

	def test_conversation_detection_excludes_settings_documents(self):
		self.assertTrue(looksLikeCodexConversation("Main landmark Do anything multiline edit"))
		self.assertTrue(looksLikeCodexConversation("Message Codex"))
		self.assertTrue(looksLikeCodexConversation("Message ChatGPT"))
		self.assertTrue(looksLikeCodexConversation("Send a message"))
		self.assertFalse(looksLikeCodexConversation("Settings Account Archived chats"))

	def test_blank_chat_detection_ignores_existing_conversation_buffer_refreshes(self):
		self.assertTrue(looksLikeBlankCodexConversation("Main landmark Do anything New chat"))
		self.assertFalse(looksLikeBlankCodexConversation("Do anything User message 3 Response complete: done"))
		self.assertFalse(looksLikeBlankCodexConversation("Do anything ChatGPT said: existing answer"))
		self.assertFalse(looksLikeBlankCodexConversation("Settings General Archived chats"))

	def test_chat_history_snapshot_requires_settle_and_confirmation(self):
		self.assertEqual(
			"settle",
			chatHistorySnapshotDecision(0.1, 0.75, ("Chat",), (), False, None, 0.0, 0.25),
		)
		self.assertEqual(
			"otherMode",
			chatHistorySnapshotDecision(1.0, 0.75, ("Chat",), ("Chat",), True, None, 0.0, 0.25),
		)
		self.assertEqual(
			"confirm",
			chatHistorySnapshotDecision(1.0, 0.75, ("Chat",), (), False, None, 0.0, 0.25),
		)
		self.assertEqual(
			"confirm",
			chatHistorySnapshotDecision(1.0, 0.75, ("Chat",), (), False, ("Chat",), 0.1, 0.25),
		)
		self.assertEqual(
			"publish",
			chatHistorySnapshotDecision(1.0, 0.75, ("Chat",), (), False, ("Chat",), 0.3, 0.25),
		)

	def test_unified_recents_are_partitioned_by_active_codex_titles(self):
		unified = ("ChatGPT only", "Shared title", "Another Codex task")
		codex = (" shared   title ", "Another Codex task")
		self.assertEqual(
			("ChatGPT only",),
			modeSpecificRecentChatTitles("chatgpt", unified, codex),
		)
		self.assertEqual(
			("Shared title", "Another Codex task"),
			modeSpecificRecentChatTitles("codex", unified, codex),
		)
		self.assertEqual((), modeSpecificRecentChatTitles("unknown", unified, codex))

	def test_history_mode_uia_probe_runs_off_main_thread_and_applies_exact_button(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in {
				"_queueConversationModeProbe", "_completeConversationModeProbe", "_setConversationMode",
			}
		]
		conditionCalls = []
		scheduled = []
		expansions = []
		focusedControls = []
		queriedInterfaces = []
		expandCollapseState = 0
		expandCollapseInterface = object()
		class ExpandCollapsePattern:
			@property
			def CurrentExpandCollapseState(self): return expandCollapseState
			def Expand(self): expansions.append(True)
		class Pattern:
			def QueryInterface(self, interface):
				queriedInterfaces.append(interface)
				return ExpandCollapsePattern()
		class Control:
			CurrentName = "Switch mode, current mode: Codex"
			helpText = None
			@property
			def CurrentHelpText(self):
				if self.helpText is None:
					raise RuntimeError("optional UIA help text unavailable")
				return self.helpText
			@property
			def CurrentAutomationId(self):
				raise AssertionError("optional UIA automation ID must not be read")
			def SetFocus(self): focusedControls.append(self.CurrentName)
			def GetCurrentPattern(self, patternId):
				self.patternId = patternId
				return Pattern()
		class Root:
			def FindFirst(self, scope, condition):
				self.scope = scope
				self.condition = condition
				return Control()
		class Client:
			def ElementFromHandleBuildCache(self, handle, cache):
				self.handle = handle
				return Root()
			def createPropertyCondition(self, propertyId, value):
				conditionCalls.append((propertyId, value))
				return (propertyId, value)
			def createOrConditionFromArray(self, conditions): return ("or", tuple(conditions))
			def createAndConditionFromArray(self, conditions): return ("and", tuple(conditions))
		client = Client()
		workerCallbacks = []
		class WorkerQueue:
			fail = False
			def put_nowait(self, callback):
				if self.fail:
					raise RuntimeError("worker unavailable")
				workerCallbacks.append(callback)
		workerQueue = WorkerQueue()
		fakeUIAHandler = type("UIAHandler", (), {
			"handler": type("Handler", (), {
				"clientObject": client,
				"baseCacheRequest": object(),
				"MTAThreadQueue": workerQueue,
			})(),
			"UIA_NamePropertyId": 1,
			"UIA_ControlTypePropertyId": 2,
			"UIA_ButtonControlTypeId": 3,
			"TreeScope_Descendants": 4,
			"UIA_ExpandCollapsePatternId": 6,
			"IUIAutomationExpandCollapsePattern": expandCollapseInterface,
		})
		namespace = {
			"CHATGPT_PROMPT_EDITOR_CLASS": core.CHATGPT_PROMPT_EDITOR_CLASS, "MODE_SWITCH_BUTTON_LABELS": core.MODE_SWITCH_BUTTON_LABELS, "SOURCES_MENU_BUTTON_NAME": core.SOURCES_MENU_BUTTON_NAME, "ADD_FILES_BUTTON_NAME": core.ADD_FILES_BUTTON_NAME,
			"_": lambda text: text,
			"conversationModeFromSwitchLabel": conversationModeFromSwitchLabel,
			"conversationModeFromSwitchControl": conversationModeFromSwitchControl,
			"time": type("Time", (), {"monotonic": staticmethod(lambda: 100.0)}),
			"queueHandler": type("QueueHandler", (), {
				"eventQueue": object(),
				"queueFunction": staticmethod(lambda queue, function, *args: function(*args)),
			}),
			"log": type("Log", (), {
				"debug": staticmethod(lambda *args, **kwargs: None),
				"debugWarning": staticmethod(lambda *args, **kwargs: None),
			}),
			"_activePluginInstance": None,
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			_conversationModeProbeGeneration = 0
			_conversationModeProbePendingGeneration = 0
			_conversationWindowHandle = 1234
			_lastConversationModeProbeAt = 0.0
			_conversationMode = "chatgpt"
			_conversationModeObserved = False
			timings = []
			def _recordOperationTiming(self, operation, durationMs):
				self.timings.append((operation, durationMs))
			def _completeConversationModeProbe(self, *args):
				return namespace["_completeConversationModeProbe"](self, *args)
			def _setConversationMode(self, mode, reason, authoritative=False):
				changed = mode != self._conversationMode
				self._conversationMode = mode
				self._conversationModeObserved = self._conversationModeObserved or authoritative
				return changed
			def _schedulePoll(self, delay=150, requestInspection=True):
				scheduled.append((delay, requestInspection))
			def _schedulePendingChatHistoryOpen(self, delay):
				return False
		subject = Subject()
		namespace["_activePluginInstance"] = subject
		previousUIAHandler = sys.modules.get("UIAHandler")
		sys.modules["UIAHandler"] = fakeUIAHandler
		try:
			self.assertTrue(namespace["_queueConversationModeProbe"](subject, "test verification"))
			self.assertEqual("chatgpt", subject._conversationMode)
			self.assertFalse(subject._conversationModeObserved)
			self.assertNotEqual(0, subject._conversationModeProbePendingGeneration)
			self.assertEqual(1, len(workerCallbacks))
			workerCallbacks.pop()()
		finally:
			if previousUIAHandler is None:
				del sys.modules["UIAHandler"]
			else:
				sys.modules["UIAHandler"] = previousUIAHandler
		self.assertEqual("codex", subject._conversationMode)
		self.assertTrue(subject._conversationModeObserved)
		self.assertEqual([(50, True)], scheduled)
		self.assertIn((1, "Switch mode, current mode: ChatGPT"), conditionCalls)
		self.assertIn((1, "Switch mode, current mode: Codex"), conditionCalls)
		self.assertIn((2, 3), conditionCalls)
		activationResults = []
		class ActivationSubject:
			_conversationModeProbeGeneration = 0
			_conversationModeProbePendingGeneration = 0
			_conversationWindowHandle = 1234
			_lastConversationModeProbeAt = 0.0
			def _completeConversationModeProbe(self, *args): activationResults.append(args)
		activationSubject = ActivationSubject()
		previousUIAHandler = sys.modules.get("UIAHandler")
		sys.modules["UIAHandler"] = fakeUIAHandler
		try:
			self.assertTrue(namespace["_queueConversationModeProbe"](
				activationSubject, "test selector open", openSelector=True,
			))
			self.assertEqual(
				activationSubject._conversationModeProbePendingGeneration,
				activationSubject._conversationModeProbeActivationGeneration,
			)
			workerCallbacks.pop()()
		finally:
			if previousUIAHandler is None:
				del sys.modules["UIAHandler"]
			else:
				sys.modules["UIAHandler"] = previousUIAHandler
		self.assertEqual([True], expansions)
		self.assertEqual(["Switch mode, current mode: Codex"], focusedControls)
		class FailedSubject:
			_conversationModeProbeGeneration = 0
			_conversationModeProbePendingGeneration = 0
			_conversationModeProbeActivationGeneration = 0
			_conversationWindowHandle = 1234
		previousUIAHandler = sys.modules.get("UIAHandler")
		sys.modules["UIAHandler"] = fakeUIAHandler
		workerQueue.fail = True
		try:
			failedSubject = FailedSubject()
			self.assertFalse(namespace["_queueConversationModeProbe"](
				failedSubject, "worker unavailable", openSelector=True,
			))
		finally:
			workerQueue.fail = False
			if previousUIAHandler is None:
				del sys.modules["UIAHandler"]
			else:
				sys.modules["UIAHandler"] = previousUIAHandler
		self.assertEqual(0, failedSubject._conversationModeProbePendingGeneration)
		self.assertEqual(0, failedSubject._conversationModeProbeActivationGeneration)
		self.assertEqual(0.0, failedSubject._modeProbeStartedAt)
		# If Chromium moves the current mode to help text, still resolve it;
		# ordinary exact labels must not depend on optional UIA properties.
		Control.CurrentName = "Switch mode"
		Control.helpText = "Current mode: Codex"
		descriptionSubject = Subject()
		namespace["_activePluginInstance"] = descriptionSubject
		previousUIAHandler = sys.modules.get("UIAHandler")
		sys.modules["UIAHandler"] = fakeUIAHandler
		try:
			self.assertTrue(namespace["_queueConversationModeProbe"](descriptionSubject, "description fallback"))
			workerCallbacks.pop()()
		finally:
			if previousUIAHandler is None:
				del sys.modules["UIAHandler"]
			else:
				sys.modules["UIAHandler"] = previousUIAHandler
		self.assertEqual("codex", descriptionSubject._conversationMode)
		Control.CurrentName = "Switch mode, current mode: Codex"
		Control.helpText = None
		self.assertIn(fakeUIAHandler.IUIAutomationExpandCollapsePattern, queriedInterfaces)
		self.assertEqual((True, True), activationResults[0][-2:])
		# A second press after an interrupted attempt can find the menu still open.
		# It must continue to item selection without calling Expand again.
		expandCollapseState = 1
		expansions.clear()
		openMenuResults = []
		class OpenMenuSubject:
			_conversationModeProbeGeneration = 0
			_conversationModeProbePendingGeneration = 0
			_conversationWindowHandle = 1234
			_lastConversationModeProbeAt = 0.0
			def _completeConversationModeProbe(self, *args): openMenuResults.append(args)
		openMenuSubject = OpenMenuSubject()
		previousUIAHandler = sys.modules.get("UIAHandler")
		sys.modules["UIAHandler"] = fakeUIAHandler
		try:
			self.assertTrue(namespace["_queueConversationModeProbe"](
				openMenuSubject, "test already expanded selector", openSelector=True,
			))
			workerCallbacks.pop()()
		finally:
			if previousUIAHandler is None:
				del sys.modules["UIAHandler"]
			else:
				sys.modules["UIAHandler"] = previousUIAHandler
		self.assertEqual([], expansions)
		self.assertEqual((True, True), openMenuResults[0][-2:])
		# An already-expanded selector keeps popup focus instead of moving it back
		# to the header button.
		self.assertEqual(["Switch mode, current mode: Codex"], focusedControls)

		callbackActions = []
		class SelectorCallbackSubject:
			_conversationModeProbeGeneration = 1
			_conversationModeProbePendingGeneration = 1
			_conversationModeProbeActivationGeneration = 1
			_conversationWindowHandle = 1234
			def _setConversationMode(self, mode, reason, authoritative=False):
				callbackActions.append((mode, reason, authoritative))
			def _announceConversationModeNotice(self, message): callbackActions.append(message)
		selectorCallbackSubject = SelectorCallbackSubject()
		namespace["_activePluginInstance"] = selectorCallbackSubject
		namespace["_completeConversationModeProbe"](
			selectorCallbackSubject, 1, 1234, "codex", "test selector callback", True, True,
		)
		self.assertEqual(("codex", "test selector callback", True), callbackActions[0])
		self.assertEqual(
			"Codex mode. Mode selector open. Use Up or Down Arrow and Enter to choose a mode.",
			callbackActions[1],
		)
		self.assertEqual(100.0, selectorCallbackSubject._modeSelectorOpenedAt)

		pluginSource = PLUGIN_PATH.read_text(encoding="utf-8")
		self.assertIn('self._queueConversationModeProbe("history mode verification")', pluginSource)
		self.assertIn('self._queueConversationModeProbe("mode switch UI Automation retry")', pluginSource)
		self.assertIn('self._queueConversationModeProbe("mode selector selection confirmation")', pluginSource)
		self.assertIn('self._observeConversationModeControl(obj, "mode switch name event")', pluginSource)
		self.assertIn('self._observeConversationModeControl(obj, "mode switch show event")', pluginSource)
		self.assertIn('self._observeConversationModeControl(obj, "mode switch state event")', pluginSource)
		self.assertNotIn("def _selectConversationModeMenuItem", pluginSource)
		self.assertNotIn("_pendingConversationModeSwitch", pluginSource)

	def test_one_history_gesture_waits_for_mode_and_cache_then_opens_automatically(self):
		pluginSource = PLUGIN_PATH.read_text(encoding="utf-8")
		pluginTree = ast.parse(pluginSource)
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		wanted = {
			"_cancelPendingChatHistoryOpen", "_schedulePendingChatHistoryOpen",
			"_requestChatHistoryOpen", "_continuePendingChatHistoryOpen",
		}
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in wanted
		]
		self.assertEqual(wanted, {node.name for node in methods})
		messages = []
		class Timer:
			def __init__(self, delay, callback):
				self.delay = delay
				self.callback = callback
				self.stopped = False
			def Stop(self): self.stopped = True
		class Wx:
			@staticmethod
			def CallLater(delay, callback): return Timer(delay, callback)
		class Api:
			@staticmethod
			def getFocusObject(): return "chatgpt"
		namespace = {
			"wx": Wx, "api": Api, "_isChatGPTObject": lambda obj: obj == "chatgpt",
			"time": type("Time", (), {"monotonic": staticmethod(lambda: 100.0)}),
			"ui": type("Ui", (), {"message": staticmethod(messages.append)}),
			"_": lambda text: text,
			"log": type("Log", (), {"debugWarning": staticmethod(lambda *args, **kwargs: None)}),
			"CHAT_HISTORY_OPEN_RETRY_MILLISECONDS": 150,
			"CHAT_HISTORY_OPEN_TIMEOUT_SECONDS": 5.0,
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			def __init__(self):
				self._buffer = object()
				self._conversationWindowHandle = 1234
				self._conversationModeObserved = False
				self._conversationMode = ""
				self._conversationModeProbePendingGeneration = 0
				self._chatHistoryCacheCurrent = {"chatgpt": False, "codex": False}
				self._pendingChatHistoryExpansion = None
				self._chatHistoryOpenTimer = None
				self._pendingChatHistoryOpen = None
				self._bufferDirty = False
				self.polls = []
				self.probes = []
				self.opened = []
			def _cancelPendingChatHistoryOpen(self):
				return namespace["_cancelPendingChatHistoryOpen"](self)
			def _schedulePendingChatHistoryOpen(self, delay):
				return namespace["_schedulePendingChatHistoryOpen"](self, delay)
			def _continuePendingChatHistoryOpen(self):
				return namespace["_continuePendingChatHistoryOpen"](self)
			def _schedulePoll(self, delay=150, requestInspection=True):
				self.polls.append((delay, requestInspection))
			def _queueConversationModeProbe(self, reason):
				self.probes.append(reason)
				self._conversationModeProbePendingGeneration = 1
				return True
			def _startChatHistoryExpansion(self, mode): return False
			def _showChatHistoryDialog(self, mode):
				self.opened.append(mode)
				self._cancelPendingChatHistoryOpen()
				return True
		subject = Subject()
		self.assertTrue(namespace["_requestChatHistoryOpen"](subject))
		self.assertEqual(["Opening chat history"], messages)
		firstTimer = subject._chatHistoryOpenTimer
		self.assertEqual(0, firstTimer.delay)
		firstTimer.callback()
		self.assertEqual(["history mode verification"], subject.probes)
		self.assertEqual([], subject.opened)
		self.assertEqual(150, subject._chatHistoryOpenTimer.delay)
		# Mode completion resumes the same request; a still-settling cache remains
		# automatic and does not ask the user to press the gesture again.
		subject._conversationModeObserved = True
		subject._conversationMode = "chatgpt"
		subject._conversationModeProbePendingGeneration = 0
		subject._chatHistoryOpenTimer.callback()
		self.assertEqual([], subject.opened)
		subject._chatHistoryCacheCurrent["chatgpt"] = True
		subject._chatHistoryOpenTimer.callback()
		self.assertEqual(["chatgpt"], subject.opened)
		self.assertIsNone(subject._pendingChatHistoryOpen)
		self.assertNotIn("Try history again in a moment", pluginSource)

	def test_mode_selector_close_verifies_selected_mode_once(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef)
			and node.name == "_confirmConversationModeAfterSelector"
		)
		namespace = {
			"time": type("Time", (), {"monotonic": staticmethod(lambda: 100.0)}),
			"MODE_SELECTOR_CONFIRM_TIMEOUT_SECONDS": 30.0,
			"_isChatGPTObject": lambda obj: bool(getattr(obj, "inChatGPT", True)),
			"conversationModeFromSwitchLabel": conversationModeFromSwitchLabel,
			"_switchControlMode": lambda obj: conversationModeFromSwitchControl(
				getattr(obj, "name", ""), "", getattr(obj, "role", ""), False,
			),
			"_roleName": lambda obj: getattr(obj, "role", ""),
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			def __init__(self):
				self._modeSelectorOpenedAt = 90.0
				self.queued = []
				self.allowQueue = True
			def _queueConversationModeProbe(self, reason):
				self.queued.append(reason)
				return self.allowQueue
		subject = Subject()
		selector = type("Object", (), {
			"name": "Switch mode, current mode: Codex", "role": "button", "inChatGPT": True,
		})()
		menuItem = type("Object", (), {
			"name": "ChatGPT Create, learn, and explore", "role": "menuitem", "inChatGPT": True,
		})()
		document = type("Object", (), {
			"name": "Current conversation", "role": "document", "inChatGPT": True,
		})()
		outside = type("Object", (), {
			"name": "Other app", "role": "document", "inChatGPT": False,
		})()
		self.assertFalse(namespace["_confirmConversationModeAfterSelector"](subject, selector))
		self.assertFalse(namespace["_confirmConversationModeAfterSelector"](subject, menuItem))
		self.assertFalse(namespace["_confirmConversationModeAfterSelector"](subject, outside))
		self.assertEqual([], subject.queued)
		self.assertTrue(namespace["_confirmConversationModeAfterSelector"](subject, document))
		self.assertEqual(["mode selector selection confirmation"], subject.queued)
		self.assertEqual(0.0, subject._modeSelectorOpenedAt)
		# A temporarily occupied UIA worker leaves the confirmation armed for the
		# next eligible focus event rather than silently accepting stale mode state.
		subject._modeSelectorOpenedAt = 90.0
		subject.allowQueue = False
		self.assertFalse(namespace["_confirmConversationModeAfterSelector"](subject, document))
		self.assertEqual(90.0, subject._modeSelectorOpenedAt)
		# An abandoned selector expires without causing later unrelated navigation
		# to trigger a mode query.
		subject.allowQueue = True
		subject._modeSelectorOpenedAt = 69.0
		self.assertFalse(namespace["_confirmConversationModeAfterSelector"](subject, document))
		self.assertEqual(0.0, subject._modeSelectorOpenedAt)

	def test_native_windows_file_dialog_is_rejected_before_chromium_parent_traversal(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		method = next(
			node for node in tree.body
			if isinstance(node, ast.FunctionDef) and node.name == "_isNativeCommonDialogObject"
		)
		class WinUser:
			GA_ROOT = 2
			@staticmethod
			def getAncestor(handle, kind): return 20
			@staticmethod
			def getClassName(handle): return "#32770" if handle == 20 else "Chrome_WidgetWin_1"
		namespace = {"winUser": WinUser}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		self.assertTrue(namespace["_isNativeCommonDialogObject"](
			type("DialogControl", (), {"windowHandle": 10})(),
		))
		self.assertFalse(namespace["_isNativeCommonDialogObject"](
			type("NoWindow", (), {"windowHandle": 0})(),
		))
		WinUser.getClassName = staticmethod(lambda handle: "Chrome_WidgetWin_1")
		self.assertFalse(namespace["_isNativeCommonDialogObject"](
			type("ConversationControl", (), {"windowHandle": 10})(),
		))

	def test_buffer_backend_refresh_preserves_task_state_but_blank_chat_resets_it(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in (
				"_setConversationMode", "_rememberBuffer", "_announceChatOpened",
			)
		]
		method = next(node for node in methods if node.name == "_rememberBuffer")
		methodSource = ast.get_source_segment(PLUGIN_PATH.read_text(encoding="utf-8"), method)
		self.assertIn("POSITION_LAST", methodSource)
		self.assertIn("_extendScanStart(position, BUFFER_TAIL_SCAN_CHARACTERS)", methodSource)
		self.assertNotIn("makeTextInfo(textInfos.POSITION_ALL)", methodSource)
		self.assertLess(
			methodSource.index("_conversationWindowIsAvailable"),
			methodSource.index("if explicitMode:"),
		)
		class TextInfo:
			def __init__(self, text): self.text = text
			def move(self, unit, count, endPoint=None): return max(-len(self.text), count)
		class Buffer:
			def __init__(self, text): self.text = text
			def makeTextInfo(self, position): return TextInfo(self.text)
		class Api:
			focus = type("Focus", (), {"inChatGPT": True})()
			@classmethod
			def getFocusObject(cls): return cls.focus
		class Subject:
			def __init__(self, oldBuffer):
				self._buffer = oldBuffer
				self._conversationMode = "chatgpt"
				self._conversationModeObserved = False
				self._conversationModeChangedAt = 0.0
				self._conversationWindowHandle = 1234
				self._chatHistoryCacheCurrent = {"chatgpt": False, "codex": False}
				self._ambiguousRecentChatTitles = {"chatgpt": set(), "codex": set()}
				self._pendingChatHistorySnapshots = {"chatgpt": None, "codex": None}
				self._pendingChatHistorySnapshotAt = {"chatgpt": 0.0, "codex": 0.0}
				self._chatHistoryMoreAvailable = {"chatgpt": False, "codex": False}
				self._recentHistoryShowMoreOrdinals = {"chatgpt": 0, "codex": 0}
				self._unifiedRecentCounts = {"chatgpt": 0, "codex": 0}
				self._chatHistoryScanGenerations = {"chatgpt": 0, "codex": 0}
				self._pendingChatHistoryAction = None
				self._chatHistoryActionTimer = None
				self._chatHistoryDialog = None
				self._pendingOpenedChatTitle = ""
				self._pendingOpenedChatAt = 0.0
				self._lastChatOpened = None
				self._documentSwitchCount = 2
				self._monitoringAnnounced = True
				self._latestMessage = self._latestFullMessage = "Running command"
				self._lastRejectedBufferLogAt = 0.0
				self.windowAvailable = True
				self.resets = []
				self.spoken = []
			def _bufferCandidates(self, obj): return getattr(obj, "candidates", (obj,))
			def _conversationWindowHandleFrom(self, obj, buffer): return 1234
			def _conversationWindowIsAvailable(self, handle): return self.windowAvailable
			def _windowProcessId(self, handle): return 4321
			def _chatGPTAppVersion(self): return "package 1.0"
			def _scheduleCompatibilityCheck(self): pass
			def _queueConversationModeProbe(self, reason): return False
			def _schedulePendingChatHistoryOpen(self, delay): return False
			def _setConversationMode(self, mode, reason, authoritative=False):
				return namespace["_setConversationMode"](self, mode, reason, authoritative)
			def _announceChatOpened(self, title, windowHandle):
				namespace["_announceChatOpened"](self, title, windowHandle)
			def _resetTaskState(self, reason): self.resets.append(reason)
			def _cancelChatHistoryExpansion(self): pass
			def _speakOnce(self, message, *args, **kwargs): self.spoken.append(message)
		namespace = {
			"_isChatGPTObject": lambda obj: bool(getattr(obj, "inChatGPT", True)),
			"_isNativeCommonDialogObject": lambda obj: bool(getattr(obj, "nativeDialog", False)),
			"api": Api, "pendingChatTitle": pendingChatTitle,
			"conversationModeFromSwitchLabel": conversationModeFromSwitchLabel,
			"_switchControlMode": lambda obj: "",
			"_isConversationObject": lambda obj: not bool(getattr(obj, "embeddedBrowser", False)),
			"_conversationModeForObject": lambda obj: "" if bool(getattr(obj, "embeddedBrowser", False)) else getattr(obj, "mode", "chatgpt"),
			"_isCodexPromptObject": lambda obj: False,
			"_isEmbeddedBrowserObject": lambda obj: bool(getattr(obj, "embeddedBrowser", False)),
			"looksLikeBlankCodexConversation": looksLikeBlankCodexConversation,
			"looksLikeCodexConversation": looksLikeCodexConversation,
			"BUFFER_TAIL_SCAN_CHARACTERS": 8192,
			"_extendScanStart": lambda info, count: info.move("character", -count, endPoint="start"),
			"time": type("Time", (), {"monotonic": staticmethod(lambda: 100.0)}),
			"textInfos": type("TextInfos", (), {"POSITION_LAST": object(), "UNIT_CHARACTER": object()}),
			"_": lambda text: text,
			"log": type("Log", (), {"info": lambda *args, **kwargs: None, "debug": lambda *args, **kwargs: None})(),
			"_settings": lambda: {"speech": True, "braille": True}, "_send": lambda *args, **kwargs: None,
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		oldBuffer = Buffer("Do anything ChatGPT said: existing answer")
		refreshedBuffer = Buffer("Do anything User message 2 ChatGPT said: existing answer")
		subject = Subject(oldBuffer)
		self.assertFalse(namespace["_rememberBuffer"](
			subject, type("NativeDialog", (), {"nativeDialog": True})(),
		))
		self.assertIs(oldBuffer, subject._buffer)
		browserBuffer = Buffer("Browser content")
		namespace["_rememberBuffer"](subject, type(
			"Object", (), {"treeInterceptor": browserBuffer, "embeddedBrowser": True},
		)())
		self.assertIs(oldBuffer, subject._buffer)
		self.assertEqual([], subject.resets)
		namespace["_rememberBuffer"](subject, type("Object", (), {"treeInterceptor": refreshedBuffer})())
		self.assertIs(refreshedBuffer, subject._buffer)
		self.assertEqual([], subject.resets)
		self.assertEqual([], subject.spoken)
		self.assertEqual(2, subject._documentSwitchCount)
		blankBuffer = Buffer("Main landmark Do anything New chat")
		namespace["_rememberBuffer"](subject, type("Object", (), {"treeInterceptor": blankBuffer})())
		self.assertEqual(["document changed"], subject.resets)
		self.assertEqual(["New chat opened"], subject.spoken)
		self.assertEqual(3, subject._documentSwitchCount)
		subject._announceChatOpened("Project discussion", 1234)
		subject._announceChatOpened("Project discussion", 1234)
		subject._announceChatOpened("Other chat", 1234)
		self.assertEqual([
			"New chat opened", "Chat opened: Project discussion", "Chat opened: Other chat",
		], subject.spoken)
		longBuffer = Buffer("Main landmark Do anything " + ("response body " * 900))
		longSubject = Subject(refreshedBuffer)
		namespace["_rememberBuffer"](longSubject, type("Object", (), {"treeInterceptor": longBuffer})())
		self.assertEqual([], longSubject.resets)
		self.assertEqual([], longSubject.spoken)
		namespace["_rememberBuffer"](subject, type(
			"Object", (), {"treeInterceptor": blankBuffer, "mode": "codex"},
		)())
		self.assertEqual(["document changed", "conversation mode changed"], subject.resets)
		self.assertEqual("codex", subject._conversationMode)
		namespace["_setConversationMode"](subject, "codex", "mode switch control scan", True)
		namespace["_rememberBuffer"](subject, type(
			"Object", (), {"treeInterceptor": blankBuffer, "mode": "chatgpt", "name": "Do anything"},
		)())
		self.assertEqual("codex", subject._conversationMode)
		self.assertEqual(["document changed", "conversation mode changed"], subject.resets)
		ancestorBuffer = Buffer("Main landmark Ask anything New chat")
		conversationDocument = type(
			"Object", (), {"treeInterceptor": ancestorBuffer, "mode": "chatgpt"},
		)()
		topLevelFocus = type(
			"Object", (), {"treeInterceptor": None, "mode": "", "candidates": ()},
		)()
		topLevelFocus.candidates = (topLevelFocus, conversationDocument)
		freshSubject = Subject(None)
		namespace["_rememberBuffer"](freshSubject, topLevelFocus)
		self.assertIs(ancestorBuffer, freshSubject._buffer)
		self.assertEqual("chatgpt", freshSubject._conversationMode)
		# Current ChatGPT builds name the outer document after the task, so a response,
		# link, or sidebar control has no mode-bearing document ancestor. An explicit
		# History request may attach that outer buffer from bounded prompt evidence;
		# ordinary background events remain conservative.
		taskTitleBuffer = Buffer("Conversation content ChatGPT said: result Do anything")
		taskTitleObject = type("Object", (), {
			"treeInterceptor": taskTitleBuffer, "mode": "", "embeddedBrowser": False,
		})()
		unclassifiedSubject = Subject(None)
		self.assertFalse(namespace["_rememberBuffer"](unclassifiedSubject, taskTitleObject))
		self.assertIsNone(unclassifiedSubject._buffer)
		self.assertTrue(namespace["_rememberBuffer"](
			unclassifiedSubject, taskTitleObject, allowUnclassifiedConversation=True,
		))
		self.assertIs(taskTitleBuffer, unclassifiedSubject._buffer)
		pluginSource = PLUGIN_PATH.read_text(encoding="utf-8")
		self.assertIn(
			"self._rememberBuffer(focus, allowUnclassifiedConversation=True)", pluginSource,
		)
		# Reproduce Chromium's delayed mode-popup object after the real window has
		# closed. It must not restore a buffer, mode, or monitoring announcement.
		staleSubject = Subject(None)
		staleSubject._conversationMode = ""
		staleSubject._monitoringAnnounced = False
		staleSubject.windowAvailable = False
		staleObject = type("Object", (), {
			"treeInterceptor": blankBuffer,
			"mode": "codex",
			"name": "Switch mode, current mode: Codex",
		})()
		namespace["_rememberBuffer"](staleSubject, staleObject)
		self.assertIsNone(staleSubject._buffer)
		self.assertEqual("", staleSubject._conversationMode)
		self.assertFalse(staleSubject._monitoringAnnounced)
		self.assertEqual([], staleSubject.spoken)
		# After a confirmed close, a visible orphaned Chromium document may briefly
		# emit events while focus remains in another app. It cannot recreate monitoring.
		orphanSubject = Subject(None)
		orphanSubject._conversationClosedAt = 99.0
		orphanSubject.windowAvailable = True
		Api.focus = type("Focus", (), {"inChatGPT": False})()
		self.assertFalse(namespace["_rememberBuffer"](orphanSubject, staleObject))
		self.assertIsNone(orphanSubject._buffer)
		Api.focus = type("Focus", (), {"inChatGPT": True})()
		self.assertTrue(namespace["_rememberBuffer"](orphanSubject, staleObject))
		self.assertIs(blankBuffer, orphanSubject._buffer)
		self.assertEqual(0.0, orphanSubject._conversationClosedAt)

	def test_chat_history_caches_are_isolated_by_conversation_mode(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in {
				"_chatHistoryTitles", "_cacheChatHistoryScan", "_loadArchivedChatHistory",
			}
		]
		namespace = {
			"_pressControl": lambda obj: obj.doAction(),
			"Path": type("UnexpectedPath", (), {
				"home": staticmethod(lambda: (_ for _ in ()).throw(AssertionError("ChatGPT read Codex files"))),
			}),
			"os": type("Os", (), {"environ": {}}),
			"uniqueThreadLabels": uniqueThreadLabels,
			"loadArchivedThreads": loadArchivedThreads,
			"log": type("Log", (), {
				"info": lambda *args, **kwargs: None,
				"debugWarning": lambda *args, **kwargs: None,
			})(),
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			_conversationMode = "chatgpt"
			_conversationWindowHandle = 1234
			_chatHistoryCacheCurrent = {"chatgpt": True, "codex": True}
			_chatHistoryCaches = {
				"chatgpt": ("ChatGPT recent",),
				"codex": ("Codex recent",),
			}
			_archivedChatHistoryCaches = {
				"chatgpt": ("ChatGPT archived",),
				"codex": ("Codex archived",),
			}
			_archivedChatHistoryLoaded = {"chatgpt": True, "codex": True}
			_archivedChatIds = {"chatgpt": {}, "codex": {"Codex archived": "thread-id"}}
			def _schedulePendingChatHistoryOpen(self, delay): return False
		subject = Subject()
		subject._chatHistoryTitles = lambda mode=None: namespace["_chatHistoryTitles"](subject, mode)
		subject._cacheChatHistoryScan = lambda mode, recentTitles=None, archivedTitles=None: namespace[
			"_cacheChatHistoryScan"
		](subject, mode, recentTitles, archivedTitles)
		self.assertEqual(("ChatGPT recent",), subject._chatHistoryTitles("chatgpt"))
		self.assertEqual(("Codex recent",), subject._chatHistoryTitles("codex"))
		self.assertEqual(
			(("ChatGPT archived",), True),
			namespace["_loadArchivedChatHistory"](subject, "chatgpt"),
		)
		subject._cacheChatHistoryScan("chatgpt", ("New ChatGPT recent",), ())
		self.assertEqual(("New ChatGPT recent",), subject._chatHistoryTitles("chatgpt"))
		self.assertEqual((), subject._archivedChatHistoryCaches["chatgpt"])
		self.assertEqual(("Codex recent",), subject._chatHistoryTitles("codex"))
		self.assertEqual(("Codex archived",), subject._archivedChatHistoryCaches["codex"])
		dialogSource = CHAT_DIALOG_PATH.read_text(encoding="utf-8")
		self.assertIn('title=_("{agent} chat history").format(agent=agentName)', dialogSource)
		self.assertIn('selection[1], self._mode)', dialogSource)
		self.assertNotIn('title=_("Codex chat history")', dialogSource)
		pluginSource = PLUGIN_PATH.read_text(encoding="utf-8")
		self.assertIn('if source == "archived" and mode == "codex":', pluginSource)
		self.assertIn('if mode != self._conversationMode:', pluginSource)
		self.assertIn("CHAT_HISTORY_MODE_SETTLE_SECONDS = 0.75", pluginSource)
		self.assertIn("if not self._chatHistoryCacheCurrent.get(mode, False):", pluginSource)
		self.assertIn("CHAT_HISTORY_EXPANSION_MAX_PAGES = 20", pluginSource)
		self.assertIn("button = self._recentHistoryShowMoreButton(mode)", pluginSource)
		self.assertIn("_pressControl(button)", pluginSource)
		self.assertIn("self._showChatHistoryDialog(mode)", pluginSource)

	def test_chat_history_scan_stops_before_transcript_controls(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_latestButtonStatus"
		)
		class Role:
			BUTTON = "button"
			LANDMARK = "landmark"
		class Command:
			def __init__(self, command, role=None, name="", landmark=""):
				self.command = command
				self.field = {"role": role, "name": name, "landmark": landmark}
		class Info:
			def getTextWithFields(self):
				return (
					Command("controlStart", Role.BUTTON, "Switch mode, current mode: Codex"),
					"Codex",
					Command("controlEnd"),
					Command("controlStart", Role.BUTTON, "Show more"),
					"Show more",
					Command("controlEnd"),
					"Recents",
					Command("controlStart", Role.BUTTON, "Real chat title"),
					"Real chat title",
					Command("controlEnd"),
					# A chat title that reads like Codex progress ("Using ...").
					Command("controlStart", Role.BUTTON, "Using VoiceOver Rotor"),
					"Using VoiceOver Rotor",
					Command("controlEnd"),
					Command("controlStart", Role.BUTTON, "Real chat title"),
					"Real chat title",
					Command("controlEnd"),
					Command("controlStart", Role.BUTTON, "Show more"),
					"Show more",
					Command("controlEnd"),
					"6% usage remaining",
					Command("controlStart", Role.BUTTON, "Account action from usage pop-over"),
					"Account action from usage pop-over",
					Command("controlEnd"),
					Command("controlStart", Role.BUTTON, "Add credits"),
					"Add credits",
					Command("controlEnd"),
					Command("controlStart", Role.BUTTON, "Update"),
					"Update",
					Command("controlEnd"),
					None,  # Boundary between bounded sidebar and transcript ranges.
					Command("controlStart", Role.BUTTON, "Jump to user message 1"),
					Command("controlEnd"),
					"Recents",
					Command("controlStart", Role.BUTTON, "Sources"),
					"SourcesWikipediaExample source",
					Command("controlEnd"),
					Command("controlStart", Role.BUTTON, "Copy response"),
					Command("controlEnd"),
					"Response complete",
				)
		cached = []
		scheduled = []
		class Time:
			now = 100.0
			@classmethod
			def monotonic(cls): return cls.now
		namespace = {
			"ATTACHMENT_POPUP_ROW_CLASS": core.ATTACHMENT_POPUP_ROW_CLASS, "ATTACHMENT_POPUP_CLASS_KEY": core.ATTACHMENT_POPUP_CLASS_KEY, "_domClassNames": lambda obj: str(getattr(obj, "domClass", "") or ""),
			"Role": Role,
			"ChatMessageAccumulator": ChatMessageAccumulator,
			"MESSAGE_LIST_LIMIT": 100,
			"State": type("State", (), {"EXPANDED": "expanded", "COLLAPSED": "collapsed"}),
			"conversationModeFromSwitchLabel": conversationModeFromSwitchLabel,
			"conversationModeFromSwitchControl": conversationModeFromSwitchControl,
			"chatHistorySnapshotDecision": chatHistorySnapshotDecision,
			"CHAT_HISTORY_MODE_SETTLE_SECONDS": 0.75,
			"CHAT_HISTORY_SNAPSHOT_CONFIRM_SECONDS": 0.25,
			"CHAT_HISTORY_RETRY_MILLISECONDS": 300,
			"time": Time,
			"re": re,
			"log": type("Log", (), {"debug": lambda *args, **kwargs: None})(),
			"isChatHistoryConversationBoundary": isChatHistoryConversationBoundary,
			"isChatHistoryInterfaceText": isChatHistoryInterfaceText,
			"isStopControlLabel": isStopControlLabel,
			"userMessageNumber": userMessageNumber,
			"firstStatusLabel": firstStatusLabel,
			"isKnownNonStatusButton": isKnownNonStatusButton,
			"usageLimitNotice": usageLimitNotice,
			"shouldLogDiagnosticSnapshot": shouldLogDiagnosticSnapshot,
			"_": lambda text: text,
			"_settings": lambda: {"diagnosticLogging": False},
			"userMessageSubmissionTransition": userMessageSubmissionTransition,
			"confirmedUserMessageSubmission": confirmedUserMessageSubmission,
			"stopControlTransition": stopControlTransition,
			"isResponseCompletionMarkerText": isResponseCompletionMarkerText,
			"responseCompletionScanMarker": responseCompletionScanMarker,
			"responseCompletionTransition": responseCompletionTransition,
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			_conversationMode = "chatgpt"
			_conversationModeObserved = False
			_conversationModeChangedAt = 0.0
			_chatHistoryCaches = {"chatgpt": (), "codex": ()}
			_chatHistoryCacheCurrent = {"chatgpt": False, "codex": False}
			_ambiguousRecentChatTitles = {"chatgpt": set(), "codex": set()}
			_pendingChatHistorySnapshots = {"chatgpt": None, "codex": None}
			_pendingChatHistorySnapshotAt = {"chatgpt": 0.0, "codex": 0.0}
			_chatHistoryMoreAvailable = {"chatgpt": False, "codex": False}
			_recentHistoryShowMoreOrdinals = {"chatgpt": 0, "codex": 0}
			_unifiedRecentCounts = {"chatgpt": 0, "codex": 0}
			_chatHistoryScanGenerations = {"chatgpt": 0, "codex": 0}
			_lastUnknownButtons = ()
			_lastUnknownButtonsAt = 0.0
			_lastDeferredHistoryLog = ()
			_lastDeferredHistoryLogAt = 0.0
			_latestUserMessageNumber = None
			_pendingUserMessageIncrease = False
			_promptHadText = False
			_busy = False
			_stopControlVisible = False
			_latestResponseMarker = None
			_responseMarkerInitialized = False
			def _setConversationMode(self, mode, reason, authoritative=False):
				if mode != self._conversationMode:
					self._conversationModeChangedAt = Time.monotonic()
					self._chatHistoryCacheCurrent[mode] = False
					self._pendingChatHistorySnapshots[mode] = None
					self._pendingChatHistorySnapshotAt[mode] = 0.0
				self._conversationMode = mode
				self._conversationModeObserved = self._conversationModeObserved or authoritative
				return True
			def _newChatMessageFieldCollector(self, stopAtPrompt=True):
				return ChatMessageFieldCollector((), None, lambda label: False, (), stopAtPrompt)
			def _schedulePoll(self, delay=150, requestInspection=True):
				scheduled.append((delay, requestInspection))
			def _cacheChatHistoryScan(self, mode, recentTitles=None, archivedTitles=None):
				cached.append((mode, recentTitles, archivedTitles))
			def _modeSpecificRecentChatTitles(self, mode, titles):
				return modeSpecificRecentChatTitles(mode, titles, ("Real chat title",))
			def _beginPromptSubmission(self, reason):
				raise AssertionError(reason)
			def _setBusy(self, busy, reason):
				raise AssertionError(reason)
			def _queueResponseCompletion(self):
				raise AssertionError("unexpected completion")
			def _applyUsageLimitNotice(self, notice):
				self.limitNotices.append(notice)
				self._busy = False
				return True
		subject = Subject()
		subject.limitNotices = []
		self.assertEqual("", namespace["_latestButtonStatus"](subject, Info()))
		self.assertTrue(firstStatusLabel("Using VoiceOver Rotor"))
		self.assertEqual((1, None), subject._latestResponseMarker)
		self.assertTrue(subject._responseMarkerInitialized)
		self.assertEqual([], cached)
		self.assertEqual(1, len(scheduled))
		self.assertTrue(scheduled[0][1])
		Time.now = 101.0
		namespace["_latestButtonStatus"](subject, Info())
		self.assertEqual([], cached)
		self.assertEqual(2, len(scheduled))
		Time.now = 101.3
		namespace["_latestButtonStatus"](subject, Info())
		self.assertEqual([("codex", ("Real chat title",), None)], cached)
		self.assertTrue(subject._conversationModeObserved)
		self.assertTrue(subject._chatHistoryMoreAvailable["codex"])
		self.assertEqual(2, subject._recentHistoryShowMoreOrdinals["codex"])
		self.assertEqual(3, subject._unifiedRecentCounts["codex"])
		self.assertEqual({"real chat title"}, subject._ambiguousRecentChatTitles["codex"])
		# A new chat is read in one piece, with no boundary after the sidebar, so a
		# chat title that reads like progress must not become the activity label.
		class NewChatInfo(Info):
			def getTextWithFields(self):
				return (
					"Recents",
					Command("controlStart", Role.BUTTON, "Using VoiceOver Rotor"),
					"Using VoiceOver Rotor",
					Command("controlEnd"),
				)
		self.assertEqual("", namespace["_latestButtonStatus"](subject, NewChatInfo()))
		# A conversation row of the "@" or Add files and more menu stays on the page
		# after the menu closes, outside the sidebar; it is never activity either.
		class MenuRow:
			command = "controlStart"
			field = {
				"role": Role.BUTTON, "name": "Using VoiceOver Rotor ChatGPT conversation",
				core.ATTACHMENT_POPUP_CLASS_KEY: "text-default min-h-[var(--app-menu-item-height,0px)] flex",
			}
		class MenuRowInfo(Info):
			def getTextWithFields(self):
				return (MenuRow(), "Using VoiceOver Rotor", "ChatGPT conversation", Command("controlEnd"))
		self.assertEqual("", namespace["_latestButtonStatus"](subject, MenuRowInfo()))
		class LimitInfo(Info):
			def getTextWithFields(self):
				return tuple(
					(
						"0% usage remainingDismiss usage alert Resets every week · "
						"Next reset is on Sep 10 at 5:25 PM Usage consumed"
					) if item == "6% usage remaining" else item
					for item in super().getTextWithFields()
				)
		subject._busy = True
		self.assertEqual("", namespace["_latestButtonStatus"](subject, LimitInfo()))
		self.assertFalse(subject._busy)
		self.assertEqual(
			[
				"Usage limit reached. You can purchase more credits in ChatGPT usage settings "
				"or try again on Sep 10 at 5:25 PM."
			],
			subject.limitNotices,
		)

	def test_exact_named_button_resolver_honors_the_scanned_ordinal(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_exactNamedButtonObject"
		)
		class Role:
			BUTTON = "button"
		class Button:
			role = Role.BUTTON
			windowHandle = 99
			IA2UniqueID = 0
			def __init__(self, name): self.name = name
		class Child:
			role = "text"
			def __init__(self, parent): self.parent = parent
		first = Button("Show more")
		notExact = Button("Show more results")
		second = Button("Show more")
		class Info:
			def __init__(self):
				self.matches = (Child(first), Child(notExact), Child(second))
				self.index = -1
				self.NVDAObjectAtStart = None
			def find(self, text, reverse=False, caseSensitive=False):
				self.index += 1
				if self.index >= len(self.matches):
					return False
				self.NVDAObjectAtStart = self.matches[self.index]
				return True
			def collapse(self, end=False): pass
			def move(self, unit, count): return 1 if self.index < len(self.matches) - 1 else 0
		class Buffer:
			def makeTextInfo(self, position): return Info()
		namespace = {
			"_isVirtualBufferDocument": lambda buffer: True,
			"Role": Role,
			"textInfos": type("TextInfos", (), {"POSITION_FIRST": object(), "UNIT_CHARACTER": object()}),
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		subject = type("Subject", (), {"_buffer": Buffer()})()
		self.assertIs(second, namespace["_exactNamedButtonObject"](subject, "Show more", 2))
		self.assertIsNone(namespace["_exactNamedButtonObject"](subject, "Show more", 3))

	def test_recent_history_expansion_waits_for_growth_and_is_bounded(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_continueChatHistoryExpansion"
		)
		messages = []
		class Api:
			focus = "chatgpt"
			@classmethod
			def getFocusObject(cls): return cls.focus
		class Button:
			def __init__(self): self.actions = 0
			def doAction(self): self.actions += 1
		class Subject:
			def __init__(self, pages=0, more=True, cacheCurrent=True, button=True):
				self._chatHistoryExpansionTimer = object()
				self._pendingChatHistoryExpansion = {
					"mode": "chatgpt", "pages": pages, "lastCount": 10,
					"lastGeneration": 1, "awaitingGrowth": False,
					"staleScans": 0, "settleScans": 0,
				}
				self._conversationMode = "chatgpt"
				self._buffer = object()
				self._unifiedRecentCounts = {"chatgpt": 10, "codex": 0}
				self._chatHistoryScanGenerations = {"chatgpt": 1, "codex": 0}
				self._chatHistoryMoreAvailable = {"chatgpt": more, "codex": False}
				self._recentHistoryShowMoreOrdinals = {"chatgpt": 1, "codex": 0}
				self._chatHistoryCacheCurrent = {"chatgpt": cacheCurrent, "codex": False}
				self._pendingChatHistorySnapshots = {"chatgpt": ("old",), "codex": None}
				self._pendingChatHistorySnapshotAt = {"chatgpt": 1.0, "codex": 0.0}
				self._bufferDirty = False
				self.button = Button() if button else None
				self.expansionSchedules = []
				self.pollSchedules = []
				self.finished = []
				self.cancelled = 0
			def _cancelChatHistoryExpansion(self):
				self.cancelled += 1
				self._pendingChatHistoryExpansion = None
			def _finishChatHistoryExpansion(self, mode, limitReached=False, failed=False):
				self.finished.append((mode, limitReached, failed))
			def _scheduleChatHistoryExpansion(self, delay): self.expansionSchedules.append(delay)
			def _schedulePoll(self, delay=150, requestInspection=True):
				self.pollSchedules.append((delay, requestInspection))
			def _recentHistoryShowMoreButton(self, mode): return self.button
		namespace = {
			"_pressControl": lambda obj: obj.doAction(),
			"api": Api,
			"_isChatGPTObject": lambda obj: obj == "chatgpt",
			"_": lambda text: text,
			"ui": type("Ui", (), {"message": staticmethod(messages.append)}),
			"log": type("Log", (), {
				"info": staticmethod(lambda *args, **kwargs: None),
				"debugWarning": staticmethod(lambda *args, **kwargs: None),
			}),
			"CHAT_HISTORY_EXPANSION_MAX_PAGES": 20,
			"CHAT_HISTORY_EXPANSION_MAX_STALE_SCANS": 30,
			"CHAT_HISTORY_EXPANSION_RETRY_MILLISECONDS": 300,
			"CHAT_HISTORY_EXPANSION_DELAY_MILLISECONDS": 700,
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		continueExpansion = namespace["_continueChatHistoryExpansion"]

		subject = Subject()
		continueExpansion(subject)
		self.assertEqual(1, subject.button.actions)
		self.assertEqual(1, subject._pendingChatHistoryExpansion["pages"])
		self.assertTrue(subject._pendingChatHistoryExpansion["awaitingGrowth"])
		self.assertFalse(subject._chatHistoryCacheCurrent["chatgpt"])
		self.assertEqual([(150, True)], subject.pollSchedules)
		self.assertEqual([700], subject.expansionSchedules)

		continueExpansion(subject)
		self.assertEqual(1, subject.button.actions)
		self.assertEqual(1, subject._pendingChatHistoryExpansion["staleScans"])
		self.assertEqual(300, subject.expansionSchedules[-1])

		subject._unifiedRecentCounts["chatgpt"] = 20
		subject._chatHistoryScanGenerations["chatgpt"] = 2
		subject._chatHistoryMoreAvailable["chatgpt"] = False
		continueExpansion(subject)
		self.assertEqual([], subject.finished)
		self.assertEqual(1, subject._pendingChatHistoryExpansion["settleScans"])
		subject._chatHistoryCacheCurrent["chatgpt"] = True
		continueExpansion(subject)
		self.assertEqual([("chatgpt", False, False)], subject.finished)

		limited = Subject(pages=20, more=True, cacheCurrent=True)
		continueExpansion(limited)
		self.assertEqual([("chatgpt", True, False)], limited.finished)
		self.assertEqual(0, limited.button.actions)

		missing = Subject(button=False)
		continueExpansion(missing)
		self.assertEqual([("chatgpt", False, True)], missing.finished)

		stalled = Subject()
		continueExpansion(stalled)
		for generation in range(2, 33):
			stalled._chatHistoryScanGenerations["chatgpt"] = generation
			continueExpansion(stalled)
		self.assertEqual([("chatgpt", False, True)], stalled.finished)
		self.assertEqual(1, stalled.button.actions)

		focusLost = Subject()
		Api.focus = "other"
		continueExpansion(focusLost)
		self.assertEqual(1, focusLost.cancelled)
		self.assertIn("Recent chat history loading stopped because ChatGPT is no longer focused", messages)
		Api.focus = "chatgpt"

	def test_chatgpt_archived_action_never_uses_a_codex_thread_id(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_performChatHistoryAction"
		)
		messages = []
		namespace = {
			"_pressControl": lambda obj: obj.doAction(),
			"_": lambda text: text,
			"codexThreadUrl": lambda threadId: (_ for _ in ()).throw(
				AssertionError("ChatGPT archived history used a Codex thread ID")
			),
			"time": type("Time", (), {"monotonic": staticmethod(lambda: 10.0)}),
			"wx": type("Wx", (), {"LaunchDefaultBrowser": staticmethod(lambda url: True)}),
			"ui": type("Ui", (), {"message": staticmethod(messages.append)}),
			"log": type("Log", (), {
				"info": lambda *args, **kwargs: None,
				"debugWarning": lambda *args, **kwargs: None,
			})(),
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Button:
			def __init__(self): self.actions = 0
			def doAction(self): self.actions += 1
		button = Button()
		class Subject:
			_conversationMode = "chatgpt"
			_conversationWindowHandle = 1234
			_archivedChatIds = {"chatgpt": {}, "codex": {}}
			_pendingOpenedChatTitle = ""
			_pendingOpenedChatAt = 0.0
			def _conversationWindowIsAvailable(self, handle): return True
			def _chatButtonObject(self, title): return button
			def _startDirectChatAction(self, title, action): raise AssertionError(action)
			def _scheduleUnarchiveButtonFocus(self): raise AssertionError("Codex-only action")
		subject = Subject()
		namespace["_performChatHistoryAction"](
			subject, "ChatGPT archived", "open", "archived", "chatgpt",
		)
		self.assertEqual(1, button.actions)
		self.assertEqual("ChatGPT archived", subject._pendingOpenedChatTitle)
		namespace["_performChatHistoryAction"](
			subject, "Codex archived", "open", "archived", "codex",
		)
		self.assertEqual(1, button.actions)
		self.assertEqual(["The chat-history mode changed. Open chat history again"], messages)

	def test_duplicate_recent_title_blocks_open_pin_and_archive_but_not_unique_titles(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_performChatHistoryAction"
		)
		messages, actions = [], []
		namespace = {
			"_pressControl": lambda obj: obj.doAction(),
			"_": lambda text: text,
			"time": type("Time", (), {"monotonic": staticmethod(lambda: 10.0)}),
			"ui": type("Ui", (), {"message": staticmethod(messages.append)}),
			"log": type("Log", (), {
				"info": lambda *args, **kwargs: None,
				"debug": lambda *args, **kwargs: None,
				"debugWarning": lambda *args, **kwargs: None,
			})(),
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Button:
			def doAction(self): actions.append("open")
		class Subject:
			_conversationMode = "chatgpt"
			_conversationWindowHandle = 1234
			_ambiguousRecentChatTitles = {"chatgpt": {"shared title"}, "codex": set()}
			_pendingOpenedChatTitle = ""
			_pendingOpenedChatAt = 0.0
			def _conversationWindowIsAvailable(self, handle): return True
			def _chatButtonObject(self, title): return Button()
			def _startDirectChatAction(self, title, action): actions.append(action)
		subject = Subject()
		for action in ("open", "pin", "archive"):
			namespace["_performChatHistoryAction"](
				subject, "  SHARED   TITLE ", action, "recent", "chatgpt",
			)
		self.assertEqual([], actions)
		self.assertEqual(3, len(messages))
		self.assertTrue(all("native Recents list" in message for message in messages))
		namespace["_performChatHistoryAction"](
			subject, "Unique title", "open", "recent", "chatgpt",
		)
		namespace["_performChatHistoryAction"](
			subject, "Unique title", "pin", "recent", "chatgpt",
		)
		self.assertEqual(["open", "pin"], actions)

	def test_plugin_progress_only_releases_busy_state_it_started(self):
		self.assertEqual((True, True), pluginProgressBusyTransition(False, False, False))
		self.assertEqual((False, False), pluginProgressBusyTransition(True, True, True))
		self.assertEqual((True, False), pluginProgressBusyTransition(True, False, True))

	def test_stale_pending_chat_titles_are_discarded(self):
		self.assertEqual("My chat", pendingChatTitle(" My  chat ", 2.0))
		self.assertEqual("", pendingChatTitle("My chat", 11.0))
		self.assertEqual("", pendingChatTitle("", 1.0))

	def test_archived_threads_load_from_jsonl_metadata_newest_first(self):
		with tempfile.TemporaryDirectory() as directory:
			codexRoot = Path(directory)
			archiveDirectory = codexRoot / "archived_sessions"
			archiveDirectory.mkdir()
			olderId = "00000000-0000-0000-0000-000000000001"
			newerId = "00000000-0000-0000-0000-000000000002"
			index = codexRoot / "session_index.jsonl"
			index.write_text(
				json.dumps(["valid JSON, wrong shape"]) + "\n" +
				json.dumps({"id": olderId, "thread_name": " Older   archived "}) + "\n" +
				json.dumps({"id": newerId, "thread_name": "Named archived"}) + "\n",
				encoding="utf-8",
			)
			olderPath = archiveDirectory / f"rollout-old-{olderId}.jsonl"
			newerPath = archiveDirectory / f"rollout-new-{newerId}.jsonl"
			invalidPath = archiveDirectory / "not-a-thread.jsonl"
			olderPath.write_text("{}\n", encoding="utf-8")
			newerPath.write_text("{}\n", encoding="utf-8")
			invalidPath.write_text("{}\n", encoding="utf-8")
			os.utime(olderPath, (10, 10))
			os.utime(newerPath, (20, 20))
			os.utime(invalidPath, (30, 30))
			self.assertEqual(
				((newerId, "Named archived"), (olderId, "Older archived")),
				loadArchivedThreads(codexRoot),
			)

	def test_active_codex_titles_deduplicate_index_and_exclude_archived_tasks(self):
		with tempfile.TemporaryDirectory() as directory:
			codexRoot = Path(directory)
			archiveDirectory = codexRoot / "archived_sessions"
			archiveDirectory.mkdir()
			activeId = "00000000-0000-0000-0000-000000000001"
			archivedId = "00000000-0000-0000-0000-000000000002"
			otherId = "00000000-0000-0000-0000-000000000003"
			(archiveDirectory / f"rollout-archived-{archivedId}.jsonl").write_text(
				"{}\n", encoding="utf-8",
			)
			(codexRoot / "session_index.jsonl").write_text(
				json.dumps({"id": activeId, "thread_name": "Old name", "updated_at": "2026-01-01"}) + "\n" +
				json.dumps({"id": archivedId, "thread_name": "Archived", "updated_at": "2026-03-01"}) + "\n" +
				json.dumps({"id": activeId, "thread_name": "Current name", "updated_at": "2026-04-01"}) + "\n" +
				json.dumps({"id": otherId, "thread_name": "Other active", "updated_at": "2026-02-01"}) + "\n",
				encoding="utf-8",
			)
			self.assertEqual(
				("Current name", "Other active"),
				loadActiveCodexThreadTitles(codexRoot),
			)

	def test_native_codex_thread_url_requires_a_uuid(self):
		self.assertEqual(
			"codex://threads/00000000-0000-0000-0000-000000000002",
			codexThreadUrl("00000000-0000-0000-0000-000000000002"),
		)
		self.assertEqual("", codexThreadUrl("../settings"))
		self.assertEqual("", codexThreadUrl(""))

	def test_duplicate_archived_titles_keep_every_native_thread_id(self):
		self.assertEqual(
			(
				("00000000-0000-0000-0000-000000000001", "Repeated title"),
				("00000000-0000-0000-0000-000000000002", "Repeated title (2)"),
				("00000000-0000-0000-0000-000000000003", "Repeated title (3)"),
			),
			uniqueThreadLabels((
				("00000000-0000-0000-0000-000000000001", "Repeated title"),
				("00000000-0000-0000-0000-000000000002", "Repeated title"),
				("00000000-0000-0000-0000-000000000003", "Repeated title"),
			)),
		)
		labels = [label for threadId, label in uniqueThreadLabels((
			("1", "Repeated title"), ("2", "Repeated title"), ("3", "Repeated title (2)"),
		))]
		self.assertEqual(len(labels), len(set(labels)))

	def test_every_click_tier_has_the_complete_valid_sound_inventory(self):
		sounds = CORE_PATH.parent / "sounds"
		expected = set(core.TONE_PATTERNS)
		for level in ("soft", "normal", "loud"):
			paths = sorted((sounds / level).glob("*.wav"))
			self.assertEqual(expected, {path.stem for path in paths}, level)
			for path in paths:
				with wave.open(str(path), "rb") as audio:
					self.assertEqual(1, audio.getnchannels(), path)
					self.assertEqual(2, audio.getsampwidth(), path)
					self.assertEqual(44100, audio.getframerate(), path)
					self.assertGreater(audio.getnframes(), 0, path)

	def test_click_designs_use_distinct_patterns_and_percussive_characters(self):
		tree = ast.parse(CLICK_GENERATOR_PATH.read_text(encoding="utf-8"))
		patterns = ast.literal_eval(next(
			node.value for node in tree.body
			if isinstance(node, ast.Assign) and any(
				isinstance(target, ast.Name) and target.id == "PATTERNS" for target in node.targets
			)
		))
		self.assertEqual(17, len(patterns))
		self.assertEqual(17, len({tuple(pattern) for pattern in patterns.values()}))
		characters = {character for pattern in patterns.values() for offset, frequency, character in pattern}
		self.assertGreaterEqual(len(characters), 6)
		self.assertNotEqual(patterns["command"], patterns["file"])
		self.assertNotEqual(patterns["completion"], patterns["failure"])

	def test_click_volume_levels_are_clearly_separated(self):
		sounds = CORE_PATH.parent / "sounds"
		for soundPath in sorted((sounds / "normal").glob("*.wav")):
			levels = []
			for level in ("soft", "normal", "loud"):
				with wave.open(str(sounds / level / soundPath.name), "rb") as audio:
					raw = audio.readframes(audio.getnframes())
				samples = struct.unpack("<" + "h" * (len(raw) // 2), raw)
				levels.append(math.sqrt(sum(sample * sample for sample in samples) / len(samples)))
			with self.subTest(sound=soundPath.name):
				self.assertLess(levels[0], levels[1] * 0.45)
				self.assertLess(levels[1], levels[2] * 0.65)

	def test_preview_selection_returns_only_requested_item(self):
		items = (("thinking", "Thinking"), ("command", "Running command"))
		self.assertEqual(items[1], previewSelection(items, 1))
		self.assertEqual(items[0], previewSelection(items, -1))
		self.assertEqual(items[0], previewSelection(items, 99))
		self.assertIsNone(previewSelection((), 0))

	def test_custom_announcement_placeholders_and_safe_fallbacks(self):
		self.assertEqual(
			"Still running Build after 12 seconds: Running tests",
			formatCustomAnnouncement(
				"Still running {activity} after {seconds} seconds: {message}",
				"Running tests", "Build", 12,
			),
		)
		self.assertEqual("Running tests", formatCustomAnnouncement("", "Running tests"))
		self.assertEqual("Keep {unknown}", formatCustomAnnouncement("Keep {unknown}", "Running tests"))
		self.assertEqual("Keep {message.missing}", formatCustomAnnouncement("Keep {message.missing}", "Running tests"))
		self.assertEqual(
			"File operations still running for 1 minute 25 seconds",
			formatCustomAnnouncement("{activity} still running for {duration}", "Working", "File operations", 85),
		)

	def test_bounded_announcement_history_and_navigation(self):
		history = AnnouncementHistory(3)
		self.assertFalse(history.add(""))
		self.assertTrue(history.add("one"))
		self.assertFalse(history.add("one"))
		history.add("two")
		history.add("three")
		history.add("four")
		self.assertEqual(("two", "three", "four"), history.items())
		self.assertEqual("three", history.move(-1))
		self.assertEqual("two", history.move(-20))
		self.assertEqual("four", history.move(20))
		history.clear()
		self.assertEqual(0, len(history))
		self.assertEqual("", history.move(-1))

	def test_chat_message_shortcuts_and_accessibility_token_extraction(self):
		self.assertEqual(tuple(range(1, 11)), tuple(
			chatMessageShortcutIndex(key) for key in "1234567890"
		))
		self.assertIsNone(chatMessageShortcutIndex("numpad1"))
		self.assertIsNone(chatMessageShortcutIndex(""))
		tokens = [
			("text", "sidebar title"),
			("speaker", "user"), ("speaker", "user"), ("text", " First question "),
			("text", "with a second line"),
			("speaker", "assistant"), ("text", "Response complete"), ("text", "First answer"),
			("speaker", "assistant"), ("text", "First answer"),
			("speaker", "user"), ("text", "Second question"), ("end", "prompt"),
			("text", "Do anything"),
		]
		self.assertEqual(
			(("user", "First question with a second line"), ("assistant", "First answer"), ("user", "Second question")),
			chatMessagesFromTokens(tokens),
		)

	def test_anonymized_chatgpt_accessibility_snapshots(self):
		fixtures = json.loads(ACCESSIBILITY_FIXTURE_PATH.read_text(encoding="utf-8"))
		for item in fixtures["modeControls"]:
			with self.subTest(view=item["view"]):
				if item["view"] in ("Chat", "Work", "Codex"):
					self.assertEqual(
						"codex" if item["view"] == "Codex" else "chatgpt",
						conversationModeFromDocumentNames((item["document"],)),
					)
				self.assertEqual(item["expected"], conversationModeFromSwitchControl(
					item["name"], item["description"], item["role"],
					item["expandable"], item["automationId"],
				))
		for snapshot in fixtures["conversationSnapshots"]:
			with self.subTest(snapshot=snapshot["name"]):
				self.assertEqual(
					tuple(tuple(item) for item in snapshot["expected"]),
					chatMessagesFromTokens(tuple(tuple(item) for item in snapshot["tokens"])),
				)
		for item in fixtures["promptLabels"]:
			with self.subTest(prompt=item["label"]):
				self.assertEqual(item["expected"], isCodexPromptLabel(item["label"]))
		for item in fixtures["stopControls"]:
			with self.subTest(stop=item["label"]):
				self.assertEqual(item["expected"], isStopControlLabel(item["label"]))
		for item in fixtures["chatActions"]:
			with self.subTest(action=item["label"]):
				self.assertEqual(item["expected"], chatActionMatches(item["action"], item["label"]))
		for item in fixtures["historyInterfaceText"]:
			with self.subTest(historyControl=item["label"]):
				self.assertEqual(item["expected"], isChatHistoryInterfaceText(item["label"]))
		for item in fixtures["permissionText"]:
			with self.subTest(permission=item["label"]):
				self.assertEqual(item["expected"], isPermissionPromptText(item["label"]))
		for item in fixtures["pluginProgress"]:
			expected = tuple(item["expected"]) if item["expected"] is not None else None
			with self.subTest(progress=item["label"]):
				self.assertEqual(expected, pluginInstallProgress(item["label"]))
		for item in fixtures["browserStructures"]:
			with self.subTest(browser=item["name"]):
				self.assertEqual(
					item["expected"], browserAccess.isEmbeddedBrowserDocumentStructure(*item["roles"]),
				)

	def test_chat_message_extraction_is_bounded_and_tolerates_bad_tokens(self):
		tokens = []
		for index in range(12):
			tokens.extend((
				("speaker", "user" if index % 2 == 0 else "assistant"),
				("text", f"message {index}"),
			))
		tokens.extend((None, ("bad",), ("speaker", "unknown")))
		messages = chatMessagesFromTokens(tokens, 10)
		self.assertEqual(10, len(messages))
		self.assertEqual(("user", "message 2"), messages[0])
		self.assertEqual(("assistant", "message 11"), messages[-1])

	def test_chat_message_fields_keep_only_visible_active_branch_before_prompt(self):
		class Command:
			def __init__(self, command, role=None, name="", states=(), **field):
				self.command = command
				self.field = {"role": role, "name": name, "states": states, **field}

		collector = ChatMessageFieldCollector(
			{"button", "edit"}, "edit", isCodexPromptLabel, {"invisible"}, True,
		)
		accumulator = ChatMessageAccumulator(10)
		fields = (
			"You said:", "current question",
			Command("controlStart", "group", states={"invisible"}),
			"You said:", "stale hidden question", "ChatGPT said:", "stale hidden answer",
			Command("controlEnd"),
			"ChatGPT said:", "current answer",
			Command("controlStart", "button", "Copy response"), "Copy", Command("controlEnd"),
			Command("controlStart", "edit", "Message ChatGPT"),
			# Chromium can retain an inactive fork after the active composer. Nothing
			# below the prompt may replace the current visible branch.
			"You said:", "stale post-prompt question", "ChatGPT said:", "stale post-prompt answer",
		)
		for item in fields:
			for token in collector.feed(item):
				accumulator.feed(token)

		self.assertTrue(collector.promptReached)
		self.assertTrue(collector.done)
		self.assertEqual(
			(("user", "current question"), ("assistant", "current answer")),
			accumulator.messages(),
		)

	def test_recent_message_commands_expand_only_a_bounded_conversation_tail(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methodNames = {
			"_newChatMessageFieldCollector", "_cacheRecentChatMessages",
			"_chatMessagesFromInfo", "_currentChatMessages", "_activeBranchMessages",
		}
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in methodNames
		]
		method = next(node for node in methods if node.name == "_currentChatMessages")
		methodSource = ast.get_source_segment(PLUGIN_PATH.read_text(encoding="utf-8"), method)
		scanMethod = next(node for node in methods if node.name == "_activeBranchMessages")
		scanSource = ast.get_source_segment(PLUGIN_PATH.read_text(encoding="utf-8"), scanMethod)
		self.assertNotIn("makeTextInfo(textInfos.POSITION_ALL)", methodSource + scanSource)
		self.assertIn("POSITION_LAST", scanSource)
		self.assertIn("allowUnclassifiedConversation=True", methodSource)

		positionLast = object()
		class Roles:
			BUTTON = "button"
			EDITABLETEXT = "edit"
			COMBOBOX = "combo"
			LIST = "list"
			TREEVIEW = "tree"
			CHECKBOX = "check"
			RADIOBUTTON = "radio"

		class Info:
			def __init__(self): self.scanCharacters = 0
			def collapse(self): pass
			def move(self, unit, count, endPoint=None):
				self.scanCharacters = abs(count)
				return count
			def getTextWithFields(self):
				# The first 32 KiB has only four turns; the second bounded read has
				# twelve. This reproduces a large chat without allocating its prefix.
				turnCount = 4 if self.scanCharacters <= 32768 else 12
				for index in range(20 - turnCount, 20):
					yield "You said:" if index % 2 == 0 else "ChatGPT said:"
					yield "message {index}".format(index=index)

		class Buffer:
			def __init__(self): self.positions = []
			def makeTextInfo(self, position):
				self.positions.append(position)
				return Info()

		buffer = Buffer()
		prompt = object()
		class Subject:
			_buffer = buffer
			def __init__(self):
				self.explicitAttachments = []
				self._recentChatMessages = ()
				self._recentChatMessagesBuffer = None
				self._conversationMessages = ()
				self._messageListDialog = None
			def _rememberBuffer(self, focus, allowUnclassifiedConversation=False):
				self.explicitAttachments.append(allowUnclassifiedConversation)
			def _findChatGPTPromptObject(self): return prompt

		focus = object()
		namespace = {
			"api": type("Api", (), {"getFocusObject": staticmethod(lambda: focus)}),
			"_isChatGPTObject": lambda obj: True,
			"Role": Roles,
			"State": type("State", (), {"INVISIBLE": "invisible"}),
			"textInfos": type("TextInfos", (), {
				"POSITION_LAST": positionLast, "UNIT_CHARACTER": object(),
			}),
			"RECENT_CHAT_INITIAL_SCAN_CHARACTERS": 32768,
			"_extendScanStart": lambda info, count: info.move("character", -count, endPoint="start"),
			"RECENT_CHAT_MAX_SCAN_CHARACTERS": 524288,
			"ChatMessageAccumulator": ChatMessageAccumulator,
			"MESSAGE_LIST_LIMIT": 100,
			"ChatMessageFieldCollector": ChatMessageFieldCollector,
			"isCodexPromptLabel": isCodexPromptLabel,
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		for name in methodNames:
			setattr(Subject, name, namespace[name])
		subject = Subject()
		messages = namespace["_currentChatMessages"](subject)
		self.assertEqual([True], subject.explicitAttachments)
		self.assertEqual([prompt, prompt], buffer.positions)
		self.assertEqual(10, len(messages))
		self.assertEqual(("user", "message 10"), messages[0])
		self.assertEqual(("assistant", "message 19"), messages[-1])
		# The second shortcut is cache-only: no Chromium fields are traversed again.
		self.assertEqual(messages, namespace["_currentChatMessages"](subject))
		self.assertEqual([prompt, prompt], buffer.positions)

	def test_conversation_message_list_keeps_100_turns_without_changing_shortcuts(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_cacheRecentChatMessages"
		)
		namespace = {
			"MESSAGE_LIST_LIMIT": 100,
			"ui": type("Ui", (), {"message": staticmethod(lambda message: None)}),
			"_": lambda text: text,
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			_buffer = object()
			_conversationMessages = ()
			_messageListDialog = None
			_messageListRefreshPending = False
		subject = Subject()
		namespace["_cacheRecentChatMessages"](
			subject, [("assistant", f"response {index}") for index in range(120)],
		)
		self.assertEqual(100, len(subject._conversationMessages))
		self.assertEqual(("assistant", "response 20"), subject._conversationMessages[0])
		self.assertEqual(10, len(subject._recentChatMessages))
		self.assertEqual(("assistant", "response 110"), subject._recentChatMessages[0])
		self.assertIs(subject._buffer, subject._recentChatMessagesBuffer)
		class Dialog:
			def __init__(self): self.snapshots = []
			def updateMessages(self, messages): self.snapshots.append(tuple(messages))
		waiting = Subject()
		waiting._messageListDialog = Dialog()
		namespace["_cacheRecentChatMessages"](waiting, [("assistant", "Loaded response")])
		self.assertEqual(1, len(waiting._messageListDialog.snapshots))
		namespace["_cacheRecentChatMessages"](waiting, [("assistant", "Updated response")])
		self.assertEqual(1, len(waiting._messageListDialog.snapshots))
		waiting._messageListRefreshPending = True
		namespace["_cacheRecentChatMessages"](waiting, [("assistant", "Updated response")])
		self.assertEqual(2, len(waiting._messageListDialog.snapshots))
		self.assertEqual((("assistant", "Updated response"),), waiting._messageListDialog.snapshots[-1])
		self.assertFalse(waiting._messageListRefreshPending)

	def test_conversation_message_list_refresh_requests_a_deferred_scan(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_requestConversationMessageListRefresh"
		)
		namespace = {}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			_buffer = object()
			_messageListRefreshPending = False
			def __init__(self): self.polls = []
			def _schedulePoll(self, **kwargs): self.polls.append(kwargs)
		subject = Subject()
		self.assertIsNone(namespace["_requestConversationMessageListRefresh"](subject))
		self.assertTrue(subject._messageListRefreshPending)
		self.assertEqual([{"delay": 50, "requestInspection": True}], subject.polls)

	def test_conversation_message_list_is_native_read_only_and_app_scoped(self):
		dialogSource = (PLUGIN_PATH.parent / "messageListDialog.py").read_text(encoding="utf-8")
		moduleSource = (PLUGIN_PATH.parents[2] / "appModules" / "chatgpt.py").read_text(encoding="utf-8")
		self.assertIn("wx.ListBox", dialogSource)
		self.assertIn("wx.TE_MULTILINE | wx.TE_READONLY", dialogSource)
		self.assertIn("self.messageList.SetFocus()", dialogSource)
		self.assertIn('self.status.SetLabel(_("Refreshing conversation messages…"))', dialogSource)
		self.assertIn("def script_openConversationMessages", moduleSource)
		self.assertNotIn('"kb:NVDA+alt+shift+r": "openConversationMessages"', moduleSource)
		pluginSource = PLUGIN_PATH.read_text(encoding="utf-8")
		self.assertIn("self._messageListDialog.Show()\n\t\t\tself._messageListDialog.messageList.SetFocus()", pluginSource)
		self.assertIn('"enableMessageList": "boolean(default=True)"', pluginSource)
		self.assertIn('if not _settings()["enableMessageList"]:', pluginSource)

	def test_disabled_conversation_message_list_never_touches_chatgpt_focus(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_openConversationMessageList"
		)
		messages = []
		namespace = {
			"_settings": lambda: {"enableMessageList": False},
			"_": lambda text: text,
			"ui": type("Ui", (), {"message": staticmethod(messages.append)}),
			"api": type("Api", (), {"getFocusObject": staticmethod(lambda: self.fail("focus queried while disabled"))}),
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		namespace["_openConversationMessageList"](object())
		self.assertEqual(
			["Conversation message list is disabled in ChatGPT Desktop Access settings"],
			messages,
		)

	def test_chat_message_extraction_removes_trailing_chatgpt_interface_text(self):
		for text in (
			"3:07 PM", "Today 3:19 PM", "13:45", "Working for 17s", "Working for 4m 4s",
			"Edited 7 files", "Good response", "Bad response", "Change permissions",
			"Review changed files", "Copy message", "Thinking", "Step 1 / 5",
			"Add files and more", "Full access",
		):
			self.assertTrue(isChatMessageTrailingUiText(text), text)
		for text in ("Meet at 3:07 PM tomorrow", "I edited 7 files", "This is a good response"):
			self.assertFalse(isChatMessageTrailingUiText(text), text)
		tokens = (
			("speaker", "assistant"), ("text", "Actual answer"), ("text", "Edited 7 files"),
			("text", "+21 -20"), ("text", "Good response"), ("text", "3:02 PM"),
			("speaker", "user"), ("text", "Actual question"), ("text", "3:07 PM"),
			("text", "Working for 17s"),
			("speaker", "assistant"), ("text", "Latest answer"), ("text", "Change permissions"),
		)
		self.assertEqual(
			(("assistant", "Actual answer"), ("user", "Actual question"), ("assistant", "Latest answer")),
			chatMessagesFromTokens(tokens),
		)

	def test_chat_message_extraction_skips_hidden_response_copy_and_preserves_split_words(self):
		tokens = (
			("speaker", "user"), ("text", "L"), ("text", "ooks like this works. "),
			("speaker", "assistant"),
			("text", "Response complete: Real answer. Real answer. Thinking Step 1 / 5"),
			("text", "Real answer. "), ("text", "Second paragraph."),
			("text", "Thinking"), ("text", "Step 1 / 5"),
		)
		self.assertEqual(
			(("user", "Looks like this works."), ("assistant", "Real answer. Second paragraph.")),
			chatMessagesFromTokens(tokens),
		)

	def test_changelog_is_clean_for_accessible_display(self):
		markdown = "# Changelog\n\nAll notable changes.\n\n## 2.2.0\n\n### What to test\n\n- Added **history**.\n- Uses `clicks`."
		self.assertEqual(
			"Complete release history\n\nAll notable changes.\n\nVersion 2.2.0\n\nWhat to test\n\nAdded history.\nUses clicks.",
			changelogForDisplay(markdown),
		)

	def test_release_notes_viewer_title_guard(self):
		self.assertTrue(viewerTitleMatches("Codex — current release notes", "Codex — current release notes"))
		self.assertTrue(viewerTitleMatches("Codex — current release notes", "Codex — CURRENT RELEASE NOTES dialog"))
		self.assertFalse(viewerTitleMatches("Codex — current release notes", "NVDA Settings"))
		self.assertFalse(viewerTitleMatches("Codex — current release notes", "Unrelated Codex — current release notes"))
		self.assertFalse(viewerTitleMatches("", "NVDA Settings"))

	def test_output_actions_with_all_channels_available(self):
		self.assertEqual(
			{"speech": True, "braille": True, "tone": True},
			outputActions(True, False, True, True, "command"),
		)

	def test_output_actions_can_disable_tones_while_speech_is_available(self):
		self.assertEqual(
			{"speech": True, "braille": True, "tone": False},
			outputActions(True, False, True, False, "command"),
		)

	def test_output_actions_when_addon_speech_is_disabled(self):
		self.assertEqual(
			{"speech": False, "braille": True, "tone": True},
			outputActions(False, False, True, True, "command"),
		)

	def test_output_actions_when_nvda_speech_mode_is_off(self):
		self.assertEqual(
			{"speech": False, "braille": True, "tone": True},
			outputActions(True, True, True, True, "command"),
		)

	def test_output_actions_respect_disabled_fallback(self):
		self.assertEqual(
			{"speech": False, "braille": False, "tone": False},
			outputActions(True, True, False, False, "command"),
		)

	def test_output_actions_require_a_tone_category(self):
		self.assertFalse(outputActions(False, False, True, True, None)["tone"])

	def test_tone_patterns_are_short_and_category_specific(self):
		self.assertNotEqual(tonePattern("command"), tonePattern("search"))
		self.assertLessEqual(sum(duration for frequency, duration in tonePattern("completion")), 250)
		self.assertEqual(((392, 35), (523, 55)), tonePattern("backgroundPulse1"))
		self.assertNotEqual(tonePattern("backgroundPulse1"), tonePattern("backgroundPulse2"))

	def test_failure_uses_descending_tone_pattern(self):
		pattern = tonePattern("completion", "Command failed with exit code 1")
		frequencies = [frequency for frequency, duration in pattern]
		self.assertEqual(frequencies, sorted(frequencies, reverse=True))
		self.assertNotEqual(pattern, tonePattern("completion", "Command finished"))
		self.assertEqual("failure", soundKey("completion", "Command failed"))
		self.assertEqual("completion", soundKey("completion", "Command finished"))
		self.assertEqual("other", soundKey("unknown"))

	def test_final_commentary_cannot_restart_completed_task(self):
		self.assertTrue(nextBusyState(False, "command"))
		self.assertFalse(nextBusyState(True, "completion"))
		self.assertFalse(nextBusyState(False, commentary=True))
		self.assertTrue(nextBusyState(True, commentary=True))

	def test_active_polling_uses_lower_cost_fallback(self):
		self.assertEqual(500, pollDelay(True, 500))
		self.assertEqual(1000, pollDelay(False, 750))
		self.assertEqual(2000, pollDelay(False, 2000))

	def test_controls_without_invoke_are_expanded_through_ui_automation(self):
		# NVDA's UI Automation objects raise NotImplementedError from doAction for
		# ChatGPT's Add files and more button, which has no Invoke pattern.
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		function = next(
			node for node in pluginTree.body
			if isinstance(node, ast.FunctionDef) and node.name == "_pressControl"
		)
		namespace = {}
		exec(compile(ast.Module(body=[function], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		pressControl = namespace["_pressControl"]
		calls = []

		class Pattern:
			def __init__(self, state): self.CurrentExpandCollapseState = state
			def Expand(self): calls.append("expand")
			def Collapse(self): calls.append("collapse")
			def Toggle(self): calls.append("toggle")

		class Control:
			UIAElement = object()
			def __init__(self, patterns): self.patterns = patterns
			def doAction(self): raise NotImplementedError
			def _getUIAPattern(self, patternId, interface): return self.patterns.get(patternId)

		uiaHandler = type(sys)("UIAHandler")
		uiaHandler.UIA_ExpandCollapsePatternId, uiaHandler.UIA_TogglePatternId = 10005, 10015
		uiaHandler.IUIAutomationExpandCollapsePattern = uiaHandler.IUIAutomationTogglePattern = object
		sys.modules["UIAHandler"] = uiaHandler
		try:
			pressControl(Control({10005: Pattern(0)}))
			pressControl(Control({10005: Pattern(1)}))
			pressControl(Control({10015: Pattern(0)}))
			with self.assertRaises(NotImplementedError):
				pressControl(Control({}))
		finally:
			del sys.modules["UIAHandler"]
		self.assertEqual(["expand", "collapse", "toggle"], calls)
		plain = type("Plain", (), {"doAction": lambda self: calls.append("action")})()
		pressControl(plain)
		self.assertEqual("action", calls[-1])
		with self.assertRaises(NotImplementedError):
			pressControl(type("NoUIA", (), {"doAction": lambda self: (_ for _ in ()).throw(NotImplementedError())})())
		self.assertNotIn(".doAction()", PLUGIN_PATH.read_text(encoding="utf-8").replace("		obj.doAction()", ""))

	def test_attachment_button_and_prompt_editor_do_not_depend_on_one_label(self):
		for label in ("Add files and more", "Add photos and files", "Add photos & files", "Attach files", "Upload files"):
			self.assertEqual("files", core.promptControlKind(label), label)
			self.assertTrue(core.isAttachmentButtonLikeLabel(label), label)
		for label in ("Add files", "Attach", "Photos", "Add"):
			self.assertTrue(core.isAttachmentButtonLikeLabel(label), label)
		for label in ("", "Send prompt", "Switch mode, current mode: ChatGPT", "Model"):
			self.assertFalse(core.isAttachmentButtonLikeLabel(label), label)
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		functions = [
			node for node in pluginTree.body
			if isinstance(node, ast.FunctionDef) and node.name in ("_domClassNames", "_isPromptEditor")
		]
		namespace = {"CHATGPT_PROMPT_EDITOR_CLASS": core.CHATGPT_PROMPT_EDITOR_CLASS, "MODE_SWITCH_BUTTON_LABELS": core.MODE_SWITCH_BUTTON_LABELS, "SOURCES_MENU_BUTTON_NAME": core.SOURCES_MENU_BUTTON_NAME, "ADD_FILES_BUTTON_NAME": core.ADD_FILES_BUTTON_NAME,}
		exec(compile(ast.Module(body=functions, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		isPromptEditor = namespace["_isPromptEditor"]
		ia2Prompt = type("IA2", (), {"IA2Attributes": {"class": "ProseMirror"}})()
		element = type("Element", (), {"CurrentClassName": "ProseMirror"})()
		uiaPrompt = type("UIA", (), {"IA2Attributes": None, "UIAElement": element})()
		other = type("Other", (), {"IA2Attributes": {"class": "ProseMirrorLike text-sm"}})()
		self.assertTrue(isPromptEditor(ia2Prompt))
		self.assertTrue(isPromptEditor(uiaPrompt))
		self.assertFalse(isPromptEditor(other))
		self.assertFalse(isPromptEditor(object()))

	def test_chat_and_work_switch_reports_and_switches(self):
		toggles = [("Chat", False), ("Work", True)]
		self.assertEqual("Work", core.selectedComposerMode(toggles))
		self.assertEqual("Chat", core.otherComposerMode(toggles, "Work"))
		self.assertEqual("Chat", core.selectedComposerMode([("Chat", True), ("Work", False)]))
		# Nothing or both selected is not a usable reading.
		self.assertEqual("", core.selectedComposerMode([("Chat", False), ("Work", False)]))
		self.assertEqual("", core.selectedComposerMode([("Chat", True), ("Work", True)]))
		self.assertEqual("", core.selectedComposerMode([]))
		self.assertEqual("", core.otherComposerMode([("Work", True)], "Work"))
		appSource = (Path(PLUGIN_PATH).parents[2] / "appModules" / "chatgpt.py").read_text(encoding="utf-8")
		self.assertIn('_runToolkitCommand("_reportOrSwitchComposerMode", getLastScriptRepeatCount() >= 1)', appSource)
		pluginSource = PLUGIN_PATH.read_text(encoding="utf-8")
		# UI Automation work for the switch stays off NVDA's main thread.
		self.assertIn("handler.MTAThreadQueue.put_nowait(probe)", pluginSource.split("def _reportOrSwitchComposerMode")[1].split("def _announceComposerMode")[0])

	def test_support_report_names_the_chatgpt_app_version(self):
		path = r"C:\Program Files\WindowsApps\OpenAI.Codex_26.1013.3656.0_x64__2p2nqsd0c76g0\app\ChatGPT.exe"
		self.assertEqual("package 26.1013.3656.0, program 155.0.8059.40", core.chatGPTAppVersionSummary(path, "155.0.8059.40"))
		self.assertEqual("package 26.1013.3656.0", core.chatGPTAppVersionSummary(path, ""))
		self.assertEqual("program 1.2", core.chatGPTAppVersionSummary(r"C:\Apps\ChatGPT.exe", "1.2"))
		self.assertEqual("unknown", core.chatGPTAppVersionSummary("", None))
		# The same number twice is reported once.
		self.assertEqual("package 26.1013.4894.0", core.chatGPTAppVersionSummary(path.replace("3656", "4894"), "26.1013.4894.0"))
		self.assertEqual(
			["attachment-sample.txt", "Web search"],
			core.uniqueLabels(["  attachment-sample.txt ", "", None, "￼ Web  search", "Web search"]),
		)
		self.assertIn("ChatGPT app: {appVersion}", PLUGIN_PATH.read_text(encoding="utf-8"))

	def test_sidebar_chat_titles_are_not_activity_in_live_events(self):
		# ChatGPT shows sidebar chats at any time; "Using VoiceOver Rotor" reads
		# like Codex progress but must not start Working feedback.
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in ("_isSidebarChatButton", "_announceStatus")
		]
		Role = type("Role", (), {"BUTTON": "button", "LISTITEM": "listitem"})
		namespace = {"ATTACHMENT_POPUP_ROW_CLASS": core.ATTACHMENT_POPUP_ROW_CLASS, "ATTACHMENT_POPUP_CLASS_KEY": core.ATTACHMENT_POPUP_CLASS_KEY, "_domClassNames": lambda obj: str(getattr(obj, "domClass", "") or ""), "Role": Role, "statusDetails": core.statusDetails, "_isConversationObject": lambda obj: True}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		announced = []
		class Subject:
			_isSidebarChatButton = namespace["_isSidebarChatButton"]
			_announceStatus = namespace["_announceStatus"]
			def _announceLabel(self, label): announced.append(label)
		def control(name, parent=None):
			return type("Control", (), {"role": Role.BUTTON, "name": name, "parent": parent})()
		sidebarItem = type("Item", (), {"role": Role.LISTITEM, "name": "Using VoiceOver Rotor"})()
		subject = Subject()
		self.assertFalse(subject._announceStatus(control("Using VoiceOver Rotor", sidebarItem)))
		# A row of the "@" or Add files and more menu lists chat titles too.
		menuRow = control("Using VoiceOver Rotor ChatGPT conversation")
		menuRow.domClass = "text-default min-h-[var(--app-menu-item-height,0px)]"
		self.assertFalse(subject._announceStatus(menuRow))
		# A title remembered from a scan is recognized even without its list item.
		subject._sidebarChatTitleKeys = {"ran the numbers"}
		self.assertFalse(subject._announceStatus(control("Ran the numbers")))
		self.assertEqual([], announced)
		# Real progress in the conversation is still announced.
		self.assertTrue(subject._announceStatus(control("Using tool")))
		self.assertEqual(["Using tool"], announced)

	def test_chatgpt_interface_names_live_in_one_place(self):
		# ChatGPT renames these between releases; each must be fixable in one line.
		coreSource = CORE_PATH.read_text(encoding="utf-8")
		pluginSource = PLUGIN_PATH.read_text(encoding="utf-8")
		central = coreSource.split("# ChatGPT interface names", 1)[1].split("COMPOSER_TOOL_ICON_CLASS", 1)[0]
		for literal in ('"ask chatgpt"', '"work with chatgpt"', '"Composer mode"', '"app-menu-item-height"', '"ProseMirror"'):
			self.assertIn(literal, central, literal)
			self.assertEqual(1, coreSource.count(literal) + pluginSource.count(literal), literal)
		self.assertNotIn('"Add files and more"', pluginSource)
		self.assertNotIn('"Switch mode, current mode: ChatGPT"', pluginSource)
		self.assertTrue(core.isCodexPromptLabel("Ask ChatGPT"))
		self.assertTrue(core.looksLikeCodexConversation("Chat title Work with ChatGPT"))
		self.assertEqual("files", core.promptControlKind(core.ADD_FILES_BUTTON_NAME))

	def test_compatibility_check_names_what_changed_after_a_chatgpt_update(self):
		healthy = core.chatGPTCompatibilityFindings(
			["Work with ChatGPT"], ["Switch mode, current mode: ChatGPT", "Add files and more", "Chat"],
			["Add files and more", "Dictate"], True,
		)
		self.assertEqual(([], ["message field: Work with ChatGPT", "Chat and Work switch shown"]), healthy)
		# An unrecognized prompt label, as when ChatGPT introduced "Ask ChatGPT".
		problems, notes = core.chatGPTCompatibilityFindings(
			["Talk to ChatGPT"], ["Switch mode, current mode: ChatGPT", "Add files and more"], [], False,
		)
		self.assertEqual(["message field label not recognized: Talk to ChatGPT"], problems)
		# A renamed button is named only when it sits beside the message field.
		problems, notes = core.chatGPTCompatibilityFindings(
			["Ask ChatGPT"],
			["Current mode: ChatGPT", "Add photos & files", "Add sugar to the recipe"],
			["Add photos & files", "Dictate"], False,
		)
		self.assertEqual(["Add files and more button not found (message field buttons: Add photos & files)"], problems)
		self.assertNotIn("sugar", " ".join(problems))
		problems, notes = core.chatGPTCompatibilityFindings(["Ask ChatGPT"], ["Add files and more"], [], False)
		self.assertEqual(["ChatGPT and Codex mode switch not found"], problems)
		# Nothing can be concluded on a page without a message field, such as Settings.
		self.assertIsNone(core.chatGPTCompatibilityFindings([], ["Settings"], [], False))
		self.assertIn("ChatGPT compatibility check: {compatibility}", PLUGIN_PATH.read_text(encoding="utf-8"))

	def test_slash_menu_rows_and_highlight_are_announced(self):
		# Rows as ChatGPT's "/" menu exposes them: the title is split into one
		# text piece per letter, so only the description is a whole piece.
		row = "text-default outline-hidden min-h-[var(--app-menu-item-height,0px)] flex"
		rows = [
			(row + " bg-primary-ghost-hover", "Feedback Send feedback about this chat", ["", "Send feedback about this chat"]),
			(row, "Goal Set a goal to keep pursuing", ["", "Set a goal to keep pursuing"]),
			(row, "Model", [""]),
			(row, "Reasoning Light", ["", "Light"]),
		]
		options = core.attachmentPopupOptionsFromRows(rows)
		self.assertEqual(["Feedback", "Goal", "Model", "Reasoning"], [option["title"] for option in options])
		self.assertEqual("Send feedback about this chat", options[0]["description"])
		self.assertEqual("Light", options[3]["description"])
		self.assertEqual((4, options[0], 1), core.suggestionMenuReading(options, True))
		moved = [dict(option, highlighted=index == 1) for index, option in enumerate(options)]
		self.assertEqual((4, moved[1], 2), core.suggestionMenuReading(moved, False))
		self.assertEqual((0, None, 0), core.suggestionMenuReading((), False))
		self.assertEqual("downarrow", core.gestureKeyName("kb(laptop):downArrow"))
		self.assertEqual("escape", core.gestureKeyName("kb:escape"))
		self.assertEqual("", core.gestureKeyName("br(freedomScientific):dot1"))

		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in ("_announceSuggestionMenu", "_closeSuggestionMenuTracking")
		]
		spoken, cancelled = [], []
		namespace = {
			"suggestionMenuReading": core.suggestionMenuReading,
			"attachmentOptionKey": core.attachmentOptionKey,
			"_": lambda text: text,
			"ui": type("Ui", (), {"message": staticmethod(spoken.append)}),
			"speech": type("Speech", (), {"cancelSpeech": staticmethod(lambda: cancelled.append(True))}),
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			_announceSuggestionMenu = namespace["_announceSuggestionMenu"]
			_closeSuggestionMenuTracking = namespace["_closeSuggestionMenuTracking"]
			def _suggestionMenuAnnouncementsEnabled(self): return True
		subject = Subject()
		subject._announceSuggestionMenu("open", options)
		self.assertEqual("Suggestions: 4. Feedback, Send feedback about this chat, 1 of 4", spoken[-1])
		self.assertTrue(subject._suggestionMenuOpen)
		subject._announceSuggestionMenu("move", moved)
		self.assertEqual("Goal, Set a goal to keep pursuing, 2 of 4", spoken[-1])
		self.assertEqual([True], cancelled)
		# Typing that leaves the same list and highlight says nothing more.
		subject._announceSuggestionMenu("filter", moved)
		self.assertEqual(2, len(spoken))
		subject._announceSuggestionMenu("move", ())
		self.assertFalse(subject._suggestionMenuOpen)
		self.assertEqual(2, len(spoken))

	def test_slow_conversation_scans_are_spaced_out(self):
		# Usual Chromium document scans take milliseconds and are never delayed.
		self.assertEqual(0.0, core.slowScanPauseSeconds(0.0))
		self.assertEqual(0.0, core.slowScanPauseSeconds(0.2))
		# UI Automation document scans took 2.1 to 2.9 seconds in ChatGPT.
		self.assertEqual(50.0, core.slowScanPauseSeconds(2.5))
		self.assertEqual(60.0, core.slowScanPauseSeconds(8.0))
		for invalid in (None, "slow", float("nan")):
			self.assertEqual(0.0, core.slowScanPauseSeconds(invalid))
		source = PLUGIN_PATH.read_text(encoding="utf-8")
		self.assertIn("and not self._attachmentMenuFlowActive()", source)
		self.assertIn("elapsed >= slowScanPauseSeconds(", source)

	def test_full_buffer_inspection_is_event_driven_and_typing_safe(self):
		# Dirty events are retained, but no whole-document read may interrupt typing.
		self.assertFalse(bufferInspectionDue(True, 0, False, False, True))
		self.assertTrue(bufferInspectionDue(True, 0, False, False, False))
		# A running task keeps a bounded fallback without scanning twice per second.
		self.assertFalse(bufferInspectionDue(False, 4.9, True, False, False))
		self.assertTrue(bufferInspectionDue(False, 5.0, True, False, False))
		# Prompt typing also suppresses fallback scans.
		self.assertFalse(bufferInspectionDue(False, 100, True, True, True))
		# Idle ChatGPT is event-only whether focused or in the background.
		self.assertFalse(bufferInspectionDue(False, 1000, False, False, False))
		self.assertFalse(bufferInspectionDue(False, 1000, False, True, False))
		self.assertFalse(bufferInspectionDue(False, float("nan"), True, True, False))

	def test_content_free_timing_counters_are_bounded_and_rate_limited(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(node for node in pluginTree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin")
		methods = [node for node in pluginClass.body if isinstance(node, ast.FunctionDef) and node.name in {
			"_recordOperationTiming", "_operationTimingSummary",
		}]
		class Clock:
			now = 100.0
			@classmethod
			def monotonic(cls): return cls.now
		warnings = []
		namespace = {
			"time": Clock,
			"log": type("Log", (), {"warning": staticmethod(lambda *args: warnings.append(args))}),
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			_operationTimings = None
			def __init__(self): self._operationTimings = {}
		for method in methods:
			setattr(Subject, method.name, namespace[method.name])
		subject = Subject()
		self.assertEqual("not measured", subject._operationTimingSummary("conversation scan"))
		subject._recordOperationTiming("conversation scan", 120.4)
		subject._recordOperationTiming("conversation scan", 150.1)
		self.assertEqual(1, len(warnings))
		self.assertEqual("last 150 ms; max 150 ms; slow 2/2", subject._operationTimingSummary("conversation scan"))
		Clock.now = 161.0
		subject._recordOperationTiming("mode detection", 700)
		subject._recordOperationTiming("conversation scan", 101)
		self.assertEqual(3, len(warnings))
		self.assertEqual("last 700 ms; max 700 ms; slow 1/1", subject._operationTimingSummary("mode detection"))
		subject._recordOperationTiming("chat text", 1000)
		self.assertNotIn("chat text", subject._operationTimings)
		self.assertEqual({"conversation scan", "mode detection"}, set(subject._operationTimings))

	def test_closed_conversation_window_requires_a_confirmed_grace_period(self):
		self.assertFalse(conversationWindowShouldDetach(False, False, False, 10, 2))
		self.assertFalse(conversationWindowShouldDetach(True, None, None, 10, 2))
		self.assertFalse(conversationWindowShouldDetach(True, True, True, 10, 2))
		self.assertFalse(conversationWindowShouldDetach(True, False, False, 1.99, 2))
		self.assertTrue(conversationWindowShouldDetach(True, False, False, 2, 2))
		self.assertTrue(conversationWindowShouldDetach(True, True, False, 2, 2))
		self.assertFalse(conversationWindowShouldDetach(True, False, False, float("nan"), 2))

	def test_runtime_window_close_detaches_stale_conversation_state(self):
		pluginSource = PLUGIN_PATH.read_text(encoding="utf-8")
		pluginTree = ast.parse(pluginSource)
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in (
				"_conversationWindowHandleFrom", "_conversationWindowIsAvailable",
				"_rememberConversationWindowFromEvent", "_detachConversationIfWindowClosed",
			)
		]
		class WinUser:
			GA_ROOT = 2
			GA_ROOTOWNER = 3
			exists = True
			visible = True
			@staticmethod
			def getAncestor(handle, relation): return handle + 100
			@classmethod
			def isWindow(cls, handle): return cls.exists
			@classmethod
			def isWindowVisible(cls, handle): return cls.visible
		class Subject:
			_buffer = object()
			_conversationWindowHandle = 110
			_conversationWindowProcessId = 700
			_conversationWindowUnavailableAt = 0.0
			_conversationClosedAt = 12.0
			_conversationMode = "codex"
			_conversationModeProbeGeneration = 2
			_conversationModeProbePendingGeneration = 2
			_monitoringAnnounced = True
			def __init__(self):
				self.resets = []
				self.actionsCancelled = 0
				self.focusRecoveries = 0
				self._embeddedBrowserLoadingPercent = 50
				self._chatHistoryExpansionTimer = None
				self._pendingChatHistoryExpansion = None
			def _resetTaskState(self, reason): self.resets.append(reason)
			def _conversationWindowIsAvailable(self, handle):
				return namespace["_conversationWindowIsAvailable"](self, handle)
			def _windowProcessId(self, handle): return 700
			def _recoverFocusAfterConversationClose(self, closedProcessId=0):
				self.focusRecoveries += closedProcessId
				return True
			def _resetEmbeddedBrowserProgress(self): self._embeddedBrowserLoadingPercent = None
			def _cancelChatHistoryExpansion(self):
				self._chatHistoryExpansionTimer = None
				self._pendingChatHistoryExpansion = None
			def _cancelPendingChatHistoryOpen(self):
				self._pendingChatHistoryOpen = None
			def _cancelConversationWindowActions(self):
				self.actionsCancelled += 1
			def _resetAttachmentMenuTracking(self):
				self._attachmentMenuActiveAt = 0.0
			def _cancelAttachmentSourceFocus(self):
				pass
		namespace = {
			"winUser": WinUser,
			"_isChatGPTObject": lambda obj: True,
			"conversationWindowShouldDetach": conversationWindowShouldDetach,
			"CONVERSATION_WINDOW_CLOSE_GRACE_SECONDS": 2.0,
			"log": type("Log", (), {"info": lambda *args, **kwargs: None})(),
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		subject = Subject()
		obj = type("Object", (), {"windowHandle": 10})()
		self.assertEqual(110, namespace["_conversationWindowHandleFrom"](subject, obj, object()))
		self.assertTrue(namespace["_rememberConversationWindowFromEvent"](subject, obj))
		self.assertEqual(110, subject._conversationWindowHandle)
		self.assertEqual(0.0, subject._conversationClosedAt)
		documentRoot = type("Object", (), {"windowHandle": 20})()
		buffer = type("Buffer", (), {"rootNVDAObject": documentRoot})()
		self.assertEqual(120, namespace["_conversationWindowHandleFrom"](subject, obj, buffer))
		self.assertTrue(namespace["_conversationWindowIsAvailable"](subject, 110))
		WinUser.visible = False
		self.assertFalse(namespace["_conversationWindowIsAvailable"](subject, 110))
		self.assertFalse(namespace["_detachConversationIfWindowClosed"](subject, 100.0))
		self.assertEqual(1, subject.actionsCancelled)
		self.assertFalse(namespace["_detachConversationIfWindowClosed"](subject, 101.99))
		self.assertTrue(namespace["_detachConversationIfWindowClosed"](subject, 102.0))
		self.assertIsNone(subject._buffer)
		self.assertEqual("", subject._conversationMode)
		self.assertEqual(0, subject._conversationModeProbePendingGeneration)
		self.assertEqual(0.0, subject._modeSelectorOpenedAt)
		self.assertEqual(102.0, subject._conversationClosedAt)
		self.assertFalse(subject._monitoringAnnounced)
		self.assertIsNone(subject._embeddedBrowserLoadingPercent)
		self.assertEqual(["ChatGPT window closed"], subject.resets)
		self.assertEqual(700, subject.focusRecoveries)

	def test_confirmed_window_close_restores_external_focus_and_nvda_event_pipeline(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methodNames = {
			"_cancelCloseFocusRecovery", "_stableExternalFocusRoot", "_rememberExternalFocus",
			"_focusRecoveryCandidate", "_confirmCloseFocusRecovery",
			"_recoverFocusAfterConversationClose",
		}
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in methodNames
		]
		def appObject(appName, handle, name="Inbox", windowClassName="ExternalWindow"):
			return type("Object", (), {
				"appModule": type("AppModule", (), {"appName": appName})(),
				"windowHandle": handle,
				"name": name,
				"windowClassName": windowClassName,
				"states": set(),
				"setFocus": lambda self: setattr(self, "focusCalls", getattr(self, "focusCalls", 0) + 1),
			})()
		external = appObject("outlook", 200)
		chat = appObject("chatgpt", 100, "Do anything")
		transient = appObject("searchhost", 300, "Search")
		class WinUser:
			GA_ROOT = 2
			foreground = 100
			setForegroundCalls = []
			@staticmethod
			def getAncestor(handle, relation): return handle
			@staticmethod
			def isWindow(handle): return handle in {100, 200, 300}
			@staticmethod
			def isWindowVisible(handle): return True
			@classmethod
			def getForegroundWindow(cls): return cls.foreground
			@classmethod
			def setForegroundWindow(cls, handle):
				cls.foreground = handle
				cls.setForegroundCalls.append(handle)
		class Desktop:
			@staticmethod
			def objectWithFocus(): return chat
			@staticmethod
			def objectInForeground(): return transient
		class Api:
			focus = chat
			@staticmethod
			def getDesktopObject(): return Desktop()
			@classmethod
			def getFocusObject(cls): return cls.focus
		class EventHandler:
			events = []
			@classmethod
			def queueEvent(cls, name, obj): cls.events.append((name, obj))
		class Timer:
			def __init__(self, delay, callback, *args):
				self.delay = delay
				self.callback = callback
				self.args = args
				self.stopped = False
			def Stop(self): self.stopped = True
		class Wx:
			@staticmethod
			def CallLater(delay, callback, *args): return Timer(delay, callback, *args)
		class Log:
			@staticmethod
			def info(*args, **kwargs): pass
			@staticmethod
			def debug(*args, **kwargs): pass
			@staticmethod
			def debugWarning(*args, **kwargs): pass
		def isChatGPTObject(obj):
			return getattr(getattr(obj, "appModule", None), "appName", "") == "chatgpt"
		namespace = {
			"State": type("State", (), {"DEFUNCT": object()}),
			"winUser": WinUser,
			"api": Api,
			"eventHandler": EventHandler,
			"wx": Wx,
			"log": Log,
			"_isChatGPTObject": isChatGPTObject,
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			def __init__(self):
				self._appFocusState = True
				self._lastExternalFocusObject = external
				self._lastExternalFocusWindowHandle = 200
				self._closeFocusRecoveryTimer = None
				self._closeFocusRecoveryGeneration = 0
				self.focusUpdates = []
			def _updateAppFocusState(self, obj):
				self.focusUpdates.append(obj)
				self._appFocusState = False
				return "inactive"
		for name in methodNames:
			setattr(Subject, name, namespace[name])
		subject = Subject()
		self.assertFalse(subject._rememberExternalFocus(transient))
		self.assertTrue(subject._recoverFocusAfterConversationClose())
		self.assertEqual([external], subject.focusUpdates)
		self.assertEqual([200], WinUser.setForegroundCalls)
		self.assertEqual(1, external.focusCalls)
		self.assertEqual(200, subject._closeFocusRecoveryTimer.delay)
		timer = subject._closeFocusRecoveryTimer
		timer.callback(*timer.args)
		self.assertEqual([("gainFocus", external)], EventHandler.events)

	def test_close_recovery_activates_next_app_when_previous_window_was_also_closed(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methodNames = {
			"_cancelCloseFocusRecovery", "_stableExternalFocusRoot", "_focusRecoveryCandidate",
			"_windowProcessId", "_fallbackExternalWindowHandle",
			"_confirmCloseFocusRecovery", "_recoverFocusAfterConversationClose",
		}
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in methodNames
		]
		def appObject(appName, handle, name):
			return type("Object", (), {
				"appModule": type("AppModule", (), {"appName": appName})(),
				"windowHandle": handle,
				"name": name,
				"windowClassName": "AppWindow",
				"states": set(),
			})()
		chat = appObject("chatgpt", 100, "ChatGPT")
		closedExplorer = appObject("explorer", 200, "Files")
		whatsApp = appObject("whatsapp", 400, "WhatsApp")
		class WinUser:
			GA_ROOT = 2
			GA_ROOTOWNER = 3
			GW_HWNDNEXT = 2
			WS_EX_TOOLWINDOW = 0x80
			WS_EX_NOACTIVATE = 0x08000000
			foreground = 100
			setForegroundCalls = []
			@staticmethod
			def getTopWindow(handle): return 100
			@staticmethod
			def getWindow(handle, relation): return {100: 300, 300: 400, 400: 0}.get(handle, 0)
			@staticmethod
			def getWindowThreadProcessID(handle): return ({100: 10, 300: 20, 400: 40}.get(handle, 0), 1)
			@staticmethod
			def getExtendedWindowStyle(handle): return 0
			@staticmethod
			def getWindowText(handle): return {100: "ChatGPT", 300: "Program Manager", 400: "WhatsApp"}.get(handle, "")
			@staticmethod
			def getClassName(handle): return {100: "Chrome_WidgetWin_1", 300: "Progman", 400: "WhatsApp"}.get(handle, "")
			@staticmethod
			def getAncestor(handle, relation): return handle
			@staticmethod
			def isWindow(handle): return handle in {100, 300, 400}
			@staticmethod
			def isWindowVisible(handle): return handle in {100, 300, 400}
			@staticmethod
			def isWindowEnabled(handle): return True
			@classmethod
			def getForegroundWindow(cls): return cls.foreground
			@classmethod
			def setForegroundWindow(cls, handle):
				cls.foreground = handle
				cls.setForegroundCalls.append(handle)
		class Desktop:
			ready = False
			@staticmethod
			def objectWithFocus(): return whatsApp if Desktop.ready and WinUser.foreground == 400 else chat
			@staticmethod
			def objectInForeground(): return whatsApp if Desktop.ready and WinUser.foreground == 400 else chat
		class Api:
			@staticmethod
			def getDesktopObject(): return Desktop()
			@staticmethod
			def getFocusObject(): return chat
		class EventHandler:
			events = []
			@classmethod
			def queueEvent(cls, name, obj): cls.events.append((name, obj))
		class Timer:
			def __init__(self, delay, callback, *args):
				self.delay, self.callback, self.args = delay, callback, args
				self.stopped = False
			def Stop(self): self.stopped = True
		class Wx:
			@staticmethod
			def CallLater(delay, callback, *args): return Timer(delay, callback, *args)
		class Log:
			@staticmethod
			def info(*args, **kwargs): pass
			@staticmethod
			def debug(*args, **kwargs): pass
			@staticmethod
			def debugWarning(*args, **kwargs): pass
		namespace = {
			"State": type("State", (), {"DEFUNCT": object()}),
			"winUser": WinUser,
			"api": Api,
			"eventHandler": EventHandler,
			"wx": Wx,
			"log": Log,
			"_isChatGPTObject": lambda obj: obj is chat,
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			def __init__(self):
				self._appFocusState = True
				self._lastExternalFocusObject = closedExplorer
				self._lastExternalFocusWindowHandle = 200
				self._closeFocusRecoveryTimer = None
				self._closeFocusRecoveryGeneration = 0
				self.focusUpdates = []
			def _updateAppFocusState(self, obj):
				self.focusUpdates.append(obj)
				self._appFocusState = False
		for name in methodNames:
			setattr(Subject, name, namespace[name])
		subject = Subject()
		self.assertTrue(subject._recoverFocusAfterConversationClose(10))
		self.assertEqual([None], subject.focusUpdates)
		self.assertEqual([400], WinUser.setForegroundCalls)
		self.assertEqual(400, subject._closeFocusRecoveryTimer.args[1])
		timer = subject._closeFocusRecoveryTimer
		timer.callback(*timer.args)
		self.assertEqual(350, subject._closeFocusRecoveryTimer.delay)
		self.assertEqual([], EventHandler.events)
		Desktop.ready = True
		timer = subject._closeFocusRecoveryTimer
		timer.callback(*timer.args)
		self.assertEqual([("gainFocus", whatsApp)], EventHandler.events)

	def test_native_external_focus_cancels_pending_close_recovery(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in {
				"_cancelCloseFocusRecovery", "_stableExternalFocusRoot", "_rememberExternalFocus",
			}
		]
		class Timer:
			stopped = False
			def Stop(self): self.stopped = True
		class WinUser:
			GA_ROOT = 2
			@staticmethod
			def getAncestor(handle, relation): return handle
			@staticmethod
			def isWindow(handle): return True
			@staticmethod
			def isWindowVisible(handle): return True
		namespace = {
			"State": type("State", (), {"DEFUNCT": object()}),
			"winUser": WinUser,
			"_isChatGPTObject": lambda obj: False,
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			_closeFocusRecoveryGeneration = 4
			_closeFocusRecoveryTimer = Timer()
			_lastExternalFocusObject = None
			_lastExternalFocusWindowHandle = 0
		for name in ("_cancelCloseFocusRecovery", "_stableExternalFocusRoot", "_rememberExternalFocus"):
			setattr(Subject, name, namespace[name])
		subject = Subject()
		timer = subject._closeFocusRecoveryTimer
		obj = type("Object", (), {
			"appModule": type("AppModule", (), {"appName": "outlook"})(),
			"windowHandle": 200,
			"name": "Inbox",
			"windowClassName": "ExternalWindow",
			"states": set(),
		})()
		self.assertTrue(subject._rememberExternalFocus(obj))
		self.assertTrue(timer.stopped)
		self.assertIsNone(subject._closeFocusRecoveryTimer)
		self.assertEqual(5, subject._closeFocusRecoveryGeneration)
		self.assertIs(obj, subject._lastExternalFocusObject)

	def test_stale_mode_control_event_cannot_restore_a_detached_conversation(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in {
				"_eventBelongsToRetainedConversationBuffer", "_observeConversationModeControl",
			}
		]
		buttonRole = object()
		namespace = {
			"Role": type("Role", (), {"BUTTON": buttonRole}),
			"_isChatGPTObject": lambda obj: True,
			"conversationModeFromSwitchLabel": conversationModeFromSwitchLabel,
			"_switchControlMode": lambda obj: conversationModeFromSwitchControl(
				getattr(obj, "name", ""), "", "button", False,
			),
			"log": type("Log", (), {"debug": lambda *args, **kwargs: None})(),
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			def __init__(self):
				self._buffer = None
				self.observedModes = []
			def _eventBelongsToRetainedConversationBuffer(self, obj):
				return namespace["_eventBelongsToRetainedConversationBuffer"](self, obj)
			def _setConversationMode(self, mode, reason, authoritative=False):
				self.observedModes.append((mode, reason, authoritative))
				return True
		subject = Subject()
		staleBuffer = object()
		obj = type("Object", (), {
			"role": buttonRole,
			"name": "Switch mode, current mode: Codex",
			"treeInterceptor": staleBuffer,
		})()
		self.assertFalse(namespace["_observeConversationModeControl"](
			subject, obj, "closed selector event",
		))
		self.assertEqual([], subject.observedModes)
		subject._buffer = staleBuffer
		self.assertTrue(namespace["_observeConversationModeControl"](
			subject, obj, "active selector event",
		))
		self.assertEqual([("codex", "active selector event", True)], subject.observedModes)

	def test_closing_window_cancels_every_delayed_focus_capable_action(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_cancelConversationWindowActions"
		)

		class Timer:
			def __init__(self): self.stopped = False
			def Stop(self): self.stopped = True
		class Dialog:
			def __init__(self): self.closed = False
			def Close(self): self.closed = True

		class Subject:
			def __init__(self):
				self._pendingChatHistoryAction = object()
				self._chatHistoryActionTimer = Timer()
				self._chatActionRetryTimer = Timer()
				self._pendingDirectChatAction = object()
				self._unarchiveFocusTimer = Timer()
				self._unarchiveFocusAttempts = 9
				self._popupFocusTimer = Timer()
				self._pendingPopupDialog = object()
				self._lastFocusedPopupDialog = object()
				self._promptInspectionTimer = Timer()
				self._pendingPromptObject = object()
				self._chatHistoryDialog = Dialog()
				self.cancelled = []
			def _cancelPendingChatHistoryOpen(self): self.cancelled.append("historyOpen")
			def _cancelChatHistoryExpansion(self): self.cancelled.append("historyExpansion")
			def _cancelVoiceControlConfirmation(self): self.cancelled.append("voice")

		namespace = {}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		subject = Subject()
		timers = (
			subject._chatHistoryActionTimer, subject._chatActionRetryTimer,
			subject._unarchiveFocusTimer, subject._popupFocusTimer,
			subject._promptInspectionTimer,
		)
		dialog = subject._chatHistoryDialog
		namespace["_cancelConversationWindowActions"](subject)
		self.assertTrue(all(timer.stopped for timer in timers))
		self.assertTrue(dialog.closed)
		self.assertEqual(["historyOpen", "historyExpansion", "voice"], subject.cancelled)
		for name in (
			"_pendingChatHistoryAction", "_pendingDirectChatAction", "_pendingPopupDialog",
			"_lastFocusedPopupDialog", "_pendingPromptObject",
		):
			self.assertIsNone(getattr(subject, name), name)

	def test_braille_display_chords_activate_typing_protection(self):
		self.assertTrue(isBrailleTypingGestureIdentifier("br(hims.BrailleSense):dot4+dot2"))
		self.assertTrue(isBrailleTypingGestureIdentifier("br(hims.BrailleSense):space"))
		self.assertTrue(isBrailleTypingGestureIdentifier("br(hims.BrailleSense):dot7"))
		self.assertFalse(isBrailleTypingGestureIdentifier("br(hims.BrailleSense):rightSideScrollDown"))
		self.assertFalse(isBrailleTypingGestureIdentifier("kb(laptop):a"))
		self.assertFalse(brailleTypingGestureCommitsText("br(hims.BrailleSense):dot4+dot2"))
		self.assertTrue(brailleTypingGestureCommitsText("br(hims.BrailleSense):space"))
		self.assertTrue(brailleTypingGestureCommitsText("br(hims.BrailleSense):dot8+dot3+space"))

	def test_delayed_caret_event_preserves_only_an_active_braille_composition(self):
		self.assertTrue(shouldPreserveBrailleComposition(True, True, True, 0.6))
		self.assertTrue(shouldPreserveBrailleComposition(True, True, True, 1.0))
		self.assertFalse(shouldPreserveBrailleComposition(True, True, True, 1.01))
		self.assertFalse(shouldPreserveBrailleComposition(False, True, True, 0.1))
		self.assertFalse(shouldPreserveBrailleComposition(True, False, True, 0.1))
		self.assertFalse(shouldPreserveBrailleComposition(True, True, False, 0.1))
		self.assertFalse(shouldPreserveBrailleComposition(True, True, True, float("nan")))

	def test_runtime_polling_preserves_state_and_coalesces_prompt_reads(self):
		plugin = PLUGIN_PATH.read_text(encoding="utf-8")
		self.assertIn("self._bufferDirty = False", plugin)
		self.assertIn("self._skippedBufferInspectionCount += 1", plugin)
		self.assertIn("PROMPT_TYPING_QUIET_SECONDS", plugin)
		self.assertIn("RESPONSE_COMPLETION_SETTLE_SECONDS = 5.0", plugin)
		self.assertIn("self._detachConversationIfWindowClosed(now)", plugin)
		self.assertIn("if self._conversationWindowHandle:\n\t\t\t\tconversationDetached", plugin)
		self.assertIn("winUser.isWindowVisible(handle)", plugin)
		self.assertEqual(2, plugin.count("if self._pendingResponseCompletionAt:\n\t\t\treturn"))
		self.assertIn("self._schedulePromptInspection(obj)", plugin)
		self.assertIn("self._promptInspectionTimer.Stop()", plugin)
		self.assertIn("inputCore.decide_executeGesture.register(self._observeInputGesture)", plugin)
		self.assertIn("inputCore.decide_executeGesture.unregister(self._observeInputGesture)", plugin)
		self.assertIn("self._brailleCompositionActive", plugin)
		self.assertIn("def event_caret(self, obj, nextHandler):", plugin)
		self.assertIn("shouldPreserveBrailleComposition(", plugin)
		self.assertIn("handler._uncontSentTime = time.time()", plugin)
		self.assertLess(
			plugin.index("from braille import input as brailleInputModule"),
			plugin.index("import brailleInput as brailleInputModule"),
		)
		self.assertNotIn("handlerClass.handleCaretMove =", plugin)
		self.assertIn('getattr(obj, "role", None) == Role.BUTTON', plugin)
		self.assertNotIn('getattr(obj, "role", None) != Role.EDITABLETEXT\n\t\t\t\tand self._eventUsesConversationBuffer(obj)', plugin)
		self.assertIn("preserving task state", plugin)
		self.assertNotIn('self._setBusy(False, "buffer inspection failed")', plugin)
		initializationPrefix = plugin.split("self._promptInspectionTimer = None", 1)[0]
		self.assertNotIn("if self._promptInspectionTimer", initializationPrefix)

	def test_event_triggered_scans_are_coalesced_away_from_the_last_poll(self):
		self.assertEqual(150, coalescedPollDelay(10, 0.0))
		self.assertEqual(100, coalescedPollDelay(10, 0.05))
		self.assertEqual(10, coalescedPollDelay(10, 0.20))
		self.assertEqual(250, coalescedPollDelay(250, 0.0))
		self.assertEqual(10, coalescedPollDelay(10, float("inf")))
		self.assertEqual(150, coalescedPollDelay(10, float("-inf")))
		self.assertEqual(150, coalescedPollDelay(10, float("nan")))
		self.assertEqual(150, coalescedPollDelay(10, -1.0))
		self.assertEqual(150, coalescedPollDelay("bad", None))
		self.assertEqual(10, coalescedPollDelay(10, 0.20, float("inf")))
		self.assertFalse(shouldReplaceScheduledPoll(10.1, 10.2))
		self.assertTrue(shouldReplaceScheduledPoll(10.2, 10.1))
		self.assertTrue(shouldReplaceScheduledPoll(0.0, 10.1))

	def test_poll_preserves_the_single_timer_scheduled_from_inside_its_callback(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = {
			node.name: node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in ("_schedulePoll", "_poll")
		}
		class Timer:
			def __init__(self, delay=0, callback=None):
				self.delay = delay
				self.callback = callback
				self.stopped = False
			def Stop(self):
				self.stopped = True
		created = []
		class Wx:
			@staticmethod
			def CallLater(delay, callback):
				timer = Timer(delay, callback)
				created.append(timer)
				return timer
		class Clock:
			@staticmethod
			def monotonic():
				return 100.0
		class Subject:
			def __init__(self):
				self._timer = Timer()
				self._nextPollAt = 100.5
				self._lastPollAt = 99.5
				self._bufferDirty = False
				self._buffer = None
				self._conversationWindowHandle = 0
				self._busy = False
				self._busyStartedAt = 0.0
				self._pendingResponseCompletionAt = 0.0
				self._lastScannedLabel = ""
				self._active = False
				self.workingClicks = 0
			def _rememberBuffer(self, obj):
				self._schedulePoll(300, requestInspection=True)
			def _setBusy(self, busy, reason): pass
			def _announceBackgroundPulse(self): pass
			def _announceContinuousWorkingClick(self): self.workingClicks += 1
		namespace = {
			"wx": Wx, "time": Clock,
			"api": type("Api", (), {"getFocusObject": staticmethod(lambda: object())}),
			"coalescedPollDelay": lambda requested, elapsed: requested,
			"shouldReplaceScheduledPoll": lambda existing, requested: True,
			"shouldFinalizeResponseCompletion": lambda *args: False,
			"pollDelay": lambda active, idle: 500,
			"_settings": lambda: {"maximumBusyMinutes": 30, "idlePollMs": 1000},
			"log": type("Log", (), {"debugWarning": staticmethod(lambda *args, **kwargs: None)})(),
			"RESPONSE_COMPLETION_SETTLE_SECONDS": 5.0,
		}
		for method in methods.values():
			exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		Subject._schedulePoll = namespace["_schedulePoll"]
		Subject._poll = namespace["_poll"]
		subject = Subject()
		currentTimer = subject._timer
		subject._poll()
		self.assertTrue(currentTimer.stopped)
		self.assertEqual(1, len(created))
		self.assertIs(created[0], subject._timer)
		self.assertEqual(300, created[0].delay)
		self.assertEqual(1, subject.workingClicks)
		created.clear()
		periodicSubject = Subject()
		periodicSubject._rememberBuffer = lambda obj: None
		periodicSubject._poll()
		self.assertEqual(1, len(created))
		self.assertIs(created[0], periodicSubject._timer)
		self.assertEqual(500, created[0].delay)
		self.assertEqual(1, periodicSubject.workingClicks)
		created.clear()
		earlyCloseSubject = Subject()
		earlyCloseSubject._conversationWindowHandle = 1234
		earlyCloseSubject.detachCalls = 0
		def detach(now):
			earlyCloseSubject.detachCalls += 1
			earlyCloseSubject._conversationWindowHandle = 0
			return True
		earlyCloseSubject._detachConversationIfWindowClosed = detach
		earlyCloseSubject._rememberBuffer = lambda obj: self.fail(
			"A confirmed early close must not try to attach a conversation buffer",
		)
		earlyCloseSubject._poll()
		self.assertEqual(1, earlyCloseSubject.detachCalls)
		self.assertEqual(1, len(created))

	def test_repetitive_poll_diagnostics_are_rate_limited(self):
		plugin = PLUGIN_PATH.read_text(encoding="utf-8")
		self.assertIn("self._lastRejectedBufferLogAt = 0.0", plugin)
		self.assertIn("now - self._lastRejectedBufferLogAt >= 30.0", plugin)
		self.assertIn("logSnapshot = (scanMode, decision)", plugin)
		self.assertIn("logSnapshot, self._lastDeferredHistoryLog", plugin)

	def test_continuous_working_sound_uses_quiet_gaps_for_clicks_and_tones(self):
		self.assertTrue(shouldPlayContinuousWorkingClick(True, True, "clicks", True, 1.4, 1.4))
		self.assertTrue(shouldPlayContinuousWorkingClick(True, True, "tones", True, 1.4, 1.4))
		self.assertFalse(shouldPlayContinuousWorkingClick(False, True, "clicks", True, 10, 1.4))
		self.assertFalse(shouldPlayContinuousWorkingClick(True, False, "clicks", True, 10, 1.4))
		self.assertFalse(shouldPlayContinuousWorkingClick(True, True, "invalid", True, 10, 1.4))
		self.assertFalse(shouldPlayContinuousWorkingClick(True, True, "clicks", False, 10, 1.4))
		self.assertFalse(shouldPlayContinuousWorkingClick(True, True, "clicks", True, 1.39, 1.4))

	def test_focus_state_clicks_only_on_transitions(self):
		state, cue = focusStateTransition(None, False)
		self.assertEqual((False, ""), (state, cue))
		state, cue = focusStateTransition(state, True)
		self.assertEqual((True, "active"), (state, cue))
		state, cue = focusStateTransition(state, True)
		self.assertEqual((True, ""), (state, cue))
		state, cue = focusStateTransition(state, False)
		self.assertEqual((False, "inactive"), (state, cue))

	def test_reentry_moves_only_stale_activity_focus_to_newer_response(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in tree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methodNames = {
			"_scheduleConversationEntryCorrection", "_restoreLatestConversationPosition", "_isSidebarChatButton",
		}
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in methodNames
		]

		class Clock:
			@staticmethod
			def monotonic(): return 10.0

		class Queue:
			eventQueue = object()
			calls = []
			@staticmethod
			def queueFunction(*args): Queue.calls.append(args)

		class Object:
			def __init__(self, role, name):
				self.role = role
				self.name = name

		activity = Object("button", "Edited files, ran commands")
		latestObject = Object("heading", "ChatGPT said:")
		prompt = object()
		class Info:
			def __init__(self, latest=False):
				self.latest = latest
				self.updated = False
				self.NVDAObjectAtStart = latestObject if latest else activity
			def collapse(self): pass
			def move(self, unit, count, endPoint=None):
				return count if self.latest and endPoint == "start" else 0
			def find(self, text, reverse=False, caseSensitive=False):
				return self.latest and text == "ChatGPT said:" and reverse and not caseSensitive
			def compareEndPoints(self, other, comparison):
				return 1 if self.latest and comparison == "startToStart" else 0
			def updateCaret(self): self.updated = True

		class Buffer:
			passThrough = False
			def __init__(self): self.latestInfo = None
			def makeTextInfo(self, position):
				info = Info(position is prompt)
				if position is prompt:
					self.latestInfo = info
				return info

		class Api:
			navigator = None
			@staticmethod
			def getFocusObject(): return activity
			@staticmethod
			def setNavigatorObject(obj): Api.navigator = obj

		class Subject:
			def __init__(self):
				self._conversationActivatedAt = 9.0
				self._conversationEntryCorrectionGeneration = 0
				self._conversationNavigationUntil = 0.0
				self._busy = True
				self._buffer = Buffer()
			def _conversationBrowseModeActive(self): return not self._buffer.passThrough
			def _rememberBuffer(self, obj): return True
			def _findChatGPTPromptObject(self): return prompt

		namespace = {
			"ATTACHMENT_POPUP_ROW_CLASS": core.ATTACHMENT_POPUP_ROW_CLASS, "ATTACHMENT_POPUP_CLASS_KEY": core.ATTACHMENT_POPUP_CLASS_KEY, "_domClassNames": lambda obj: str(getattr(obj, "domClass", "") or ""),
			"time": Clock,
			"queueHandler": Queue,
			"api": Api,
			"textInfos": type("TextInfos", (), {
				"POSITION_LAST": object(), "UNIT_CHARACTER": object(),
			}),
			"_roleName": lambda obj: obj.role,
			"_isChatGPTObject": lambda obj: True,
			"statusDetails": statusDetails,
			"CONVERSATION_ENTRY_CORRECTION_SECONDS": 4.0,
			"CONVERSATION_NAVIGATION_QUIET_SECONDS": 3.0,
			"RECENT_CHAT_INITIAL_SCAN_CHARACTERS": 32768,
			"_extendScanStart": lambda info, count: info.move("character", -count, endPoint="start"),
			"_activePluginInstance": None,
			"log": type("Log", (), {
				"info": staticmethod(lambda *args, **kwargs: None),
				"debugWarning": staticmethod(lambda *args, **kwargs: None),
			})(),
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		for name in methodNames:
			setattr(Subject, name, namespace[name])
		subject = Subject()
		namespace["_activePluginInstance"] = subject

		self.assertTrue(subject._scheduleConversationEntryCorrection(activity))
		self.assertEqual(1, len(Queue.calls))
		_queue, callback, *args = Queue.calls.pop()
		self.assertTrue(callback(*args))
		self.assertTrue(subject._buffer.latestInfo.updated)
		self.assertIs(latestObject, Api.navigator)
		self.assertEqual(13.0, subject._conversationNavigationUntil)

		# A user gesture increments the generation before the queued callback and
		# therefore wins without moving the browse cursor.
		subject._conversationActivatedAt = 9.0
		self.assertTrue(subject._scheduleConversationEntryCorrection(activity))
		_queue, callback, *args = Queue.calls.pop()
		subject._conversationEntryCorrectionGeneration += 1
		subject._buffer.latestInfo = None
		self.assertFalse(callback(*args))
		self.assertIsNone(subject._buffer.latestInfo)

		subject._conversationActivatedAt = 9.0
		subject._busy = False
		self.assertFalse(subject._scheduleConversationEntryCorrection(activity))
		self.assertEqual([], Queue.calls)

	def test_deleting_a_prompt_draft_never_starts_processing(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in tree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_trackPromptDraftState"
		)
		self.assertNotIn("_beginPromptSubmission", ast.unparse(method))
		class Roles:
			EDITABLETEXT = "editableText"
		class Object:
			role = Roles.EDITABLETEXT
			def __init__(self, value): self.value = value
		namespace = {
			"Role": Roles,
			"_isCodexPromptObject": lambda obj: True,
			"textInfos": type("TextInfos", (), {"POSITION_ALL": object()}),
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			_promptHadText = None
		subject = Subject()
		self.assertFalse(namespace["_trackPromptDraftState"](subject, Object("draft")))
		self.assertTrue(subject._promptHadText)
		self.assertFalse(namespace["_trackPromptDraftState"](subject, Object("")))
		self.assertFalse(subject._promptHadText)
		self.assertFalse(namespace["_trackPromptDraftState"](subject, Object("")))

	def test_prompt_submission_gesture_recognizes_only_unmodified_enter(self):
		for identifier in (
			"kb(laptop):enter", "kb(desktop):enter", "kb:enter",
			"kb(desktop):numpadEnter", "br(hims.BrailleSense):dot8",
		):
			self.assertTrue(isPromptSubmissionGestureIdentifier(identifier), identifier)
		for identifier in (
			"kb(laptop):shift+enter", "kb(laptop):control+enter",
			"br(hims.BrailleSense):dot7+dot8", "br(hims.BrailleSense):space",
			"kb(laptop):a", "enter", "",
		):
			self.assertFalse(isPromptSubmissionGestureIdentifier(identifier), identifier)

	def test_conversation_navigation_gestures_are_unmodified_browse_keys(self):
		for identifier in (
			"kb(laptop):upArrow", "kb(desktop):downArrow", "kb:pageUp",
			"kb(laptop):pageDown", "kb(laptop):home", "kb(laptop):end",
		):
			self.assertTrue(isConversationNavigationGestureIdentifier(identifier), identifier)
		for identifier in (
			"kb(laptop):shift+upArrow", "kb(laptop):control+home",
			"br(hims):rightSideScrollDown", "kb(laptop):enter", "upArrow", "",
		):
			self.assertFalse(isConversationNavigationGestureIdentifier(identifier), identifier)

	def test_prompt_submission_gesture_requires_focus_mode_and_prompt_text_evidence(self):
		self.assertFalse(promptSubmissionGestureShouldStart(False, True, True))
		self.assertFalse(promptSubmissionGestureShouldStart(True, False, False))
		self.assertFalse(promptSubmissionGestureShouldStart(True, None, False))
		self.assertTrue(promptSubmissionGestureShouldStart(True, True, False))
		self.assertTrue(promptSubmissionGestureShouldStart(True, False, True))

	def test_prompt_enter_observer_queues_feedback_without_claiming_the_gesture(self):
		plugin = PLUGIN_PATH.read_text(encoding="utf-8")
		observerStart = plugin.index("\tdef _observeInputGesture(self, gesture):")
		observerEnd = plugin.index("\n\tdef event_caret", observerStart)
		observer = plugin[observerStart:observerEnd]
		self.assertIn("isPromptSubmissionGestureIdentifier(identifier)", observer)
		self.assertIn("promptSubmissionGestureShouldStart(", observer)
		self.assertIn('getattr(self._buffer, "passThrough", True)', observer)
		self.assertIn("queueHandler.queueFunction(", observer)
		self.assertIn("queueHandler.eventQueue, self._beginPromptSubmissionFromGesture", observer)
		self.assertIn("self._conversationNavigationUntil", observer)
		self.assertIn("now < self._conversationNavigationUntil", plugin)
		self.assertIn("return True", observer)
		self.assertNotIn("gesture.send", observer)
		self.assertNotIn("raise NoInputGestureAction", observer)

	def test_prompt_enter_observer_ignores_browse_mode_activation_and_empty_focus_mode(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in tree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_observeInputGesture"
		)

		class Clock:
			@staticmethod
			def monotonic():
				return 10.0

		class Queue:
			eventQueue = object()
			calls = []

			@staticmethod
			def queueFunction(*args):
				Queue.calls.append(args)

		namespace = {
			"time": Clock,
			"threading": type("Threading", (), {
				"current_thread": staticmethod(lambda: 1),
				"main_thread": staticmethod(lambda: 1),
			}),
			"queueHandler": Queue,
			"isPromptSubmissionGestureIdentifier": isPromptSubmissionGestureIdentifier,
			"promptSubmissionGestureShouldStart": promptSubmissionGestureShouldStart,
			"isBrailleTypingGestureIdentifier": isBrailleTypingGestureIdentifier,
			"brailleTypingGestureCommitsText": brailleTypingGestureCommitsText,
			"isConversationNavigationGestureIdentifier": isConversationNavigationGestureIdentifier,
			"CONVERSATION_NAVIGATION_QUIET_SECONDS": 3.0,
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)

		class Buffer:
			def __init__(self, passThrough):
				self.passThrough = passThrough

		class Gesture:
			def __init__(self, identifier):
				self.identifiers = (identifier,)

		class Subject:
			_appFocusState = True
			_promptFocused = True
			_promptHadText = False
			_promptTypingUntil = 0.0
			_brailleCompositionActive = False
			_lastBrailleTextInjectionAt = 0.0
			_promptSubmissionGestureQueued = False
			_promptSubmissionDraftQueued = ""
			_promptDraftText = "draft"
			_conversationNavigationUntil = 0.0
			_conversationActivatedAt = 0.0
			_conversationEntryCorrectionGeneration = 0

			def _beginPromptSubmissionFromGesture(self):
				pass

			def _conversationBrowseModeActive(self):
				return not self._buffer.passThrough

			def _noteAttachmentActivationGesture(self, identifiers):
				pass

		helper = next(node for node in pluginClass.body if isinstance(node, ast.FunctionDef) and node.name == "_observePromptGestureIdentifiers")
		exec(compile(ast.Module(body=[helper], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		Subject._observePromptGestureIdentifiers = namespace["_observePromptGestureIdentifiers"]
		subject = Subject()
		subject._buffer = Buffer(False)
		namespace["_observeInputGesture"](subject, Gesture("kb(laptop):upArrow"))
		self.assertEqual(13.0, subject._conversationNavigationUntil)
		subject._conversationNavigationUntil = 0.0
		subject._promptHadText = True
		subject._promptTypingUntil = 20.0
		namespace["_observeInputGesture"](subject, Gesture("br(hims.BrailleSense):dot8"))
		self.assertEqual([], Queue.calls)
		self.assertFalse(subject._promptSubmissionGestureQueued)
		self.assertEqual(0.0, subject._promptTypingUntil)

		subject._buffer = Buffer(True)
		subject._promptHadText = False
		namespace["_observeInputGesture"](subject, Gesture("kb(laptop):enter"))
		self.assertEqual([], Queue.calls)

		subject._promptTypingUntil = 20.0
		namespace["_observeInputGesture"](subject, Gesture("br(hims.BrailleSense):dot8"))
		self.assertEqual(1, len(Queue.calls))
		self.assertTrue(subject._promptSubmissionGestureQueued)

		Queue.calls.clear()
		subject._promptSubmissionGestureQueued = False
		subject._buffer = Buffer(False)
		namespace["_observeInputGesture"](subject, Gesture("br(hims.BrailleSense):dot1+dot5"))
		self.assertEqual(0.0, subject._promptTypingUntil)
		self.assertFalse(subject._brailleCompositionActive)

		subject._promptFocused = False
		namespace["_observeInputGesture"](subject, Gesture("br(hims):rightSideScrollDown"))
		self.assertEqual(13.0, subject._conversationNavigationUntil)

	def test_attachment_keyboard_input_thread_records_candidate_without_touching_chromium(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_observeInputGesture"
		)
		class Clock:
			@staticmethod
			def monotonic(): return 10.0
		class Queue:
			eventQueue = object()
			calls = []
			@staticmethod
			def queueFunction(*args): Queue.calls.append(args)
		namespace = {
			"time": Clock,
			"threading": type("Threading", (), {
				"current_thread": staticmethod(lambda: 2),
				"main_thread": staticmethod(lambda: 1),
			}),
			"queueHandler": Queue,
			"isPromptSubmissionGestureIdentifier": isPromptSubmissionGestureIdentifier,
			"isConversationNavigationGestureIdentifier": isConversationNavigationGestureIdentifier,
			"CONVERSATION_NAVIGATION_QUIET_SECONDS": 3.0,
			"log": type("Log", (), {"debugWarning": staticmethod(lambda *a, **kw: None)}),
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Gesture:
			def __init__(self, identifier): self.identifiers = (identifier,)
		class Subject:
			_appFocusState = True
			_promptFocused = False
			_conversationWindowHandle = 10
			_attachmentInputCandidateAt = 0.0
			_attachmentInputCandidateWindowHandle = 0
			_attachmentActivationAt = 0.0
			_attachmentSourceFocusTimer = None
			_conversationActivatedAt = 0.0
			_conversationEntryCorrectionGeneration = 0
			_conversationNavigationUntil = 0.0
			providerReads = 0
			def _conversationBrowseModeActive(self):
				self.providerReads += 1
				raise AssertionError("provider access on input thread")
			def _captureAttachmentActivationFromQueuedGesture(self, *args): pass
			def _noteAttachmentActivationGesture(self, *args): pass
			def _observePromptGestureIdentifiers(self, identifiers): pass
		subject = Subject()
		for key in ("kb(laptop):space", "kb(laptop):enter"):
			Queue.calls.clear()
			namespace["_observeInputGesture"](subject, Gesture(key))
			self.assertEqual(10.0, subject._attachmentInputCandidateAt)
			self.assertEqual(10, subject._attachmentInputCandidateWindowHandle)
			self.assertEqual(2, len(Queue.calls))
			self.assertEqual("_captureAttachmentActivationFromQueuedGesture", Queue.calls[0][1].__name__)
			self.assertEqual((key,), Queue.calls[0][2])
			self.assertEqual("_observePromptGestureIdentifiers", Queue.calls[1][1].__name__)
			self.assertEqual(0, subject.providerReads)
		Queue.calls.clear()
		namespace["_observeInputGesture"](subject, Gesture("kb(laptop):downArrow"))
		self.assertEqual(0.0, subject._attachmentInputCandidateAt)
		self.assertEqual(0, subject._attachmentInputCandidateWindowHandle)
		self.assertEqual("_noteAttachmentActivationGesture", Queue.calls[0][1].__name__)
		Queue.calls.clear()
		subject._appFocusState = False
		namespace["_observeInputGesture"](subject, Gesture("kb(laptop):space"))
		self.assertEqual([], Queue.calls)

	def test_chatgpt_popup_focus_never_reclaims_focus_after_switching_apps(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_focusPopupDialog"
		)
		class Roles:
			EDITABLETEXT = "edit"
			COMBOBOX = "combo"
			LIST = "list"
			TREEVIEW = "tree"
			CHECKBOX = "checkbox"
			RADIOBUTTON = "radio"
			BUTTON = "button"
		class Focus:
			current = None
			@staticmethod
			def getFocusObject(): return Focus.current
		class Control:
			def __init__(self, name, role, app=True):
				self.name = name
				self.role = role
				self.app = app
				self.parent = None
				self.firstChild = None
				self.next = None
				self.focused = False
			def setFocus(self): self.focused = True
		class Log:
			@staticmethod
			def info(*args, **kwargs): pass
			@staticmethod
			def debugWarning(*args, **kwargs): raise AssertionError("unexpected popup error")
		namespace = {
			"Role": Roles,
			"api": Focus,
			"State": type("State", (), {"INVISIBLE": "invisible", "UNAVAILABLE": "unavailable", "DEFUNCT": "defunct"}),
			"_isChatGPTObject": lambda obj: bool(getattr(obj, "app", False)),
			"isPermissionPromptText": lambda text: False,
			"isPermissionDecisionLabel": lambda text: False,
			"log": Log,
		}
		sameObject = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_sameNVDAObject")
		exec(compile(ast.Module(body=[sameObject, method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		dialog = Control("Attachment choices", "dialog")
		choice = Control("Attach files or folders", Roles.BUTTON)
		dialog.firstChild = choice
		class Subject:
			_appFocusState = True
			_conversationWindowHandle = 42
			_popupFocusTimer = object()
			_pendingPopupDialog = dialog
			_pendingPopupDialogWindowHandle = 42
			_lastFocusedPopupDialog = None
			def _conversationWindowIsAvailable(self, handle): return handle == 42
			def _conversationWindowOwnsForeground(self, handle): return handle == 42 and self.foreground
		subject = Subject()
		subject.foreground = True
		Focus.current = Control("Outlook", "window", app=False)
		namespace["_focusPopupDialog"](subject)
		self.assertFalse(choice.focused)
		self.assertIsNone(subject._pendingPopupDialog)
		subject._pendingPopupDialog = dialog
		subject._pendingPopupDialogWindowHandle = 42
		subject._appFocusState = False
		Focus.current = Control("ChatGPT prompt", Roles.EDITABLETEXT)
		namespace["_focusPopupDialog"](subject)
		self.assertFalse(choice.focused)
		subject._pendingPopupDialog = dialog
		subject._pendingPopupDialogWindowHandle = 41
		subject._appFocusState = True
		namespace["_focusPopupDialog"](subject)
		self.assertFalse(choice.focused)
		subject._pendingPopupDialog = dialog
		subject._pendingPopupDialogWindowHandle = 42
		subject.foreground = False
		namespace["_focusPopupDialog"](subject)
		self.assertFalse(choice.focused)
		subject._pendingPopupDialog = dialog
		subject._pendingPopupDialogWindowHandle = 42
		subject.foreground = True
		namespace["_focusPopupDialog"](subject)
		self.assertTrue(choice.focused)
		choice.focused = False
		subject._pendingPopupDialog = dialog
		subject._pendingPopupDialogWindowHandle = 42
		subject._pendingPopupInputGeneration = 1
		subject._conversationEntryCorrectionGeneration = 2
		namespace["_focusPopupDialog"](subject)
		self.assertFalse(choice.focused)
		subject._pendingPopupInputGeneration = 2
		subject._pendingPopupDialog = dialog
		subject._pendingPopupDialogWindowHandle = 42
		dialog.states = {"defunct"}
		namespace["_focusPopupDialog"](subject)
		self.assertFalse(choice.focused)
		# Issue 4: typing a project name renames the dialog's "Change marker for"
		# button. NVDA hands back a new object for the same dialog each time, so
		# focus already inside it must be recognized by equality, not identity.
		class SameControl(Control):
			def __init__(self, name, role, key):
				super().__init__(name, role)
				self.key = key
			def __eq__(self, other): return isinstance(other, SameControl) and other.key == self.key
			__hash__ = object.__hash__
		eventDialog = SameControl("Create project", "dialog", "create-project")
		marker = Control("Change marker for D", Roles.BUTTON)
		eventDialog.firstChild = marker
		nameField = Control("Project name", Roles.EDITABLETEXT)
		nameField.parent = SameControl("Create project", "dialog", "create-project")
		Focus.current = nameField
		subject._pendingPopupDialog = eventDialog
		subject._pendingPopupDialogWindowHandle = 42
		namespace["_focusPopupDialog"](subject)
		self.assertFalse(marker.focused)
		self.assertIs(subject._lastFocusedPopupDialog, eventDialog)
		ownerMethod = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_conversationWindowOwnsForeground"
		)
		class Windows:
			GA_ROOTOWNER = 3
			foreground = 42
			@staticmethod
			def getForegroundWindow(): return Windows.foreground
			@staticmethod
			def getAncestor(handle, kind): return 42 if handle in (42, 77) else handle
		ownerNamespace = {"winUser": Windows}
		exec(compile(ast.Module(body=[ownerMethod], type_ignores=[]), str(PLUGIN_PATH), "exec"), ownerNamespace)
		self.assertTrue(ownerNamespace["_conversationWindowOwnsForeground"](subject, 42))
		Windows.foreground = 77
		self.assertTrue(ownerNamespace["_conversationWindowOwnsForeground"](subject, 42))
		Windows.foreground = 99
		self.assertFalse(ownerNamespace["_conversationWindowOwnsForeground"](subject, 42))

	def test_queued_prompt_submission_starts_once_and_ignores_terminated_plugin(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in tree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_beginPromptSubmissionFromGesture"
		)
		namespace = {"_activePluginInstance": None}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)

		class Subject:
			def __init__(self):
				self._promptSubmissionGestureQueued = True
				self._promptSubmissionDraftQueued = "submitted draft"
				self._promptDraftText = ""
				self._busy = False
				self._promptHadText = True
				self.started = []
				self.polls = []

			def _beginPromptSubmission(self, reason):
				self.started.append(reason)

			def _schedulePoll(self, delay, requestInspection):
				self.polls.append((delay, requestInspection))

		subject = Subject()
		namespace["_beginPromptSubmissionFromGesture"](subject)
		self.assertFalse(subject._promptSubmissionGestureQueued)
		self.assertEqual([], subject.started)
		namespace["_activePluginInstance"] = subject
		subject._promptSubmissionGestureQueued = True
		subject._promptSubmissionDraftQueued = "submitted draft"
		namespace["_beginPromptSubmissionFromGesture"](subject)
		self.assertFalse(subject._promptHadText)
		self.assertEqual("submitted draft", subject._promptDraftText)
		self.assertEqual(["unmodified Enter gesture"], subject.started)
		self.assertEqual([(50, True)], subject.polls)
		subject._busy = True
		namespace["_beginPromptSubmissionFromGesture"](subject)
		self.assertEqual(1, len(subject.started))

	def test_prompt_labels_are_narrow_and_do_not_require_a_document_name(self):
		for label in (
			"Do anything", "Ask anything", "Message Codex", "Message ChatGPT", "Send a message",
			"Work with Codex", "Work with ChatGPT",
		):
			self.assertTrue(isCodexPromptLabel(label), label)
		self.assertTrue(looksLikeCodexConversation("Main landmark Work with Codex"))
		# ChatGPT's chat mode names its prompt differently from Codex.
		self.assertTrue(looksLikeCodexConversation("Main landmark Work with ChatGPT"))
		for label in ("Search chats", "Announcement text", "Change permissions", ""):
			self.assertFalse(isCodexPromptLabel(label), label)

	def test_user_message_number_and_submission_transition(self):
		self.assertEqual(80, userMessageNumber("Jump to user message 80"))
		self.assertIsNone(userMessageNumber("Jump to latest message"))
		state, submitted = userMessageSubmissionTransition(None, 79)
		self.assertEqual((79, False), (state, submitted))
		state, submitted = userMessageSubmissionTransition(state, 80)
		self.assertEqual((80, True), (state, submitted))
		state, submitted = userMessageSubmissionTransition(state, 80)
		self.assertEqual((80, False), (state, submitted))
		state, submitted = userMessageSubmissionTransition(state, None)
		self.assertEqual((80, False), (state, submitted))

	def test_user_message_increase_requires_active_stop_control(self):
		pending, confirmed = confirmedUserMessageSubmission(False, True, False)
		self.assertEqual((True, False), (pending, confirmed))
		pending, confirmed = confirmedUserMessageSubmission(pending, False, True)
		self.assertEqual((False, True), (pending, confirmed))
		self.assertEqual((False, False), confirmedUserMessageSubmission(False, False, True))

	def test_current_navigation_buttons_are_not_diagnostic_noise(self):
		for label in (
			"Review", "Review changed files", "Undo", "Open chat", "Edit message",
			"Worked for 2m 58s", "Worked for 27s",
			"Download Codex Status Announcer 2026.2.1",
		):
			self.assertTrue(isKnownNonStatusButton(label), label)

	def test_stop_control_and_duplicate_event_safeguards(self):
		self.assertTrue(isStopControlLabel("Stop generating"))
		self.assertTrue(isStopControlLabel("Cancel task"))
		self.assertFalse(isStopControlLabel("Send message"))
		state, stopped = stopControlTransition(False, True)
		self.assertEqual((True, False), (state, stopped))
		state, stopped = stopControlTransition(state, False)
		self.assertEqual((False, True), (state, stopped))
		self.assertTrue(shouldSuppressDuplicate("Working", "Working", 1.49))
		self.assertFalse(shouldSuppressDuplicate("Working", "Working", 1.5))
		self.assertFalse(shouldSuppressDuplicate("Thinking", "Working", 0.1))
		self.assertTrue(shouldLogDiagnosticSnapshot(("Copy",), (), 0))
		self.assertTrue(shouldLogDiagnosticSnapshot(("Retry",), ("Copy",), 1))
		self.assertFalse(shouldLogDiagnosticSnapshot(("Copy",), ("Copy",), 29.9))
		self.assertTrue(shouldLogDiagnosticSnapshot(("Copy",), ("Copy",), 30))
		self.assertFalse(shouldLogDiagnosticSnapshot((), ("Copy",), 30))

	def test_response_completion_marker_requires_baseline_and_busy_state(self):
		marker, initialized, completed = responseCompletionTransition(None, False, 100, False)
		self.assertEqual((100, True, False), (marker, initialized, completed))
		marker, initialized, completed = responseCompletionTransition(marker, initialized, 100, True)
		self.assertEqual((100, True, False), (marker, initialized, completed))
		marker, initialized, completed = responseCompletionTransition(marker, initialized, 200, True)
		self.assertEqual((200, True, True), (marker, initialized, completed))
		marker, initialized, completed = responseCompletionTransition(marker, initialized, None, True)
		self.assertEqual((200, True, False), (marker, initialized, completed))
		marker, initialized, completed = responseCompletionTransition(marker, initialized, 300, False)
		self.assertEqual((300, True, False), (marker, initialized, completed))

	def test_plain_response_complete_marker_ends_a_busy_submission(self):
		self.assertTrue(isResponseCompletionMarkerText("Response complete"))
		self.assertTrue(isResponseCompletionMarkerText(" Response   complete: finished answer "))
		self.assertFalse(isResponseCompletionMarkerText("Response completing"))
		previous = responseCompletionScanMarker(12)
		current = responseCompletionScanMarker(13)
		marker, initialized, completed = responseCompletionTransition(previous, True, current, True)
		self.assertEqual((current, True, True), (marker, initialized, completed))
		self.assertIsNone(responseCompletionScanMarker(0))

	def test_tentative_response_completion_requires_a_quiet_idle_scan(self):
		self.assertTrue(shouldFinalizeResponseCompletion(True, 30, 30, True, False, ""))
		self.assertTrue(shouldFinalizeResponseCompletion(True, 5, 5, True, False, ""))
		self.assertFalse(shouldFinalizeResponseCompletion(True, 4.99, 5, True, False, ""))
		self.assertTrue(shouldFinalizeResponseCompletion(True, 30, 30, True, False, "Reading finished"))
		self.assertTrue(shouldFinalizeResponseCompletion(True, 30, 30, True, False, "Command finished"))
		self.assertFalse(shouldFinalizeResponseCompletion(True, 30, 30, True, True, ""))
		self.assertFalse(shouldFinalizeResponseCompletion(True, 30, 30, True, False, "Running command"))
		self.assertFalse(shouldFinalizeResponseCompletion(True, 30, 30, False, False, ""))
		self.assertFalse(shouldFinalizeResponseCompletion(True, 29.9, 30, True, False, ""))

	def test_trailing_intermediate_completion_preserves_response_completion_candidate(self):
		self.assertEqual(("completion", "Reading finished"), statusDetails("Reading finished"))
		for label in ("Reading finished", "Command finished", "File edit complete"):
			self.assertFalse(supersedesResponseCompletionCandidate(label), label)
		for label in ("Reading", "Working", "Thinking", "Running command"):
			self.assertTrue(supersedesResponseCompletionCandidate(label), label)

	def test_only_whole_task_labels_end_continuous_activity(self):
		for label in ("Response complete", "Finished", "Completed task", "Cancelled"):
			self.assertTrue(isTaskCompletionLabel(label), label)
		for label in ("Ran command", "File edit complete", "Compiled project", "Search finished"):
			self.assertFalse(isTaskCompletionLabel(label), label)
		self.assertEqual("command", intermediateCompletionCategory("Ran rg --files"))
		self.assertEqual("file", intermediateCompletionCategory("File edit complete"))
		self.assertEqual("build", intermediateCompletionCategory("Compiled project"))
		self.assertEqual("search", intermediateCompletionCategory("Searched the web"))

	def test_known_codex_controls_are_not_diagnostic_noise(self):
		for label in (
			"Jump to user message 95", "Outputs", "Sources", "View all", "Copy", "Copy message",
			"Fork chat from here", "Scroll to bottom", "Add files and more", "Dictate",
			"Start voice chat", "Send", "Show 4 more files", "changelog.md+11-2",
		):
			self.assertTrue(isKnownNonStatusButton(label), label)
		self.assertFalse(isKnownNonStatusButton("Unexpected new control"))
		self.assertFalse(isKnownNonStatusButton("Running command"))
		for label in (
			"Share", "Copy", "Copy message", "Read aloud", "Regenerate response",
			"Good response", "Bad response", "More actions", "Previous response",
			"Sources", "Sources 4", "Outputs (2)", "Copy response", "Share link",
			"Show more", "Show less", "Loading", "Loading…", "Add credits", "Upgrade",
			"Update", "Update now", "Dismiss usage alert", "6% usage remaining",
			"Resets every week", "Next reset is on Sep 10", "Usage consumed", "Manage plan",
		):
			self.assertTrue(isChatHistoryInterfaceText(label), label)
		self.assertFalse(isChatHistoryInterfaceText("Plan an accessible vacation"))
		self.assertFalse(isChatHistoryInterfaceText("Sources of accessible software"))
		self.assertFalse(isChatHistoryInterfaceText("Update NVDA add-on documentation"))
		self.assertFalse(isChatHistoryInterfaceText("Upgrade an accessible computer"))
		for label in (
			"Jump to user message 1", "You said:", "ChatGPT said:", "Dismiss usage alert",
			"6% usage remaining", "Resets every week", "Next reset is tomorrow", "Usage consumed",
		):
			self.assertTrue(isChatHistoryConversationBoundary(label), label)
		self.assertFalse(isChatHistoryConversationBoundary("Discuss message navigation"))
		plugin = PLUGIN_PATH.read_text(encoding="utf-8")
		self.assertEqual(2, plugin.count("not isChatHistoryInterfaceText("))
		self.assertIn("if not recentsSeen and plainText.casefold() == \"recents\":", plugin)
		self.assertGreaterEqual(plugin.count("inRecents = inArchived = False"), 3)

	def test_activity_messages(self):
		cases = {
			"Planning next step": "Thinking",
			"Thinking": "Thinking",
			"Working": "Working",
			"Analyzing files": "Analyzing",
			"Reading package metadata": "Checking files",
			"Writing tests": "Editing code",
			"Editing source": "Editing code",
			"Applying patch": "Applying changes",
			"Generating output": "Generating",
			"Waiting for process": "Waiting for command",
			"Using tool": "Using tool",
			"Searching the web": "Searching the web",
			"Running command Get-ChildItem": "Running command",
			"Running web search": "Searching the web",
			"Searched the web": "Web search finished",
			"Ran command": "Command finished",
			"Ran command and web search": "Command and web search finished",
			"Completed task": "Task finished",
			"Response complete: final answer": "Task finished",
			"Reviewed files": "Reading finished",
			"Updated source": "File updated",
		}
		for label, expected in cases.items():
			with self.subTest(label=label):
				self.assertEqual(expected, statusMessage(label))
		self.assertEqual(("build", "Running tests"), statusDetails("Running tests: 53 tests"))
		self.assertEqual(("build", "Generating"), statusDetails("Running build"))
		self.assertEqual(("tool", "Using tool"), statusDetails("Running tool: apply_patch"))

	def test_attention_messages(self):
		self.assertEqual(("attention", "Permission required"), statusDetails("Permission required to continue"))
		self.assertEqual(("attention", "User input required"), statusDetails("Waiting for your input"))
		self.assertFalse(nextBusyState(True, "attention"))
		self.assertEqual("urgent", announcementPriority("attention", "Permission required"))

	def test_first_status_label_falls_back_to_accessible_name(self):
		self.assertEqual("Planning", firstStatusLabel("", " Planning  "))

	def test_first_status_label_rejects_ordinary_button(self):
		self.assertEqual("", firstStatusLabel("Copy", "Retry"))

	def test_compilation_and_file_edit_messages(self):
		self.assertEqual("Compiling", statusMessage("Compiling project"))
		self.assertEqual("Compilation finished", statusMessage("Compiled project"))
		self.assertEqual("Editing code", statusMessage("File edit source.py"))
		self.assertEqual("File updated", statusMessage("File edit complete source.py"))

	def test_full_mode_returns_complete_normalized_label(self):
		self.assertEqual(
			"Running shell command: python -m unittest",
			statusMessage("  Running   shell command: python -m unittest  ", verbosity="full"),
		)

	def test_full_speech_profiles_offer_standard_developer_and_raw_detail(self):
		label = "  Running   shell command: python -m unittest discover -s tests  "
		self.assertEqual("Running command: python", statusMessage(label, verbosity="full", fullProfile="standard"))
		self.assertEqual(
			"Running shell command: python -m unittest discover -s tests",
			statusMessage(label, verbosity="full", fullProfile="developer"),
		)
		self.assertEqual(
			"Running   shell command: python -m unittest discover -s tests",
			statusMessage(label, verbosity="full", fullProfile="raw"),
		)
		self.assertEqual(
			"Command finished: rg",
			statusMessage("Ran rg -n pattern source", verbosity="full", fullProfile="standard"),
		)

	def test_standard_full_profile_keeps_file_counts_and_useful_timing(self):
		self.assertEqual(
			"Running tests: 43 tests, 12 seconds",
			statusMessage("Testing project: 43 tests for 12 seconds", verbosity="full", fullProfile="standard"),
		)

	def test_minimal_speech_profiles_are_essential_balanced_and_informative(self):
		self.assertEqual("", statusMessage("Editing C:\\project\\core.py", minimalProfile="essential"))
		self.assertEqual("Thinking", statusMessage("Thinking", minimalProfile="essential"))
		self.assertEqual("Task finished", statusMessage("Response complete", minimalProfile="essential"))
		self.assertEqual("Checking files", statusMessage("Inspecting source", minimalProfile="balanced"))
		self.assertEqual("Editing code", statusMessage("Editing C:\\project\\core.py", minimalProfile="balanced"))
		self.assertEqual(
			"Editing code: core.py",
			statusMessage("Editing C:\\project\\core.py", minimalProfile="informative"),
		)
		self.assertEqual(
			"Running tests: 43 tests, 12 seconds",
			statusMessage("Testing project: 43 tests for 12 seconds", minimalProfile="informative"),
		)

	def test_minimal_results_distinguish_success_failure_and_file_updates(self):
		self.assertEqual("Tests passed", statusMessage("Tests passed: 43 tests", minimalProfile="balanced"))
		self.assertEqual("Tests failed", statusMessage("Tests failed: 1 failure", minimalProfile="balanced"))
		self.assertEqual("File updated", statusMessage("Updated core.py", minimalProfile="balanced"))
		self.assertEqual("Waiting for command", statusMessage("Waiting for command", minimalProfile="balanced"))
		self.assertEqual(
			"Editing: core.py",
			statusMessage("Editing C:\\project\\core.py", verbosity="full", fullProfile="standard"),
		)

	def test_categories(self):
		self.assertEqual(("command", "Running command"), statusDetails("Executing shell command: dir"))
		self.assertEqual(("build", "Running tests"), statusDetails("Testing project"))
		self.assertEqual(("completion", "Command failed"), statusDetails("Command failed with exit code 1"))
		self.assertEqual(("completion", "Command finished"), statusDetails("Ran rg -n pattern source"))

	def test_full_mode_speaks_complete_ran_label(self):
		label = "Ran rg -n pattern source -g '*.py'"
		self.assertEqual(label, statusMessage(label, verbosity="full"))
		self.assertEqual("Command finished", statusMessage(label))

	def test_sensitive_redaction(self):
		text = redactSensitive("Running token=abc123 remote key=mySecret C:\\Users\\alice\\project https://example.com/?key=value")
		self.assertNotIn("abc123", text)
		self.assertNotIn("alice", text)
		self.assertNotIn("key=value", text)
		self.assertNotIn("mySecret", text)
		quoted = redactSensitive('password="two word secret" C:\\Users\\Jane Doe\\project')
		self.assertNotIn("two word secret", quoted)
		self.assertNotIn("Jane Doe", quoted)
		commandLine = redactSensitive("Running command: tool --token abc123 --password 'two words'")
		self.assertNotIn("abc123", commandLine)
		self.assertNotIn("two words", commandLine)

	def test_category_output_routing_respects_master_switches(self):
		self.assertEqual(
			{"speech": True, "braille": True, "sound": True},
			categoryOutputActions("all", True, True, True),
		)
		self.assertEqual(
			{"speech": False, "braille": False, "sound": True},
			categoryOutputActions("sound", True, True, True),
		)
		self.assertEqual(
			{"speech": False, "braille": False, "sound": False},
			categoryOutputActions("speech", False, True, True),
		)

	def test_braille_reading_protection_only_suppresses_focused_routine_progress(self):
		for category in (
			"thinking", "working", "command", "search", "file", "build", "tool", "commentary",
			"backgroundPulse1", "backgroundPulse2",
		):
			self.assertTrue(shouldSuppressRoutineBraille(True, True, category, "normal"), category)
		self.assertFalse(shouldSuppressRoutineBraille(True, False, "command", "normal"))
		self.assertFalse(shouldSuppressRoutineBraille(False, True, "command", "normal"))
		self.assertFalse(shouldSuppressRoutineBraille(True, True, "command", "high"))
		self.assertFalse(shouldSuppressRoutineBraille(True, True, "completion", "high"))
		self.assertTrue(shouldSuppressRoutineBraille(True, True, "completion", "high", True))
		self.assertFalse(shouldSuppressRoutineBraille(True, True, "completion", "urgent", True))
		self.assertFalse(shouldSuppressRoutineBraille(True, True, "attention", "urgent"))
		self.assertFalse(shouldSuppressRoutineBraille(True, True, "other", "normal"))
		self.assertEqual(
			{"speech": False, "braille": False, "sound": False},
			categoryOutputActions("off", True, True, True),
		)

	def test_conversation_reading_protection_suppresses_only_browse_mode_response_updates(self):
		self.assertTrue(shouldSuppressNativeConversationUpdate(
			True, True, True, True, False, "Response: streamed assistant text",
		))
		self.assertTrue(shouldSuppressNativeConversationUpdate(
			True, True, True, True, False, "Response complete: finished text",
		))
		self.assertTrue(shouldSuppressNativeConversationUpdate(
			True, True, True, True, False, "Response complete",
		))
		self.assertTrue(shouldSuppressNativeConversationUpdate(
			True, True, True, True, False, "ChatGPT said: streamed assistant text",
		))
		for arguments in (
			(False, True, True, True, False, "Response: text"),
			(True, False, True, True, False, "Response: text"),
			(True, True, False, True, False, "Response: text"),
			(True, True, True, False, False, "Response: text"),
			(True, True, True, True, True, "Response: text"),
			(True, True, True, True, False, "Permission required: Allow or deny"),
			(True, True, True, True, False, "Running command"),
			(True, True, True, True, False, ""),
		):
			self.assertFalse(shouldSuppressNativeConversationUpdate(*arguments), arguments)

	def test_live_region_hook_withholds_response_but_passes_focus_mode_and_permissions(self):
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in tree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "event_liveRegionChange"
		)

		class Logger:
			def debug(self, *args, **kwargs): pass
			def debugWarning(self, *args, **kwargs): pass

		class Roles:
			BUTTON = "button"

		namespace = {
			"shouldSuppressNativeConversationUpdate": shouldSuppressNativeConversationUpdate,
			"usageLimitNotice": usageLimitNotice,
			"_isChatGPTObject": lambda obj: True,
			"_": lambda text: text,
			"_settings": lambda: {"protectBrailleReading": True},
			"statusDetails": statusDetails,
			"Role": Roles,
			"log": Logger(),
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)

		class Buffer:
			passThrough = False

		class Object:
			def __init__(self, name, buffer):
				self.name = name
				self.value = ""
				self.treeInterceptor = buffer
				self.role = "section"

		class Subject:
			def __init__(self):
				self._buffer = Buffer()
				self._appFocusState = True
				self._suppressedConversationUpdates = 0
				self.commentary = 0
				self.limitAlerts = []

			def _eventUsesConversationBuffer(self, obj): return True
			def _popupDialogFromObject(self, obj): return None
			def _conversationBrowseModeActive(self): return not self._buffer.passThrough
			def _schedulePopupDialogFocus(self, obj): pass
			def _announceUsageLimit(self, obj, text=""):
				notice = usageLimitNotice(text)
				if notice:
					self.limitAlerts.append(notice)
					return True
				return False
			def _announceStatus(self, obj): return False
			def _announceCommentary(self, obj):
				self.commentary += 1
				return True

		subject = Subject()
		passed = []
		response = Object("Response: streamed assistant text", subject._buffer)
		namespace["event_liveRegionChange"](subject, response, lambda: passed.append(True))
		self.assertEqual([], passed)
		self.assertEqual(0, subject.commentary)
		self.assertEqual(1, subject._suppressedConversationUpdates)

		permission = Object("Permission required: Allow or deny", subject._buffer)
		namespace["event_liveRegionChange"](subject, permission, lambda: passed.append(True))
		self.assertEqual([True], passed)
		self.assertEqual(1, subject.commentary)

		limit = Object("You've hit your usage limit. Try again at 9:45 PM.", subject._buffer)
		namespace["event_liveRegionChange"](subject, limit, lambda: passed.append(True))
		self.assertEqual([True], passed)
		self.assertEqual(1, len(subject.limitAlerts))
		self.assertEqual(1, subject.commentary)

		subject._buffer.passThrough = True
		namespace["event_liveRegionChange"](subject, response, lambda: passed.append(True))
		self.assertEqual([True, True], passed)
		self.assertEqual(2, subject.commentary)

	def test_announcement_priorities(self):
		self.assertEqual("urgent", announcementPriority("completion", "Command failed"))
		self.assertEqual("high", announcementPriority("completion", "Command finished"))
		self.assertEqual("low", announcementPriority("commentary", "Inspecting files"))
		self.assertEqual("normal", announcementPriority("command", "Running command"))

	def test_elapsed_seconds(self):
		self.assertEqual(25, elapsedSeconds("Working for 25s"))
		self.assertIsNone(elapsedSeconds("Working"))

	def test_streamed_commentary_waits_for_complete_sentences(self):
		message, offset = completedTextDelta("I am inspecting the source")
		self.assertEqual("", message)
		message, offset = completedTextDelta("I am inspecting the source. Next step", offset)
		self.assertEqual("I am inspecting the source.", message)
		message, offset = completedTextDelta("I am inspecting the source. Next step is testing.", offset)
		self.assertEqual("Next step is testing.", message)

	def test_issue_forms_do_not_use_unquoted_non_string_scalars(self):
		issueForms = PROJECT_ROOT / ".github" / "ISSUE_TEMPLATE"
		ambiguousOption = re.compile(
			r"^\s*-\s*(?:yes|no|on|off|true|false|null|none|~)\s*$",
			re.IGNORECASE | re.MULTILINE,
		)
		ambiguousStringField = re.compile(
			r"^\s*(?:name|description|title|type|id|label|placeholder|value|render):\s*"
			r"(?:yes|no|on|off|true|false|null|none|~|[-+]?\d+(?:\.\d+)?)\s*$",
			re.IGNORECASE | re.MULTILINE,
		)
		invalidForms = []
		for formPath in sorted(issueForms.glob("*.yml")):
			formText = formPath.read_text(encoding="utf-8")
			if ambiguousOption.search(formText) or ambiguousStringField.search(formText):
				invalidForms.append(formPath.name)
		self.assertEqual(
			[],
			invalidForms,
			"Issue-form strings that YAML may parse as another type must be quoted or made descriptive",
		)

	def test_trailing_completion_is_suppressed_only_after_task_completion(self):
		self.assertTrue(core.shouldSuppressTrailingCompletion("completion", False, "completion", "Ran a web search"))
		self.assertFalse(core.shouldSuppressTrailingCompletion("completion", True, "completion", "Ran a web search"))
		self.assertFalse(core.shouldSuppressTrailingCompletion("completion", False, "stop control disappeared", "Ran a web search"))
		self.assertFalse(core.shouldSuppressTrailingCompletion("command", False, "completion", "Running command"))
		self.assertFalse(core.shouldSuppressTrailingCompletion("completion", False, "completion", "Command failed"))
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_announceLabel"
		)
		namespace = {
			"statusDetails": core.statusDetails,
			"shouldSuppressTrailingCompletion": core.shouldSuppressTrailingCompletion,
			"log": type("Log", (), {"debug": lambda *args: None})(),
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		instance = type("Instance", (), {"_busy": False, "_lastStateReason": "completion"})()
		# Any fall-through would need numerous other fields and raise here.
		namespace["_announceLabel"](instance, "Ran a web search")

	def test_clicks_are_serialized_and_old_task_cues_are_discarded(self):
		started = []
		timers = []

		class Timer:
			def __init__(self, callback, args):
				self.callback = callback
				self.args = args
				self.stopped = False

			def Stop(self):
				self.stopped = True

			def fire(self):
				if self.stopped:
					raise AssertionError("Stopped timer must not fire")
				self.callback(*self.args)

		class Wx:
			def CallLater(self, delay, callback, *args):
				timer = Timer(callback, args)
				timers.append(timer)
				return timer

		class Nvwave:
			def playWaveFile(self, path):
				started.append(Path(path).stem)

		source = ast.parse(SOUND_OUTPUT_PATH.read_text(encoding="utf-8"))
		source.body = [
			node for node in source.body
			if not isinstance(node, (ast.Import, ast.ImportFrom))
		]
		namespace = {
			"__file__": str(SOUND_OUTPUT_PATH),
			"deque": deque, "os": os, "wave": wave,
			"nvwave": Nvwave(), "wx": Wx(),
			"tones": type("Tones", (), {"beep": lambda *args: None})(),
			"log": type("Log", (), {
				"debug": lambda *args: None,
				"debugWarning": lambda *args, **kwargs: None,
			})(),
			"soundKey": core.soundKey,
			"tonePattern": core.tonePattern,
		}
		exec(compile(source, str(SOUND_OUTPUT_PATH), "exec"), namespace)
		play = namespace["playProgressSound"]
		self.assertTrue(play("working"))
		self.assertFalse(play("working"))
		self.assertTrue(play("command"))
		self.assertTrue(play("file"))
		self.assertTrue(play("completion"))
		self.assertEqual(["working"], started)
		# A task ends while command, file, and intermediate completion wait.
		namespace["discardPendingActivitySounds"]()
		self.assertEqual([], list(namespace["_pendingProgressSounds"]))
		self.assertTrue(play("completion"))
		timers[-1].fire()
		self.assertEqual(["working", "completion"], started)
		timers[-1].fire()
		self.assertIsNone(namespace["_progressSoundTimer"])
		self.assertTrue(play("command"))
		self.assertTrue(play("file"))
		self.assertTrue(play("completion"))
		self.assertEqual(["working", "completion", "command"], started)
		timers[-1].fire()
		self.assertEqual(["working", "completion", "command", "file"], started)
		timers[-1].fire()
		self.assertEqual(["working", "completion", "command", "file", "completion"], started)
		self.assertTrue(play("command"))
		namespace["stopProgressSounds"]()
		self.assertTrue(timers[-1].stopped)
		self.assertEqual([], list(namespace["_pendingProgressSounds"]))
		self.assertTrue(play("command"))
		for _ in range(6):
			self.assertTrue(play("submission"))
		self.assertTrue(play("completion"))
		self.assertEqual(6, len(namespace["_pendingProgressSounds"]))
		self.assertEqual("completion", namespace["_pendingProgressSounds"][-1][0])
		namespace["stopProgressSounds"]()


	def test_global_content_events_leave_other_apps_to_nvda(self):
		"""Foreign UIA events must not query costly names, roles, or states."""
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methodNames = (
			"event_nameChange", "event_valueChange", "event_stateChange",
			"event_liveRegionChange", "event_show", "event_selection",
			"event_selectionAdd", "event_selectionWithIn", "event_hide",
			"event_alert", "event_textChange",
			"_observeConversationModeControl", "_attachmentMenuSelectionState",
		)
		namespace = {"_isChatGPTObject": lambda obj: False}
		for method in pluginClass.body:
			if isinstance(method, ast.FunctionDef) and method.name in methodNames:
				exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class ForeignObject:
			def __getattribute__(self, attribute):
				raise AssertionError("foreign accessibility property read: " + attribute)
		obj = ForeignObject()
		for name in methodNames:
			with self.subTest(method=name):
				if name.startswith("event_"):
					calls = []
					namespace[name](object(), obj, lambda: calls.append(True))
					self.assertEqual([True], calls)
				elif name == "_observeConversationModeControl":
					self.assertFalse(namespace[name](object(), obj, "foreign event"))
				else:
					self.assertFalse(namespace[name](object(), obj))

	def test_conversation_scan_limits_large_virtual_buffers(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		nodes = [
			node for node in pluginTree.body
			if isinstance(node, (ast.FunctionDef, ast.ClassDef))
			and node.name in ("_conversationScanInfo", "_SplitConversationScanInfo", "_extendScanStart", "_scanProviderInfo")
		]
		class TextInfo:
			def __init__(self, text, start=0, end=None):
				self.text, self.start = text, start
				self.end = len(text) if end is None else end
			def copy(self): return TextInfo(self.text, self.start, self.end)
			def collapse(self, end=False):
				self.start = self.end if end else self.start
				self.end = self.start
			def move(self, unit, count, endPoint=None):
				if endPoint == "end":
					old = self.end
					self.end = max(self.start, min(len(self.text), self.end + count))
					return self.end - old
				old = self.start
				self.start = max(0, min(self.end, self.start + count))
				return self.start - old
			def compareEndPoints(self, other, kind):
				selfValue = self.end if kind.startswith("end") else self.start
				otherValue = other.start if kind.endswith("Start") else other.end
				return selfValue - otherValue
			def getTextWithFields(self): return (self.text[self.start:self.end],)
		class Buffer:
			def __init__(self, text): self.text = text
			def makeTextInfo(self, position): return TextInfo(self.text)
		class OffsetsTextInfo:
			pass
		bulkMoves = []
		class RootProxyTextInfo:
			def __init__(self, inner): self.innerTextInfo = inner
			def copy(self): return RootProxyTextInfo(self.innerTextInfo.copy())
			def collapse(self, end=False): self.innerTextInfo.collapse(end=end)
			def compareEndPoints(self, other, kind):
				return self.innerTextInfo.compareEndPoints(other.innerTextInfo, kind)
			def getTextWithFields(self): return self.innerTextInfo.getTextWithFields()
			def move(self, *args, **kwargs): raise AssertionError("Proxy must not walk characters")
		class UIATextInfo:
			def move(self, unit, count, endPoint=None):
				bulkMoves.append((count, endPoint))
				return TextInfo.move(self, unit, count, endPoint=endPoint)
		namespace = {
			"UIATextInfo": UIATextInfo,
			"RootProxyTextInfo": RootProxyTextInfo,
			"textInfos": type("TextInfos", (), {
				"POSITION_ALL": "all", "UNIT_CHARACTER": "character",
				"offsets": type("OffsetsModule", (), {"OffsetsTextInfo": OffsetsTextInfo}),
			}),
			"CONVERSATION_SCAN_HEAD_CHARACTERS": 32768,
			"CONVERSATION_SCAN_TAIL_CHARACTERS": 32768,
		}
		exec(compile(ast.Module(body=nodes, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		with self.assertRaises(NotImplementedError):
			namespace["_conversationScanInfo"](Buffer("short document"))
		longText = "H" * 32768 + "M" * 10000 + "T" * 32768
		with self.assertRaises(NotImplementedError):
			namespace["_conversationScanInfo"](Buffer(longText))
		with self.assertRaises(NotImplementedError):
			namespace["_extendScanStart"](TextInfo(longText), 32768)
		class OffsetInfo(TextInfo, OffsetsTextInfo):
			@property
			def _startOffset(self): return self.start
			@_startOffset.setter
			def _startOffset(self, value): self.start = value
			@property
			def _endOffset(self): return self.end
			def move(self, *args, **kwargs):
				raise AssertionError("Offset scans must not walk characters")
		class OffsetBuffer(Buffer):
			def makeTextInfo(self, position):
				if position == "all": return OffsetInfo(self.text)
				return OffsetInfo(self.text, position[0], position[1])
		namespace["textInfos"].offsets.Offsets = lambda start, end: (start, end)
		bounded = namespace["_conversationScanInfo"](OffsetBuffer(longText))
		self.assertEqual(("H" * 32768, None, "T" * 32768), tuple(bounded.getTextWithFields()))
		self.assertEqual(("short document",), tuple(
			namespace["_conversationScanInfo"](OffsetBuffer("short document")).getTextWithFields(),
		))
		info = OffsetInfo(longText, 40000, 40000)
		self.assertEqual(-32768, namespace["_extendScanStart"](info, 32768))
		self.assertEqual((7232, 40000), (info.start, info.end))
		self.assertEqual(-7232, namespace["_extendScanStart"](info, 32768))
		self.assertEqual((0, 40000), (info.start, info.end))
		class WebUIAInfo(TextInfo, UIATextInfo):
			def copy(self): return WebUIAInfo(self.text, self.start, self.end)
			def move(self, *args, **kwargs):
				raise AssertionError("Never use web UIA character-walking override")
		class UIABuffer(Buffer):
			def makeTextInfo(self, position): return WebUIAInfo(self.text)
		class ProxyBuffer(Buffer):
			def makeTextInfo(self, position): return RootProxyTextInfo(WebUIAInfo(self.text))
		bounded = namespace["_conversationScanInfo"](ProxyBuffer(longText))
		self.assertEqual(("H" * 32768, None, "T" * 32768), tuple(bounded.getTextWithFields()))
		self.assertEqual([(32768, "end"), (-32768, "start")], bulkMoves)
		bulkMoves.clear()
		proxy = RootProxyTextInfo(WebUIAInfo(longText, 40000, 40000))
		self.assertEqual(-32768, namespace["_extendScanStart"](proxy, 32768))
		self.assertEqual((7232, 40000), (proxy.innerTextInfo.start, proxy.innerTextInfo.end))
		cycle = RootProxyTextInfo(None)
		cycle.innerTextInfo = cycle
		with self.assertRaises(NotImplementedError): namespace["_scanProviderInfo"](cycle)
		bulkMoves.clear()
		bounded = namespace["_conversationScanInfo"](UIABuffer(longText))
		self.assertEqual([(32768, "end"), (-32768, "start")], bulkMoves)
		self.assertEqual(("H" * 32768, None, "T" * 32768), tuple(bounded.getTextWithFields()))
		bulkMoves.clear()
		short = namespace["_conversationScanInfo"](UIABuffer("short document"))
		self.assertEqual(("short document",), tuple(short.getTextWithFields()))
		self.assertEqual(2, len(bulkMoves))
		info = WebUIAInfo(longText, 40000, 40000)
		self.assertEqual(-32768, namespace["_extendScanStart"](info, 32768))
		self.assertEqual((7232, 40000), (info.start, info.end))
		self.assertEqual(-7232, namespace["_extendScanStart"](info, 32768))
		self.assertEqual((0, 40000), (info.start, info.end))

	def test_pending_response_completion_suppresses_even_forced_working_ticks(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(node for node in pluginTree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin")
		for name in ("_retryDirectChatAction", "_focusUnarchiveButton"):
			method = next(node for node in pluginClass.body if isinstance(node, ast.FunctionDef) and node.name == name)
			namespace = {}
			exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
			subject = type("Subject", (), {
				"_pendingDirectChatAction": ("title", "archive", "codex", 0),
				"_conversationWindowHandle": 123,
				"_conversationWindowOwnsForeground": lambda self, handle: False,
			})()
			namespace[name](subject)
			if name == "_retryDirectChatAction": self.assertIsNone(subject._pendingDirectChatAction)
			else: self.assertEqual(0, subject._unarchiveFocusAttempts)
		method = next(node for node in pluginClass.body if isinstance(node, ast.FunctionDef) and node.name == "_retryDirectChatAction")
		namespace = {}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		subject = type("Subject", (), {
			"_pendingDirectChatAction": ("title", "archive", "codex", 0),
			"_conversationWindowHandle": 222,
			"_pendingDirectChatActionWindowHandle": 111,
		})()
		namespace["_retryDirectChatAction"](subject)
		self.assertIsNone(subject._pendingDirectChatAction)
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(node for node in pluginTree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin")
		method = next(node for node in pluginClass.body if isinstance(node, ast.FunctionDef) and node.name == "_announceContinuousWorkingClick")
		namespace = {}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		# No settings, clock, or audio dependencies: pending completion must return
		# before consulting any of them, including a forced submission tick.
		subject = type("Subject", (), {"_pendingResponseCompletionAt": 123.0})()
		self.assertIsNone(namespace["_announceContinuousWorkingClick"](subject))
		self.assertIsNone(namespace["_announceContinuousWorkingClick"](subject, force=True))

	def test_package_audit_checks_current_source_bytes(self):
		auditSource = AUDIT_PATH.read_text(encoding="utf-8")
		self.assertIn("archive.read(archiveName) == packageData(path)", auditSource)

	def test_new_task_and_buffer_discard_old_prompt_anchor(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		for methodName in ("_resetTaskState", "_rememberBuffer"):
			method = next(
				node for node in pluginClass.body
				if isinstance(node, ast.FunctionDef) and node.name == methodName
			)
			clearsPrompt = any(
				isinstance(node, ast.Assign)
				and any(
					isinstance(target, ast.Attribute)
					and isinstance(target.value, ast.Name)
					and target.value.id == "self"
					and target.attr == "_lastPromptObject"
					for target in node.targets
				)
				and isinstance(node.value, ast.Constant)
				and node.value.value is None
				for node in ast.walk(method)
			)
			self.assertTrue(clearsPrompt, methodName)

	def test_focus_buffer_candidates_reuse_nvda_ancestors_without_parent_queries(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(node for node in pluginTree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin")
		method = next(node for node in pluginClass.body if isinstance(node, ast.FunctionDef) and node.name == "_bufferCandidates")
		class Focus:
			@property
			def parent(self): raise AssertionError("focused ancestry was queried again")
		focus, document, window = Focus(), object(), object()
		namespace = {"api": type("Api", (), {
			"getFocusObject": staticmethod(lambda: focus),
			"getFocusAncestors": staticmethod(lambda: [window, document, document]),
		})}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		self.assertEqual([focus, document, window], list(namespace["_bufferCandidates"](object(), focus)))
		background = type("Background", (), {"parent": None})()
		self.assertEqual([background], list(namespace["_bufferCandidates"](object(), background)))
		background.parent = background
		self.assertEqual([background], list(namespace["_bufferCandidates"](object(), background)))

	def test_retained_verified_buffer_avoids_mode_and_browser_ancestry_queries(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(node for node in pluginTree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin")
		method = next(node for node in pluginClass.body if isinstance(node, ast.FunctionDef) and node.name == "_rememberBuffer")
		def expensiveQuery(obj):
			raise AssertionError("retained buffer performed redundant accessibility queries")
		namespace = {
			"_isChatGPTObject": lambda obj: True,
			"_isNativeCommonDialogObject": lambda obj: False,
			"_switchControlMode": expensiveQuery,
			"_conversationModeForObject": expensiveQuery,
			"_isCodexPromptObject": expensiveQuery,
			"_isEmbeddedBrowserObject": expensiveQuery,
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		buffer = object()
		control = type("Control", (), {"treeInterceptor": buffer})()
		unbuffered = type("Unbuffered", (), {"treeInterceptor": None})()
		class Subject:
			_buffer = buffer
			_conversationModeObserved = True
			_conversationWindowHandle = 1234
			available = True
			def _bufferCandidates(self, obj): return (unbuffered, control)
			def _conversationWindowIsAvailable(self, handle):
				assert handle == 1234
				return self.available
		subject = Subject()
		self.assertTrue(namespace["_rememberBuffer"](subject, control))
		subject.available = False
		self.assertFalse(namespace["_rememberBuffer"](subject, control))

	def test_no_function_shadows_the_translation_function(self):
		# A loop such as "for _ in range(7)" makes _ a local integer for the whole
		# function, so a later _("...") call raises TypeError at runtime.
		sources = sorted(CORE_PATH.parent.glob("*.py")) + [CHATGPT_APP_MODULE_PATH]
		offenders = []
		for path in sources:
			tree = ast.parse(path.read_text(encoding="utf-8"))
			for node in ast.walk(tree):
				if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
					continue
				assigns = any(
					isinstance(child, ast.Name) and child.id == "_" and isinstance(child.ctx, ast.Store)
					for child in ast.walk(node)
				)
				calls = any(
					isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == "_"
					for child in ast.walk(node)
				)
				if assigns and calls:
					offenders.append(f"{path.name}:{node.name}")
		self.assertEqual([], offenders)

	def test_plugin_install_progress_announces_with_translated_text(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_announcePluginInstallProgress"
		)
		namespace = {
			"Role": type("Role", (), {"PROGRESSBAR": "progressbar"}),
			"_isChatGPTObject": lambda obj: True,
			"pluginInstallProgress": core.pluginInstallProgress,
			"pluginProgressBusyTransition": core.pluginProgressBusyTransition,
			"_": lambda text: text,
			"log": type("Log", (), {
				"info": staticmethod(lambda *args, **kwargs: None),
				"debugWarning": staticmethod(lambda *args, **kwargs: None),
			}),
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			_busy = False
			def __init__(self):
				self._pluginProgressBuckets = {}
				self._pluginProgressOwnedBusy = set()
				self.spoken = []
			def _setBusy(self, busy, reason): self._busy = busy
			def _speakOnce(self, message, *args, **kwargs): self.spoken.append(message)
		progress = type("Progress", (), {
			"role": "progressbar", "name": "Installing GitHub plugin", "value": "40%",
			"description": "", "parent": None,
		})()
		subject = Subject()
		self.assertTrue(namespace["_announcePluginInstallProgress"](subject, progress))
		self.assertEqual(["Plugin installation 40 percent"], subject.spoken)

	def test_message_list_dialog_destroys_itself_when_closed(self):
		tree = ast.parse((PLUGIN_PATH.parent / "messageListDialog.py").read_text(encoding="utf-8"))
		dialogClass = next(node for node in tree.body if isinstance(node, ast.ClassDef))
		closeMethod = next(
			node for node in dialogClass.body if isinstance(node, ast.FunctionDef) and node.name == "_close"
		)
		calledAttributes = {
			node.func.attr for node in ast.walk(closeMethod)
			if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
		}
		self.assertIn("Destroy", calledAttributes)
		self.assertNotIn("Skip", calledAttributes)

	def test_long_conversation_tail_merges_with_cached_turns(self):
		cached = (("user", "A"), ("assistant", "B"), ("user", "C"))
		tail = (("assistant", "partial B"), ("assistant", "B"), ("user", "C"), ("assistant", "D"))
		self.assertEqual(cached + (("assistant", "D"),), core.mergeConversationTail(cached, tail))
		# The first tail turn may be cut off, so it is never kept on its own.
		self.assertEqual(cached, core.mergeConversationTail(cached, (("assistant", "partial"),)))
		self.assertEqual((("user", "C"),), core.mergeConversationTail((), (("assistant", "partial"), ("user", "C"))))
		# A tail that does not line up with the cache replaces it.
		self.assertEqual(
			(("user", "X"), ("assistant", "Y")),
			core.mergeConversationTail(cached, (("user", "partial"), ("user", "X"), ("assistant", "Y"))),
		)

	def test_split_scans_feed_the_message_list_in_long_conversations(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef)
			and node.name in ("_splitScanConversationMessages", "_currentConversationMessageList")
		]
		namespace = {
			"MESSAGE_LIST_LIMIT": 100,
			"mergeConversationTail": core.mergeConversationTail,
			"log": type("Log", (), {"debugWarning": staticmethod(lambda *args, **kwargs: None)}),
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		fullScan = tuple(("assistant", f"response {index}") for index in range(40))
		class Subject:
			_buffer = object()
			_messageListDialog = None
			_messageListRefreshPending = False
			def __init__(self):
				self._recentChatMessagesBuffer = self._buffer
				self._conversationMessages = ()
				self.fullScans = []
			def _activeBranchMessages(self, limit):
				self.fullScans.append(limit)
				return fullScan
		for name in ("_splitScanConversationMessages", "_currentConversationMessageList"):
			setattr(Subject, name, namespace[name])
		tail = (("assistant", "partial"), ("user", "newest"))
		background = Subject()
		self.assertEqual((("user", "newest"),), background._splitScanConversationMessages(tail))
		self.assertEqual([], background.fullScans)
		refresh = Subject()
		refresh._messageListRefreshPending = True
		self.assertEqual(fullScan, refresh._splitScanConversationMessages(tail))
		self.assertEqual([100], refresh.fullScans)
		emptyDialog = Subject()
		emptyDialog._messageListDialog = object()
		self.assertEqual(fullScan, emptyDialog._splitScanConversationMessages(tail))
		pluginSource = PLUGIN_PATH.read_text(encoding="utf-8")
		self.assertNotIn("messageCollector.promptReached and not isinstance(info, _SplitConversationScanInfo)", pluginSource)

	def test_short_messages_matching_interface_labels_are_kept(self):
		tokens = (
			("speaker", "user"), ("text", "Stop"),
			("speaker", "assistant"), ("text", "OK, stopping."), ("text", "Copy"), ("text", "Good response"),
			("speaker", "user"), ("text", "Retry"),
			("speaker", "assistant"), ("text", "Thinking"), ("text", "Retrying now."),
			("speaker", "user"), ("text", "10:30"), ("end", ""),
		)
		self.assertEqual(
			(
				("user", "Stop"), ("assistant", "OK, stopping."), ("user", "Retry"),
				("assistant", "Retrying now."), ("user", "10:30"),
			),
			chatMessagesFromTokens(tokens),
		)
		# Two interface labels in a row are still chrome, not a message.
		self.assertEqual((), chatMessagesFromTokens((
			("speaker", "assistant"), ("text", "Copy"), ("text", "Retry"), ("text", "stray"),
		)))

	def test_usage_limit_retry_time_keeps_decimals_and_clock_suffixes(self):
		self.assertEqual(
			"Usage limit reached. You can try again in 2.5 hours.",
			core.usageLimitNotice("You've hit your usage limit. Try again in 2.5 hours."),
		)
		self.assertEqual(
			"Usage limit reached. You can upgrade to Pro or try again at 3:45 p.m.",
			core.usageLimitNotice("You've hit your usage limit. Upgrade to Pro. Try again at 3:45 p.m. Thanks."),
		)
		self.assertEqual(
			"Usage limit reached. You can try again at 9 a.m.",
			core.usageLimitNotice("You've hit your usage limit. Your limit resets at 9 a.m."),
		)

	def test_archived_threads_match_index_ids_case_insensitively(self):
		threadId = "0123abcd-4567-89ab-cdef-0123456789ab"
		with tempfile.TemporaryDirectory() as tempDir:
			root = Path(tempDir)
			(root / "archived_sessions").mkdir()
			(root / "archived_sessions" / f"rollout-{threadId}.jsonl").write_text("", encoding="utf-8")
			(root / "session_index.jsonl").write_text(
				json.dumps({"id": threadId.upper(), "thread_name": "Release prep"}) + "\n", encoding="utf-8",
			)
			self.assertEqual(((threadId, "Release prep"),), loadArchivedThreads(root))

	def test_activity_summary_and_verbosity_toggle_are_translatable(self):
		translated = []
		def translate(text):
			translated.append(text)
			return text
		self.assertEqual("Codex is idle", currentActivitySummary(False, "other", "", 0, translate))
		self.assertEqual(
			"Codex is still running commands, 5 seconds",
			currentActivitySummary(True, "command", "", 5, translate),
		)
		self.assertIn("{agent} is idle", translated)
		self.assertIn("{agent} is still {activity}, {duration}", translated)
		self.assertIn("running commands", translated)
		pluginSource = PLUGIN_PATH.read_text(encoding="utf-8")
		self.assertIn('modeName = _("Minimal") if conf["verbosity"] == "minimal" else _("Full")', pluginSource)

	def test_permission_dialog_focus_prefers_deny_over_allow(self):
		pluginSource = PLUGIN_PATH.read_text(encoding="utf-8")
		self.assertIn('word in str(getattr(obj, "name", "") or "").casefold() for word in ("deny", "reject")', pluginSource)
		names = ["Allow once", "Deny", "Always allow"]
		names.sort(key=lambda name: not any(word in name.casefold() for word in ("deny", "reject")))
		self.assertEqual("Deny", names[0])

	def test_zero_error_counts_are_not_failures(self):
		for label in ("Tests passed: 0 errors", "Build finished with no errors", "Tests passed, zero failures"):
			with self.subTest(label=label):
				self.assertFalse(core.isFailureText(label))
				self.assertEqual("completion", core.soundKey("completion", label))
				self.assertNotEqual("urgent", core.announcementPriority("completion", label))
		for label in ("Tests failed: 2 errors", "Command failed", "Cancelled", "Build error"):
			with self.subTest(label=label):
				self.assertTrue(core.isFailureText(label))
				self.assertEqual("failure", core.soundKey("completion", label))
				self.assertEqual("urgent", core.announcementPriority("completion", label))

	def test_completion_words_must_be_whole_words(self):
		for label in ("Random seed", "Ranked results", "Built-in tools", "Doneness", "Ready", "Readme"):
			with self.subTest(label=label):
				self.assertEqual("", statusDetails(label)[0])
				self.assertEqual("", core.intermediateCompletionCategory(label))
				self.assertFalse(core.isTaskCompletionLabel(label))
		self.assertEqual(("completion", "Command finished"), statusDetails("Ran npm test"))
		self.assertEqual(("completion", "Generation finished"), statusDetails("Built package"))
		self.assertEqual("file", core.intermediateCompletionCategory("Read README.md"))
		self.assertTrue(core.isTaskCompletionLabel("Done."))

	def test_elapsed_seconds_include_hours_and_minutes(self):
		self.assertEqual(90, elapsedSeconds("Working for 1m 30s"))
		self.assertEqual(3725, elapsedSeconds("Running tests for 1h 2m 5s"))
		self.assertEqual(123, elapsedSeconds("for 2 minutes 3 seconds"))
		self.assertEqual(45, elapsedSeconds("Thinking for 45s"))
		self.assertIsNone(elapsedSeconds("Ran 3 steps"))

	def test_indirectly_translated_status_wording_reaches_the_template(self):
		template = TRANSLATION_TEMPLATE_PATH.read_text(encoding="utf-8")
		tree = ast.parse(CORE_PATH.read_text(encoding="utf-8"))
		functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
		dynamic = set()
		for node in ast.walk(functions["statusDetails"]):
			if isinstance(node, ast.Return) and isinstance(node.value, ast.Tuple):
				message = node.value.elts[1]
				if isinstance(message, ast.Constant) and message.value:
					dynamic.add(message.value)
				elif isinstance(message, ast.IfExp):
					dynamic.update(part.value for part in (message.body, message.orelse))
		for node in ast.walk(functions["minimalProfileMessage"]):
			if isinstance(node, ast.Assign) and any(
				isinstance(target, ast.Name) and target.id == "balanced" for target in node.targets
			):
				dynamic.update(
					child.value for child in ast.walk(node.value)
					if isinstance(child, ast.Constant) and isinstance(child.value, str) and child.value[:1].isupper()
				)
		for node in ast.walk(functions["backgroundActivityName"]):
			if isinstance(node, ast.Return):
				dynamic.update(
					child.value for child in ast.walk(node.value)
					if isinstance(child, ast.Constant) and isinstance(child.value, str) and child.value[:1].isupper()
				)
		self.assertGreater(len(dynamic), 30)
		missing = sorted(message for message in dynamic if f"msgid {json.dumps(message)}" not in template)
		self.assertEqual([], missing)
		for message in ("{count} hour", "{count} minutes", "Read the most recent ChatGPT message"):
			self.assertIn(f"msgid {json.dumps(message)}", template)

	def test_app_module_commands_report_handler_failures(self):
		source = CHATGPT_APP_MODULE_PATH.read_text(encoding="utf-8")
		tree = ast.parse(source)
		method = next(
			node for node in ast.walk(tree)
			if isinstance(node, ast.FunctionDef) and node.name == "_runToolkitCommand"
		)
		self.assertTrue(any(isinstance(node, ast.Try) for node in ast.walk(method)))
		self.assertIn("from logHandler import log", source)

	def test_settings_save_never_closes_an_already_destroyed_message_list(self):
		pluginSource = PLUGIN_PATH.read_text(encoding="utf-8")
		self.assertNotIn("wx.CallAfter(dialog.Close)", pluginSource)
		self.assertIn("if plugin._messageListDialog is dialog:", pluginSource)

	def test_chat_history_refresh_requests_a_sidebar_rescan(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_refreshChatHistoryData"
		)
		namespace = {}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			_conversationMode = "codex"
			_bufferDirty = False
			def __init__(self): self.polls = []
			def _loadArchivedChatHistory(self, mode): return ("Old task",), True
			def _chatHistoryTitles(self, mode): return ("Recent task",)
			def _schedulePoll(self, **kwargs): self.polls.append(kwargs)
		subject = Subject()
		self.assertEqual(
			(("Recent task",), ("Old task",), True),
			namespace["_refreshChatHistoryData"](subject, "codex"),
		)
		self.assertTrue(subject._bufferDirty)
		self.assertEqual([{"delay": 50, "requestInspection": True}], subject.polls)
		self.assertEqual(((), (), False), namespace["_refreshChatHistoryData"](subject, "chatgpt"))

	def test_attachment_diagnostic_summary_hides_chat_text(self):
		elements = (
			("listitem", "Private chat title", "listitem", "", False),
			("menu", "", "menu", "radix-menu", False),
			("menuitem", "Upload files", "menuitem", "", False),
			("menuitem", "Token=abc123 secret", "menuitem", "", True),
		)
		lines = core.attachmentDiagnosticLines(elements)
		text = "\n".join(lines)
		self.assertIn("UIA candidate counts: listitem 1, menu 1, menuitem 2", text)
		self.assertIn("menuitem: Upload files", text)
		self.assertNotIn("Private chat title", text)
		self.assertNotIn("abc123", text)
		self.assertIn("offscreen", text)
		baselineLines = core.attachmentDiagnosticLines(elements, baseline=elements[:1])
		self.assertIn("New since Add files and more was focused: 3", baselineLines[1])
		self.assertNotIn("Private chat title", "\n".join(baselineLines))
		self.assertIn("UIA candidate counts: none", core.attachmentDiagnosticLines(())[0])

	def test_attachment_diagnostics_stay_bounded_and_off_the_main_thread(self):
		source = (CORE_PATH.parent / "attachmentDiagnostics.py").read_text(encoding="utf-8")
		self.assertIn("handler.MTAThreadQueue.put_nowait(probe)", source)
		self.assertNotIn("GetRootElement", source)
		self.assertIn("for window in windows[:MAX_PROCESS_WINDOWS]:", source)
		self.assertIn("MAX_UIA_ELEMENTS - len(elements)", source)
		self.assertIn("FindAllBuildCache", source)
		pluginSource = PLUGIN_PATH.read_text(encoding="utf-8")
		self.assertIn("def script_captureAttachmentMenuDiagnostics", pluginSource)
		self.assertIn('_("Attachment menu diagnostics:")', pluginSource)
		self.assertIn('self._attachmentDiagnostics.noteButtonActivated(obj, "expanded event")', pluginSource)

	def test_add_files_popup_returns_to_browse_mode_after_focus_settles_in_prompt(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in (
				"_moveBrowseCaretToAttachmentPopup", "_focusAttachmentSourceMenu",
			)
		]
		events = []
		class Anchor:
			def updateCaret(self): events.append("caret")
			def copy(self): return self
			def expand(self, unit): events.append(("expand", unit))
		class Buffer:
			passThrough = True
		focus = {"value": "button"}
		timers = []
		namespace = {
			"textInfos": type("TextInfos", (), {"UNIT_LINE": "line"}),
			"OutputReason": type("OutputReason", (), {"CARET": "caret"}),
			"State": type("State", (), {"COLLAPSED": "collapsed"}),
			"_isChatGPTObject": lambda obj: True,
			"_isCodexPromptObject": lambda obj: obj == "prompt",
			"_isVirtualBufferDocument": lambda buffer: True,
			"api": type("Api", (), {"getFocusObject": staticmethod(lambda: focus["value"])}),
			"speech": type("Speech", (), {"speakTextInfo": staticmethod(lambda info, **kwargs: events.append("spoken"))}),
			"braille": type("Braille", (), {"handler": type("Handler", (), {
				"handleCaretMove": staticmethod(lambda buffer: events.append("braille")),
			})()}),
			"wx": type("Wx", (), {"CallLater": staticmethod(lambda delay, *args: timers.append(args) or object())}),
			"ATTACHMENT_POPUP_RETRIES": 10,
			"ATTACHMENT_POPUP_RETRY_MILLISECONDS": 150,
			"ATTACHMENT_POPUP_SETTLE_ATTEMPTS": 4,
			"log": type("Log", (), {
				"debug": staticmethod(lambda *args, **kwargs: None),
				"debugWarning": staticmethod(lambda *args, **kwargs: None),
				"info": staticmethod(lambda *args, **kwargs: None),
			}),
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		buffer = Buffer()
		class Subject:
			_conversationWindowHandle = 10
			def __init__(self):
				self._buffer = buffer
				self._attachmentSourceFocusTimer = None
				self.sourcesChecked = False
			def _conversationWindowIsAvailable(self, handle): return True
			def _conversationWindowOwnsForeground(self, handle): return True
			def _isAddFilesButton(self, obj): return obj == "button"
			def _attachmentPopupAnchor(self, buffer): return Anchor()
			def _readAttachmentPopupOptions(self, buffer): return ()
			def _attachmentSourceMenuObject(self, buffer):
				self.sourcesChecked = True
				return None
		for method in methods:
			setattr(Subject, method.name, namespace[method.name])
		button = type("Button", (), {"states": ("expanded",)})()
		subject = Subject()
		# Focus is still on the button: wait for ChatGPT to return focus to the prompt.
		subject._focusAttachmentSourceMenu(button, buffer, 10)
		self.assertEqual([], events)
		self.assertEqual(1, timers[-1][-1])
		self.assertFalse(subject.sourcesChecked)
		focus["value"] = "prompt"
		subject._focusAttachmentSourceMenu(button, buffer, 10, 1)
		self.assertFalse(buffer.passThrough)
		self.assertEqual(["caret", ("expand", "line"), "spoken", "braille"], events)
		# If focus never reaches the prompt, the browse cursor still moves after settling.
		events.clear()
		buffer.passThrough = False
		focus["value"] = "button"
		subject._focusAttachmentSourceMenu(button, buffer, 10, 4)
		self.assertIn("caret", events)

	def test_add_files_rows_use_chatgpt_row_classes_including_non_button_rows(self):
		classKey = core.ATTACHMENT_POPUP_CLASS_KEY
		row = "text-default focus:bg-primary-ghost-hover min-h-[var(--app-menu-item-height,0px)] menu-row-opacity"
		highlighted = "text-default focus:bg-primary-ghost-hover min-h-[var(--app-menu-item-height,0px)] bg-primary-ghost-hover opacity-100"
		appshot = "flex min-h-[var(--app-menu-item-height,0px)] items-center"
		header = "text-codex-description h-[var(--suggestion-menu-header-height,auto)]"
		def start(role, className=None, **field):
			if className is not None:
				field[classKey] = className
			return ("start", dict(field, role=role))
		end = ("end", None)
		def text(value): return ("text", value)
		tokens = [
			start("edit", name="Work with Codex"), end,
			start("section", "_suggestionMenu_14z1j_2"), start("section", "vertical-scroll-fade-mask"),
			start("section", header), text("Add"), end,
			start("button", highlighted), text("Files and folders"), end,
			# Not a button, but ChatGPT's keyboard still stops on this row.
			start("section", appshot), text("Attach appshot"), end,
			start("button", row), text("GoalSet a goal to keep pursuing"), end,
			start("section", header), text("Plugins"), end,
			start("button", row), text("GitHubTriage PRs, issues, CI, and publish flows"), end,
			start("section", "status"), text("Loading sites…"), end,
			end,
			start("section", "px-row-x"), text("Type to search files or chats"), end,
			end,
		]
		options = core.attachmentPopupOptions(
			tokens,
			lambda field: field.get("role") == "edit" and isCodexPromptLabel(field.get("name", "")),
			lambda field: field.get("role") == "button",
		)
		self.assertEqual(
			["Files and folders", "Attach appshot", "Goal", "GitHub"], [option["title"] for option in options],
		)
		self.assertEqual(["Add", "Add", "Add", "Plugins"], [option["section"] for option in options])
		self.assertEqual([True, False, False, False], [option["highlighted"] for option in options])
		self.assertEqual("downArrow", core.attachmentOptionKeyStep(options, options[2]))
		self.assertEqual("tab", core.attachmentOptionKeyStep(options, options[0]))
		moved = [dict(option, highlighted=index == 3) for index, option in enumerate(options)]
		self.assertEqual("upArrow", core.attachmentOptionKeyStep(moved, options[2]))
		unknown = [dict(option, highlighted=False) for option in options]
		self.assertEqual("", core.attachmentOptionKeyStep(unknown, options[2]))
		self.assertEqual("", core.attachmentOptionKeyStep(options, {"title": "Missing", "section": "Add"}))
		# A tester's chat mode, with the prompt "Ask ChatGPT", has no "Type to
		# search" text; the popup is found from its last row instead.
		withoutHint = [start("edit", name="Ask ChatGPT"), end] + tokens[2:-4] + [end]
		self.assertEqual(
			[(option["title"], option["section"]) for option in options],
			[(option["title"], option["section"]) for option in core.attachmentPopupOptions(
				withoutHint,
				lambda field: field.get("role") == "edit" and isCodexPromptLabel(field.get("name", "")),
				lambda field: field.get("role") == "button",
			)],
		)
		self.assertEqual((), core.attachmentPopupOptions(
			[start("edit", name="Ask ChatGPT"), end, start("button"), text("Send"), end],
			lambda field: True, lambda field: True,
		))
		isPrompt = lambda field: field.get("role") == "edit" and isCodexPromptLabel(field.get("name", ""))
		self.assertEqual(
			"section x4, section[header] x2, button[row,highlighted] x1, section[row] x1, button[row] x2",
			core.attachmentPopupStructureSummary(tokens, isPrompt),
		)
		self.assertEqual("prompt not found", core.attachmentPopupStructureSummary(tokens[2:], isPrompt))
		self.assertEqual("no controls after the prompt", core.attachmentPopupStructureSummary(tokens[:2], isPrompt))
		self.assertNotIn("Files", core.attachmentPopupStructureSummary(tokens, isPrompt))

	def test_option_highlight_is_stepped_until_the_chosen_row_then_tab(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_stepToAttachmentOption"
		)
		keys, later, spoken = [], [], []
		focus = {"value": "prompt"}
		titles = ["Files and folders", "Attach appshot", "Goal", "Plan mode"]
		state = {"highlight": 0}
		class Gesture:
			@staticmethod
			def fromName(name):
				def send(self):
					keys.append(name)
					if name == "downArrow":
						state["highlight"] += 1
				return type("Key", (), {"send": send})()
		namespace = {
			"api": type("Api", (), {"getFocusObject": staticmethod(lambda: focus["value"])}),
			"_isCodexPromptObject": lambda obj: obj == "prompt",
			"keyboardHandler": type("Keyboard", (), {"KeyboardInputGesture": Gesture}),
			"wx": type("Wx", (), {"CallLater": staticmethod(lambda delay, *args: later.append(args))}),
			"ui": type("Ui", (), {"message": staticmethod(spoken.append)}),
			"attachmentOptionKeyStep": core.attachmentOptionKeyStep,
			"ATTACHMENT_OPTION_CONFIRM_MILLISECONDS": 600,
			"ATTACHMENT_OPTION_HIGHLIGHT_MILLISECONDS": 80,
			"ATTACHMENT_OPTION_HIGHLIGHT_WAITS": 25,
			"ATTACHMENT_OPTION_EXTRA_STEPS": 5,
			"_": lambda text: text,
			"log": type("Log", (), {"info": staticmethod(lambda *args, **kwargs: None)}),
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		class Subject:
			_attachmentMenuWindowHandle = 10
			_buffer = "buffer"
			def _conversationWindowOwnsForeground(self, handle): return True
			def _readAttachmentPopupOptions(self, buffer):
				return tuple(
					{"title": title, "section": "Add", "highlighted": index == state["highlight"]}
					for index, title in enumerate(titles)
				)
			def _confirmAttachmentChoice(self, option): pass
			def _promptTextForAnnouncement(self): return ""
		Subject._stepToAttachmentOption = namespace["_stepToAttachmentOption"]
		subject = Subject()
		subject._stepToAttachmentOption({"title": "Goal", "section": "Add"}, 0)
		while later:
			callback, *args = later.pop(0)
			callback(*args)
		self.assertEqual(["downArrow", "downArrow", "tab"], keys)
		self.assertEqual([], spoken)
		# NVDA's copy of the page can show the old highlight for a few reads after a
		# key. The add-on must wait for it to move rather than press Down again.
		keys.clear()
		state["highlight"] = 0
		delayed = {"lagReads": 0}
		originalRead = Subject._readAttachmentPopupOptions
		def laggingRead(self, buffer):
			if keys and keys[-1] == "downArrow" and delayed["lagReads"] < 3:
				delayed["lagReads"] += 1
				return tuple(
					{"title": title, "section": "Add", "highlighted": index == state["highlight"] - 1}
					for index, title in enumerate(titles)
				)
			delayed["lagReads"] = 0 if not keys or keys[-1] != "downArrow" else delayed["lagReads"]
			return originalRead(self, buffer)
		Subject._readAttachmentPopupOptions = laggingRead
		subject._stepToAttachmentOption({"title": "Goal", "section": "Add"}, 0)
		while later:
			callback, *args = later.pop(0)
			callback(*args)
		self.assertEqual(["downArrow", "downArrow", "tab"], keys)
		Subject._readAttachmentPopupOptions = originalRead
		# Focus leaving the prompt stops before any key is sent.
		keys.clear()
		state["highlight"] = 0
		focus["value"] = "elsewhere"
		subject._stepToAttachmentOption({"title": "Goal", "section": "Add"}, 0)
		self.assertEqual([], keys)
		self.assertIn("could not be chosen", spoken[-1])

	def test_chosen_option_is_found_again_when_its_text_or_spacing_changes(self):
		first = [
			{"title": "Files and folders", "description": "", "section": "Add", "sectionIndex": 0, "index": 0},
			{"title": "Attach The Chat Place, a home for your Claude Code chats", "description": "", "section": "Add", "sectionIndex": 1, "index": 1},
			{"title": "Code Review", "description": "Review and manage GitHub pull requests", "section": "Plugins", "sectionIndex": 0, "index": 2},
		]
		later = [
			{"title": "Files and folders", "description": "", "section": "Add", "sectionIndex": 0},
			{"title": "Attach appshot", "description": "", "section": "Add", "sectionIndex": 1},
			{"title": "Code Review Review and manage GitHub pull requests", "description": "", "section": "Plugins", "sectionIndex": 0},
		]
		# Same row, different spacing between title and description.
		self.assertEqual(2, core.findAttachmentOption(later, first[2]))
		# The appshot row renamed itself; its position in the section still matches.
		self.assertEqual(1, core.findAttachmentOption(later, first[1]))
		self.assertIsNone(core.findAttachmentOption(later, {"title": "Gone", "section": "Apps"}))

	def test_chosen_option_announcement_uses_the_prompt_tag_it_added(self):
		self.assertEqual("Code Review", core.promptTextAddition("", "Code Review"))
		self.assertEqual("GitHub", core.promptTextAddition("Please review", "Please review GitHub"))
		self.assertEqual("", core.promptTextAddition("same", "same"))
		self.assertEqual("", core.promptTextAddition("draft text", "something else"))
		self.assertEqual("", core.promptTextAddition("", "x" * 80))

	def test_run_together_option_titles_are_split_from_descriptions(self):
		cases = {
			"GitHubTriage PRs, issues, CI, and publish flows": ("GitHub", "Triage PRs, issues, CI, and publish flows"),
			"PDFRead, create, and verify PDFs": ("PDF", "Read, create, and verify PDFs"),
			"Plan modeTurn plan mode on": ("Plan mode", "Turn plan mode on"),
			"Work in a projectStart a chat in a project": ("Work in a project", "Start a chat in a project"),
			"Wyndham Hotels & ResortsBook thousands of hotels": ("Wyndham Hotels & Resorts", "Book thousands of hotels"),
			"Code ReviewReview and manage GitHub pull requests": ("Code Review", "Review and manage GitHub pull requests"),
			"Files and folders": ("Files and folders", ""),
			"LinkedIn": ("LinkedIn", ""),
			"AI Money Making OptionsChatGPT conversation": ("AI Money Making Options", "ChatGPT conversation"),
			"AirPlay During Calls ChatGPT conversation": ("AirPlay During Calls", "ChatGPT conversation"),
			"Code Review Review and manage GitHub pull requests": ("Code Review Review and manage GitHub pull requests", ""),
			"Crossroadscrossroads-audio-city.example.chatgpt.site": ("Crossroads", "crossroads-audio-city.example.chatgpt.site"),
		}
		for text, expected in cases.items():
			self.assertEqual(expected, core.splitRunTogetherTitle(text), text)

	def test_add_files_popup_options_are_read_by_section_without_toolbar_controls(self):
		def start(**field): return ("start", field)
		end = ("end", None)
		def text(value): return ("text", value)
		tokens = [
			start(role="document"), text("Earlier conversation text"),
			start(role="form"), start(role="edit", name="Work with Codex"), end,
			start(role="button", name="Add files and more"), end, end,
			start(role="dialog"),
			start(role="section"), text("Add"), end,
			start(role="button", name="", id=1), text("Files and folders"), end,
			start(role="button", name="", id=2), text("Goal"), text("Set a goal to keep pursuing"), end,
			start(role="section"), text("Apps"), end,
			start(role="button", name="", id=3), text("Hotline"), text("Look up local helpline "), text("information for the user"), end,
			start(role="section"), text("Files and chats"), end,
			start(role="section"), text("Type to search files or chats"), end,
			end, end,
		]
		options = core.attachmentPopupOptions(
			tokens,
			lambda field: field.get("role") == "edit" and isCodexPromptLabel(field.get("name", "")),
			lambda field: field.get("role") == "button",
		)
		self.assertEqual(["Files and folders", "Goal", "Hotline"], [option["title"] for option in options])
		self.assertEqual(["Add", "Add", "Apps"], [option["section"] for option in options])
		self.assertEqual("Look up local helpline information for the user", options[2]["description"])
		self.assertEqual(3, options[2]["field"]["id"])
		self.assertEqual(
			"Goal — Set a goal to keep pursuing (Add)", core.attachmentOptionLabel(options[1]),
		)
		self.assertEqual((), core.attachmentPopupOptions(tokens[:8], lambda field: False, lambda field: True))
		self.assertFalse(options[0]["classBased"])

	def test_add_files_popup_options_read_from_ui_automation_rows(self):
		row = "flex app-menu-item-height rounded"
		rows = [
			("suggestion-menu-header px-2", "Add", []),
			(row + " bg-primary-ghost-hover", "", ["Files and folders"]),
			("flex text-sm", "Attach appshot", []),
			(row, "", ["Goal", "Set a goal to keep pursuing"]),
			("suggestion-menu-header", "", ["Apps"]),
			(row, "", ["Hotline", "Look up local helpline"]),
			(row, "Type to search files or chats", []),
		]
		options = core.attachmentPopupOptionsFromRows(rows)
		self.assertEqual(["Files and folders", "Goal", "Hotline"], [option["title"] for option in options])
		self.assertEqual(["Add", "Add", "Apps"], [option["section"] for option in options])
		self.assertEqual([0, 1, 0], [option["sectionIndex"] for option in options])
		self.assertEqual([0, 1, 2], [option["index"] for option in options])
		self.assertEqual([True, False, False], [option["highlighted"] for option in options])
		self.assertEqual("Set a goal to keep pursuing", options[1]["description"])
		self.assertTrue(all(option["classBased"] for option in options))
		self.assertEqual(1, core.findAttachmentOption(options, dict(options[1])))
		self.assertEqual((), core.attachmentPopupOptionsFromRows([]))

	def test_add_files_popup_list_uses_exact_titles_when_rows_agree(self):
		joined = (
			{"section": "Plugins", "title": "Code Review Review and manage GitHub pull requests", "description": "", "sectionIndex": 0, "index": 0, "field": {"id": 1}},
			{"section": "Plugins", "title": "PDF", "description": "Read, create, and verify PDFs", "sectionIndex": 1, "index": 1, "field": {"id": 2}},
		)
		exact = (
			{"section": "Plugins", "title": "Code Review", "description": "Review and manage GitHub pull requests"},
			{"section": "Plugins", "title": "PDF", "description": "Read, create, and verify PDFs"},
		)
		merged = core.withAttachmentOptionTitles(joined, exact)
		self.assertEqual(["Code Review", "PDF"], [option["title"] for option in merged])
		self.assertEqual("Review and manage GitHub pull requests", merged[0]["description"])
		self.assertEqual({"id": 1}, merged[0]["field"])
		self.assertEqual(0, core.findAttachmentOption(joined, merged[0]))
		# Any disagreement keeps the document's reading.
		self.assertEqual(joined, core.withAttachmentOptionTitles(joined, exact[:1]))
		self.assertEqual(joined, core.withAttachmentOptionTitles(joined, (exact[0], dict(exact[1], section="Apps"))))
		self.assertEqual(joined, core.withAttachmentOptionTitles(joined, (exact[0], dict(exact[1], title="Docs"))))
		self.assertEqual(joined, core.withAttachmentOptionTitles(joined, ()))

	def test_add_files_popup_options_open_in_a_native_list(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		method = next(
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name == "_focusAttachmentSourceMenu"
		)
		namespace = {
			"State": type("State", (), {"COLLAPSED": "collapsed"}),
			"_isChatGPTObject": lambda obj: True,
			"_isCodexPromptObject": lambda obj: obj == "prompt",
			"_isVirtualBufferDocument": lambda buffer: True,
			"api": type("Api", (), {"getFocusObject": staticmethod(lambda: "prompt")}),
			"ATTACHMENT_POPUP_SETTLE_ATTEMPTS": 4,
			"log": type("Log", (), {"debugWarning": staticmethod(lambda *args, **kwargs: None)}),
			"withAttachmentOptionTitles": core.withAttachmentOptionTitles,
		}
		exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		shown = []
		class Subject:
			_conversationWindowHandle = 10
			_buffer = "buffer"
			_attachmentSourceFocusTimer = None
			def _conversationWindowIsAvailable(self, handle): return True
			def _conversationWindowOwnsForeground(self, handle): return True
			def _isAddFilesButton(self, obj): return False
			def _attachmentPopupAnchor(self, buffer): return "anchor"
			def _readAttachmentPopupOptions(self, buffer): return ({"title": "Files and folders"},)
			def _readAttachmentPopupOptionsWithUIA(self, buffer): return ()
			def _showAttachmentMenuDialog(self, options, button, windowHandle): shown.append((options, windowHandle))
			def _moveBrowseCaretToAttachmentPopup(self, buffer, anchor): raise AssertionError("browse fallback used")
		button = type("Button", (), {"states": ("expanded",)})()
		namespace["_focusAttachmentSourceMenu"](Subject(), button, "buffer", 10)
		self.assertEqual([(({"title": "Files and folders"},), 10)], shown)

	def test_add_files_popup_in_ui_automation_document_skips_document_search(self):
		# Searching NVDA's UI Automation document took six seconds in ChatGPT.
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef)
			and node.name in ("_focusAttachmentSourceMenu", "_showAttachmentMenuFromUIA", "_readAttachmentPopupOptions")
		]
		timers = []
		namespace = {
			"State": type("State", (), {"COLLAPSED": "collapsed"}),
			"_isChatGPTObject": lambda obj: True,
			"_isCodexPromptObject": lambda obj: obj == "prompt",
			"_isVirtualBufferDocument": lambda buffer: False,
			"api": type("Api", (), {"getFocusObject": staticmethod(lambda: "prompt")}),
			"ATTACHMENT_POPUP_SETTLE_ATTEMPTS": 4,
			"ATTACHMENT_POPUP_RETRIES": 10,
			"ATTACHMENT_POPUP_RETRY_MILLISECONDS": 150,
			"wx": type("Wx", (), {"CallLater": staticmethod(lambda *args: timers.append(args) or "timer")}),
			"log": type("Log", (), {
				"debug": staticmethod(lambda *args, **kwargs: None),
				"debugWarning": staticmethod(lambda *args, **kwargs: (_ for _ in ()).throw(sys.exc_info()[1])),
				"info": staticmethod(lambda *args, **kwargs: None),
			}),
		}
		for method in methods:
			exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		shown = []
		uiaOptions = [()]
		class Subject:
			_conversationWindowHandle = 10
			_buffer = "buffer"
			_attachmentSourceFocusTimer = None
			_showAttachmentMenuFromUIA = namespace["_showAttachmentMenuFromUIA"]
			_focusAttachmentSourceMenu = namespace["_focusAttachmentSourceMenu"]
			_readAttachmentPopupOptions = namespace["_readAttachmentPopupOptions"]
			def _conversationWindowIsAvailable(self, handle): return True
			def _conversationWindowOwnsForeground(self, handle): return True
			def _isAddFilesButton(self, obj): return False
			def _attachmentPopupAnchor(self, buffer): raise AssertionError("document searched")
			def _attachmentSourceMenuObject(self, buffer): raise AssertionError("document searched")
			def _readAttachmentPopupOptionsWithUIA(self, buffer): return uiaOptions[0]
			def _showAttachmentMenuDialog(self, options, button, windowHandle): shown.append(options)
		subject = Subject()
		button = type("Button", (), {"states": ("expanded",)})()
		namespace["_focusAttachmentSourceMenu"](subject, button, "buffer", 10)
		self.assertEqual([], shown)
		self.assertEqual(1, timers[-1][-1])
		uiaOptions[0] = ({"title": "Files and folders"},)
		namespace["_focusAttachmentSourceMenu"](subject, button, "buffer", 10, 1)
		self.assertEqual([({"title": "Files and folders"},)], shown)
		self.assertEqual(({"title": "Files and folders"},), subject._readAttachmentPopupOptions("buffer"))

	def test_chosen_add_files_option_is_chosen_with_the_popup_keyboard(self):
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(
			node for node in pluginTree.body
			if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin"
		)
		methods = [
			node for node in pluginClass.body
			if isinstance(node, ast.FunctionDef) and node.name in (
				"_activateAttachmentOption", "_confirmAttachmentChoice", "_addFilesPopupIsOpen",
			)
		]
		later, spoken, keys = [], [], []
		focus = {"value": "prompt"}
		class Gesture:
			@staticmethod
			def fromName(name):
				return type("Key", (), {"send": lambda self: keys.append(name)})()
		namespace = {
			"State": type("State", (), {"EXPANDED": "expanded"}),
			"wx": type("Wx", (), {"CallLater": staticmethod(lambda delay, *args: later.append(args))}),
			"winUser": type("WinUser", (), {"setForegroundWindow": staticmethod(lambda handle: None)}),
			"ui": type("Ui", (), {"message": staticmethod(spoken.append)}),
			"api": type("Api", (), {"getFocusObject": staticmethod(lambda: focus["value"])}),
			"keyboardHandler": type("Keyboard", (), {"KeyboardInputGesture": Gesture}),
			"_isCodexPromptObject": lambda obj: obj == "prompt",
			"ATTACHMENT_OPTION_ACTIVATION_ATTEMPTS": 10,
			"ATTACHMENT_OPTION_CONFIRM_MILLISECONDS": 600,
			"ATTACHMENT_OPTION_STEP_MILLISECONDS": 200,
			"findAttachmentOption": core.findAttachmentOption,
			"promptTextAddition": core.promptTextAddition,
			"_": lambda text: text,
			"log": type("Log", (), {
				"info": staticmethod(lambda *args, **kwargs: None),
				"debugWarning": staticmethod(lambda *args, **kwargs: None),
			}),
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
		files = {"title": "Files and folders", "section": "Add", "field": {}}
		goal = {"title": "Goal", "section": "Add", "field": {}}
		plan = {"title": "Plan mode", "section": "Add", "field": {}}
		class Button:
			def __init__(self, expanded): self.states = ("expanded",) if expanded else ()
		class Subject:
			_conversationWindowHandle = 10
			_attachmentMenuWindowHandle = 10
			_attachmentMenuButton = None
			_buffer = "buffer"
			def __init__(self, expanded):
				self.button = Button(expanded)
				self.reopened = 0
			def _conversationWindowIsAvailable(self, handle): return True
			def _conversationWindowOwnsForeground(self, handle): return True
			def _currentAddFilesButton(self, saved=None): return self.button
			def _readAttachmentPopupOptions(self, buffer): return (files, goal, plan)
			def _promptTextForAnnouncement(self): return ""
			def _reopenAttachmentPopup(self, button):
				self.reopened += 1
				button.states = ("expanded",)
				return True
		for method in methods:
			setattr(Subject, method.name, namespace[method.name])
		def runOne():
			callback, *args = later.pop(0)
			callback(*args)
		# The list closed ChatGPT's popup: let focus settle, reopen it, then use
		# Down Arrow to the option's position and Tab. No click is attempted.
		subject = Subject(expanded=False)
		subject._activateAttachmentOption(plan, 0, False)
		self.assertEqual([], keys)
		runOne()
		self.assertEqual(1, subject.reopened)
		runOne()
		self.assertEqual(["downArrow", "downArrow", "tab"], keys)
		subject.button.states = ()
		runOne()
		self.assertEqual(["Plan mode chosen"], spoken)
		spoken.clear()
		# The first option needs only Tab, and a popup that is already open is not reopened.
		keys.clear()
		subject = Subject(expanded=True)
		subject._activateAttachmentOption(files, 0, False)
		runOne()
		self.assertEqual(["tab"], keys)
		self.assertEqual(0, subject.reopened)
		subject.button.states = ()
		# Select files took focus; NVDA announces the dialog, so the add-on stays quiet.
		focus["value"] = "Select files"
		runOne()
		self.assertEqual([], spoken)
		focus["value"] = "prompt"
		# Keys are never sent while focus is outside the prompt.
		keys.clear()
		later.clear()
		focus["value"] = "sidebar"
		subject = Subject(expanded=True)
		subject._activateAttachmentOption(goal, 0, False)
		while later:
			runOne()
		self.assertEqual([], keys)
		self.assertIn("could not be chosen", spoken[-1])
		# If the popup stays open after Tab, the user is told.
		focus["value"] = "prompt"
		spoken.clear()
		subject = Subject(expanded=True)
		subject._activateAttachmentOption(goal, 0, False)
		runOne()
		runOne()
		self.assertIn("could not be chosen", spoken[-1])

	def test_browser_navigator_is_removed(self):
		self.assertFalse((PLUGIN_PATH.parent / "browserNavigatorDialog.py").exists())
		pluginSource = PLUGIN_PATH.read_text(encoding="utf-8")
		for removed in (
			"BrowserNavigatorDialog", "_startEmbeddedBrowserScan", "_browserNavigatorDialog",
			"rememberEmbeddedBrowserLocations", "_browserSavedLocations",
		):
			self.assertNotIn(removed, pluginSource)
		for removed in ("browserNavigatorCategory", "browserPageSummary", "browserSnapshotText"):
			self.assertFalse(hasattr(browserAccess, removed), removed)
		# Embedded-browser loading announcements remain available.
		self.assertIn("def _announceEmbeddedBrowserProgress", pluginSource)


if __name__ == "__main__":
	unittest.main()
