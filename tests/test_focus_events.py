"""Check native focus acceptance without changing NVDA's event dispatcher."""

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest


PLUGIN_PATH = Path(__file__).parents[1] / "globalPlugins" / "codexStatusAnnouncer" / "__init__.py"


class NativeFocusGuardTests(unittest.TestCase):
	def setUp(self):
		self.foreground = 10
		self.owners = {10: 10, 11: 10, 12: 10, 20: 20, 21: 20, 30: 30}
		self.messages = []
		class IAccessible:
			shouldAllowIAccessibleFocusEvent = property(lambda obj: obj.nativeAllows)
		class UIA:
			shouldAllowUIAFocusEvent = property(lambda obj: obj.nativeAllows)
		self.namespace = {
			"IAccessible": IAccessible, "UIA": UIA,
			"winUser": SimpleNamespace(
				GA_ROOTOWNER=3, getForegroundWindow=lambda: self.foreground,
				getAncestor=lambda handle, flag: self.owners.get(handle, handle),
				getWindowThreadProcessID=lambda handle: (8 if handle == 30 else 7, 1),
			),
			"log": SimpleNamespace(debug=lambda *args: self.messages.append(args)),
			"_isChatGPTObject": lambda obj: obj.processID == 7,
			"_isCodexPromptObject": lambda obj: False,
			"Role": SimpleNamespace(BUTTON="button", COMBOBOX="combo", EDITABLETEXT="edit"),
		}
		tree = ast.parse(PLUGIN_PATH.read_text(encoding="utf-8"))
		nodes = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in (
			"_isOtherChatGPTWindow", "ChatGPTIAccessibleFocusGuard", "ChatGPTUIAFocusGuard",
		)]
		plugin = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "GlobalPlugin")
		nodes.append(next(node for node in plugin.body if isinstance(node, ast.FunctionDef) and node.name == "chooseNVDAObjectOverlayClasses"))
		exec(compile(ast.Module(body=nodes, type_ignores=[]), str(PLUGIN_PATH), "exec"), self.namespace)

	def object(self, backend, handle=21, nativeAllows=True):
		obj = self.namespace[f"ChatGPT{backend}FocusGuard"]()
		obj.windowHandle, obj.processID = handle, 7
		obj.nativeAllows, obj.role = nativeAllows, "section"
		return obj

	def accepts(self, obj, backend):
		return getattr(obj, f"_get_shouldAllow{backend}FocusEvent")()

	def test_background_focus_is_rejected_before_native_focus_processing(self):
		for backend in ("IAccessible", "UIA"):
			with self.subTest(backend=backend):
				self.assertFalse(self.accepts(self.object(backend), backend))
		self.assertEqual(2, len(self.messages))

	def test_actual_window_switch_is_allowed_even_before_nvda_updates_its_foreground(self):
		for backend in ("IAccessible", "UIA"):
			obj = self.object(backend)
			self.assertFalse(self.accepts(obj, backend))
			self.foreground = 20
			self.assertTrue(self.accepts(obj, backend))
			self.foreground = 10

	def test_owned_dialogs_keep_native_acceptance_and_native_rejections(self):
		for backend in ("IAccessible", "UIA"):
			with self.subTest(backend=backend):
				self.assertTrue(self.accepts(self.object(backend, 12), backend))
				self.assertFalse(self.accepts(self.object(backend, 12, nativeAllows=False), backend))
				self.foreground = 12
				self.assertTrue(self.accepts(self.object(backend, 11), backend))
				self.foreground = 10

	def test_guard_does_not_override_native_rules_when_another_app_is_foreground(self):
		self.foreground = 30
		for backend in ("IAccessible", "UIA"):
			self.assertTrue(self.accepts(self.object(backend), backend))
			self.assertFalse(self.accepts(self.object(backend, nativeAllows=False), backend))

	def test_overlays_are_registered_only_for_supported_app_objects(self):
		choose = self.namespace["chooseNVDAObjectOverlayClasses"]
		for backend in ("IAccessible", "UIA"):
			obj = self.object(backend)
			classes = []
			choose(None, obj, classes)
			self.assertEqual([type(obj)], classes)
			obj.processID = 8
			classes = []
			choose(None, obj, classes)
			self.assertEqual([], classes)
