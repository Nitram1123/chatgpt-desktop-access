import ast
from collections import deque
from dataclasses import dataclass
from enum import Enum
import gettext
from itertools import product
from pathlib import Path
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).parents[1]
APP_PATH = ROOT / "appModules" / "chatgpt.py"
Role = Enum("Role", "MENUBUTTON BUTTON DOCUMENT GROUPING LANDMARK LINK LIST LISTITEM TOGGLEBUTTON")
State = Enum("State", "CHECKED COLLAPSED EXPANDED HASPOPUP INVISIBLE PRESSED")

class COMError(Exception):
	pass


class SidebarNavigationTests(unittest.TestCase):
	def setUp(self):
		self.window = self.node(Role.GROUPING)
		self.window.processID = 3
		self.focused = None
		self.focusAncestors = []
		self.messages = []
		self.keys = []
		self.onKey = lambda key: None
		self.modifiersHeld = False

	def node(self, role, name="", *, children=(), states=()):
		obj = SimpleNamespace(role=role, name=name, children=list(children), states=set(states), windowHandle=10)
		obj.setFocus = lambda: setattr(self, "focused", obj)
		return obj

	def loadApp(self, language):
		tree = ast.parse(APP_PATH.read_text(encoding="utf-8"))
		body = [
			node for node in tree.body
			if isinstance(node, (ast.Assign, ast.ClassDef, ast.FunctionDef))
		]
		namespace = {
			"__name__": __name__,
			"_": gettext.translation("nvda", ROOT / "locale", languages=[language], fallback=True).gettext,
			"dataclass": dataclass,
			"deque": deque,
			"Role": Role,
			"State": State,
			"COMError": COMError,
			"api": SimpleNamespace(
				getForegroundObject=lambda: self.window, getFocusObject=lambda: self.focused,
				getFocusAncestors=lambda: self.focusAncestors,
			),
			"appModuleHandler": SimpleNamespace(AppModule=SimpleNamespace),
			"core": SimpleNamespace(callLater=lambda delay, fn, *args: SimpleNamespace(
				run=lambda: fn(*args), Stop=lambda: None,
			)),
			"KeyboardInputGesture": SimpleNamespace(fromName=lambda key: SimpleNamespace(send=lambda: self.send(key))),
			"NVDAObject": SimpleNamespace(objectWithFocus=lambda: self.focused),
			"script": lambda **kwargs: lambda fn: fn,
			"ui": SimpleNamespace(message=self.messages.append),
			"log": SimpleNamespace(info=lambda *args: None),
			"winUser": SimpleNamespace(
				VK_SHIFT=1, VK_CONTROL=2, VK_MENU=3,
				getForegroundWindow=lambda: self.window.windowHandle,
				getAsyncKeyState=lambda key: 0x8000 if key == 1 and self.modifiersHeld else 0,
				isDescendantWindow=lambda parent, child: False,
			),
		}
		exec(compile(ast.Module(body=body, type_ignores=[]), str(APP_PATH), "exec"), namespace)
		return namespace["AppModule"](processID=self.window.processID)

	def send(self, key):
		self.keys.append(key)
		self.onKey(key)

	def test_navigation_finds_sidebar_inside_unpruned_ia2_layouts(self):
		for language, home, projects, recents in (
			("en", "Home", "Projects", "Recents"),
			("fr_CA", "Accueil", "Projets", "Récents"),
		):
			for section in ("projects", "recents"):
				with self.subTest(language=language, section=section):
					app = self.loadApp(language)
					project = self.node(Role.LINK, "Workspace", children=[
						self.node(Role.BUTTON, "Project actions for Workspace"),
					])
					chat = self.node(Role.LINK, "Conversation")
					rows = self.node(Role.LIST, children=[self.node(Role.LISTITEM, children=[chat])])
					sidebar = self.node(Role.LANDMARK, home, children=[
						self.node(Role.BUTTON, projects, states=[State.EXPANDED]), project,
						self.node(Role.BUTTON, recents, states=[State.EXPANDED]), rows,
					])
					nestedSidebar = sidebar
					for _ in range(13):
						nestedSidebar = self.node(Role.GROUPING, children=[nestedSidebar])
					panel = self.node(Role.GROUPING, children=[nestedSidebar])
					panel.IA2Attributes = {"class": "app-shell-left-panel responsive-layout"}
					content = panel
					for _ in range(6):
						content = self.node(Role.GROUPING, children=[content])
					self.window.children = [self.node(Role.DOCUMENT, children=[content])]
					app._prepareSidebarSection(section)
					self.assertIs(self.focused, project if section == "projects" else chat)
					self.assertIsNone(app._sidebarFocusRequest)
					self.assertEqual([], self.keys)
					self.assertEqual([], self.messages)

	def test_project_command_waits_for_sidebar_and_expands_projects(self):
		app = self.loadApp("en")
		toggle = self.node(Role.BUTTON, "Localized sidebar label", states=[State.COLLAPSED])
		toggle.IA2Attributes = {"class": "group/sidebar-trigger"}
		header = self.node(Role.BUTTON, "Projects", states=[State.COLLAPSED])
		project = self.node(Role.LINK, "Workspace", children=[self.node(Role.BUTTON, "Project actions for Workspace")])
		sidebar = self.node(Role.LANDMARK, "Home", children=[header])
		document = self.node(Role.DOCUMENT, children=[toggle])
		self.window.children = [document]

		def onKey(key):
			self.assertEqual("enter", key)
			if self.focused is toggle:
				document.children.append(sidebar)
			else:
				self.assertIs(self.focused, header)
				header.states = {State.EXPANDED}
				sidebar.children.append(project)

		self.onKey = onKey
		self.modifiersHeld = True
		app.script_focusFirstProject(None)
		self.assertEqual([], self.keys)
		self.modifiersHeld = False
		for _ in range(5):
			app._sidebarFocusTimer.run()
		self.assertEqual(["enter", "enter"], self.keys)
		self.assertIs(self.focused, project)
		self.assertIsNone(app._sidebarFocusRequest)
		self.assertEqual([], self.messages)

	def test_nested_sidebar_configuration_matrix(self):
		labelsByLanguage = {
			"en": ("Home", "Projects", "Recents", "Show sidebar", "Exit full view", "View activity"),
			"fr_CA": ("Accueil", "Projets", "Récents", "Afficher la barre latérale", "Quitter la vue complète", "Afficher l’activité"),
		}
		for language, section, initiallyOpen, initiallyExpanded, view in product(
			labelsByLanguage, ("projects", "recents"), (False, True), (False, True), ("normal", "activity", "full"),
		):
			with self.subTest(language=language, section=section, open=initiallyOpen, expanded=initiallyExpanded, view=view):
				self.focused, self.focusAncestors = None, []
				self.keys.clear()
				self.messages.clear()
				app = self.loadApp(language)
				home, projects, recents, show, full, activityLabel = labelsByLanguage[language]
				def wrap(obj, levels):
					for _ in range(levels):
						obj = self.node(Role.GROUPING, children=[obj])
					return obj
				header = self.node(Role.BUTTON, projects if section == "projects" else recents,
					states=[State.EXPANDED if initiallyExpanded else State.COLLAPSED])
				target = self.node(Role.LINK, "Target")
				if section == "projects":
					target.children = [self.node(Role.BUTTON, "Project actions for Target")]
				items = wrap(self.node(Role.LIST, children=[self.node(Role.LISTITEM, children=[target])]), 3)
				content = self.node(Role.GROUPING, children=[wrap(header, 3)])
				if initiallyExpanded:
					content.children.append(items)
				activity = self.node(Role.TOGGLEBUTTON, activityLabel,
					states=[State.PRESSED] if view == "activity" else [])
				sidebar = self.node(Role.LANDMARK, home, children=[activity, content])
				panel = self.node(Role.GROUPING, children=[wrap(sidebar, 13)])
				panel.IA2Attributes = {"class": "app-shell-left-panel"}
				toggle = self.node(Role.BUTTON, show, states=[State.COLLAPSED])
				toggle.IA2Attributes = {"class": "group/sidebar-trigger"}
				document = self.node(Role.DOCUMENT, children=[toggle])
				if initiallyOpen and view != "full":
					document.children.append(panel)
					toggle.states = {State.EXPANDED}
				if view == "full":
					fullButton = self.node(Role.TOGGLEBUTTON, full, states=[State.PRESSED])
					document.children.append(fullButton)
					fullButton.doAction = lambda: document.children.remove(fullButton)
				self.window.children = [document]
				def onKey(key):
					self.assertEqual("enter", key)
					if self.focused is toggle:
						toggle.states = {State.EXPANDED}
						document.children.append(panel)
					elif self.focused is activity:
						activity.states.clear()
					else:
						self.assertIs(self.focused, header)
						header.states = {State.EXPANDED}
						content.children.append(items)
				self.onKey = onKey
				app._prepareSidebarSection(section)
				for _ in range(30):
					if app._sidebarFocusRequest is None:
						break
					app._sidebarFocusTimer.run()
				self.assertIs(self.focused, target)
				self.assertIsNone(app._sidebarFocusRequest)
				self.assertEqual([], self.messages)

	def test_project_row_uses_structure_without_a_translated_actions_label(self):
		app = self.loadApp("fr")
		project = self.node(Role.BUTTON, "Workspace", states=[State.COLLAPSED])
		project.IA2Attributes = {"class": "sidebar-item sidebar-row-focus group/folder-row"}
		sidebar = self.node(Role.LANDMARK, "Accueil", children=[
			self.node(Role.BUTTON, "Projets", states=[State.EXPANDED]),
			self.node(Role.LIST, children=[self.node(Role.LISTITEM, children=[project])]),
		])
		self.window.children = [self.node(Role.DOCUMENT, children=[sidebar])]
		app.script_focusFirstProject(None)
		self.assertIs(self.focused, project)
		self.assertEqual([], self.keys)
		self.assertEqual([], self.messages)

	def test_project_actions_can_be_a_nested_menu_button(self):
		app = self.loadApp("en")
		project = self.node(Role.BUTTON, "Workspace", children=[self.node(Role.GROUPING, children=[
			self.node(Role.MENUBUTTON, "Project actions for Workspace"),
		])])
		sidebar = self.node(Role.LANDMARK, "Home", children=[
			self.node(Role.BUTTON, "Projects", states=[State.EXPANDED]), project,
		])
		self.window.children = [self.node(Role.DOCUMENT, children=[sidebar])]
		app.script_focusFirstProject(None)
		self.assertIs(self.focused, project)
		self.assertEqual([], self.messages)

	def test_recents_lookup_skips_project_conversation_lists(self):
		app = self.loadApp("fr")
		class UnreadableList:
			role = Role.LIST
			name = ""
			@property
			def children(self):
				raise AssertionError("Project chat lists must not be scanned to find Recents")
		chat = self.node(Role.BUTTON, "Conversation")
		sidebar = self.node(Role.LANDMARK, "Accueil", children=[
			self.node(Role.BUTTON, "Projets", states=[State.EXPANDED]), UnreadableList(),
			self.node(Role.BUTTON, "Récents", states=[State.EXPANDED]),
			self.node(Role.LIST, children=[self.node(Role.LISTITEM, children=[chat])]),
		])
		self.window.children = [self.node(Role.DOCUMENT, children=[sidebar])]
		app.script_focusFirstRecentChat(None)
		self.assertIs(self.focused, chat)
		self.assertEqual([], self.messages)

	def test_recent_chat_command_closes_activity_and_expands_french_section(self):
		app = self.loadApp("fr_CA")
		activity = self.node(Role.TOGGLEBUTTON, "Afficher l’activité, attention requise", states=[State.PRESSED])
		header = self.node(Role.BUTTON, "Récents", states=[State.COLLAPSED])
		options = self.node(Role.BUTTON, "Options de la barre latérale de Chat")
		chat = self.node(Role.LINK, "Conversation")
		rows = self.node(Role.LIST, children=[self.node(Role.LISTITEM, children=[chat])])
		sidebar = self.node(Role.LANDMARK, "Accueil", children=[header, options])
		document = self.node(Role.DOCUMENT, children=[activity, sidebar])
		self.window.children = [document]

		def onKey(key):
			if self.focused is activity:
				activity.states.clear()
			else:
				self.assertIs(self.focused, header)
				header.states = {State.EXPANDED}
				sidebar.children.append(rows)

		self.onKey = onKey
		app.script_focusFirstRecentChat(None)
		self.assertIs(self.focused, activity)
		for _ in range(4):
			app._sidebarFocusTimer.run()
		self.assertEqual(["enter", "enter"], self.keys)
		self.assertIs(self.focused, chat)
		self.assertIsNone(app._sidebarFocusRequest)
		self.assertEqual([], self.messages)

	def test_pending_navigation_stops_when_foreground_changes(self):
		app = self.loadApp("en")
		toggle = self.node(Role.BUTTON, "Show sidebar")
		self.window.children = [self.node(Role.DOCUMENT, children=[toggle])]
		self.modifiersHeld = True
		app.script_focusFirstProject(None)
		self.window.windowHandle = 11
		self.modifiersHeld = False
		app._sidebarFocusTimer.run()
		self.assertEqual([], self.keys)
		self.assertIsNone(app._sidebarFocusRequest)

	def test_delayed_sidebar_render_does_not_trigger_a_second_toggle(self):
		app = self.loadApp("fr")
		toggle = self.node(Role.BUTTON, "Afficher la barre latérale", states=[State.COLLAPSED])
		document = self.node(Role.DOCUMENT, children=[toggle])
		self.window.children = [document]
		app.script_focusFirstRecentChat(None)
		app._sidebarFocusTimer.run()
		for _ in range(20):
			app._sidebarFocusTimer.run()
		self.assertEqual(["enter"], self.keys)
		self.assertEqual([], self.messages)
		chat = self.node(Role.BUTTON, "Conversation")
		document.children.append(self.node(Role.LANDMARK, "Accueil", children=[
			self.node(Role.BUTTON, "Récents", states=[State.EXPANDED]),
			self.node(Role.LIST, children=[self.node(Role.LISTITEM, children=[chat])]),
		]))
		app._sidebarFocusTimer.run()
		self.assertIs(self.focused, chat)
		self.assertIsNone(app._sidebarFocusRequest)
		self.assertEqual(["enter"], self.keys)
		self.assertEqual([], self.messages)


	def test_closed_sidebar_uses_native_shortcut_when_uia_nodes_are_stale(self):
		app = self.loadApp("fr")
		class StaleNode:
			@property
			def role(self):
				raise COMError("UI Automation disconnected")

			@property
			def children(self):
				raise COMError("UI Automation disconnected")

		chat = self.node(Role.LINK, "Conversation")
		rows = self.node(Role.LIST, children=[self.node(Role.LISTITEM, children=[chat])])
		header = self.node(Role.BUTTON, "Récents", states=[State.EXPANDED])
		sidebar = self.node(Role.LANDMARK, "Accueil", children=[header, rows])
		document = self.node(Role.DOCUMENT, children=[StaleNode()])
		self.window.children = [document]
		app.script_focusFirstRecentChat(None)
		self.assertEqual(["control+shift+s"], self.keys)
		app._sidebarFocusTimer.run()
		self.assertEqual(["control+shift+s"], self.keys)
		document.children.append(sidebar)
		app._sidebarFocusTimer.run()
		self.assertIs(self.focused, chat)
		self.assertIsNone(app._sidebarFocusRequest)
		self.assertEqual([], self.messages)

	def test_recents_waits_for_full_view_to_close_before_opening_the_sidebar(self):
		app = self.loadApp("fr")
		document = self.node(Role.DOCUMENT)
		exitButton = self.node(Role.TOGGLEBUTTON, "Quitter la vue complète", states=[State.PRESSED])
		# The workspace toolbar can be a sibling of the conversation document.
		self.window.children = [document, exitButton]
		exits = []
		exitButton.doAction = lambda: exits.append(True)
		app.script_focusFirstRecentChat(None)
		app._sidebarFocusTimer.run()
		self.assertEqual([True], exits)
		self.assertEqual([], self.keys)
		self.window.children.remove(exitButton)
		app._sidebarFocusTimer.run()
		self.assertEqual(["control+shift+s"], self.keys)
		chat = self.node(Role.LINK, "Conversation")
		document.children.append(self.node(Role.LANDMARK, "Accueil", children=[
			self.node(Role.BUTTON, "Récents", states=[State.EXPANDED]),
			self.node(Role.LIST, children=[self.node(Role.LISTITEM, children=[chat])]),
		]))
		app._sidebarFocusTimer.run()
		self.assertIs(self.focused, chat)
		self.assertIsNone(app._sidebarFocusRequest)
		self.assertEqual([], self.messages)

	def test_closed_sidebar_can_open_when_the_foreground_tree_has_no_document(self):
		app = self.loadApp("fr")
		self.focused = self.node(Role.GROUPING)
		chat = self.node(Role.LINK, "Conversation")
		rows = self.node(Role.LIST, children=[self.node(Role.LISTITEM, children=[chat])])
		header = self.node(Role.BUTTON, "Récents", states=[State.EXPANDED])
		sidebar = self.node(Role.LANDMARK, "Accueil", children=[header, rows])

		app.script_focusFirstRecentChat(None)
		self.assertEqual(["control+shift+s"], self.keys)
		self.focusAncestors = [self.window, self.node(Role.DOCUMENT, children=[sidebar])]
		app._sidebarFocusTimer.run()
		self.assertIs(self.focused, chat)
		self.assertIsNone(app._sidebarFocusRequest)
