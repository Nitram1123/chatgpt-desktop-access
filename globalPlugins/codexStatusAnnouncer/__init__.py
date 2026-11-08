"""Provide accessible feedback and navigation for the ChatGPT desktop app."""

import os
import json
import re
import threading
import time
from pathlib import Path

import addonHandler
import api
import appModuleHandler
import braille
import config
import eventHandler
import globalPluginHandler
import gui
import inputCore
import keyboardHandler
import queueHandler
import speech
import textInfos
import textInfos.offsets
import ui
import versionInfo
import winUser
import wx
from controlTypes import OutputReason, Role, State
from NVDAObjects.UIA import UIATextInfo
from treeInterceptorHandler import RootProxyTextInfo
from gui import guiHelper
from gui.settingsDialogs import NVDASettingsDialog, SettingsPanel
from logHandler import log
from scriptHandler import script

from .browserAccess import (
	embeddedBrowserProgress, embeddedBrowserTitle, isEmbeddedBrowserContainerRole,
	isEmbeddedBrowserContainerText, isEmbeddedBrowserDocumentStructure,
)
from .attachmentDiagnostics import AttachmentMenuDiagnostics
from .attachmentMenuDialog import AttachmentMenuDialog
from .chatHistoryDialog import ChatHistoryDialog
from .messageListDialog import MessageListDialog
from .bufferUpdates import BufferUpdateObserver
from .core import AnnouncementHistory, CATEGORY_SETTING, ChatMessageAccumulator, ChatMessageFieldCollector, announcementPriority, attachmentMenuItemLabel, brailleStatusMessage, brailleTypingGestureCommitsText, bufferInspectionDue, categoryOutputActions, changelogForDisplay, chatActionMatches, chatHistorySnapshotDecision, chatTitleMatches, codexHistorySourceSignature, codexThreadUrl, coalescedPollDelay, completedTextDelta, confirmedUserMessageSubmission, conversationModeFromDocumentNames, conversationModeFromSwitchControl, conversationWindowShouldDetach, currentActivitySummary, duplicateChannelActions, firstStatusLabel, focusStateTransition, formatCommandSpeech, formatCustomAnnouncement, formatElapsedDuration, intermediateCompletionCategory, isBrailleTypingGestureIdentifier, isChatHistoryConversationBoundary, attachmentOptionKeyStep, attachmentPopupOptions, findAttachmentOption, promptTextAddition, isChatHistoryInterfaceText, isCodexPromptLabel, isConversationNavigationGestureIdentifier, isKnownNonStatusButton, isPermissionDecisionLabel, isPermissionPromptText, isPromptSubmissionGestureIdentifier, isResponseCompletionMarkerText, isStopControlLabel, isTaskCompletionLabel, loadActiveCodexThreadTitles, mergeConversationTail, loadArchivedThreads, looksLikeBlankCodexConversation, looksLikeCodexConversation, mergeSupportedAppNames, modeSpecificRecentChatTitles, nextBusyState, outputActions, pendingChatTitle, pluginInstallProgress, pluginProgressBusyTransition, pollDelay, previewSelection, promptControlKind, promptSubmissionGestureShouldStart, redactSensitive, repairConfigurationValues, responseCompletionScanMarker, responseCompletionTransition, shouldFinalizeResponseCompletion, shouldLogDiagnosticSnapshot, shouldPlayContinuousWorkingClick, shouldPreserveBrailleComposition, shouldReplaceScheduledPoll, shouldSuppressNativeConversationUpdate, shouldSuppressRoutineBraille, shouldSuppressSemanticDuplicate, soundKey, statusDetails, statusMessage, stopControlTransition, supersedesResponseCompletionCandidate, uniqueThreadLabels, usageLimitNotice, userMessageNumber, userMessageSubmissionTransition, viewerTitleMatches
from .core import voiceControlKind
from .core import (
	NATIVE_TASK_TIMER_PREFIXES,
	chatMessageHeadingSpeaker, chatMessageSpeaker, isNativeThinkingControl, isNativeThinkingLabel,
	nativeActiveTaskSeconds, nativeTaskTimer,
)
from .core import attachmentPopupStructureSummary, isAttachmentButtonLikeLabel
from .core import chatGPTAppVersionSummary, otherComposerMode, selectedComposerMode
from .core import chatGPTCompatibilityFindings, submittedTurnFinishedUnseen
from .core import (
	SUGGESTION_MENU_CLOSE_KEYS, SUGGESTION_MENU_EDIT_KEYS, SUGGESTION_MENU_MOVE_KEYS,
	SUGGESTION_MENU_TRIGGER_CHARACTERS, attachmentOptionKey, gestureKeyName, suggestionMenuReading,
)
from .core import COMPOSER_FILE_CLASS, COMPOSER_TOOL_ICON_CLASS, uniqueLabels
from .core import (
	ADD_FILES_BUTTON_NAME, CHATGPT_PROMPT_EDITOR_CLASS, COMPOSER_MODE_GROUP_NAME,
	MODE_SWITCH_BUTTON_LABELS, SOURCES_MENU_BUTTON_NAME,
)
from .core import ATTACHMENT_POPUP_CLASS_KEY, ATTACHMENT_POPUP_HEADER_CLASS, ATTACHMENT_POPUP_HINT_LABELS, ATTACHMENT_POPUP_ROW_CLASS, attachmentPopupOptionsFromRows, slowScanPauseSeconds, withAttachmentOptionTitles
from .core import shouldSuppressTrailingCompletion
from .soundOutput import (
	discardPendingActivitySounds as _discardPendingActivitySounds,
	playProgressSound as _playProgressSound,
	safeBeep as _safeBeep,
	stopProgressSounds as _stopProgressSounds,
)

addonHandler.initTranslation()

CONFIG_SECTION = "codexStatusAnnouncer"
ADDON_VERSION = "2026.2.20"
CHATGPT_USAGE_URL = "https://chatgpt.com/settings/usage"
DEFAULT_SUPPORTED_APP_NAMES = "chatgpt,codex"
APP_MODULE_ALIASES = (("codex", "chatgpt"),)
CURRENT_RELEASE_NOTES = _(
	"Version 2026.2.20\n\n"
	"What's new:\n"
	"• The Working sound now stops after a short Codex or ChatGPT turn, instead of playing until the ChatGPT window is closed.\n"
	"• French translation of the add-on's settings, commands, and announcements, contributed by Nitram1123."
)
VERBOSITY_CHOICES = ("minimal", "full")
FULL_SPEECH_PROFILE_CHOICES = ("standard", "developer", "raw")
MINIMAL_SPEECH_PROFILE_CHOICES = ("essential", "balanced", "informative")
BRAILLE_DETAIL_CHOICES = ("concise", "informative", "full")
SOUND_STYLE_CHOICES = ("clicks", "tones")
CLICK_VOLUME_CHOICES = ("soft", "normal", "loud")
COMMAND_PUNCTUATION_CHOICES = ("normal", "enhanced", "literal")
OUTPUT_MODE_CHOICES = ("all", "speech", "sound", "braille", "off")
CATEGORY_OUTPUT_CONFIG = {
	"thinking": "outputThinking", "working": "outputWorking", "command": "outputCommands",
	"search": "outputSearches", "file": "outputFiles", "build": "outputBuilds",
	"tool": "outputTools", "completion": "outputCompletions", "attention": "outputAttention",
	"other": "outputOther", "commentary": "outputCommentary",
}
PREVIEW_ITEMS = (
	("thinking", "announcementThinking", _("Thinking"), _("Thinking")),
	("working", "announcementWorking", _("Working"), _("Working")),
	("command", "announcementCommand", _("Command"), _("Running command")),
	("search", "announcementSearch", _("Search"), _("Searching the web")),
	("file", "announcementFile", _("File"), _("Editing file")),
	("build", "announcementBuild", _("Build and test"), _("Running tests")),
	("tool", "announcementTool", _("Tool"), _("Using tool")),
	("commentary", "announcementCommentary", _("Commentary"), _("I am inspecting the current task.")),
	("backgroundPulse1", "announcementPulse1", _("Background progress one"), _("Command still running, 5 seconds")),
	("backgroundPulse2", "announcementPulse2", _("Background progress two"), _("Command still running, 10 seconds")),
	("completion", "announcementCompletion", _("Completion"), _("Command finished")),
	("completion", "announcementFailure", _("Failure"), _("Command failed")),
	("attention", "announcementAttention", _("Permission required"), _("Permission required")),
	("other", "announcementOther", _("Other progress"), _("Waiting")),
	("monitoringActive", "announcementMonitoringActive", _("Monitoring active"), _("Activity monitoring active")),
	("monitoringInactive", "announcementMonitoringInactive", _("Monitoring inactive"), _("Activity monitoring inactive")),
	("submission", "announcementSubmission", _("Prompt submitted"), _("Prompt submitted")),
)
ANNOUNCEMENT_CONFIG_BY_ACTION = {item[0]: item[1] for item in PREVIEW_ITEMS if item[0] != "completion"}
ANNOUNCEMENT_CONFIG_BY_ACTION.update({"completion": "announcementCompletion", "failure": "announcementFailure"})
RESPONSE_COMPLETION_SETTLE_SECONDS = 5.0
PROMPT_TYPING_QUIET_SECONDS = 1.25
CONVERSATION_NAVIGATION_QUIET_SECONDS = 3.0
CONVERSATION_ENTRY_CORRECTION_SECONDS = 4.0
CONVERSATION_WINDOW_CLOSE_GRACE_SECONDS = 2.0
CHAT_HISTORY_MODE_SETTLE_SECONDS = 0.75
CHAT_HISTORY_SNAPSHOT_CONFIRM_SECONDS = 0.25
CHAT_HISTORY_RETRY_MILLISECONDS = 300
CHAT_HISTORY_EXPANSION_DELAY_MILLISECONDS = 700
CHAT_HISTORY_EXPANSION_RETRY_MILLISECONDS = 300
CHAT_HISTORY_EXPANSION_MAX_PAGES = 20
CHAT_HISTORY_EXPANSION_MAX_STALE_SCANS = 30
CHAT_HISTORY_OPEN_RETRY_MILLISECONDS = 150
CHAT_HISTORY_OPEN_TIMEOUT_SECONDS = 5.0
BUFFER_TAIL_SCAN_CHARACTERS = 8192
RECENT_CHAT_INITIAL_SCAN_CHARACTERS = 32768
CONVERSATION_SCAN_HEAD_CHARACTERS = 32768
CONVERSATION_SCAN_TAIL_CHARACTERS = 32768
RECENT_CHAT_MAX_SCAN_CHARACTERS = 524288
MESSAGE_LIST_LIMIT = 100
MODE_CONTROL_RETRY_SECONDS = 5.0
MODE_SELECTOR_CONFIRM_TIMEOUT_SECONDS = 30.0
ATTACHMENT_MENU_ARM_SECONDS = 5.0
ATTACHMENT_MENU_TIMEOUT_SECONDS = 60.0
ATTACHMENT_MENU_DUPLICATE_SECONDS = 0.35
ATTACHMENT_MENU_STALE_EXPANSION_SECONDS = 1.25
ATTACHMENT_SOURCE_FOCUS_DELAY_MILLISECONDS = 180
ATTACHMENT_POPUP_RETRIES = 10
ATTACHMENT_POPUP_SETTLE_ATTEMPTS = 4
ATTACHMENT_POPUP_SCAN_CHARACTERS = 40000
COMPATIBILITY_CHECK_DELAY_MILLISECONDS = 5000
SUGGESTION_MENU_OPEN_DELAY_MILLISECONDS = 350
SUGGESTION_MENU_MOVE_DELAY_MILLISECONDS = 90
SUGGESTION_MENU_FILTER_DELAY_MILLISECONDS = 300
COMPATIBILITY_CHECK_RETRY_MILLISECONDS = 30000
COMPATIBILITY_CHECK_RETRIES = 10
ATTACHMENT_OPTION_ACTIVATION_ATTEMPTS = 10
ATTACHMENT_OPTION_CONFIRM_MILLISECONDS = 600
ATTACHMENT_OPTION_STEP_MILLISECONDS = 200
ATTACHMENT_OPTION_HIGHLIGHT_MILLISECONDS = 80
ATTACHMENT_OPTION_HIGHLIGHT_WAITS = 25
ATTACHMENT_OPTION_EXTRA_STEPS = 5
ATTACHMENT_POPUP_RETRY_MILLISECONDS = 150
ATTACHMENT_ACTIVATION_WINDOW_SECONDS = 1.5
PROMPT_INSPECTION_DELAY_MS = 250
BRAILLE_CARET_GRACE_SECONDS = 1.0
BROWSER_LOAD_SETTLE_MILLISECONDS = 1500
BROWSER_BUSY_FALLBACK_MILLISECONDS = 30000
VOICE_CONTROL_SEARCH_LABELS = (
	("stop", "Stop voice chat"),
	("stop", "End voice chat"),
	("stop", "Leave voice mode"),
	("stop", "Exit voice mode"),
	("start", "Start voice chat"),
	("start", "Start voice mode"),
	("unmute", "Unmute microphone"),
	("unmute", "Unmute mic"),
	("mute", "Mute microphone"),
	("mute", "Mute mic"),
)
VOICE_CONTROL_CONFIRMATION_DELAY_MS = 500
VOICE_CONTROL_CONFIRMATION_ATTEMPTS = 2
APP_SCOPED_SCRIPT_NAMES = (
	"readMostRecentChatMessage", "readSecondMostRecentChatMessage",
	"readThirdMostRecentChatMessage", "readFourthMostRecentChatMessage",
	"readFifthMostRecentChatMessage", "readSixthMostRecentChatMessage",
	"readSeventhMostRecentChatMessage", "readEighthMostRecentChatMessage",
	"readNinthMostRecentChatMessage", "readTenthMostRecentChatMessage",
	"toggleVoiceMode", "toggleMicrophoneMute", "toggleConversationMode",
	"openConversationMessages", "reportOrSwitchComposerMode", "reportComposerAttachments",
)
APP_SCOPED_DEFAULT_GESTURES = (
	"kb:control+1", "kb:control+2", "kb:control+3", "kb:control+4", "kb:control+5",
	"kb:control+6", "kb:control+7", "kb:control+8", "kb:control+9", "kb:control+0",
	"kb:NVDA+alt+v", "kb:NVDA+`", "kb:NVDA+alt+w", "kb:NVDA+alt+a",
)
_lastConfigurationRepairs = ()
_activePluginInstance = None
config.conf.spec[CONFIG_SECTION] = {
	"verbosity": "option('minimal', 'full', default='full')",
	"fullSpeechProfile": "option('standard', 'developer', 'raw', default='developer')",
	"minimalSpeechProfile": "option('essential', 'balanced', 'informative', default='balanced')",
	"commandPunctuation": "option('normal', 'enhanced', 'literal', default='enhanced')",
	"maximumSpokenCommandCharacters": "integer(default=240, min=40, max=2000)",
	"speech": "boolean(default=True)",
	"braille": "boolean(default=True)",
	"brailleDetail": "option('concise', 'informative', 'full', default='full')",
	"enableMessageList": "boolean(default=True)",
	"protectBrailleReading": "boolean(default=True)",
	"interruptUrgentSpeech": "boolean(default=True)",
	"redactSensitive": "boolean(default=False)",
	"workingIntervalSeconds": "integer(default=5, min=1, max=300)",
	"idlePollMs": "integer(default=500, min=100, max=5000)",
	"completionSound": "boolean(default=False)",
	"soundWhenSpeechUnavailable": "boolean(default=True)",
	"progressSoundStyle": "option('clicks', 'tones', default='clicks')",
	"clickVolume": "option('soft', 'normal', 'loud', default='normal')",
	"continuousWorkingClicks": "boolean(default=True)",
	"workingClickIntervalMs": "integer(default=1400, min=500, max=5000)",
	"workingClickStartDelayMs": "integer(default=750, min=0, max=10000)",
	"promptSubmissionClick": "boolean(default=True)",
	"monitoringFocusClicks": "boolean(default=True)",
	"maximumBusyMinutes": "integer(default=60, min=1, max=240)",
	"welcomeShown": "boolean(default=False)",
	"lastShownVersion": "string(default='')",
	"lastCheckedChatGPTVersion": "string(default='')",
	"supportedAppNames": "string(default='chatgpt,codex')",
	"diagnosticLogging": "boolean(default=False)",
	"announceEmbeddedBrowserProgress": "boolean(default=True)",
	"announceSuggestionMenus": "boolean(default=True)",
	"announceThinking": "boolean(default=True)",
	"announceWorking": "boolean(default=True)",
	"announceCommands": "boolean(default=True)",
	"announceSearches": "boolean(default=True)",
	"announceFiles": "boolean(default=True)",
	"announceBuilds": "boolean(default=True)",
	"announceTools": "boolean(default=True)",
	"announceCompletions": "boolean(default=True)",
	"announceOther": "boolean(default=True)",
	"announceCommentary": "boolean(default=True)",
	"announceHeartbeat": "boolean(default=True)",
	"announceAttention": "boolean(default=True)",
	"outputThinking": "option('all', 'speech', 'sound', 'braille', 'off', default='all')",
	"outputWorking": "option('all', 'speech', 'sound', 'braille', 'off', default='all')",
	"outputCommands": "option('all', 'speech', 'sound', 'braille', 'off', default='all')",
	"outputSearches": "option('all', 'speech', 'sound', 'braille', 'off', default='all')",
	"outputFiles": "option('all', 'speech', 'sound', 'braille', 'off', default='all')",
	"outputBuilds": "option('all', 'speech', 'sound', 'braille', 'off', default='all')",
	"outputTools": "option('all', 'speech', 'sound', 'braille', 'off', default='all')",
	"outputCompletions": "option('all', 'speech', 'sound', 'braille', 'off', default='all')",
	"outputAttention": "option('all', 'speech', 'sound', 'braille', 'off', default='all')",
	"outputOther": "option('all', 'speech', 'sound', 'braille', 'off', default='all')",
	"outputCommentary": "option('all', 'speech', 'sound', 'braille', 'off', default='all')",
	"announcementThinking": "string(default='')",
	"announcementWorking": "string(default='')",
	"announcementCommand": "string(default='')",
	"announcementSearch": "string(default='')",
	"announcementFile": "string(default='')",
	"announcementBuild": "string(default='')",
	"announcementTool": "string(default='')",
	"announcementCommentary": "string(default='')",
	"announcementPulse1": "string(default='')",
	"announcementPulse2": "string(default='')",
	"announcementCompletion": "string(default='')",
	"announcementFailure": "string(default='')",
	"announcementAttention": "string(default='')",
	"announcementOther": "string(default='')",
	"announcementMonitoringActive": "string(default='')",
	"announcementMonitoringInactive": "string(default='')",
	"announcementSubmission": "string(default='')",
}


def _settings():
	return config.conf[CONFIG_SECTION]


def _repairConfiguration():
	"""Repair migrated choice and numeric values without discarding valid preferences."""
	global _lastConfigurationRepairs
	conf = _settings()
	choiceDefaults = {
		"verbosity": (VERBOSITY_CHOICES, "full"),
		"fullSpeechProfile": (FULL_SPEECH_PROFILE_CHOICES, "developer"),
		"minimalSpeechProfile": (MINIMAL_SPEECH_PROFILE_CHOICES, "balanced"),
		"brailleDetail": (BRAILLE_DETAIL_CHOICES, "full"),
		"commandPunctuation": (COMMAND_PUNCTUATION_CHOICES, "enhanced"),
		"progressSoundStyle": (SOUND_STYLE_CHOICES, "clicks"),
		"clickVolume": (CLICK_VOLUME_CHOICES, "normal"),
	}
	for key in CATEGORY_OUTPUT_CONFIG.values():
		choiceDefaults[key] = (OUTPUT_MODE_CHOICES, "all")
	numericDefaults = {
		"maximumSpokenCommandCharacters": (40, 2000, 240),
		"workingIntervalSeconds": (1, 300, 5),
		"idlePollMs": (100, 5000, 500),
		"workingClickIntervalMs": (500, 5000, 1400),
		"workingClickStartDelayMs": (0, 10000, 750),
		"maximumBusyMinutes": (1, 240, 60),
	}
	booleanKeys = tuple((key, default) for key, default in {
		"speech": True, "braille": True, "protectBrailleReading": True,
		"enableMessageList": True,
		"interruptUrgentSpeech": True, "redactSensitive": False,
		"completionSound": False, "soundWhenSpeechUnavailable": True,
		"continuousWorkingClicks": True, "promptSubmissionClick": True,
		"monitoringFocusClicks": True, "welcomeShown": False,
		"diagnosticLogging": False,
		"announceEmbeddedBrowserProgress": True, "announceSuggestionMenus": True, "announceThinking": True,
		"announceWorking": True, "announceCommands": True,
		"announceSearches": True, "announceFiles": True,
		"announceBuilds": True, "announceTools": True,
		"announceCompletions": True, "announceOther": True,
		"announceCommentary": True, "announceHeartbeat": True,
		"announceAttention": True,
	}.items())
	repaired = repairConfigurationValues(
		conf, choiceDefaults, numericDefaults, booleanKeys,
		(
			("supportedAppNames", DEFAULT_SUPPORTED_APP_NAMES), ("lastShownVersion", ""),
			("lastCheckedChatGPTVersion", ""),
		),
	)
	mergedAppNames = mergeSupportedAppNames(conf["supportedAppNames"])
	if conf["supportedAppNames"] != mergedAppNames:
		conf["supportedAppNames"] = mergedAppNames
		repaired = tuple(dict.fromkeys((*repaired, "supportedAppNames")))
	if repaired:
		log.warning("ChatGPT Desktop Access repaired configuration fields: %s", ", ".join(repaired))
	_lastConfigurationRepairs = repaired
	return tuple(repaired)


def _migrateApplicationGestureMappings():
	"""Move custom mappings for newly app-scoped commands without touching unrelated gestures."""
	userMap = getattr(getattr(inputCore, "manager", None), "userGestureMap", None)
	if userMap is None:
		return 0
	oldModule, oldClass = "globalPlugins.codexStatusAnnouncer", "GlobalPlugin"
	newModule, newClass = "appModules.chatgpt", "AppModule"
	oldSectionName = f"{oldModule}.{oldClass}"
	newSectionName = f"{newModule}.{newClass}"

	def gesturesFrom(value):
		if value in (None, ""):
			return ()
		if isinstance(value, str):
			return (value,)
		return tuple(value)

	try:
		exported = userMap.export()
		oldSection = exported.get(oldSectionName, {})
		if not oldSection:
			return 0
		newSection = exported.get(newSectionName, {})
		existing = set()
		for scriptName, gestureValues in newSection.items():
			scriptName = None if scriptName in (None, "None") else scriptName
			for gesture in gesturesFrom(gestureValues):
				existing.add((inputCore.normalizeGestureIdentifier(gesture), scriptName))
		defaultGestures = {
			inputCore.normalizeGestureIdentifier(gesture)
			for gesture in APP_SCOPED_DEFAULT_GESTURES
		}
		moves = []
		for scriptName in APP_SCOPED_SCRIPT_NAMES:
			for gesture in gesturesFrom(oldSection.get(scriptName)):
				moves.append((gesture, scriptName))
		for noneKey in (None, "None"):
			for gesture in gesturesFrom(oldSection.get(noneKey)):
				if inputCore.normalizeGestureIdentifier(gesture) in defaultGestures:
					moves.append((gesture, None))
		moved = 0
		for gesture, scriptName in moves:
			normalizedGesture = inputCore.normalizeGestureIdentifier(gesture)
			userMap.remove(normalizedGesture, oldModule, oldClass, scriptName)
			try:
				if (normalizedGesture, scriptName) not in existing:
					userMap.add(normalizedGesture, newModule, newClass, scriptName)
					existing.add((normalizedGesture, scriptName))
			except Exception:
				# Keep the user's original mapping if the new location cannot accept it.
				userMap.add(normalizedGesture, oldModule, oldClass, scriptName)
				raise
			moved += 1
		if moved:
			userMap.save()
		return moved
	except Exception:
		log.debugWarning("ChatGPT Desktop Access could not migrate application gesture mappings", exc_info=True)
		return 0


def _customizeAnnouncement(message, action, activity="", seconds=0, values=None):
	conf = values or _settings()
	key = ANNOUNCEMENT_CONFIG_BY_ACTION.get(action)
	return formatCustomAnnouncement(conf.get(key, "") if key else "", message, activity, seconds)


def _speechIsOff():
	try:
		return speech.getState().speechMode == speech.SpeechMode.off
	except Exception:
		log.debugWarning("ChatGPT Desktop Access could not read NVDA's speech mode", exc_info=True)
		return False


def _send(message, speak=True, showBraille=True, toneCategory=None, progressSoundsEnabled=True, soundStyle=None, clickVolume=None, priority="normal", brailleMessage=None, interruptUrgent=None):
	actions = outputActions(speak, _speechIsOff(), showBraille, progressSoundsEnabled, toneCategory)
	if actions["speech"]:
		if interruptUrgent is None:
			interruptUrgent = _settings()["interruptUrgentSpeech"]
		if priority == "urgent" and interruptUrgent:
			try:
				speech.cancelSpeech()
			except Exception:
				log.debugWarning("ChatGPT Desktop Access could not cancel speech for an urgent message", exc_info=True)
		try:
			speech.speakMessage(message)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access speech output failed", exc_info=True)
	if actions["braille"]:
		try:
			braille.handler.message(message if brailleMessage is None else brailleMessage)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access Braille output failed", exc_info=True)
	if actions["tone"]:
		try:
			return bool(_playProgressSound(
				toneCategory, message, soundStyle or _settings()["progressSoundStyle"],
				clickVolume or _settings()["clickVolume"],
			))
		except Exception:
			log.debugWarning("ChatGPT Desktop Access progress sound output failed", exc_info=True)
	return False


def _moveBrowseableMessageToTop(expectedTitle):
	try:
		foreground = api.getForegroundObject()
		foregroundName = str(getattr(foreground, "name", "") or "")
		if not viewerTitleMatches(expectedTitle, foregroundName):
			log.debug("ChatGPT Desktop Access did not move document focus; expected viewer is not foreground")
			return
		keyboardHandler.KeyboardInputGesture.fromName("control+home").send()
	except Exception:
		log.debugWarning("ChatGPT Desktop Access could not move the document viewer to the top", exc_info=True)


def _showBrowseableMessageAtTop(message, title):
	ui.browseableMessage(message, title=title, closeButton=True)
	wx.CallLater(350, _moveBrowseableMessageToTop, title)


def _completeChangelogMessage():
	changelogPath = Path(addonHandler.getCodeAddon().path) / "changelog.md"
	return changelogForDisplay(changelogPath.read_text(encoding="utf-8"))


def _saveSupportReport(parent, diagnosticReport):
	"""Let the user choose where to save a sanitized support report."""
	defaultName = "chatgpt-desktop-access-support-{timestamp}.txt".format(
		timestamp=time.strftime("%Y%m%d-%H%M%S"),
	)
	with wx.FileDialog(
		parent,
		_("Save sanitized ChatGPT Desktop Access support report"),
		defaultFile=defaultName,
		wildcard=_("Text files (*.txt)|*.txt"),
		style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
	) as dialog:
		if dialog.ShowModal() != wx.ID_OK:
			return False
		path = Path(dialog.GetPath())
	payload = _(
		"ChatGPT Desktop Access sanitized support report\n"
		"Generated: {generated}\nNVDA version: {nvdaVersion}\n\n{report}\n"
	).format(
		generated=time.strftime("%Y-%m-%d %H:%M:%S %z"),
		nvdaVersion=getattr(versionInfo, "version", "unknown"),
		report=diagnosticReport,
	)
	try:
		path.write_text(payload, encoding="utf-8")
	except Exception:
		log.error("Unable to save ChatGPT Desktop Access support report", exc_info=True)
		ui.message(_("The sanitized support report could not be saved"))
		return False
	ui.message(_("Sanitized ChatGPT Desktop Access support report saved"))
	return True


def _openUsageDashboard(message):
	try:
		opened = wx.LaunchDefaultBrowser(CHATGPT_USAGE_URL)
	except Exception:
		log.error("Unable to open the Codex usage dashboard", exc_info=True)
		opened = False
	ui.message(message if opened else _("The Codex usage dashboard could not be opened"))


class CodexStatusAnnouncerSettingsPanel(SettingsPanel):
	title = _("ChatGPT Desktop Access")

	def _addPage(self, title):
		page = wx.Panel(self.notebook)
		sizer = wx.BoxSizer(wx.VERTICAL)
		page.SetSizer(sizer)
		self.notebook.AddPage(page, title)
		return page, guiHelper.BoxSizerHelper(page, sizer=sizer)

	def makeSettings(self, settingsSizer):
		conf = _settings()
		self.notebook = wx.Notebook(self)
		settingsSizer.Add(self.notebook, proportion=1, flag=wx.EXPAND)

		generalPage, helper = self._addPage(_("General"))
		helper.addItem(wx.StaticText(generalPage, label=_(
			"Settings are organized into pages. Press Control+Tab or Shift+Control+Tab to change pages. "
			"Select Apply or OK to save changes. Speech profile and Braille detail settings are on the "
			"Speech and Braille page."
		)))
		self.speech = helper.addItem(wx.CheckBox(generalPage, label=_("Enable &speech announcements")))
		self.braille = helper.addItem(wx.CheckBox(generalPage, label=_("Enable &braille flash messages")))
		self.redactSensitive = helper.addItem(wx.CheckBox(
			generalPage, label=_("&Redact likely secrets and personal path names in Full mode"),
		))
		self.enableMessageList = helper.addItem(wx.CheckBox(
			generalPage, label=_("Enable native conversation &message list"),
		))
		helper.addItem(wx.StaticText(generalPage, label=_(
			"No keyboard shortcut is assigned by default. To open the list, assign "
			"Open the current conversation's messages in a native list in NVDA Input Gestures. "
			"The command works while ChatGPT is focused."
		)))
		self.announceSuggestionMenus = helper.addItem(wx.CheckBox(
			generalPage, label=_("Announce the \"/\" and \"@\" suggestion &menus in the message field"),
		))
		for name in ("speech", "braille", "redactSensitive", "enableMessageList", "announceSuggestionMenus"):
			getattr(self, name).SetValue(conf[name])
		self.testButton = helper.addItem(wx.Button(generalPage, label=_("Test current announcement outputs (&T)")))
		self.testButton.Bind(wx.EVT_BUTTON, self._onTest)

		speechPage, helper = self._addPage(_("Speech and Braille"))
		helper.addItem(wx.StaticText(speechPage, label=_(
			"Speech uses one active profile at a time. Active speech detail selects Minimal or Full, and "
			"the two profile choices are saved separately. Braille detail is independent of speech."
		)))
		self.verbosity = helper.addLabeledControl(_("Active speech &detail:"), wx.Choice, choices=[
			_("Minimal — uses the Minimal speech profile below"),
			_("Full — uses the Full speech profile below"),
		])
		self.verbosity.SetSelection(VERBOSITY_CHOICES.index(conf["verbosity"]))
		self.fullSpeechProfile = helper.addLabeledControl(
			_("Profile used for &Full speech:"), wx.Choice,
			choices=[
				_("Standard — action, target, counts, and useful timing"),
				_("Developer — complete normalized commands and progress"),
				_("Raw — exact exposed Codex progress text"),
			],
		)
		self.fullSpeechProfile.SetSelection(FULL_SPEECH_PROFILE_CHOICES.index(conf["fullSpeechProfile"]))
		self.minimalSpeechProfile = helper.addLabeledControl(
			_("Profile used for &Minimal speech:"), wx.Choice,
			choices=[
				_("Essential — thinking, attention, failures, and task completion"),
				_("Balanced — concise activity changes and results"),
				_("Informative — Balanced plus filenames, counts, and timing"),
			],
		)
		self.minimalSpeechProfile.SetSelection(MINIMAL_SPEECH_PROFILE_CHOICES.index(conf["minimalSpeechProfile"]))
		self.commandPunctuation = helper.addLabeledControl(
			_("Full speech command &punctuation:"), wx.Choice,
			choices=[_("Normal"), _("Enhanced — speak pipes and redirects naturally"), _("Literal — name command symbols")],
		)
		self.commandPunctuation.SetSelection(COMMAND_PUNCTUATION_CHOICES.index(conf["commandPunctuation"]))
		self.maximumSpokenCommandCharacters = helper.addLabeledControl(
			_("Maximum Full speech command &length:"), wx.SpinCtrl,
			min=40, max=2000, initial=conf["maximumSpokenCommandCharacters"],
		)
		self.brailleDetail = helper.addLabeledControl(
			_("Braille detail (&B), independent of speech:"), wx.Choice,
			choices=[_("Concise"), _("Informative"), _("Full — complete commands and progress")],
		)
		self.brailleDetail.SetSelection(BRAILLE_DETAIL_CHOICES.index(conf["brailleDetail"]))
		self.profileSummaryButton = helper.addItem(wx.Button(speechPage, label=""))
		self.profileSummaryButton.Bind(wx.EVT_BUTTON, self._onReviewProfileSummary)
		for control in (self.verbosity, self.fullSpeechProfile, self.minimalSpeechProfile, self.brailleDetail):
			control.Bind(wx.EVT_CHOICE, self._onProfileSettingChanged)
		self._updateProfileSummary()
		self.protectBrailleReading = helper.addItem(wx.CheckBox(
			speechPage, label=_("Keep &conversation reading stable for speech and Braille during live updates"),
		))
		self.protectBrailleReading.SetValue(conf["protectBrailleReading"])
		self.interruptUrgentSpeech = helper.addItem(wx.CheckBox(
			speechPage, label=_("Allow &urgent permission and failure announcements to interrupt current speech"),
		))
		self.interruptUrgentSpeech.SetValue(conf["interruptUrgentSpeech"])
		self.resetSpeechSettings = helper.addItem(wx.Button(speechPage, label=_("&Reset speech profile settings")))
		self.resetSpeechSettings.Bind(wx.EVT_BUTTON, self._onResetSpeechSettings)

		soundsPage, helper = self._addPage(_("Sounds"))
		self.completionSound = helper.addItem(wx.CheckBox(soundsPage, label=_("Play a sound for task &completion or failure")))
		self.progressSounds = helper.addItem(
			wx.CheckBox(soundsPage, label=_("Play &progress sounds for enabled announcements")),
		)
		self.progressSoundStyle = helper.addLabeledControl(
			_("Progress sound style (&J):"), wx.Choice,
			choices=[_("Clicks — soft percussive earcons"), _("Tones — musical earcons")],
		)
		self.progressSoundStyle.SetSelection(SOUND_STYLE_CHOICES.index(conf["progressSoundStyle"]))
		self.clickVolume = helper.addLabeledControl(
			_("Click volume (&Z):"), wx.Choice,
			choices=[_("Soft"), _("Normal"), _("Loud")],
		)
		self.clickVolume.SetSelection(CLICK_VOLUME_CHOICES.index(conf["clickVolume"]))
		self.continuousWorkingClicks = helper.addItem(wx.CheckBox(
			soundsPage, label=_("Play a continuous &Working sound while ChatGPT or Codex is busy"),
		))
		self.continuousWorkingClicks.SetValue(conf["continuousWorkingClicks"])
		self.workingClickIntervalMs = helper.addLabeledControl(
			_("Working sound &interval (milliseconds):"), wx.SpinCtrl,
			min=500, max=5000, initial=conf["workingClickIntervalMs"],
		)
		self.workingClickStartDelayMs = helper.addLabeledControl(
			_("&Delay before repeating Working sounds (milliseconds):"), wx.SpinCtrl,
			min=0, max=10000, initial=conf["workingClickStartDelayMs"],
		)
		self.promptSubmissionClick = helper.addItem(wx.CheckBox(
			soundsPage, label=_("Play a distinct sound when a prompt is &submitted"),
		))
		self.promptSubmissionClick.SetValue(conf["promptSubmissionClick"])
		self.monitoringFocusClicks = helper.addItem(wx.CheckBox(
			soundsPage, label=_("Play sounds when ChatGPT or Codex &monitoring becomes active or inactive"),
		))
		self.monitoringFocusClicks.SetValue(conf["monitoringFocusClicks"])
		self.completionSound.SetValue(conf["completionSound"])
		self.progressSounds.SetValue(conf["soundWhenSpeechUnavailable"])
		self.testSoundButton = helper.addItem(wx.Button(soundsPage, label=_("Test command progress sound (&K)")))
		self.testSoundButton.Bind(wx.EVT_BUTTON, self._onTestSound)

		activityPage, helper = self._addPage(_("Activity Output"))
		helper.addItem(wx.StaticText(activityPage, label=_(
			"Configure background timing, then choose each activity category to review its enabled state and output route."
		)))
		self.workingIntervalSeconds = helper.addLabeledControl(
			_("Background progress &interval (seconds):"), wx.SpinCtrl,
			min=1, max=300, initial=conf["workingIntervalSeconds"],
		)
		self.maximumBusyMinutes = helper.addLabeledControl(
			_("Maximum background activity (&minutes):"), wx.SpinCtrl,
			min=1, max=240, initial=conf["maximumBusyMinutes"],
		)
		self.announceHeartbeat = helper.addItem(wx.CheckBox(
			activityPage, label=_("Announce a recurring background progress &pulse"),
		))
		self.announceHeartbeat.SetValue(conf["announceHeartbeat"])
		self._activityCategories = (
			("announceThinking", "thinking", _("Thinking")),
			("announceWorking", "working", _("Working and analysis")),
			("announceCommands", "command", _("Commands")),
			("announceSearches", "search", _("Web searches")),
			("announceFiles", "file", _("File activity")),
			("announceBuilds", "build", _("Builds, compilation, and tests")),
			("announceTools", "tool", _("Tool use")),
			("announceCompletions", "completion", _("Completions and failures")),
			("announceAttention", "attention", _("Permission and input requests")),
			("announceOther", "other", _("Other recognized progress")),
			("announceCommentary", "commentary", _("Plain-language commentary")),
		)
		self._categoryEnabledValues = {key: bool(conf[key]) for key, category, label in self._activityCategories}
		self._categoryOutputValues = {
			category: str(conf[CATEGORY_OUTPUT_CONFIG[category]])
			for key, category, label in self._activityCategories
		}
		self._outputModeLabels = (
			_("all enabled channels"), _("speech only"), _("sound only"), _("braille only"), _("off"),
		)
		self.activityCategory = helper.addLabeledControl(
			_("Activity &category:"), wx.Choice,
			choices=[self._activityCategoryDisplay(index) for index in range(len(self._activityCategories))],
		)
		self.activityCategory.SetSelection(0)
		self.activityEnabled = helper.addItem(wx.CheckBox(activityPage, label=_("&Enable this activity category")))
		self.activityOutput = helper.addLabeledControl(
			_("Output &route for this category:"), wx.Choice,
			choices=[_("All enabled channels"), _("Speech only"), _("Sound only"), _("Braille only"), _("Off")],
		)
		self._activityCategorySelection = 0
		self._loadActivityCategory(0)
		self.activityCategory.Bind(wx.EVT_CHOICE, self._onActivityCategoryChanged)
		self.activityEnabled.Bind(wx.EVT_CHECKBOX, self._onActivitySettingChanged)
		self.activityOutput.Bind(wx.EVT_CHOICE, self._onActivitySettingChanged)

		wordingPage, helper = self._addPage(_("Wording and Preview"))
		self.previewItem = helper.addLabeledControl(
			_("Preview action (&V):"), wx.Choice,
			choices=[label for category, key, label, message in PREVIEW_ITEMS],
		)
		self.previewItem.SetSelection(0)
		self._announcementEdits = {key: str(conf[key]) for category, key, label, message in PREVIEW_ITEMS}
		self.previewItem.Bind(wx.EVT_CHOICE, self._onPreviewItemChanged)
		self.announcementText = helper.addLabeledControl(
			_("Announcement &text (blank uses built-in):"), wx.TextCtrl,
		)
		self.announcementText.SetValue(self._announcementEdits[PREVIEW_ITEMS[0][1]])
		self.restoreAnnouncementButton = helper.addItem(wx.Button(wordingPage, label=_("&Restore built-in announcement")))
		self.restoreAnnouncementButton.Bind(wx.EVT_BUTTON, self._onRestoreAnnouncement)
		helper.addItem(wx.StaticText(wordingPage, label=_(
			"Available placeholders: {message}, {activity}, {seconds}, and {duration}."
		)))
		self.previewSoundButton = helper.addItem(wx.Button(wordingPage, label=_("Preview selected &sound")))
		self.previewSoundButton.Bind(wx.EVT_BUTTON, self._onPreviewSelectedSound)
		self.previewSpeechButton = helper.addItem(wx.Button(wordingPage, label=_("Preview selected s&peech")))
		self.previewSpeechButton.Bind(wx.EVT_BUTTON, self._onPreviewSelectedSpeech)

		browserPage, helper = self._addPage(_("Browser Access"))
		helper.addItem(wx.StaticText(browserPage, label=_(
			"Use ChatGPT's embedded browser like any other web page in NVDA. Enter or Space activates the current control. Tab and Shift+Tab move between controls. NVDA browse-mode commands work normally."
		)))
		self.announceEmbeddedBrowserProgress = helper.addItem(wx.CheckBox(
			browserPage, label=_("Announce when embedded browser pages start and finish &loading"),
		))
		self.announceEmbeddedBrowserProgress.SetValue(conf["announceEmbeddedBrowserProgress"])

		advancedPage, helper = self._addPage(_("Advanced"))
		self.idlePollMs = helper.addLabeledControl(
			_("Idle compatibility &polling interval (milliseconds):"), wx.SpinCtrl,
			min=100, max=5000, initial=conf["idlePollMs"],
		)
		self.supportedAppNames = helper.addLabeledControl(
			_("Supported application &names, comma separated:"), wx.TextCtrl,
		)
		self.supportedAppNames.SetValue(conf["supportedAppNames"])
		self.diagnosticLogging = helper.addItem(wx.CheckBox(
			advancedPage, label=_("Enable sanitized dia&gnostic logging"),
		))
		self.diagnosticLogging.SetValue(conf["diagnosticLogging"])
		helper.addItem(wx.StaticText(advancedPage, label=_(
			"Warning: NVDA debug logging records spoken Full-mode text, including commands, even when add-on diagnostics are sanitized."
		)))

		supportPage, helper = self._addPage(_("Support"))
		helper.addItem(wx.StaticText(supportPage, label=_(
			"Open help and account pages, save sanitized troubleshooting information, or transfer add-on settings."
		)))
		self.openUsageAndCreditsButton = helper.addItem(wx.Button(supportPage, label=_("&Open usage and credits")))
		self.openUsageAndCreditsButton.Bind(wx.EVT_BUTTON, self._onOpenUsageAndCredits)
		self.viewCurrentRelease = helper.addItem(wx.Button(supportPage, label=_("View current release &notes…")))
		self.viewCurrentRelease.Bind(wx.EVT_BUTTON, self._onViewCurrentRelease)
		self.viewCompleteHistory = helper.addItem(wx.Button(supportPage, label=_("View complete release &history…")))
		self.viewCompleteHistory.Bind(wx.EVT_BUTTON, self._onViewCompleteHistory)
		self.saveSupportReport = helper.addItem(wx.Button(supportPage, label=_("Save sanitized support &report…")))
		self.saveSupportReport.Bind(wx.EVT_BUTTON, self._onSaveSupportReport)
		self.exportSettings = helper.addItem(wx.Button(supportPage, label=_("&Export add-on settings…")))
		self.exportSettings.Bind(wx.EVT_BUTTON, self._onExportSettings)
		self.importSettings = helper.addItem(wx.Button(supportPage, label=_("&Import add-on settings…")))
		self.importSettings.Bind(wx.EVT_BUTTON, self._onImportSettings)

	def _activityCategoryDisplay(self, index):
		enabledKey, category, label = self._activityCategories[index]
		state = _("enabled") if self._categoryEnabledValues[enabledKey] else _("disabled")
		output = self._outputModeLabels[OUTPUT_MODE_CHOICES.index(self._categoryOutputValues[category])]
		return _("{label}: {state}; {output}").format(label=label, state=state, output=output)

	def _refreshActivityCategoryDisplay(self, index):
		if 0 <= index < len(self._activityCategories):
			self.activityCategory.SetString(index, self._activityCategoryDisplay(index))

	def _selectedProfileSummary(self):
		verbosityIndex = self.verbosity.GetSelection()
		verbosity = VERBOSITY_CHOICES[verbosityIndex] if 0 <= verbosityIndex < len(VERBOSITY_CHOICES) else "full"
		if verbosity == "minimal":
			detailLabel = _("Minimal")
			profileLabels = (_("Essential"), _("Balanced"), _("Informative"))
			profileIndex = self.minimalSpeechProfile.GetSelection()
			profileLabel = profileLabels[profileIndex] if 0 <= profileIndex < len(profileLabels) else _("Balanced")
		else:
			detailLabel = _("Full")
			profileLabels = (_("Standard"), _("Developer"), _("Raw"))
			profileIndex = self.fullSpeechProfile.GetSelection()
			profileLabel = profileLabels[profileIndex] if 0 <= profileIndex < len(profileLabels) else _("Developer")
		brailleLabels = (_("Concise"), _("Informative"), _("Full"))
		brailleIndex = self.brailleDetail.GetSelection()
		brailleLabel = brailleLabels[brailleIndex] if 0 <= brailleIndex < len(brailleLabels) else _("Full")
		return _(
			"Selected speech profile: {detail} — {profile}. "
			"Selected Braille detail: {braille}, independent of speech."
		).format(detail=detailLabel, profile=profileLabel, braille=brailleLabel)

	def _updateProfileSummary(self):
		self.profileSummaryButton.SetLabel(_("Review selected profiles (&S): {summary}").format(
			summary=self._selectedProfileSummary(),
		))
		self.profileSummaryButton.GetParent().Layout()

	def _onReviewProfileSummary(self, evt):
		ui.message(self._selectedProfileSummary())

	def _onProfileSettingChanged(self, evt):
		self._updateProfileSummary()
		evt.Skip()

	def _storeActivityCategory(self, index=None):
		index = self._activityCategorySelection if index is None else index
		if index < 0 or index >= len(self._activityCategories):
			return
		enabledKey, category, label = self._activityCategories[index]
		self._categoryEnabledValues[enabledKey] = self.activityEnabled.IsChecked()
		selection = self.activityOutput.GetSelection()
		if 0 <= selection < len(OUTPUT_MODE_CHOICES):
			self._categoryOutputValues[category] = OUTPUT_MODE_CHOICES[selection]
		self._refreshActivityCategoryDisplay(index)

	def _loadActivityCategory(self, index):
		if index < 0 or index >= len(self._activityCategories):
			return
		enabledKey, category, label = self._activityCategories[index]
		self.activityEnabled.SetValue(self._categoryEnabledValues[enabledKey])
		self.activityOutput.SetSelection(OUTPUT_MODE_CHOICES.index(self._categoryOutputValues[category]))

	def _onActivityCategoryChanged(self, evt):
		self._storeActivityCategory(self._activityCategorySelection)
		self._activityCategorySelection = self.activityCategory.GetSelection()
		self._loadActivityCategory(self._activityCategorySelection)

	def _onActivitySettingChanged(self, evt):
		self._storeActivityCategory()

	def _onTest(self, evt):
		verbosity = VERBOSITY_CHOICES[self.verbosity.GetSelection()]
		label = "Testing project: 43 tests for 12 seconds" if verbosity == "minimal" else "Running shell command: python -m unittest discover -s tests"
		fullProfile = FULL_SPEECH_PROFILE_CHOICES[self.fullSpeechProfile.GetSelection()]
		minimalProfile = MINIMAL_SPEECH_PROFILE_CHOICES[self.minimalSpeechProfile.GetSelection()]
		speechMessage = statusMessage(
			label, _, verbosity, self.redactSensitive.IsChecked(), fullProfile, minimalProfile,
		)
		brailleMessage = brailleStatusMessage(
			label, _, BRAILLE_DETAIL_CHOICES[self.brailleDetail.GetSelection()], self.redactSensitive.IsChecked(),
		)
		_send(
			speechMessage,
			self.speech.IsChecked(), self.braille.IsChecked(), "command",
			self.progressSounds.IsChecked(),
			SOUND_STYLE_CHOICES[self.progressSoundStyle.GetSelection()],
			CLICK_VOLUME_CHOICES[self.clickVolume.GetSelection()],
			brailleMessage=brailleMessage,
			interruptUrgent=self.interruptUrgentSpeech.IsChecked(),
		)

	def _onTestSound(self, evt):
		_playProgressSound(
			"command", _("Running command"),
			SOUND_STYLE_CHOICES[self.progressSoundStyle.GetSelection()],
			CLICK_VOLUME_CHOICES[self.clickVolume.GetSelection()],
		)

	def _selectedPreview(self):
		return previewSelection(PREVIEW_ITEMS, self.previewItem.GetSelection())

	def _storeCurrentAnnouncementEdit(self):
		category, key, label, message = self._selectedPreview()
		self._announcementEdits[key] = self.announcementText.GetValue()

	def _onPreviewItemChanged(self, evt):
		oldSelection = getattr(self, "_previousPreviewSelection", 0)
		oldItem = previewSelection(PREVIEW_ITEMS, oldSelection)
		if oldItem:
			self._announcementEdits[oldItem[1]] = self.announcementText.GetValue()
		category, key, label, message = self._selectedPreview()
		self.announcementText.SetValue(self._announcementEdits[key])
		self._previousPreviewSelection = self.previewItem.GetSelection()

	def _onRestoreAnnouncement(self, evt):
		category, key, label, message = self._selectedPreview()
		self._announcementEdits[key] = ""
		self.announcementText.SetValue("")

	def _onPreviewSelectedSound(self, evt):
		style = SOUND_STYLE_CHOICES[self.progressSoundStyle.GetSelection()]
		volume = CLICK_VOLUME_CHOICES[self.clickVolume.GetSelection()]
		category, key, label, message = self._selectedPreview()
		_playProgressSound(category, message, style, volume)

	def _onPreviewSelectedSpeech(self, evt):
		self._storeCurrentAnnouncementEdit()
		category, key, label, message = self._selectedPreview()
		speech.speakMessage(formatCustomAnnouncement(self._announcementEdits[key], message, label, 0))

	def _onOpenUsageAndCredits(self, evt):
		_openUsageDashboard(_("Opening ChatGPT usage and credits. No purchase will be made automatically."))

	def _onViewCurrentRelease(self, evt):
		_showBrowseableMessageAtTop(
			CURRENT_RELEASE_NOTES, _("ChatGPT Desktop Access — current release notes"),
		)

	def _onViewCompleteHistory(self, evt):
		try:
			message = _completeChangelogMessage()
		except Exception:
			log.error("Unable to open the ChatGPT Desktop Access changelog", exc_info=True)
			ui.message(_("The complete release history could not be opened"))
			return
		_showBrowseableMessageAtTop(
			message, _("ChatGPT Desktop Access — complete release history"),
		)

	def _onSaveSupportReport(self, evt):
		if _activePluginInstance is None:
			ui.message(_("ChatGPT Desktop Access is not currently running"))
			return
		_saveSupportReport(self, _activePluginInstance._diagnosticReport())

	def _onExportSettings(self, evt):
		with wx.FileDialog(
			self, _("Export ChatGPT Desktop Access settings"),
			defaultFile="chatgpt-desktop-access-settings.json",
			wildcard=_("JSON files (*.json)|*.json"), style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
		) as dialog:
			if dialog.ShowModal() != wx.ID_OK:
				return
			path = Path(dialog.GetPath())
		try:
			values = {key: value for key, value in _settings().items() if isinstance(value, (str, int, float, bool))}
			path.write_text(json.dumps(values, ensure_ascii=False, indent=2), encoding="utf-8")
		except Exception:
			log.error("Unable to export ChatGPT Desktop Access settings", exc_info=True)
			ui.message(_("Settings could not be exported"))
			return
		ui.message(_("ChatGPT Desktop Access settings exported"))

	def _onImportSettings(self, evt):
		with wx.FileDialog(
			self, _("Import ChatGPT Desktop Access settings"),
			wildcard=_("JSON files (*.json)|*.json"), style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
		) as dialog:
			if dialog.ShowModal() != wx.ID_OK:
				return
			path = Path(dialog.GetPath())
		conf = _settings()
		previousValues = {
			key: value for key, value in conf.items()
			if key in config.conf.spec[CONFIG_SECTION] and isinstance(value, (str, int, float, bool))
		}
		try:
			if path.stat().st_size > 1024 * 1024:
				raise ValueError("settings file exceeds 1 MB")
			values = json.loads(path.read_text(encoding="utf-8"))
			if not isinstance(values, dict):
				raise ValueError("settings root is not an object")
			for key, value in values.items():
				if key in config.conf.spec[CONFIG_SECTION] and isinstance(value, (str, int, float, bool)):
					conf[key] = value
			_repairConfiguration()
			config.conf.save()
			self._loadControlsFromConfiguration()
		except Exception:
			for key, value in previousValues.items():
				conf[key] = value
			_repairConfiguration()
			try:
				config.conf.save()
			except Exception:
				log.debugWarning("Unable to save restored ChatGPT Desktop Access settings", exc_info=True)
			self._loadControlsFromConfiguration()
			log.error("Unable to import ChatGPT Desktop Access settings", exc_info=True)
			ui.message(_("Settings could not be imported"))
			return
		ui.message(_("Settings imported and loaded into this panel."))

	def _loadControlsFromConfiguration(self):
		"""Refresh every editable control after an in-place settings import."""
		conf = _settings()
		self.verbosity.SetSelection(VERBOSITY_CHOICES.index(conf["verbosity"]))
		self.fullSpeechProfile.SetSelection(FULL_SPEECH_PROFILE_CHOICES.index(conf["fullSpeechProfile"]))
		self.minimalSpeechProfile.SetSelection(MINIMAL_SPEECH_PROFILE_CHOICES.index(conf["minimalSpeechProfile"]))
		self.brailleDetail.SetSelection(BRAILLE_DETAIL_CHOICES.index(conf["brailleDetail"]))
		self.interruptUrgentSpeech.SetValue(conf["interruptUrgentSpeech"])
		self.commandPunctuation.SetSelection(COMMAND_PUNCTUATION_CHOICES.index(conf["commandPunctuation"]))
		self.maximumSpokenCommandCharacters.SetValue(conf["maximumSpokenCommandCharacters"])
		for name in (
			"speech", "braille", "protectBrailleReading", "redactSensitive", "completionSound",
			"enableMessageList", "announceSuggestionMenus",
			"diagnosticLogging", "announceHeartbeat", "announceEmbeddedBrowserProgress",
		):
			getattr(self, name).SetValue(conf[name])
		self.workingIntervalSeconds.SetValue(conf["workingIntervalSeconds"])
		self.idlePollMs.SetValue(conf["idlePollMs"])
		self.supportedAppNames.SetValue(conf["supportedAppNames"])
		self.progressSounds.SetValue(conf["soundWhenSpeechUnavailable"])
		self.progressSoundStyle.SetSelection(SOUND_STYLE_CHOICES.index(conf["progressSoundStyle"]))
		self.clickVolume.SetSelection(CLICK_VOLUME_CHOICES.index(conf["clickVolume"]))
		self.continuousWorkingClicks.SetValue(conf["continuousWorkingClicks"])
		self.workingClickIntervalMs.SetValue(conf["workingClickIntervalMs"])
		self.workingClickStartDelayMs.SetValue(conf["workingClickStartDelayMs"])
		self.promptSubmissionClick.SetValue(conf["promptSubmissionClick"])
		self.monitoringFocusClicks.SetValue(conf["monitoringFocusClicks"])
		self.maximumBusyMinutes.SetValue(conf["maximumBusyMinutes"])
		self._categoryEnabledValues = {
			key: bool(conf[key]) for key, category, label in self._activityCategories
		}
		self._categoryOutputValues = {
			category: str(conf[CATEGORY_OUTPUT_CONFIG[category]])
			for key, category, label in self._activityCategories
		}
		for index in range(len(self._activityCategories)):
			self._refreshActivityCategoryDisplay(index)
		self._activityCategorySelection = max(0, self.activityCategory.GetSelection())
		self._loadActivityCategory(self._activityCategorySelection)
		self._announcementEdits = {key: str(conf[key]) for category, key, label, message in PREVIEW_ITEMS}
		selected = self._selectedPreview()
		self.announcementText.SetValue(self._announcementEdits[selected[1]])
		self._previousPreviewSelection = self.previewItem.GetSelection()
		self._updateProfileSummary()

	def _onResetSpeechSettings(self, evt):
		self.verbosity.SetSelection(VERBOSITY_CHOICES.index("full"))
		self.fullSpeechProfile.SetSelection(FULL_SPEECH_PROFILE_CHOICES.index("developer"))
		self.minimalSpeechProfile.SetSelection(MINIMAL_SPEECH_PROFILE_CHOICES.index("balanced"))
		self.commandPunctuation.SetSelection(COMMAND_PUNCTUATION_CHOICES.index("enhanced"))
		self.maximumSpokenCommandCharacters.SetValue(240)
		self.redactSensitive.SetValue(False)
		self._updateProfileSummary()
		ui.message(_("Speech profile settings reset. Select OK to save."))

	def onSave(self):
		conf = _settings()
		self._storeCurrentAnnouncementEdit()
		self._storeActivityCategory()
		conf["verbosity"] = VERBOSITY_CHOICES[self.verbosity.GetSelection()]
		conf["fullSpeechProfile"] = FULL_SPEECH_PROFILE_CHOICES[self.fullSpeechProfile.GetSelection()]
		conf["minimalSpeechProfile"] = MINIMAL_SPEECH_PROFILE_CHOICES[self.minimalSpeechProfile.GetSelection()]
		conf["brailleDetail"] = BRAILLE_DETAIL_CHOICES[self.brailleDetail.GetSelection()]
		conf["interruptUrgentSpeech"] = self.interruptUrgentSpeech.IsChecked()
		conf["commandPunctuation"] = COMMAND_PUNCTUATION_CHOICES[self.commandPunctuation.GetSelection()]
		conf["maximumSpokenCommandCharacters"] = self.maximumSpokenCommandCharacters.GetValue()
		for name in (
			"speech", "braille", "protectBrailleReading", "redactSensitive", "completionSound",
			"enableMessageList", "announceSuggestionMenus",
			"diagnosticLogging", "announceHeartbeat", "announceEmbeddedBrowserProgress",
		):
			conf[name] = getattr(self, name).IsChecked()
		if not conf["enableMessageList"] and _activePluginInstance is not None:
			dialog = _activePluginInstance._messageListDialog
			if dialog is not None:
				plugin = _activePluginInstance

				def closeMessageList():
					# The user may close the list before this runs, destroying the dialog.
					if plugin._messageListDialog is dialog:
						dialog.Close()
				wx.CallAfter(closeMessageList)
		conf["soundWhenSpeechUnavailable"] = self.progressSounds.IsChecked()
		conf["progressSoundStyle"] = SOUND_STYLE_CHOICES[self.progressSoundStyle.GetSelection()]
		conf["clickVolume"] = CLICK_VOLUME_CHOICES[self.clickVolume.GetSelection()]
		conf["continuousWorkingClicks"] = self.continuousWorkingClicks.IsChecked()
		conf["workingClickIntervalMs"] = self.workingClickIntervalMs.GetValue()
		conf["workingClickStartDelayMs"] = self.workingClickStartDelayMs.GetValue()
		conf["promptSubmissionClick"] = self.promptSubmissionClick.IsChecked()
		conf["monitoringFocusClicks"] = self.monitoringFocusClicks.IsChecked()
		conf["maximumBusyMinutes"] = self.maximumBusyMinutes.GetValue()
		for key, value in self._announcementEdits.items():
			conf[key] = value.strip()
		for name, value in self._categoryEnabledValues.items():
			conf[name] = value
		for category, value in self._categoryOutputValues.items():
			conf[CATEGORY_OUTPUT_CONFIG[category]] = value
		conf["workingIntervalSeconds"] = self.workingIntervalSeconds.GetValue()
		conf["idlePollMs"] = self.idlePollMs.GetValue()
		conf["supportedAppNames"] = mergeSupportedAppNames(self.supportedAppNames.GetValue())


class _SplitConversationScanInfo:
	"""Expose the sidebar and newest conversation without the middle transcript."""

	def __init__(self, head, tail):
		self._head = head
		self._tail = tail

	def getTextWithFields(self):
		yield from self._head.getTextWithFields()
		# A None sentinel resets transcript-only parsing state between disjoint ranges.
		yield None
		yield from self._tail.getTextWithFields()


def _scanProviderInfo(info):
	"""Resolve NVDA's known document proxy without changing its ownership."""
	seen = set()
	for _ in range(8):
		if not isinstance(info, RootProxyTextInfo):
			return info
		if id(info) in seen:
			break
		seen.add(id(info))
		info = info.innerTextInfo
	raise NotImplementedError("Cyclic or excessive text provider proxies")


def _extendScanStart(info, count):
	"""Extend a private scan range without per-character Chromium RPC calls."""
	info = _scanProviderInfo(info)
	if isinstance(info, textInfos.offsets.OffsetsTextInfo):
		oldStart = info._startOffset
		info._startOffset = max(0, oldStart - count)
		return info._startOffset - oldStart
	if isinstance(info, UIATextInfo):
		# Bind the base implementation deliberately. Web UIA's override walks
		# replaced content one character at a time; the base moves one endpoint
		# with a single native TextRange call and normalizes its return sign.
		return UIATextInfo.move(info, textInfos.UNIT_CHARACTER, -count, endPoint="start")
	raise NotImplementedError("Safe bounded scans require an offset text provider")


def _conversationScanInfo(buffer):
	"""Bound the expensive virtual-buffer traversal in large conversations."""
	whole = buffer.makeTextInfo(textInfos.POSITION_ALL)
	provider = _scanProviderInfo(whole)
	if isinstance(provider, textInfos.offsets.OffsetsTextInfo):
		# Character movement can issue a provider call for every character.
		# Construct ranges from this snapshot's offsets instead; do not retain
		# them across polls, because Chromium replaces its buffer while streaming.
		start, end = provider._startOffset, provider._endOffset
		if end - start <= CONVERSATION_SCAN_HEAD_CHARACTERS + CONVERSATION_SCAN_TAIL_CHARACTERS:
			return whole
		head = buffer.makeTextInfo(textInfos.offsets.Offsets(
			start, start + CONVERSATION_SCAN_HEAD_CHARACTERS,
		))
		tail = buffer.makeTextInfo(textInfos.offsets.Offsets(
			end - CONVERSATION_SCAN_TAIL_CHARACTERS, end,
		))
		return _SplitConversationScanInfo(head, tail)
	if isinstance(provider, UIATextInfo):
		head = whole.copy()
		head.collapse()
		UIATextInfo.move(_scanProviderInfo(head), textInfos.UNIT_CHARACTER, CONVERSATION_SCAN_HEAD_CHARACTERS, endPoint="end")
		tail = whole.copy()
		tail.collapse(end=True)
		_extendScanStart(tail, CONVERSATION_SCAN_TAIL_CHARACTERS)
		if head.compareEndPoints(tail, "endToStart") >= 0:
			return whole
		return _SplitConversationScanInfo(head, tail)
	# Unknown providers remain fail-closed; do not invoke generic movement.
	raise NotImplementedError("Safe bounded scans require an offset text provider")


def _isChatGPTObject(obj):
	try:
		appName = str(getattr(getattr(obj, "appModule", None), "appName", "") or "").lower()
		supported = {name.strip().lower() for name in _settings()["supportedAppNames"].split(",") if name.strip()}
		return appName in supported
	except Exception:
		return False


def _conversationModeForObject(obj):
	"""Return the active conversation mode while excluding nested browser documents."""
	if not _isChatGPTObject(obj):
		return ""
	current = obj
	documentNames = []
	for _ in range(20):
		try:
			if current is None:
				break
			roleName = _roleName(current)
			if roleName == "document":
				documentNames.append(getattr(current, "name", ""))
			current = getattr(current, "parent", None)
		except Exception:
			return ""
	return conversationModeFromDocumentNames(documentNames)


def _isConversationObject(obj):
	return bool(_conversationModeForObject(obj))


_otherSuggestionMenuAddon = None


def _otherSuggestionMenuAddonRunning():
	"""True when another add-on, such as Slash Menus, already reads "/" and "@" menus."""
	global _otherSuggestionMenuAddon
	if _otherSuggestionMenuAddon is None:
		_otherSuggestionMenuAddon = ""
		try:
			for addon in addonHandler.getRunningAddons():
				name = str(getattr(addon, "name", "") or "")
				summary = str(getattr(addon, "manifest", {}).get("summary", "") or "")
				if name != "codexStatusAnnouncer" and "slash" in (name + " " + summary).casefold():
					_otherSuggestionMenuAddon = summary or name
					log.info("ChatGPT Desktop Access leaves suggestion menus to the %s add-on", _otherSuggestionMenuAddon)
					break
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not list running add-ons", exc_info=True)
	return bool(_otherSuggestionMenuAddon)


def _sameNVDAObject(first, second):
	"""Compare NVDA objects by the control they represent.

	NVDA creates a new object each time it looks a control up, so ``is`` is
	false for two lookups of the same dialog. NVDA's own equality compares the
	underlying control. Chromium wrappers can also be matched by their IA2
	identity within the same window.
	"""
	if first is None or second is None:
		return False
	if first is second:
		return True
	try:
		if first == second:
			return True
		uniqueID = getattr(first, "IA2UniqueID", None)
		if not uniqueID or uniqueID != getattr(second, "IA2UniqueID", None):
			return False
		firstWindow = getattr(first, "IA2WindowHandle", None) or getattr(first, "windowHandle", None)
		secondWindow = getattr(second, "IA2WindowHandle", None) or getattr(second, "windowHandle", None)
		return bool(firstWindow) and firstWindow == secondWindow
	except Exception:
		return False


def _pressControl(obj):
	"""Press a ChatGPT control, including ones UI Automation exposes only as expandable.

	In NVDA's UI Automation document, buttons such as Add files and more have no
	Invoke pattern, so NVDA's own doAction raises NotImplementedError. Those are
	expanded or collapsed, or toggled, through UI Automation instead.
	"""
	try:
		obj.doAction()
		return
	except NotImplementedError:
		element = getattr(obj, "UIAElement", None)
		if element is None:
			raise
	import UIAHandler
	pattern = obj._getUIAPattern(UIAHandler.UIA_ExpandCollapsePatternId, UIAHandler.IUIAutomationExpandCollapsePattern)
	if pattern:
		# 0 is collapsed; 1, 2 and 3 are expanded, partly expanded, and a leaf.
		if int(pattern.CurrentExpandCollapseState) == 0:
			pattern.Expand()
		else:
			pattern.Collapse()
		return
	pattern = obj._getUIAPattern(UIAHandler.UIA_TogglePatternId, UIAHandler.IUIAutomationTogglePattern)
	if pattern:
		pattern.Toggle()
		return
	raise NotImplementedError("No way to press this UI Automation control")


def _isVirtualBufferDocument(buffer):
	"""True for NVDA's usual Chromium document; False for its UI Automation one.

	Searching NVDA's UI Automation document takes seconds, so the Add files and
	more popup is then read from UI Automation directly.
	"""
	try:
		from virtualBuffers import VirtualBuffer
	except Exception:
		return True
	return isinstance(buffer, VirtualBuffer)


def _isCodexPromptObject(obj):
	"""Recognize the prompt without relying solely on a sometimes-stale document ancestor."""
	try:
		if obj.role != Role.EDITABLETEXT or not _isChatGPTObject(obj):
			return False
	except Exception:
		return False
	labels = []
	for attribute in ("name", "placeholder", "description"):
		try:
			labels.append(getattr(obj, attribute, ""))
		except Exception:
			continue
	if any(isCodexPromptLabel(label) for label in labels):
		return True
	if _isPromptEditor(obj):
		return True
	return _isConversationObject(obj)


def _domClassNames(obj):
	"""Return the web page class names of a ChatGPT control, or an empty string."""
	try:
		attributes = getattr(obj, "IA2Attributes", None) or {}
		if attributes.get("class"):
			return str(attributes["class"])
		element = getattr(obj, "UIAElement", None)
		return str(element.CurrentClassName or "") if element is not None else ""
	except Exception:
		return ""


def _isPromptEditor(obj):
	"""Recognize ChatGPT's prompt editor, a ProseMirror field, whatever its label says."""
	return CHATGPT_PROMPT_EDITOR_CLASS in _domClassNames(obj).split()


def _roleName(obj):
	role = getattr(obj, "role", None)
	name = getattr(role, "name", "")
	if name:
		return str(name).casefold()
	return str(role or "").rsplit(".", 1)[-1].casefold()


def _switchControlMode(obj):
	"""Read one selector control; never infer a mode from a nearby chat title."""
	name = getattr(obj, "name", "")
	nameKey = " ".join(str(name or "").casefold().split())
	# Prompt and streamed-message events are hot paths. Do not ask their Chromium
	# providers for description or states unless the name resembles a selector.
	if nameKey and nameKey not in ("chatgpt", "codex", "mode selector") and not nameKey.startswith(
		("switch mode", "current mode:"),
	):
		return ""
	role = _roleName(obj)
	if role not in ("button", "menubutton", "menu button"):
		return ""
	mode = conversationModeFromSwitchControl(name, role=role)
	if mode:
		return mode
	try:
		description = getattr(obj, "description", "")
	except Exception:
		description = ""
	mode = conversationModeFromSwitchControl(name, description, role)
	if mode or nameKey not in ("chatgpt", "codex"):
		return mode
	try:
		states = getattr(obj, "states", ()) or ()
		identifier = getattr(obj, "automationID", "") or getattr(obj, "automationId", "")
	except Exception:
		return ""
	return conversationModeFromSwitchControl(
		name, description, role,
		bool({State.EXPANDED, State.COLLAPSED} & set(states)), identifier,
	)


def _isDefunctObject(obj):
	"""Return whether NVDA has marked an object as no longer available."""
	try:
		return State.DEFUNCT in (getattr(obj, "states", ()) or ())
	except Exception:
		return False


def _isEmbeddedBrowserObject(obj):
	"""Recognize an explicit browser container or a web document nested in ChatGPT."""
	if not _isChatGPTObject(obj):
		return False
	cached = getattr(obj, "_codexEmbeddedBrowserDetected", None)
	if cached is not None:
		return bool(cached)
	# The primary prompt and its known toolbar controls are never embedded-browser
	# content. Reject them before any Chromium ancestor access; these objects are
	# recreated frequently while typing and a negative ancestry walk blocks NVDA's
	# main thread and delays queued Braille input.
	if _isCodexPromptObject(obj) or promptControlKind(getattr(obj, "name", "")):
		try:
			obj._codexEmbeddedBrowserDetected = False
		except Exception:
			pass
		return False
	current = obj
	ancestorRoles = []
	for _ in range(18):
		if current is None:
			break
		try:
			roleName = _roleName(current)
			ancestorRoles.append(roleName)
			if isEmbeddedBrowserContainerRole(roleName) and isEmbeddedBrowserContainerText(
				getattr(current, "name", ""),
			):
				try:
					obj._codexEmbeddedBrowserDetected = True
				except Exception:
					pass
				return True
			if isEmbeddedBrowserDocumentStructure(*ancestorRoles):
				try:
					obj._codexEmbeddedBrowserDetected = True
				except Exception:
					pass
				return True
			current = getattr(current, "parent", None)
		except Exception:
			return False


	try:
		obj._codexEmbeddedBrowserDetected = False
	except Exception:
		pass
	return False


def _isNativeCommonDialogObject(obj):
	"""Recognize a Windows file chooser without traversing its COM parent chain."""
	try:
		handle = int(getattr(obj, "windowHandle", 0) or 0)
		if not handle:
			return False
		root = int(winUser.getAncestor(handle, winUser.GA_ROOT) or handle)
		return str(winUser.getClassName(root) or "").casefold() == "#32770"
	except Exception:
		return False


class CodexPromptControlOverlay:
	"""Add concise help to recognized native controls beside the Codex prompt."""

	def _get_description(self):
		descriptions = {
			"files": _("Opens attachment options. In Codex, Enter or Space can move to the native attachment menu when available."),
			"model": _("Opens the model and reasoning choices. Press Enter or Space to open, then use the native menu to choose."),
			"permissions": _("Opens permission choices. Press Enter or Space to open, then use arrow keys and Enter."),
		}
		nativeDescription = str(getattr(self, "_codexNativeDescription", "") or "").strip()
		helpDescription = descriptions.get(getattr(self, "_codexPromptControlKind", ""), "")
		if nativeDescription and helpDescription.casefold() not in nativeDescription.casefold():
			return _("{native} {help}").format(native=nativeDescription, help=helpDescription)
		return nativeDescription or helpDescription


class CodexPromptEditableTextOverlay:
	"""Let ChatGPT handle Enter without NVDA inspecting its replaced prompt object."""

	# ChatGPT submits Enter instead of inserting a newline, then immediately replaces
	# its content-editable object. NVDA's generic multiline-edit Enter script tries to
	# inspect that stale IA2 object and can play the log-error sound even though the
	# message was sent. Disabling only the generic newline-announcement binding leaves
	# physical Enter, numpad Enter, Shift+Enter, and Braille-emulated keys native.
	announceNewLineText = False


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("ChatGPT Desktop Access")

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		"""Enhance known controls without adding or intercepting gestures."""
		try:
			if not _isChatGPTObject(obj):
				return
			# Known prompt-toolbar controls are much more common than embedded
			# browser controls. Handle them without an unnecessary ancestor walk.
			if obj.role in (Role.BUTTON, Role.COMBOBOX):
				kind = promptControlKind(getattr(obj, "name", ""))
				if kind:
					obj._codexPromptControlKind = kind
					obj._codexNativeDescription = getattr(obj, "description", "")
					clsList.insert(0, CodexPromptControlOverlay)
					return
			# The prompt submits Enter rather than inserting a newline. Apply the
			# prompt-specific overlay before EditableTextBase initializes so NVDA does
			# not bind its generic caret_newLine script to this transient Chromium node.
			if obj.role == Role.EDITABLETEXT and _isCodexPromptObject(obj):
				clsList.insert(0, CodexPromptEditableTextOverlay)
				return
		except Exception:
			return

	def __init__(self):
		global _activePluginInstance
		self._registeredAppAliases = []
		super().__init__()
		for executableName, appModuleName in APP_MODULE_ALIASES:
			appModuleHandler.registerExecutableWithAppModule(executableName, appModuleName)
			self._registeredAppAliases.append(executableName)
		_activePluginInstance = self
		_repairConfiguration()
		migratedGestures = _migrateApplicationGestureMappings()
		if migratedGestures:
			log.info("ChatGPT Desktop Access migrated %d application gesture mappings", migratedGestures)
		self._lastMessage = ""
		self._lastMessageAt = 0.0
		self._lastSpeechMessage = ""
		self._lastSpeechMessageAt = 0.0
		self._lastBrailleMessage = ""
		self._lastBrailleMessageAt = 0.0
		self._lastLabel = ""
		self._latestMessage = ""
		self._latestFullMessage = ""
		self._haveBaseline = False
		self._buffer = None
		self._nativeTimerObserver = BufferUpdateObserver(self._observeNativeTaskTimer)
		self._nativeTimerDocument = ""
		self._nativeTimerSeconds = None
		self._nativeTimerTurn = None
		self._nativeHeartbeatAt = None
		self._nativeClickAt = None
		self._unsupportedScanBuffer = None
		self._conversationWindowHandle = 0
		self._conversationWindowUnavailableAt = 0.0
		self._conversationClosedAt = 0.0
		self._conversationMode = ""
		self._conversationModeObserved = False
		self._conversationModeChangedAt = 0.0
		self._lastConversationModeProbeAt = 0.0
		self._modeProbeStartedAt = 0.0
		self._conversationModeProbeGeneration = 0
		self._conversationModeProbePendingGeneration = 0
		self._conversationModeProbeActivationGeneration = 0
		self._conversationModeObservedAt = 0.0
		self._modeSelectorOpenedAt = 0.0
		self._attachmentMenuActiveAt = 0.0
		self._attachmentMenuLastClosedAt = 0.0
		self._attachmentMenuButtonFocusedAt = 0.0
		self._lastAttachmentMenuItem = ""
		self._lastAttachmentMenuItemAt = 0.0
		self._attachmentActivationAt = 0.0
		self._attachmentInputCandidateAt = 0.0
		self._attachmentInputCandidateWindowHandle = 0
		self._attachmentSourcePendingButton = None
		self._attachmentSourceFocusTimer = None
		self._attachmentDiagnostics = AttachmentMenuDiagnostics(self)
		self._attachmentMenuDialog = None
		self._attachmentMenuButton = None
		self._attachmentMenuWindowHandle = 0
		self._monitoringAnnounced = False
		self._lastNoStatusLogAt = 0.0
		self._active = False
		self._busy = False
		self._busyTimeout = None
		self._backgroundPulseCount = 0
		self._commentaryOffsets = {}
		self._paused = False
		self._speechHistory = AnnouncementHistory(20)
		self._brailleHistory = AnnouncementHistory(20)
		self._history = self._speechHistory
		self._activeCategory = "other"
		self._appFocusState = None
		self._lastExternalFocusObject = None
		self._lastExternalFocusWindowHandle = 0
		self._closeFocusRecoveryTimer = None
		self._closeFocusRecoveryGeneration = 0
		self._promptHadText = None
		self._promptDraftText = ""
		self._recentChatMessages = ()
		self._recentChatMessagesBuffer = None
		self._conversationMessages = ()
		self._messageListDialog = None
		self._messageListRefreshPending = False
		self._latestUserMessageNumber = None
		self._pendingUserMessageIncrease = False
		self._stopControlVisible = False
		self._lastStateReason = "startup"
		self._lastSubmissionSignal = "none"
		self._documentSwitchCount = 0
		self._lastInspectionError = "none"
		self._lastUnknownButtons = ()
		self._lastUnknownButtonsAt = 0.0
		self._lastRejectedBufferLogAt = 0.0
		self._lastDeferredHistoryLog = ()
		self._lastDeferredHistoryLogAt = 0.0
		self._lastPollAt = 0.0
		self._nextPollAt = 0.0
		self._bufferDirty = True
		self._lastBufferInspectionAt = 0.0
		self._lastBufferInspectionSeconds = 0.0
		self._lastScannedLabel = ""
		self._bufferInspectionCount = 0
		self._operationTimings = {}
		self._skippedBufferInspectionCount = 0
		self._promptTypingUntil = 0.0
		self._conversationNavigationUntil = 0.0
		self._conversationActivatedAt = 0.0
		self._conversationEntryCorrectionGeneration = 0
		self._promptFocused = False
		self._brailleCompositionActive = False
		self._lastBrailleTextInjectionAt = 0.0
		self._brailleCaretMoveSuppressions = 0
		self._suppressedConversationUpdates = 0
		self._promptInspectionTimer = None
		self._pendingPromptObject = None
		self._lastPromptObject = None
		self._promptSubmissionGestureQueued = False
		self._promptSubmissionDraftQueued = ""
		self._inputGestureObserverRegistered = False
		self._latestResponseMarker = None
		self._responseMarkerInitialized = False
		self._pendingResponseCompletionAt = 0.0
		self._submittedTurnUnconfirmedAt = 0.0
		self._chatHistoryDialog = None
		self._pendingChatHistoryAction = None
		self._chatHistoryActionTimer = None
		self._chatHistoryExpansionTimer = None
		self._pendingChatHistoryExpansion = None
		self._chatHistoryOpenTimer = None
		self._pendingChatHistoryOpen = None
		self._chatActionRetryTimer = None
		self._pendingDirectChatAction = None
		self._unarchiveFocusTimer = None
		self._unarchiveFocusAttempts = 0
		self._popupFocusTimer = None
		self._pendingPopupDialog = None
		self._pendingPopupDialogWindowHandle = 0
		self._lastFocusedPopupDialog = None
		self._usageLimitActive = False
		self._lastUsageLimitNotice = ""
		self._pluginProgressBuckets = {}
		self._pluginProgressOwnedBusy = set()
		self._embeddedBrowserFocused = False
		self._embeddedBrowserLoadingPercent = None
		self._embeddedBrowserLoading = False
		self._embeddedBrowserBusySeen = False
		self._embeddedBrowserLoadIdentity = ""
		self._embeddedBrowserCompletedIdentity = ""
		self._embeddedBrowserLoadGeneration = 0
		self._embeddedBrowserLoadTimer = None
		self._lastEmbeddedBrowserTitle = ""
		self._lastEmbeddedBrowserNotice = ""
		self._lastEmbeddedBrowserNoticeAt = 0.0
		self._embeddedBrowserProgressBuckets = {}
		self._pendingOpenedChatTitle = ""
		self._lastChatOpened = None
		self._pendingOpenedChatAt = 0.0
		self._chatHistoryCaches = {"chatgpt": (), "codex": ()}
		self._ambiguousRecentChatTitles = {"chatgpt": set(), "codex": set()}
		self._chatHistoryCacheCurrent = {"chatgpt": False, "codex": False}
		self._pendingChatHistorySnapshots = {"chatgpt": None, "codex": None}
		self._pendingChatHistorySnapshotAt = {"chatgpt": 0.0, "codex": 0.0}
		self._chatHistoryMoreAvailable = {"chatgpt": False, "codex": False}
		self._recentHistoryShowMoreOrdinals = {"chatgpt": 0, "codex": 0}
		self._unifiedRecentCounts = {"chatgpt": 0, "codex": 0}
		self._chatHistoryScanGenerations = {"chatgpt": 0, "codex": 0}
		self._activeCodexTitlesCache = ()
		self._activeCodexTitlesSourceSignature = None
		self._recentClassificationSummaries = {"chatgpt": None, "codex": None}
		self._archivedChatHistoryCaches = {"chatgpt": (), "codex": ()}
		self._archivedChatHistoryLoaded = {"chatgpt": False, "codex": False}
		self._archivedChatIds = {"chatgpt": {}, "codex": {}}
		self._chatHistoryDialogMode = ""
		self._voiceControlConfirmationTimer = None
		self._pendingVoiceControlConfirmation = None
		self._whatsNewTimer = None
		log.info(
			"ChatGPT Desktop Access %s loaded (verbosity=%s, fullProfile=%s, minimalProfile=%s, brailleDetail=%s, soundStyle=%s)",
			ADDON_VERSION,
			_settings()["verbosity"], _settings()["fullSpeechProfile"],
			_settings()["minimalSpeechProfile"], _settings()["brailleDetail"], _settings()["progressSoundStyle"],
		)
		if CodexStatusAnnouncerSettingsPanel not in NVDASettingsDialog.categoryClasses:
			NVDASettingsDialog.categoryClasses.append(CodexStatusAnnouncerSettingsPanel)
		try:
			inputCore.decide_executeGesture.register(self._observeInputGesture)
			self._inputGestureObserverRegistered = True
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not observe Braille input gestures", exc_info=True)
		self._timer = wx.CallLater(100, self._poll)
		self._nextPollAt = time.monotonic() + 0.1
		self._whatsNewTimer = wx.CallLater(1500, self._showWhatsNewIfNeeded)

	def terminate(self):
		global _activePluginInstance
		self._nativeTimerObserver.detach()
		self._clearNativeTaskTimer()
		if self._busyTimeout is not None:
			self._busyTimeout.Stop()
			self._busyTimeout = None
		_stopProgressSounds()
		self._conversationModeProbeGeneration += 1
		self._conversationModeProbePendingGeneration = 0
		self._conversationModeProbeActivationGeneration = 0
		self._modeProbeStartedAt = 0.0
		self._modeSelectorOpenedAt = 0.0
		self._resetAttachmentMenuTracking()
		self._cancelAttachmentSourceFocus()
		self._cancelCloseFocusRecovery()
		if self._inputGestureObserverRegistered:
			try:
				inputCore.decide_executeGesture.unregister(self._observeInputGesture)
			except Exception:
				log.debugWarning("ChatGPT Desktop Access could not remove its Braille input observer", exc_info=True)
			self._inputGestureObserverRegistered = False
		if self._timer:
			self._timer.Stop()
			self._timer = None
		self._nextPollAt = 0.0
		if self._whatsNewTimer:
			self._whatsNewTimer.Stop()
			self._whatsNewTimer = None
		if self._promptInspectionTimer:
			self._promptInspectionTimer.Stop()
			self._promptInspectionTimer = None
		self._pendingPromptObject = None
		if self._embeddedBrowserLoadTimer:
			self._embeddedBrowserLoadTimer.Stop()
			self._embeddedBrowserLoadTimer = None
		if self._chatHistoryDialog:
			self._chatHistoryDialog.Destroy()
			self._chatHistoryDialog = None
			gui.mainFrame.postPopup()
		if self._messageListDialog:
			self._messageListDialog.Destroy()
			self._messageListDialog = None
			gui.mainFrame.postPopup()
		if self._attachmentMenuDialog:
			self._attachmentMenuDialog.Destroy()
			self._attachmentMenuDialog = None
			gui.mainFrame.postPopup()
		if self._chatHistoryActionTimer:
			self._chatHistoryActionTimer.Stop()
			self._chatHistoryActionTimer = None
		self._cancelPendingChatHistoryOpen()
		self._cancelChatHistoryExpansion()
		if self._chatActionRetryTimer:
			self._chatActionRetryTimer.Stop()
			self._chatActionRetryTimer = None
		self._pendingDirectChatAction = None
		if self._unarchiveFocusTimer:
			self._unarchiveFocusTimer.Stop()
			self._unarchiveFocusTimer = None
		if self._popupFocusTimer:
			self._popupFocusTimer.Stop()
			self._popupFocusTimer = None
		self._cancelVoiceControlConfirmation()
		self._pendingPopupDialog = None
		self._pendingPopupDialogWindowHandle = 0
		self._lastFocusedPopupDialog = None
		self._pluginProgressBuckets.clear()
		self._pluginProgressOwnedBusy.clear()
		self._embeddedBrowserProgressBuckets.clear()
		self._pendingChatHistoryAction = None
		try:
			NVDASettingsDialog.categoryClasses.remove(CodexStatusAnnouncerSettingsPanel)
		except ValueError:
			pass
		for executableName in reversed(self._registeredAppAliases):
			try:
				appModuleHandler.unregisterExecutable(executableName)
			except Exception:
				log.debugWarning(
					"ChatGPT Desktop Access could not unregister app-module alias for %s",
					executableName,
					exc_info=True,
				)
		self._registeredAppAliases.clear()
		if _activePluginInstance is self:
			_activePluginInstance = None
		super().terminate()

	def _schedulePoll(self, delay=150, requestInspection=True):
		if requestInspection:
			self._bufferDirty = True
		now = time.monotonic()
		actualDelay = coalescedPollDelay(
			delay, now - self._lastPollAt if self._lastPollAt else float("inf"),
		)
		requestedDeadline = now + actualDelay / 1000.0
		if self._timer and not shouldReplaceScheduledPoll(self._nextPollAt, requestedDeadline):
			return
		if self._timer:
			self._timer.Stop()
		self._timer = wx.CallLater(actualDelay, self._poll)
		self._nextPollAt = requestedDeadline

	def _showWhatsNewIfNeeded(self):
		self._whatsNewTimer = None
		conf = _settings()
		if conf["lastShownVersion"] == ADDON_VERSION:
			return
		_showBrowseableMessageAtTop(
			CURRENT_RELEASE_NOTES, _("ChatGPT Desktop Access — what's new"),
		)
		conf["lastShownVersion"] = ADDON_VERSION
		conf["welcomeShown"] = True
		try:
			config.conf.save()
		except Exception:
			log.debugWarning("Unable to save the last displayed add-on version", exc_info=True)

	def _resetTaskState(self, reason):
		self._bindNativeTaskTimer(self._buffer)
		self._setBusy(False, reason)
		self._resetAttachmentMenuTracking()
		self._cancelAttachmentSourceFocus()
		self._lastLabel = ""
		self._haveBaseline = False
		self._commentaryOffsets.clear()
		self._promptHadText = None
		self._promptDraftText = ""
		self._promptSubmissionDraftQueued = ""
		self._recentChatMessages = ()
		self._recentChatMessagesBuffer = None
		self._conversationMessages = ()
		self._messageListRefreshPending = False
		if self._messageListDialog:
			self._messageListDialog.Close()
		self._conversationActivatedAt = 0.0
		self._conversationEntryCorrectionGeneration += 1
		self._promptTypingUntil = 0.0
		self._conversationNavigationUntil = 0.0
		self._brailleCompositionActive = False
		if self._promptInspectionTimer:
			self._promptInspectionTimer.Stop()
			self._promptInspectionTimer = None
		self._pendingPromptObject = None
		self._lastPromptObject = None
		self._bufferDirty = True
		self._lastScannedLabel = ""
		self._latestUserMessageNumber = None
		self._pendingUserMessageIncrease = False
		self._stopControlVisible = False
		self._lastUnknownButtons = ()
		self._lastUnknownButtonsAt = 0.0
		self._latestResponseMarker = None
		self._responseMarkerInitialized = False
		self._pendingResponseCompletionAt = 0.0
		self._submittedTurnUnconfirmedAt = 0.0
		self._usageLimitActive = False
		self._lastUsageLimitNotice = ""
		self._speechHistory.clear()
		self._brailleHistory.clear()
		self._latestMessage = ""
		self._latestFullMessage = ""
		self._lastMessage = ""
		self._lastMessageAt = 0.0
		self._lastSpeechMessage = ""
		self._lastSpeechMessageAt = 0.0
		self._lastBrailleMessage = ""
		self._lastBrailleMessageAt = 0.0
		self._activeCategory = "other"

	def _recordHistory(self, speechMessage, brailleMessage=None):
		brailleText = str(brailleMessage if brailleMessage is not None else speechMessage or "").strip()
		# Keep navigation aligned even when an Essential speech profile intentionally
		# omits a live event; explicit history review may still expose its details.
		self._speechHistory.add(str(speechMessage or brailleText).strip())
		self._brailleHistory.add(brailleText or str(speechMessage or "").strip())

	def _historyMessage(self, offset):
		if not self._speechHistory and not self._brailleHistory:
			ui.message(_("No activity announcement history is available"))
			return
		speechMessage = self._speechHistory.move(offset) if self._speechHistory else ""
		brailleMessage = self._brailleHistory.move(offset) if self._brailleHistory else speechMessage
		conf = _settings()
		_send(
			speechMessage or brailleMessage, conf["speech"] and bool(speechMessage), conf["braille"],
			None, False, brailleMessage=brailleMessage,
		)

	def _newChatMessageFieldCollector(self, stopAtPrompt=True):
		interactiveRoles = {
			Role.BUTTON, Role.EDITABLETEXT, Role.COMBOBOX, Role.LIST, Role.TREEVIEW,
			Role.CHECKBOX, Role.RADIOBUTTON,
		}
		invisible = getattr(State, "INVISIBLE", None)
		promptIdentifier = None
		if stopAtPrompt:
			prompt = self._pendingPromptObject or self._lastPromptObject
			if prompt is not None:
				try:
					promptIdentifier = self._buffer.getIdentifierFromNVDAObject(prompt)
				except Exception:
					# UIA and stale IA2 objects can lack a virtual-buffer identifier.
					pass
		return ChatMessageFieldCollector(
			interactiveRoles, Role.EDITABLETEXT, isCodexPromptLabel,
			((invisible,) if invisible is not None else ()), stopAtPrompt,
			headingRole=Role.HEADING, focusableState=State.FOCUSABLE, promptIdentifier=promptIdentifier,
		)

	def _cacheRecentChatMessages(self, messages):
		"""Publish one active-branch snapshot for immediate Control+number review."""
		cleaned = []
		for speaker, text in messages or ():
			speaker = str(speaker or "").casefold()
			text = " ".join(str(text or "").split())
			if speaker in ("user", "assistant") and text:
				item = (speaker, text)
				if not cleaned or cleaned[-1] != item:
					cleaned.append(item)
		wasEmpty = not self._conversationMessages
		self._conversationMessages = tuple(cleaned[-MESSAGE_LIST_LIMIT:])
		self._recentChatMessages = self._conversationMessages[-10:]
		self._recentChatMessagesBuffer = self._buffer
		if self._messageListDialog and (
			(wasEmpty and self._conversationMessages) or self._messageListRefreshPending
		):
			self._messageListRefreshPending = False
			self._messageListDialog.updateMessages(self._conversationMessages)
			ui.message(_("{count} conversation messages loaded").format(count=len(self._conversationMessages)))

	def _appendRecentChatMessage(self, speaker, text):
		"""Add a locally observed turn without waiting for Chromium to refresh."""
		text = " ".join(str(text or "").split())
		if not text or speaker not in ("user", "assistant"):
			return
		messages = list(
			self._conversationMessages
			if self._recentChatMessagesBuffer is self._buffer else ()
		)
		item = (speaker, text)
		if not messages or messages[-1] != item:
			messages.append(item)
		self._cacheRecentChatMessages(messages)

	def _chatMessagesFromInfo(self, info, stopAtPrompt=True, limit=10):
		collector = self._newChatMessageFieldCollector(stopAtPrompt)
		accumulator = ChatMessageAccumulator(limit)
		for item in info.getTextWithFields():
			for token in collector.feed(item):
				accumulator.feed(token)
		return accumulator.messages(), collector.promptReached

	def _currentChatMessages(self):
		"""Return the cached active-branch turns, scanning once only before a cache exists."""
		focus = api.getFocusObject()
		if not _isChatGPTObject(focus):
			return ()
		self._rememberBuffer(focus, allowUnclassifiedConversation=True)
		if not self._buffer:
			return ()
		if self._recentChatMessagesBuffer is self._buffer and len(self._recentChatMessages) >= 10:
			return self._recentChatMessages
		self._cacheRecentChatMessages(self._activeBranchMessages(10))
		return self._recentChatMessages

	def _readNativeTaskTimer(self, includeThinking=False):
		buffer = self._buffer
		if buffer is None:
			return "", None
		prompt = self._findChatGPTPromptObject()
		try:
			info = buffer.makeTextInfo(prompt if prompt is not None else textInfos.POSITION_LAST)
			info.collapse()
		except Exception:
			info = buffer.makeTextInfo(textInfos.POSITION_LAST)
		_extendScanStart(info, RECENT_CHAT_INITIAL_SCAN_CHARACTERS)
		label = ""
		textField = {}
		timerObject = None
		pendingPrefix = ""
		turn = None
		thinking = False
		thinkingFields = []
		for item in info.getTextWithFields():
			if isinstance(item, str):
				lines = item.splitlines()
				sourceObject = (textField.get("ia2TextWindowHandle"), textField.get("ia2TextUniqueID"))
			elif item.command == "formatChange":
				textField = item.field or {}
				continue
			elif item.command == "controlStart":
				field = item.field or {}
				lines = [str(field.get("name") or "")]
				sourceObject = (field.get("controlIdentifier_docHandle"), field.get("controlIdentifier_ID"))
				if includeThinking:
					thinkingFields.append(
						bool(thinkingFields and thinkingFields[-1])
						or isNativeThinkingControl(field.get(ATTACHMENT_POPUP_CLASS_KEY)),
					)
				if chatMessageHeadingSpeaker(field, Role.HEADING, State.FOCUSABLE) == "user":
					label, timerObject, pendingPrefix = "", None, ""
					turn = sourceObject if all(sourceObject) else None
					thinking = False
			elif item.command == "controlEnd":
				if thinkingFields:
					thinkingFields.pop()
				continue
			else:
				continue
			for line in lines:
				if chatMessageSpeaker(line) == "user":
					label, timerObject, pendingPrefix = "", None, ""
					thinking = False
				if includeThinking and isResponseCompletionMarkerText(line):
					thinking = False
				if includeThinking and not thinking and isNativeThinkingLabel(line):
					thinking = bool(thinkingFields and thinkingFields[-1])
					if not thinking and all(sourceObject):
						# Some Chromium ranges expose the class only on the live object.
						try:
							obj = buffer.getNVDAObjectFromIdentifier(*map(int, sourceObject))
							thinking = isNativeThinkingControl(_domClassNames(obj)) or isNativeThinkingControl(
								_domClassNames(getattr(obj, "parent", None)),
							)
						except Exception:
							pass
				timer = nativeTaskTimer(line)
				if isinstance(item, str) and line.strip():
					if pendingPrefix and not timer:
						timer = nativeTaskTimer(f"{pendingPrefix} {line}")
					normalized = " ".join(line.casefold().split())
					pendingPrefix = normalized if normalized in NATIVE_TASK_TIMER_PREFIXES else ""
				if timer:
					label = timer
					timerObject = sourceObject
		if timerObject and all(timerObject):
			try:
				obj = buffer.getNVDAObjectFromIdentifier(*map(int, timerObject))
				current = nativeTaskTimer(getattr(obj, "name", "")) or nativeTaskTimer(getattr(obj, "value", ""))
				if current:
					label = current
			except Exception:
				# Some Chromium ranges expose only virtual-buffer text.
				pass
		if thinking and not label:
			label = "Thinking"
		return label, turn

	def _reportNativeTaskTimer(self):
		self._rememberBuffer(api.getFocusObject(), allowUnclassifiedConversation=True)
		try:
			label, _turn = self._readNativeTaskTimer(includeThinking=True)
		except NotImplementedError:
			label = ""
		if label == "Thinking":
			label = _("Thinking")
		elif nativeActiveTaskSeconds(label) is None:
			label = _("No active task timer")
		ui.message(label)

	def _bindNativeTaskTimer(self, buffer):
		self._clearNativeTaskTimer()
		self._nativeTimerDocument = ""
		self._nativeTimerObserver.attach(buffer)

	def _clearNativeTaskTimer(self):
		if self._nativeTimerSeconds is not None:
			_discardPendingActivitySounds()
		self._nativeTimerSeconds = None
		self._nativeTimerTurn = None
		self._nativeHeartbeatAt = None
		self._nativeClickAt = None
		self._backgroundPulseCount = 0

	def _observeNativeTaskTimer(self, buffer):
		if buffer is not self._buffer:
			return
		if not self._conversationWindowIsAvailable(self._conversationWindowHandle):
			self._clearNativeTaskTimer()
			return
		if self._attachmentMenuFlowActive() or self._brailleCompositionActive:
			return
		# Chromium may retain the same buffer when opening a different chat.
		document = buffer.rootNVDAObject.name or ""
		if document and document != self._nativeTimerDocument:
			if self._nativeTimerDocument:
				self._clearNativeTaskTimer()
				self._lastPromptObject = None
			self._nativeTimerDocument = document
		label, turn = self._readNativeTaskTimer()
		seconds = nativeActiveTaskSeconds(label)
		if seconds is None:
			self._clearNativeTaskTimer()
			return
		newTurn = turn and self._nativeTimerTurn and turn != self._nativeTimerTurn
		if self._nativeTimerSeconds is None or seconds < self._nativeTimerSeconds or newTurn:
			self._clearNativeTaskTimer()
			self._nativeTimerTurn = turn
			self._nativeTimerSeconds = self._nativeHeartbeatAt = seconds
			return
		self._nativeTimerTurn = turn or self._nativeTimerTurn
		if seconds == self._nativeTimerSeconds:
			return
		self._nativeTimerSeconds = seconds
		conf = _settings()
		if self._paused or not conf["announceWorking"] or seconds >= conf["maximumBusyMinutes"] * 60:
			return
		mode = conf[CATEGORY_OUTPUT_CONFIG["working"]]
		actions = categoryOutputActions(mode, conf["speech"], conf["braille"], conf["soundWhenSpeechUnavailable"])
		if conf["announceHeartbeat"] and seconds - self._nativeHeartbeatAt >= conf["workingIntervalSeconds"]:
			self._nativeHeartbeatAt = seconds
			pulseActions = actions.copy()
			if self._appFocusState is False or not self._conversationWindowOwnsForeground(self._conversationWindowHandle):
				pulseActions.update(speech=False, braille=False)
			if any(pulseActions.values()) and self._announceBackgroundPulse(seconds, conf, pulseActions):
				self._nativeClickAt = seconds
		if seconds * 1000 < conf["workingClickStartDelayMs"]:
			return
		sinceClick = float("inf") if self._nativeClickAt is None else seconds - self._nativeClickAt
		if shouldPlayContinuousWorkingClick(
			True, conf["continuousWorkingClicks"], conf["progressSoundStyle"], actions["sound"],
			sinceClick, conf["workingClickIntervalMs"] / 1000,
		) and _playProgressSound("working", _("Working"), conf["progressSoundStyle"], conf["clickVolume"]):
			self._nativeClickAt = seconds

	def _activeBranchMessages(self, limit):
		"""Scan back from the active prompt until enough turns or the start is found."""
		# Anchor the fallback range at the active composer. POSITION_LAST can include
		# inactive fork/side-conversation DOM after the composer and therefore return
		# convincing but stale messages from another branch.
		anchor = None
		try:
			anchor = self._findChatGPTPromptObject()
		except Exception:
			pass
		scanCharacters = RECENT_CHAT_INITIAL_SCAN_CHARACTERS
		while True:
			if anchor is not None:
				try:
					info = self._buffer.makeTextInfo(anchor)
					info.collapse()
				except Exception:
					anchor = None
			if anchor is None:
				info = self._buffer.makeTextInfo(textInfos.POSITION_LAST)
			moved = _extendScanStart(info, scanCharacters)
			messages, _promptReached = self._chatMessagesFromInfo(
				info, stopAtPrompt=anchor is None, limit=limit,
			)
			reachedStart = abs(moved) < scanCharacters
			if len(messages) >= limit or reachedStart or scanCharacters >= RECENT_CHAT_MAX_SCAN_CHARACTERS:
				return messages
			scanCharacters = min(scanCharacters * 2, RECENT_CHAT_MAX_SCAN_CHARACTERS)

	def _readRecentChatMessage(self, position):
		try:
			messages = self._currentChatMessages()
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not read recent chat messages", exc_info=True)
			ui.message(_("Recent chat messages could not be read"))
			return
		if not messages:
			ui.message(_("No recent chat messages are available"))
			return
		if len(messages) < position:
			ui.message(_("Only {count} recent chat messages are available").format(count=len(messages)))
			return
		speaker, text = messages[-position]
		speakerLabel = _("You") if speaker == "user" else _("ChatGPT")
		ui.message(_("Chat message {position}, {speaker}: {text}").format(
			position=position, speaker=speakerLabel, text=text,
		))

	def _splitScanConversationMessages(self, tailMessages):
		"""Keep long-conversation caches current without discarding earlier turns."""
		if self._messageListRefreshPending or (
			self._messageListDialog and not self._currentConversationMessageList()
		):
			# The message list asked for turns. This runs from the poll, never from a
			# button handler, and uses the same bounded scan as message shortcuts.
			try:
				return self._activeBranchMessages(MESSAGE_LIST_LIMIT)
			except Exception:
				log.debugWarning("ChatGPT Desktop Access could not scan conversation messages", exc_info=True)
		return mergeConversationTail(self._currentConversationMessageList(), tailMessages)

	def _currentConversationMessageList(self):
		if self._recentChatMessagesBuffer is self._buffer:
			return self._conversationMessages
		return ()

	def _messageListClosed(self):
		self._messageListDialog = None
		self._messageListRefreshPending = False
		gui.mainFrame.postPopup()

	def _requestConversationMessageListRefresh(self):
		"""Refresh from Chromium on the next poll, never in a button handler."""
		if not self._buffer:
			return ()
		self._messageListRefreshPending = True
		self._schedulePoll(delay=50, requestInspection=True)
		return None

	def _openConversationMessageList(self):
		if not _settings()["enableMessageList"]:
			ui.message(_("Conversation message list is disabled in ChatGPT Desktop Access settings"))
			return
		focus = api.getFocusObject()
		if not _isChatGPTObject(focus) or not self._rememberBuffer(
			focus, allowUnclassifiedConversation=True,
		):
			ui.message(_("Open a ChatGPT or Codex conversation before viewing messages"))
			return
		if self._messageListDialog:
			self._messageListDialog.Raise()
			self._messageListDialog.messageList.SetFocus()
			return
		messages = self._currentConversationMessageList()
		if not messages:
			self._schedulePoll(delay=50, requestInspection=True)
		gui.mainFrame.prePopup()
		try:
			self._messageListDialog = MessageListDialog(
				gui.mainFrame, messages, self._requestConversationMessageListRefresh,
				self._messageListClosed,
			)
			self._messageListDialog.Show()
			self._messageListDialog.messageList.SetFocus()
		except Exception:
			self._messageListDialog = None
			gui.mainFrame.postPopup()
			raise

	def _diagnosticReport(self):
		conf = _settings()
		return _(
			"Version: {version}\nChatGPT app: {appVersion}\nChatGPT compatibility check: {compatibility}\nVerbosity: {verbosity}\nFull speech profile: {profile}\nMinimal speech profile: {minimalProfile}\nBraille detail: {brailleDetail}\nSound style: {style}\nClick volume: {volume}\n"
			"Monitoring attached: {attached}\nBackground state: {state}\nPaused: {paused}\n"
			"Active category: {category}\nLast state reason: {reason}\nLast submission signal: {signal}\n"
			"Codex document switches: {switches}\nFull buffer inspections: {inspections}\nLightweight ticks without inspection: {skipped}\nConversation scan timing: {scanTiming}\nBackground mode-probe timing: {modeTiming}\nPrompt typing protection: {typingProtection}\nPreserved Braille compositions: {braillePreserved}\nSuppressed disruptive conversation updates: {conversationUpdates}\nLast inspection error: {error}\n"
			"Embedded browser focus detected: {browserFocused}\nNative browser interaction: yes\n"
			"Embedded browser loading announcements: {browserProgress}\n"
			"Speech history entries: {speechHistory}\nBraille history entries: {brailleHistory}\nRecent chats cached: {recent}\nArchived chats cached: {archived}\n"
			"Configuration repairs this session: {repairs}\nSupported applications: {apps}\n"
			"Speech: {speech}\nBraille: {braille}\nStable conversation reading: {protectBraille}\nUrgent speech interruption: {interrupt}\nProgress sounds: {sounds}\nCategory output routing:\n{routing}"
		).format(
			version=ADDON_VERSION, appVersion=self._chatGPTAppVersion(),
			compatibility=getattr(self, "_compatibilityReport", "") or "not run yet",
			verbosity=conf["verbosity"], profile=conf["fullSpeechProfile"], minimalProfile=conf["minimalSpeechProfile"],
			brailleDetail=conf["brailleDetail"],
			style=conf["progressSoundStyle"], volume=conf["clickVolume"],
			attached=bool(self._buffer), state="active" if self._busy else "idle", paused=self._paused,
			category=self._activeCategory, reason=self._lastStateReason, signal=self._lastSubmissionSignal,
			switches=self._documentSwitchCount, inspections=self._bufferInspectionCount,
			skipped=self._skippedBufferInspectionCount,
			scanTiming=self._operationTimingSummary("conversation scan"),
			modeTiming=self._operationTimingSummary("mode detection"),
			typingProtection="active" if time.monotonic() < self._promptTypingUntil else "inactive",
			braillePreserved=self._brailleCaretMoveSuppressions,
			conversationUpdates=self._suppressedConversationUpdates,
			error=self._lastInspectionError,
			browserFocused=self._embeddedBrowserFocused,
			browserProgress=conf["announceEmbeddedBrowserProgress"],
			speechHistory=len(self._speechHistory), brailleHistory=len(self._brailleHistory),
			recent=len(self._chatHistoryTitles()),
			archived=len(self._archivedChatHistoryCaches.get(self._conversationMode, ())),
			repairs=", ".join(_lastConfigurationRepairs) or "none", apps=conf["supportedAppNames"], speech=conf["speech"],
			braille=conf["braille"], protectBraille=conf["protectBrailleReading"],
			interrupt=conf["interruptUrgentSpeech"], sounds=conf["soundWhenSpeechUnavailable"],
			routing="\n".join(
				"{category}: {mode}".format(category=category, mode=conf[key])
				for category, key in CATEGORY_OUTPUT_CONFIG.items()
			),
		) + "\n" + _("Attachment menu diagnostics:") + "\n" + (
			self._attachmentDiagnostics.report or _("not captured")
		)

	def _recordOperationTiming(self, operation, durationMs):
		"""Keep bounded, content-free responsiveness measurements."""
		if operation not in ("conversation scan", "mode detection"):
			return
		stats = self._operationTimings.setdefault(
			operation, {"count": 0, "last": 0, "max": 0, "slow": 0, "lastLoggedAt": 0.0},
		)
		elapsed = max(0, int(round(durationMs)))
		stats["count"] += 1
		stats["last"] = elapsed
		stats["max"] = max(stats["max"], elapsed)
		threshold = 100 if operation == "conversation scan" else 500
		if elapsed >= threshold:
			stats["slow"] += 1
			now = time.monotonic()
			if now - stats["lastLoggedAt"] >= 60:
				stats["lastLoggedAt"] = now
				log.warning(
					"ChatGPT Desktop Access slow %s: %d ms (count=%d); no content recorded",
					operation, elapsed, stats["count"],
				)

	def _operationTimingSummary(self, operation):
		stats = self._operationTimings.get(operation)
		if not stats:
			return "not measured"
		return "last {last} ms; max {max} ms; slow {slow}/{count}".format(**stats)

	def _bufferCandidates(self, obj):
		seen = set()
		# NVDA has already resolved the ancestry before delivering gainFocus.
		# Reuse it rather than making another chain of Chromium COM calls.
		try:
			if api.getFocusObject() is obj:
				ancestors = api.getFocusAncestors() or ()
				if ancestors:
					for current in (obj, *reversed(ancestors)):
						if current is not None and id(current) not in seen:
							seen.add(id(current))
							yield current
					return
		except Exception:
			pass
		current = obj
		for _ in range(24):
			if current is None or id(current) in seen:
				break
			seen.add(id(current))
			yield current
			try:
				current = getattr(current, "parent", None)
			except Exception:
				break

	def _queueConversationModeProbe(self, reason, openSelector=False):
		"""Resolve or open the exact header selector off NVDA's main thread."""
		if self._conversationModeProbePendingGeneration or not self._conversationWindowHandle:
			return False
		try:
			import UIAHandler
			handler = UIAHandler.handler
			client = handler.clientObject
		except Exception:
			return False
		self._conversationModeProbeGeneration += 1
		generation = self._conversationModeProbeGeneration
		self._conversationModeProbePendingGeneration = generation
		if openSelector:
			self._conversationModeProbeActivationGeneration = generation
		windowHandle = self._conversationWindowHandle
		self._lastConversationModeProbeAt = time.monotonic()
		self._modeProbeStartedAt = self._lastConversationModeProbeAt

		def probe():
			mode = ""
			selectorOpened = False
			try:
				root = client.ElementFromHandleBuildCache(windowHandle, handler.baseCacheRequest)
				nameConditions = [
					client.createPropertyCondition(UIAHandler.UIA_NamePropertyId, label)
					for label in MODE_SWITCH_BUTTON_LABELS
				]
				nameCondition = client.createOrConditionFromArray(nameConditions)
				buttonCondition = client.createPropertyCondition(
					UIAHandler.UIA_ControlTypePropertyId, UIAHandler.UIA_ButtonControlTypeId,
				)
				condition = client.createAndConditionFromArray([buttonCondition, nameCondition])
				control = root.FindFirst(UIAHandler.TreeScope_Descendants, condition) if root else None
				if control:
					controlName = control.CurrentName
					mode = conversationModeFromSwitchControl(controlName, role="button")
					if not mode:
						try:
							helpText = control.CurrentHelpText
						except Exception:
							helpText = ""
						mode = conversationModeFromSwitchControl(controlName, helpText, "button")
				if openSelector and control and mode:
					pattern = control.GetCurrentPattern(UIAHandler.UIA_ExpandCollapsePatternId)
					expandPattern = (
						pattern.QueryInterface(UIAHandler.IUIAutomationExpandCollapsePattern)
						if pattern else None
					)
					if expandPattern:
						try:
							expandState = int(expandPattern.CurrentExpandCollapseState)
						except Exception:
							expandState = 0
						if expandState in (1, 2):
							# An already-open popup already owns keyboard focus. Do not move
							# focus back to its header button.
							selectorOpened = True
						else:
							control.SetFocus()
							expandPattern.Expand()
							selectorOpened = True
						log.debug(
							"ChatGPT Desktop Access opened the native mode selector (current=%s)",
							mode,
						)
			except Exception:
				log.debugWarning(
					"ChatGPT Desktop Access could not query the mode-switch control",
					exc_info=True,
				)
			finally:
				queueHandler.queueFunction(
					queueHandler.eventQueue,
					self._completeConversationModeProbe,
					generation, windowHandle, mode, reason, openSelector, selectorOpened,
				)

		try:
			handler.MTAThreadQueue.put_nowait(probe)
		except Exception:
			self._conversationModeProbePendingGeneration = 0
			self._modeProbeStartedAt = 0.0
			if self._conversationModeProbeActivationGeneration == generation:
				self._conversationModeProbeActivationGeneration = 0
			log.debugWarning("ChatGPT Desktop Access could not schedule mode verification", exc_info=True)
			return False
		return True

	def _completeConversationModeProbe(
		self, generation, windowHandle, mode, reason,
		selectorRequested=False, selectorOpened=False,
	):
		"""Apply an asynchronous mode result only to the conversation that requested it."""
		global _activePluginInstance
		if generation != self._conversationModeProbePendingGeneration:
			return
		self._conversationModeProbePendingGeneration = 0
		startedAt = getattr(self, "_modeProbeStartedAt", 0.0)
		self._modeProbeStartedAt = 0.0
		if startedAt:
			self._recordOperationTiming("mode detection", (time.monotonic() - startedAt) * 1000)
		if getattr(self, "_conversationModeProbeActivationGeneration", 0) == generation:
			self._conversationModeProbeActivationGeneration = 0
		if _activePluginInstance is not self or windowHandle != self._conversationWindowHandle:
			return
		if selectorRequested:
			if not mode:
				self._announceConversationModeNotice(
					_("The ChatGPT and Codex mode switch is not available in this view"),
				)
				log.debugWarning("ChatGPT Desktop Access could not find the mode-switch control")
				return
			if not selectorOpened:
				self._announceConversationModeNotice(
					_("The ChatGPT and Codex mode menu could not be opened"),
				)
				log.debugWarning("ChatGPT Desktop Access could not expand the mode-switch control")
				return
			self._setConversationMode(mode, reason, authoritative=True)
			# Chromium does not reliably emit a name or state event for this button
			# after a menu item is chosen. Remember that the native selector is open
			# and verify it once focus returns to the app document.
			self._modeSelectorOpenedAt = time.monotonic()
			modeName = _("Codex") if mode == "codex" else _("ChatGPT")
			self._announceConversationModeNotice(
				_("{mode} mode. Mode selector open. Use Up or Down Arrow and Enter to choose a mode.").format(
					mode=modeName,
				),
			)
			return
		if not mode:
			log.debug("ChatGPT Desktop Access mode-switch control was not available during verification")
			self._schedulePendingChatHistoryOpen(CHAT_HISTORY_OPEN_RETRY_MILLISECONDS)
			return
		if self._setConversationMode(mode, reason, authoritative=True):
			self._schedulePoll(delay=50, requestInspection=True)
		self._schedulePendingChatHistoryOpen(0)

	def _announceConversationModeNotice(self, message):
		"""Send a mode-switch result through the add-on's enabled output channels."""
		self._latestMessage = self._latestFullMessage = message
		self._speakOnce(
			message, "other", "other", brailleMessage=message, protectBrailleReading=False,
		)

	def _chatGPTAppVersion(self):
		"""Describe the installed ChatGPT app, which changes behavior with each update."""
		processId = self._conversationWindowProcessId
		if not processId:
			try:
				focus = api.getFocusObject()
				processId = getattr(focus, "processID", 0) if _isChatGPTObject(focus) else 0
			except Exception:
				processId = 0
		if not processId:
			return _("not open")
		try:
			appModule = appModuleHandler.getAppModuleFromProcessID(processId)
			appPath = getattr(appModule, "appPath", "")
			try:
				productVersion = appModule.productVersion
			except Exception:
				productVersion = ""
			return chatGPTAppVersionSummary(appPath, productVersion)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not read the ChatGPT app version", exc_info=True)
			return "unknown"

	def _scheduleCompatibilityCheck(self, delayMilliseconds=COMPATIBILITY_CHECK_DELAY_MILLISECONDS):
		"""Check once per ChatGPT window that the names the add-on relies on are still there."""
		processId = self._conversationWindowProcessId
		if not processId or processId == getattr(self, "_compatibilityCheckedProcessId", 0):
			return
		if getattr(self, "_compatibilityCheckTimer", None):
			self._compatibilityCheckTimer.Stop()
		self._compatibilityCheckTimer = wx.CallLater(delayMilliseconds, self._runCompatibilityCheck, processId)

	def _runCompatibilityCheck(self, processId, attempt=0):
		"""Read ChatGPT's window on UI Automation's thread and report anything missing.

		ChatGPT renames controls between releases. Finding out here, right after an
		update, means the NVDA log and support report say what changed before
		users notice a feature has stopped working.
		"""
		self._compatibilityCheckTimer = None
		windowHandle = self._conversationWindowHandle
		if processId != self._conversationWindowProcessId or not windowHandle:
			return
		try:
			import UIAHandler
			handler = UIAHandler.handler
			client = handler.clientObject
		except Exception:
			return
		appVersion = self._chatGPTAppVersion()

		def probe():
			promptNames, buttonNames, composerButtonNames, switchShown, failed = [], [], [], False, False
			try:
				walker = client.RawViewWalker
				root = client.ElementFromHandle(windowHandle)
				edits = root.FindAll(
					UIAHandler.TreeScope_Descendants,
					client.createPropertyCondition(UIAHandler.UIA_ControlTypePropertyId, UIAHandler.UIA_EditControlTypeId),
				)
				buttonCondition = client.createPropertyCondition(
					UIAHandler.UIA_ControlTypePropertyId, UIAHandler.UIA_ButtonControlTypeId,
				)
				prompt = None
				for index in range(edits.Length if edits else 0):
					element = edits.GetElement(index)
					if CHATGPT_PROMPT_EDITOR_CLASS in str(element.CurrentClassName or "").split():
						promptNames.append(str(element.CurrentName or ""))
						prompt = prompt or element
				buttons = root.FindAll(UIAHandler.TreeScope_Descendants, buttonCondition)
				buttonNames = [
					str(buttons.GetElement(index).CurrentName or "")
					for index in range(buttons.Length if buttons else 0)
				]
				if prompt is not None:
					# Buttons beside the message field are interface controls, not chat titles.
					composer = prompt
					for _ancestorLevel in range(8):
						composer = walker.GetParentElement(composer)
						if not composer:
							break
						nearby = composer.FindAll(UIAHandler.TreeScope_Descendants, buttonCondition)
						if nearby and nearby.Length:
							composerButtonNames = [
								str(nearby.GetElement(index).CurrentName or "")
								for index in range(min(nearby.Length, 20))
							]
							break
				switchShown = bool(root.FindFirst(
					UIAHandler.TreeScope_Descendants,
					client.createPropertyCondition(UIAHandler.UIA_NamePropertyId, COMPOSER_MODE_GROUP_NAME),
				))
			except Exception:
				log.debugWarning("ChatGPT Desktop Access compatibility check could not read ChatGPT", exc_info=True)
				failed = True
			finally:
				queueHandler.queueFunction(
					queueHandler.eventQueue, self._finishCompatibilityCheck,
					processId, attempt, appVersion, failed,
					chatGPTCompatibilityFindings(promptNames, buttonNames, composerButtonNames, switchShown),
				)

		try:
			handler.MTAThreadQueue.put_nowait(probe)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not queue the compatibility check", exc_info=True)

	def _finishCompatibilityCheck(self, processId, attempt, appVersion, failed, findings):
		if processId != self._conversationWindowProcessId:
			return
		if failed or findings is None:
			# No message field on this page yet, such as Settings; try again later.
			if attempt < COMPATIBILITY_CHECK_RETRIES:
				self._compatibilityCheckTimer = wx.CallLater(
					COMPATIBILITY_CHECK_RETRY_MILLISECONDS, self._runCompatibilityCheck, processId, attempt + 1,
				)
			return
		self._compatibilityCheckedProcessId = processId
		problems, notes = findings
		self._compatibilityReport = "{version}: {result}; {notes}".format(
			version=appVersion,
			result="problems: " + "; ".join(problems) if problems else "everything found",
			notes="; ".join(notes),
		)
		log.info("ChatGPT Desktop Access compatibility check for ChatGPT %s", self._compatibilityReport)
		conf = _settings()
		previousVersion = conf["lastCheckedChatGPTVersion"]
		if previousVersion == appVersion:
			return
		conf["lastCheckedChatGPTVersion"] = appVersion
		try:
			config.conf.save()
		except Exception:
			log.debugWarning("Unable to save the checked ChatGPT version", exc_info=True)
		if problems and previousVersion:
			# Only after an update, and only once per ChatGPT version.
			ui.message(_(
				"ChatGPT Desktop Access: ChatGPT was updated, and some add-on features may not work until "
				"the add-on is updated. Details are in the support report."
			))

	def _reportOrSwitchComposerMode(self, switch=False):
		"""Report ChatGPT's Chat or Work composer setting, or switch it.

		The switch sits above a new chat's message field in ChatGPT. Its Chat and
		Work settings offer different Add files and more menus. UI Automation is
		used on its own thread so NVDA never waits on ChatGPT.
		"""
		focus = api.getFocusObject()
		if not _isChatGPTObject(focus):
			ui.message(_("Move to ChatGPT first"))
			return
		try:
			import UIAHandler
			handler = UIAHandler.handler
			client = handler.clientObject
			windowHandle = winUser.getAncestor(focus.windowHandle, winUser.GA_ROOT)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not prepare the Chat and Work switch", exc_info=True)
			ui.message(_("The Chat and Work switch could not be read"))
			return

		def probe():
			outcome, mode, other = "failed", "", ""
			try:
				root = client.ElementFromHandle(windowHandle)
				group = root.FindFirst(
					UIAHandler.TreeScope_Descendants,
					client.createPropertyCondition(UIAHandler.UIA_NamePropertyId, COMPOSER_MODE_GROUP_NAME),
				) if root else None
				if not group:
					outcome = "missing"
					return
				buttons = group.FindAll(
					UIAHandler.TreeScope_Children,
					client.createPropertyCondition(UIAHandler.UIA_ControlTypePropertyId, UIAHandler.UIA_ButtonControlTypeId),
				)
				toggles = []
				for index in range(buttons.Length if buttons else 0):
					element = buttons.GetElement(index)
					pattern = element.GetCurrentPattern(UIAHandler.UIA_TogglePatternId)
					toggle = pattern.QueryInterface(UIAHandler.IUIAutomationTogglePattern) if pattern else None
					isOn = bool(toggle) and int(toggle.CurrentToggleState) == 1
					toggles.append((str(element.CurrentName or ""), isOn, toggle))
				pairs = [(name, isOn) for name, isOn, _toggle in toggles]
				mode = selectedComposerMode(pairs)
				other = otherComposerMode(pairs, mode)
				if not mode or not other:
					outcome = "missing"
					return
				if not switch:
					outcome = "current"
					return
				target = next(toggle for name, isOn, toggle in toggles if " ".join(name.split()) == other)
				target.Toggle()
				outcome, mode, other = "switched", other, mode
			except Exception:
				log.debugWarning("ChatGPT Desktop Access could not use the Chat and Work switch", exc_info=True)
				outcome = "failed"
			finally:
				queueHandler.queueFunction(queueHandler.eventQueue, self._announceComposerMode, outcome, mode, other)

		try:
			handler.MTAThreadQueue.put_nowait(probe)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not queue the Chat and Work switch", exc_info=True)
			ui.message(_("The Chat and Work switch could not be read"))

	def _reportComposerAttachments(self):
		"""Say which files and tools are attached to ChatGPT's message.

		Files appear as buttons above the message field, each with its own Remove
		button. Tools such as Web search are chips inside the field, which NVDA
		reads only as an unlabeled object. UI Automation is used on its own thread.
		"""
		focus = api.getFocusObject()
		if not _isChatGPTObject(focus):
			ui.message(_("Move to ChatGPT first"))
			return
		try:
			import UIAHandler
			handler = UIAHandler.handler
			client = handler.clientObject
			windowHandle = winUser.getAncestor(focus.windowHandle, winUser.GA_ROOT)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not prepare the attachment report", exc_info=True)
			ui.message(_("The message attachments could not be read"))
			return

		def probe():
			found, files, tools = False, [], []
			try:
				walker = client.RawViewWalker
				root = client.ElementFromHandle(windowHandle)
				buttons = root.FindAll(
					UIAHandler.TreeScope_Descendants,
					client.createAndConditionFromArray([
						client.createPropertyCondition(UIAHandler.UIA_ControlTypePropertyId, UIAHandler.UIA_ButtonControlTypeId),
						client.createPropertyCondition(UIAHandler.UIA_NamePropertyId, ADD_FILES_BUTTON_NAME),
					]),
				) if root else None
				editCondition = client.createPropertyCondition(UIAHandler.UIA_ControlTypePropertyId, UIAHandler.UIA_EditControlTypeId)
				composer = editor = None
				for index in range(buttons.Length if buttons else 0):
					candidate = buttons.GetElement(index)
					# With Work selected, the message field is several levels further
					# from the button than with Chat selected.
					for _ancestorLevel in range(8):
						candidate = walker.GetParentElement(candidate)
						if not candidate:
							break
						edit = candidate.FindFirst(UIAHandler.TreeScope_Descendants, editCondition)
						if edit and CHATGPT_PROMPT_EDITOR_CLASS in str(edit.CurrentClassName or "").split():
							composer, editor = candidate, edit
							break
					if composer:
						break
				if not composer:
					return
				found = True
				composerButtons = composer.FindAll(
					UIAHandler.TreeScope_Descendants,
					client.createPropertyCondition(UIAHandler.UIA_ControlTypePropertyId, UIAHandler.UIA_ButtonControlTypeId),
				)
				for index in range(composerButtons.Length if composerButtons else 0):
					element = composerButtons.GetElement(index)
					if COMPOSER_FILE_CLASS in str(element.CurrentClassName or ""):
						files.append(element.CurrentName)
				editorElements = editor.FindAll(UIAHandler.TreeScope_Descendants, client.CreateTrueCondition())
				for index in range(editorElements.Length if editorElements else 0):
					element = editorElements.GetElement(index)
					if COMPOSER_TOOL_ICON_CLASS not in str(element.CurrentClassName or ""):
						continue
					chip = walker.GetParentElement(element)
					texts = chip.FindAll(UIAHandler.TreeScope_Children, client.createPropertyCondition(
						UIAHandler.UIA_ControlTypePropertyId, UIAHandler.UIA_TextControlTypeId,
					)) if chip else None
					tools.append(" ".join(
						str(texts.GetElement(textIndex).CurrentName or "") for textIndex in range(texts.Length if texts else 0)
					))
			except Exception:
				log.debugWarning("ChatGPT Desktop Access could not read the message attachments", exc_info=True)
				found = None
			finally:
				queueHandler.queueFunction(
					queueHandler.eventQueue, self._announceComposerAttachments,
					found, uniqueLabels(files), uniqueLabels(tools),
				)

		try:
			handler.MTAThreadQueue.put_nowait(probe)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not queue the attachment report", exc_info=True)
			ui.message(_("The message attachments could not be read"))

	def _suggestionMenuAnnouncementsEnabled(self):
		"""On unless turned off in settings or another add-on already reads these menus."""
		if not _settings()["announceSuggestionMenus"]:
			return False
		if _otherSuggestionMenuAddonRunning():
			return False
		try:
			return _isCodexPromptObject(api.getFocusObject())
		except Exception:
			return False

	def _noteSuggestionMenuKeys(self, keys):
		if not getattr(self, "_suggestionMenuOpen", False):
			return
		if set(keys) & set(SUGGESTION_MENU_CLOSE_KEYS):
			self._closeSuggestionMenuTracking()
		elif set(keys) & set(SUGGESTION_MENU_MOVE_KEYS):
			self._scheduleSuggestionMenuRead("move", SUGGESTION_MENU_MOVE_DELAY_MILLISECONDS)
		elif set(keys) & set(SUGGESTION_MENU_EDIT_KEYS):
			self._scheduleSuggestionMenuRead("filter", SUGGESTION_MENU_FILTER_DELAY_MILLISECONDS)

	def _closeSuggestionMenuTracking(self):
		self._suggestionMenuOpen = False
		self._suggestionMenuLastReading = None
		timer = getattr(self, "_suggestionMenuTimer", None)
		if timer:
			timer.Stop()
		self._suggestionMenuTimer = None

	def _scheduleSuggestionMenuRead(self, reason, delayMilliseconds):
		"""Read ChatGPT's "/" or "@" menu shortly after a key, once its highlight has moved."""
		if not self._suggestionMenuAnnouncementsEnabled():
			return
		if self._attachmentMenuFlowActive():
			# Add files and more has its own list.
			return
		pending = getattr(self, "_suggestionMenuReason", "")
		self._suggestionMenuReason = "open" if "open" in (pending, reason) else reason
		timer = getattr(self, "_suggestionMenuTimer", None)
		if timer:
			timer.Stop()
		self._suggestionMenuTimer = wx.CallLater(delayMilliseconds, self._readSuggestionMenu)

	def _readSuggestionMenu(self):
		self._suggestionMenuTimer = None
		reason, self._suggestionMenuReason = getattr(self, "_suggestionMenuReason", "move"), ""
		buffer = self._buffer
		if buffer is None:
			return
		try:
			import UIAHandler
			handler = UIAHandler.handler
		except Exception:
			return

		def probe():
			options = ()
			try:
				options = self._readAttachmentPopupRowsWithUIA(buffer)
			except Exception:
				log.debugWarning("ChatGPT Desktop Access could not read a suggestion menu", exc_info=True)
			finally:
				queueHandler.queueFunction(queueHandler.eventQueue, self._announceSuggestionMenu, reason, options)

		try:
			handler.MTAThreadQueue.put_nowait(probe)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not queue a suggestion menu read", exc_info=True)

	def _announceSuggestionMenu(self, reason, options):
		"""Say how many suggestions there are and which one ChatGPT has highlighted."""
		if not options:
			self._closeSuggestionMenuTracking()
			return
		if not self._suggestionMenuAnnouncementsEnabled():
			return
		count, option, position = suggestionMenuReading(options, reason == "open")
		wasOpen = getattr(self, "_suggestionMenuOpen", False)
		self._suggestionMenuOpen = True
		reading = (count, attachmentOptionKey(option) if option else "", position)
		if reason == "filter" and reading == getattr(self, "_suggestionMenuLastReading", None):
			return
		self._suggestionMenuLastReading = reading
		parts = []
		if not wasOpen or reason in ("open", "filter"):
			# Translators: announced when ChatGPT's "/" or "@" menu opens or its list changes.
			parts.append(_("Suggestions: {count}").format(count=count))
		if option is not None:
			label = option["title"] + (", " + option["description"] if option.get("description") else "")
			# Translators: {label} is a suggestion such as "Goal, Set a goal to keep pursuing"; {position} and {count} give its place.
			parts.append(_("{label}, {position} of {count}").format(label=label, position=position, count=count))
		if reason == "move":
			speech.cancelSpeech()
		ui.message(". ".join(parts))

	def _announceComposerAttachments(self, found, files, tools):
		if found is None:
			ui.message(_("The message attachments could not be read"))
		elif not found:
			ui.message(_("No message field with Add files and more is shown here"))
		elif not files and not tools:
			ui.message(_("Nothing is attached to the message"))
		else:
			parts = []
			if files:
				# Translators: {files} is a comma-separated list of files attached to the message.
				parts.append(_("Attached: {files}").format(files=", ".join(files)))
			if tools:
				# Translators: {tools} is a comma-separated list of tools, such as Web search, added to the message.
				parts.append(_("Tools: {tools}").format(tools=", ".join(tools)))
			ui.message(". ".join(parts))
		log.info(
			"ChatGPT Desktop Access attachment report: field found %s, %d files, %d tools",
			found, len(files), len(tools),
		)

	def _announceComposerMode(self, outcome, mode, other):
		if outcome == "current":
			# Translators: {mode} and {other} are ChatGPT's Chat and Work composer settings.
			ui.message(_("{mode} selected. Press twice quickly to switch to {other}").format(mode=mode, other=other))
		elif outcome == "switched":
			# Translators: {mode} is the newly selected Chat or Work composer setting.
			ui.message(_("{mode} selected").format(mode=mode))
		elif outcome == "missing":
			ui.message(_("The Chat and Work switch is not shown here. It is above the message field in a new ChatGPT chat"))
		else:
			ui.message(_("The Chat and Work switch could not be read"))
		log.info("ChatGPT Desktop Access composer setting command: %s %s", outcome, mode)

	def _openConversationModeSelector(self):
		"""Focus and expand ChatGPT's native mode control for manual selection."""
		focus = api.getFocusObject()
		if not _isChatGPTObject(focus):
			self._announceConversationModeNotice(_("Move to ChatGPT before switching modes"))
			return
		self._rememberBuffer(focus)
		if not self._conversationWindowHandle:
			self._announceConversationModeNotice(
				_("The ChatGPT and Codex mode switch is not available in this view"),
			)
			return
		self._modeSelectorOpenedAt = 0.0
		# A routine verification may already be queued. Invalidate only its result so
		# this user-requested action never waits behind stale state on NVDA's main thread.
		if self._conversationModeProbePendingGeneration:
			self._conversationModeProbeGeneration += 1
			self._conversationModeProbePendingGeneration = 0
			self._conversationModeProbeActivationGeneration = 0
		if not self._queueConversationModeProbe("requested mode selector", openSelector=True):
			self._announceConversationModeNotice(_("The ChatGPT and Codex mode menu could not be opened"))

	def _confirmConversationModeAfterSelector(self, obj):
		"""Verify the native mode after its popup closes without blocking focus events."""
		openedAt = getattr(self, "_modeSelectorOpenedAt", 0.0)
		if not openedAt:
			return False
		now = time.monotonic()
		if now - openedAt > MODE_SELECTOR_CONFIRM_TIMEOUT_SECONDS:
			self._modeSelectorOpenedAt = 0.0
			return False
		if not _isChatGPTObject(obj):
			return False
		# SetFocus and Expand first focus the selector button and then its menu.
		# Waiting for any other ChatGPT control distinguishes the menu closing after
		# Enter or Escape from those expected opening-focus events.
		if _switchControlMode(obj):
			return False
		if _roleName(obj) in ("menu", "menuitem"):
			return False
		if not self._queueConversationModeProbe("mode selector selection confirmation"):
			return False
		self._modeSelectorOpenedAt = 0.0
		return True

	def _observeConversationModeControl(self, obj, reason):
		"""Apply an exact mode-switch accessibility event without walking ancestors."""
		if not _isChatGPTObject(obj):
			return False
		if getattr(obj, "role", None) != Role.BUTTON:
			return False
		mode = _switchControlMode(obj)
		if not mode:
			return False
		if not self._eventBelongsToRetainedConversationBuffer(obj):
			# Chromium can emit delayed state/show events for the selector after its
			# window has closed. Never let that orphaned button recreate a session.
			log.debug("ChatGPT Desktop Access ignored a stale mode-control event")
			return False
		return self._setConversationMode(mode, reason, authoritative=True)

	def _eventBelongsToRetainedConversationBuffer(self, obj):
		"""Require an event to use the exact retained buffer, not stale ancestry."""
		if self._buffer is None:
			return False
		seen = set()
		current = obj
		for _ in range(24):
			if current is None or id(current) in seen:
				break
			seen.add(id(current))
			try:
				buffer = getattr(current, "treeInterceptor", None)
				if buffer is not None:
					return buffer is self._buffer
				current = getattr(current, "parent", None)
			except Exception:
				return False
		return False

	def _eventUsesConversationBuffer(self, obj):
		"""Exclude embedded-browser and unrelated ChatGPT events from conversation scans."""
		if not _isChatGPTObject(obj):
			return False
		# A live region can retain a newly rebuilt Chromium tree interceptor while
		# ``self._buffer`` still points to the preceding instance. Document ancestry
		# is authoritative in that interval. Nested browser documents have no
		# conversation mode and therefore continue to be excluded below.
		if _isConversationObject(obj) or _isCodexPromptObject(obj):
			return True
		if self._buffer is None:
			return False
		seen = set()
		current = obj
		for _ in range(24):
			if current is None or id(current) in seen:
				break
			seen.add(id(current))
			try:
				buffer = getattr(current, "treeInterceptor", None)
				if buffer is not None:
					return buffer is self._buffer
				current = getattr(current, "parent", None)
			except Exception:
				return False
		return _isConversationObject(obj) or _isCodexPromptObject(obj)

	def _conversationBrowseModeActive(self):
		"""Return the mode of the conversation being read, not a transient event buffer."""
		try:
			return bool(self._buffer is not None and not getattr(self._buffer, "passThrough", True))
		except Exception:
			return False

	def _conversationWindowHandleFrom(self, obj, buffer):
		"""Return the outer ChatGPT window, not Chromium's replaceable renderer child."""
		root = getattr(buffer, "rootNVDAObject", None)
		# The event object can belong to a temporary mode-menu popup. Prefer the
		# conversation document root so closing the main window cannot leave the
		# popup handle looking like a new ChatGPT session.
		for candidate in (root, obj):
			try:
				handle = int(getattr(candidate, "windowHandle", 0) or 0)
			except Exception:
				continue
			if not handle:
				continue
			try:
				return int(winUser.getAncestor(handle, winUser.GA_ROOT) or handle)
			except Exception:
				return handle
		return 0

	def _conversationWindowIsAvailable(self, handle):
		"""Conservatively accept only a living, visible outer ChatGPT window."""
		if not handle:
			return False
		try:
			return bool(winUser.isWindow(handle) and winUser.isWindowVisible(handle))
		except Exception:
			# Attachment is reversible and event-driven. If Windows cannot validate a
			# candidate, wait for a later event instead of reviving a closed session.
			return False

	def _conversationWindowOwnsForeground(self, handle):
		"""Reject delayed focus moves after Windows has switched to another app."""
		if not handle:
			return False
		try:
			foreground = int(winUser.getForegroundWindow() or 0)
			foregroundOwner = int(winUser.getAncestor(foreground, winUser.GA_ROOTOWNER) or foreground)
			expectedOwner = int(winUser.getAncestor(handle, winUser.GA_ROOTOWNER) or handle)
			return foregroundOwner == expectedOwner
		except Exception:
			return False

	def _windowProcessId(self, handle):
		try:
			return int(winUser.getWindowThreadProcessID(handle)[0] or 0)
		except Exception:
			return 0

	def _rememberConversationWindowFromEvent(self, obj):
		"""Track ChatGPT's owner window before its virtual buffer becomes available."""
		if not _isChatGPTObject(obj):
			return False
		try:
			handle = int(getattr(obj, "windowHandle", 0) or 0)
			if not handle:
				return False
			# Popup and menu objects can have their own top-level HWND. Root-owner keeps
			# closure tracking attached to the app window that owns those transient UI.
			root = int(winUser.getAncestor(handle, winUser.GA_ROOTOWNER) or 0)
			if not root:
				root = int(winUser.getAncestor(handle, winUser.GA_ROOT) or handle)
		except Exception:
			return False
		if not self._conversationWindowIsAvailable(root):
			return False
		previousHandle = self._conversationWindowHandle
		self._conversationWindowHandle = root
		self._conversationWindowProcessId = self._windowProcessId(root)
		self._conversationWindowUnavailableAt = 0.0
		self._conversationClosedAt = 0.0
		if root != previousHandle and self._buffer is None:
			log.debug("ChatGPT Desktop Access tracked the app window before its buffer attached")
		return True

	def _cancelConversationWindowActions(self):
		"""Cancel delayed actions that could touch or refocus a closing ChatGPT window."""
		self._pendingChatHistoryAction = None
		if self._chatHistoryActionTimer:
			self._chatHistoryActionTimer.Stop()
			self._chatHistoryActionTimer = None
		self._cancelPendingChatHistoryOpen()
		self._cancelChatHistoryExpansion()
		if self._chatActionRetryTimer:
			self._chatActionRetryTimer.Stop()
			self._chatActionRetryTimer = None
		self._pendingDirectChatAction = None
		if self._unarchiveFocusTimer:
			self._unarchiveFocusTimer.Stop()
			self._unarchiveFocusTimer = None
		self._unarchiveFocusAttempts = 0
		if self._popupFocusTimer:
			self._popupFocusTimer.Stop()
			self._popupFocusTimer = None
		self._pendingPopupDialog = None
		self._pendingPopupDialogWindowHandle = 0
		self._lastFocusedPopupDialog = None
		self._cancelVoiceControlConfirmation()
		if self._promptInspectionTimer:
			self._promptInspectionTimer.Stop()
			self._promptInspectionTimer = None
		self._pendingPromptObject = None
		if self._chatHistoryDialog:
			try:
				self._chatHistoryDialog.Close()
			except Exception:
				# The native window may already have destroyed a modeless dialog's
				# underlying handle. Closure cleanup must still proceed.
				self._chatHistoryDialog = None

	def _cancelCloseFocusRecovery(self):
		"""Cancel a delayed synthetic focus event after native recovery wins."""
		self._closeFocusRecoveryGeneration += 1
		if self._closeFocusRecoveryTimer:
			self._closeFocusRecoveryTimer.Stop()
			self._closeFocusRecoveryTimer = None

	def _stableExternalFocusRoot(self, obj):
		"""Return a stable non-ChatGPT root window suitable for close recovery."""
		if obj is None or _isChatGPTObject(obj):
			return 0
		try:
			if State.DEFUNCT in getattr(obj, "states", set()):
				return 0
		except Exception:
			return 0
		appName = str(getattr(getattr(obj, "appModule", None), "appName", "") or "").casefold()
		if appName in {"searchhost", "startmenuexperiencehost", "shellexperiencehost"}:
			return 0
		identity = " ".join((
			str(getattr(obj, "name", "") or ""),
			str(getattr(obj, "windowClassName", "") or ""),
			str(getattr(obj, "UIAAutomationId", "") or ""),
		)).casefold()
		if any(marker in identity for marker in (
			"multitaskingviewframe", "foregroundstaging", "task switcher", "task view",
			"running applications",
		)):
			return 0
		try:
			handle = int(getattr(obj, "windowHandle", 0) or 0)
			root = int(winUser.getAncestor(handle, winUser.GA_ROOT) or handle)
			if not root or not winUser.isWindow(root) or not winUser.isWindowVisible(root):
				return 0
		except Exception:
			return 0
		return root

	def _rememberExternalFocus(self, obj):
		"""Remember the latest real application focus without retaining shell switchers."""
		root = self._stableExternalFocusRoot(obj)
		if not root:
			return False
		self._lastExternalFocusObject = obj
		self._lastExternalFocusWindowHandle = root
		self._cancelCloseFocusRecovery()
		return True

	def _focusRecoveryCandidate(self):
		"""Choose NVDA's current external focus or the last stable application focus."""
		candidates = []
		try:
			desktop = api.getDesktopObject()
			candidates.extend((desktop.objectWithFocus(), desktop.objectInForeground()))
		except Exception:
			pass
		candidates.append(self._lastExternalFocusObject)
		seen = set()
		for candidate in candidates:
			if candidate is None or id(candidate) in seen:
				continue
			seen.add(id(candidate))
			root = self._stableExternalFocusRoot(candidate)
			if root:
				return candidate, root
		return None, 0

	def _fallbackExternalWindowHandle(self, excludedProcessId):
		"""Find the highest usable app window when Windows leaves no focus target."""
		try:
			handle = int(winUser.getTopWindow(0) or 0)
		except Exception:
			return 0
		seen = set()
		for _ in range(256):
			if not handle or handle in seen:
				break
			seen.add(handle)
			try:
				nextHandle = int(winUser.getWindow(handle, winUser.GW_HWNDNEXT) or 0)
				processId = self._windowProcessId(handle)
				extendedStyle = int(winUser.getExtendedWindowStyle(handle) or 0)
				title = str(winUser.getWindowText(handle) or "").strip()
				className = str(winUser.getClassName(handle) or "").casefold()
				rootOwner = int(winUser.getAncestor(handle, winUser.GA_ROOTOWNER) or handle)
				usable = bool(
					handle == rootOwner
					and processId
					and processId != excludedProcessId
					and title
					and winUser.isWindow(handle)
					and winUser.isWindowVisible(handle)
					and winUser.isWindowEnabled(handle)
					and not extendedStyle & (winUser.WS_EX_TOOLWINDOW | winUser.WS_EX_NOACTIVATE)
					and className not in {
						"progman", "workerw", "shell_traywnd", "shell_secondarytraywnd",
						"multitaskingviewframe", "foregroundstaging",
					}
				)
			except Exception:
				usable = False
				nextHandle = 0
			if usable:
				return handle
			handle = nextHandle
		return 0

	def _confirmCloseFocusRecovery(self, target, root, generation, attempt=0):
		"""Queue NVDA's normal gain-focus pipeline only if native focus stayed stale."""
		self._closeFocusRecoveryTimer = None
		if generation != self._closeFocusRecoveryGeneration:
			return False
		try:
			if self._stableExternalFocusRoot(api.getFocusObject()):
				return True
			if not self._stableExternalFocusRoot(target):
				target, candidateRoot = self._focusRecoveryCandidate()
				if candidateRoot:
					root = candidateRoot
			if not target or not self._stableExternalFocusRoot(target):
				# Some UIA providers do not expose an NVDA object immediately after
				# Windows activates their top-level window. Give the provider one
				# bounded extra interval; a natural gain-focus event cancels this timer.
				if attempt < 1 and root and winUser.isWindow(root) and winUser.isWindowVisible(root):
					if winUser.getForegroundWindow() != root:
						winUser.setForegroundWindow(root)
					self._closeFocusRecoveryTimer = wx.CallLater(
						350, self._confirmCloseFocusRecovery, None, root, generation, attempt + 1,
					)
					return True
				log.debugWarning(
					"ChatGPT Desktop Access could not obtain an NVDA object for the recovered window",
				)
				return False
			eventHandler.queueEvent("gainFocus", target)
			log.info("ChatGPT Desktop Access restored NVDA focus after the ChatGPT window closed")
			return True
		except Exception:
			log.debugWarning(
				"ChatGPT Desktop Access could not restore NVDA focus after ChatGPT closed",
				exc_info=True,
			)
			return False

	def _recoverFocusAfterConversationClose(self, closedProcessId=0):
		"""Leave app monitoring and recover speech/Braille when Electron omits focus events."""
		if not self._appFocusState:
			return False
		target, root = self._focusRecoveryCandidate()
		if not root:
			root = self._fallbackExternalWindowHandle(closedProcessId)
		# This produces the same single inactive cue as a normal Alt+Tab transition,
		# even when Windows supplies no replacement foreground or gain-focus event.
		self._updateAppFocusState(target)
		if not root:
			log.debugWarning(
				"ChatGPT Desktop Access could not find an external window after ChatGPT closed",
			)
			return False
		targetAppName = str(getattr(getattr(target, "appModule", None), "appName", "") or "")
		log.info(
			"ChatGPT Desktop Access recovering focus after closure%s",
			" to %s" % targetAppName if targetAppName else " using the next application window",
		)
		self._cancelCloseFocusRecovery()
		generation = self._closeFocusRecoveryGeneration
		try:
			if winUser.getForegroundWindow() != root:
				winUser.setForegroundWindow(root)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not restore the foreground window", exc_info=True)
		if target is not None:
			try:
				target.setFocus()
			except Exception:
				# Some UIA objects do not implement SetFocus even though they remain a
				# valid NVDA target. The confirmation below still restores NVDA state.
				log.debug("ChatGPT Desktop Access focus target did not accept SetFocus", exc_info=True)
		self._closeFocusRecoveryTimer = wx.CallLater(
			200, self._confirmCloseFocusRecovery, target, root, generation,
		)
		return True

	def _detachConversationIfWindowClosed(self, now):
		"""Stop retained activity after the real ChatGPT window closes or hides to the tray."""
		handle = self._conversationWindowHandle
		if not handle:
			self._conversationWindowUnavailableAt = 0.0
			return False
		try:
			windowExists = bool(winUser.isWindow(handle))
			windowVisible = bool(windowExists and winUser.isWindowVisible(handle))
		except Exception:
			# Unknown window state must not interrupt legitimate background work.
			self._conversationWindowUnavailableAt = 0.0
			return False
		if windowExists and windowVisible:
			self._conversationWindowUnavailableAt = 0.0
			return False
		if not self._conversationWindowUnavailableAt:
			self._conversationWindowUnavailableAt = now
			# Do not let a 50-150 ms delayed focus/action callback restore an Electron
			# window during the conservative close-confirmation grace period.
			self._cancelConversationWindowActions()
		if not conversationWindowShouldDetach(
			True, windowExists, windowVisible,
			now - self._conversationWindowUnavailableAt,
			CONVERSATION_WINDOW_CLOSE_GRACE_SECONDS,
		):
			return False
		closedProcessId = self._conversationWindowProcessId
		self._buffer = None
		self._unsupportedScanBuffer = None
		self._conversationWindowHandle = 0
		self._conversationWindowProcessId = 0
		self._conversationWindowUnavailableAt = 0.0
		self._conversationClosedAt = now
		self._conversationMode = ""
		self._conversationModeObserved = False
		self._conversationModeObservedAt = 0.0
		self._conversationModeChangedAt = 0.0
		self._lastConversationModeProbeAt = 0.0
		self._conversationModeProbeGeneration += 1
		self._conversationModeProbePendingGeneration = 0
		self._conversationModeProbeActivationGeneration = 0
		self._modeProbeStartedAt = 0.0
		self._modeSelectorOpenedAt = 0.0
		self._resetAttachmentMenuTracking()
		self._cancelAttachmentSourceFocus()
		self._chatHistoryCacheCurrent = {"chatgpt": False, "codex": False}
		self._ambiguousRecentChatTitles = {"chatgpt": set(), "codex": set()}
		self._pendingChatHistorySnapshots = {"chatgpt": None, "codex": None}
		self._pendingChatHistorySnapshotAt = {"chatgpt": 0.0, "codex": 0.0}
		self._chatHistoryMoreAvailable = {"chatgpt": False, "codex": False}
		self._recentHistoryShowMoreOrdinals = {"chatgpt": 0, "codex": 0}
		self._unifiedRecentCounts = {"chatgpt": 0, "codex": 0}
		self._chatHistoryScanGenerations = {"chatgpt": 0, "codex": 0}
		self._monitoringAnnounced = False
		self._resetEmbeddedBrowserProgress()
		self._resetTaskState("ChatGPT window closed")
		self._recoverFocusAfterConversationClose(closedProcessId)
		log.info("ChatGPT Desktop Access detached after the ChatGPT window closed")
		return True

	def _setConversationMode(self, mode, reason, authoritative=False):
		"""Update the active mode without letting ChatGPT's host document override its switch."""
		mode = str(mode or "").casefold()
		if mode not in ("chatgpt", "codex"):
			return False
		if authoritative:
			# An exact accessibility event is newer than any worker query already in
			# flight. Invalidate that result so it cannot restore the preceding mode.
			pendingProbe = getattr(self, "_conversationModeProbePendingGeneration", 0)
			activationProbe = getattr(self, "_conversationModeProbeActivationGeneration", 0)
			if pendingProbe and pendingProbe != activationProbe:
				self._conversationModeProbeGeneration += 1
				self._conversationModeProbePendingGeneration = 0
			self._conversationModeObserved = True
			self._conversationModeObservedAt = time.monotonic()
		previousMode = self._conversationMode
		if mode == previousMode:
			self._schedulePendingChatHistoryOpen(0)
			return False
		if previousMode:
			self._cancelChatHistoryExpansion()
			self._pendingChatHistoryAction = None
			if self._chatHistoryActionTimer:
				self._chatHistoryActionTimer.Stop()
				self._chatHistoryActionTimer = None
			if self._chatHistoryDialog:
				self._chatHistoryDialog.Close()
			self._resetTaskState("conversation mode changed")
		self._conversationMode = mode
		self._conversationModeChangedAt = time.monotonic()
		self._chatHistoryCacheCurrent[mode] = False
		self._ambiguousRecentChatTitles[mode].clear()
		self._pendingChatHistorySnapshots[mode] = None
		self._pendingChatHistorySnapshotAt[mode] = 0.0
		self._chatHistoryMoreAvailable[mode] = False
		self._recentHistoryShowMoreOrdinals[mode] = 0
		self._unifiedRecentCounts[mode] = 0
		self._chatHistoryScanGenerations[mode] = 0
		log.info(
			"ChatGPT Desktop Access conversation mode changed from %s to %s (%s)",
			previousMode or "unknown", mode, reason,
		)
		self._schedulePendingChatHistoryOpen(0)
		return True

	def _chatHistoryTitles(self, mode=None):
		"""Return only the recent titles cached for one conversation mode."""
		mode = mode or self._conversationMode
		return self._chatHistoryCaches.get(mode, ())

	def _activeCodexThreadTitles(self):
		"""Read the local Codex index only after its source metadata changes."""
		codexRoot = Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))
		sourceSignature = codexHistorySourceSignature(codexRoot)
		if sourceSignature == self._activeCodexTitlesSourceSignature:
			return self._activeCodexTitlesCache
		try:
			activeCodexTitles = tuple(loadActiveCodexThreadTitles(codexRoot))
		except Exception:
			log.debugWarning(
				"ChatGPT Desktop Access could not read active Codex chat metadata",
				exc_info=True,
			)
			activeCodexTitles = ()
		self._activeCodexTitlesCache = activeCodexTitles
		self._activeCodexTitlesSourceSignature = sourceSignature
		log.info(
			"ChatGPT Desktop Access refreshed %d active Codex history titles after source metadata changed",
			len(activeCodexTitles),
		)
		return activeCodexTitles

	def _modeSpecificRecentChatTitles(self, mode, unifiedTitles):
		"""Filter the app's unified Recents region using cached local Codex metadata."""
		activeCodexTitles = self._activeCodexThreadTitles()
		filtered = modeSpecificRecentChatTitles(mode, unifiedTitles, activeCodexTitles)
		summary = (len(unifiedTitles), len(filtered), len(unifiedTitles) - len(filtered))
		if self._recentClassificationSummaries.get(mode) != summary:
			self._recentClassificationSummaries[mode] = summary
			log.info(
				"ChatGPT Desktop Access classified %d unified recent entries for %s: kept %d, excluded %d",
				summary[0], mode, summary[1], summary[2],
			)
		return filtered

	def _cacheChatHistoryScan(self, mode, recentTitles=None, archivedTitles=None):
		"""Store sidebar results without allowing one conversation mode to replace another."""
		if mode not in self._chatHistoryCaches:
			return
		if recentTitles is not None:
			recentTitles = tuple(recentTitles)
			wasCurrent = self._chatHistoryCacheCurrent[mode]
			changed = recentTitles != self._chatHistoryCaches[mode]
			self._chatHistoryCaches[mode] = recentTitles
			self._chatHistoryCacheCurrent[mode] = True
			if changed or not wasCurrent:
				otherMode = "codex" if mode == "chatgpt" else "chatgpt"
				overlap = len(set(recentTitles).intersection(self._chatHistoryCaches[otherMode]))
				log.info(
					"ChatGPT Desktop Access cached %d settled recent %s chats; overlap with %s: %d",
					len(recentTitles), mode, otherMode, overlap,
				)
		if archivedTitles is not None:
			self._archivedChatHistoryCaches[mode] = tuple(archivedTitles)
			self._archivedChatHistoryLoaded[mode] = True
		if recentTitles is not None:
			self._schedulePendingChatHistoryOpen(0)

	def _refreshChatHistoryData(self, mode):
		if mode != self._conversationMode:
			return (), (), False
		archivedTitles, archivedLoaded = self._loadArchivedChatHistory(mode)
		# The Refresh button returns the current cache immediately. Ask the next
		# poll to rescan the sidebar so a later refresh shows newer chats.
		self._bufferDirty = True
		self._schedulePoll(delay=50, requestInspection=True)
		return self._chatHistoryTitles(mode), archivedTitles, archivedLoaded

	def _cancelChatHistoryExpansion(self):
		if self._chatHistoryExpansionTimer:
			self._chatHistoryExpansionTimer.Stop()
			self._chatHistoryExpansionTimer = None
		self._pendingChatHistoryExpansion = None

	def _scheduleChatHistoryExpansion(self, delay):
		if self._chatHistoryExpansionTimer:
			self._chatHistoryExpansionTimer.Stop()
		self._chatHistoryExpansionTimer = wx.CallLater(delay, self._continueChatHistoryExpansion)

	def _startChatHistoryExpansion(self, mode):
		"""Load bounded native Recents pages before presenting the history dialog."""
		if self._pendingChatHistoryExpansion:
			ui.message(_("Recent chat history is already loading"))
			return True
		if not self._chatHistoryMoreAvailable.get(mode, False):
			return False
		agentName = _("ChatGPT") if mode == "chatgpt" else _("Codex")
		self._pendingChatHistoryExpansion = {
			"mode": mode,
			"pages": 0,
			"lastCount": self._unifiedRecentCounts.get(mode, 0),
			"lastGeneration": self._chatHistoryScanGenerations.get(mode, 0),
			"awaitingGrowth": False,
			"staleScans": 0,
			"settleScans": 0,
		}
		ui.message(_("Loading additional {agent} recent chats").format(agent=agentName))
		self._scheduleChatHistoryExpansion(50)
		return True

	def _finishChatHistoryExpansion(self, mode, limitReached=False, failed=False):
		state = self._pendingChatHistoryExpansion or {}
		pages = state.get("pages", 0)
		self._cancelChatHistoryExpansion()
		agentName = _("ChatGPT") if mode == "chatgpt" else _("Codex")
		count = len(self._chatHistoryTitles(mode))
		moreAvailable = self._chatHistoryMoreAvailable.get(mode, False)
		if failed:
			ui.message(_(
				"More recent chats could not be loaded. Showing the {count} currently available {agent} chats"
			).format(count=count, agent=agentName))
		elif limitReached:
			ui.message(_(
				"Loaded {count} {agent} recent chats. More are available; open history again to continue loading"
			).format(count=count, agent=agentName))
		else:
			ui.message(_("Loaded {count} currently available {agent} recent chats").format(
				count=count, agent=agentName,
			))
		log.info(
			"ChatGPT Desktop Access finished %s recent-history expansion after %d pages; "
			"kept %d mode-specific chats; more available: %s; failed: %s",
			mode, pages, count, moreAvailable, bool(failed),
		)
		if mode == self._conversationMode and _isChatGPTObject(api.getFocusObject()):
			self._showChatHistoryDialog(mode)

	def _continueChatHistoryExpansion(self):
		"""Advance native Show more one page at a time without an unbounded UI loop."""
		self._chatHistoryExpansionTimer = None
		state = self._pendingChatHistoryExpansion
		if not state:
			return
		mode = state["mode"]
		if mode != self._conversationMode or self._buffer is None or not _isChatGPTObject(api.getFocusObject()):
			self._cancelChatHistoryExpansion()
			ui.message(_("Recent chat history loading stopped because ChatGPT is no longer focused"))
			return
		currentCount = self._unifiedRecentCounts.get(mode, 0)
		currentGeneration = self._chatHistoryScanGenerations.get(mode, 0)
		moreAvailable = self._chatHistoryMoreAvailable.get(mode, False)
		if state["awaitingGrowth"]:
			if currentGeneration <= state["lastGeneration"] or currentCount <= state["lastCount"]:
				state["staleScans"] += 1
				if state["staleScans"] <= CHAT_HISTORY_EXPANSION_MAX_STALE_SCANS:
					self._schedulePoll(delay=150, requestInspection=True)
					self._scheduleChatHistoryExpansion(CHAT_HISTORY_EXPANSION_RETRY_MILLISECONDS)
					return
				self._finishChatHistoryExpansion(mode, failed=True)
				return
			state["awaitingGrowth"] = False
			state["staleScans"] = 0
			state["lastCount"] = currentCount
			state["lastGeneration"] = currentGeneration
		limitReached = state["pages"] >= CHAT_HISTORY_EXPANSION_MAX_PAGES and moreAvailable
		if not moreAvailable or limitReached:
			if not self._chatHistoryCacheCurrent.get(mode, False):
				state["settleScans"] += 1
				if state["settleScans"] <= CHAT_HISTORY_EXPANSION_MAX_STALE_SCANS:
					self._schedulePoll(delay=150, requestInspection=True)
					self._scheduleChatHistoryExpansion(CHAT_HISTORY_EXPANSION_RETRY_MILLISECONDS)
					return
			self._finishChatHistoryExpansion(
				mode,
				limitReached=limitReached,
				failed=not self._chatHistoryCacheCurrent.get(mode, False),
			)
			return
		try:
			button = self._recentHistoryShowMoreButton(mode)
			if button is None:
				raise LookupError("Recents Show more button not found")
			_pressControl(button)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not activate Recents Show more", exc_info=True)
			self._finishChatHistoryExpansion(mode, failed=True)
			return
		state["pages"] += 1
		state["lastCount"] = currentCount
		state["lastGeneration"] = currentGeneration
		state["awaitingGrowth"] = True
		state["staleScans"] = 0
		self._chatHistoryCacheCurrent[mode] = False
		self._pendingChatHistorySnapshots[mode] = None
		self._pendingChatHistorySnapshotAt[mode] = 0.0
		self._chatHistoryMoreAvailable[mode] = False
		self._recentHistoryShowMoreOrdinals[mode] = 0
		self._bufferDirty = True
		self._schedulePoll(delay=150, requestInspection=True)
		log.info(
			"ChatGPT Desktop Access requested recent-history page %d for %s; "
			"%d unified entries were visible",
			state["pages"], mode, currentCount,
		)
		self._scheduleChatHistoryExpansion(CHAT_HISTORY_EXPANSION_DELAY_MILLISECONDS)

	def _loadArchivedChatHistory(self, mode=None):
		"""Load archived titles from the source belonging to one conversation mode."""
		mode = mode or self._conversationMode
		if mode not in self._archivedChatHistoryCaches:
			return (), False
		if mode == "chatgpt":
			return (
				self._archivedChatHistoryCaches[mode],
				self._archivedChatHistoryLoaded[mode],
			)
		codexRoot = Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))
		try:
			entries = uniqueThreadLabels(loadArchivedThreads(codexRoot, translate=_), translate=_)
			self._archivedChatHistoryCaches[mode] = tuple(title for threadId, title in entries)
			self._archivedChatIds[mode] = {title: threadId for threadId, title in entries}
			self._archivedChatHistoryLoaded[mode] = True
			log.info("ChatGPT Desktop Access loaded %d archived chats from the local index", len(entries))
			return self._archivedChatHistoryCaches[mode], True
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not read archived chat metadata", exc_info=True)
			return self._archivedChatHistoryCaches[mode], False

	def _chatButtonObject(self, title):
		"""Resolve an exact accessible sidebar title to its button."""
		position = self._buffer.makeTextInfo(textInfos.POSITION_FIRST)
		if not position.find(title, reverse=False, caseSensitive=True):
			return None
		obj = getattr(position, "NVDAObjectAtStart", None)
		for _ in range(8):
			if obj is None or getattr(obj, "role", None) == Role.BUTTON:
				break
			obj = getattr(obj, "parent", None)
		if getattr(obj, "role", None) != Role.BUTTON:
			return None
		return obj if chatTitleMatches(title, getattr(obj, "name", ""), titleFoundInsideButton=True) else None

	def _exactNamedButtonObject(self, name, ordinal=1):
		"""Resolve one exact button occurrence without walking Chromium's full object tree."""
		if self._buffer is None or ordinal < 1:
			return None
		wantedName = " ".join(str(name or "").casefold().split())
		if not wantedName:
			return None
		if not _isVirtualBufferDocument(self._buffer):
			return self._namedButtonFromUIA(name, ordinal)
		position = self._buffer.makeTextInfo(textInfos.POSITION_FIRST)
		found = 0
		seen = set()
		for _ in range(64):
			if not position.find(name, reverse=False, caseSensitive=False):
				break
			obj = getattr(position, "NVDAObjectAtStart", None)
			for _ in range(8):
				if obj is None or getattr(obj, "role", None) == Role.BUTTON:
					break
				obj = getattr(obj, "parent", None)
			if getattr(obj, "role", None) == Role.BUTTON and (
				" ".join(str(getattr(obj, "name", "") or "").casefold().split()) == wantedName
			):
				windowHandle = getattr(obj, "windowHandle", 0)
				uniqueId = getattr(obj, "IA2UniqueID", 0)
				identity = (windowHandle, uniqueId) if uniqueId else id(obj)
				if identity not in seen:
					seen.add(identity)
					found += 1
					if found == ordinal:
						return obj
			try:
				position.collapse(end=True)
				if position.move(textInfos.UNIT_CHARACTER, 1) == 0:
					break
			except Exception:
				break
		return None

	def _recentHistoryShowMoreButton(self, mode):
		"""Return the Show more button proven by the latest Recents-region scan."""
		if not self._chatHistoryMoreAvailable.get(mode, False):
			return None
		ordinal = self._recentHistoryShowMoreOrdinals.get(mode, 0)
		return self._exactNamedButtonObject("Show more", ordinal)

	def _namedChatActionButton(self, chatButton, action):
		"""Resolve the action exposed beside the focused chat, not matching transcript text."""
		container = getattr(chatButton, "parent", None)
		for _ in range(2):
			if container is None:
				break
			pending = [getattr(container, "firstChild", None)]
			seen = set()
			while pending and len(seen) < 32:
				obj = pending.pop()
				if obj is None or id(obj) in seen:
					continue
				seen.add(id(obj))
				if obj is not chatButton and getattr(obj, "role", None) == Role.BUTTON and chatActionMatches(
					action, getattr(obj, "name", ""),
				):
					return obj
				nextObject = getattr(obj, "next", None)
				firstChild = getattr(obj, "firstChild", None)
				if nextObject is not None:
					pending.append(nextObject)
				if firstChild is not None:
					pending.append(firstChild)
			container = getattr(container, "parent", None)
		return None

	def _voiceControlFromObject(self, obj, wantedKinds):
		"""Return an exact voice control from an object or one of its ancestors."""
		wantedKinds = set(wantedKinds)
		for _ in range(8):
			if obj is None:
				break
			kind = voiceControlKind(getattr(obj, "name", ""))
			roleName = _roleName(obj)
			if kind and roleName in ("button", "togglebutton"):
				# ChatGPT currently exposes Mute microphone as a toggle button.
				# Some builds retain that name when pressed instead of renaming it
				# Unmute microphone, so the pressed state determines the next action.
				if kind == "mute" and roleName == "togglebutton":
					states = getattr(obj, "states", ()) or ()
					if State.PRESSED in states or State.CHECKED in states:
						kind = "unmute"
				if kind in wantedKinds:
					return obj, kind
			obj = getattr(obj, "parent", None)
		return None, ""

	def _voiceControlObject(self, wantedKinds):
		"""Find a native voice control without scanning the full Chromium object tree."""
		wantedKinds = tuple(wantedKinds)
		focus = api.getFocusObject()
		for candidate in (focus, *(api.getFocusAncestors() or ())):
			control, kind = self._voiceControlFromObject(candidate, wantedKinds)
			if control is not None:
				return control, kind
		self._rememberBuffer(focus)
		if self._buffer is None:
			return None, ""
		for expectedKind, label in VOICE_CONTROL_SEARCH_LABELS:
			if expectedKind not in wantedKinds:
				continue
			try:
				position = self._buffer.makeTextInfo(textInfos.POSITION_LAST)
				if not position.find(label, reverse=True, caseSensitive=False):
					continue
				control, kind = self._voiceControlFromObject(
					getattr(position, "NVDAObjectAtStart", None), wantedKinds,
				)
				if control is not None:
					return control, kind
			except Exception:
				continue
		return None, ""

	def _cancelVoiceControlConfirmation(self):
		if self._voiceControlConfirmationTimer:
			self._voiceControlConfirmationTimer.Stop()
			self._voiceControlConfirmationTimer = None
		self._pendingVoiceControlConfirmation = None

	def _scheduleVoiceControlConfirmation(self, actionKind):
		self._cancelVoiceControlConfirmation()
		self._pendingVoiceControlConfirmation = (actionKind, 0)
		self._voiceControlConfirmationTimer = wx.CallLater(
			VOICE_CONTROL_CONFIRMATION_DELAY_MS, self._confirmVoiceControlAction,
		)

	def _confirmVoiceControlAction(self):
		"""Confirm the resulting native button state before reporting success."""
		self._voiceControlConfirmationTimer = None
		pending = self._pendingVoiceControlConfirmation
		if not pending:
			return
		actionKind, attempt = pending
		expectedKinds = {
			"start": ("stop",),
			"stop": ("start",),
			"mute": ("unmute",),
			"unmute": ("mute",),
		}
		try:
			control, resultingKind = self._voiceControlObject(expectedKinds[actionKind])
		except Exception:
			control, resultingKind = None, ""
		if control is not None and resultingKind in expectedKinds[actionKind]:
			self._pendingVoiceControlConfirmation = None
			messages = {
				"start": _("Voice mode started"),
				"stop": _("Voice mode ended"),
				"mute": _("Microphone muted"),
				"unmute": _("Microphone unmuted"),
			}
			ui.message(messages[actionKind])
			log.info("ChatGPT Desktop Access confirmed ChatGPT voice control: %s", actionKind)
			return
		attempt += 1
		if attempt < VOICE_CONTROL_CONFIRMATION_ATTEMPTS and _isChatGPTObject(api.getFocusObject()):
			self._pendingVoiceControlConfirmation = (actionKind, attempt)
			self._voiceControlConfirmationTimer = wx.CallLater(
				VOICE_CONTROL_CONFIRMATION_DELAY_MS, self._confirmVoiceControlAction,
			)
			return
		self._pendingVoiceControlConfirmation = None
		failure = (
			_("Microphone state could not be confirmed")
			if actionKind in ("mute", "unmute")
			else _("Voice mode state could not be confirmed")
		)
		ui.message(failure)
		log.debugWarning("ChatGPT Desktop Access could not confirm ChatGPT voice control: %s", actionKind)

	def _activateVoiceControl(self, wantedKinds):
		"""Activate an exact native control and verify the resulting state."""
		try:
			self._cancelVoiceControlConfirmation()
			control, kind = self._voiceControlObject(wantedKinds)
			if control is None:
				if set(wantedKinds) == {"mute", "unmute"}:
					ui.message(_("Microphone control is unavailable. Start voice mode first"))
				else:
					ui.message(_("Voice mode control is not available in this ChatGPT view"))
				return
			_pressControl(control)
			messages = {
				"start": _("Starting voice mode"),
				"stop": _("Ending voice mode"),
				"mute": _("Muting microphone"),
				"unmute": _("Unmuting microphone"),
			}
			ui.message(messages[kind])
			self._scheduleVoiceControlConfirmation(kind)
			log.info("ChatGPT Desktop Access requested ChatGPT voice control: %s", kind)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not activate a ChatGPT voice control", exc_info=True)
			ui.message(_("The ChatGPT voice control could not be activated"))

	def _startDirectChatAction(self, title, action):
		if self._chatActionRetryTimer:
			self._chatActionRetryTimer.Stop()
			self._chatActionRetryTimer = None
		self._pendingDirectChatAction = (title, action, self._conversationMode, 0)
		self._pendingDirectChatActionWindowHandle = self._conversationWindowHandle
		self._retryDirectChatAction()

	def _invokeChatAction(self, actionButton, mode):
		_pressControl(actionButton)
		self._chatHistoryCacheCurrent[mode] = False
		self._pendingChatHistorySnapshots[mode] = None
		self._pendingChatHistorySnapshotAt[mode] = 0.0
		self._bufferDirty = True
		self._schedulePoll(delay=250, requestInspection=True)

	def _retryDirectChatAction(self):
		self._chatActionRetryTimer = None
		pending = self._pendingDirectChatAction
		if not pending:
			return
		if getattr(self, "_pendingDirectChatActionWindowHandle", self._conversationWindowHandle) != self._conversationWindowHandle:
			self._pendingDirectChatAction = None
			return
		if not self._conversationWindowOwnsForeground(self._conversationWindowHandle):
			self._pendingDirectChatAction = None
			return
		if not self._conversationWindowIsAvailable(self._conversationWindowHandle):
			self._pendingDirectChatAction = None
			log.debug("ChatGPT Desktop Access cancelled a chat action after its window closed")
			return
		title, action, mode, attempt = pending
		if mode != self._conversationMode:
			self._pendingDirectChatAction = None
			ui.message(_("Chat action cancelled because the ChatGPT view changed or closed"))
			return
		try:
			chatButton = self._chatButtonObject(title)
			if chatButton is None:
				raise LookupError("selected chat button not found")
			chatButton.setFocus()
			actionButton = self._namedChatActionButton(chatButton, action)
			if actionButton is not None:
				actionLabel = " ".join(str(getattr(actionButton, "name", "") or "").split())
				self._invokeChatAction(actionButton, mode)
				self._pendingDirectChatAction = None
				ui.message(_("{action} requested").format(
					action=actionLabel or _("Chat action"),
				))
				log.info(
					"ChatGPT Desktop Access invoked the selected chat action directly: %s",
					actionLabel or action,
				)
				return
		except Exception:
			if attempt >= 11:
				self._pendingDirectChatAction = None
				log.debugWarning("ChatGPT Desktop Access could not activate the selected chat action", exc_info=True)
				ui.message(_("The selected chat action could not be completed"))
				return
		# A missing action control is a normal transient state while Chromium updates
		# the selected sidebar row, so it does not raise above. Apply the same retry
		# limit here; otherwise this path can schedule a main-thread timer forever.
		if attempt >= 11:
			self._pendingDirectChatAction = None
			log.debugWarning("ChatGPT Desktop Access could not find the selected chat action after retrying")
			ui.message(_("The selected chat action could not be completed"))
			return
		self._pendingDirectChatAction = (title, action, mode, attempt + 1)
		self._chatActionRetryTimer = wx.CallLater(100, self._retryDirectChatAction)

	def _scheduleUnarchiveButtonFocus(self):
		self._unarchiveFocusAttempts = 0
		if self._unarchiveFocusTimer:
			self._unarchiveFocusTimer.Stop()
		self._unarchiveFocusTimer = wx.CallLater(100, self._focusUnarchiveButton)

	def _focusUnarchiveButton(self):
		"""Focus Codex's confirmation after its new document becomes accessible."""
		self._unarchiveFocusTimer = None
		if not self._conversationWindowOwnsForeground(self._conversationWindowHandle):
			self._unarchiveFocusAttempts = 0
			return
		if not self._conversationWindowIsAvailable(self._conversationWindowHandle):
			self._unarchiveFocusAttempts = 0
			return
		self._unarchiveFocusAttempts += 1
		try:
			if self._buffer:
				position = self._buffer.makeTextInfo(textInfos.POSITION_FIRST)
				if position.find("Unarchive and open", reverse=False, caseSensitive=False):
					obj = getattr(position, "NVDAObjectAtStart", None)
					for _ancestorLevel in range(8):
						if obj is None or getattr(obj, "role", None) == Role.BUTTON:
							break
						obj = getattr(obj, "parent", None)
					if getattr(obj, "role", None) == Role.BUTTON and " ".join(
						str(getattr(obj, "name", "") or "").casefold().split()
					) == "unarchive and open":
						obj.setFocus()
						log.info("ChatGPT Desktop Access focused the Unarchive and open button")
						return
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not yet focus the unarchive confirmation", exc_info=True)
		if self._unarchiveFocusAttempts < 25:
			self._unarchiveFocusTimer = wx.CallLater(150, self._focusUnarchiveButton)
		else:
			ui.message(_("Unarchive confirmation opened; move to the Unarchive and open button"))

	def _usageLimitTextFromObject(self, obj):
		"""Collect only a small ChatGPT alert subtree when its own text is incomplete."""
		if not _isChatGPTObject(obj):
			return ""
		parts = []
		seenText = set()

		def addObjectText(candidate):
			for attribute in ("name", "value", "description"):
				try:
					value = " ".join(str(getattr(candidate, attribute, "") or "").split())
				except Exception:
					continue
				if value and value not in seenText:
					seenText.add(value)
					parts.append(value[:2000])

		container = None
		current = obj
		seenObjects = set()
		for _ in range(10):
			if current is None or id(current) in seenObjects:
				break
			seenObjects.add(id(current))
			addObjectText(current)
			if _roleName(current) in ("alert", "dialog"):
				container = current
				break
			try:
				current = getattr(current, "parent", None)
			except Exception:
				break
		if container is None:
			return " ".join(parts)

		# Usage pop-overs are small, but Chromium can split the message and its
		# choices across siblings. Bound this rare traversal so an accessibility
		# provider problem can never stall NVDA's main thread.
		pending = [container]
		seenObjects.clear()
		while pending and len(seenObjects) < 80 and sum(map(len, parts)) < 6000:
			current = pending.pop()
			if current is None or id(current) in seenObjects:
				continue
			seenObjects.add(id(current))
			addObjectText(current)
			try:
				nextObject = getattr(current, "next", None) if current is not container else None
				firstChild = getattr(current, "firstChild", None)
			except Exception:
				continue
			if nextObject is not None:
				pending.append(nextObject)
			if firstChild is not None:
				pending.append(firstChild)
		return " ".join(parts)

	def _usageLimitObjectIsPopup(self, obj):
		"""Return whether an object is within an ARIA alert or dialog."""
		seen = set()
		current = obj
		for _ in range(10):
			if current is None or id(current) in seen:
				return False
			seen.add(id(current))
			if _roleName(current) in ("alert", "dialog"):
				return True
			try:
				current = getattr(current, "parent", None)
			except Exception:
				return False
		return False

	def _announceUsageLimit(self, obj, eventText=""):
		"""End local activity and announce an exhausted usage allowance once."""
		if not _isChatGPTObject(obj):
			return False
		objectRole = _roleName(obj)
		if objectRole == "editabletext":
			return False
		text = " ".join(str(eventText or "").split())
		if not text:
			try:
				text = " ".join(str(getattr(obj, "name", "") or "").split())
			except Exception:
				text = ""
		notice = usageLimitNotice(text, _)
		lower = text.casefold()
		inPopup = self._usageLimitObjectIsPopup(obj) if notice or any(
			marker in lower for marker in ("usage", "limit", "credit", "upgrade", "try again")
		) or objectRole in ("alert", "dialog") else False
		if not notice and not inPopup:
			# Most events in the ChatGPT window are unrelated and can return after
			# reading only the local accessible name.
			if not any(
				marker in lower for marker in ("usage", "limit", "credit", "upgrade", "try again")
			):
				return False
		combinedText = self._usageLimitTextFromObject(obj)
		combinedNotice = usageLimitNotice(combinedText, _)
		if combinedNotice:
			text, notice = combinedText, combinedNotice
		if not notice:
			return False
		# Outside a semantically exposed pop-over, require the distinctive full
		# ChatGPT error. This prevents a user's prompt or an assistant response
		# discussing usage limits from being mistaken for the account state.
		lower = text.casefold()
		detailCount = sum((
			bool(re.search(r"\bupgrade(?:\s+to\s+pro|\s+(?:your\s+)?plan)?\b", lower)),
			bool(re.search(r"\b(?:add|buy|purchase)(?:\s+some)?(?:\s+more)?\s+credits?\b", lower)),
			bool("try again" in lower or "next reset" in lower),
		))
		if not inPopup and not (
			"chatgpt.com/codex/settings/usage" in lower or detailCount >= 2
		):
			return False
		return self._applyUsageLimitNotice(notice)

	def _applyUsageLimitNotice(self, notice):
		"""Apply a terminal usage-limit state independently of its event source."""
		self._pluginProgressOwnedBusy.clear()
		self._pendingResponseCompletionAt = 0.0
		self._submittedTurnUnconfirmedAt = 0.0
		self._pendingUserMessageIncrease = False
		self._stopControlVisible = False
		self._promptHadText = False
		self._lastScannedLabel = ""
		self._lastLabel = ""
		self._latestResponseMarker = None
		self._responseMarkerInitialized = False
		self._setBusy(False, "usage limit reached")
		self._active = False
		self._activeCategory = "attention"
		if self._usageLimitActive and notice == self._lastUsageLimitNotice:
			return True
		self._usageLimitActive = True
		self._lastUsageLimitNotice = notice
		self._latestMessage = notice
		self._latestFullMessage = notice
		self._speakOnce(
			notice, "attention", "attention", priority="urgent", brailleMessage=notice,
		)
		log.info("ChatGPT Desktop Access detected a terminal usage-limit notice")
		return True

	def _popupDialogFromObject(self, obj):
		for _ in range(10):
			if obj is None or getattr(obj, "role", None) == Role.DIALOG:
				return obj
			obj = getattr(obj, "parent", None)
		return None

	def _schedulePopupDialogFocus(self, obj):
		if not self._appFocusState or not _isChatGPTObject(obj):
			return
		try:
			dialog = self._popupDialogFromObject(obj)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not inspect a possible ChatGPT pop-up", exc_info=True)
			return
		if dialog is None or _sameNVDAObject(dialog, self._pendingPopupDialog) or _sameNVDAObject(
			dialog, self._lastFocusedPopupDialog,
		):
			return
		self._pendingPopupDialog = dialog
		self._pendingPopupDialogWindowHandle = self._conversationWindowHandle
		self._pendingPopupInputGeneration = self._conversationEntryCorrectionGeneration
		if self._popupFocusTimer:
			self._popupFocusTimer.Stop()
		self._popupFocusTimer = wx.CallLater(50, self._focusPopupDialog)

	def _focusPopupDialog(self):
		"""Move focus into a newly displayed ChatGPT dialog without activating a control."""
		self._popupFocusTimer = None
		dialog, self._pendingPopupDialog = self._pendingPopupDialog, None
		windowHandle, self._pendingPopupDialogWindowHandle = self._pendingPopupDialogWindowHandle, 0
		if dialog is None:
			return
		if getattr(self, "_pendingPopupInputGeneration", 0) != getattr(self, "_conversationEntryCorrectionGeneration", 0):
			return
		if (
			not self._appFocusState
			or not windowHandle
			or windowHandle != self._conversationWindowHandle
			or not self._conversationWindowIsAvailable(windowHandle)
			or not self._conversationWindowOwnsForeground(windowHandle)
		):
			return
		try:
			focused = api.getFocusObject()
			blockedStates = {getattr(State, name, None) for name in ("INVISIBLE", "UNAVAILABLE", "DEFUNCT")}
			blockedStates.discard(None)
			if blockedStates.intersection(getattr(dialog, "states", ()) or ()):
				return
			if not _isChatGPTObject(focused):
				# A queued popup event must never pull the user back from another app.
				return
			current = focused
			for _ in range(12):
				# Focus already inside the dialog, such as a name being typed, stays put.
				if _sameNVDAObject(current, dialog):
					self._lastFocusedPopupDialog = dialog
					return
				current = getattr(current, "parent", None) if current is not None else None
			pending = [dialog]
			seen = set()
			objects = []
			while pending and len(seen) < 100:
				obj = pending.pop()
				if obj is None or id(obj) in seen:
					continue
				seen.add(id(obj))
				objects.append(obj)
				nextObject = getattr(obj, "next", None) if obj is not dialog else None
				firstChild = getattr(obj, "firstChild", None)
				if nextObject is not None:
					pending.append(nextObject)
				if firstChild is not None:
					pending.append(firstChild)
			text = " ".join(str(getattr(obj, "name", "") or "") for obj in objects)
			permissionPrompt = isPermissionPromptText(text)
			interactiveRoles = (
				Role.EDITABLETEXT, Role.COMBOBOX, Role.LIST, Role.TREEVIEW,
				Role.CHECKBOX, Role.RADIOBUTTON, Role.BUTTON,
			)
			candidates = [obj for obj in objects if getattr(obj, "role", None) in interactiveRoles
				and not blockedStates.intersection(getattr(obj, "states", ()) or ())]
			if permissionPrompt:
				decisions = [obj for obj in candidates if isPermissionDecisionLabel(getattr(obj, "name", ""))]
				# Offer Deny or Reject first so an accidental Enter never approves a command.
				decisions.sort(key=lambda obj: not any(
					word in str(getattr(obj, "name", "") or "").casefold() for word in ("deny", "reject")
				))
				candidates = decisions or candidates
			else:
				useful = [obj for obj in candidates if " ".join(
					str(getattr(obj, "name", "") or "").casefold().split()
				) not in ("close", "cancel", "dismiss")]
				candidates = useful or candidates
			for obj in candidates:
				if not self._conversationWindowOwnsForeground(windowHandle):
					return
				try:
					obj.setFocus()
					self._lastFocusedPopupDialog = dialog
					log.info("ChatGPT Desktop Access focused a ChatGPT pop-up dialog control")
					return
				except Exception:
					continue
			if not self._conversationWindowOwnsForeground(windowHandle):
				return
			dialog.setFocus()
			self._lastFocusedPopupDialog = dialog
			log.info("ChatGPT Desktop Access focused a ChatGPT pop-up dialog")
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not focus the ChatGPT pop-up dialog", exc_info=True)

	def _announcePluginInstallProgress(self, obj):
		try:
			if getattr(obj, "role", None) != Role.PROGRESSBAR or not _isChatGPTObject(obj):
				return False
			parts = []
			current = obj
			for _ancestorLevel in range(7):
				if current is None:
					break
				for attribute in ("name", "value", "description"):
					value = " ".join(str(getattr(current, attribute, "") or "").split())
					if value and value not in parts:
						parts.append(value)
				current = getattr(current, "parent", None)
			parsed = pluginInstallProgress(" ".join(parts))
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not inspect a plug-in progress event", exc_info=True)
			return False
		if parsed is None:
			return False
		identity, percent, bucket = parsed
		if self._pluginProgressBuckets.get(identity, object()) == bucket:
			return True
		if len(self._pluginProgressBuckets) >= 32 and identity not in self._pluginProgressBuckets:
			expiredIdentity = next(iter(self._pluginProgressBuckets))
			self._pluginProgressBuckets.pop(expiredIdentity)
			self._pluginProgressOwnedBusy.discard(expiredIdentity)
		self._pluginProgressBuckets[identity] = bucket
		if percent is None:
			message = _("Plugin installation in progress")
		elif percent >= 100:
			message = _("Plugin installation complete")
		else:
			message = _("Plugin installation {percent} percent").format(percent=percent)
		complete = percent is not None and percent >= 100
		busy, ownsBusy = pluginProgressBusyTransition(
			self._busy, identity in self._pluginProgressOwnedBusy, complete,
		)
		if ownsBusy:
			self._pluginProgressOwnedBusy.add(identity)
		else:
			self._pluginProgressOwnedBusy.discard(identity)
		self._setBusy(busy, "plugin installation progress")
		self._activeCategory = "tool"
		self._latestMessage = self._latestFullMessage = message
		self._speakOnce(message, "tool", "tool", brailleMessage=message)
		log.info("ChatGPT Desktop Access announced plug-in installation progress")
		return True

	def _resetEmbeddedBrowserProgress(self):
		"""Discard page-specific loading state after browser exit or app shutdown."""
		if self._embeddedBrowserLoadTimer:
			self._embeddedBrowserLoadTimer.Stop()
			self._embeddedBrowserLoadTimer = None
		self._embeddedBrowserLoadGeneration += 1
		self._embeddedBrowserLoadingPercent = None
		self._embeddedBrowserLoading = False
		self._embeddedBrowserBusySeen = False
		self._embeddedBrowserLoadIdentity = ""
		self._embeddedBrowserCompletedIdentity = ""
		self._embeddedBrowserProgressBuckets.clear()

	def _embeddedBrowserDocumentIdentity(self, obj):
		"""Return a stable-enough identity without walking or reading the page."""
		try:
			title = embeddedBrowserTitle(getattr(obj, "name", ""))
			windowHandle = int(getattr(obj, "windowHandle", 0) or 0)
			uniqueId = int(getattr(obj, "IA2UniqueID", 0) or 0)
		except Exception:
			title = ""
			windowHandle = 0
			uniqueId = 0
		return "{window}:{unique}:{title}".format(
			window=windowHandle, unique=uniqueId, title=title.casefold(),
		), title

	def _scheduleEmbeddedBrowserLoadComplete(self, busy=False):
		if self._embeddedBrowserLoadTimer:
			self._embeddedBrowserLoadTimer.Stop()
		self._embeddedBrowserLoadGeneration += 1
		generation = self._embeddedBrowserLoadGeneration
		self._embeddedBrowserLoadTimer = wx.CallLater(
			BROWSER_BUSY_FALLBACK_MILLISECONDS if busy else BROWSER_LOAD_SETTLE_MILLISECONDS,
			self._completeEmbeddedBrowserLoading, generation,
		)

	def _startEmbeddedBrowserLoading(self, identity, title="", force=False, busy=False):
		"""Announce one load start and schedule a quiet fallback completion."""
		if not _settings()["announceEmbeddedBrowserProgress"]:
			return False
		identity = str(identity or "embedded browser")[:400]
		if busy:
			self._embeddedBrowserBusySeen = True
		if self._embeddedBrowserLoading:
			if identity != self._embeddedBrowserLoadIdentity:
				self._embeddedBrowserLoadIdentity = identity
				self._embeddedBrowserCompletedIdentity = ""
			self._scheduleEmbeddedBrowserLoadComplete(busy=self._embeddedBrowserBusySeen)
			return True
		if not force and identity == self._embeddedBrowserCompletedIdentity:
			return False
		self._embeddedBrowserLoading = True
		self._embeddedBrowserLoadingPercent = 0
		self._embeddedBrowserLoadIdentity = identity
		self._embeddedBrowserCompletedIdentity = ""
		self._embeddedBrowserNotice(_("Loading page"))
		self._scheduleEmbeddedBrowserLoadComplete(busy=self._embeddedBrowserBusySeen)
		log.info("ChatGPT Desktop Access announced embedded browser load start")
		return True

	def _completeEmbeddedBrowserLoading(self, generation=None):
		"""Report completion from a native busy-state change, progress event, or settle timer."""
		if generation is not None and generation != self._embeddedBrowserLoadGeneration:
			return False
		if generation is None and self._embeddedBrowserLoadTimer:
			self._embeddedBrowserLoadTimer.Stop()
		self._embeddedBrowserLoadTimer = None
		if not self._embeddedBrowserLoading:
			return False
		self._embeddedBrowserLoading = False
		self._embeddedBrowserBusySeen = False
		self._embeddedBrowserLoadingPercent = 100
		self._embeddedBrowserCompletedIdentity = self._embeddedBrowserLoadIdentity
		if _settings()["announceEmbeddedBrowserProgress"]:
			self._embeddedBrowserNotice(_("Loading complete"))
			log.info("ChatGPT Desktop Access announced embedded browser load completion")
		return True

	def _noteEmbeddedBrowserDocument(self, obj, force=False):
		"""Observe a nested document without altering focus, actions, or browse mode."""
		if _roleName(obj) != "document" or not _isEmbeddedBrowserObject(obj):
			return False
		identity, title = self._embeddedBrowserDocumentIdentity(obj)
		try:
			busy = State.BUSY in (getattr(obj, "states", ()) or ())
		except Exception:
			busy = False
		return self._startEmbeddedBrowserLoading(identity, title, force=force, busy=busy)

	def _updateEmbeddedBrowserDocumentBusyState(self, obj):
		"""Use Chromium's native busy document state when it is exposed."""
		if _roleName(obj) != "document" or not _isEmbeddedBrowserObject(obj):
			return False
		identity, title = self._embeddedBrowserDocumentIdentity(obj)
		try:
			busy = State.BUSY in (getattr(obj, "states", ()) or ())
		except Exception:
			busy = False
		if busy:
			return self._startEmbeddedBrowserLoading(identity, title, force=True, busy=True)
		if self._embeddedBrowserLoading and self._embeddedBrowserBusySeen:
			return self._completeEmbeddedBrowserLoading()
		return False

	def _findChatGPTPromptObject(self):
		candidates = [self._lastPromptObject, self._pendingPromptObject]
		try:
			candidates.append(api.getFocusObject())
		except Exception:
			pass
		for candidate in tuple(candidates):
			current = candidate
			for _ in range(8):
				if current is None:
					break
				try:
					if _isDefunctObject(current):
						break
					if _isCodexPromptObject(current):
						return current
					current = getattr(current, "parent", None)
				except Exception:
					break
		if self._buffer is not None:
			try:
				position = self._buffer.makeTextInfo(textInfos.POSITION_LAST)
				current = getattr(position, "NVDAObjectAtStart", None)
				for _ in range(10):
					if current is None:
						break
					if _isDefunctObject(current):
						break
					if _isCodexPromptObject(current):
						return current
					current = getattr(current, "parent", None)
			except Exception:
				pass
		return None

	def _embeddedBrowserNotice(self, message):
		now = time.monotonic()
		if shouldSuppressSemanticDuplicate(
			message, self._lastEmbeddedBrowserNotice,
			now - self._lastEmbeddedBrowserNoticeAt,
		):
			return
		self._lastEmbeddedBrowserNotice = message
		self._lastEmbeddedBrowserNoticeAt = now
		conf = _settings()
		_send(message, conf["speech"], conf["braille"], None, False, brailleMessage=message)

	def _updateEmbeddedBrowserFocus(self, obj):
		inBrowser = _isEmbeddedBrowserObject(obj)
		if inBrowser == self._embeddedBrowserFocused:
			return
		wasInBrowser = self._embeddedBrowserFocused
		self._embeddedBrowserFocused = inBrowser
		if wasInBrowser and not inBrowser:
			self._resetEmbeddedBrowserProgress()

	def _announceEmbeddedBrowserProgress(self, obj):
		if not _settings()["announceEmbeddedBrowserProgress"]:
			return
		if getattr(obj, "role", None) != Role.PROGRESSBAR or not _isEmbeddedBrowserObject(obj):
			return
		parsed = embeddedBrowserProgress(
			getattr(obj, "name", ""), getattr(obj, "value", ""), getattr(obj, "description", ""),
		)
		if parsed is None:
			return
		identity, percent, _bucket = parsed
		self._embeddedBrowserLoadingPercent = percent
		progressIdentity = "progress:{identity}".format(identity=identity)
		if percent is not None and percent >= 100:
			if not self._embeddedBrowserLoading:
				self._embeddedBrowserLoadIdentity = progressIdentity
				self._embeddedBrowserLoading = True
			self._completeEmbeddedBrowserLoading()
		else:
			self._startEmbeddedBrowserLoading(progressIdentity, force=True)

	def _performChatHistoryAction(self, title, action, source="recent", mode=None):
		mode = mode or self._conversationMode
		agentName = _("ChatGPT") if mode == "chatgpt" else _("Codex")
		if mode not in ("chatgpt", "codex") or mode != self._conversationMode:
			ui.message(_("The chat-history mode changed. Open chat history again"))
			return
		if not self._conversationWindowIsAvailable(self._conversationWindowHandle):
			log.debug("ChatGPT Desktop Access ignored a chat-history action after its window closed")
			return
		if source == "recent" and " ".join(str(title or "").casefold().split()) in self._ambiguousRecentChatTitles[mode]:
			ui.message(_(
				"More than one recent chat has this title. Choose one from the native Recents list"
			))
			return
		if source == "archived" and mode == "codex":
			threadUrl = codexThreadUrl(self._archivedChatIds[mode].get(title))
			if not threadUrl:
				log.debugWarning("ChatGPT Desktop Access has no valid thread ID for the selected archived chat")
				ui.message(_("The selected archived {agent} chat could not be opened").format(agent=agentName))
				return
			try:
				self._pendingOpenedChatTitle = title
				self._pendingOpenedChatAt = time.monotonic()
				opened = wx.LaunchDefaultBrowser(threadUrl)
			except Exception:
				opened = False
				log.debugWarning("ChatGPT Desktop Access could not launch the archived task link", exc_info=True)
			if opened:
				log.info("ChatGPT Desktop Access opened an archived task with the native Codex thread link")
				self._scheduleUnarchiveButtonFocus()
			else:
				self._pendingOpenedChatTitle = ""
				self._pendingOpenedChatAt = 0.0
				ui.message(_("The selected archived {agent} chat could not be opened").format(agent=agentName))
			return
		try:
			if action in ("pin", "archive"):
				self._startDirectChatAction(title, action)
				return
			button = self._chatButtonObject(title)
			if button is None:
				raise LookupError("selected chat button not found")
			self._pendingOpenedChatTitle = title
			self._pendingOpenedChatAt = time.monotonic()
			_pressControl(button)
			log.info("ChatGPT Desktop Access performed chat history action: %s", action)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not act on the selected chat", exc_info=True)
			ui.message(_("The selected {agent} chat could not be opened").format(agent=agentName))

	def _queueChatHistoryAction(self, title, action, source, mode):
		self._pendingChatHistoryAction = (title, action, source, mode)

	def _chatHistoryClosed(self):
		self._chatHistoryDialog = None
		self._chatHistoryDialogMode = ""
		gui.mainFrame.postPopup()
		pending, self._pendingChatHistoryAction = self._pendingChatHistoryAction, None
		if pending:
			self._chatHistoryActionTimer = wx.CallLater(
				100, self._runChatHistoryAction, *pending,
			)

	def _runChatHistoryAction(self, title, action, source, mode):
		self._chatHistoryActionTimer = None
		self._performChatHistoryAction(title, action, source, mode)

	def _announceChatOpened(self, title, windowHandle):
		# History and the document watcher can report the same chat switch.
		message = _("Chat opened: {title}").format(title=title) if title else _("New chat opened")
		self._latestMessage = self._latestFullMessage = message
		now = time.monotonic()
		key = windowHandle, " ".join(title.casefold().split())
		previous = self._lastChatOpened
		if title and previous is not None and previous[0] == key and now - previous[1] < 2.0:
			return
		self._lastChatOpened = key, now
		self._speakOnce(message, "other", "other", brailleMessage=message)

	def _rememberBuffer(self, obj, allowUnclassifiedConversation=False):
		if not _isChatGPTObject(obj):
			return False
		if _isNativeCommonDialogObject(obj):
			# The Windows Select files dialog is owned by ChatGPT.exe, but has no
			# Chromium conversation buffer. Following its UIA/IA2 parents can stall
			# NVDA's main thread while the chooser is opening.
			return False
		if self._buffer is None and getattr(self, "_conversationClosedAt", 0.0):
			# Chromium can emit document events after Electron's top-level window was
			# closed. Do not recreate background monitoring from those orphaned events.
			# A genuine return to ChatGPT (or an explicit command made there) is enough
			# to permit attachment again.
			try:
				appActuallyFocused = _isChatGPTObject(api.getFocusObject())
			except Exception:
				appActuallyFocused = False
			if not appActuallyFocused and not allowUnclassifiedConversation:
				log.debug("ChatGPT Desktop Access ignored a background buffer after window closure")
				return False
		mode = None
		for current in self._bufferCandidates(obj):
			buffer = getattr(current, "treeInterceptor", None)
			if not buffer:
				continue
			if buffer is self._buffer and self._conversationModeObserved:
				# Mode events are handled independently. Navigation inside the
				# retained document needs only a cheap live-window check, not
				# repeated mode/browser ancestry queries for every focused control.
				return self._conversationWindowIsAvailable(self._conversationWindowHandle)
			if mode is None:
				explicitMode = _switchControlMode(obj)
				mode = _conversationModeForObject(obj)
				isPrompt = _isCodexPromptObject(obj)
				isEmbeddedBrowser = False if isPrompt else _isEmbeddedBrowserObject(obj)
			candidateMode = mode if current is obj else _conversationModeForObject(current)
			if not (mode or candidateMode or isPrompt):
				if not allowUnclassifiedConversation or isEmbeddedBrowser:
					continue
				try:
					# Conversation document names are task titles in current ChatGPT builds.
					# For an explicit app-scoped command, inspect only the bounded tail where
					# the primary prompt lives instead of requiring focus to reach that prompt.
					conversationTail = buffer.makeTextInfo(textInfos.POSITION_LAST)
					_extendScanStart(conversationTail, BUFFER_TAIL_SCAN_CHARACTERS)
					if not looksLikeCodexConversation(conversationTail.text):
						continue
				except Exception:
					continue
			# The embedded browser has its own Chromium tree interceptor. Only run the
			# ancestry check once, skip its nested document, and continue until the
			# outer ChatGPT/Codex conversation document is found.
			if isEmbeddedBrowser and not candidateMode:
				continue
			resolvedMode = mode or candidateMode
			candidateWindowHandle = self._conversationWindowHandleFrom(obj, buffer)
			if not self._conversationWindowIsAvailable(candidateWindowHandle):
				now = time.monotonic()
				if now - self._lastRejectedBufferLogAt >= 30.0:
					self._lastRejectedBufferLogAt = now
					log.debug("ChatGPT Desktop Access ignored a buffer from a closed or hidden window")
				continue
			self._lastRejectedBufferLogAt = 0.0
			if explicitMode:
				self._setConversationMode(explicitMode, "mode switch control event", authoritative=True)
			differentWindow = bool(
				self._conversationWindowHandle and candidateWindowHandle
				and candidateWindowHandle != self._conversationWindowHandle
			)
			if differentWindow and not explicitMode:
				# A different top-level application window needs a fresh authoritative
				# mode observation. Within one ChatGPT window, its document remains named
				# ChatGPT in both modes and therefore cannot override the switch control.
				self._conversationModeObserved = False
				self._conversationModeObservedAt = 0.0
			if resolvedMode and not self._conversationModeObserved:
				self._setConversationMode(resolvedMode, "conversation document")
			wasMissing = self._buffer is None
			bufferChanged = self._buffer is not None and buffer is not self._buffer
			if bufferChanged:
				# A prompt from the previous virtual buffer cannot safely anchor
				# message review in the new buffer, even if Chromium kept it alive.
				self._lastPromptObject = None
				title = pendingChatTitle(
					self._pendingOpenedChatTitle,
					time.monotonic() - self._pendingOpenedChatAt if self._pendingOpenedChatAt else float("inf"),
				)
				self._pendingOpenedChatTitle = ""
				self._pendingOpenedChatAt = 0.0
				bufferSampleComplete = False
				try:
					# The end of the document contains the prompt and newest turns. Reading
					# only a bounded tail is sufficient to distinguish a blank chat and avoids
					# copying an entire large transcript on NVDA's main thread merely because
					# Chromium rebuilt its virtual-buffer object.
					position = buffer.makeTextInfo(textInfos.POSITION_LAST)
					moved = _extendScanStart(position, BUFFER_TAIL_SCAN_CHARACTERS)
					bufferText = position.text
					# Absence of message markers proves the chat is blank only when this
					# bounded range reached the document start. A truncated long response
					# may legitimately have its speaker heading outside the sampled tail.
					bufferSampleComplete = abs(moved) < BUFFER_TAIL_SCAN_CHARACTERS
				except Exception:
					bufferText = ""
				conversationChanged = bool(
					title or (bufferSampleComplete and looksLikeBlankCodexConversation(bufferText))
				)
				if conversationChanged:
					self._documentSwitchCount += 1
					self._resetTaskState("document changed")
					self._announceChatOpened(title, candidateWindowHandle)
					log.info("ChatGPT Desktop Access detected a newly opened chat document")
				else:
					log.debug("ChatGPT Desktop Access refreshed the Chromium virtual buffer without resetting task state")
			if self._buffer is not buffer:
				self._unsupportedScanBuffer = None
				self._bindNativeTaskTimer(buffer)
			self._buffer = buffer
			if wasMissing or bufferChanged:
				self._conversationWindowHandle = candidateWindowHandle
				self._conversationWindowProcessId = self._windowProcessId(candidateWindowHandle)
				self._conversationWindowUnavailableAt = 0.0
				self._conversationClosedAt = 0.0
				self._bufferDirty = True
				self._lastBufferInspectionAt = 0.0
				self._lastBufferInspectionSeconds = 0.0
				self._lastScannedLabel = ""
				self._queueConversationModeProbe("mode switch UI Automation probe")
			if wasMissing:
				log.info("ChatGPT Desktop Access attached to %s", type(buffer).__name__)
				log.info("ChatGPT Desktop Access: ChatGPT app %s", self._chatGPTAppVersion())
				self._scheduleCompatibilityCheck()
			if not self._monitoringAnnounced:
				self._monitoringAnnounced = True
				conf = _settings()
				_send(_("Activity monitoring active"), conf["speech"], conf["braille"], None, False)
			return True
		return False

	def _updateAppFocusState(self, obj):
		appFocused = _isChatGPTObject(obj)
		self._appFocusState, cue = focusStateTransition(self._appFocusState, appFocused)
		if cue == "active":
			# Foreground and real-focus events arrive separately in Chromium. Keep a
			# short one-shot window so the later activity-button focus can be corrected.
			self._conversationActivatedAt = time.monotonic()
			self._conversationEntryCorrectionGeneration += 1
		if cue == "inactive":
			self._conversationActivatedAt = 0.0
			self._conversationEntryCorrectionGeneration += 1
			if self._popupFocusTimer:
				self._popupFocusTimer.Stop()
				self._popupFocusTimer = None
			self._pendingPopupDialog = None
			self._pendingPopupDialogWindowHandle = 0
			self._resetAttachmentMenuTracking()
			self._cancelAttachmentSourceFocus()
			self._promptFocused = False
			self._brailleCompositionActive = False
			self._promptTypingUntil = 0.0
			self._conversationNavigationUntil = 0.0
			if self._promptInspectionTimer:
				self._promptInspectionTimer.Stop()
				self._promptInspectionTimer = None
			self._pendingPromptObject = None
		conf = _settings()
		if not cue or self._paused or not conf["monitoringFocusClicks"] or not conf["soundWhenSpeechUnavailable"]:
			return cue
		category = "monitoringActive" if cue == "active" else "monitoringInactive"
		_playProgressSound(category, cue, conf["progressSoundStyle"], conf["clickVolume"])
		return cue

	def _scheduleConversationEntryCorrection(self, obj):
		"""Queue one browse-caret correction for Chromium's stale activity focus."""
		activatedAt = self._conversationActivatedAt
		if not activatedAt:
			return False
		roleName = _roleName(obj)
		if roleName in ("window", "document", "pane"):
			# These are normal intermediate focus events while Alt+Tab settles.
			return False
		if time.monotonic() - activatedAt > CONVERSATION_ENTRY_CORRECTION_SECONDS:
			self._conversationActivatedAt = 0.0
			return False
		label = " ".join(str(getattr(obj, "name", "") or "").split())
		category, _message = statusDetails(label)
		if (
			roleName != "button"
			or not category
			or self._isSidebarChatButton(obj, label)
			or not self._busy
			or not self._conversationBrowseModeActive()
		):
			self._conversationActivatedAt = 0.0
			self._conversationEntryCorrectionGeneration += 1
			return False
		self._conversationActivatedAt = 0.0
		self._conversationEntryCorrectionGeneration += 1
		generation = self._conversationEntryCorrectionGeneration
		queueHandler.queueFunction(
			queueHandler.eventQueue,
			self._restoreLatestConversationPosition,
			label,
			generation,
		)
		return True

	def _restoreLatestConversationPosition(self, activityLabel, generation):
		"""Move only the virtual caret from a stale activity card to newer output."""
		global _activePluginInstance
		if (
			_activePluginInstance is not self
			or generation != self._conversationEntryCorrectionGeneration
			or not self._busy
			or not self._conversationBrowseModeActive()
		):
			return False
		try:
			focus = api.getFocusObject()
			focusLabel = " ".join(str(getattr(focus, "name", "") or "").split())
			if (
				not _isChatGPTObject(focus)
				or _roleName(focus) != "button"
				or focusLabel != activityLabel
				or not statusDetails(focusLabel)[0]
			):
				return False
			self._rememberBuffer(focus)
			if not self._buffer:
				return False
			focusInfo = self._buffer.makeTextInfo(focus)
			focusInfo.collapse()
			# Anchor the reverse search at the active composer. Chromium may retain an
			# inactive fork after it in the same document, and POSITION_LAST would move
			# the user into that hidden branch.
			prompt = self._findChatGPTPromptObject()
			if prompt is None:
				return False
			latest = self._buffer.makeTextInfo(prompt)
			latest.collapse()
			_extendScanStart(latest, RECENT_CHAT_INITIAL_SCAN_CHARACTERS)
			if not latest.find("ChatGPT said:", reverse=True, caseSensitive=False):
				return False
			latest.collapse()
			if latest.compareEndPoints(focusInfo, "startToStart") <= 0:
				return False
			# updateCaret changes the browse position without moving Windows focus.
			# Align object navigation as well so Braille and subsequent navigation begin
			# at the same newest response heading.
			latest.updateCaret()
			latestObject = getattr(latest, "NVDAObjectAtStart", None)
			if latestObject is not None:
				api.setNavigatorObject(latestObject)
			self._conversationNavigationUntil = max(
				self._conversationNavigationUntil,
				time.monotonic() + CONVERSATION_NAVIGATION_QUIET_SECONDS,
			)
			log.info("ChatGPT Desktop Access moved the browse position past a stale activity card")
			return True
		except Exception:
			log.debugWarning(
				"ChatGPT Desktop Access could not correct the restored conversation position",
				exc_info=True,
			)
			return False

	def _resetAttachmentMenuTracking(self):
		if self._attachmentMenuActiveAt:
			self._attachmentMenuLastClosedAt = time.monotonic()
		self._attachmentMenuActiveAt = 0.0
		self._attachmentMenuButtonFocusedAt = 0.0
		self._lastAttachmentMenuItem = ""
		self._lastAttachmentMenuItemAt = 0.0

	def _cancelAttachmentSourceFocus(self):
		self._attachmentActivationAt = 0.0
		self._attachmentInputCandidateAt = 0.0
		self._attachmentInputCandidateWindowHandle = 0
		self._attachmentSourcePendingButton = None
		if self._attachmentSourceFocusTimer:
			self._attachmentSourceFocusTimer.Stop()
			self._attachmentSourceFocusTimer = None

	def _isAddFilesButton(self, obj):
		try:
			return bool(
				obj is not None and _roleName(obj) == "button"
				and promptControlKind(getattr(obj, "name", "")) == "files"
				and _isChatGPTObject(obj)
			)
		except Exception:
			return False

	def _attachmentButtonIsCurrent(self):
		"""Return the actual focused or browse-caret button, never a stale event."""
		try:
			focus = api.getFocusObject()
			if not _isChatGPTObject(focus):
				return False
			if self._isAddFilesButton(focus):
				return focus
			# The first Enter in a browse-mode conversation can arrive before our
			# background monitor has attached its copy of the virtual buffer.
			buffer = self._buffer or getattr(focus, "treeInterceptor", None)
			if buffer is None or getattr(buffer, "passThrough", True):
				return False
			position = buffer.makeTextInfo(textInfos.POSITION_CARET)
			current = getattr(position, "NVDAObjectAtStart", None)
			for _ in range(8):
				if current is None:
					break
				if self._isAddFilesButton(current):
					return current
				current = getattr(current, "parent", None)
		except Exception:
			log.debug("ChatGPT Desktop Access could not verify the Add files browse position")
		return False

	def _noteAttachmentActivationGesture(self, identifiers):
		"""Arm one focus move only for an explicit Enter or Space on Add files."""
		activation = any(
			isPromptSubmissionGestureIdentifier(identifier)
			or str(identifier or "").casefold().endswith(":space")
			for identifier in identifiers
		)
		if not activation:
			if self._attachmentActivationAt or self._attachmentSourceFocusTimer:
				self._cancelAttachmentSourceFocus()
			return
		buffer = self._buffer
		if buffer is None and getattr(self, "_promptFocused", False):
			try:
				buffer = getattr(api.getFocusObject(), "treeInterceptor", None)
			except Exception:
				buffer = None
		if getattr(self, "_promptFocused", False) and getattr(buffer, "passThrough", True):
			# Space in the edit field is a hot path, particularly with Braille input.
			# Do not query Chromium's browse caret for every typed word.
			if self._attachmentActivationAt or self._attachmentSourceFocusTimer:
				self._cancelAttachmentSourceFocus()
			return
		self._logAttachmentButtonPress()
		button = self._attachmentButtonIsCurrent()
		if not button:
			# Chromium can replace the browse caret before the input observer runs.
			# A recent Enter is only a candidate: the exact Add files expanded
			# event must still arrive before we move focus anywhere.
			try:
				focus = api.getFocusObject()
				buffer = self._buffer or getattr(focus, "treeInterceptor", None)
				unattachedBrowse = (
					self._buffer is None and _isChatGPTObject(focus)
					and buffer is not None and not getattr(buffer, "passThrough", True)
				)
			except Exception:
				unattachedBrowse = False
			if unattachedBrowse:
				self._cancelAttachmentSourceFocus()
				self._attachmentActivationAt = time.monotonic()
				log.debug("ChatGPT Desktop Access armed attachment focus pending the Add files expansion")
				return
			if self._attachmentActivationAt or self._attachmentSourceFocusTimer:
				self._cancelAttachmentSourceFocus()
			return
		self._cancelAttachmentSourceFocus()
		self._attachmentActivationAt = time.monotonic()
		# Browse-mode activation does not consistently produce a state-change
		# event. Retain the exact control and finish after focus returns to the
		# prompt and the conversation buffer has attached.
		self._attachmentSourcePendingButton = button
		self._attachmentDiagnostics.noteButtonActivated(button, "Enter or Space on Add files and more")
		log.debug("ChatGPT Desktop Access armed native attachment-menu focus from an explicit gesture")

	def _logAttachmentButtonPress(self):
		"""Write one support line when Enter or Space lands on a files-like ChatGPT button.

		This goes to NVDA's normal log so a support log shows where Add files and
		more stopped. Only control names and states are written, never chat text
		or conversation titles.
		"""
		try:
			focus = api.getFocusObject()
			if not _isChatGPTObject(focus):
				return
			target = focus
			buffer = self._buffer or getattr(focus, "treeInterceptor", None)
			browseMode = buffer is not None and not getattr(buffer, "passThrough", True)
			if browseMode and _roleName(focus) not in ("button", "menubutton"):
				caret = buffer.makeTextInfo(textInfos.POSITION_CARET)
				target = getattr(caret, "NVDAObjectAtStart", None) or focus
			for _ancestorLevel in range(4):
				if target is None or _roleName(target) in ("button", "menubutton"):
					break
				target = getattr(target, "parent", None)
			name = " ".join(str(getattr(target, "name", "") or "").split())
			if target is None or _roleName(target) not in ("button", "menubutton") or not isAttachmentButtonLikeLabel(name):
				return
			states = sorted(getattr(state, "name", str(state)).casefold() for state in (getattr(target, "states", ()) or ()))
			log.info(
				"ChatGPT Desktop Access: Enter or Space on %r (%s; states %s); recognized as Add files and more: %s; "
				"conversation attached: %s (%s); mode: %s; browse mode: %s",
				name, _roleName(target), ", ".join(states) or "none", self._isAddFilesButton(target),
				self._buffer is not None, type(self._buffer).__name__ if self._buffer is not None else "none",
				self._conversationMode or "unknown", browseMode,
			)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not log the attachment button press", exc_info=True)

	def _captureAttachmentActivationFromQueuedGesture(self, identifiers, candidateAt, windowHandle):
		"""Inspect the browse caret on NVDA's main thread, before Chromium may replace it."""
		if (
			candidateAt != self._attachmentInputCandidateAt
			or windowHandle != self._conversationWindowHandle
			or not self._appFocusState
			or self._attachmentSourceFocusTimer
			or self._attachmentSourcePendingButton
		):
			return
		if self._attachmentButtonIsCurrent():
			self._noteAttachmentActivationGesture(identifiers)

	def _attachmentSourceMenuObject(self, buffer):
		"""Resolve the exact native Sources menu button from the buffer tail."""
		position = buffer.makeTextInfo(textInfos.POSITION_LAST)
		if not position.find(SOURCES_MENU_BUTTON_NAME, reverse=True, caseSensitive=False):
			return None
		current = getattr(position, "NVDAObjectAtStart", None)
		for _ in range(8):
			if current is None:
				break
			if (
				_roleName(current) in ("menubutton", "button")
				and " ".join(str(getattr(current, "name", "") or "").casefold().split())
				== "attach files or connect apps"
				and _isChatGPTObject(current)
			):
				return current
			current = getattr(current, "parent", None)
		return None

	def _attachmentPopupAnchor(self, buffer):
		"""Return a caret position at the popup's "Type to search files" text.

		ChatGPT adds the popup at the end of the page and keeps keyboard focus in
		the prompt, where arrows move an unannounced highlight. The options are
		readable in browse mode, so the browse cursor is placed at the popup.
		"""
		try:
			position = buffer.makeTextInfo(textInfos.POSITION_LAST)
			if not position.find("search files", reverse=True, caseSensitive=False):
				return None
			if _isCodexPromptObject(getattr(position, "NVDAObjectAtStart", None)):
				return None
			position.collapse()
			return position
		except Exception:
			log.debug("ChatGPT Desktop Access could not find the attachment popup text", exc_info=True)
			return None

	def _readAttachmentPopupOptions(self, buffer):
		"""Read the popup's sections and option buttons from the end of the document."""
		if not _isVirtualBufferDocument(buffer):
			return self._readAttachmentPopupOptionsWithUIA(buffer)
		def isPromptField(field):
			return field.get("role") == Role.EDITABLETEXT and isCodexPromptLabel(field.get("name", ""))

		def isOptionField(field):
			if field.get("role") not in (Role.BUTTON, Role.MENUITEM, Role.LISTITEM, Role.LINK, Role.CHECKBOX):
				return False
			name = " ".join(str(field.get("name", "") or "").split())
			# Prompt-toolbar controls are not popup options.
			return not (name and (promptControlKind(name) or voiceControlKind(name) or isKnownNonStatusButton(name)))

		try:
			position = buffer.makeTextInfo(textInfos.POSITION_LAST)
			_extendScanStart(position, ATTACHMENT_POPUP_SCAN_CHARACTERS)
			tokens = []
			for item in position.getTextWithFields():
				if isinstance(item, str):
					tokens.append(("text", item))
				elif getattr(item, "command", "") == "controlStart":
					tokens.append(("start", getattr(item, "field", {}) or {}))
				elif getattr(item, "command", "") == "controlEnd":
					tokens.append(("end", None))
			options = attachmentPopupOptions(tokens, isPromptField, isOptionField)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not read the Add files and more options", exc_info=True)
			options = ()
		if options and options[0].get("classBased"):
			return options
		# NVDA's UI Automation document mode carries no class names, so rows,
		# headings and the highlight are read from UI Automation directly.
		return self._readAttachmentPopupOptionsWithUIA(buffer) or options

	def _attachmentPopupStructure(self, buffer):
		"""Describe the controls after the prompt for the log, without names or text."""
		if not _isVirtualBufferDocument(buffer):
			return "not read in NVDA's UI Automation document"
		try:
			position = buffer.makeTextInfo(textInfos.POSITION_LAST)
			_extendScanStart(position, ATTACHMENT_POPUP_SCAN_CHARACTERS)
			tokens = [
				("start", getattr(item, "field", {}) or {})
				for item in position.getTextWithFields()
				if getattr(item, "command", "") == "controlStart"
			]
			return attachmentPopupStructureSummary(
				tokens,
				lambda field: field.get("role") == Role.EDITABLETEXT and (
					isCodexPromptLabel(field.get("name", ""))
					or CHATGPT_PROMPT_EDITOR_CLASS in str(field.get(ATTACHMENT_POPUP_CLASS_KEY, "") or "").split()
				),
			)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not summarize the page after the prompt", exc_info=True)
			return "unreadable"

	def _readAttachmentPopupOptionsWithUIA(self, buffer):
		"""Read the popup's rows, headings and highlight through UI Automation."""
		# ChatGPT re-renders the popup just after it opens, which can leave a row
		# unreadable partway through; read again from the start when that happens.
		for attempt in range(3):
			try:
				return self._readAttachmentPopupRowsWithUIA(buffer)
			except Exception:
				if attempt == 2:
					log.debugWarning("ChatGPT Desktop Access could not read the Add files and more options through UI Automation", exc_info=True)
		return ()

	def _readAttachmentPopupRowsWithUIA(self, buffer):
		"""Read the popup once through UI Automation; raises if it goes away."""
		import UIAHandler
		handler = UIAHandler.handler
		client = handler.clientObject
		rootObject = getattr(buffer, "rootNVDAObject", None)
		root = getattr(rootObject, "UIAElement", None)
		if root is None:
			windowHandle = getattr(rootObject, "windowHandle", 0) or self._conversationWindowHandle
			root = client.ElementFromHandle(windowHandle) if windowHandle else None
		if root is None:
			return ()
		hintCondition = client.createOrConditionFromArray([
			client.createPropertyCondition(UIAHandler.UIA_NamePropertyId, label)
			for label in ATTACHMENT_POPUP_HINT_LABELS
		])
		hint = root.FindFirst(UIAHandler.TreeScope_Descendants, hintCondition)
		rowsNeeded = 1
		if not hint:
			# Some ChatGPT versions have no "Type to search" text. Start from the
			# last row button instead, and widen until every row button is inside.
			classRequest = client.CreateCacheRequest()
			classRequest.AddProperty(UIAHandler.UIA_ClassNamePropertyId)
			buttons = root.FindAllBuildCache(
				UIAHandler.TreeScope_Descendants,
				client.createPropertyCondition(UIAHandler.UIA_ControlTypePropertyId, UIAHandler.UIA_ButtonControlTypeId),
				classRequest,
			)
			rowButtons = [
				buttons.GetElement(index) for index in range(buttons.Length if buttons else 0)
				if ATTACHMENT_POPUP_ROW_CLASS in str(buttons.GetElement(index).GetCachedPropertyValue(UIAHandler.UIA_ClassNamePropertyId) or "")
			]
			if not rowButtons:
				return ()
			hint = rowButtons[-1]
			rowsNeeded = len(rowButtons)
		# Raw view: ChatGPT's section headings are unnamed groups that the
		# control view leaves out. The popup is read from one cached snapshot,
		# because ChatGPT replaces rows while it settles.
		walker = client.RawViewWalker
		cacheRequest = client.CreateCacheRequest()
		cacheRequest.AddProperty(UIAHandler.UIA_NamePropertyId)
		cacheRequest.AddProperty(UIAHandler.UIA_ClassNamePropertyId)
		cacheRequest.TreeScope = UIAHandler.TreeScope_Subtree
		cacheRequest.TreeFilter = client.RawViewCondition

		def cachedChildren(element):
			children = element.GetCachedChildren()
			return [children.GetElement(index) for index in range(children.Length if children else 0)]

		def cachedText(element, propertyId):
			return str(element.GetCachedPropertyValue(propertyId) or "")

		def popupElements(container):
			found = []
			pending = [(child, 1) for child in reversed(cachedChildren(container))]
			while pending and len(found) < 600:
				element, depth = pending.pop()
				found.append((element, cachedText(element, UIAHandler.UIA_ClassNamePropertyId)))
				if depth < 4:
					pending.extend((child, depth + 1) for child in reversed(cachedChildren(element)))
			return found

		container = hint
		for _ancestorLevel in range(6):
			container = walker.GetParentElement(container)
			if not container:
				return ()
			elements = popupElements(container.BuildUpdatedCache(cacheRequest))
			if sum(ATTACHMENT_POPUP_ROW_CLASS in className for _element, className in elements) >= rowsNeeded:
				break
		else:
			return ()
		rows = []
		for element, className in elements:
			if ATTACHMENT_POPUP_ROW_CLASS not in className and ATTACHMENT_POPUP_HEADER_CLASS not in className:
				continue
			# Titles, descriptions and section names are separate text children.
			texts = [cachedText(child, UIAHandler.UIA_NamePropertyId) for child in cachedChildren(element)[:8]]
			rows.append((className, cachedText(element, UIAHandler.UIA_NamePropertyId), texts))
		return attachmentPopupOptionsFromRows(rows)

	def _showAttachmentMenuDialog(self, options, button, windowHandle):
		"""Present the popup's options as a native list."""
		if self._attachmentMenuDialog:
			self._attachmentMenuDialog.Raise()
			return
		self._attachmentMenuButton = button
		self._attachmentMenuWindowHandle = windowHandle
		gui.mainFrame.prePopup()
		try:
			self._attachmentMenuDialog = AttachmentMenuDialog(
				gui.mainFrame, options, self._attachmentMenuDialogClosed,
			)
			self._attachmentMenuDialog.Show()
		except Exception:
			self._attachmentMenuDialog = None
			gui.mainFrame.postPopup()
			raise
		log.info("ChatGPT Desktop Access listed %d Add files and more options", len(options))

	def _attachmentMenuDialogClosed(self, chosen):
		self._attachmentMenuDialog = None
		gui.mainFrame.postPopup()
		if chosen is not None:
			# Let Windows return the foreground to ChatGPT before clicking the option.
			wx.CallLater(400, self._activateAttachmentOption, chosen, 0, False)
		else:
			wx.CallLater(250, self._closeAttachmentPopup)

	def _activateAttachmentOption(self, option, attempt, reopened):
		"""Choose the option with the popup's own keyboard handling from the prompt.

		Clicking options from outside proved unreliable: ChatGPT closes its popup
		when the list takes focus and ignores clicks on the closing popup. With the
		popup open and focus in the prompt, its highlight starts on the first
		option, Down Arrow moves it, and Tab chooses it.
		"""
		windowHandle = self._attachmentMenuWindowHandle
		if windowHandle != self._conversationWindowHandle or not self._conversationWindowIsAvailable(windowHandle):
			ui.message(_("ChatGPT closed or changed; nothing was chosen"))
			return
		if not self._conversationWindowOwnsForeground(windowHandle):
			if attempt < ATTACHMENT_OPTION_ACTIVATION_ATTEMPTS:
				if attempt == 0:
					try:
						winUser.setForegroundWindow(windowHandle)
					except Exception:
						pass
				wx.CallLater(ATTACHMENT_OPTION_STEP_MILLISECONDS, self._activateAttachmentOption, option, attempt + 1, reopened)
				return
			ui.message(_("ChatGPT is not in the foreground; nothing was chosen"))
			return
		focusInPrompt = _isCodexPromptObject(api.getFocusObject())
		button = self._currentAddFilesButton(self._attachmentMenuButton)
		popupOpen = self._addFilesPopupIsOpen(button)
		# The first check right after ChatGPT returns can see a popup that is still
		# closing, so always let focus settle once before acting.
		if attempt == 0 or not (popupOpen and focusInPrompt):
			if attempt < ATTACHMENT_OPTION_ACTIVATION_ATTEMPTS:
				if attempt > 0 and not popupOpen and not reopened and (focusInPrompt or attempt >= 3):
					reopened = self._reopenAttachmentPopup(button)
				wx.CallLater(ATTACHMENT_OPTION_STEP_MILLISECONDS, self._activateAttachmentOption, option, attempt + 1, reopened)
				return
			log.info(
				"ChatGPT Desktop Access could not choose an Add files and more option: "
				"button found %s, popup open %s, focus in prompt %s, popup reopened %s",
				button is not None, popupOpen, focusInPrompt, reopened,
			)
			ui.message(_("{option} could not be chosen. Open Add files and more again").format(option=option["title"]))
			return
		buffer = self._buffer
		current = self._readAttachmentPopupOptions(buffer) if buffer is not None else ()
		index = findAttachmentOption(current, option)
		if index is None:
			log.info(
				"ChatGPT Desktop Access could not choose an Add files and more option: "
				"popup open with %d options, no match", len(current),
			)
			ui.message(_("{option} could not be chosen. Open Add files and more again").format(option=option["title"]))
			return
		if any(candidate.get("highlighted") for candidate in current):
			self._stepToAttachmentOption(option, 0)
			return
		# ChatGPT did not expose its highlight: count from the first row, where the
		# highlight starts. Tab is used instead of Enter, which could send the prompt.
		for _step in range(index):
			keyboardHandler.KeyboardInputGesture.fromName("downArrow").send()
		keyboardHandler.KeyboardInputGesture.fromName("tab").send()
		log.info(
			"ChatGPT Desktop Access chose Add files and more option position %d of %d by counting",
			index + 1, len(current),
		)
		wx.CallLater(ATTACHMENT_OPTION_CONFIRM_MILLISECONDS, self._confirmAttachmentChoice, option)

	def _stepToAttachmentOption(self, option, step, awaitingFrom=None, waits=0):
		"""Move ChatGPT's highlight one row at a time and press Tab only on the chosen row.

		NVDA's copy of the page shows a new highlight shortly after ChatGPT moves
		it. After each key, wait until the highlight has moved away from the row it
		was on, so a stale reading can never cause an extra key press.
		"""
		if (
			not self._conversationWindowOwnsForeground(self._attachmentMenuWindowHandle)
			or not _isCodexPromptObject(api.getFocusObject())
		):
			log.info("ChatGPT Desktop Access stopped choosing an option: focus left the prompt")
			ui.message(_("{option} could not be chosen. Open Add files and more again").format(option=option["title"]))
			return
		current = self._readAttachmentPopupOptions(self._buffer) if self._buffer is not None else ()
		highlighted = next((index for index, candidate in enumerate(current) if candidate.get("highlighted")), None)
		if awaitingFrom is not None and highlighted == awaitingFrom:
			if waits < ATTACHMENT_OPTION_HIGHLIGHT_WAITS:
				wx.CallLater(
					ATTACHMENT_OPTION_HIGHLIGHT_MILLISECONDS, self._stepToAttachmentOption,
					option, step, awaitingFrom, waits + 1,
				)
				return
			log.info("ChatGPT Desktop Access could not reach an Add files and more option: the highlight did not move")
			ui.message(_("{option} could not be chosen. Open Add files and more again").format(option=option["title"]))
			return
		key = attachmentOptionKeyStep(current, option)
		if not key or step > len(current) + ATTACHMENT_OPTION_EXTRA_STEPS:
			log.info(
				"ChatGPT Desktop Access could not reach an Add files and more option: "
				"%d options, step %d, highlight readable %s",
				len(current), step, any(candidate.get("highlighted") for candidate in current),
			)
			ui.message(_("{option} could not be chosen. Open Add files and more again").format(option=option["title"]))
			return
		if key == "tab":
			self._attachmentPromptTextBefore = self._promptTextForAnnouncement()
		# Tab chooses the highlighted row; Enter is never used because it could send the prompt.
		keyboardHandler.KeyboardInputGesture.fromName(key).send()
		if key == "tab":
			log.info("ChatGPT Desktop Access chose an Add files and more option after %d highlight steps", step)
			wx.CallLater(ATTACHMENT_OPTION_CONFIRM_MILLISECONDS, self._confirmAttachmentChoice, option)
			return
		wx.CallLater(
			ATTACHMENT_OPTION_HIGHLIGHT_MILLISECONDS, self._stepToAttachmentOption,
			option, step + 1, highlighted, 0,
		)

	def _confirmAttachmentChoice(self, option):
		"""A chosen option closes ChatGPT's popup; report if it stayed open."""
		button = self._currentAddFilesButton(self._attachmentMenuButton)
		if not self._addFilesPopupIsOpen(button):
			log.info("ChatGPT Desktop Access confirmed the Add files and more choice")
			# Plugins and modes change the prompt silently. A dialog such as Select
			# files takes focus and is announced by NVDA, so stay quiet then.
			if _isCodexPromptObject(api.getFocusObject()):
				# The tag ChatGPT adds is the option's exact short name, such as
				# "Code Review", even when the list title includes its description.
				added = promptTextAddition(
					getattr(self, "_attachmentPromptTextBefore", ""), self._promptTextForAnnouncement(),
				)
				if added:
					ui.message(_("{option} added").format(option=added))
				else:
					ui.message(_("{option} chosen").format(option=option["title"]))
			return
		log.info("ChatGPT Desktop Access could not choose an Add files and more option: popup stayed open")
		ui.message(_("{option} could not be chosen. Open Add files and more again").format(option=option["title"]))

	def _promptTextForAnnouncement(self):
		"""Return the prompt's text, treating its placeholder as empty."""
		try:
			prompt = self._findChatGPTPromptObject()
			if prompt is None:
				return ""
			text = " ".join(prompt.makeTextInfo(textInfos.POSITION_ALL).text.replace("￼", " ").split())
			return "" if text == " ".join(str(prompt.name or "").split()) else text
		except Exception:
			return ""

	def _currentAddFilesButton(self, savedButton=None):
		"""Return a fresh Add files and more button from the page, or a still-valid saved one."""
		try:
			button = self._exactNamedButtonObject(ADD_FILES_BUTTON_NAME)
			if button is not None:
				return button
		except Exception:
			log.debug("ChatGPT Desktop Access could not find the current Add files and more button", exc_info=True)
		if savedButton is not None and not _isDefunctObject(savedButton):
			return savedButton
		return None

	def _attachmentMenuFlowActive(self):
		"""True from Enter on Add files and more until its dialog closes."""
		return bool(
			self._attachmentActivationAt or self._attachmentSourceFocusTimer
			or self._attachmentSourcePendingButton or self._attachmentMenuDialog
		)

	def _namedButtonFromUIA(self, name, ordinal=1):
		"""Find a named button through UI Automation, without searching NVDA's document.

		Searching NVDA's UI Automation document is slow and does not find every
		button, so the page is queried directly. ``ordinal`` counts matches in page
		order, as in the document search.
		"""
		import UIAHandler
		from NVDAObjects.UIA import UIA
		client = UIAHandler.handler.clientObject
		root = getattr(getattr(self._buffer, "rootNVDAObject", None), "UIAElement", None)
		if root is None:
			return None
		condition = client.createAndConditionFromArray([
			client.createPropertyCondition(UIAHandler.UIA_ControlTypePropertyId, UIAHandler.UIA_ButtonControlTypeId),
			client.createPropertyConditionEx(UIAHandler.UIA_NamePropertyId, name, getattr(UIAHandler, "PropertyConditionFlags_IgnoreCase", 1)),
		])
		found = root.FindAllBuildCache(UIAHandler.TreeScope_Descendants, condition, UIAHandler.handler.baseCacheRequest)
		if not found or found.Length < ordinal:
			return None
		return UIA(UIAElement=found.GetElement(ordinal - 1))

	def _addFilesPopupIsOpen(self, button):
		try:
			return button is not None and State.EXPANDED in (getattr(button, "states", ()) or ())
		except Exception:
			return False

	def _reopenAttachmentPopup(self, button):
		"""Press Add files and more to reopen ChatGPT's popup."""
		if button is None:
			return False
		try:
			_pressControl(button)
			log.info("ChatGPT Desktop Access reopened Add files and more to choose an option")
			return True
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not reopen Add files and more", exc_info=True)
			return False

	def _closeAttachmentPopup(self):
		"""After Cancel, close ChatGPT's popup so focus mode in the prompt behaves normally."""
		button = self._attachmentMenuButton
		windowHandle = self._attachmentMenuWindowHandle
		try:
			if (
				windowHandle == self._conversationWindowHandle
				and self._conversationWindowOwnsForeground(windowHandle)
				and State.EXPANDED in (getattr(button, "states", ()) or ())
			):
				_pressControl(button)
		except Exception:
			log.debug("ChatGPT Desktop Access could not close the Add files and more popup", exc_info=True)

	def _moveBrowseCaretToAttachmentPopup(self, buffer, anchor):
		"""Return to browse mode at the popup so arrows read options and Enter chooses one."""
		if getattr(buffer, "passThrough", False):
			buffer.passThrough = False
			try:
				import browseMode
				browseMode.reportPassThrough(buffer)
			except Exception:
				log.debug("ChatGPT Desktop Access could not report browse mode", exc_info=True)
		anchor.updateCaret()
		line = anchor.copy()
		line.expand(textInfos.UNIT_LINE)
		try:
			speech.speakTextInfo(line, unit=textInfos.UNIT_LINE, reason=OutputReason.CARET)
		except Exception:
			log.debug("ChatGPT Desktop Access could not speak the attachment popup line", exc_info=True)
		try:
			braille.handler.handleCaretMove(buffer)
		except Exception:
			log.debug("ChatGPT Desktop Access could not update Braille at the attachment popup", exc_info=True)
		log.info("ChatGPT Desktop Access moved the browse cursor to the Add files and more popup")

	def _focusAttachmentSourceMenu(self, button, buffer, windowHandle, attempt=0):
		self._attachmentSourceFocusTimer = None
		try:
			if (
				buffer is None or buffer is not self._buffer
				or windowHandle != self._conversationWindowHandle
				or not self._conversationWindowIsAvailable(windowHandle)
				or not self._conversationWindowOwnsForeground(windowHandle)
				or State.COLLAPSED in (getattr(button, "states", ()) or ())
			):
				log.info(
					"ChatGPT Desktop Access stopped opening Add files and more: conversation changed %s, "
					"window changed %s, ChatGPT in foreground %s, menu collapsed %s",
					buffer is None or buffer is not self._buffer, windowHandle != self._conversationWindowHandle,
					self._conversationWindowOwnsForeground(windowHandle),
					State.COLLAPSED in (getattr(button, "states", ()) or ()),
				)
				return
			focus = api.getFocusObject()
			if not _isChatGPTObject(focus):
				log.info("ChatGPT Desktop Access stopped opening Add files and more: focus is outside ChatGPT")
				return
			if not (self._isAddFilesButton(focus) or _isCodexPromptObject(focus)):
				# A real popup item or another user-selected control already has focus.
				log.info(
					"ChatGPT Desktop Access stopped opening Add files and more: focus moved to %s %r, "
					"which is not the button or a recognized prompt",
					_roleName(focus), getattr(focus, "name", "") if _roleName(focus) != "editabletext" else "",
				)
				return
			if not _isVirtualBufferDocument(buffer):
				self._showAttachmentMenuFromUIA(button, buffer, windowHandle, focus, attempt)
				return
			anchor = self._attachmentPopupAnchor(buffer)
			rowOptions = ()
			if anchor is None:
				# Some ChatGPT versions have no "Type to search" text; their popup is
				# still recognizable by its row classes.
				rowOptions = tuple(
					option for option in self._readAttachmentPopupOptions(buffer) if option.get("classBased")
				)
			if anchor is not None or rowOptions:
				# ChatGPT returns focus to the prompt about 300 ms after opening the
				# popup, which puts NVDA in focus mode. Act only after that, or the
				# focus change would undo the move.
				if _isCodexPromptObject(focus) or attempt >= ATTACHMENT_POPUP_SETTLE_ATTEMPTS:
					options = rowOptions or self._readAttachmentPopupOptions(buffer)
					if options:
						# The document joins some titles to their descriptions; list
						# the exact ones from UI Automation when they agree.
						options = withAttachmentOptionTitles(options, self._readAttachmentPopupOptionsWithUIA(buffer))
					if options:
						self._showAttachmentMenuDialog(options, button, windowHandle)
					elif anchor is not None:
						self._moveBrowseCaretToAttachmentPopup(buffer, anchor)
					return
				target = None
			else:
				target = self._attachmentSourceMenuObject(buffer)
			if target is None:
				if attempt < ATTACHMENT_POPUP_RETRIES:
					# Chromium can add the popup to the virtual buffer a few hundred
					# milliseconds after reporting the button as expanded.
					self._attachmentSourceFocusTimer = wx.CallLater(
						ATTACHMENT_POPUP_RETRY_MILLISECONDS,
						self._focusAttachmentSourceMenu, button, buffer, windowHandle, attempt + 1,
					)
					return
				log.info(
					"ChatGPT Desktop Access found no Add files and more popup after %d tries; page after the prompt: %s",
					attempt + 1, self._attachmentPopupStructure(buffer),
				)
				return
			target.setFocus()
			# Keyboard focus alone does not reliably move Chromium's browse cursor.
			# Align it with the same exact menu control so speech, Braille, and the
			# next arrow key all begin at the native attachment options.
			try:
				position = buffer.makeTextInfo(target)
				position.collapse()
				position.updateCaret()
			except Exception:
				log.debug("ChatGPT Desktop Access could not align the attachment browse caret")
			api.setNavigatorObject(target)
			log.info("ChatGPT Desktop Access focused the native Sources attachment menu")
		except Exception:
			log.debugWarning(
				"ChatGPT Desktop Access could not focus the native Sources attachment menu",
				exc_info=True,
			)

	def _showAttachmentMenuFromUIA(self, button, buffer, windowHandle, focus, attempt):
		"""List the popup's options when NVDA reads ChatGPT through UI Automation."""
		options = self._readAttachmentPopupOptionsWithUIA(buffer)
		# As in the usual document, wait for ChatGPT to return focus to the prompt.
		if options and (_isCodexPromptObject(focus) or attempt >= ATTACHMENT_POPUP_SETTLE_ATTEMPTS):
			self._showAttachmentMenuDialog(options, button, windowHandle)
			return
		if attempt < ATTACHMENT_POPUP_RETRIES:
			self._attachmentSourceFocusTimer = wx.CallLater(
				ATTACHMENT_POPUP_RETRY_MILLISECONDS,
				self._focusAttachmentSourceMenu, button, buffer, windowHandle, attempt + 1,
			)
			return
		log.info("ChatGPT Desktop Access found no Add files and more options through UI Automation")

	def _scheduleAttachmentSourceFocus(self, button, now):
		if not (
			self._attachmentActivationAt
			and now - self._attachmentActivationAt <= ATTACHMENT_ACTIVATION_WINDOW_SECONDS
			and self._buffer is not None
			and self._conversationWindowIsAvailable(self._conversationWindowHandle)
		):
			return False
		self._attachmentSourceFocusTimer = wx.CallLater(
			ATTACHMENT_SOURCE_FOCUS_DELAY_MILLISECONDS,
			self._focusAttachmentSourceMenu,
			button, self._buffer, self._conversationWindowHandle,
		)
		log.debug("ChatGPT Desktop Access scheduled focus on the native Sources attachment menu")
		return True

	def _resumeAttachmentSourceFocus(self):
		"""Finish an explicit menu activation after its buffer becomes available."""
		button = self._attachmentSourcePendingButton
		if button is None:
			return
		if self._scheduleAttachmentSourceFocus(button, time.monotonic()):
			self._attachmentSourcePendingButton = None
			self._attachmentActivationAt = 0.0

	def _noteAttachmentMenuControl(self, obj, focused=False):
		"""Track only ChatGPT's native Add files and more control."""
		if not _isChatGPTObject(obj) or _roleName(obj) != "button":
			return False
		states = getattr(obj, "states", ()) or ()
		if not ({State.EXPANDED, State.COLLAPSED} & set(states)):
			return False
		if promptControlKind(getattr(obj, "name", "")) != "files":
			return False
		now = time.monotonic()
		if focused:
			self._attachmentMenuButtonFocusedAt = now
			self._attachmentDiagnostics.noteButtonFocused(obj)
		if State.EXPANDED in states:
			candidateAt = self._attachmentInputCandidateAt
			if (
				candidateAt
				and 0 <= now - candidateAt <= ATTACHMENT_ACTIVATION_WINDOW_SECONDS
				and self._attachmentInputCandidateWindowHandle == self._conversationWindowHandle
				and self._appFocusState
			):
				# Hardware keyboard gestures can arrive on winInputHook rather than
				# NVDA's main thread. Only the exact expanded Add files control may
				# turn that timestamp into a focus move; never inspect IA2 here from
				# the input thread or redirect after an unrelated key.
				self._attachmentActivationAt = candidateAt
				self._attachmentInputCandidateAt = 0.0
				self._attachmentInputCandidateWindowHandle = 0
				log.debug("ChatGPT Desktop Access confirmed keyboard attachment activation")
			if (
				self._attachmentMenuLastClosedAt
				and now - self._attachmentMenuLastClosedAt < ATTACHMENT_MENU_STALE_EXPANSION_SECONDS
				and not focused
				and not (
					self._attachmentActivationAt
					and now - self._attachmentActivationAt <= ATTACHMENT_ACTIVATION_WINDOW_SECONDS
				)
			):
				# Chromium may deliver a stale expanded event after the menu has
				# collapsed and focus has returned to the prompt.
				return True
			firstExpansion = not self._attachmentMenuActiveAt
			self._attachmentMenuActiveAt = now
			if firstExpansion:
				self._attachmentDiagnostics.noteButtonActivated(obj, "expanded event")
				if self._scheduleAttachmentSourceFocus(obj, now):
					self._attachmentActivationAt = 0.0
					self._attachmentSourcePendingButton = None
				else:
					log.debug(
						"ChatGPT Desktop Access saw Add files and more open before its activation: "
						"keyboard activation %s, conversation attached %s",
						bool(self._attachmentActivationAt), getattr(self, "_buffer", None) is not None,
					)
					self._attachmentSourcePendingButton = obj if (
						self._attachmentActivationAt
						and now - self._attachmentActivationAt <= ATTACHMENT_ACTIVATION_WINDOW_SECONDS
					) else None
		elif State.COLLAPSED in states:
			if self._attachmentMenuActiveAt:
				self._cancelAttachmentSourceFocus()
				self._attachmentMenuLastClosedAt = now
				self._attachmentMenuButtonFocusedAt = 0.0
			self._attachmentMenuActiveAt = 0.0
			self._lastAttachmentMenuItem = ""
			self._lastAttachmentMenuItemAt = 0.0
		return True

	def _attachmentMenuSelectionState(self, obj):
		if not _isChatGPTObject(obj):
			return False
		states = getattr(obj, "states", ()) or ()
		return State.SELECTED in states or State.FOCUSED in states

	def _attachmentMenuLabel(self, obj):
		values = {}
		for attribute in ("name", "value", "description"):
			try:
				values[attribute] = getattr(obj, attribute, "")
			except Exception:
				values[attribute] = ""
		return attachmentMenuItemLabel(
			True, _roleName(obj), values["name"], values["value"], values["description"],
		)

	def _attachmentMenuContextActive(self, obj):
		if not _isChatGPTObject(obj):
			return False
		now = time.monotonic()
		if self._attachmentMenuActiveAt:
			if now - self._attachmentMenuActiveAt <= ATTACHMENT_MENU_TIMEOUT_SECONDS:
				return True
			self._resetAttachmentMenuTracking()
			return False
		if (
			self._attachmentMenuButtonFocusedAt
			and now - self._attachmentMenuButtonFocusedAt <= ATTACHMENT_MENU_ARM_SECONDS
			and self._attachmentMenuLabel(obj)
		):
			# Some Chromium builds omit the expanded-state event. A genuine popup item
			# immediately following focus on Add files is sufficient, bounded evidence.
			self._attachmentMenuActiveAt = now
			return True
		return False

	def _announceAttachmentMenuSelection(self, obj, speak=True):
		"""Provide speech and Braille for the attachment popup's selected item.

		When an option receives real focus, NVDA already reports it, so the focus
		handler passes speak=False and only the duplicate tracking is updated.
		"""
		if not self._attachmentMenuContextActive(obj):
			return False
		label = self._attachmentMenuLabel(obj)
		if not label:
			return False
		now = time.monotonic()
		if (
			label == self._lastAttachmentMenuItem
			and now - self._lastAttachmentMenuItemAt < ATTACHMENT_MENU_DUPLICATE_SECONDS
		):
			return True
		self._attachmentMenuActiveAt = now
		self._lastAttachmentMenuItem = label
		self._lastAttachmentMenuItemAt = now
		if not speak:
			return True
		message = _("{item}, menu item").format(item=label)
		conf = _settings()
		_send(message, conf["speech"], conf["braille"], None, False, brailleMessage=message)
		log.debug("ChatGPT Desktop Access announced attachment menu selection")
		return True

	def _observeInputGesture(self, gesture):
		"""Observe prompt input and defer large scans during conversation navigation."""
		try:
			identifiers = getattr(gesture, "identifiers", ()) or ()
			if isinstance(identifiers, str):
				identifiers = (identifiers,)
			if not identifiers:
				identifier = getattr(gesture, "identifier", "")
				identifiers = (identifier,) if identifier else ()
			if identifiers and getattr(self, "_suggestionMenuOpen", False):
				keys = {gestureKeyName(identifier) for identifier in identifiers} - {""}
				if keys:
					queueHandler.queueFunction(queueHandler.eventQueue, self._noteSuggestionMenuKeys, tuple(keys))
			if identifiers:
				if threading.current_thread() is threading.main_thread():
					self._noteAttachmentActivationGesture(identifiers)
				else:
					activation = any(
						isPromptSubmissionGestureIdentifier(identifier)
						or str(identifier or "").casefold().endswith(":space")
						for identifier in identifiers
					)
					if activation and self._appFocusState:
						candidateAt = time.monotonic()
						windowHandle = self._conversationWindowHandle
						self._attachmentInputCandidateAt = candidateAt
						self._attachmentInputCandidateWindowHandle = windowHandle
						queueHandler.queueFunction(
							queueHandler.eventQueue, self._captureAttachmentActivationFromQueuedGesture,
							tuple(identifiers), candidateAt, windowHandle,
						)
					elif (
						self._attachmentInputCandidateAt or self._attachmentActivationAt
						or self._attachmentSourceFocusTimer
					):
						self._attachmentInputCandidateAt = 0.0
						self._attachmentInputCandidateWindowHandle = 0
						queueHandler.queueFunction(
							queueHandler.eventQueue, self._noteAttachmentActivationGesture,
							tuple(identifiers),
						)
			if not self._appFocusState:
				return True
			identifiers = tuple(identifiers)
			if threading.current_thread() is threading.main_thread():
				return self._observePromptGestureIdentifiers(identifiers)
			queueHandler.queueFunction(queueHandler.eventQueue, self._observePromptGestureIdentifiers, identifiers)
		except Exception:
			pass
		return True

	def _observePromptGestureIdentifiers(self, identifiers):
		"""Process immutable gesture identifiers only on NVDA's main queue."""
		try:
			if not self._appFocusState or getattr(self, "_timer", True) is None:
				return True
			# Conversation state is owned by NVDA's main thread.
			self._conversationActivatedAt = 0.0
			self._conversationEntryCorrectionGeneration += 1
			if (
				self._conversationBrowseModeActive()
				and any(isConversationNavigationGestureIdentifier(identifier) for identifier in identifiers)
			):
				# Focus can still be reported on the prompt for the first arrow after the
				# user enters browse mode. Protect that transition as well as subsequent
				# reading, otherwise an event-driven scan can rebuild Chromium's buffer and
				# return the browse cursor to the prompt in a large conversation.
				self._conversationNavigationUntil = max(
					self._conversationNavigationUntil,
					time.monotonic() + CONVERSATION_NAVIGATION_QUIET_SECONDS,
				)
				return True
			if not self._promptFocused:
				# Whole-buffer reads are the most expensive operation in a large
				# conversation. Any user gesture outside the prompt means navigation is
				# active, so leave the browse cursor and Braille viewport undisturbed until
				# the user pauses. The gesture always continues through NVDA unchanged.
				if identifiers:
					self._conversationNavigationUntil = max(
						self._conversationNavigationUntil,
						time.monotonic() + CONVERSATION_NAVIGATION_QUIET_SECONDS,
					)
				return True
			promptInFocusMode = bool(getattr(self._buffer, "passThrough", True))
			if any(isPromptSubmissionGestureIdentifier(identifier) for identifier in identifiers):
				promptTypingActive = time.monotonic() < self._promptTypingUntil
				if not promptSubmissionGestureShouldStart(
					promptInFocusMode, self._promptHadText, promptTypingActive,
				):
					# In browse mode, dot-8 activates the empty editor. It does not
					# submit anything and must not start clicks or elapsed messages.
					self._brailleCompositionActive = False
					self._promptTypingUntil = 0.0
					return True
				# ChatGPT replaces its content-editable prompt as Enter is processed.
				# That can leave NVDA's normal text/caret script holding a stale IA2
				# object, so observe Enter before the replacement and queue only our
				# state transition. The gesture itself continues through NVDA unchanged.
				self._brailleCompositionActive = False
				self._promptTypingUntil = 0.0
				if not self._promptSubmissionGestureQueued:
					self._promptSubmissionGestureQueued = True
					self._promptSubmissionDraftQueued = self._promptDraftText
					try:
						queueHandler.queueFunction(
							queueHandler.eventQueue, self._beginPromptSubmissionFromGesture,
						)
					except Exception:
						# A transient queue failure must not disable all later Enter
						# observations for the lifetime of this NVDA session.
						self._promptSubmissionGestureQueued = False
						self._promptSubmissionDraftQueued = ""
						raise
				return True
			brailleIdentifiers = tuple(
				identifier for identifier in identifiers
				if isBrailleTypingGestureIdentifier(identifier)
			)
			if brailleIdentifiers:
				if not promptInFocusMode:
					# Braille dot chords are browse-mode navigation until the prompt
					# has actually entered focus mode; do not treat them as draft text.
					self._brailleCompositionActive = False
					self._promptTypingUntil = 0.0
					return True
				commitsText = any(
					brailleTypingGestureCommitsText(identifier) for identifier in brailleIdentifiers
				)
				self._brailleCompositionActive = not commitsText
				if commitsText:
					# Contracted Braille sends the completed word just after this
					# observer runs. ChatGPT can report its resulting caret move only
					# after the first cell of the next word has already been entered.
					self._lastBrailleTextInjectionAt = time.monotonic()
				self._promptTypingUntil = max(
					self._promptTypingUntil,
					time.monotonic() + PROMPT_TYPING_QUIET_SECONDS,
				)
		except Exception:
			# This observer must never interfere with another add-on or NVDA gesture.
			pass
		return True

	def _beginPromptSubmissionFromGesture(self):
		"""Start feedback for an observed Enter after returning to NVDA's main queue."""
		global _activePluginInstance
		self._promptSubmissionGestureQueued = False
		queuedDraft, self._promptSubmissionDraftQueued = self._promptSubmissionDraftQueued, ""
		if _activePluginInstance is not self or self._busy:
			return
		if queuedDraft:
			self._promptDraftText = queuedDraft
		self._promptHadText = False
		self._beginPromptSubmission("unmodified Enter gesture")
		self._schedulePoll(50, requestInspection=True)

	def event_caret(self, obj, nextHandler):
		"""Preserve a new contracted word across ChatGPT's delayed prior-word caret event."""
		try:
			if self._appFocusState and _isCodexPromptObject(obj):
				try:
					from braille import input as brailleInputModule
				except ImportError:
					# Compatibility fallback for NVDA versions predating braille.input.
					import brailleInput as brailleInputModule
				handler = getattr(brailleInputModule, "handler", None)
				elapsed = (
					time.monotonic() - self._lastBrailleTextInjectionAt
					if self._lastBrailleTextInjectionAt else float("inf")
				)
				if handler is not None and shouldPreserveBrailleComposition(
					self._promptFocused,
					self._brailleCompositionActive,
					bool(getattr(handler, "bufferBraille", ())),
					elapsed,
					BRAILLE_CARET_GRACE_SECONDS,
				):
					# NVDA already ignores caret events generated by uncontracted
					# Braille for 0.3 seconds. Mark this one the same way instead of
					# replacing or bypassing the Braille input handler.
					handler._uncontSentTime = time.time()
					self._brailleCaretMoveSuppressions += 1
		except Exception:
			# Caret handling must always continue even if NVDA changes its
			# internal Braille input implementation in a future release.
			log.debugWarning("ChatGPT Desktop Access Braille caret protection failed", exc_info=True)
		finally:
			nextHandler()

	def _trackPromptDraftState(self, obj, allowTextInfo=True):
		"""Track whether the draft has text; never infer submission from deletion."""
		try:
			isEditable = obj.role == Role.EDITABLETEXT
		except Exception:
			return False
		if not isEditable or not _isCodexPromptObject(obj):
			return False
		valueRead = False
		text = ""
		try:
			value = obj.value
			if value is not None:
				valueRead = True
				text = str(value)
		except Exception:
			pass
		# Chromium content-editable controls do not always expose a useful value.
		# Trust a non-empty value, and trust an empty value only after this prompt
		# was known to contain text. This avoids a redundant IA2 TextInfo read at
		# the exact moment Enter replaces the editor object.
		if not (valueRead and (text.strip() or self._promptHadText is True)):
			if not allowTextInfo:
				return False
			try:
				text = str(obj.makeTextInfo(textInfos.POSITION_ALL).text or "")
				valueRead = True
			except Exception:
				pass
		if not valueRead:
			return False
		self._promptDraftText = " ".join(text.split())
		self._promptHadText = bool(self._promptDraftText)
		return False

	def _schedulePromptInspection(self, obj):
		"""Debounce prompt-local TextInfo reads until Braille or keyboard typing pauses."""
		self._pendingPromptObject = obj
		if self._promptInspectionTimer:
			self._promptInspectionTimer.Stop()
		self._promptInspectionTimer = wx.CallLater(
			PROMPT_INSPECTION_DELAY_MS, self._inspectPendingPrompt,
		)

	def _inspectPendingPrompt(self):
		self._promptInspectionTimer = None
		obj = self._pendingPromptObject
		self._pendingPromptObject = None
		try:
			if obj is None or not _isCodexPromptObject(obj):
				return
			self._trackPromptDraftState(obj, allowTextInfo=True)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access deferred prompt inspection failed", exc_info=True)

	def _notePromptTyping(self, obj):
		if not _isCodexPromptObject(obj):
			return False
		self._lastPromptObject = obj
		self._promptTypingUntil = time.monotonic() + PROMPT_TYPING_QUIET_SECONDS
		return True

	def _beginPromptSubmission(self, reason):
		draftText = self._promptDraftText
		self._promptDraftText = ""
		self._submittedTurnUnconfirmedAt = time.monotonic()
		if draftText:
			# Chromium can take several seconds to expose a newly posted message to
			# its virtual buffer. Make the user's submitted turn reviewable immediately.
			self._appendRecentChatMessage("user", draftText)
		self._promptTypingUntil = 0.0
		self._brailleCompositionActive = False
		self._lastBrailleTextInjectionAt = 0.0
		if self._usageLimitActive:
			# A new explicit submission is a new attempt. It may succeed after the
			# reset time or expose a fresh limit notice that should be announced.
			self._usageLimitActive = False
			self._lastUsageLimitNotice = ""
			self._lastLabel = ""
			self._lastScannedLabel = ""
		if self._promptInspectionTimer:
			self._promptInspectionTimer.Stop()
			self._promptInspectionTimer = None
		self._pendingPromptObject = None
		if self._pluginProgressOwnedBusy:
			# A real task supersedes installation-owned background state. Otherwise a
			# later installation completion could incorrectly end the new task.
			self._pluginProgressOwnedBusy.clear()
			self._setBusy(False, "prompt superseded plugin installation")
		if self._busy:
			return
		self._latestMessage = ""
		self._latestFullMessage = ""
		self._lastMessage = ""
		self._lastMessageAt = 0.0
		self._pendingResponseCompletionAt = 0.0
		self._lastSubmissionSignal = reason
		self._active = True
		self._activeCategory = "working"
		self._setBusy(True, reason)
		conf = _settings()
		if conf["promptSubmissionClick"] and not self._paused:
			mode = conf[CATEGORY_OUTPUT_CONFIG["working"]]
			actions = categoryOutputActions(mode, conf["speech"], conf["braille"], conf["soundWhenSpeechUnavailable"])
			if actions["sound"]:
				_playProgressSound(
					"submission", _("Prompt submitted"), conf["progressSoundStyle"], conf["clickVolume"],
				)
		log.info("ChatGPT Desktop Access submission detected: %s", reason)

	def _queueResponseCompletion(self):
		if self._busy and not self._pendingResponseCompletionAt:
			self._pendingResponseCompletionAt = time.monotonic()
			log.debug("ChatGPT Desktop Access queued response completion candidate")

	def _latestButtonStatus(self, info):
		latest = ""
		latestUserMessageNumber = None
		stopControlVisible = False
		responseCompleteMarkerCount = 0
		latestDetailedResponseMarker = None
		buttonDepth = 0
		buttonText = []
		buttonName = ""
		unknown = []
		usageEvidence = []
		usageActionControls = set()
		usageBannerSeen = False
		inRecents = False
		recentsSeen = False
		recentTitles = []
		recentTitleKeys = set()
		ambiguousRecentTitles = set()
		recentItemCount = 0
		inArchived = False
		archivedSeen = False
		archivedTitles = []
		showMoreButtonOrdinal = 0
		recentShowMoreButtonOrdinal = 0
		observedMode = ""
		messageCollector = self._newChatMessageFieldCollector(stopAtPrompt=True)
		messageAccumulator = ChatMessageAccumulator(MESSAGE_LIST_LIMIT)
		sidebarTitleKeys = set()
		buttonIsMenuRow = False
		for item in info.getTextWithFields():
			if item is None:
				# The sidebar and newest transcript are separate bounded ranges.
				# Do not let a truncated sidebar button or Recents region consume
				# conversation controls as chat-history entries.
				inRecents = inArchived = False
				buttonDepth, buttonText, buttonName = 0, [], ""
				latest = ""
				latestUserMessageNumber = None
				stopControlVisible = False
				responseCompleteMarkerCount = 0
				latestDetailedResponseMarker = None
				messageCollector = self._newChatMessageFieldCollector(stopAtPrompt=True)
				messageAccumulator = ChatMessageAccumulator(MESSAGE_LIST_LIMIT)
				continue
			for token in messageCollector.feed(item):
				messageAccumulator.feed(token)
			if isinstance(item, str):
				plainText = " ".join(item.split())
				usagePlainText = re.sub(r"(?<=[a-z0-9%])(?=[A-Z])", " ", plainText)
				if inRecents and re.search(
					r"\b(?:\d{1,3}(?:\.\d+)?\s*%\s*usage\s+(?:remaining|consumed)|no usage remaining)\b",
					usagePlainText,
					flags=re.IGNORECASE,
				):
					usageEvidence.append(usagePlainText[:256])
					usageBannerSeen = True
				elif usageBannerSeen and any(marker in usagePlainText.casefold() for marker in (
					"next reset", "resets every", "add credits", "buy credits", "purchase credits", "upgrade",
				)):
					usageEvidence.append(usagePlainText[:256])
				if not recentsSeen and plainText.casefold() == "recents":
					inRecents = recentsSeen = True
				if not archivedSeen and plainText.casefold() == "archived chats":
					inArchived = archivedSeen = True
				if not buttonDepth and inRecents and plainText.casefold() in ("pinned", "projects", "agents"):
					inRecents = False
				if isChatHistoryConversationBoundary(plainText):
					inRecents = inArchived = False
				if isResponseCompletionMarkerText(plainText):
					responseCompleteMarkerCount += 1
					if plainText.casefold().startswith("response complete:"):
						# Python's per-process hash avoids retaining or logging response text.
						latestDetailedResponseMarker = hash(plainText)
				if buttonDepth:
					buttonText.append(item)
				continue
			command = getattr(item, "command", "")
			field = getattr(item, "field", {}) or {}
			if command == "controlStart":
				role = field.get("role")
				fieldName = " ".join(str(field.get("name", "") or "").split())
				fieldMode = ""
				fieldNameKey = fieldName.casefold()
				if role == Role.BUTTON and (
					fieldNameKey in ("", "chatgpt", "codex", "mode selector")
					or fieldNameKey.startswith(("switch mode", "current mode:"))
				):
					fieldStates = field.get("states", ()) or ()
					fieldMode = conversationModeFromSwitchControl(
						fieldName, field.get("description", ""), "button",
						bool({State.EXPANDED, State.COLLAPSED} & set(fieldStates)),
						field.get("automationID", "") or field.get("automationId", ""),
					)
				if fieldMode:
					observedMode = fieldMode
				landmarkName = " ".join(str(field.get("landmark", "") or "").casefold().split())
				isMainLandmark = role == Role.LANDMARK and (
					fieldName.casefold() in ("main", "main content") or landmarkName == "main"
				)
				isFollowingSectionHeading = inRecents and role == getattr(Role, "HEADING", None) and (
					fieldName.casefold() not in ("", "recents")
				)
				if inRecents and isMainLandmark:
					inRecents = False
				if isFollowingSectionHeading:
					inRecents = False
				if inArchived and isMainLandmark:
					inArchived = False
				if buttonDepth:
					buttonDepth += 1
				elif role == Role.BUTTON:
					buttonDepth, buttonText, buttonName = 1, [], field.get("name", "")
					# Rows of the "@", "/", and Add files and more menus list chat titles
					# and stay on the page after the menu closes; they are never activity.
					buttonIsMenuRow = ATTACHMENT_POPUP_ROW_CLASS in str(field.get(ATTACHMENT_POPUP_CLASS_KEY, "") or "")
			elif command == "controlEnd" and buttonDepth:
				buttonDepth -= 1
				if buttonDepth == 0:
					textLabel = " ".join("".join(buttonText).split())
					historyLabel = textLabel or " ".join(str(buttonName or "").split())
					accountLabel = historyLabel.casefold()
					if usageBannerSeen and (
						accountLabel in ("upgrade", "upgrade plan", "upgrade to pro")
						or re.fullmatch(
							r"(?:add|buy|purchase)(?:\s+some)?(?:\s+more)?\s+credits?", accountLabel,
						)
					):
						usageEvidence.append(historyLabel[:256])
						usageActionControls.add(accountLabel)
					if historyLabel.casefold() == "show more":
						showMoreButtonOrdinal += 1
						if inRecents and not recentShowMoreButtonOrdinal:
							recentShowMoreButtonOrdinal = showMoreButtonOrdinal
					if any(isChatHistoryConversationBoundary(candidate) for candidate in (textLabel, buttonName)):
						inRecents = inArchived = False
					isRecentTitle = inRecents and historyLabel and historyLabel.casefold() not in (
						"recents", "open profile menu", "new chat", "view activity",
					) and not isChatHistoryInterfaceText(historyLabel)
					if isRecentTitle:
						recentItemCount += 1
						titleKey = " ".join(historyLabel.casefold().split())
						if titleKey in recentTitleKeys:
							ambiguousRecentTitles.add(titleKey)
						else:
							recentTitleKeys.add(titleKey)
						if historyLabel not in recentTitles:
							recentTitles.append(historyLabel)
					archivedKey = historyLabel.casefold()
					if inArchived and historyLabel and archivedKey not in (
						"archived chats", "close", "cancel", "done", "delete", "unarchive",
					) and not archivedKey.startswith(("delete ", "unarchive ")) and not isChatHistoryInterfaceText(
						historyLabel
					) and historyLabel not in archivedTitles:
						archivedTitles.append(historyLabel)
					for candidate in (textLabel, buttonName):
						if isStopControlLabel(candidate):
							stopControlVisible = True
						number = userMessageNumber(candidate)
						if number is not None:
							latestUserMessageNumber = max(latestUserMessageNumber or number, number)
					# A chat title in the sidebar, such as "Using VoiceOver Rotor", is not
					# progress even when it reads like a Codex status.
					isHistoryTitle = isRecentTitle or (inArchived and bool(historyLabel))
					if isHistoryTitle:
						sidebarTitleKeys.add(" ".join(historyLabel.casefold().split()))
					isNotActivity = isHistoryTitle or buttonIsMenuRow
					label = "" if isNotActivity else firstStatusLabel(textLabel, buttonName)
					if label:
						latest = label
					elif textLabel or buttonName:
						candidate = textLabel or buttonName
						if not isNotActivity and not isKnownNonStatusButton(candidate) and not isStopControlLabel(candidate):
							unknown.append(candidate)
		if sidebarTitleKeys:
			known = getattr(self, "_sidebarChatTitleKeys", set())
			self._sidebarChatTitleKeys = (known | sidebarTitleKeys) if len(known) < 500 else sidebarTitleKeys
		if messageCollector.promptReached:
			# Reuse the existing compatibility scan. Shortcut presses can now read a
			# ten-turn snapshot without synchronously traversing Chromium on NVDA's
			# main thread, and content after the active prompt cannot replace it.
			messages = messageAccumulator.messages()
			if isinstance(info, _SplitConversationScanInfo):
				messages = self._splitScanConversationMessages(messages)
			self._cacheRecentChatMessages(messages)
		if observedMode:
			self._setConversationMode(observedMode, "mode switch control scan", authoritative=True)
		scanMode = observedMode or self._conversationMode
		recentSnapshot = tuple(recentTitles) if recentsSeen else None
		archivedSnapshot = tuple(archivedTitles) if archivedSeen else None
		if scanMode in ("chatgpt", "codex") and recentSnapshot is not None:
			self._chatHistoryMoreAvailable[scanMode] = bool(recentShowMoreButtonOrdinal)
			self._recentHistoryShowMoreOrdinals[scanMode] = recentShowMoreButtonOrdinal
			self._unifiedRecentCounts[scanMode] = recentItemCount
			self._chatHistoryScanGenerations[scanMode] += 1
		if scanMode not in ("chatgpt", "codex") or recentSnapshot is None:
			self._cacheChatHistoryScan(
				scanMode, recentSnapshot, archivedSnapshot,
			)
		else:
			now = time.monotonic()
			modeChangedAt = self._conversationModeChangedAt
			modeAge = now - modeChangedAt if modeChangedAt else float("inf")
			pendingSnapshot = self._pendingChatHistorySnapshots[scanMode]
			pendingAt = self._pendingChatHistorySnapshotAt[scanMode]
			pendingAge = now - pendingAt if pendingSnapshot is not None and pendingAt else 0.0
			otherMode = "codex" if scanMode == "chatgpt" else "chatgpt"
			decision = chatHistorySnapshotDecision(
				modeAge, CHAT_HISTORY_MODE_SETTLE_SECONDS,
				recentSnapshot, self._chatHistoryCaches[otherMode],
				self._chatHistoryCacheCurrent[otherMode],
				pendingSnapshot, pendingAge, CHAT_HISTORY_SNAPSHOT_CONFIRM_SECONDS,
			)
			if decision == "publish":
				self._ambiguousRecentChatTitles[scanMode] = ambiguousRecentTitles
				self._pendingChatHistorySnapshots[scanMode] = None
				self._pendingChatHistorySnapshotAt[scanMode] = 0.0
				self._lastDeferredHistoryLog = ()
				self._lastDeferredHistoryLogAt = 0.0
				self._cacheChatHistoryScan(
					scanMode,
					self._modeSpecificRecentChatTitles(scanMode, recentSnapshot),
					archivedSnapshot,
				)
			else:
				if decision == "confirm" and pendingSnapshot != recentSnapshot:
					self._pendingChatHistorySnapshots[scanMode] = recentSnapshot
					self._pendingChatHistorySnapshotAt[scanMode] = now
				elif decision == "otherMode":
					self._pendingChatHistorySnapshots[scanMode] = None
					self._pendingChatHistorySnapshotAt[scanMode] = 0.0
				delay = CHAT_HISTORY_RETRY_MILLISECONDS
				if decision == "settle":
					delay = max(150, int(
						(CHAT_HISTORY_MODE_SETTLE_SECONDS - modeAge) * 1000
					) + 1)
				self._schedulePoll(delay=delay, requestInspection=True)
				logSnapshot = (scanMode, decision)
				if shouldLogDiagnosticSnapshot(
					logSnapshot, self._lastDeferredHistoryLog,
					now - self._lastDeferredHistoryLogAt,
				):
					log.debug(
						"ChatGPT Desktop Access deferred %s history caching: %s",
						scanMode, decision,
					)
					self._lastDeferredHistoryLog = logSnapshot
					self._lastDeferredHistoryLogAt = now
		if _settings()["diagnosticLogging"] and unknown:
			now = time.monotonic()
			# Arbitrary button labels can contain private task titles. Keep only
			# ephemeral hashes for change detection and log non-content metadata.
			snapshot = tuple((len(x), hash(x)) for x in unknown[-5:])
			if shouldLogDiagnosticSnapshot(snapshot, self._lastUnknownButtons, now - self._lastUnknownButtonsAt):
				log.debug(
					"ChatGPT Desktop Access unrecognized buttons: count=%d, lengths=%s",
					len(unknown), [len(x) for x in unknown[-5:]],
				)
				self._lastUnknownButtons = snapshot
				self._lastUnknownButtonsAt = now
		usageNotice = usageLimitNotice(" ".join(usageEvidence), _) if usageActionControls else ""
		if usageNotice:
			# Some Chromium builds expose the account banner in the virtual buffer
			# without firing an alert event. End the task here before stale Stop or
			# progress controls later in this same scan can restart Working feedback.
			self._applyUsageLimitNotice(usageNotice)
			return ""
		self._latestUserMessageNumber, submitted = userMessageSubmissionTransition(
			self._latestUserMessageNumber, latestUserMessageNumber,
		)
		self._pendingUserMessageIncrease, confirmedSubmission = confirmedUserMessageSubmission(
			self._pendingUserMessageIncrease, submitted, stopControlVisible,
		)
		if confirmedSubmission:
			self._beginPromptSubmission("new user message detected")
		if stopControlVisible and self._promptHadText and not self._busy:
			self._promptHadText = False
			self._beginPromptSubmission("Send button activated")
		self._stopControlVisible, stopped = stopControlTransition(self._stopControlVisible, stopControlVisible)
		if stopped and self._busy and not latest:
			self._setBusy(False, "stop control disappeared")
		if stopControlVisible:
			# A Stop button was seen, so its disappearance will end the turn.
			self._submittedTurnUnconfirmedAt = 0.0
		elif submittedTurnFinishedUnseen(
			self._submittedTurnUnconfirmedAt, time.monotonic(), self._busy, stopControlVisible, latest,
			self._promptDraftText,
		):
			self._submittedTurnUnconfirmedAt = 0.0
			log.debug("ChatGPT Desktop Access found no Stop button after a submitted turn")
			self._queueResponseCompletion()
		latestResponseMarker = responseCompletionScanMarker(
			responseCompleteMarkerCount, latestDetailedResponseMarker,
		)
		self._latestResponseMarker, self._responseMarkerInitialized, responseCompleted = responseCompletionTransition(
			self._latestResponseMarker, self._responseMarkerInitialized, latestResponseMarker, self._busy,
		)
		if responseCompleted:
			self._queueResponseCompletion()
		return latest

	def _shouldAnnounce(self, category):
		conf = _settings()
		return conf[CATEGORY_SETTING[category]] and conf[CATEGORY_OUTPUT_CONFIG.get(category, "outputOther")] != "off"

	def _announceLabel(self, label):
		category, safeMessage = statusDetails(label)
		if not category or nativeTaskTimer(label):
			return
		if shouldSuppressTrailingCompletion(category, self._busy, self._lastStateReason, label):
			log.debug("ChatGPT Desktop Access ignored an operation completion after task end")
			return
		if self._usageLimitActive:
			# Stale progress and completion labels can remain beneath the pop-over.
			# Do not resume output until the user explicitly submits again.
			return
		# Explicit Codex activity owns the busy state from this point onward.
		self._pluginProgressOwnedBusy.clear()
		# New work supersedes a tentative response-completion announcement.
		if supersedesResponseCompletionCandidate(label):
			self._pendingResponseCompletionAt = 0.0
		taskCompletion = category == "completion" and isTaskCompletionLabel(label)
		stateCategory = category if category != "completion" or taskCompletion else ""
		self._setBusy(nextBusyState(self._busy, stateCategory), category)
		if category == "working":
			return
		if category != "completion":
			self._activeCategory = category
		elif not taskCompletion:
			self._activeCategory = intermediateCompletionCategory(label) or self._activeCategory
		if not self._shouldAnnounce(category):
			return
		conf = _settings()
		message = statusMessage(
			label, _, conf["verbosity"], conf["redactSensitive"], conf["fullSpeechProfile"],
			conf["minimalSpeechProfile"],
		)
		brailleMessage = brailleStatusMessage(label, _, conf["brailleDetail"], conf["redactSensitive"])
		self._latestFullMessage = brailleMessage
		if category == "command" and conf["verbosity"] == "full":
			message, shortened = formatCommandSpeech(
				message, conf["commandPunctuation"], conf["maximumSpokenCommandCharacters"],
			)
			if shortened:
				message += _(" Complete command available with Copy latest full Codex progress.")
		priority = announcementPriority(category, message)
		action = soundKey(category, message) if category == "completion" else category
		message = _customizeAnnouncement(message, action)
		log.info("ChatGPT Desktop Access detected activity: %s", safeMessage)
		self._latestMessage = message
		fallbackPlayed = self._speakOnce(message, category, action, priority, brailleMessage)
		completionMode = conf[CATEGORY_OUTPUT_CONFIG["completion"]]
		if category == "completion" and conf["completionSound"] and completionMode in ("all", "sound") and not fallbackPlayed:
				_safeBeep(880, 80)

	def _applyScannedLabel(self, label, now):
		"""Apply one successful compatibility scan to the task state machine."""
		self._lastScannedLabel = label
		if label and label != self._lastLabel and supersedesResponseCompletionCandidate(label):
			self._pendingResponseCompletionAt = 0.0
		if not label:
			if not self._haveBaseline:
				self._haveBaseline, self._lastLabel = True, ""
				log.info("ChatGPT Desktop Access baseline established: no activity")
			elif self._lastLabel:
				self._lastLabel = ""
				log.debug("ChatGPT Desktop Access activity cleared")
			if now - self._lastNoStatusLogAt >= 30.0:
				self._lastNoStatusLogAt = now
				log.debug("ChatGPT Desktop Access scanned buffer; no activity button found")
			return
		if not self._haveBaseline:
			self._lastLabel, self._haveBaseline = label, True
			baselineCategory = statusDetails(label)[0]
			stateCategory = baselineCategory if baselineCategory != "completion" or isTaskCompletionLabel(label) else ""
			self._setBusy(nextBusyState(self._busy, stateCategory), "baseline")
			return
		if label != self._lastLabel:
			self._lastLabel = label
			self._announceLabel(label)

	def _poll(self):
		pollTimer = self._timer
		try:
			self._nextPollAt = 0.0
			now = time.monotonic()
			self._lastPollAt = now
			conversationDetached = False
			if self._conversationWindowHandle:
				conversationDetached = self._detachConversationIfWindowClosed(now)
			if self._buffer is None and not conversationDetached:
				self._rememberBuffer(api.getFocusObject())
			if self._buffer:
				if not self._conversationModeObserved and (
					not self._lastConversationModeProbeAt
					or now - self._lastConversationModeProbeAt >= MODE_CONTROL_RETRY_SECONDS
				):
					self._queueConversationModeProbe("mode switch UI Automation retry")
				elapsed = now - self._lastBufferInspectionAt if self._lastBufferInspectionAt else float("inf")
				promptTyping = bool(
					self._brailleCompositionActive
					or (self._appFocusState and now < self._promptTypingUntil)
					or (self._appFocusState and now < self._conversationNavigationUntil)
				)
				if (
					self._buffer is not getattr(self, "_unsupportedScanBuffer", None)
					# A scan blocks NVDA: never during an Add files and more activation,
					# and only rarely when scans are slow.
					and not self._attachmentMenuFlowActive()
					and elapsed >= slowScanPauseSeconds(getattr(self, "_lastBufferInspectionSeconds", 0.0))
					and bufferInspectionDue(
						self._bufferDirty, elapsed, self._active or self._busy,
						self._appFocusState, promptTyping,
					)
				):
					# Clear the dirty flag before inspection. A concurrent relevant event
					# can set it again, while a failed provider call backs off to fallback
					# cadence instead of hammering the same stale IA2 object.
					self._bufferDirty = False
					self._lastBufferInspectionAt = now
					inspectionStartedAt = time.perf_counter()
					try:
						label = self._latestButtonStatus(_conversationScanInfo(self._buffer))
					except NotImplementedError:
						self._unsupportedScanBuffer = self._buffer
						self._lastInspectionError = "unsupported text provider; using live events"
						log.warning("ChatGPT Desktop Access disabled unsafe scans for this text provider; live events remain enabled")
					except Exception:
						self._lastInspectionError = "virtual buffer inspection failed"
						log.debugWarning(
							"ChatGPT Desktop Access could not inspect the virtual buffer; preserving task state",
							exc_info=True,
						)
					else:
						self._bufferInspectionCount += 1
						self._lastInspectionError = "none"
						self._applyScannedLabel(label, now)
					finally:
						self._lastBufferInspectionSeconds = time.perf_counter() - inspectionStartedAt
						self._recordOperationTiming("conversation scan", self._lastBufferInspectionSeconds * 1000)
				else:
					self._skippedBufferInspectionCount += 1
			label = self._lastScannedLabel
			if shouldFinalizeResponseCompletion(
				self._pendingResponseCompletionAt,
				now - self._pendingResponseCompletionAt if self._pendingResponseCompletionAt else 0.0,
				RESPONSE_COMPLETION_SETTLE_SECONDS,
				self._busy, self._stopControlVisible, label,
			):
				self._pendingResponseCompletionAt = 0.0
				self._lastScannedLabel = ""
				self._haveBaseline, self._lastLabel = True, "Response complete"
				self._announceLabel("Response complete")
			self._active = bool(self._lastScannedLabel) or self._busy
		except Exception:
			log.debugWarning("ChatGPT Desktop Access polling housekeeping failed", exc_info=True)
			self._lastInspectionError = "polling housekeeping failed"
		finally:
			if self._timer is pollTimer and pollTimer is not None:
				delay = pollDelay(self._active, _settings()["idlePollMs"])
				self._timer = wx.CallLater(delay, self._poll)
				self._nextPollAt = time.monotonic() + delay / 1000.0

	def _speakOnce(
		self, message, category="other", soundCategory=None, priority=None,
		brailleMessage=None, protectBrailleReading=True,
	):
		if self._paused:
			return False
		now = time.monotonic()
		brailleOutput = brailleMessage if brailleMessage is not None else message
		comparisonMessage = brailleOutput or message or category
		soundDuplicate = shouldSuppressSemanticDuplicate(comparisonMessage, self._lastMessage, now - self._lastMessageAt)
		channelDuplicates = duplicateChannelActions(
			message, brailleOutput, self._lastSpeechMessage, self._lastBrailleMessage,
			now - self._lastSpeechMessageAt, now - self._lastBrailleMessageAt,
		)
		speechDuplicate = channelDuplicates["speech"]
		brailleDuplicate = channelDuplicates["braille"]
		self._lastMessage, self._lastMessageAt = comparisonMessage, now
		conf = _settings()
		mode = conf[CATEGORY_OUTPUT_CONFIG.get(category, "outputOther")]
		actions = categoryOutputActions(mode, conf["speech"], conf["braille"], conf["soundWhenSpeechUnavailable"])
		effectivePriority = priority or announcementPriority(category, message)
		if protectBrailleReading and shouldSuppressRoutineBraille(
			conf["protectBrailleReading"], self._appFocusState, category, effectivePriority,
			self._conversationBrowseModeActive(),
		):
			actions["braille"] = False
		if category not in ("backgroundPulse1", "backgroundPulse2"):
			self._recordHistory(message, brailleOutput)
		if actions["speech"] and message and not speechDuplicate:
			self._lastSpeechMessage, self._lastSpeechMessageAt = message, now
		if actions["braille"] and brailleOutput and not brailleDuplicate:
			self._lastBrailleMessage, self._lastBrailleMessageAt = brailleOutput, now
		if conf["diagnosticLogging"] and speechDuplicate and brailleDuplicate and soundDuplicate:
			log.debug("ChatGPT Desktop Access suppressed duplicate %s event on all enabled channels", category)
		return _send(
			message, actions["speech"] and bool(message) and not speechDuplicate,
			actions["braille"] and bool(brailleOutput) and not brailleDuplicate,
			soundCategory or category, actions["sound"] and not soundDuplicate,
			priority=effectivePriority, brailleMessage=brailleOutput,
		)

	def _setBusy(self, busy, reason):
		# The compatibility scanner and plugin installer still use this state.
		# Recurring task feedback is driven separately by the native timer.
		busy = bool(busy)
		if not busy and self._nativeTimerSeconds is None:
			_discardPendingActivitySounds()
		if busy == self._busy:
			self._lastStateReason = reason
			return
		self._busy = busy
		if not busy:
			self._submittedTurnUnconfirmedAt = 0.0
		self._lastStateReason = reason
		if busy:
			self._busyTimeout = wx.CallLater(_settings()["maximumBusyMinutes"] * 60000, self._expireBusyState)
		elif self._busyTimeout is not None:
			self._busyTimeout.Stop()
			self._busyTimeout = None
		log.info(
			"ChatGPT Desktop Access background state: %s (%s)",
			"active" if busy else "idle", reason,
		)

	def _expireBusyState(self):
		self._busyTimeout = None
		self._setBusy(False, "maximum activity timeout")

	def _announceBackgroundPulse(self, elapsed, conf, actions):
		self._backgroundPulseCount += 1
		toneCategory = "backgroundPulse1" if self._backgroundPulseCount % 2 else "backgroundPulse2"
		name = _("Processing")
		duration = formatElapsedDuration(elapsed, _)
		fullMessage = _("{activity} still running, {duration}").format(activity=name, duration=duration)
		minimalProfile = conf["minimalSpeechProfile"]
		if conf["verbosity"] == "minimal" and minimalProfile == "essential":
			message = ""
		elif conf["verbosity"] == "minimal" and minimalProfile == "balanced" and elapsed < 30:
			message = _("{activity} still running").format(activity=name)
		else:
			message = fullMessage
		if message:
			message = _customizeAnnouncement(message, toneCategory, name, elapsed)
		if shouldSuppressRoutineBraille(
			conf["protectBrailleReading"], self._appFocusState, toneCategory, "low",
			self._conversationBrowseModeActive(),
		):
			actions["braille"] = False
		return _send(
			message, actions["speech"] and bool(message), actions["braille"], toneCategory,
			actions["sound"], priority="low", brailleMessage=fullMessage,
		)

	def _isSidebarChatButton(self, obj, label):
		"""True for a chat title in ChatGPT's sidebar or menus, which can read like progress.

		Sidebar chats are buttons inside a list item of the same name, and their
		titles are remembered from each conversation scan. Progress controls in
		the conversation are neither.
		"""
		key = " ".join(str(label or "").casefold().split())
		if not key:
			return False
		if key in getattr(self, "_sidebarChatTitleKeys", ()):
			return True
		if ATTACHMENT_POPUP_ROW_CLASS in _domClassNames(obj):
			# A row of the "@", "/", or Add files and more menu, which lists chat titles.
			return True
		try:
			parent = getattr(obj, "parent", None)
			return bool(
				parent is not None and getattr(parent, "role", None) == Role.LISTITEM
				and " ".join(str(getattr(parent, "name", "") or "").casefold().split()) == key
			)
		except Exception:
			return False

	def _announceStatus(self, obj):
		if getattr(obj, "role", None) != Role.BUTTON or not _isConversationObject(obj):
			return False
		label = getattr(obj, "name", "")
		if statusDetails(label)[0] and not self._isSidebarChatButton(obj, label):
			self._lastScannedLabel = label
			self._haveBaseline, self._lastLabel = True, label
			self._announceLabel(label)
			return True
		return False

	def _announceCommentary(self, obj):
		if not _isConversationObject(obj):
			return False
		if getattr(obj, "role", None) in (Role.BUTTON, Role.EDITABLETEXT):
			return False
		if self._usageLimitActive:
			return True
		text = " ".join(str(getattr(obj, "name", "") or getattr(obj, "value", "") or "").split())
		if not text:
			return False
		if nativeTaskTimer(text):
			return True
		category = statusDetails(text)[0]
		if category:
			# Chromium can expose completion and progress as a non-button live region.
			# Route it through the normal state machine instead of discarding it as
			# status-like commentary. Avoid repeating response text in Full mode.
			label = "Response complete" if text.lower().startswith("response complete") else text
			if label == "Response complete":
				self._lastScannedLabel = ""
				self._queueResponseCompletion()
				return True
			if category == "completion" and self._haveBaseline and label == self._lastLabel:
				return True
			self._lastScannedLabel = label
			self._haveBaseline, self._lastLabel = True, label
			self._announceLabel(label)
			return True
		if not _settings()["announceCommentary"]:
			return True
		key = id(obj)
		if key not in self._commentaryOffsets and len(self._commentaryOffsets) >= 256:
			self._commentaryOffsets.pop(next(iter(self._commentaryOffsets)))
		previousText, offset = self._commentaryOffsets.get(key, ("", 0))
		if previousText and not text.startswith(previousText[:offset]):
			offset = 0
		message, newOffset = completedTextDelta(text, offset)
		self._commentaryOffsets[key] = (text, newOffset)
		if message:
			# Final-response commentary can arrive after the completion control.
			# It may refresh an active task, but must never restart one.
			self._pluginProgressOwnedBusy.clear()
			self._setBusy(nextBusyState(self._busy, commentary=True), "commentary")
			log.info("ChatGPT Desktop Access detected activity: Commentary update")
			conf = _settings()
			fullMessage = redactSensitive(message) if conf["redactSensitive"] else message
			message = fullMessage
			if conf["verbosity"] == "minimal":
				profile = conf["minimalSpeechProfile"]
				if profile == "essential":
					message = ""
				else:
					wordLimit = 18 if profile == "balanced" else 30
					words = message.split()
					message = " ".join(words[:wordLimit]) + ("…" if len(words) > wordLimit else "")
			if message:
				message = _customizeAnnouncement(message, "commentary")
			self._latestMessage = message or fullMessage
			self._latestFullMessage = fullMessage
			self._speakOnce(message, "commentary", brailleMessage=fullMessage)
		return True

	@script(description=_("Report current Codex activity or repeat the latest message"))
	def script_repeatLatestStatus(self, gesture):
		elapsed = self._nativeTimerSeconds
		agentName = _("ChatGPT") if self._conversationMode == "chatgpt" else _("Codex")
		message = currentActivitySummary(
			elapsed is not None, "working", self._latestMessage, elapsed, _, agentName,
		)
		conf = _settings()
		_send(
			message, conf["speech"], conf["braille"], "other", conf["soundWhenSpeechUnavailable"],
			brailleMessage=self._latestFullMessage or message,
		)

	@script(description=_("Toggle Minimal and Full Codex announcements"))
	def script_toggleVerbosity(self, gesture):
		conf = _settings()
		conf["verbosity"] = "minimal" if conf["verbosity"] == "full" else "full"
		modeName = _("Minimal") if conf["verbosity"] == "minimal" else _("Full")
		message = _("Codex announcements: {mode}").format(mode=modeName)
		_send(message, conf["speech"], conf["braille"], "other", conf["soundWhenSpeechUnavailable"])

	@script(description=_("Pause or resume Codex announcements"))
	def script_togglePause(self, gesture):
		self._paused = not self._paused
		ui.message(_("Codex announcements paused") if self._paused else _("Codex announcements resumed"))

	@script(description=_("Read the previous Codex announcement"))
	def script_previousHistory(self, gesture):
		self._historyMessage(-1)

	@script(description=_("Read the next Codex announcement"))
	def script_nextHistory(self, gesture):
		self._historyMessage(1)

	@script(description=_("Show Codex announcement history"))
	def script_showHistory(self, gesture):
		if not self._speechHistory and not self._brailleHistory:
			ui.message(_("No activity announcement history is available"))
			return
		sections = []
		if self._speechHistory:
			sections.append(_("Speech history") + "\n" + "\n".join(self._speechHistory.items()))
		if self._brailleHistory and self._brailleHistory.items() != self._speechHistory.items():
			sections.append(_("Braille history") + "\n" + "\n".join(self._brailleHistory.items()))
		ui.browseableMessage("\n\n".join(sections), title=_("ChatGPT Desktop Access announcement history"))

	@script(description=_("Clear Codex announcement history"))
	def script_clearHistory(self, gesture):
		self._speechHistory.clear()
		self._brailleHistory.clear()
		ui.message(_("Codex announcement history cleared"))

	@script(description=_("Toggle Codex privacy redaction"))
	def script_togglePrivacy(self, gesture):
		conf = _settings()
		conf["redactSensitive"] = not conf["redactSensitive"]
		ui.message(_("Codex privacy redaction on") if conf["redactSensitive"] else _("Codex privacy redaction off"))

	@script(description=_("Show sanitized ChatGPT Desktop Access diagnostics"))
	def script_showDiagnostics(self, gesture):
		ui.browseableMessage(self._diagnosticReport(), title=_("ChatGPT Desktop Access diagnostics"))

	@script(description=_("Copy sanitized ChatGPT Desktop Access diagnostics"))
	def script_copyDiagnostics(self, gesture):
		if not wx.TheClipboard.Open():
			ui.message(_("Could not open the clipboard"))
			return
		try:
			wx.TheClipboard.SetData(wx.TextDataObject(self._diagnosticReport()))
			wx.TheClipboard.Flush()
		finally:
			wx.TheClipboard.Close()
		ui.message(_("Sanitized Codex diagnostics copied"))

	@script(description=_("Save a sanitized ChatGPT Desktop Access support report"))
	def script_saveSupportReport(self, gesture):
		_saveSupportReport(gui.mainFrame, self._diagnosticReport())

	@script(description=_("Capture diagnostics for the open Add files and more menu"))
	def script_captureAttachmentMenuDiagnostics(self, gesture):
		self._attachmentDiagnostics.captureNow()

	@script(description=_("Copy latest full Codex progress"))
	def script_copyLatestFullProgress(self, gesture):
		if not self._latestFullMessage:
			ui.message(_("No complete Codex progress message is available"))
			return
		if not wx.TheClipboard.Open():
			ui.message(_("Could not open the clipboard"))
			return
		try:
			wx.TheClipboard.SetData(wx.TextDataObject(self._latestFullMessage))
			wx.TheClipboard.Flush()
		finally:
			wx.TheClipboard.Close()
		ui.message(_("Latest full Codex progress copied"))

	@script(description=_("Run ChatGPT Desktop Access compatibility self-test"))
	def script_runCompatibilitySelfTest(self, gesture):
		checks = [
			_("Global plugin loaded: yes"),
			_("Codex monitoring attached: {value}").format(value=_("yes") if self._buffer else _("no")),
			_("Speech enabled: {value}").format(value=_("yes") if _settings()["speech"] else _("no")),
			_("Braille enabled: {value}").format(value=_("yes") if _settings()["braille"] else _("no")),
			_("Sound inventory: {count} files").format(count=len(list((Path(__file__).parent / "sounds").rglob("*.wav")))),
			_("Recent chats cached: {count}").format(count=len(self._chatHistoryTitles())),
			_("Archived chats cached: {count}").format(count=len(self._loadArchivedChatHistory()[0])),
			_("Native embedded browser navigation: yes"),
			_("Embedded browser loading announcements: {value}").format(
				value=_("yes") if _settings()["announceEmbeddedBrowserProgress"] else _("no"),
			),
			_("Embedded browser focus detected: {value}").format(
				value=_("yes") if self._embeddedBrowserFocused else _("no"),
			),
			_("Last inspection error: {value}").format(value=self._lastInspectionError),
		]
		_showBrowseableMessageAtTop("\n".join(checks), _("ChatGPT Desktop Access — compatibility self-test"))

	@script(description=_("Open ChatGPT usage and credits"))
	def script_openUsageStatistics(self, gesture):
		_openUsageDashboard(_("Opening ChatGPT usage and credits. No purchase will be made automatically."))

	def script_openUsageCredits(self, gesture):
		# Retain existing user gesture assignments without exposing a duplicate action.
		self.script_openUsageStatistics(gesture)

	def _cancelPendingChatHistoryOpen(self):
		"""Cancel an automatic History open without affecting an active dialog."""
		if getattr(self, "_chatHistoryOpenTimer", None):
			self._chatHistoryOpenTimer.Stop()
			self._chatHistoryOpenTimer = None
		self._pendingChatHistoryOpen = None

	def _schedulePendingChatHistoryOpen(self, delay):
		"""Resume a user-requested History open after mode or cache state changes."""
		if not getattr(self, "_pendingChatHistoryOpen", None):
			return False
		if self._chatHistoryOpenTimer:
			self._chatHistoryOpenTimer.Stop()
		self._chatHistoryOpenTimer = wx.CallLater(
			max(0, int(delay)), self._continuePendingChatHistoryOpen,
		)
		return True

	def _requestChatHistoryOpen(self):
		"""Start one asynchronous History request that completes without a second gesture."""
		windowHandle = self._conversationWindowHandle
		if not self._buffer or not windowHandle:
			ui.message(_("Chat history is not available in the current view"))
			return False
		pending = self._pendingChatHistoryOpen
		if pending and pending.get("windowHandle") == windowHandle:
			ui.message(_("Chat history is already opening"))
			self._schedulePendingChatHistoryOpen(0)
			return True
		self._cancelPendingChatHistoryOpen()
		self._pendingChatHistoryOpen = {
			"windowHandle": windowHandle,
			"startedAt": time.monotonic(),
		}
		ui.message(_("Opening chat history"))
		self._bufferDirty = True
		self._schedulePoll(delay=50, requestInspection=True)
		self._schedulePendingChatHistoryOpen(0)
		return True

	def _continuePendingChatHistoryOpen(self):
		"""Finish mode detection, cache refresh, and History opening from one key press."""
		self._chatHistoryOpenTimer = None
		pending = self._pendingChatHistoryOpen
		if not pending:
			return
		now = time.monotonic()
		if (
			pending.get("windowHandle") != self._conversationWindowHandle
			or not self._buffer
			or not _isChatGPTObject(api.getFocusObject())
		):
			self._cancelPendingChatHistoryOpen()
			return
		if now - pending.get("startedAt", now) >= CHAT_HISTORY_OPEN_TIMEOUT_SECONDS:
			self._cancelPendingChatHistoryOpen()
			ui.message(_("Chat history could not be loaded from this view"))
			log.debugWarning("ChatGPT Desktop Access timed out while opening chat history")
			return
		if not self._conversationModeObserved:
			if not self._conversationModeProbePendingGeneration:
				self._queueConversationModeProbe("history mode verification")
			# A virtual-buffer scan is an independent fallback when Chromium's UIA
			# worker is occupied. Whichever source identifies the selector first resumes
			# this same request; neither path blocks NVDA's main thread.
			self._bufferDirty = True
			self._schedulePoll(delay=50, requestInspection=True)
			self._schedulePendingChatHistoryOpen(CHAT_HISTORY_OPEN_RETRY_MILLISECONDS)
			return
		mode = self._conversationMode
		if mode not in ("chatgpt", "codex"):
			self._schedulePendingChatHistoryOpen(CHAT_HISTORY_OPEN_RETRY_MILLISECONDS)
			return
		if not self._chatHistoryCacheCurrent.get(mode, False):
			self._bufferDirty = True
			self._schedulePoll(delay=50, requestInspection=True)
			self._schedulePendingChatHistoryOpen(CHAT_HISTORY_OPEN_RETRY_MILLISECONDS)
			return
		if self._pendingChatHistoryExpansion:
			return
		if self._startChatHistoryExpansion(mode):
			return
		self._showChatHistoryDialog(mode)

	def _showChatHistoryDialog(self, mode):
		"""Present the settled mode-specific history without starting another expansion."""
		agentName = _("ChatGPT") if mode == "chatgpt" else _("Codex")
		if mode != self._conversationMode or mode not in ("chatgpt", "codex"):
			ui.message(_("The chat-history mode changed. Open chat history again"))
			return False
		if not self._chatHistoryCacheCurrent.get(mode, False):
			self._schedulePoll(delay=150, requestInspection=True)
			if self._pendingChatHistoryOpen:
				self._schedulePendingChatHistoryOpen(CHAT_HISTORY_OPEN_RETRY_MILLISECONDS)
			else:
				ui.message(_("{agent} chat history is refreshing").format(agent=agentName))
			log.info("ChatGPT Desktop Access deferred opening unsettled %s chat history", mode)
			return False
		recentTitles = self._chatHistoryTitles(mode)
		archivedTitles, archivedLoaded = self._loadArchivedChatHistory(mode)
		if not recentTitles and not archivedTitles:
			self._cancelPendingChatHistoryOpen()
			ui.message(_("No {agent} chats are cached yet. Wait a moment and try again").format(agent=agentName))
			return False
		if self._chatHistoryDialog:
			if self._chatHistoryDialogMode == mode:
				self._cancelPendingChatHistoryOpen()
				self._chatHistoryDialog.Raise()
				self._chatHistoryDialog.search.SetFocus()
				return True
			self._chatHistoryDialog.Close()
		gui.mainFrame.prePopup()
		try:
			self._chatHistoryDialog = ChatHistoryDialog(
				gui.mainFrame, mode, agentName, recentTitles, archivedTitles, archivedLoaded,
				lambda: self._refreshChatHistoryData(mode),
				self._queueChatHistoryAction, self._chatHistoryClosed,
			)
			self._chatHistoryDialogMode = mode
			self._chatHistoryDialog.Show()
			self._cancelPendingChatHistoryOpen()
		except Exception:
			self._chatHistoryDialog = None
			gui.mainFrame.postPopup()
			raise
		log.info(
			"ChatGPT Desktop Access displayed %d recent and %d archived %s chats",
			len(recentTitles), len(archivedTitles), mode,
		)
		return True

	@script(description=_("Open searchable and arrow-navigable ChatGPT or Codex chat history"))
	def script_openChatHistory(self, gesture):
		"""Expand native Recents, then show searchable Recent and Archived lists."""
		focus = api.getFocusObject()
		if not _isChatGPTObject(focus):
			ui.message(_("Move to ChatGPT or Codex before opening chat history"))
			return
		try:
			self._rememberBuffer(focus, allowUnclassifiedConversation=True)
			self._requestChatHistoryOpen()
		except Exception:
			self._cancelPendingChatHistoryOpen()
			log.debugWarning("ChatGPT Desktop Access could not display chat history", exc_info=True)
			ui.message(_("Chat history could not be opened"))

	def event_typedCharacter(self, obj, nextHandler, ch):
		nextHandler()
		try:
			if ch in SUGGESTION_MENU_TRIGGER_CHARACTERS:
				self._scheduleSuggestionMenuRead("open", SUGGESTION_MENU_OPEN_DELAY_MILLISECONDS)
			elif getattr(self, "_suggestionMenuOpen", False) and str(ch or "").strip():
				self._scheduleSuggestionMenuRead("filter", SUGGESTION_MENU_FILTER_DELAY_MILLISECONDS)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not follow a typed suggestion character", exc_info=True)

	def event_gainFocus(self, obj, nextHandler):
		nextHandler()
		try:
			if _isChatGPTObject(obj):
				self._rememberConversationWindowFromEvent(obj)
			else:
				self._rememberExternalFocus(obj)
			focusCue = self._updateAppFocusState(obj)
			self._updateEmbeddedBrowserFocus(obj)
			self._rememberBuffer(obj)
			self._resumeAttachmentSourceFocus()
			self._scheduleConversationEntryCorrection(obj)
			self._confirmConversationModeAfterSelector(obj)
			self._noteAttachmentMenuControl(obj, focused=True)
			if self._attachmentMenuActiveAt and (
				_isCodexPromptObject(obj)
				or promptControlKind(getattr(obj, "name", "")) in ("model", "permissions")
			):
				self._resetAttachmentMenuTracking()
			self._announceAttachmentMenuSelection(obj, speak=False)
			self._schedulePopupDialogFocus(obj)
			if self._announceUsageLimit(obj):
				return
			isPrompt = _isCodexPromptObject(obj)
			self._promptFocused = isPrompt
			if isPrompt:
				self._lastPromptObject = obj
			if not isPrompt:
				self._brailleCompositionActive = False
			if isPrompt:
				self._trackPromptDraftState(obj)
			# ChatGPT briefly focuses an intermediate section after Enter and before
			# returning to the now-empty prompt. Preserve draft/submission state across
			# those in-app focus events; _resetTaskState handles real task switches.
			if _isChatGPTObject(obj):
				# Moving among controls does not change task status. Inspect once when
				# returning to ChatGPT; a newly attached buffer is already marked dirty.
				self._schedulePoll(requestInspection=focusCue == "active")
		except Exception:
			log.debugWarning("ChatGPT Desktop Access focus-event handling failed", exc_info=True)

	def event_foreground(self, obj, nextHandler):
		nextHandler()
		try:
			if _isChatGPTObject(obj):
				self._rememberConversationWindowFromEvent(obj)
			else:
				self._rememberExternalFocus(obj)
			focusCue = self._updateAppFocusState(obj)
			self._updateEmbeddedBrowserFocus(obj)
			self._rememberBuffer(obj)
			if self._announceUsageLimit(obj):
				return
			if _isChatGPTObject(obj):
				self._schedulePoll(requestInspection=focusCue == "active")
		except Exception:
			log.debugWarning("ChatGPT Desktop Access foreground-event handling failed", exc_info=True)

	def event_nameChange(self, obj, nextHandler):
		nextHandler()
		if not _isChatGPTObject(obj):
			return
		try:
			self._noteAttachmentMenuControl(obj)
			if self._attachmentMenuSelectionState(obj):
				self._announceAttachmentMenuSelection(obj)
			if self._observeConversationModeControl(obj, "mode switch name event"):
				self._schedulePoll(requestInspection=True)
			self._noteEmbeddedBrowserDocument(obj)
			self._rememberBuffer(obj)
			self._schedulePopupDialogFocus(obj)
			if self._announceUsageLimit(obj):
				return
			self._announceEmbeddedBrowserProgress(obj)
			statusHandled = self._announceStatus(obj)
			if getattr(obj, "role", None) == Role.BUTTON and self._eventUsesConversationBuffer(obj):
				self._schedulePoll(requestInspection=not statusHandled)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access name-change handling failed", exc_info=True)

	def event_valueChange(self, obj, nextHandler):
		nextHandler()
		if not _isChatGPTObject(obj):
			return
		try:
			self._noteAttachmentMenuControl(obj)
			self._announceAttachmentMenuSelection(obj)
			if self._announceUsageLimit(obj):
				return
			isPrompt = self._notePromptTyping(obj)
			self._trackPromptDraftState(obj, allowTextInfo=not isPrompt)
			if isPrompt:
				self._schedulePromptInspection(obj)
			pluginHandled = self._announcePluginInstallProgress(obj)
			self._announceEmbeddedBrowserProgress(obj)
			statusHandled = self._announceStatus(obj)
			if getattr(obj, "role", None) == Role.BUTTON and self._eventUsesConversationBuffer(obj):
				self._schedulePoll(requestInspection=not (pluginHandled or statusHandled))
		except Exception:
			log.debugWarning("ChatGPT Desktop Access value-change handling failed", exc_info=True)

	def event_stateChange(self, obj, nextHandler):
		nextHandler()
		if not _isChatGPTObject(obj):
			return
		try:
			self._noteAttachmentMenuControl(obj)
			if self._attachmentMenuSelectionState(obj):
				self._announceAttachmentMenuSelection(obj)
			if self._observeConversationModeControl(obj, "mode switch state event"):
				self._schedulePoll(requestInspection=True)
			if self._announceUsageLimit(obj):
				return
			self._updateEmbeddedBrowserDocumentBusyState(obj)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access state-change handling failed", exc_info=True)

	def event_liveRegionChange(self, obj, nextHandler):
		if not _isChatGPTObject(obj):
			nextHandler()
			return
		suppressNative = False
		text = ""
		limitHandled = False
		try:
			text = " ".join(str(
				getattr(obj, "name", "") or getattr(obj, "value", "") or ""
			).split())
			limitHandled = self._announceUsageLimit(obj, text)
			# Chromium can rebuild the event object's tree interceptor while the user
			# remains in the same conversation buffer. Determine reading mode from the
			# retained conversation buffer so a replacement live-region object cannot
			# bypass protection and relocate speech or the Braille viewport.
			browseMode = self._conversationBrowseModeActive()
			suppressNative = limitHandled or shouldSuppressNativeConversationUpdate(
				_settings()["protectBrailleReading"], self._appFocusState, browseMode,
				self._eventUsesConversationBuffer(obj), self._popupDialogFromObject(obj) is not None,
				text,
			)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access could not classify a conversation live update", exc_info=True)
		if suppressNative:
			self._suppressedConversationUpdates += 1
			log.debug("ChatGPT Desktop Access preserved browse-mode reading across a streamed response update")
		else:
			nextHandler()
		try:
			self._schedulePopupDialogFocus(obj)
			if limitHandled or self._announceUsageLimit(obj, text):
				return
			statusHandled = self._announceStatus(obj)
			# Ordinary Response text was intentionally withheld from NVDA's native
			# live-region handler above, so do not reintroduce the same interruption
			# through add-on commentary. Completion still reaches the state machine.
			if suppressNative and not statusDetails(text)[0]:
				commentaryHandled = True
			else:
				commentaryHandled = self._announceCommentary(obj)
			if getattr(obj, "role", None) == Role.BUTTON and self._eventUsesConversationBuffer(obj):
				self._schedulePoll(requestInspection=not (statusHandled or commentaryHandled))
		except Exception:
			log.debugWarning("ChatGPT Desktop Access live-region handling failed", exc_info=True)

	def event_show(self, obj, nextHandler):
		nextHandler()
		if not _isChatGPTObject(obj):
			return
		try:
			if self._attachmentMenuSelectionState(obj):
				self._announceAttachmentMenuSelection(obj)
			if self._observeConversationModeControl(obj, "mode switch show event"):
				self._schedulePoll(requestInspection=True)
			self._noteEmbeddedBrowserDocument(obj, force=True)
			self._schedulePopupDialogFocus(obj)
			if self._announceUsageLimit(obj):
				return
			pluginHandled = self._announcePluginInstallProgress(obj)
			self._announceEmbeddedBrowserProgress(obj)
			statusHandled = self._announceStatus(obj)
			if getattr(obj, "role", None) == Role.BUTTON and self._eventUsesConversationBuffer(obj):
				self._schedulePoll(requestInspection=not (pluginHandled or statusHandled))
		except Exception:
			log.debugWarning("ChatGPT Desktop Access show-event handling failed", exc_info=True)

	def event_selection(self, obj, nextHandler):
		nextHandler()
		if not _isChatGPTObject(obj):
			return
		try:
			self._announceAttachmentMenuSelection(obj)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access selection-event handling failed", exc_info=True)

	def event_selectionAdd(self, obj, nextHandler):
		nextHandler()
		if not _isChatGPTObject(obj):
			return
		try:
			self._announceAttachmentMenuSelection(obj)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access selection-add handling failed", exc_info=True)

	def event_selectionWithIn(self, obj, nextHandler):
		nextHandler()
		if not _isChatGPTObject(obj):
			return
		try:
			self._announceAttachmentMenuSelection(obj)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access selection-within handling failed", exc_info=True)

	def event_hide(self, obj, nextHandler):
		nextHandler()
		if not _isChatGPTObject(obj):
			return
		try:
			if _sameNVDAObject(obj, self._pendingPopupDialog):
				if self._popupFocusTimer:
					self._popupFocusTimer.Stop()
				self._popupFocusTimer = None
				self._pendingPopupDialog = None
				self._pendingPopupDialogWindowHandle = 0
			if self._attachmentMenuActiveAt and _roleName(obj) == "menu":
				self._resetAttachmentMenuTracking()
		except Exception:
			log.debugWarning("ChatGPT Desktop Access hide-event handling failed", exc_info=True)

	def event_alert(self, obj, nextHandler):
		nextHandler()
		if not _isChatGPTObject(obj):
			return
		try:
			self._schedulePopupDialogFocus(obj)
			self._announceUsageLimit(obj)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access alert-event handling failed", exc_info=True)

	def event_textChange(self, obj, nextHandler):
		nextHandler()
		if not _isChatGPTObject(obj):
			return
		try:
			isPrompt = self._notePromptTyping(obj)
			self._trackPromptDraftState(obj, allowTextInfo=not isPrompt)
			if isPrompt:
				self._schedulePromptInspection(obj)
		except Exception:
			log.debugWarning("ChatGPT Desktop Access text-change handling failed", exc_info=True)
