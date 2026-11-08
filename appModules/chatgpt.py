"""Application-scoped commands for the ChatGPT desktop app."""

import addonHandler
import appModuleHandler
import ui
from logHandler import log
from scriptHandler import getLastScriptRepeatCount, script


addonHandler.initTranslation()


def _activeToolkitPlugin():
	"""Return the running toolkit instance without creating another global plugin."""
	try:
		from globalPlugins import codexStatusAnnouncer
		return codexStatusAnnouncer._activePluginInstance
	except Exception:
		return None


class AppModule(appModuleHandler.AppModule):
	"""Expose commands only while ChatGPT or its Codex host has focus."""

	scriptCategory = _("ChatGPT Desktop Access")
	__gestures = {
		"kb:control+1": "readMostRecentChatMessage",
		"kb:control+2": "readSecondMostRecentChatMessage",
		"kb:control+3": "readThirdMostRecentChatMessage",
		"kb:control+4": "readFourthMostRecentChatMessage",
		"kb:control+5": "readFifthMostRecentChatMessage",
		"kb:control+6": "readSixthMostRecentChatMessage",
		"kb:control+7": "readSeventhMostRecentChatMessage",
		"kb:control+8": "readEighthMostRecentChatMessage",
		"kb:control+9": "readNinthMostRecentChatMessage",
		"kb:control+0": "readTenthMostRecentChatMessage",
		"kb:NVDA+alt+v": "toggleVoiceMode",
		"kb:NVDA+`": "toggleConversationMode",
		"kb:NVDA+alt+w": "reportOrSwitchComposerMode",
		"kb:NVDA+alt+a": "reportComposerAttachments",
	}

	def _runToolkitCommand(self, methodName, *args):
		plugin = _activeToolkitPlugin()
		handler = getattr(plugin, methodName, None) if plugin is not None else None
		if not callable(handler):
			ui.message(_("ChatGPT Desktop Access is not ready"))
			return
		try:
			handler(*args)
		except Exception:
			log.error("ChatGPT Desktop Access command failed: %s", methodName, exc_info=True)
			ui.message(_("That ChatGPT Desktop Access command could not be completed"))

	@script(description=_("Read the most recent ChatGPT message"))
	def script_readMostRecentChatMessage(self, gesture):
		self._runToolkitCommand("_readRecentChatMessage", 1)

	@script(description=_("Read the second-most-recent ChatGPT message"))
	def script_readSecondMostRecentChatMessage(self, gesture):
		self._runToolkitCommand("_readRecentChatMessage", 2)

	@script(description=_("Read the third-most-recent ChatGPT message"))
	def script_readThirdMostRecentChatMessage(self, gesture):
		self._runToolkitCommand("_readRecentChatMessage", 3)

	@script(description=_("Read the fourth-most-recent ChatGPT message"))
	def script_readFourthMostRecentChatMessage(self, gesture):
		self._runToolkitCommand("_readRecentChatMessage", 4)

	@script(description=_("Read the fifth-most-recent ChatGPT message"))
	def script_readFifthMostRecentChatMessage(self, gesture):
		self._runToolkitCommand("_readRecentChatMessage", 5)

	@script(description=_("Read the sixth-most-recent ChatGPT message"))
	def script_readSixthMostRecentChatMessage(self, gesture):
		self._runToolkitCommand("_readRecentChatMessage", 6)

	@script(description=_("Read the seventh-most-recent ChatGPT message"))
	def script_readSeventhMostRecentChatMessage(self, gesture):
		self._runToolkitCommand("_readRecentChatMessage", 7)

	@script(description=_("Read the eighth-most-recent ChatGPT message"))
	def script_readEighthMostRecentChatMessage(self, gesture):
		self._runToolkitCommand("_readRecentChatMessage", 8)

	@script(description=_("Read the ninth-most-recent ChatGPT message"))
	def script_readNinthMostRecentChatMessage(self, gesture):
		self._runToolkitCommand("_readRecentChatMessage", 9)

	@script(description=_("Read the tenth-most-recent ChatGPT message"))
	def script_readTenthMostRecentChatMessage(self, gesture):
		self._runToolkitCommand("_readRecentChatMessage", 10)

	@script(description=_("Open the current conversation's messages in a native list"))
	def script_openConversationMessages(self, gesture):
		self._runToolkitCommand("_openConversationMessageList")

	@script(description=_("Start or end ChatGPT voice mode"))
	def script_toggleVoiceMode(self, gesture):
		self._runToolkitCommand("_activateVoiceControl", ("stop", "start"))

	@script(description=_("Mute or unmute the ChatGPT microphone"))
	def script_toggleMicrophoneMute(self, gesture):
		self._runToolkitCommand("_activateVoiceControl", ("unmute", "mute"))

	@script(description=_(
		"Report whether ChatGPT's message field is set to Chat or Work; press twice to switch"
	))
	def script_reportOrSwitchComposerMode(self, gesture):
		self._runToolkitCommand("_reportOrSwitchComposerMode", getLastScriptRepeatCount() >= 1)

	@script(description=_("Report the files and tools attached to the ChatGPT message"))
	def script_reportComposerAttachments(self, gesture):
		self._runToolkitCommand("_reportComposerAttachments")

	@script(description=_("Read the native task timer"))
	def script_reportNativeTaskTimer(self, gesture):
		self._runToolkitCommand("_reportNativeTaskTimer")

	@script(description=_("Open and focus the ChatGPT and Codex mode selector"))
	def script_toggleConversationMode(self, gesture):
		"""Open ChatGPT's native selector for manual Arrow-key selection."""
		self._runToolkitCommand("_openConversationModeSelector")
