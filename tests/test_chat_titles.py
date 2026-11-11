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
	def __init__(self, delay, callback, *args):
		self.delay = delay
		self.callback = lambda: callback(*args)
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
		self.now = 10.0
		self.cancellations = []
		self.foreground = self.window
		self.focus = SimpleNamespace(treeInterceptor=SimpleNamespace(isReady=True))

	def _startWatcher(self, language):
		translate = gettext.translation(
			"nvda", PROJECT_ROOT / "locale", languages=[language], fallback=language == "en",
		).gettext
		pluginTree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		pluginClass = next(node for node in pluginTree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin")
		methods = [
			node for node in pluginClass.body if isinstance(node, ast.FunctionDef) and node.name in (
				"_announceChatOpened", "_speakChatTitle", "_chatTitleSpeechEnabled",
				"_filterChatTitleSpeech", "_checkChatTitleBeforeFocus", "event_focusEntered",
				"_observeInputGesture", "_observePromptGestureIdentifiers", "event_alert",
			)
		]
		self.settings = {"outputOther": "speech", "speech": True, "braille": True, "soundWhenSpeechUnavailable": False}
		self.api = SimpleNamespace(getForegroundObject=lambda: self.foreground, getFocusObject=lambda: self.focus)
		pluginNamespace = {
			"_": translate, "time": SimpleNamespace(monotonic=lambda: self.now),
			"api": self.api, "wx": SimpleNamespace(CallLater=ScheduledCall),
			"CHAT_TITLE_FOCUS_DELAY_MS": 100,
			"CHAT_TITLE_SWITCH_QUIET_SECONDS": 1.5, "CHAT_TITLE_FOCUS_QUIET_SECONDS": 0.8,
			"speech": SimpleNamespace(cancelSpeech=lambda: self.cancellations.append(self.now)),
			"_settings": lambda: self.settings, "_speechIsOff": lambda: False,
			"categoryOutputActions": lambda mode, speech, braille, sounds: {"speech": speech and mode == "speech"},
			"_isChatGPTObject": lambda obj: getattr(obj, "processID", None) == self.window.processID,
			"log": SimpleNamespace(debugWarning=lambda *args, **kwargs: None),
		}
		exec(compile(ast.Module(body=methods, type_ignores=[]), str(PLUGIN_PATH), "exec"), pluginNamespace)

		messages = self.messages

		class Announcer:
			_lastChatOpened = None
			_chatTitleTimer = None
			_chatTitleSpeechQuietUntil = 0.0
			_chatTitleSpeechWindowHandle = 0
			_paused = False

			def _speakOnce(self, message, *args, brailleMessage, **kwargs):
				if not self._paused:
					messages.append((message, brailleMessage))
					self.titleWasFiltered = not self._filterChatTitleSpeech([message])

		for method in methods:
			setattr(Announcer, method.name, pluginNamespace[method.name])

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
			"api": self.api,
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

	def test_only_the_title_is_announced_once_in_each_language(self):
		for language in ("en", "fr_CA"):
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
					self.assertEqual([], self.messages)
					plugin._chatTitleTimer.callback()
					self.assertEqual([("Second chat", "Second chat")], self.messages)
					self.assertFalse(plugin.titleWasFiltered)
					self.window.children = [self.document]

	def test_focus_speech_is_suppressed_before_the_title_is_queued(self):
		watcher, plugin = self._startWatcher("en")
		self.window.children = [SimpleNamespace(role="document", name="Second chat", children=[])]
		obj = SimpleNamespace(processID=self.window.processID, appModule=watcher)
		nativeSpeech = []
		plugin.event_focusEntered(obj, lambda: nativeSpeech.extend(plugin._filterChatTitleSpeech(["Prompt edit"])))
		self.assertEqual([], nativeSpeech)
		self.assertEqual([10.0], self.cancellations)
		self.assertEqual(100, plugin._chatTitleTimer.delay)
		plugin._chatTitleTimer.callback()
		self.assertEqual([("Second chat", "Second chat")], self.messages)
		self.assertEqual([], plugin._filterChatTitleSpeech(["Conversation region"]))
		self.now += 0.81
		self.assertEqual(["Prompt edit"], plugin._filterChatTitleSpeech(["Prompt edit"]))

	def test_background_application_is_neither_muted_nor_given_a_stale_title(self):
		_, plugin = self._startWatcher("en")
		plugin._announceChatOpened("Second chat", self.window.windowHandle)
		self.foreground = SimpleNamespace(windowHandle=22, processID=8)
		self.assertEqual(["Other app"], plugin._filterChatTitleSpeech(["Other app"]))
		plugin._chatTitleTimer.callback()
		self.assertEqual([], self.messages)
		self.assertEqual(0.0, plugin._chatTitleSpeechQuietUntil)

	def test_quick_switches_replace_the_pending_title(self):
		_, plugin = self._startWatcher("en")
		plugin._announceChatOpened("Second chat", self.window.windowHandle)
		oldTimer = plugin._chatTitleTimer
		plugin._announceChatOpened("Third chat", self.window.windowHandle)
		self.assertTrue(oldTimer.stopped)
		plugin._chatTitleTimer.callback()
		self.assertEqual([("Third chat", "Third chat")], self.messages)

	def test_unready_browse_buffer_delays_the_title_with_a_deadline(self):
		_, plugin = self._startWatcher("en")
		plugin._announceChatOpened("Second chat", self.window.windowHandle)
		self.focus.treeInterceptor.isReady = False
		plugin._chatTitleTimer.callback()
		self.assertEqual([], self.messages)
		self.now += 1.6
		plugin._chatTitleTimer.callback()
		self.assertEqual([("Second chat", "Second chat")], self.messages)

	def test_paused_or_silent_announcements_do_not_silence_focus_speech(self):
		for paused, speechEnabled in ((True, True), (False, False)):
			with self.subTest(paused=paused, speechEnabled=speechEnabled):
				_, plugin = self._startWatcher("en")
				plugin._paused = paused
				self.settings["speech"] = speechEnabled
				self.cancellations.clear()
				plugin._announceChatOpened("Second chat", self.window.windowHandle)
				self.assertEqual([], self.cancellations)
				self.assertEqual(["Prompt"], plugin._filterChatTitleSpeech(["Prompt"]))
				self.messages.clear()

	def test_keyboard_input_restores_speech_and_cancels_pending_titles_on_the_main_queue(self):
		_, plugin = self._startWatcher("en")
		plugin._announceChatOpened("Second chat", self.window.windowHandle)
		pending = plugin._chatTitleTimer
		plugin._appFocusState = False
		self.assertTrue(plugin._observeInputGesture(SimpleNamespace()))
		self.assertEqual(["Typed character"], plugin._filterChatTitleSpeech(["Typed character"]))
		self.assertTrue(plugin._observePromptGestureIdentifiers(()))
		self.assertTrue(pending.stopped)
		self.assertIsNone(plugin._chatTitleTimer)

	def test_native_alerts_are_forwarded_without_speech_suppression(self):
		_, plugin = self._startWatcher("en")
		plugin._announceChatOpened("Second chat", self.window.windowHandle)
		alerts = []
		plugin.event_alert(self.window, lambda: alerts.extend(plugin._filterChatTitleSpeech(["Permission required"])))
		self.assertEqual(["Permission required"], alerts)

	def test_focus_event_is_forwarded_even_if_the_title_check_fails(self):
		_, plugin = self._startWatcher("en")
		def fail(obj):
			raise RuntimeError("Document disappeared")
		plugin._checkChatTitleBeforeFocus = fail
		events = []
		plugin.event_focusEntered(self.window, lambda: events.append("forwarded"))
		self.assertEqual(["forwarded"], events)

	@unittest.expectedFailure
	def test_renaming_the_current_chat_does_not_announce_an_opening(self):
		watcher, plugin = self._startWatcher("en")
		self.document.name = "Renamed chat"
		watcher._titleWatch.callback()
		plugin._chatTitleTimer.callback()
		self.assertEqual([], self.messages)
