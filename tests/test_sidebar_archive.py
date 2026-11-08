import ast
from enum import Enum
from pathlib import Path
import runpy
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).parents[1]
PLUGIN_PATH = ROOT / "globalPlugins" / "codexStatusAnnouncer" / "__init__.py"
Role = Enum("Role", "DOCUMENT LANDMARK LIST LISTITEM LINK BUTTON EDITABLETEXT")
State = Enum("State", "FOCUSED INVISIBLE")


class Node:
	windowHandle = 10

	def __init__(self, role, name="", *children):
		self.role, self.name = role, name
		self.children = list(children)
		self.states = set()
		self.parent = None
		self.focused = False
		for child in children:
			child.parent = self

	def setFocus(self):
		self.focused = True


class BrowseMode(SimpleNamespace):
	pass


class SidebarArchiveTests(unittest.TestCase):
	def setUp(self):
		self.messages = []
		self.first = Node(Role.LINK, "Same title", Node(Role.BUTTON, "Archive chat"))
		self.second = Node(Role.LINK, "Same title", Node(Role.BUTTON, "Archiver le chat"))
		self.rows = Node(Role.LIST, "", Node(Role.LISTITEM, "", self.first), Node(Role.LISTITEM, "", self.second))
		self.header = Node(Role.BUTTON, "Récents")
		sidebar = Node(Role.LANDMARK, "Accueil", self.header, self.rows)
		self.editor = Node(Role.EDITABLETEXT, "Prompt")
		document = Node(Role.DOCUMENT, "Test chat", sidebar, self.editor)
		self.window = Node(Role.LANDMARK, "", document)
		self.window.processID = 3
		self.focus = self.first
		self.archived = []

		for chat in (self.first, self.second):
			chat.children[0].doAction = lambda chat=chat: self.archived.append(chat)

		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		compare = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_sameNVDAObject")
		comparison = {}
		exec(compile(ast.Module(body=[compare], type_ignores=[]), str(PLUGIN_PATH), "exec"), comparison)
		prefix = "globalPlugins.codexStatusAnnouncer"
		plugin = SimpleNamespace(_activePluginInstance=None, _pressControl=lambda obj: obj.doAction(),
			_sameNVDAObject=comparison["_sameNVDAObject"])
		nvdaObject = type("NVDAObject", (), {"objectWithFocus": staticmethod(lambda: self.focus)})
		stubs = {
			"addonHandler": SimpleNamespace(initTranslation=lambda: None),
			"api": SimpleNamespace(getForegroundObject=lambda: self.window, getFocusObject=lambda: self.focus),
			"appModuleHandler": SimpleNamespace(AppModule=SimpleNamespace),
			"browseMode": SimpleNamespace(BrowseModeDocumentTreeInterceptor=BrowseMode),
			"controlTypes": SimpleNamespace(Role=Role, State=State),
			"core": SimpleNamespace(callLater=lambda delay, fn: SimpleNamespace(run=fn, Stop=lambda: None)),
			"logHandler": SimpleNamespace(log=None),
			"NVDAObjects": SimpleNamespace(NVDAObject=nvdaObject),
			"scriptHandler": SimpleNamespace(getLastScriptRepeatCount=lambda: 0, script=lambda **kwargs: lambda fn: fn),
			"ui": SimpleNamespace(message=self.messages.append),
			"globalPlugins": SimpleNamespace(codexStatusAnnouncer=plugin),
			prefix: plugin,
			prefix + ".core": SimpleNamespace(**runpy.run_path(str(PLUGIN_PATH.with_name("core.py")))),
		}
		self.enterContext(patch.dict(sys.modules, stubs))
		app = runpy.run_path(str(ROOT / "appModules" / "chatgpt.py"), init_globals={"_": lambda text: text})
		self.app = app["AppModule"](processID=3)
		self.app._titleWatch.run()

	def test_focus_mode_waits_for_removal_then_focuses_next_chat(self):
		self.app.script_archiveSidebarChat(None)
		self.app.script_archiveSidebarChat(None)
		self.app._titleWatch.run()
		self.assertEqual([self.first], self.archived)
		self.assertFalse(self.second.focused)
		self.rows.children.pop(0)
		self.app._titleWatch.run()
		self.assertTrue(self.second.focused)
		self.assertIsNone(self.app._chatArchiveRequest)

	def test_browse_mode_uses_cursor_and_falls_back_to_previous_chat(self):
		self.first.treeInterceptor = BrowseMode(passThrough=False, currentNVDAObject=self.second)
		self.app.script_archiveSidebarChat(None)
		self.assertEqual([self.second], self.archived)
		self.rows.children.pop()
		self.app._titleWatch.run()
		self.assertTrue(self.first.focused)

	def test_focus_moves_to_recents_heading_when_list_becomes_empty(self):
		self.rows.children.pop()
		self.app.script_archiveSidebarChat(None)
		self.rows.children.clear()
		self.app._titleWatch.run()
		self.assertTrue(self.header.focused)
		self.assertEqual(["Chat archived. No other chats in this list"], self.messages)

	def test_command_does_not_archive_from_editor(self):
		self.focus = self.editor
		self.app.script_archiveSidebarChat(None)
		self.assertEqual([], self.archived)
		self.assertEqual(["Move to a chat in the sidebar to archive it"], self.messages)
