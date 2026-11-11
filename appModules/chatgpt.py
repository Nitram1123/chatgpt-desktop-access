"""Application-scoped commands for the ChatGPT desktop app."""

from collections import deque
from dataclasses import dataclass

import addonHandler
import api
import appModuleHandler
import core
import ui
import winUser
from browseMode import BrowseModeDocumentTreeInterceptor
from controlTypes import Role, State
from keyboardHandler import KeyboardInputGesture
from logHandler import log
from NVDAObjects import NVDAObject
from scriptHandler import getLastScriptRepeatCount, script


addonHandler.initTranslation()

_SIDEBAR_LABELS = {
	"Hide sidebar": True, "Masquer la barre latérale": True,
	"Show sidebar": False, "Afficher la barre latérale": False,
}
_SIDEBAR_LANDMARKS = {"Accueil", "Home"}
_ACTIVITY_OPEN_LABELS = {
	"View activity", "View activity, needs attention",
	"Afficher l’activité", "Afficher l’activité, attention requise",
}
_ACTIVITY_CLOSE_LABELS = {
	"Turn off activity view", "Fermer la vue d’activité", "Désactiver la vue Activité",
}
_PROJECTS_LABELS = {"Projets", "Projects"}
_PROJECT_ACTION_PREFIXES = ("Actions du projet ", "Project actions for ")
_RECENTS_LABELS = {"Récents", "Recents"}
_RECENTS_OPTIONS_LABELS = {"Options de la barre latérale de Chat", "Chat sidebar options"}
_SIDEBAR_CHECKS = 30


@dataclass
class _SidebarFocusRequest:
	windowHandle: int
	section: str
	checksLeft: int = _SIDEBAR_CHECKS
	activityFocused: bool = False
	activityCloseRequested: bool = False
	sidebarOpened: bool = False
	headerFocused: bool = False
	headerActivated: bool = False


@dataclass
class _ChatArchiveRequest:
	windowHandle: int
	chatList: NVDAObject
	row: NVDAObject
	index: int
	# Quoted so Python 3.7 in NVDA 2023 does not evaluate the union at import.
	fallback: "NVDAObject | None"
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


def _getSidebarState(document):
	for obj in _walkObjects(document, 5):
		if obj.role == Role.BUTTON and obj.name in _SIDEBAR_LABELS:
			return _SIDEBAR_LABELS[obj.name]
	return None


def _isActiveActivityButton(obj):
	if obj.role not in (Role.BUTTON, Role.TOGGLEBUTTON):
		return False
	name = (obj.name or "").replace("'", "’")
	if name not in _ACTIVITY_OPEN_LABELS and name not in _ACTIVITY_CLOSE_LABELS:
		return False
	states = obj.states
	return State.INVISIBLE not in states and (
		name in _ACTIVITY_CLOSE_LABELS or State.PRESSED in states or State.CHECKED in states
	)


def _getActiveActivityButton(root):
	return next((obj for obj in _walkObjects(root, 6) if _isActiveActivityButton(obj)), None)


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


def _projectTarget(sidebar):
	for obj in sidebar.children:
		if obj.role == Role.BUTTON and obj.name in _PROJECTS_LABELS and State.COLLAPSED in obj.states:
			return None, obj
	return _getFirstProject(sidebar), None


def _iterChatRows(items):
	for item in items:
		if item.role != Role.LISTITEM:
			continue
		for control in _walkObjects(item, 3):
			if control.role in (Role.BUTTON, Role.LINK) and control.name:
				yield item, control
				break


def _recentChatTarget(sidebar):
	siblings = iter(sidebar.children)
	header = next((obj for obj in siblings if obj.role == Role.BUTTON and obj.name in _RECENTS_LABELS), None)
	if header is None:
		return None, None
	if State.COLLAPSED in header.states:
		return None, header

	# The list follows the header and its options button in the accessibility tree.
	for content in siblings:
		if content.role in (Role.GROUPING, Role.LIST):
			break
		if content.role == Role.BUTTON and content.name not in _RECENTS_OPTIONS_LABELS:
			states = content.states
			if State.HASPOPUP not in states and {State.COLLAPSED, State.EXPANDED} & states:
				return None, None
	else:
		return None, None
	chatList = next((obj for obj in _walkObjects(content, 2) if obj.role == Role.LIST), None)
	if chatList is not None:
		for _, control in _iterChatRows(chatList.children):
			if not any((child.name or "").startswith(_PROJECT_ACTION_PREFIXES) for child in control.children):
				return control, None
	return None, None


def _modifiersReleased():
	return not any(
		winUser.getAsyncKeyState(key) & 0x8000
		for key in (winUser.VK_SHIFT, winUser.VK_CONTROL, winUser.VK_MENU)
	)


def _activateFocusedSidebarControl(control, windowHandle, *, activity=False):
	if not _modifiersReleased():
		return False
	# Read the keyboard focus directly. The cached NVDA event can lag behind Chromium.
	focused = NVDAObject.objectWithFocus()
	focusWindow = getattr(focused, "windowHandle", 0)
	if focused is None or not (
		focusWindow == windowHandle or winUser.isDescendantWindow(windowHandle, focusWindow)
	):
		return False
	# The activity toggle can expose a different role or label in the focus object.
	matches = _isActiveActivityButton(focused) if activity else (
		focused.role == control.role and focused.name == control.name and State.EXPANDED not in focused.states
	)
	if not matches:
		return False
	KeyboardInputGesture.fromName("enter").send()
	return True


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
		self._sidebarFocusRequest = None
		self._sidebarFocusTimer = None
		self._chatArchiveRequest = None
		self._titleWatch = None
		self._lastChatTitle = None
		self._scheduleTitleWatch(0)

	def event_appModule_gainFocus(self):
		if self._titleWatch is None:
			self._scheduleTitleWatch(0)

	def event_appModule_loseFocus(self):
		self._cancelSidebarFocus()
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
				self._titleWatch = None
				self._checkChatTitle()

		pending = self._titleWatch = core.callLater(delay, check)

	def _checkChatTitle(self, checkArchive=True):
		window = api.getForegroundObject()
		if window is None or window.processID != self.processID:
			self._chatArchiveRequest = None
			self._lastChatTitle = None
			return
		if self._titleWatch is None:
			self._scheduleTitleWatch(500)
		if checkArchive and self._chatArchiveRequest is not None:
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

	def _cancelSidebarFocus(self):
		self._sidebarFocusRequest = None
		if self._sidebarFocusTimer is not None:
			self._sidebarFocusTimer.Stop()
			self._sidebarFocusTimer = None

	def _focusSidebarSection(self, section):
		foreground = api.getForegroundObject()
		if foreground is None or foreground.processID != self.processID:
			return
		if self._sidebarFocusRequest is not None:
			request = self._sidebarFocusRequest
			if request.section == section and request.windowHandle == foreground.windowHandle:
				return
		self._cancelSidebarFocus()
		request = self._sidebarFocusRequest = _SidebarFocusRequest(foreground.windowHandle, section)
		self._continueSidebarFocus(request)

	def _continueSidebarFocus(self, request):
		if request is not self._sidebarFocusRequest:
			return
		self._sidebarFocusTimer = None
		foreground = api.getForegroundObject()
		if foreground is None or foreground.windowHandle != request.windowHandle or foreground.processID != self.processID:
			self._cancelSidebarFocus()
			return

		header = None
		try:
			document = _getMainDocument(foreground)
			sidebar = _getSidebar(document)
			activityButton = _getActiveActivityButton(document)
			if activityButton is not None:
				if not request.activityFocused:
					activityButton.setFocus()
					request.activityFocused = True
					request.checksLeft = _SIDEBAR_CHECKS
				elif not request.activityCloseRequested and _activateFocusedSidebarControl(
					activityButton, request.windowHandle, activity=True,
				):
					request.activityCloseRequested = True
					request.checksLeft = _SIDEBAR_CHECKS
			elif sidebar is None:
				if not request.sidebarOpened and _getSidebarState(document) is False and _modifiersReleased():
					request.sidebarOpened = True
					KeyboardInputGesture.fromName("control+shift+s").send()
			else:
				target, header = self._sidebarTarget(sidebar, request.section)
				if target is not None:
					self._cancelSidebarFocus()
					target.setFocus()
					return
				if header is not None and not request.headerFocused:
					header.setFocus()
					request.headerFocused = True
					request.checksLeft = _SIDEBAR_CHECKS
				elif header is not None and not request.headerActivated and _activateFocusedSidebarControl(
					header, request.windowHandle,
				):
					request.headerActivated = True
					request.checksLeft = _SIDEBAR_CHECKS
		except (LookupError, NotImplementedError):
			self._cancelSidebarFocus()
			ui.message(_("Could not move focus in the sidebar"))
			return

		request.checksLeft -= 1
		if request.checksLeft > 0:
			self._sidebarFocusTimer = core.callLater(150, self._continueSidebarFocus, request)
			return
		self._cancelSidebarFocus()
		if activityButton is not None:
			ui.message(_("Could not move focus in the sidebar"))
		elif sidebar is None:
			ui.message(_("The sidebar is unavailable"))
		elif header is not None:
			ui.message(_("Could not expand {section}").format(section=header.name))
		else:
			ui.message(self._emptySidebarSectionMessage(request.section))

	def _sidebarTarget(self, sidebar, section):
		return _projectTarget(sidebar) if section == "projects" else _recentChatTarget(sidebar)

	def _emptySidebarSectionMessage(self, section):
		if section == "projects":
			return _("No projects found in the sidebar")
		return _("No chats found in Recents")

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

	@script(description=_("Move to the first project in the sidebar"))
	def script_focusFirstProject(self, gesture):
		self._focusSidebarSection("projects")

	@script(description=_("Move to the first chat in Recents"))
	def script_focusFirstRecentChat(self, gesture):
		self._focusSidebarSection("recents")

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
