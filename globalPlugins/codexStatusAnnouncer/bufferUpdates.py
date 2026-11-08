"""Observe updates to one Chromium virtual buffer owned by NVDA."""

import time

import wx
from logHandler import log


class BufferUpdateObserver:
	def __init__(self, onUpdate):
		self._onUpdate = onUpdate
		self._detach = None

	def attach(self, buffer):
		self.detach()
		original = getattr(buffer, "_handleUpdate", None)
		if not callable(original):
			return

		missing = object()
		originalOverride = vars(buffer).get("_handleUpdate", missing)
		pending = None
		lastSampleAt = None
		attached = True

		def sample():
			nonlocal pending, lastSampleAt
			pending = None
			if not attached:
				return
			lastSampleAt = time.monotonic()
			try:
				self._onUpdate(buffer)
			except Exception:
				log.debugWarning("ChatGPT Desktop Access could not read the updated task timer", exc_info=True)

		def handleUpdate(*args, **kwargs):
			nonlocal pending
			result = original(*args, **kwargs)
			if attached and pending is None:
				delay = 120 if lastSampleAt is None else max(120, round(1000 * (1 - (time.monotonic() - lastSampleAt))))
				try:
					pending = wx.CallLater(delay, sample)
				except Exception:
					log.debugWarning("ChatGPT Desktop Access could not schedule a task timer read", exc_info=True)
			return result

		def detach():
			nonlocal attached, pending
			attached = False
			if pending is not None:
				pending.Stop()
				pending = None
			if vars(buffer).get("_handleUpdate") is handleUpdate:
				if originalOverride is missing:
					del buffer._handleUpdate
				else:
					buffer._handleUpdate = originalOverride

		try:
			# NVDA currently exposes no public virtual-buffer update subscription.
			buffer._handleUpdate = handleUpdate
		except (AttributeError, TypeError):
			log.debugWarning("ChatGPT Desktop Access could not observe this virtual buffer", exc_info=True)
			return
		self._detach = detach

	def detach(self):
		if self._detach is not None:
			detach, self._detach = self._detach, None
			detach()
