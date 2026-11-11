import ast
import gettext
from pathlib import Path
from types import SimpleNamespace
import unittest


PLUGIN_PATH = Path(__file__).parents[1] / "globalPlugins" / "codexStatusAnnouncer" / "__init__.py"


def loadMethod(name, namespace):
	tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
	plugin = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin")
	method = next(node for node in plugin.body if isinstance(node, ast.FunctionDef) and node.name == name)
	exec(compile(ast.Module(body=[method], type_ignores=[]), str(PLUGIN_PATH), "exec"), namespace)
	return namespace[name]


class MessageReviewTests(unittest.TestCase):
	def test_all_ten_positions_announce_only_the_author_and_text_in_english_and_french(self):
		messages = tuple(
			("user" if index % 2 else "assistant", f"Actual message text {index}")
			for index in range(10)
		)
		for language, userLabel, assistantLabel, separator in (
			("en", "You", "ChatGPT", ": "),
			("fr", "Vous", "ChatGPT", " : "),
			("fr_CA", "Vous", "ChatGPT", " : "),
		):
			with self.subTest(language=language):
				spoken = []
				translate = gettext.translation(
					"nvda", PLUGIN_PATH.parents[2] / "locale", languages=[language], fallback=language == "en",
				).gettext
				method = loadMethod("_readRecentChatMessage", {"_": translate, "ui": SimpleNamespace(message=spoken.append)})
				subject = SimpleNamespace(_currentChatMessages=lambda: messages)
				for position in range(1, 11):
					method(subject, position)
				self.assertEqual([
					(userLabel if speaker == "user" else assistantLabel) + separator + text
					for speaker, text in reversed(messages)
				], spoken)

	def test_empty_or_short_conversations_keep_their_explanatory_messages(self):
		spoken = []
		method = loadMethod("_readRecentChatMessage", {"_": lambda text: text, "ui": SimpleNamespace(message=spoken.append)})
		method(SimpleNamespace(_currentChatMessages=lambda: ()), 1)
		method(SimpleNamespace(_currentChatMessages=lambda: (("assistant", "Only response"),)), 2)
		self.assertEqual([
			"No recent chat messages are available", "Only 1 recent chat messages are available",
		], spoken)

	def test_focused_composer_precedes_a_valid_remembered_composer_in_another_pane(self):
		remembered = SimpleNamespace(isPrompt=True)
		focused = SimpleNamespace(isPrompt=True)
		focus = SimpleNamespace(isPrompt=False, parent=focused)
		namespace = {
			"api": SimpleNamespace(getFocusObject=lambda: focus),
			"_isDefunctObject": lambda obj: False,
			"_isCodexPromptObject": lambda obj: obj.isPrompt,
		}
		method = loadMethod("_findChatGPTPromptObject", namespace)
		subject = SimpleNamespace(_lastPromptObject=remembered, _pendingPromptObject=None, _buffer=None)
		self.assertIs(focused, method(subject))
		focus.parent = None
		self.assertIs(remembered, method(subject))

	def test_short_side_conversation_does_not_include_older_main_pane_messages(self):
		container = SimpleNamespace(role="region", classes="thread-scroll-container", parent=None)
		prompt = SimpleNamespace(parent=container)
		class Info:
			def __init__(self, start, end):
				self.start, self.end = start, end
			def collapse(self):
				self.end = self.start
			def compareEndPoints(self, other, which):
				assert which == "startToStart"
				return self.start - other.start
			def setEndPoint(self, other, which):
				assert which == "startToStart"
				self.start = other.start
		class Buffer:
			def makeTextInfo(self, obj):
				if obj is container:
					return Info(100, 220)
				assert obj is prompt
				return Info(200, 210)
		def extend(info, count):
			previous = info.start
			info.start = max(0, info.start - count)
			return info.start - previous
		namespace = {
			"Role": SimpleNamespace(DOCUMENT="document"),
			"_domClassNames": lambda obj: obj.classes,
			"_extendScanStart": extend,
			"RECENT_CHAT_INITIAL_SCAN_CHARACTERS": 32768,
			"RECENT_CHAT_MAX_SCAN_CHARACTERS": 524288,
		}
		method = loadMethod("_activeBranchMessages", namespace)
		scans = []
		def messages(info, **kwargs):
			scans.append((info.start, info.end))
			main = (("assistant", "Other conversation"),) if info.start < 100 else ()
			return main + (("user", "Side question"), ("assistant", "Side answer")), False
		subject = SimpleNamespace(
			_buffer=Buffer(), _findChatGPTPromptObject=lambda: prompt,
			_chatMessagesFromInfo=messages,
		)
		self.assertEqual((("user", "Side question"), ("assistant", "Side answer")), method(subject, 10))
		self.assertEqual([(100, 200)], scans)
