import ast
from collections import deque
from dataclasses import dataclass
from enum import Enum
import gettext
from pathlib import Path
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).parents[1]
APP_PATH = ROOT / "appModules" / "chatgpt.py"
Role = Enum("Role", "BUTTON DOCUMENT GROUPING LANDMARK LINK LIST LISTITEM TOGGLEBUTTON")
State = Enum("State", "CHECKED COLLAPSED EXPANDED HASPOPUP INVISIBLE PRESSED")


class SidebarNavigationTests(unittest.TestCase):
	def setUp(self):
		self.window = self.node(Role.GROUPING)
		self.window.processID = 3
		self.focused = None
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
			"api": SimpleNamespace(getForegroundObject=lambda: self.window),
			"appModuleHandler": SimpleNamespace(AppModule=SimpleNamespace),
			"core": SimpleNamespace(callLater=lambda delay, fn, *args: SimpleNamespace(
				run=lambda: fn(*args), Stop=lambda: None,
			)),
			"KeyboardInputGesture": SimpleNamespace(fromName=lambda key: SimpleNamespace(send=lambda: self.send(key))),
			"NVDAObject": SimpleNamespace(objectWithFocus=lambda: self.focused),
			"script": lambda **kwargs: lambda fn: fn,
			"ui": SimpleNamespace(message=self.messages.append),
			"winUser": SimpleNamespace(
				VK_SHIFT=1, VK_CONTROL=2, VK_MENU=3,
				getAsyncKeyState=lambda key: 0x8000 if key == 1 and self.modifiersHeld else 0,
				isDescendantWindow=lambda parent, child: False,
			),
		}
		exec(compile(ast.Module(body=body, type_ignores=[]), str(APP_PATH), "exec"), namespace)
		return namespace["AppModule"](processID=self.window.processID)

	def send(self, key):
		self.keys.append(key)
		self.onKey(key)

	def test_project_command_waits_for_sidebar_and_expands_projects(self):
		app = self.loadApp("en")
		toggle = self.node(Role.BUTTON, "Show sidebar")
		header = self.node(Role.BUTTON, "Projects", states=[State.COLLAPSED])
		project = self.node(Role.LINK, "Workspace", children=[self.node(Role.BUTTON, "Project actions for Workspace")])
		sidebar = self.node(Role.LANDMARK, "Home", children=[header])
		document = self.node(Role.DOCUMENT, children=[toggle])
		self.window.children = [document]

		def onKey(key):
			if key == "control+shift+s":
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
		for _ in range(4):
			app._sidebarFocusTimer.run()
		self.assertEqual(["control+shift+s", "enter"], self.keys)
		self.assertIs(self.focused, project)
		self.assertIsNone(app._sidebarFocusRequest)
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
