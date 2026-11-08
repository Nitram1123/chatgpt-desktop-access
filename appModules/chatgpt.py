"""Application-scoped commands for the ChatGPT desktop app."""

from collections import deque
from dataclasses import dataclass

import addonHandler
import api
import appModuleHandler
import core
import ui
from browseMode import BrowseModeDocumentTreeInterceptor
from controlTypes import Role, State
from logHandler import log
from NVDAObjects import NVDAObject
from scriptHandler import getLastScriptRepeatCount, script


addonHandler.initTranslation()

_SIDEBAR_LANDMARKS = {"Accueil", "Home"}
_PROJECT_ACTION_PREFIXES = ("Actions du projet ", "Project actions for ")
_RECENTS_LABELS = {"Récents", "Recents"}


@dataclass
class _ChatArchiveRequest:
	windowHandle: int
	chatList: NVDAObject
	row: NVDAObject
	index: int
	fallback: NVDAObject | None
	checksLeft: int = 12


def _walkObjects(root, maxDepth):
	if root is None:
		return
	objects = deque([(root, 0)])
	while objects:
		obj, depth = objects.popleft()
		yield obj
		if depth < maxDepth:
			objects.extend((child, depth + 1) for child in obj.children)


def _getMainDocument(window):
	# Start at the outer window, so a browser pane cannot supply its own title.
	return next((obj for obj in _walkObjects(window, 10) if obj.role == Role.DOCUMENT), None)


def _chatTitle(window):
	document = _getMainDocument(window)
	return (document.name or "").strip() if document is not None else ""


def _getSidebar(document):
	return next((obj for obj in _walkObjects(document, 6) if (
		obj.role == Role.LANDMARK and obj.name in _SIDEBAR_LANDMARKS and State.INVISIBLE not in obj.states
	)), None)


def _getFirstProject(sidebar):
	# Walk in sidebar order even if some project rows are nested more deeply.
	objects = [sidebar]
	while objects:
		obj = objects.pop()
		children = obj.children
		if obj.role in (Role.BUTTON, Role.LINK) and any(
			child.role == Role.BUTTON and (child.name or "").startswith(_PROJECT_ACTION_PREFIXES)
			for child in children
		):
			return obj
		objects.extend(reversed(children))
	return None


def _iterChatRows(items):
	for item in items:
		if item.role != Role.LISTITEM:
			continue
		for control in _walkObjects(item, 3):
			if control.role in (Role.BUTTON, Role.LINK) and control.name:
				yield item, control
				break


def _iterArchivableChats(chatList):
	from globalPlugins.codexStatusAnnouncer.core import chatActionMatches

	for row, control in _iterChatRows(chatList.children):
		for button in (*control.children, *row.children):
			if button.role == Role.BUTTON and button is not control and chatActionMatches("archive", button.name):
				yield row, control, button
				break


def _findSidebarChat(sidebar, position, matchFocusedState=False):
	from globalPlugins.codexStatusAnnouncer import _sameNVDAObject

	if position is None:
		return None
	focus = position
	ancestors = []
	while position is not None and position.role not in (Role.DOCUMENT, Role.LANDMARK):
		ancestors.append(position)
		position = position.parent
	if not ancestors:
		return None
	canMatchFocusedState = matchFocusedState and State.FOCUSED in focus.states
	focusedTargets = []
	for chatList in _walkObjects(sidebar, 12):
		if chatList.role != Role.LIST:
			continue
		for index, (row, control, button) in enumerate(_iterArchivableChats(chatList)):
			target = chatList, row, index, button
			candidates = (row, control, button, *control.children)
			if any(_sameNVDAObject(item, ancestor) for item in candidates for ancestor in ancestors):
				return target
			# Some focus objects are from another accessibility backend. Require one unique focused row.
			if canMatchFocusedState and any(
				item.role == focus.role and State.FOCUSED in item.states and item.name == focus.name
				for item in candidates
			):
				focusedTargets.append(target)
	return focusedTargets[0] if len(focusedTargets) == 1 else None


def _chatListFallback(sidebar, chatList):
	parent = chatList.parent
	while parent is not None and parent != sidebar:
		if parent.role == Role.LISTITEM:
			return _getFirstProject(parent)
		parent = parent.parent
	return next((child for child in sidebar.children if child.role == Role.BUTTON and child.name in _RECENTS_LABELS), None)


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
		"kb:NVDA+shift+c": "announceChatTitle",
		"kb:NVDA+alt+v": "toggleVoiceMode",
		"kb:NVDA+`": "toggleConversationMode",
		"kb:NVDA+alt+w": "reportOrSwitchComposerMode",
		"kb:NVDA+alt+a": "reportComposerAttachments",
	}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._chatArchiveRequest = None
		self._titleWatch = None
		self._lastChatTitle = None
		self._scheduleTitleWatch(0)

	def event_appModule_gainFocus(self):
		if self._titleWatch is None:
			self._scheduleTitleWatch(0)

	def event_appModule_loseFocus(self):
		self._chatArchiveRequest = None
		if self._titleWatch is not None:
			self._titleWatch.Stop()
			self._titleWatch = None
		self._lastChatTitle = None

	def terminate(self):
		self.event_appModule_loseFocus()
		super().terminate()

	def _scheduleTitleWatch(self, delay):
		def check():
			if self._titleWatch is pending:
				self._checkChatTitle()

		pending = self._titleWatch = core.callLater(delay, check)

	def _checkChatTitle(self):
		self._titleWatch = None
		window = api.getForegroundObject()
		if window is None or window.processID != self.processID:
			self._chatArchiveRequest = None
			self._lastChatTitle = None
			return
		self._scheduleTitleWatch(500)
		if self._chatArchiveRequest is not None:
			self._continueChatArchive(window)
		title = _chatTitle(window)
		if not title:
			return
		current = window.windowHandle, title
		previous, self._lastChatTitle = self._lastChatTitle, current
		if previous is not None and previous[0] == current[0] and previous[1] != title:
			plugin = _activeToolkitPlugin()
			if plugin is not None:
				plugin._announceChatOpened(title, window.windowHandle)
			else:
				ui.message(title)

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

	@script(description=_("Announce the current chat title"))
	def script_announceChatTitle(self, gesture):
		ui.message(_chatTitle(api.getForegroundObject()) or _("The chat title is unavailable"))

	@script(description=_("Archive the focused sidebar chat and move to the next chat"))
	def script_archiveSidebarChat(self, gesture):
		from globalPlugins.codexStatusAnnouncer import _pressControl

		if self._chatArchiveRequest is not None or getLastScriptRepeatCount():
			return
		foreground = api.getForegroundObject()
		if foreground is None or foreground.processID != self.processID:
			return
		sidebar = _getSidebar(_getMainDocument(foreground))
		if sidebar is None:
			ui.message(_("The sidebar is unavailable"))
			return
		focus = api.getFocusObject()
		interceptor = getattr(focus, "treeInterceptor", None)
		browseMode = isinstance(interceptor, BrowseModeDocumentTreeInterceptor) and not interceptor.passThrough
		try:
			position = interceptor.currentNVDAObject if browseMode else focus
		except (LookupError, NotImplementedError):
			position = None
		target = _findSidebarChat(sidebar, position)
		if target is None and not browseMode:
			target = _findSidebarChat(sidebar, NVDAObject.objectWithFocus() or focus, matchFocusedState=True)
		if target is None:
			ui.message(_("Move to a chat in the sidebar to archive it"))
			return
		chatList, row, index, button = target
		request = _ChatArchiveRequest(foreground.windowHandle, chatList, row, index, _chatListFallback(sidebar, chatList))
		try:
			plugin = _activeToolkitPlugin()
			if plugin is not None and plugin._conversationWindowHandle == foreground.windowHandle:
				plugin._invokeChatAction(button, plugin._conversationMode)
			else:
				_pressControl(button)
		except (LookupError, NotImplementedError):
			ui.message(_("Could not activate Archive chat"))
			return
		self._chatArchiveRequest = request
		if self._titleWatch is None:
			self._scheduleTitleWatch(0)

	def _continueChatArchive(self, window):
		from globalPlugins.codexStatusAnnouncer import _sameNVDAObject

		request = self._chatArchiveRequest
		if request.windowHandle != window.windowHandle:
			self._chatArchiveRequest = None
			return
		try:
			sidebar = _getSidebar(_getMainDocument(window))
			if sidebar is not None:
				chatList = next((obj for obj in _walkObjects(sidebar, 12) if (
					obj.role == Role.LIST and _sameNVDAObject(request.chatList, obj)
				)), None)
				if chatList is not None and not any(_sameNVDAObject(request.row, item) for item in chatList.children):
					self._chatArchiveRequest = None
					chats = [control for row, control, archiveButton in _iterArchivableChats(chatList)]
					target = chats[min(request.index, len(chats) - 1)] if chats else request.fallback
					if target is not None:
						target.setFocus()
					if not chats:
						ui.message(_("Chat archived. No other chats in this list"))
					return
		except (LookupError, NotImplementedError):
			if self._chatArchiveRequest is None:
				ui.message(_("Chat archived. Could not restore focus in the list"))
				return
		request.checksLeft -= 1
		if not request.checksLeft:
			self._chatArchiveRequest = None
			ui.message(_("Could not confirm that the chat was archived"))

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
