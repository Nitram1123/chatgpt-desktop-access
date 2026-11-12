"""Load the end of one conversation before reviewing its newest messages."""

from collections import deque
from dataclasses import dataclass


THREAD_SCROLL_CLASS = "thread-scroll-container"
BUFFER_SETTLE_DELAY_MS = 120
REVIEW_TIMEOUT_MS = 1800


def conversationContainer(obj, classNames):
	"""Find the transcript containing a prompt or another conversation control."""
	for _ in range(32):
		if obj is None:
			return None
		if THREAD_SCROLL_CLASS in classNames(obj).split():
			return obj
		obj = getattr(obj, "parent", None)
	return None


def activeConversationContainer(buffer, focus, classNames):
	"""Follow the browse caret, or keyboard focus when entering text."""
	if buffer is not None and not getattr(buffer, "passThrough", True):
		try:
			container = conversationContainer(buffer.selection.NVDAObjectAtStart, classNames)
			if container is not None:
				return container
		except Exception:
			# A refresh can invalidate the old browse selection. Keep focus usable.
			pass
	return conversationContainer(focus, classNames)


def conversationScrollPattern(container, windowHandle, classNames):
	"""Match the same transcript in UIA by class and bounds, never by its label."""
	import UIAHandler

	classes = classNames(container)
	if THREAD_SCROLL_CLASS not in classes.split():
		return None
	left, top, width, height = container.location
	expected = left, top, left + width, top + height
	client = UIAHandler.handler.clientObject
	root = client.ElementFromHandle(windowHandle)
	condition = client.createPropertyCondition(UIAHandler.UIA_ClassNamePropertyId, classes)
	elements = root.FindAll(UIAHandler.TreeScope_Descendants, condition)
	matches = []
	for index in range(elements.Length):
		element = elements.GetElement(index)
		rect = element.CurrentBoundingRectangle
		bounds = rect.left, rect.top, rect.right, rect.bottom
		if all(abs(actual - target) <= 3 for actual, target in zip(bounds, expected)):
			matches.append(element)
	if len(matches) != 1:
		return None
	pattern = matches[0].GetCurrentPattern(UIAHandler.UIA_ScrollPatternId)
	return pattern.QueryInterface(UIAHandler.IUIAutomationScrollPattern) if pattern else None


def findConversationPrompt(container, isPrompt):
	"""Find a composer within a known transcript, without searching other panes."""
	pending = deque([(container, 0)])
	for _ in range(512):
		if not pending:
			break
		obj, depth = pending.popleft()
		try:
			if isPrompt(obj):
				return obj
			if depth < 16:
				pending.extend((child, depth + 1) for child in obj.children)
		except Exception:
			continue
	return None


def atConversationEnd(pattern):
	return not pattern.CurrentVerticallyScrollable or pattern.CurrentVerticalScrollPercent >= 100


@dataclass(eq=False)
class _ReviewRequest:
	position: int
	context: tuple
	pattern: object


class RecentMessageReview:
	"""Wait for a scrolled transcript's buffer, keeping focus and drafts intact."""

	def __init__(self, schedule, observerFactory, read, valid):
		self._schedule = schedule
		self._observerFactory = observerFactory
		self._read = read
		self._valid = valid
		self._pending = None
		self._observer = None
		self._timeout = None
		self._settle = None

	def cancel(self):
		self._pending = None
		for name in ("_timeout", "_settle"):
			timer = getattr(self, name)
			if timer is not None:
				timer.Stop()
				setattr(self, name, None)
		if self._observer is not None:
			self._observer.detach()
			self._observer = None

	def request(self, position, context, pattern):
		pending = self._pending
		try:
			if pending is not None and self._valid(pending.context) and atConversationEnd(pending.pattern):
				# UIA can reach the bottom before NVDA receives the refreshed content.
				# Keep that subscription and its deadline; only replace the desired turn.
				pending.position = position
				return
		except Exception:
			# A stale provider must not prevent a fresh request from being prepared.
			pass
		self.cancel()
		if atConversationEnd(pattern):
			self._read(position)
			return
		request = _ReviewRequest(position, context, pattern)
		self._pending = request
		try:
			self._observer = self._observerFactory(lambda buffer: self._updated(request, buffer))
			self._observer.attach(context[0])
			# Scrolling already-loaded content may produce no buffer event. Keep a
			# bounded fallback, also covering an unavailable update subscription.
			self._timeout = self._schedule(REVIEW_TIMEOUT_MS, self._finish, request, True)
			pattern.SetScrollPercent(-1, 100)
		except Exception:
			self.cancel()
			raise

	def _updated(self, request, buffer):
		if request is not self._pending or buffer is not request.context[0]:
			return
		if self._settle is not None:
			self._settle.Stop()
		self._settle = self._schedule(BUFFER_SETTLE_DELAY_MS, self._finish, request)

	def _finish(self, request, deadlineReached=False):
		if request is not self._pending:
			return
		try:
			valid = self._valid(request.context)
			atEnd = atConversationEnd(request.pattern) if valid else False
		except Exception:
			valid = False
			atEnd = False
		if valid and not atEnd and not deadlineReached:
			# Intermediate DOM updates can precede completion of the native scroll.
			return
		self.cancel()
		if valid and atEnd:
			self._read(request.position)
