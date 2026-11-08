import ast
from collections import deque
import gettext
from pathlib import Path
from types import SimpleNamespace
import unittest


PROJECT_ROOT = Path(__file__).parents[1]
APP_PATH = PROJECT_ROOT / "appModules" / "chatgpt.py"
PLUGIN_PATH = PROJECT_ROOT / "globalPlugins" / "codexStatusAnnouncer" / "__init__.py"


class ScheduledCall:
	def __init__(self, _delay, callback):
		self.callback = callback
		self.stopped = False

	def Stop(self):
		self.stopped = True


class ChatTitleTests(unittest.TestCase):
	def setUp(self):
		self.document = SimpleNamespace(role="document", name="First chat", children=[])
		self.window = SimpleNamespace(
			role="window", windowHandle=11, processID=7, children=[self.document],
		)
		self.messages = []

	def _startWatcher(self, language):
		translate = gettext.translation(
			"nvda", PROJECT_ROOT / "locale", languages=[language], fallback=language == "en",
		).gettext
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(node for node in pluginTree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin")
		announce = next(node for node in pluginClass.body if isinstance(node, ast.FunctionDef) and node.name == "_announceChatOpened")
		pluginNamespace = {"_": translate, "time": SimpleNamespace(monotonic=lambda: 10.0)}
		exec(compile(ast.Module(body=[announce], type_ignores=[]), str(PLUGIN_PATH), "exec"), pluginNamespace)

		messages = self.messages

		class Announcer:
			_lastChatOpened = None
			_announceChatOpened = pluginNamespace["_announceChatOpened"]

			def _speakOnce(self, message, *args, brailleMessage):
				messages.append((message, brailleMessage))

		plugin = Announcer()
		appTree = ast.parse(APP_PATH.read_text(encoding="utf-8"))
		nodes = [
			node for node in appTree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))
			and node.name != "_activeToolkitPlugin"
			and (not isinstance(node, ast.ClassDef) or node.name == "AppModule")
		]
		appNamespace = {
			"_": translate,
			"deque": deque,
			"Role": SimpleNamespace(DOCUMENT="document"),
			"api": SimpleNamespace(getForegroundObject=lambda: self.window),
			"appModuleHandler": SimpleNamespace(AppModule=SimpleNamespace),
			"core": SimpleNamespace(callLater=ScheduledCall),
			"ui": SimpleNamespace(message=messages.append),
			"script": lambda **kwargs: lambda function: function,
			"_activeToolkitPlugin": lambda: plugin,
		}
		exec(compile(ast.Module(body=nodes, type_ignores=[]), str(APP_PATH), "exec"), appNamespace)
		watcher = appNamespace["AppModule"](processID=self.window.processID)
		watcher._titleWatch.callback()
		self.assertEqual([], self.messages)
		return watcher, plugin

	def test_one_localized_announcement_when_history_and_watcher_report_the_same_chat(self):
		for language, expected in (
			("en", "Chat opened: Second chat"),
			("fr_CA", "Chat ouvert : Second chat"),
		):
			for historyFirst in (True, False):
				with self.subTest(language=language, historyFirst=historyFirst):
					self.messages.clear()
					watcher, plugin = self._startWatcher(language)
					self.window.children = [
						SimpleNamespace(role="document", name="Second chat", children=[]),
					]
					if historyFirst:
						plugin._announceChatOpened("Second chat", self.window.windowHandle)
					watcher._titleWatch.callback()
					if not historyFirst:
						plugin._announceChatOpened("Second chat", self.window.windowHandle)
					watcher._titleWatch.callback()
					self.assertEqual([(expected, expected)], self.messages)
					self.window.children = [self.document]

	@unittest.expectedFailure
	def test_renaming_the_current_chat_does_not_announce_an_opening(self):
		watcher, _plugin = self._startWatcher("en")
		self.document.name = "Renamed chat"
		watcher._titleWatch.callback()
		self.assertEqual([], self.messages)
