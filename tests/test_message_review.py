import ast
import gettext
from pathlib import Path
import runpy
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch


PLUGIN_PATH = Path(__file__).parents[1] / "globalPlugins" / "codexStatusAnnouncer" / "__init__.py"
REVIEW = runpy.run_path(str(PLUGIN_PATH.with_name("recentMessages.py")))


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
				method = loadMethod("_speakRecentChatMessage", {"_": translate, "ui": SimpleNamespace(message=spoken.append)})
				subject = SimpleNamespace(_currentChatMessages=lambda: messages)
				for position in range(1, 11):
					method(subject, position)
				self.assertEqual([
					(userLabel if speaker == "user" else assistantLabel) + separator + text
					for speaker, text in reversed(messages)
				], spoken)

	def test_empty_or_short_conversations_keep_their_explanatory_messages(self):
		spoken = []
		method = loadMethod("_speakRecentChatMessage", {"_": lambda text: text, "ui": SimpleNamespace(message=spoken.append)})
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
			"conversationContainer": REVIEW["conversationContainer"],
			"activeConversationContainer": REVIEW["activeConversationContainer"],
			"findConversationPrompt": REVIEW["findConversationPrompt"],
			"_domClassNames": lambda obj: getattr(obj, "classes", ""),
			"_sameNVDAObject": lambda left, right: left is right,
		}
		method = loadMethod("_findChatGPTPromptObject", namespace)
		subject = SimpleNamespace(_lastPromptObject=remembered, _pendingPromptObject=None, _buffer=None)
		self.assertIs(focused, method(subject))
		focus.parent = None
		self.assertIs(remembered, method(subject))

	def test_focus_in_transcript_uses_its_composer_instead_of_the_other_panes_cache(self):
		wrong = SimpleNamespace(isPrompt=True, parent=None)
		composer = SimpleNamespace(isPrompt=True, children=[], classes="ProseMirror")
		container = SimpleNamespace(isPrompt=False, classes="thread-scroll-container", parent=None, children=[composer])
		composer.parent = container
		focus = SimpleNamespace(isPrompt=False, parent=container, children=[])
		namespace = {
			"api": SimpleNamespace(getFocusObject=lambda: focus),
			"_isDefunctObject": lambda obj: False,
			"_isCodexPromptObject": lambda obj: obj.isPrompt,
			"conversationContainer": REVIEW["conversationContainer"],
			"activeConversationContainer": REVIEW["activeConversationContainer"],
			"findConversationPrompt": REVIEW["findConversationPrompt"],
			"_domClassNames": lambda obj: getattr(obj, "classes", ""),
			"_sameNVDAObject": lambda left, right: left is right,
		}
		method = loadMethod("_findChatGPTPromptObject", namespace)
		subject = SimpleNamespace(_lastPromptObject=wrong, _pendingPromptObject=None, _buffer=None)
		self.assertIs(composer, method(subject))
		container.children.clear()
		self.assertIsNone(method(subject))

	def test_short_side_conversation_does_not_include_older_main_pane_messages(self):
		container = SimpleNamespace(role="region", classes="thread-scroll-container", parent=None)
		prompt = SimpleNamespace(parent=container, classes="ProseMirror")
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
			"conversationContainer": REVIEW["conversationContainer"],
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

	def test_browse_caret_selects_its_pane_even_when_keyboard_focus_stays_in_another(self):
		def pane():
			container = SimpleNamespace(classes="thread-scroll-container", parent=None, isPrompt=False)
			prompt = SimpleNamespace(classes="ProseMirror", parent=container, isPrompt=True, children=[])
			container.children = [prompt]
			return container, prompt
		left, leftPrompt = pane()
		right, rightPrompt = pane()
		heading = SimpleNamespace(classes="sr-only", parent=left, isPrompt=False)
		buffer = SimpleNamespace(passThrough=False, selection=SimpleNamespace(NVDAObjectAtStart=heading))
		namespace = {
			"api": SimpleNamespace(getFocusObject=lambda: rightPrompt),
			"_isDefunctObject": lambda obj: False,
			"_isCodexPromptObject": lambda obj: obj.isPrompt,
			"conversationContainer": REVIEW["conversationContainer"],
			"activeConversationContainer": REVIEW["activeConversationContainer"],
			"findConversationPrompt": REVIEW["findConversationPrompt"],
			"_domClassNames": lambda obj: getattr(obj, "classes", ""),
			"_sameNVDAObject": lambda a, b: a is b,
		}
		method = loadMethod("_findChatGPTPromptObject", namespace)
		subject = SimpleNamespace(_buffer=buffer, _lastPromptObject=rightPrompt, _pendingPromptObject=None)
		self.assertIs(leftPrompt, method(subject))
		# Focus mode must follow its actual editor even when browse selection is stale.
		buffer.passThrough = True
		self.assertIs(rightPrompt, method(subject))
		# Outside a transcript (for example in the sidebar), keep the focused pane.
		buffer.passThrough = False
		buffer.selection.NVDAObjectAtStart = SimpleNamespace(classes="", parent=None)
		self.assertIs(rightPrompt, method(subject))

	def test_unavailable_browse_selection_falls_back_to_the_focused_conversation(self):
		container = SimpleNamespace(classes="thread-scroll-container", parent=None)
		focus = SimpleNamespace(classes="ProseMirror", parent=container)
		class UpdatingBuffer:
			passThrough = False
			@property
			def selection(self):
				raise RuntimeError("Virtual buffer is being refreshed")
		self.assertIs(container, REVIEW["activeConversationContainer"](
			UpdatingBuffer(), focus, lambda obj: obj.classes,
		))


class RecentMessageScrollTests(unittest.TestCase):
	def setUp(self):
		self.timers = []
		self.observers = []
		self.reads = []
		self.valid = True
		self.content = "Old viewport response"
		self.context = object(), object(), 10, "Chat"
		self.scrolls = []
		self.pattern = SimpleNamespace(CurrentVerticallyScrollable=True, CurrentVerticalScrollPercent=40)
		def scroll(horizontal, vertical):
			self.scrolls.append((horizontal, vertical))
			self.pattern.CurrentVerticalScrollPercent = vertical
		self.pattern.SetScrollPercent = scroll
		def schedule(delay, callback, *args):
			timer = SimpleNamespace(delay=delay, stopped=False)
			timer.Stop = lambda: setattr(timer, "stopped", True)
			timer.run = lambda: callback(*args)
			self.timers.append(timer)
			return timer
		def observer(callback):
			obj = SimpleNamespace(callback=callback, detached=False)
			obj.attach = lambda buffer: setattr(obj, "buffer", buffer)
			obj.detach = lambda: setattr(obj, "detached", True)
			self.observers.append(obj)
			return obj
		self.review = REVIEW["RecentMessageReview"](
			schedule, observer, lambda position: self.reads.append((position, self.content)),
			lambda context: self.valid and context is self.context,
		)

	def test_scrolling_waits_for_updated_content_without_reading_the_old_viewport(self):
		self.review.request(1, self.context, self.pattern)
		self.assertEqual([(-1, 100)], self.scrolls)
		self.assertEqual([], self.reads)
		self.content = "Actual newest response"
		self.observers[-1].callback(self.context[0])
		self.assertEqual([], self.reads)
		self.timers[-1].run()
		self.assertEqual([(1, "Actual newest response")], self.reads)
		self.assertTrue(self.observers[-1].detached)
		self.assertTrue(self.timers[0].stopped)

	def test_already_at_end_reads_immediately_without_scroll_or_timers(self):
		self.pattern.CurrentVerticalScrollPercent = 100
		self.review.request(2, self.context, self.pattern)
		self.assertEqual([(2, self.content)], self.reads)
		self.assertEqual([], self.scrolls)
		self.assertEqual([], self.timers)

	def test_nearly_at_end_still_scrolls_to_the_actual_bottom(self):
		self.pattern.CurrentVerticalScrollPercent = 99.999
		self.review.request(1, self.context, self.pattern)
		self.assertEqual([(-1, 100)], self.scrolls)
		self.assertEqual([], self.reads)

	def test_changing_chat_pane_or_application_cancels_delayed_speech(self):
		self.review.request(1, self.context, self.pattern)
		self.valid = False
		self.observers[-1].callback(self.context[0])
		self.timers[-1].run()
		self.assertEqual([], self.reads)
		self.assertTrue(self.observers[-1].detached)

	def test_scrolling_away_again_does_not_read_a_misleading_old_message(self):
		self.review.request(1, self.context, self.pattern)
		self.pattern.CurrentVerticalScrollPercent = 25
		self.timers[0].run()
		self.assertEqual([], self.reads)

	def test_no_dom_change_reacquires_content_after_the_settle_deadline(self):
		self.review.request(1, self.context, self.pattern)
		self.content = "Response already present in the unchanged buffer"
		self.timers[0].run()
		self.assertEqual([(1, self.content)], self.reads)
		self.assertTrue(self.observers[-1].detached)

	def test_repeated_shortcuts_replace_pending_reads_and_ignore_late_callbacks(self):
		self.review.request(1, self.context, self.pattern)
		old = self.observers[-1]
		self.pattern.CurrentVerticalScrollPercent = 20
		self.review.request(3, self.context, self.pattern)
		self.assertTrue(old.detached)
		old.callback(self.context[0])
		self.assertEqual([], self.reads)
		self.observers[-1].callback(self.context[0])
		self.timers[-1].run()
		self.assertEqual([(3, self.content)], self.reads)

	def test_scroll_error_detaches_the_observer_and_cancels_the_timeout(self):
		def fail(*args):
			raise RuntimeError("Disconnected scroll provider")
		self.pattern.SetScrollPercent = fail
		with self.assertRaises(RuntimeError):
			self.review.request(1, self.context, self.pattern)
		self.assertTrue(self.observers[-1].detached)
		self.assertTrue(self.timers[-1].stopped)
		self.assertEqual([], self.reads)

	def test_other_buffer_updates_do_not_complete_the_request(self):
		self.review.request(1, self.context, self.pattern)
		self.observers[-1].callback(object())
		self.assertEqual(1, len(self.timers))
		self.assertEqual([], self.reads)

	def test_repeated_shortcut_at_scroll_end_still_waits_for_the_pending_buffer(self):
		self.review.request(1, self.context, self.pattern)
		self.assertEqual(100, self.pattern.CurrentVerticalScrollPercent)
		self.review.request(2, self.context, self.pattern)
		self.assertEqual([], self.reads)
		self.content = "Newest content after Chromium refresh"
		self.observers[-1].callback(self.context[0])
		self.timers[-1].run()
		self.assertEqual([(2, self.content)], self.reads)

	def test_command_preserves_an_inflight_review_when_the_shortcut_is_repeated(self):
		prompt = object()
		buffer = SimpleNamespace(rootNVDAObject=SimpleNamespace(name="Chat"))
		self.review._valid = lambda context: context[0] is buffer and context[1] is prompt
		subject = SimpleNamespace(
			_recentMessageReview=self.review, _buffer=buffer,
			_rememberBuffer=lambda *args, **kwargs: None,
			_findChatGPTPromptObject=lambda: prompt,
			_speakRecentChatMessage=lambda position: self.fail("Read bypassed the pending buffer"),
		)
		namespace = {
			"api": SimpleNamespace(getFocusObject=lambda: prompt),
			"conversationContainer": lambda *args: SimpleNamespace(windowHandle=10),
			"_domClassNames": lambda obj: "thread-scroll-container",
			"winUser": SimpleNamespace(GA_ROOT=2, getAncestor=lambda *args: 10, getForegroundWindow=lambda: 10),
			"conversationScrollPattern": lambda *args: self.pattern,
			"log": SimpleNamespace(debug=lambda *args: None),
		}
		method = loadMethod("_readRecentChatMessage", namespace)
		method(subject, 1)
		method(subject, 2)
		self.assertEqual([], self.reads)
		self.assertEqual(1, len(self.observers))
		self.content = "Latest response from the refreshed conversation"
		self.observers[-1].callback(buffer)
		self.timers[-1].run()
		self.assertEqual([(2, self.content)], self.reads)

	def test_delayed_review_rejects_a_changed_buffer_prompt_window_or_title(self):
		prompt = object()
		buffer = SimpleNamespace(rootNVDAObject=SimpleNamespace(name="Chat"))
		foreground = [10]
		namespace = {
			"winUser": SimpleNamespace(getForegroundWindow=lambda: foreground[0]),
			"_sameNVDAObject": lambda left, right: left is right,
			"log": SimpleNamespace(debug=lambda *args: None),
		}
		method = loadMethod("_recentMessageContextIsCurrent", namespace)
		subject = SimpleNamespace(_buffer=buffer, _findChatGPTPromptObject=lambda: prompt)
		context = buffer, prompt, 10, "Chat"
		self.assertTrue(method(subject, context))
		for changed in ("buffer", "prompt", "window", "title"):
			with self.subTest(changed=changed):
				subject._buffer = object() if changed == "buffer" else buffer
				subject._findChatGPTPromptObject = lambda: None if changed == "prompt" else prompt
				foreground[0] = 20 if changed == "window" else 10
				buffer.rootNVDAObject.name = "Other chat" if changed == "title" else "Chat"
				self.assertFalse(method(subject, context))

	def test_observer_attach_error_cleans_up_the_partial_request(self):
		def observer(callback):
			obj = SimpleNamespace(detached=False)
			def fail(buffer):
				raise RuntimeError("Buffer unavailable")
			obj.attach = fail
			obj.detach = lambda: setattr(obj, "detached", True)
			self.observers.append(obj)
			return obj
		self.review._observerFactory = observer
		with self.assertRaises(RuntimeError):
			self.review.request(1, self.context, self.pattern)
		self.assertTrue(self.observers[-1].detached)
		self.assertIsNone(self.review._pending)
		self.assertEqual([], self.scrolls)

	def test_scheduler_error_cleans_up_the_attached_observer(self):
		def fail(*args):
			raise RuntimeError("Application shutting down")
		self.review._schedule = fail
		with self.assertRaises(RuntimeError):
			self.review.request(1, self.context, self.pattern)
		self.assertTrue(self.observers[-1].detached)
		self.assertIsNone(self.review._pending)
		self.assertEqual([], self.scrolls)

	def test_intermediate_buffer_event_does_not_cancel_an_unfinished_scroll(self):
		self.review.request(1, self.context, self.pattern)
		self.pattern.CurrentVerticalScrollPercent = 90
		self.observers[-1].callback(self.context[0])
		self.timers[-1].run()
		self.assertFalse(self.observers[-1].detached)
		self.pattern.CurrentVerticalScrollPercent = 100
		self.content = "Newest content after the final update"
		self.observers[-1].callback(self.context[0])
		self.timers[-1].run()
		self.assertEqual([(1, self.content)], self.reads)

	def test_native_scroller_selection_uses_structure_and_bounds_in_any_language(self):
		classes = "thread-scroll-container overflow-y-auto"
		container = SimpleNamespace(location=(720, 100, 1100, 900))
		selected = object()
		def element(name, left, pattern):
			return SimpleNamespace(
				CurrentName=name,
				CurrentBoundingRectangle=SimpleNamespace(left=left, top=100, right=left + 1100, bottom=1000),
				GetCurrentPattern=lambda kind: SimpleNamespace(QueryInterface=lambda interface: pattern),
			)
		for name in ("Conversation", "Discussion", "Gespräch"):
			with self.subTest(name=name):
				elements = [element("Other pane", 10, object()), element(name, 720, selected)]
				conditions = []
				client = SimpleNamespace(
					ElementFromHandle=lambda handle: SimpleNamespace(FindAll=lambda scope, condition: SimpleNamespace(
						Length=len(elements), GetElement=lambda index: elements[index],
					)),
					createPropertyCondition=lambda prop, value: conditions.append((prop, value)),
				)
				stub = SimpleNamespace(handler=SimpleNamespace(clientObject=client), UIA_ClassNamePropertyId=1,
					TreeScope_Descendants=2, UIA_ScrollPatternId=3, IUIAutomationScrollPattern=object())
				with patch.dict(sys.modules, {"UIAHandler": stub}):
					actual = REVIEW["conversationScrollPattern"](container, 10, lambda obj: classes)
				self.assertIs(selected, actual)
				self.assertEqual([(1, classes)], conditions)


class ForegroundConversationTests(unittest.TestCase):
	def setUp(self):
		self.foreground = SimpleNamespace(windowHandle=10, supported=True, processID=7)
		self.owners = {10: 10, 11: 10, 12: 10, 20: 20}
		self.namespace = {
			"api": SimpleNamespace(getForegroundObject=lambda: self.foreground),
			"winUser": SimpleNamespace(
				GA_ROOTOWNER=3, getAncestor=lambda handle, flag: self.owners.get(handle, handle),
				getForegroundWindow=lambda: self.foreground.windowHandle,
				getWindowThreadProcessID=lambda handle: (8 if handle == 30 else 7, 1),
			),
			"_isChatGPTObject": lambda obj: getattr(obj, "supported", False),
		}
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		helper = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_isOtherChatGPTWindow")
		exec(compile(ast.Module(body=[helper], type_ignores=[]), str(PLUGIN_PATH), "exec"), self.namespace)

	def test_secondary_window_is_not_allowed_to_replace_the_foreground_chat(self):
		other = SimpleNamespace(windowHandle=20, supported=True, processID=7)
		guard = self.namespace["_isOtherChatGPTWindow"]
		self.assertTrue(guard(other))
		self.assertFalse(guard(SimpleNamespace(windowHandle=11, processID=7)))
		# An owned menu belongs to the same foreground window.
		self.assertFalse(guard(SimpleNamespace(windowHandle=12, processID=7)))
		self.foreground = other
		self.assertFalse(guard(other))

	def test_other_application_foreground_preserves_background_monitoring(self):
		self.foreground = SimpleNamespace(windowHandle=30, supported=False)
		self.assertFalse(self.namespace["_isOtherChatGPTWindow"](SimpleNamespace(windowHandle=20, processID=7)))

	def test_secondary_events_do_not_change_buffers_titles_or_popup_focus(self):
		other = SimpleNamespace(windowHandle=20, supported=True, processID=7)
		buffer = object()
		subject = SimpleNamespace(_buffer=buffer, _appFocusState=True, _conversationWindowHandle=10)
		for name in ("_rememberBuffer", "_rememberConversationWindowFromEvent", "_schedulePopupDialogFocus"):
			with self.subTest(method=name):
				method = loadMethod(name, self.namespace)
				self.assertFalse(method(subject, other))
				self.assertIs(buffer, subject._buffer)
				self.assertEqual(10, subject._conversationWindowHandle)
		checks = []
		other.appModule = SimpleNamespace(_checkChatTitle=lambda **kwargs: checks.append(kwargs))
		method = loadMethod("_checkChatTitleBeforeFocus", self.namespace)
		method(subject, other)
		self.assertEqual([], checks)
