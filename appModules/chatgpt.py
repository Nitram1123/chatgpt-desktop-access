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
from comtypes import COMError
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
_FULL_VIEW_EXIT_LABELS = {"Exit full view", "Quitter la vue complète"}
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
	fullViewExitRequested: bool = False
	activityFocused: bool = False
	activityCloseRequested: bool = False
	sidebarToggleFocused: bool = False
	sidebarOpenRequested: bool = False
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


def _walkObjects(root, maxDepth, *, skipLists=False):
	if root is None:
		return
	objects = deque([(root, 0)])
	while objects:
		obj, depth = objects.popleft()
		yield obj
		if depth < maxDepth:
			try:
				if skipLists and obj.role == Role.LIST:
					continue
				objects.extend((child, depth + 1) for child in obj.children)
			except COMError:
				# Chromium can replace a subtree while NVDA is walking it.
				continue


def _getMainDocument(window):
	# Focus ancestors may describe another Chromium document in the same window
	# (for example, the mascot or an embedded pane). Alternating between that
	# document and the main one would falsely report a chat switch on every update.
	# Always resolve the outer document from the requested window instead.
	return _findObject(window, 10, lambda obj: obj.role == Role.DOCUMENT)


def _chatTitle(window):
	document = _getMainDocument(window)
	return (document.name or "").strip() if document is not None else ""


def _getSidebar(document):
	def isSidebar(obj):
		return obj.role == Role.LANDMARK and obj.name in _SIDEBAR_LANDMARKS and State.INVISIBLE not in obj.states

	# Keep the fast path for older/pruned accessibility trees.
	sidebar = _findObject(document, 6, isSidebar, skipLists=True)
	if sidebar is not None:
		return sidebar
	# IA2 retains layout containers that UI Automation omits. Search the shell's
	# left panel first, so deeper layouts do not require walking conversations.
	panel = _findObject(document, 8, lambda obj: (
		"app-shell-left-panel" in str((getattr(obj, "IA2Attributes", None) or {}).get("class", "")).split()
		and State.INVISIBLE not in obj.states
	), skipLists=True)
	# Full view can remove the entire panel. Do not scan message transcripts
	# while waiting for the shell to restore it.
	return _findObject(panel, 20, isSidebar, skipLists=True) if panel is not None else None


def _getSidebarState(document):
	toggle = _getSidebarToggle(document)
	return _sidebarToggleState(toggle) if toggle is not None else None


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


def _getActiveActivityButton(root, *, sidebar=False):
	if sidebar:
		for obj in _sidebarObjects(root, skipLists=True):
			if _isActiveActivityButton(obj):
				return obj
			if obj.role == Role.BUTTON and obj.name in _PROJECTS_LABELS | _RECENTS_LABELS:
				break
		return None
	return _findObject(root, 6, _isActiveActivityButton, skipLists=True)


def _getFirstProject(sidebar):
	# Walk in sidebar order even if some project rows are nested more deeply.
	for obj in _sidebarObjects(sidebar):
		if obj.role == Role.BUTTON and obj.name in _RECENTS_LABELS:
			break
		if obj.role not in (Role.BUTTON, Role.LINK):
			continue
		classes = str((getattr(obj, "IA2Attributes", None) or {}).get("class", "")).split()
		if "sidebar-item" in classes and "group/folder-row" in classes:
			return obj
		# Older/pruned trees expose the actions directly; IA2 may retain wrappers
		# and expose a menu button instead of a plain button.
		if any(
			child.role in (Role.BUTTON, Role.MENUBUTTON)
			and (child.name or "").startswith(_PROJECT_ACTION_PREFIXES)
			for child in _walkObjects(obj, 3) if child is not obj
		):
			return obj
	return None


def _projectTarget(sidebar):
	for obj in _sidebarObjects(sidebar, skipLists=True):
		if obj.role != Role.BUTTON:
			continue
		if obj.name in _PROJECTS_LABELS:
			if State.COLLAPSED in obj.states:
				return None, obj
			break
		if obj.name in _RECENTS_LABELS:
			return None, None
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


def _activateFocusedSidebarControl(control, windowHandle, *, activity=False, sidebarToggle=False):
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
	if activity:
		matches = _isActiveActivityButton(focused)
	elif sidebarToggle:
		matches = _sidebarToggleState(focused) is False
	else:
		matches = focused.role == control.role and focused.name == control.name and State.EXPANDED not in focused.states
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
	return next((child for child in _sidebarObjects(sidebar, skipLists=True) if child.role == Role.BUTTON and child.name in _RECENTS_LABELS), None)


def _findObject(root, maxDepth, matches, *, skipLists=False):
	for obj in _walkObjects(root, maxDepth, skipLists=skipLists):
		try:
			if matches(obj):
				return obj
		except COMError:
			continue
	return None

def _getSidebarDocument(window):
	"""Use NVDA's current focus ancestry if the foreground tree omits Chromium."""
	document = _getMainDocument(window)
	if document is not None:
		return document
	focus = api.getFocusObject()
	focusWindow = getattr(focus, "windowHandle", 0)
	if focusWindow != window.windowHandle and not (
		focusWindow and winUser.isDescendantWindow(window.windowHandle, focusWindow)
	):
		return None
	for obj in (*api.getFocusAncestors(), focus):
		try:
			if obj is not None and obj.role == Role.DOCUMENT:
				return obj
		except COMError:
			continue
	return None

def _getSidebarToggle(document):
	return _findObject(document, 5, lambda obj: (
		_sidebarToggleState(obj) is not None and State.INVISIBLE not in obj.states
	))

def _sidebarToggleState(obj):
	if obj.role != Role.BUTTON:
		return None
	attrs = getattr(obj, "IA2Attributes", None) or {}
	if "group/sidebar-trigger" in str(attrs.get("class", "")).split():
		states = obj.states
		if State.EXPANDED in states:
			return True
		if State.COLLAPSED in states:
			return False
	return _SIDEBAR_LABELS.get(obj.name)

def _isFullViewExitButton(obj):
	return (
		obj.role in (Role.BUTTON, Role.TOGGLEBUTTON)
		and obj.name in _FULL_VIEW_EXIT_LABELS
		and State.INVISIBLE not in obj.states
	)

def _getFullViewExitButton(root, foreground):
	button = _findObject(root, 6, _isFullViewExitButton)
	if button is None and root is not foreground:
		button = _findObject(foreground, 12, _isFullViewExitButton)
	return button

def _sidebarObjects(sidebar, *, skipLists=False):
	"""Yield sidebar controls in document order, retaining nested IA2 sections."""
	objects = [sidebar] if sidebar is not None else []
	while objects:
		obj = objects.pop()
		try:
			# Validate a node before yielding it; Chromium may have removed it.
			obj.role
			yield obj
			if not (skipLists and obj.role == Role.LIST):
				objects.extend(reversed(obj.children))
		except COMError:
			continue

def _recentChatList(sidebar, *, requireList=True):
	siblings = _sidebarObjects(sidebar, skipLists=True)
	header = next((obj for obj in siblings if obj.role == Role.BUTTON and obj.name in _RECENTS_LABELS), None)
	if header is None:
		return None, None
	if State.COLLAPSED in header.states:
		return None, header
	if not requireList:
		return None, None

	# Layout wrappers differ between IA2 and UIA. Preserve document order while
	# finding the first list after the section heading, regardless of wrappers.
	for content in siblings:
		if content.role == Role.LIST:
			return content, None
		if content.role == Role.BUTTON and content.name not in _RECENTS_OPTIONS_LABELS:
			states = content.states
			if State.HASPOPUP not in states and {State.COLLAPSED, State.EXPANDED} & states:
				break
	return None, None

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
		self._lastSidebarState = None
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
		self._lastSidebarState = None

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
			self._lastSidebarState = None
			return
		if self._titleWatch is None:
			self._scheduleTitleWatch(500)
		document = _getMainDocument(window)
		if checkArchive:
			self._announceSidebarChange(document, window.windowHandle)
		if checkArchive and self._chatArchiveRequest is not None:
			self._continueChatArchive(window)
		title = (document.name or "").strip() if document is not None else ""
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

	def _announceSidebarChange(self, document, windowHandle):
		expanded = _getSidebarState(document)
		if expanded is None:
			return
		previous, self._lastSidebarState = self._lastSidebarState, (windowHandle, expanded)
		if previous == (windowHandle, not expanded):
			ui.message(_("Sidebar shown") if expanded else _("Sidebar hidden"))

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

	def _prepareSidebarSection(self, section):
		foreground = api.getForegroundObject()
		if foreground is None or foreground.processID != self.processID:
			return
		if self._sidebarFocusRequest is not None:
			request = self._sidebarFocusRequest
			if (
				request.section == section
				and request.windowHandle == foreground.windowHandle
			):
				return
		self._cancelSidebarFocus()
		request = self._sidebarFocusRequest = _SidebarFocusRequest(
			foreground.windowHandle, section,
		)
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
		document = fullViewButton = activityButton = sidebar = None
		try:
			document = _getSidebarDocument(foreground)
			root = document if document is not None else foreground
			sidebar = _getSidebar(root)

			if sidebar is None and not request.sidebarOpenRequested:
				fullViewButton = _getFullViewExitButton(root, foreground)
			if fullViewButton is None:
				if sidebar is not None:
					activityButton = _getActiveActivityButton(sidebar, sidebar=True)
				if activityButton is None:
					activityButton = _getActiveActivityButton(root)
			if fullViewButton is not None:
				self._requestFullViewExit(fullViewButton, request)
			elif activityButton is not None:
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
				self._requestSidebarOpen(root, request)
			else:
				target, header = self._sidebarTarget(sidebar, request)
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
		except COMError:
			# Reacquire the document on the next check if it changed mid-request.
			pass
		except (LookupError, NotImplementedError):
			self._failSidebarFocus(request, _("Could not move focus in the sidebar"))
			return

		request.checksLeft -= 1
		if request.checksLeft > 0:
			self._sidebarFocusTimer = core.callLater(150, self._continueSidebarFocus, request)
			return
		if fullViewButton is not None or activityButton is not None:
			message = _("Could not move focus in the sidebar")
		elif sidebar is None:
			log.info(
				"ChatGPT Desktop Access sidebar unavailable (document found=%s, toggle focused=%s, open requested=%s)",
				document is not None, request.sidebarToggleFocused, request.sidebarOpenRequested,
			)
			message = _("The sidebar is unavailable")
		elif header is not None:
			message = _("Could not expand {section}").format(section=header.name)
		else:
			message = self._emptySidebarSectionMessage(request.section)
		self._failSidebarFocus(request, message)

	def _requestFullViewExit(self, button, request):
		"""Leave full view before sending any command to open the sidebar."""
		if request.fullViewExitRequested or not _modifiersReleased():
			return
		if winUser.getForegroundWindow() != request.windowHandle:
			return
		try:
			button.doAction()
		except NotImplementedError:
			KeyboardInputGesture.fromName("control+shift+f").send()
		request.fullViewExitRequested = True
		request.checksLeft = _SIDEBAR_CHECKS

	def _requestSidebarOpen(self, root, request):
		"""Activate the native show button once, after it receives keyboard focus."""
		if request.sidebarOpenRequested or not _modifiersReleased():
			return
		toggle = _getSidebarToggle(root)
		if toggle is not None:
			try:
				if _sidebarToggleState(toggle) is not False:
					return
				if not request.sidebarToggleFocused:
					toggle.setFocus()
					request.sidebarToggleFocused = True
					request.checksLeft = _SIDEBAR_CHECKS
					return
				if _activateFocusedSidebarControl(toggle, request.windowHandle, sidebarToggle=True):
					request.sidebarOpenRequested = True
					request.checksLeft = _SIDEBAR_CHECKS
					return
				if request.checksLeft > _SIDEBAR_CHECKS - 5:
					return
			except (COMError, LookupError, NotImplementedError):
				pass
		# Use the app's primary native sidebar shortcut when the button is unavailable.
		if winUser.getForegroundWindow() != request.windowHandle:
			return
		KeyboardInputGesture.fromName("control+shift+s").send()
		request.sidebarOpenRequested = True
		request.checksLeft = _SIDEBAR_CHECKS
		log.info("ChatGPT Desktop Access requested sidebar opening with Ctrl+Shift+S")

	def _failSidebarFocus(self, request, message):
		self._cancelSidebarFocus()
		ui.message(message)

	def _sidebarTarget(self, sidebar, request):
		if request.section == "projects":
			return _projectTarget(sidebar)
		chatList, header = _recentChatList(sidebar)
		if chatList is None:
			return chatList, header
		for _, control in _iterChatRows(chatList.children):
			if not any((child.name or "").startswith(_PROJECT_ACTION_PREFIXES) for child in control.children):
				return control, None
		return None, None

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
		self._prepareSidebarSection("projects")

	@script(description=_("Move to the first chat in Recents"))
	def script_focusFirstRecentChat(self, gesture):
		self._prepareSidebarSection("recents")

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
