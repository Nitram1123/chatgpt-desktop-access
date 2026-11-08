"""NVDA-independent parsing and privacy helpers for Codex activity."""

import json
import math
import re
from collections import deque
from pathlib import Path


# ChatGPT interface names
# -----------------------
# Everything the add-on recognizes in ChatGPT by its exact wording or web
# class names is listed here. ChatGPT renames these between releases, so when
# a feature stops working after a ChatGPT update, check this list first. The
# compatibility check run after each ChatGPT update looks for the main ones.

# Labels of the message field, compared without case or extra spaces.
CHATGPT_PROMPT_LABELS = (
	"do anything", "ask anything", "message codex", "message chatgpt", "send a message",
	"work with codex", "work with chatgpt", "ask chatgpt",
	"travaillez avec codex", "travailler avec chatgpt", "travail avec chatgpt", "demander à chatgpt",
)
CHAT_MESSAGE_SPEAKER_LABELS = {
	"you said": "user",
	"chatgpt said": "assistant",
	"vous avez dit": "user",
	"chatgpt a dit": "assistant",
}
# Web class of the message field's editor, whatever its label says.
CHATGPT_PROMPT_EDITOR_CLASS = "ProseMirror"
CHAT_MESSAGE_HEADING_CLASSES = frozenset({
	"sr-only", "print:group-data-[print-formatting]/conversation-print:font-normal",
})
# The button that opens the attachment and tools menu.
ADD_FILES_BUTTON_NAME = "Add files and more"
# Older Codex views offer this separate attachment control.
SOURCES_MENU_BUTTON_NAME = "Attach files or connect apps"
# The ChatGPT and Codex product switch, in the forms ChatGPT has used.
MODE_SWITCH_BUTTON_LABELS = (
	"Switch mode, current mode: ChatGPT", "Switch mode, current mode: Codex",
	"Current mode: ChatGPT", "Current mode: Codex",
	"Switch mode: ChatGPT", "Switch mode: Codex", "Switch mode",
)
# The Chat and Work switch above a new chat's message field.
COMPOSER_MODE_GROUP_NAME = "Composer mode"
# Menus that keep focus in the message field (Add files and more, "/", "@"):
# rows, section headings, and the highlighted row are marked by web classes.
ATTACHMENT_POPUP_HINT_LABELS = ("Type to search files or chats", "Type to search files")
ATTACHMENT_POPUP_CLASS_KEY = "IAccessible2::attribute_class"
ATTACHMENT_POPUP_ROW_CLASS = "app-menu-item-height"
ATTACHMENT_POPUP_HEADER_CLASS = "suggestion-menu-header"
ATTACHMENT_POPUP_HIGHLIGHT_CLASS = "bg-primary-ghost-hover"
# Attached files above the message field, and tool chips such as Web search inside it.
COMPOSER_FILE_CLASS = "composer-attachment-surface"
COMPOSER_TOOL_ICON_CLASS = "_IconContainer"


def mergeSupportedAppNames(value, requiredNames=("chatgpt", "codex")):
	"""Return a stable comma-separated app-module list containing required hosts."""
	result = []
	seen = set()
	for name in (*requiredNames, *str(value or "").split(",")):
		name = str(name or "").strip().casefold()
		if name and name not in seen:
			seen.add(name)
			result.append(name)
	return ",".join(result)


def conversationModeFromDocumentNames(documentNames):
	"""Identify one top-level ChatGPT or Codex conversation document.

	Nested web content contains two document ancestors and is deliberately rejected,
	so activity on an embedded browser page is not mistaken for conversation status.
	"""
	names = tuple(" ".join(str(name or "").casefold().split()) for name in documentNames)
	if len(names) != 1:
		return ""
	return names[0] if names[0] in ("chatgpt", "codex") else ""


def conversationModeFromSwitchLabel(label):
	"""Read the active product mode from ChatGPT's authoritative switch control."""
	text = " ".join(str(label or "").casefold().split())
	match = re.fullmatch(
		r"(?:switch mode,?\s*)?current mode:\s*(chatgpt|codex)"
		r"|switch mode:\s*(chatgpt|codex)",
		text,
	)
	return next((group for group in match.groups() if group), "") if match else ""


def conversationModeFromSwitchControl(name, description="", role="", expandable=False, automationId=""):
	"""Use a switch button's semantics when Chromium moves its label to another field."""
	if str(role or "").casefold() not in ("button", "menubutton", "menu button"):
		return ""
	for label in (name, description):
		mode = conversationModeFromSwitchLabel(label)
		if mode:
			return mode
	if not expandable:
		return ""
	identifier = " ".join(str(automationId or "").casefold().replace("_", " ").split())
	if not ("mode" in identifier or "product" in identifier):
		return ""
	name = " ".join(str(name or "").casefold().split())
	return name if name in ("chatgpt", "codex") else ""


def chatHistorySnapshotDecision(
	modeAge, settleSeconds, titles, otherTitles, otherCurrent,
	pendingTitles, pendingAge, confirmSeconds,
):
	"""Decide when a mode-specific sidebar snapshot is safe to publish."""
	try:
		modeAge = float(modeAge)
	except (TypeError, ValueError, OverflowError):
		modeAge = 0.0
	try:
		pendingAge = float(pendingAge)
	except (TypeError, ValueError, OverflowError):
		pendingAge = 0.0
	if modeAge < max(0.0, float(settleSeconds)):
		return "settle"
	titles = tuple(titles)
	otherTitles = tuple(otherTitles)
	if titles and otherCurrent and titles == otherTitles:
		return "otherMode"
	if pendingTitles is None or tuple(pendingTitles) != titles:
		return "confirm"
	if pendingAge < max(0.0, float(confirmSeconds)):
		return "confirm"
	return "publish"


def loadActiveCodexThreadTitles(codexRoot, limit=2000):
	"""Read active Codex task titles from the append-only local session index."""
	if limit < 1:
		return ()
	codexRoot = Path(codexRoot)
	archivedIds = set()
	archiveDirectory = codexRoot / "archived_sessions"
	if archiveDirectory.is_dir():
		for path in archiveDirectory.glob("*.jsonl"):
			threadId = path.stem[-36:].lower()
			if re.fullmatch(
				r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
				threadId,
			):
				archivedIds.add(threadId)
	indexPath = codexRoot / "session_index.jsonl"
	if not indexPath.is_file():
		return ()
	# The index can contain multiple records for one task. The last valid record is
	# authoritative, while updated_at preserves newest-first display order.
	records = {}
	with indexPath.open("r", encoding="utf-8") as indexFile:
		for line in indexFile:
			try:
				record = json.loads(line)
			except (TypeError, ValueError):
				continue
			if not isinstance(record, dict):
				continue
			threadId = str(record.get("id") or "").strip().lower()
			if not re.fullmatch(
				r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
				threadId,
			):
				continue
			title = " ".join(str(record.get("thread_name") or "").split())
			updatedAt = str(record.get("updated_at") or "")
			if title:
				records[threadId] = (updatedAt, title)
	result = [
		title for threadId, (updatedAt, title) in sorted(
			records.items(), key=lambda item: item[1][0], reverse=True,
		)
		if threadId not in archivedIds
	]
	return tuple(result[:int(limit)])


def codexHistorySourceSignature(codexRoot):
	"""Return cheap metadata that changes when the local Codex history sources change."""
	codexRoot = Path(codexRoot)
	def sourceSignature(path):
		try:
			stat = path.stat()
			return True, int(getattr(stat, "st_mtime_ns", int(stat.st_mtime * 1_000_000_000))), int(stat.st_size)
		except OSError:
			return False, 0, 0
	return (
		str(codexRoot),
		sourceSignature(codexRoot / "session_index.jsonl"),
		sourceSignature(codexRoot / "archived_sessions"),
	)


def modeSpecificRecentChatTitles(mode, unifiedTitles, activeCodexTitles):
	"""Partition ChatGPT's unified Recents list into ChatGPT chats or Codex tasks."""
	mode = str(mode or "").casefold()
	if mode not in ("chatgpt", "codex"):
		return ()
	codexKeys = {
		" ".join(str(title or "").split()).casefold()
		for title in activeCodexTitles
		if str(title or "").strip()
	}
	result = []
	seen = set()
	for rawTitle in unifiedTitles:
		title = " ".join(str(rawTitle or "").split())
		key = title.casefold()
		if not title or key in seen:
			continue
		isCodex = key in codexKeys
		if (mode == "codex") == isCodex:
			seen.add(key)
			result.append(title)
	return tuple(result)


def loadArchivedThreads(codexRoot, limit=200, translate=lambda text: text):
	"""Read archived thread IDs and titles from Codex's JSONL metadata."""
	if limit < 1:
		return ()
	codexRoot = Path(codexRoot)
	archiveDirectory = codexRoot / "archived_sessions"
	if not archiveDirectory.is_dir():
		return ()
	def modifiedTime(path):
		try:
			return path.stat().st_mtime
		except OSError:
			return 0
	paths = sorted(archiveDirectory.glob("*.jsonl"), key=modifiedTime, reverse=True)
	threadIds = []
	for path in paths:
		threadId = path.stem[-36:]
		if re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", threadId):
			threadIds.append(threadId.lower())
	threadIds = tuple(threadIds[:int(limit)])
	targetIds = set(threadIds)
	titles = {}
	indexPath = codexRoot / "session_index.jsonl"
	if indexPath.is_file() and targetIds:
		with indexPath.open("r", encoding="utf-8") as indexFile:
			for line in indexFile:
				try:
					record = json.loads(line)
				except (TypeError, ValueError):
					continue
				if not isinstance(record, dict):
					continue
				threadId = str(record.get("id") or "").strip().lower()
				if threadId not in targetIds:
					continue
				title = " ".join(str(record.get("thread_name") or "").split())
				if title:
					titles[threadId] = title
	result = []
	for threadId in threadIds:
		title = titles.get(threadId) or translate("Archived task {threadId}").format(threadId=threadId)
		result.append((threadId, title))
	return tuple(result)


def uniqueThreadLabels(entries, translate=lambda text: text):
	"""Give duplicate archived task titles distinct labels without losing their IDs."""
	result = []
	counts = {}
	used = set()
	for threadId, title in entries:
		base = " ".join(str(title or "").split()) or translate("Archived task {threadId}").format(threadId=threadId)
		count = counts.get(base, 0) + 1
		label = base if count == 1 else f"{base} ({count})"
		while label in used:
			count += 1
			label = f"{base} ({count})"
		counts[base] = count
		used.add(label)
		result.append((threadId, label))
	return tuple(result)


def codexThreadUrl(threadId):
	"""Return the native Codex deep link for a validated thread UUID."""
	threadId = str(threadId or "").strip().lower()
	if not re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", threadId):
		return ""
	return f"codex://threads/{threadId}"


def repairConfigurationValues(values, choiceDefaults, numericDefaults, booleanDefaults=(), stringDefaults=()):
	"""Repair imported or migrated configuration values in place."""
	repaired = []
	for key, (choices, default) in choiceDefaults.items():
		if values.get(key) not in choices:
			values[key] = default
			repaired.append(key)
	for key, (minimum, maximum, default) in numericDefaults.items():
		original = values.get(key, default)
		try:
			value = default if isinstance(original, bool) else int(original)
		except (TypeError, ValueError, OverflowError):
			value = default
		if value < minimum or value > maximum:
			value = default
		if original != value:
			repaired.append(key)
		values[key] = value
	for key, default in booleanDefaults:
		original = values.get(key, default)
		if isinstance(original, bool):
			value = original
		elif original in (0, 1):
			value = bool(original)
		elif isinstance(original, str) and original.strip().casefold() in ("true", "yes", "on", "1", "false", "no", "off", "0"):
			value = original.strip().casefold() in ("true", "yes", "on", "1")
		else:
			value = default
		if original != value:
			repaired.append(key)
		values[key] = value
	for key, default in stringDefaults:
		original = values.get(key, default)
		value = original.strip() if isinstance(original, str) else default
		if not value and default:
			value = default
		if original != value:
			repaired.append(key)
		values[key] = value
	return tuple(dict.fromkeys(repaired))


def chatTitleMatches(selectedTitle, buttonName, titleFoundInsideButton=False):
	"""Validate a sidebar title, including Chromium's unnamed-button structure."""
	selected = " ".join(str(selectedTitle or "").casefold().split())
	button = " ".join(str(buttonName or "").casefold().split())
	return bool(selected and (selected == button or (titleFoundInsideButton and not button)))


def isChatOptionsLabel(label):
	"""Recognize Chromium labels for a conversation's custom options button."""
	label = " ".join(str(label or "").casefold().split())
	return bool(
		label in ("more", "options", "chat options", "conversation options", "open conversation options")
		or label.endswith((" chat options", " conversation options"))
	)


def chatActionMatches(action, label):
	"""Match only the exposed action buttons for a focused sidebar chat."""
	action = str(action or "").strip().casefold()
	label = " ".join(str(label or "").casefold().split())
	if action == "pin":
		return label in ("pin chat", "unpin chat")
	if action == "archive":
		return label == "archive chat"
	return False


def voiceControlKind(label):
	"""Classify only native ChatGPT voice and microphone control labels."""
	label = " ".join(str(label or "").casefold().split())
	if label in ("start voice chat", "start voice mode"):
		return "start"
	if label in ("stop voice chat", "end voice chat", "leave voice mode", "exit voice mode"):
		return "stop"
	if label in ("mute microphone", "mute mic"):
		return "mute"
	if label in ("unmute microphone", "unmute mic"):
		return "unmute"
	return ""


def isPermissionPromptText(text):
	"""Identify permission/approval dialog wording without matching ordinary settings."""
	text = " ".join(str(text or "").casefold().split())
	return bool(
		any(phrase in text for phrase in (
			"permission required", "approval required", "requires your approval",
			"needs your approval", "allow this command", "allow codex", "approve this",
		))
		or ("permission" in text and any(word in text for word in ("allow", "deny", "approve", "reject")))
	)


def isPermissionDecisionLabel(label):
	"""Recognize a permission dialog decision control; focus only, never activate it."""
	label = " ".join(str(label or "").casefold().split())
	return bool(label and any(word in label for word in ("allow", "approve", "deny", "reject")))


def usageLimitNotice(text, translate=lambda text: text):
	"""Return a concise actionable notice for an exhausted ChatGPT usage allowance.

	The match deliberately requires exhaustion wording as well as ``usage limit``
	or ``credits``. This keeps help text and the normal usage-settings page from
	being mistaken for a terminal task error.
	"""
	text = re.sub(
		r"(?<=[a-z0-9%])(?=[A-Z])", " ",
		str(text or "").replace("\u2019", "'"),
	)
	text = " ".join(text.split())
	lower = text.casefold()
	remaining = re.search(r"\b(?P<percent>\d{1,3}(?:\.\d+)?)\s*%\s*usage\s+remaining", lower)
	consumed = re.search(r"\b(?P<percent>\d{1,3}(?:\.\d+)?)\s*%\s*usage\s+consumed", lower)
	percentageExhausted = bool(
		(remaining and float(remaining.group("percent")) <= 0)
		or (consumed and float(consumed.group("percent")) >= 100)
		or "no usage remaining" in lower
	)
	usageLimitReached = bool(
		percentageExhausted
		or "usage limit exceeded" in lower
		or re.search(r"\byou(?:'ve| have)\s+(?:hit|reached)\s+(?:your|the)\s+(?:\w+\s+){0,3}usage limit\b", lower)
		or re.search(r"\b(?:you are|you're)\s+out of\s+(?:chatgpt |codex )?usage\b", lower)
	)
	creditsExhausted = bool(
		("credit" in lower and re.search(
			r"\b(?:out of|not enough|insufficient|no)\s+(?:usage )?credits?\b", lower,
		))
		or re.search(r"\b0(?:\.0+)?\s+credits?\s+remaining\b", lower)
	)
	if not (usageLimitReached or creditsExhausted):
		return ""

	options = []
	if re.search(r"\bupgrade\s+(?:your\s+plan\s+)?to\s+pro\b", lower):
		options.append(translate("upgrade to Pro"))
	elif re.search(r"\bupgrade(?:\s+(?:your\s+)?plan)?\b", lower):
		options.append(translate("upgrade your plan"))
	if re.search(r"\b(?:add|buy|purchase)(?:\s+some)?(?:\s+more)?\s+credits?\b", lower):
		options.append(translate("purchase more credits in ChatGPT usage settings"))
	# A retry time runs to the end of its sentence, but decimal amounts such as
	# "2.5 hours" and clock suffixes such as "p.m." belong to the time. A suffix
	# followed by a capitalized word also ends the sentence.
	whenText = r"(?:\d+\.\d+|\b[ap]\.m\.(?!\s+(?-i:[A-Z]))|\b[ap]\.m|[^.!?])+"

	def whenPhrase(match):
		return re.sub(r"\b([ap])\.m$", r"\1.m.", match.group("when").strip(), flags=re.IGNORECASE)

	retry = re.search(
		r"\btry again\s+(?P<when>(?:at|in|after)\s+" + whenText + ")",
		text,
		flags=re.IGNORECASE,
	)
	if retry:
		options.append(translate("try again {when}").format(when=whenPhrase(retry)))
	else:
		reset = re.search(
			r"\b(?:usage|limit)\s+resets?\s+(?P<when>(?:at|in|after)\s+" + whenText + ")",
			text,
			flags=re.IGNORECASE,
		)
		if not reset:
			reset = re.search(
				r"\bnext reset\s+(?:is\s+)?(?P<when>(?:on|at|in|after)\s+.*?)"
				r"(?=\s+(?:usage consumed|add credits|buy credits|purchase credits|upgrade)\b|[.!?\u00b7]|$)",
				text,
				flags=re.IGNORECASE,
			)
		if reset:
			options.append(translate("try again {when}").format(when=whenPhrase(reset)))

	message = translate("Usage limit reached")
	if options:
		if len(options) == 1:
			actionText = options[0]
		elif len(options) == 2:
			actionText = translate("{first} or {last}").format(first=options[0], last=options[1])
		else:
			actionText = translate("{first}, {middle}, or {last}").format(
				first=options[0], middle=", ".join(options[1:-1]), last=options[-1],
			)
		notice = translate("{message}. You can {actions}.").format(message=message, actions=actionText)
		# A time such as "9 a.m." already ends with the sentence's full stop.
		return notice[:-1] if notice.endswith("..") else notice
	return translate("{message}. Check ChatGPT usage settings for reset details.").format(message=message)


def pluginInstallProgress(text, step=10):
	"""Parse and bucket a ChatGPT plug-in installation progress description."""
	text = " ".join(str(text or "").split())
	lower = text.casefold()
	if "install" not in lower or not any(word in lower for word in ("plugin", "plug-in", "connector", "extension")):
		return None
	match = re.search(r"(?<!\d)(100|[1-9]?\d)\s*%", lower)
	if not match:
		match = re.search(r"(?<!\d)(100|[1-9]?\d)\s+percent\b", lower)
	percent = int(match.group(1)) if match else None
	if percent is None and re.search(r"\b(?:complete|completed|finished|installed|succeeded)\b", lower):
		percent = 100
	step = max(1, min(100, int(step)))
	bucket = None if percent is None else (100 if percent == 100 else (percent // step) * step)
	identity = re.sub(r"(?<!\d)(100|[1-9]?\d)\s*(?:%|percent\b)", "", lower)
	identity = re.sub(r"\bin\s+progress\b", "", identity)
	identity = re.sub(
		r"\b(?:install|installing|installation|installed|progress|complete|completed|finished|succeeded)\b",
		"", identity,
	)
	identity = " ".join(identity.split()) or "plugin installation"
	return identity, percent, bucket


def pluginProgressBusyTransition(currentBusy, ownsBusyState, complete):
	"""Keep installation completion from clearing an unrelated active Codex task."""
	currentBusy = bool(currentBusy)
	ownsBusyState = bool(ownsBusyState)
	if complete:
		return (False, False) if ownsBusyState else (currentBusy, False)
	return True, bool(ownsBusyState or not currentBusy)


def pendingChatTitle(title, elapsed, timeout=10.0):
	"""Discard a stale history selection before a later unrelated document switch."""
	title = " ".join(str(title or "").split())
	return title if title and 0 <= float(elapsed) <= float(timeout) else ""


def formatElapsedDuration(totalSeconds, translate=lambda text: text):
	"""Format elapsed seconds as compact, speech-friendly hours, minutes, and seconds."""
	totalSeconds = max(0, int(round(float(totalSeconds or 0))))
	hours, remainder = divmod(totalSeconds, 3600)
	minutes, seconds = divmod(remainder, 60)
	parts = []
	if hours:
		label = translate("{count} hour") if hours == 1 else translate("{count} hours")
		parts.append(label.format(count=hours))
	if minutes:
		label = translate("{count} minute") if minutes == 1 else translate("{count} minutes")
		parts.append(label.format(count=minutes))
	if seconds or not parts:
		label = translate("{count} second") if seconds == 1 else translate("{count} seconds")
		parts.append(label.format(count=seconds))
	return " ".join(parts)


def currentActivitySummary(
	busy, category, latestMessage, elapsed=0, translate=lambda text: text, agentName="Codex",
):
	"""Return useful current activity even during a gap in exposed commentary."""
	agentName = " ".join(str(agentName or "Codex").split()) or "Codex"
	latestMessage = " ".join(str(latestMessage or "").split())
	if latestMessage:
		return latestMessage
	if not busy:
		return translate("{agent} is idle").format(agent=agentName)
	names = {
		"command": translate("running commands"), "build": translate("running tests"),
		"tool": translate("using tools"), "search": translate("searching"),
		"file": translate("working with files"), "thinking": translate("thinking"),
		"working": translate("working"), "commentary": translate("working"),
	}
	activity = names.get(str(category or "").casefold(), names["working"])
	elapsed = max(0, int(elapsed or 0))
	if elapsed:
		return translate("{agent} is still {activity}, {duration}").format(
			agent=agentName, activity=activity, duration=formatElapsedDuration(elapsed, translate),
		)
	return translate("{agent} is still {activity}").format(agent=agentName, activity=activity)


def backgroundActivityName(category, latestMessage=""):
	"""Return an accurate activity name for recurring background announcements."""
	category = str(category or "").casefold()
	text = " ".join(str(latestMessage or "").casefold().split())
	if any(word in text for word in ("finished", "complete", "updated", "done")):
		return "Processing"
	detectedCategory = statusDetails(latestMessage)[0]
	if detectedCategory and detectedCategory != "completion":
		category = detectedCategory
	if category == "file":
		if any(word in text for word in ("editing", "writing", "creating", "updating", "modifying", "patching")):
			return "Editing code"
		if any(word in text for word in ("checking", "reading", "inspecting", "reviewing")):
			return "Checking files"
		return "File operations"
	return {
		"command": "Command", "build": "Tests", "tool": "Tool operation",
		"search": "Web search", "thinking": "Thinking", "working": "Processing",
	}.get(category, "Work")


def looksLikeCodexConversation(text):
	"""Distinguish a conversation document from settings and transient viewers."""
	text = " ".join(str(text or "").casefold().split())
	return any(marker in text for marker in CHATGPT_PROMPT_LABELS)


def looksLikeBlankCodexConversation(text):
	"""Recognize a new blank conversation without mistaking a buffer refresh for one."""
	text = " ".join(str(text or "").casefold().split())
	if not looksLikeCodexConversation(text):
		return False
	return not (
		re.search(r"\buser message\s+\d+\b", text)
		or "response complete:" in text
		or any(f"{label}:" in text or f"{label} :" in text for label in CHAT_MESSAGE_SPEAKER_LABELS)
	)


def chatMessageSpeaker(label):
	"""Identify a speaker heading with or without whitespace before its colon."""
	text = " ".join(str(label or "").casefold().split())
	return CHAT_MESSAGE_SPEAKER_LABELS.get(text[:-1].rstrip(), "") if text.endswith(":") else ""


def chatMessageHeadingSpeaker(field, headingRole, focusableState):
	"""Identify Chromium's conversation headings using its accessible metadata."""
	if (
		headingRole is None or field.get("role") != headingRole or focusableState is None
		or "states" not in field or str(field.get("level")) != "4"
		or not CHAT_MESSAGE_HEADING_CLASSES.issubset(str(field.get(ATTACHMENT_POPUP_CLASS_KEY, "")).split())
	):
		return ""
	# The app uses tabindex=-1 only on assistant headings.
	return "assistant" if focusableState in (field.get("states") or ()) else "user"


def chatMessageShortcutIndex(keyName):
	"""Map Control+1 through Control+0 to newest-first chat message positions 1 through 10."""
	keyName = str(keyName or "").strip()
	if keyName == "0":
		return 10
	if keyName in tuple(str(number) for number in range(1, 10)):
		return int(keyName)
	return None


def isChatMessageTrailingUiText(text):
	"""Identify ChatGPT chrome that follows, but is not part of, a conversation turn."""
	text = " ".join(str(text or "").strip().casefold().split())
	if not text:
		return False
	if re.fullmatch(r"(?:(?:today|yesterday)\s+)?\d{1,2}:\d{2}(?:\s*[ap]m)?", text):
		return True
	if re.fullmatch(r"(?:working|worked|thinking)\s+for\s+\d+(?:\s*[hms]|\s*(?:hours?|minutes?|seconds?))(?:\s+\d+(?:\s*[hms]|\s*(?:hours?|minutes?|seconds?)))*", text):
		return True
	if re.fullmatch(r"edited\s+\d+\s+files?", text):
		return True
	if re.fullmatch(r"step\s+\d+\s*/\s*\d+", text):
		return True
	return text in {
		"good response", "bad response", "copy", "copy message", "retry", "edit message",
		"share", "more", "change permissions", "review", "review changed files", "undo",
		"open chat", "outputs", "sources", "view all", "thinking", "working",
		"running command", "reading finished", "command finished", "stop",
		"add files and more", "full access",
	}


class ChatMessageAccumulator:
	"""Incrementally retain only the newest complete conversation turns."""

	def __init__(self, limit=10):
		try:
			limit = max(1, int(limit))
		except (TypeError, ValueError, OverflowError):
			limit = 10
		self._messages = deque(maxlen=limit)
		self._currentSpeaker = ""
		self._parts = []
		# A turn whose only text matches interface wording, such as a user
		# message of "Stop", is held here until the next token shows whether it
		# was the message itself or chrome before the message text.
		self._interfaceCandidate = None

	def _finish(self):
		if not self._parts and self._interfaceCandidate is not None:
			self._parts = [self._interfaceCandidate]
		self._interfaceCandidate = None
		text = " ".join("".join(self._parts).split())
		if self._currentSpeaker and text:
			item = (self._currentSpeaker, text)
			if not self._messages or self._messages[-1] != item:
				self._messages.append(item)
		self._parts = []

	def feed(self, token):
		try:
			kind, value = token
		except (TypeError, ValueError):
			return
		kind = str(kind or "").strip().casefold()
		rawValue = str(value or "")
		value = " ".join(rawValue.split())
		if kind == "speaker" and value in ("user", "assistant"):
			if value != self._currentSpeaker or self._parts or self._interfaceCandidate is not None:
				self._finish()
			self._currentSpeaker = value
		elif kind == "text" and self._currentSpeaker and value:
			if isResponseCompletionMarkerText(value) or chatMessageSpeaker(value):
				return
			if isChatMessageTrailingUiText(value):
				if self._parts or self._interfaceCandidate is not None:
					# Interface text after message text, or two interface labels in a
					# row, is chrome that ends the turn.
					if not self._parts:
						self._interfaceCandidate = None
					self._finish()
					self._currentSpeaker = ""
				else:
					self._interfaceCandidate = rawValue
			else:
				self._interfaceCandidate = None
				self._parts.append(rawValue)
		elif kind == "end":
			self._finish()
			self._currentSpeaker = ""

	def messages(self):
		self._finish()
		return tuple(self._messages)


class ChatMessageFieldCollector:
	"""Convert virtual-buffer fields into tokens from the active branch before its prompt."""

	def __init__(
		self, interactiveRoles, editableRole, promptLabelPredicate, invisibleStates=(), stopAtPrompt=True,
		*, headingRole=None, focusableState=None, promptIdentifier=None,
	):
		self._interactiveRoles = frozenset(interactiveRoles or ())
		self._editableRole = editableRole
		self._promptLabelPredicate = promptLabelPredicate
		self._invisibleStates = frozenset(invisibleStates or ())
		self._stopAtPrompt = bool(stopAtPrompt)
		self._headingRole = headingRole
		self._focusableState = focusableState
		self._promptIdentifier = tuple(map(str, promptIdentifier)) if promptIdentifier else None
		self._ignoredDepth = 0
		self.promptReached = False
		self.done = False

	def feed(self, item):
		if self.done:
			return ()
		if isinstance(item, str):
			if self._ignoredDepth:
				return ()
			speaker = chatMessageSpeaker(item)
			if speaker:
				return (("speaker", speaker),)
			if not isResponseCompletionMarkerText(item):
				return (("text", item),)
			return ()
		command = getattr(item, "command", "")
		field = getattr(item, "field", {}) or {}
		if command == "controlStart":
			if self._ignoredDepth:
				self._ignoredDepth += 1
				return ()
			role = field.get("role")
			states = field.get("states", ()) or ()
			hidden = bool(
				self._invisibleStates.intersection(states)
				or field.get("hidden") is True
				or str(field.get("aria-hidden", "")).casefold() == "true"
			)
			if hidden:
				self._ignoredDepth = 1
				return ()
			headingSpeaker = chatMessageHeadingSpeaker(field, self._headingRole, self._focusableState)
			if headingSpeaker:
				# Skip the localized heading text so it cannot become part of the message.
				self._ignoredDepth = 1
				return (("speaker", headingSpeaker),)
			name = " ".join(str(field.get("name", "") or "").split())
			promptLabels = (
				name,
				" ".join(str(field.get("placeholder", "") or "").split()),
				" ".join(str(field.get("description", "") or "").split()),
			)
			if role == self._editableRole and (
				(self._promptIdentifier is not None and self._promptIdentifier == (
					str(field.get("controlIdentifier_docHandle")), str(field.get("controlIdentifier_ID")),
				))
				or any(self._promptLabelPredicate(label) for label in promptLabels if label)
			):
				self.promptReached = True
				if self._stopAtPrompt:
					self.done = True
				return (("end", ""),)
			tokens = []
			speaker = chatMessageSpeaker(name)
			if speaker:
				tokens.append(("speaker", speaker))
			if role in self._interactiveRoles:
				self._ignoredDepth = 1
				if role == self._editableRole:
					tokens.append(("end", ""))
			return tuple(tokens)
		if command == "controlEnd" and self._ignoredDepth:
			self._ignoredDepth -= 1
		return ()


def mergeConversationTail(existing, tail):
	"""Join turns from a bounded newest-text scan onto earlier cached turns.

	The first tail turn may have started before the scanned range, so it is
	dropped as possibly incomplete. The remaining turns are aligned with the
	cache; without an overlap the tail alone is the safest current view.
	"""
	existing = tuple(existing or ())
	tail = tuple(tail or ())[1:]
	if not tail:
		return existing
	for start in range(len(existing)):
		count = min(len(existing) - start, len(tail))
		if existing[start:start + count] == tail[:count]:
			return existing[:start] + tail
	return tail


def chatMessagesFromTokens(tokens, limit=10):
	"""Build bounded conversation turns from accessibility-order speaker and text tokens."""
	accumulator = ChatMessageAccumulator(limit)
	for token in tokens or ():
		accumulator.feed(token)
	return accumulator.messages()


class AnnouncementHistory:
	"""A bounded, in-memory announcement history with review navigation."""

	def __init__(self, limit=20):
		self._items = deque(maxlen=limit)
		self._index = -1

	def add(self, message):
		message = str(message or "").strip()
		if not message or (self._items and self._items[-1] == message):
			return False
		self._items.append(message)
		self._index = len(self._items) - 1
		return True

	def move(self, offset):
		if not self._items:
			return ""
		self._index = min(max(self._index + offset, 0), len(self._items) - 1)
		return self._items[self._index]

	def clear(self):
		self._items.clear()
		self._index = -1

	def items(self):
		return tuple(self._items)

	def __len__(self):
		return len(self._items)

CATEGORY_SETTING = {"thinking": "announceThinking", "working": "announceWorking", "command": "announceCommands", "search": "announceSearches", "file": "announceFiles", "build": "announceBuilds", "tool": "announceTools", "completion": "announceCompletions", "attention": "announceAttention", "other": "announceOther", "commentary": "announceCommentary"}

TONE_PATTERNS = {
	"thinking": ((392, 45), (440, 45)),
	"working": ((440, 45),),
	"command": ((523, 55), (659, 65)),
	"search": ((659, 50), (784, 60)),
	"file": ((494, 45), (587, 55)),
	"build": ((587, 55), (698, 70)),
	"tool": ((698, 55),),
	"completion": ((659, 55), (784, 55), (988, 85)),
	"failure": ((659, 65), (523, 65), (392, 100)),
	"other": ((392, 50),),
	"commentary": ((554, 45),),
	"attention": ((784, 70), (988, 100)),
	"backgroundPulse1": ((392, 35), (523, 55)),
	"backgroundPulse2": ((440, 35), (587, 55)),
	"monitoringActive": ((523, 45), (784, 65)),
	"monitoringInactive": ((587, 45), (392, 70)),
	"submission": ((523, 40), (659, 50), (784, 65)),
}


def isFailureText(text):
	"""Return whether status text reports a failure, error, or cancellation.

	Counts of zero, such as "0 errors" or "no failures", report success.
	"""
	text = " ".join(str(text or "").casefold().split())
	text = re.sub(r"\b(?:0|no|zero)\s+(?:errors?|failures?|failed)\b", "", text)
	return any(word in text for word in ("fail", "error", "cancel"))


def startsWithWord(text, words):
	"""Return whether text begins with one of the words as a whole word.

	A hyphen continues the word, so "Built-in tools" does not start with "built".
	"""
	pattern = r"(?:" + "|".join(re.escape(word) for word in words) + r")(?=$|[\s:;,.!?)])"
	return re.match(pattern, text) is not None


def tonePattern(category, message=""):
	"""Return a short earcon pattern for a progress category and message."""
	if category == "completion" and isFailureText(message):
		return TONE_PATTERNS["failure"]
	return TONE_PATTERNS.get(category, TONE_PATTERNS["other"])


def soundKey(category, message=""):
	"""Return the bundled click-earcon name for a category and message."""
	if category == "completion" and isFailureText(message):
		return "failure"
	return category if category in TONE_PATTERNS else "other"


def userMessageNumber(label):
	"""Return the number from a Codex 'Jump to user message' control."""
	match = re.search(r"(?i)\bjump to user message\s+(\d+)\b", str(label or ""))
	return int(match.group(1)) if match else None


def userMessageSubmissionTransition(previousNumber, currentNumber):
	"""Detect a newly posted user message without firing on the initial baseline."""
	if currentNumber is None:
		return previousNumber, False
	return currentNumber, previousNumber is not None and currentNumber > previousNumber


def confirmedUserMessageSubmission(pendingIncrease, messageNumberIncreased, stopControlVisible):
	"""Retain and confirm a message-count increase once active work is visible.

	Loading a different Codex task can expose a larger historical user-message
	count.  The active Stop/Cancel control distinguishes that navigation change
	from a request that ChatGPT is currently processing. Retaining an increase
	also covers Chromium exposing the new message one scan before the Stop control.
	"""
	pending = bool(pendingIncrease or messageNumberIncreased)
	confirmed = bool(pending and stopControlVisible)
	return False if confirmed else pending, confirmed


def isStopControlLabel(label):
	"""Return whether a button is the active-task stop or cancel control."""
	lower = " ".join(str(label or "").lower().split())
	return lower in ("stop", "stop generating", "cancel", "cancel task", "cancel request")


def stopControlTransition(previousVisible, currentVisible):
	"""Detect disappearance of a previously visible task stop control."""
	currentVisible = bool(currentVisible)
	return currentVisible, bool(previousVisible and not currentVisible)


def shouldSuppressDuplicate(message, previousMessage, elapsedSeconds, windowSeconds=1.5):
	"""Suppress rapid duplicate accessibility events without hiding later updates."""
	return bool(message == previousMessage and float(elapsedSeconds) < float(windowSeconds))


def semanticStatusKey(message):
	"""Collapse cosmetic wording differences into a stable activity key."""
	text = " ".join(str(message or "").casefold().split())
	replacements = (
		("editing file", "editing code"), ("editing source", "editing code"),
		("reading files", "checking files"), ("reading", "checking files"),
		("file edit finished", "file updated"), ("changes finished", "file updated"),
		("build or test still running", "tests still running"),
	)
	for old, new in replacements:
		if text.startswith(old):
			text = new + text[len(old):]
	return text


def shouldSuppressSemanticDuplicate(message, previousMessage, elapsedSeconds, windowSeconds=1.5):
	return bool(
		semanticStatusKey(message)
		and semanticStatusKey(message) == semanticStatusKey(previousMessage)
		and float(elapsedSeconds) < float(windowSeconds)
	)


def duplicateChannelActions(speechMessage, brailleMessage, previousSpeech, previousBraille, speechElapsed, brailleElapsed):
	"""Resolve duplicate suppression independently for speech and Braille."""
	return {
		"speech": bool(speechMessage) and shouldSuppressSemanticDuplicate(
			speechMessage, previousSpeech, speechElapsed,
		),
		"braille": bool(brailleMessage) and shouldSuppressSemanticDuplicate(
			brailleMessage, previousBraille, brailleElapsed,
		),
	}


def formatCommandSpeech(message, punctuation="normal", maximumCharacters=240):
	"""Prepare long command text for speech without changing stored or braille text."""
	text = str(message or "")
	if punctuation == "enhanced":
		text = text.replace("&&", " and then ").replace("||", " or else ").replace("|", " pipe ")
		text = text.replace(">>", " append to ").replace(">", " redirect to ")
	elif punctuation == "literal":
		for symbol, word in (("&&", " ampersand ampersand "), ("||", " pipe pipe "), ("|", " pipe "), (">", " greater than "), ("<", " less than ")):
			text = text.replace(symbol, word)
	text = " ".join(text.split())
	maximumCharacters = max(40, int(maximumCharacters or 240))
	if len(text) <= maximumCharacters:
		return text, False
	return text[:maximumCharacters].rstrip(" ,;:-") + "…", True


def shouldLogDiagnosticSnapshot(snapshot, previousSnapshot, elapsedSeconds, repeatSeconds=30.0):
	"""Log changed diagnostic data immediately and unchanged data only periodically."""
	snapshot = tuple(snapshot or ())
	return bool(snapshot and (snapshot != tuple(previousSnapshot or ()) or float(elapsedSeconds) >= float(repeatSeconds)))


def isResponseCompletionMarkerText(text):
	"""Return whether virtual-buffer text is ChatGPT's completed-response marker."""
	normalized = " ".join(str(text or "").casefold().split())
	return normalized == "response complete" or normalized.startswith("response complete:")


def responseCompletionScanMarker(markerCount, latestDetailedFingerprint=None):
	"""Create privacy-safe scan state that changes when another response completes."""
	count = max(0, int(markerCount or 0))
	if not count:
		return None
	return count, latestDetailedFingerprint


def responseCompletionTransition(previousMarker, initialized, currentMarker, busy):
	"""Detect a new completed-response marker after establishing a buffer baseline."""
	if currentMarker is None:
		return previousMarker, True, False
	completed = bool(initialized and busy and currentMarker != previousMarker)
	return currentMarker, True, completed


def shouldFinalizeResponseCompletion(pending, elapsedSeconds, settleSeconds, busy, stopControlVisible, activityLabel):
	"""Finalize a tentative response only after a quiet, explicitly idle scan."""
	normalizedLabel = " ".join(str(activityLabel or "").lower().split())
	operationFinished = bool(
		intermediateCompletionCategory(activityLabel)
		and any(word in normalizedLabel for word in ("finished", "complete", "succeeded", "failed", "passed"))
	)
	labelIsQuiet = (
		not normalizedLabel
		or statusDetails(activityLabel)[0] == "completion"
		or operationFinished
	)
	return bool(
		pending
		and busy
		and not stopControlVisible
		and labelIsQuiet
		and float(elapsedSeconds) >= float(settleSeconds)
	)


def isTaskCompletionLabel(label):
	"""Distinguish whole-task completion from an intermediate operation finishing."""
	lower = " ".join(str(label or "").lower().split())
	return lower.startswith("response complete") or startsWithWord(
		lower, ("finished", "completed", "done", "cancelled", "canceled"),
	)


def shouldSuppressTrailingCompletion(category, busy, lastStateReason, label=""):
	"""Ignore old success cues after task end, but never hide a failure."""
	if category != "completion" or busy or lastStateReason != "completion":
		return False
	return not isFailureText(label)


def supersedesResponseCompletionCandidate(label):
	"""Return whether a new activity label proves that a tentative response completion is stale."""
	category, _message = statusDetails(label)
	return bool(category and category != "completion")


def intermediateCompletionCategory(label):
	"""Map an operation completion back to the activity category it belongs to."""
	lower = " ".join(str(label or "").lower().split())
	if startsWithWord(lower, ("ran",)) or "command" in lower or "process" in lower:
		return "command"
	if "search" in lower and ("web" in lower or "internet" in lower):
		return "search"
	if startsWithWord(lower, ("compiled", "transpiled", "generated", "built")):
		return "build"
	if lower.startswith(("file edit", "file editing", "file edited")) or startsWithWord(lower, (
		"wrote", "created", "edited", "updated", "modified", "applied", "patched", "read", "inspected", "reviewed",
	)):
		return "file"
	return ""


def isKnownNonStatusButton(label):
	"""Filter stable Codex controls that are not progress statuses."""
	text = " ".join(str(label or "").lower().split())
	return bool(
		userMessageNumber(text) is not None
		or promptControlKind(text)
		or voiceControlKind(text)
		or text in (
			"outputs", "sources", "view all", "copy", "copy message", "retry", "edit", "share", "more",
			"fork chat from here", "scroll to bottom", "add files and more", "dictate", "send",
			"review", "review changed files", "undo", "open chat", "edit message",
		)
		or re.fullmatch(r"worked for (?:\d+h )?(?:\d+m )?\d+s", text) is not None
		or text.startswith("download codex status announcer ")
		or re.fullmatch(r"show \d+ more files?", text) is not None
		or re.search(r"\+\d+-\d+$", text) is not None
	)


def isChatHistoryInterfaceText(label):
	"""Identify non-history controls that must never become chat titles."""
	text = " ".join(str(label or "").casefold().split())
	if not text:
		return False
	return bool(
		isKnownNonStatusButton(text)
		or isChatMessageTrailingUiText(text)
		or re.fullmatch(r"(?:sources?|outputs?)(?:\s+\d+|\s*\(\d+\))?", text)
		or re.fullmatch(r"(?:copy|share) (?:response|message|link)", text)
		or re.fullmatch(r"\d{1,3}% usage remaining", text)
		or text.startswith(("resets every ", "next reset "))
		or text in (
			"read aloud", "stop reading", "regenerate", "regenerate response",
			"branch in new chat", "like", "dislike", "thumbs up", "thumbs down",
			"report", "copy code", "copy code to clipboard", "share chat",
			"more actions", "more options", "open message actions", "previous response", "next response",
			"show more", "show less", "loading", "loading…",
			"dismiss usage alert", "usage consumed", "view usage", "add credits", "buy credits",
			"purchase credits", "manage plan", "manage subscription", "my plan", "upgrade",
			"upgrade plan", "upgrade to pro", "update", "update now", "install update",
			"restart to update", "manage account", "settings", "help", "log out", "sign out",
		)
	)


def isChatHistoryConversationBoundary(label):
	"""Identify conversation or account content following the sidebar chat list."""
	text = " ".join(str(label or "").casefold().split())
	return bool(
		userMessageNumber(text) is not None
		or chatMessageSpeaker(text)
		or text in ("dismiss usage alert", "usage consumed")
		or re.fullmatch(r"\d{1,3}% usage remaining", text)
		or text.startswith(("resets every ", "next reset "))
	)


def promptControlKind(name):
	"""Classify stable and dynamic prompt-toolbar control names."""
	text = " ".join(str(name or "").casefold().split())
	if text == ADD_FILES_BUTTON_NAME.casefold() or text.startswith((
		"add files", "attach files", "upload files", "add photos", "add images",
	)):
		return "files"
	if text == "change permissions" or ("permission" in text and text.startswith(("change", "select", "choose"))):
		return "permissions"
	if text in (
		"model", "select model", "choose model", "change model",
		"model and reasoning", "model and reasoning effort",
		"select model and reasoning", "choose model and reasoning",
	):
		return "model"
	# The desktop picker can expose either a full GPT-prefixed name or a short
	# label such as "6 Sol Light" or "Astra Light". Match the whole control name:
	# a progress heading that happens to mention a model is not a picker.
	if re.fullmatch(
		r"(?:(?:gpt[- ]?)?\d+(?:\.\d+)?[- ]+(?:astra|sol|luna|terra|developer)"
		r"|(?:astra|sol|luna|terra))"
		r"(?:[- ]+(?:light|medium|high|extra high|xhigh|max|ultra|fast|standard|ultrafast))?",
		text,
	):
		return "model"
	if re.fullmatch(r"o[1345](?:[- ]+[a-z0-9]+)*", text):
		return "model"
	if text in ("codex model", "reasoning model"):
		return "model"
	return ""


def attachmentPopupOptions(tokens, isPromptField, isOptionField):
	"""Read the Add files and more popup from virtual-buffer tokens.

	``tokens`` are ``("start", field)``, ``("end", None)``, or ``("text", value)``.
	The popup is the outermost container of its "Type to search" text that does
	not also contain the prompt. Some ChatGPT versions have no such text; their
	popup is found from its last row, marked with ChatGPT's row class. Text outside option buttons is a section header,
	such as Add, Plugins, or Apps. Each option button's text chunks are its title
	followed by an optional description. Returns dictionaries with ``section``,
	``title``, ``description``, and the button's ``field``.
	"""
	root = {"field": None, "children": [], "parent": None}
	current = root
	promptNode = None
	hintNode = None
	lastRowNode = None
	for kind, value in tokens:
		if kind == "start":
			node = {"field": value or {}, "children": [], "parent": current}
			current["children"].append(node)
			current = node
			if promptNode is None and isPromptField(node["field"]):
				promptNode = node
			if ATTACHMENT_POPUP_ROW_CLASS in str(node["field"].get(ATTACHMENT_POPUP_CLASS_KEY, "") or ""):
				lastRowNode = node
		elif kind == "end":
			if current["parent"] is not None:
				current = current["parent"]
		elif kind == "text":
			# Keep the raw text: rows below the visible area can reach NVDA split
			# mid-word, so their pieces are joined exactly as they were sent.
			raw = str(value or "")
			text = " ".join(raw.split())
			if not text:
				continue
			current["children"].append(raw)
			if "type to search" in text.casefold():
				# The popup is added last, so the final match belongs to it.
				hintNode = current
	if hintNode is None:
		hintNode = lastRowNode
	if hintNode is None:
		return ()

	def contains(node, target):
		while target is not None:
			if target is node:
				return True
			target = target["parent"]
		return False

	path = []
	node = hintNode
	while node is not None:
		path.append(node)
		node = node["parent"]
	container = next(
		(node for node in reversed(path) if node is not root and not (promptNode and contains(node, promptNode))),
		hintNode,
	)
	options = []
	section = [""]

	def textChunks(node):
		chunks = []
		for child in node["children"]:
			if isinstance(child, str):
				chunks.append(child)
			else:
				chunks.extend(textChunks(child))
		return chunks

	def classNames(node):
		return str(node["field"].get(ATTACHMENT_POPUP_CLASS_KEY, "") or "").split()

	def subtreeUsesRowClasses(node):
		for child in node["children"]:
			if isinstance(child, str):
				continue
			names = " ".join(classNames(child))
			if ATTACHMENT_POPUP_ROW_CLASS in names or ATTACHMENT_POPUP_HEADER_CLASS in names:
				return True
			if subtreeUsesRowClasses(child):
				return True
		return False

	# ChatGPT marks every keyboard row, including ones that are not buttons such
	# as "Attach appshot", with the same row class, and headings with a header
	# class. Prefer those markers; fall back to roles for other layouts.
	useClasses = subtreeUsesRowClasses(container)

	def addOption(node):
		full = " ".join("".join(textChunks(node)).split())
		name = " ".join(str(node["field"].get("name", "") or "").split())
		if name:
			title, description = name, ("" if full == name else full)
		else:
			title, description = splitRunTogetherTitle(full)
		if title and "type to search" not in title.casefold():
			sectionIndex = sum(1 for option in options if option["section"] == section[0])
			options.append({
				"section": section[0], "title": title, "description": description,
				"sectionIndex": sectionIndex,
				"field": node["field"], "classBased": useClasses,
				"highlighted": ATTACHMENT_POPUP_HIGHLIGHT_CLASS in classNames(node),
			})

	def walk(node):
		for child in node["children"]:
			if isinstance(child, str):
				if not useClasses and "type to search" not in child.casefold():
					section[0] = " ".join(child.split())
				continue
			names = " ".join(classNames(child))
			if useClasses:
				if ATTACHMENT_POPUP_HEADER_CLASS in names:
					headerText = " ".join("".join(textChunks(child)).split())
					if headerText:
						section[0] = headerText
					continue
				if ATTACHMENT_POPUP_ROW_CLASS in names:
					addOption(child)
					continue
			elif isOptionField(child["field"]):
				addOption(child)
				continue
			walk(child)

	walk(container)
	for index, option in enumerate(options):
		option["index"] = index
	return tuple(options)


def attachmentPopupOptionsFromRows(rows):
	"""Build popup options from UI Automation rows of ``(className, name, texts)``.

	Used when NVDA's document does not carry class names, as in its UI
	Automation document mode. Rows and headings are recognized by the same
	ChatGPT class names as in the virtual buffer.
	"""
	options = []
	section = ""
	for className, name, texts in rows:
		classText = str(className or "")
		textParts = [" ".join(str(text).split()) for text in texts or () if str(text or "").strip()]
		if ATTACHMENT_POPUP_HEADER_CLASS in classText:
			section = " ".join(str(name or "").split()) or " ".join(textParts)
			continue
		if ATTACHMENT_POPUP_ROW_CLASS not in classText:
			continue
		fullName = " ".join(str(name or "").split())
		if len(textParts) >= 2:
			title, description = textParts[0], " ".join(textParts[1:])
		elif len(textParts) == 1 and fullName.endswith(textParts[0]) and fullName != textParts[0]:
			# The "/" menu splits each title into one piece per letter for match
			# highlighting; only the description is a whole text piece.
			title, description = fullName[:-len(textParts[0])].strip(), textParts[0]
		else:
			title, description = splitRunTogetherTitle(" ".join(str(name or "").split()) or " ".join(textParts))
		if not title or "type to search" in title.casefold():
			continue
		options.append({
			"section": section, "title": title, "description": description,
			"sectionIndex": sum(1 for option in options if option["section"] == section),
			"field": {}, "classBased": True,
			"highlighted": ATTACHMENT_POPUP_HIGHLIGHT_CLASS in classText.split(),
		})
	for index, option in enumerate(options):
		option["index"] = index
	return tuple(options)


# The highlighted row has this exact class token; every row also has the
# "focus:bg-primary-ghost-hover" variant, which is a different token.


def findAttachmentOption(options, wanted):
	"""Find a chosen option again in a fresh read of the popup.

	Rows are matched by their text, ignoring spacing. A row whose text changed,
	such as "Attach The Chat Place" becoming "Attach appshot", is matched by its
	position within the same section, then by its overall position.
	"""
	wantedKey = attachmentOptionKey(wanted)
	for index, option in enumerate(options):
		if attachmentOptionKey(option) == wantedKey and option.get("section") == wanted.get("section"):
			return index
	for index, option in enumerate(options):
		if attachmentOptionKey(option) == wantedKey:
			return index
	if wanted.get("sectionIndex") is not None:
		for index, option in enumerate(options):
			if option.get("section") == wanted.get("section") and option.get("sectionIndex") == wanted["sectionIndex"]:
				return index
	if wanted.get("index") is not None and 0 <= wanted["index"] < len(options):
		return wanted["index"]
	return None


def promptTextAddition(before, after, maximumCharacters=60):
	"""Return the short text a chosen option added to the prompt, if any."""
	before = " ".join(str(before or "").split())
	after = " ".join(str(after or "").split())
	if not after or after == before:
		return ""
	if not before:
		added = after
	elif before in after:
		added = after.replace(before, "", 1).strip()
	else:
		return ""
	return added if 0 < len(added) <= maximumCharacters else ""


def attachmentOptionKeyStep(options, wanted):
	"""Return the next key to reach the wanted option, "tab" to choose it, or "" if unknown.

	``options`` carry a ``highlighted`` flag read from the popup. Without a
	highlighted row the caller must fall back to counting from the first row.
	"""
	highlighted = next((index for index, option in enumerate(options) if option.get("highlighted")), None)
	target = findAttachmentOption(options, wanted)
	if highlighted is None or target is None:
		return ""
	if highlighted == target:
		return "tab"
	return "downArrow" if highlighted < target else "upArrow"


def splitRunTogetherTitle(text):
	"""Split a popup row's text into title and description where that is reliable.

	ChatGPT renders a title and description in adjacent elements, which reach
	NVDA as one run such as "GitHubTriage PRs" or "Plan modeTurn plan mode on".
	Conversation rows end in "ChatGPT conversation" and site rows end in a
	".chatgpt.site" address, so those suffixes are split exactly. Otherwise a
	split is made where a capitalized word begins, only if that word has no
	further case change, the description has at least two words, and the title
	looks like a name of at most four words, such as "Work in a project". Text
	such as "AirPlay During Calls" or "Review and manage GitHub" stays whole.
	"""
	text = " ".join(str(text or "").split())
	conversation = re.fullmatch(r"(?P<title>.+?)\s*(?P<description>ChatGPT conversation)", text)
	if conversation:
		return conversation.group("title"), conversation.group("description")
	if re.search(r"\.chatgpt\.site$", text):
		# A site's address starts with its own name, as in "Crossroads" followed by
		# "crossroads-audio-city.example.chatgpt.site".
		for position in range(1, len(text)):
			title = text[:position].strip()
			slug = re.sub(r"[^a-z0-9]+", "-", title.casefold()).strip("-")
			address = text[position:].strip()
			if slug and address.startswith(slug) and re.fullmatch(r"[a-z0-9][a-z0-9.-]*\.chatgpt\.site", address):
				return title, address
		return text, ""
	for match in re.finditer(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", text):
		position = match.start()
		word = re.match(r"[A-Za-z]+", text[position:]).group(0)
		if not re.fullmatch(r"[A-Z][a-z]+", word):
			continue
		title, description = text[:position].strip(), text[position:].strip()
		if len(description.split()) < 2:
			continue
		titleWords = title.split()
		if len(titleWords) > 4 or sum(1 for titleWord in titleWords if titleWord[:1].islower()) > 3:
			continue
		return title, description
	return text, ""


def attachmentOptionKey(option):
	"""Compare popup rows ignoring spacing, punctuation, and capitalization."""
	return re.sub(r"\W+", "", "{0}{1}".format(option.get("title", ""), option.get("description", ""))).casefold()


def withAttachmentOptionTitles(options, exactOptions):
	"""Use exact titles and descriptions from a second reading of the same rows.

	NVDA's document joins a row's title and description into one run, which
	cannot always be split, as in "Code Review Review and manage GitHub pull
	requests". UI Automation keeps them apart. Titles are taken only when both
	readings list the same rows in the same sections; otherwise ``options`` is
	returned unchanged.
	"""
	if not exactOptions or len(exactOptions) != len(options):
		return tuple(options)
	if any(
		attachmentOptionKey(option) != attachmentOptionKey(exact) or option.get("section") != exact.get("section")
		for option, exact in zip(options, exactOptions)
	):
		return tuple(options)
	return tuple(
		dict(option, title=exact["title"], description=exact["description"])
		for option, exact in zip(options, exactOptions)
	)


def attachmentPopupStructureSummary(tokens, isPromptField, limit=80):
	"""Summarize the controls after the prompt for the NVDA log: roles and ChatGPT row classes only.

	Used when the Add files and more popup cannot be found, to show what the
	page contains instead. Names and text are never included.
	"""
	afterPrompt = False
	counts = {}
	order = []
	for kind, value in tokens:
		if kind != "start":
			continue
		field = value or {}
		if not afterPrompt:
			afterPrompt = bool(isPromptField(field))
			continue
		role = field.get("role")
		roleName = str(getattr(role, "name", role) or "none").casefold()
		classes = str(field.get(ATTACHMENT_POPUP_CLASS_KEY, "") or "")
		marks = [
			mark for mark, className in (
				("row", ATTACHMENT_POPUP_ROW_CLASS), ("header", ATTACHMENT_POPUP_HEADER_CLASS),
				("highlighted", ATTACHMENT_POPUP_HIGHLIGHT_CLASS),
			)
			if className in classes.split() or (mark != "highlighted" and className in classes)
		]
		key = roleName + ("[" + ",".join(marks) + "]" if marks else "")
		if key not in counts:
			order.append(key)
		counts[key] = counts.get(key, 0) + 1
		if sum(counts.values()) >= limit:
			break
	if not afterPrompt:
		return "prompt not found"
	if not counts:
		return "no controls after the prompt"
	return ", ".join("{0} x{1}".format(key, counts[key]) for key in order)


def attachmentOptionLabel(option):
	"""Title first for first-letter navigation, then description and section."""
	label = option.get("title", "")
	if option.get("description"):
		label += " — " + option["description"]
	if option.get("section"):
		label += f" ({option['section']})"
	return label


def attachmentMenuItemLabel(active, roleName, name="", value="", description=""):
	"""Return usable text only for a control in the active attachment popup."""
	if not active:
		return ""
	roleName = "".join(str(roleName or "").casefold().split())
	if roleName not in {
		"button", "checkbutton", "checkbox", "listitem", "menu", "menuitem",
		"radiobutton", "togglebutton",
	}:
		return ""
	# Chromium can keep focus on the exact Add files and more button and expose
	# the selected descendant through its value. Do not mistake that button's help
	# description for an item label. Labels such as "Upload files" remain valid
	# popup choices even though the toolbar classifier also recognizes them.
	if " ".join(str(name or "").casefold().split()) == "add files and more":
		candidates = (value,)
	else:
		candidates = (name, value, description)
	for candidate in candidates:
		text = " ".join(str(candidate or "").split())
		if text and text.casefold() != "add files and more":
			return text
	return ""


ATTACHMENT_DIAGNOSTIC_NAMED_TYPES = frozenset(("menu", "menuitem", "checkbox", "radiobutton"))


def attachmentDiagnosticLines(elements, baseline=None, limit=60):
	"""Summarize popup candidates for a support report without exposing chat text.

	Each element is ``(controlType, name, ariaRole, className, offscreen)``. Without
	a baseline, names are reported only for menu-like controls. With a baseline
	captured before the menu opened, only newly appeared elements are listed.
	"""
	elements = tuple(elements or ())
	counts = {}
	for element in elements:
		counts[element[0]] = counts.get(element[0], 0) + 1
	lines = ["UIA candidate counts: " + (
		", ".join(f"{kind} {count}" for kind, count in sorted(counts.items())) or "none"
	)]
	if baseline is None:
		listed = [element for element in elements if element[0] in ATTACHMENT_DIAGNOSTIC_NAMED_TYPES]
		lines.append(f"Menu-like elements: {len(listed)} (no baseline before opening)")
	else:
		baselineKeys = {tuple(element[:4]) for element in baseline}
		listed = [element for element in elements if tuple(element[:4]) not in baselineKeys]
		lines.append(f"New since Add files and more was focused: {len(listed)}")
	for controlType, name, ariaRole, className, offscreen in listed[:max(0, int(limit))]:
		name = redactSensitive(" ".join(str(name or "").split()))[:60]
		lines.append("  {kind}: {name}; aria role {aria}; class {cls}; {visibility}".format(
			kind=controlType, name=name or "(no name)", aria=ariaRole or "none",
			cls=" ".join(str(className or "").split())[:60] or "none",
			visibility="offscreen" if offscreen else "onscreen",
		))
	if len(listed) > limit:
		lines.append(f"  … {len(listed) - limit} more")
	return tuple(lines)


def categoryOutputActions(mode, speechEnabled=True, brailleEnabled=True, soundEnabled=True):
	"""Resolve a category output mode through the global master switches."""
	mode = mode if mode in ("all", "speech", "sound", "braille", "off") else "all"
	return {
		"speech": bool(speechEnabled and mode in ("all", "speech")),
		"braille": bool(brailleEnabled and mode in ("all", "braille")),
		"sound": bool(soundEnabled and mode in ("all", "sound")),
	}


def shouldSuppressRoutineBraille(
	protectReading, appFocused, category, priority="normal", browseMode=False,
):
	"""Keep routine background output from replacing a Braille line being read in ChatGPT."""
	routineCategories = {
		"thinking", "working", "command", "search", "file", "build", "tool", "commentary",
		"backgroundPulse1", "backgroundPulse2",
	}
	if not (protectReading and appFocused):
		return False
	priority = str(priority or "normal")
	category = str(category or "")
	if priority == "urgent" or category == "attention":
		return False
	if browseMode and category == "completion":
		return True
	return category in routineCategories and priority != "high"


def shouldSuppressNativeConversationUpdate(
	protectReading, appFocused, browseMode, inConversation, inPopup, text,
):
	"""Keep ordinary streamed response updates from replacing active reading.

	Permission and approval text is never suppressed. The caller remains responsible
	for handling any state-only completion signal after suppressing native output.
	"""
	if not (protectReading and appFocused and browseMode and inConversation) or inPopup:
		return False
	text = " ".join(str(text or "").casefold().split())
	if not text or isPermissionPromptText(text) or statusDetails(text)[0] == "attention":
		return False
	return text == "response complete" or text.startswith((
		"response:", "response complete:", "chatgpt said:",
	))


def announcementPriority(category, message=""):
	"""Return low, normal, high, or urgent output priority."""
	message = str(message or "").lower()
	if category == "attention" or any(word in message for word in ("permission", "input required", "needs your")):
		return "urgent"
	if category == "completion" and isFailureText(message):
		return "urgent"
	if category == "completion":
		return "high"
	if category in ("commentary", "backgroundPulse1", "backgroundPulse2"):
		return "low"
	return "normal"


def outputActions(speechEnabled, speechOff, brailleEnabled, progressSoundsEnabled, toneCategory):
	"""Return which output channels should be used for one announcement."""
	speechUnavailable = not speechEnabled or speechOff
	return {
		"speech": bool(speechEnabled and not speechUnavailable),
		"braille": bool(brailleEnabled),
		"tone": bool(progressSoundsEnabled and toneCategory),
	}


def nextBusyState(currentBusy, category="", commentary=False):
	"""Update task activity without allowing final commentary to restart it."""
	if commentary:
		return bool(currentBusy)
	if category:
		return category not in ("completion", "attention")
	return bool(currentBusy)


def pollDelay(active, idlePollMs, activePollMs=500):
	"""Return the lightweight housekeeping interval, not a full-buffer scan rate."""
	return int(activePollMs if active else max(1000, idlePollMs))


def bufferInspectionDue(
	dirty, elapsedSinceInspection, active, appFocused, promptTyping,
	activeFallbackSeconds=5.0, focusedIdleFallbackSeconds=15.0,
):
	"""Decide whether the comparatively expensive ChatGPT buffer must be inspected.

	Relevant accessibility events mark the buffer dirty for the next safe moment.
	All whole-buffer inspection is deliberately suspended while the user is typing,
	and idle ChatGPT is event-only whether focused or in the background. Direct event
	handlers still announce time-sensitive activity.
	"""
	if promptTyping:
		return False
	if dirty:
		return True
	try:
		elapsed = float(elapsedSinceInspection)
	except (TypeError, ValueError, OverflowError):
		elapsed = 0.0
	if math.isnan(elapsed) or elapsed < 0:
		elapsed = 0.0
	if active:
		try:
			fallback = max(0.0, float(activeFallbackSeconds))
		except (TypeError, ValueError, OverflowError):
			fallback = 5.0
		return elapsed >= fallback
	return False


def conversationWindowShouldDetach(
	windowKnown, windowExists, windowVisible, unavailableSeconds, graceSeconds=2.0,
):
	"""Confirm that the tracked ChatGPT window is unavailable before discarding task state."""
	if not windowKnown or windowExists is None or windowVisible is None:
		return False
	if bool(windowExists) and bool(windowVisible):
		return False
	try:
		elapsed = float(unavailableSeconds)
		grace = max(0.0, float(graceSeconds))
	except (TypeError, ValueError, OverflowError):
		return False
	return bool(not math.isnan(elapsed) and elapsed >= grace)


def isBrailleTypingGestureIdentifier(identifier):
	"""Recognize a Braille display dot/space chord without claiming its command."""
	text = str(identifier or "").casefold().strip()
	if not text.startswith("br(") or ":" not in text:
		return False
	gesture = text.rsplit(":", 1)[-1]
	return any(re.fullmatch(r"dot[1-8]|space", token) for token in gesture.split("+"))


def brailleTypingGestureCommitsText(identifier):
	"""Return whether a recognized Braille typing gesture contains Space."""
	if not isBrailleTypingGestureIdentifier(identifier):
		return False
	gesture = str(identifier or "").casefold().rsplit(":", 1)[-1]
	return "space" in gesture.split("+")


def isPromptSubmissionGestureIdentifier(identifier):
	"""Recognize an unmodified keyboard Enter or a Braille display Enter chord.

	This classifies identifiers only. It neither claims nor sends a gesture, so the
	caller can observe submission without changing NVDA or display-driver behavior.
	"""
	text = str(identifier or "").casefold().strip()
	if ":" not in text:
		return False
	prefix, gesture = text.rsplit(":", 1)
	if prefix.startswith("kb"):
		return gesture in ("enter", "numpadenter")
	if prefix.startswith("br("):
		return gesture == "dot8"
	return False


def isConversationNavigationGestureIdentifier(identifier):
	"""Recognize unmodified keys that move NVDA's browse cursor."""
	text = str(identifier or "").casefold().strip()
	if ":" not in text:
		return False
	prefix, gesture = text.rsplit(":", 1)
	if not prefix.startswith("kb") or "+" in gesture:
		return False
	return gesture in ("uparrow", "downarrow", "pageup", "pagedown", "home", "end")


def promptSubmissionGestureShouldStart(promptInFocusMode, promptHadText, promptTypingActive):
	"""Require evidence of an actual prompt before Enter starts task feedback.

	Braille dot-8 activates an edit field while NVDA is in browse mode, so the
	gesture alone is not proof that ChatGPT received a prompt. Recent typing is
	accepted because Chromium can replace the editor before its final text event.
	"""
	return bool(promptInFocusMode and (promptHadText is True or promptTypingActive))


def shouldPreserveBrailleComposition(
	promptFocused, compositionActive, hasBufferedCells, elapsedSinceSend, graceSeconds=1.0,
):
	"""Ignore only the delayed caret event produced by our prior contracted-word send."""
	if not (promptFocused and compositionActive and hasBufferedCells):
		return False
	try:
		elapsed = float(elapsedSinceSend)
		grace = max(0.0, float(graceSeconds))
	except (TypeError, ValueError, OverflowError):
		return False
	return math.isfinite(elapsed) and 0.0 <= elapsed <= grace


def slowScanPauseSeconds(lastScanSeconds, factor=20.0, maximumSeconds=60.0, slowSeconds=0.5):
	"""Return how long to wait after a slow conversation scan before the next one.

	A scan blocks NVDA while it runs. In NVDA's usual Chromium document it takes
	milliseconds; in its UI Automation document it can take three seconds, so
	repeated scans would freeze NVDA most of the time during a task. A scan
	slower than ``slowSeconds`` is followed by a pause ``factor`` times its
	length, up to ``maximumSeconds``.
	"""
	try:
		duration = float(lastScanSeconds)
	except (TypeError, ValueError, OverflowError):
		return 0.0
	if math.isnan(duration) or duration < slowSeconds:
		return 0.0
	return min(float(maximumSeconds), duration * factor)


def coalescedPollDelay(requestedDelayMs, elapsedSinceLastPoll, minimumIntervalMs=150):
	"""Prevent rapid accessibility events from flooding NVDA's main thread with scans."""
	try:
		requestedDelayMs = int(requestedDelayMs)
	except (TypeError, ValueError, OverflowError):
		requestedDelayMs = 0
	requestedDelayMs = max(0, requestedDelayMs)
	try:
		minimumIntervalMs = int(minimumIntervalMs)
	except (TypeError, ValueError, OverflowError):
		minimumIntervalMs = 150
	minimumIntervalMs = max(0, minimumIntervalMs)
	try:
		elapsedSeconds = float(elapsedSinceLastPoll)
	except (TypeError, ValueError, OverflowError):
		elapsedSeconds = 0.0
	# Positive infinity deliberately means there has never been a previous poll.
	# It therefore needs no minimum-interval throttle and must never be rounded.
	if math.isinf(elapsedSeconds) and elapsedSeconds > 0:
		return requestedDelayMs
	if not math.isfinite(elapsedSeconds):
		elapsedSeconds = 0.0
	elapsedMs = max(0.0, elapsedSeconds * 1000.0)
	remainingMs = max(0, round(minimumIntervalMs - elapsedMs))
	return max(requestedDelayMs, remainingMs)


def shouldReplaceScheduledPoll(existingDeadline, requestedDeadline):
	"""Keep an already scheduled earlier scan instead of postponing it during event storms."""
	existingDeadline = float(existingDeadline or 0.0)
	requestedDeadline = float(requestedDeadline or 0.0)
	return not existingDeadline or requestedDeadline < existingDeadline


def shouldPlayContinuousWorkingClick(busy, enabled, soundStyle, soundAllowed, elapsedSinceSound, intervalSeconds):
	"""Play a working earcon only in a quiet gap between other progress sounds.

	The legacy function name is retained for add-on configuration compatibility.
	"""
	return bool(
		busy
		and enabled
		and soundStyle in ("clicks", "tones")
		and soundAllowed
		and float(elapsedSinceSound) >= float(intervalSeconds)
	)


def focusStateTransition(previousState, isFocused):
	"""Return the new focus state and a cue only when the state changes."""
	isFocused = bool(isFocused)
	if previousState is None:
		return isFocused, "active" if isFocused else ""
	if bool(previousState) == isFocused:
		return isFocused, ""
	return isFocused, "active" if isFocused else "inactive"


def selectedComposerMode(toggles):
	"""Return the selected name from ``(name, isOn)`` pairs of ChatGPT's Chat and Work switch.

	Returns an empty string unless exactly one option is selected.
	"""
	selected = [" ".join(str(name or "").split()) for name, isOn in toggles if isOn]
	return selected[0] if len(selected) == 1 and selected[0] else ""


def otherComposerMode(toggles, current):
	"""Return the first switch option that is not ``current``, or an empty string."""
	for name, _isOn in toggles:
		name = " ".join(str(name or "").split())
		if name and name != current:
			return name
	return ""


def chatGPTAppVersionSummary(appPath, productVersion):
	"""Describe the installed ChatGPT app for support: its Store package and program versions.

	The Store package version, such as 26.1013.3656.0, comes from the install
	folder name; it changes with every ChatGPT update.
	"""
	match = re.search(r"OpenAI\.[A-Za-z]+_(\d+(?:\.\d+)+)_", str(appPath or ""))
	parts = []
	if match:
		parts.append("package " + match.group(1))
	program = " ".join(str(productVersion or "").split())
	if program and not (match and program == match.group(1)):
		parts.append("program " + program)
	return ", ".join(parts) or "unknown"




def uniqueLabels(labels):
	"""Return non-empty labels with spacing normalized, without repeats, in order."""
	seen = []
	for label in labels:
		text = " ".join(str(label or "").replace("\ufffc", " ").split())
		if text and text not in seen:
			seen.append(text)
	return seen


def chatGPTCompatibilityFindings(promptNames, buttonNames, composerButtonNames, composerSwitchShown):
	"""Compare what ChatGPT's window shows with the names the add-on relies on.

	``promptNames`` are labels of ProseMirror message fields; ``buttonNames``
	are all button names in the window; ``composerButtonNames`` are buttons next
	to the message field, which are interface controls rather than chat titles.
	Returns ``None`` when no message field is shown, because nothing can be
	concluded on such a page. Otherwise returns ``(problems, notes)``: short
	plain-language findings for the NVDA log and support report.
	"""
	prompts = uniqueLabels(promptNames)
	if not prompts:
		return None
	buttons = {" ".join(str(name or "").casefold().split()) for name in buttonNames}
	problems = []
	notes = []
	if not any(isCodexPromptLabel(name) for name in prompts):
		problems.append("message field label not recognized: " + ", ".join(prompts))
	if ADD_FILES_BUTTON_NAME.casefold() not in buttons:
		candidates = [
			name for name in uniqueLabels(composerButtonNames)
			if isAttachmentButtonLikeLabel(name)
		]
		problems.append(
			ADD_FILES_BUTTON_NAME + " button not found"
			+ (" (message field buttons: " + ", ".join(candidates) + ")" if candidates else "")
		)
	if not any(
		name.startswith("switch mode") or name.startswith("current mode")
		for name in buttons
	):
		problems.append("ChatGPT and Codex mode switch not found")
	notes.append("message field: " + ", ".join(prompts))
	if composerSwitchShown:
		notes.append("Chat and Work switch shown")
	return problems, notes


SUGGESTION_MENU_TRIGGER_CHARACTERS = ("/", "@")
SUGGESTION_MENU_CLOSE_KEYS = ("escape", "enter", "numpadenter", "tab", "shift+tab")
SUGGESTION_MENU_MOVE_KEYS = ("downarrow", "uparrow")
SUGGESTION_MENU_EDIT_KEYS = ("backspace", "delete")


def gestureKeyName(identifier):
	"""Return the key of a keyboard gesture identifier, such as "downarrow" for "kb(laptop):downArrow"."""
	text = str(identifier or "")
	if not text.casefold().startswith("kb"):
		return ""
	return text.split(":", 1)[-1].casefold() if ":" in text else ""


def suggestionMenuReading(options, opened):
	"""Return ``(count, highlighted option or None, position)`` for announcing a suggestion menu.

	``position`` is the highlighted option's 1-based place in the menu, or 0.
	``opened`` is accepted so callers state why the menu is being read.
	"""
	options = tuple(options or ())
	for index, option in enumerate(options):
		if option.get("highlighted"):
			return len(options), option, index + 1
	return len(options), None, 0


def isAttachmentButtonLikeLabel(label):
	"""Recognize button names that may open ChatGPT's attachment menu, for support logging."""
	text = " ".join(str(label or "").casefold().split())
	if not text:
		return False
	return bool(promptControlKind(text) == "files" or re.search(r"\b(?:add|attach|upload|files?|photos?)\b", text))


def isCodexPromptLabel(label):
	"""Recognize stable accessible labels used by ChatGPT's primary prompt editor."""
	label = " ".join(str(label or "").casefold().split())
	return label in CHATGPT_PROMPT_LABELS


def statusDetails(label):
	"""Return ``(category, minimal message)`` for a recognized activity label."""
	text = " ".join(str(label or "").split())
	lower = text.lower()
	if not lower:
		return "", ""
	if lower.startswith(("permission required", "approval required", "waiting for approval", "needs your approval", "requires permission")):
		return "attention", "Permission required"
	if lower.startswith(("input required", "waiting for user input", "waiting for your input", "needs your input", "question for you")):
		return "attention", "User input required"
	if lower.startswith(("file edit complete", "file editing complete", "file edited")):
		return "completion", "File edit finished"
	if lower.startswith(("compiled", "transpiled")):
		return "completion", "Compilation finished"
	if lower.startswith(("searched the web", "search complete", "search finished")):
		return "completion", "Web search finished"
	if startsWithWord(lower, ("ran",)):
		hasSearch = "search" in lower and "web" in lower
		if hasSearch:
			return "completion", "Command and web search finished"
		# Codex normally formats completed shell activity as "Ran <command>"
		# without including the literal word "command".
		return "completion", "Command finished"
	if lower.startswith(("command failed", "failed command", "process failed")):
		return "completion", "Command failed"
	if lower.startswith(("command succeeded", "process succeeded")):
		return "completion", "Command finished"
	if lower.startswith(("tests failed", "testing failed", "test failed")):
		return "completion", "Tests failed"
	if lower.startswith(("tests passed", "testing passed", "test passed")):
		return "completion", "Tests passed"
	if lower.startswith(("build failed", "compilation failed")):
		return "completion", "Build failed"
	if lower.startswith("response complete") or startsWithWord(
		lower, ("finished", "completed", "done", "cancelled", "canceled"),
	):
		return "completion", "Finished"
	if lower.startswith(("reading finished", "reading complete", "inspection finished", "review finished")):
		return "completion", "Reading finished"
	if lower == "read" or lower.startswith(("read ", "read:", "inspected", "reviewed")):
		return "completion", "Reading finished"
	if startsWithWord(lower, ("wrote", "created")):
		return "completion", "Writing finished"
	if startsWithWord(lower, ("edited", "updated", "modified", "applied", "patched")):
		return "completion", "Changes finished"
	if startsWithWord(lower, ("generated", "built")):
		return "completion", "Generation finished"
	if lower.startswith(("planning", "thinking")):
		return "thinking", "Thinking"
	if lower.startswith(("working", "processing")):
		return "working", "Working"
	if lower.startswith(("analyzing", "analysing")):
		return "working", "Analyzing"
	if lower.startswith(("running", "executing")):
		if "search" in lower and ("web" in lower or "internet" in lower):
			return "search", "Searching the web"
		if lower.startswith(("running tests", "running test", "executing tests", "executing test", "running build", "executing build")):
			return "build", "Running tests" if "test" in lower else "Generating"
		if lower.startswith(("running tool", "executing tool")):
			return "tool", "Using tool"
		return "command", "Running command"
	if lower.startswith("searching"):
		return "search", "Searching the web"
	if lower.startswith(("reading", "inspecting", "reviewing")):
		return "file", "Reading"
	if lower.startswith(("writing", "creating")):
		return "file", "Writing"
	if lower.startswith(("file edit", "editing", "updating", "modifying")):
		return "file", "Editing file" if lower.startswith("file edit") else "Editing"
	if lower.startswith(("applying", "patching")):
		return "file", "Applying changes"
	if lower.startswith(("compiling", "transpiling", "generating", "building", "testing")):
		if lower.startswith(("compiling", "transpiling")):
			return "build", "Compiling"
		if lower.startswith("testing"):
			return "build", "Running tests"
		return "build", "Generating"
	if lower.startswith(("using", "calling")):
		return "tool", "Using tool"
	if lower.startswith("waiting"):
		return "other", "Waiting"
	return "", ""


def translatableStatusMessages(translate=lambda text: text):
	"""List status wording that reaches translate() through a variable.

	statusDetails, minimalProfileMessage, and backgroundActivityName pass these
	strings to the translation function indirectly. Naming them here lets
	tools/extract_messages.py add them to the translation template.
	"""
	return (
		translate("Analyzing"), translate("Applying changes"), translate("Build failed"),
		translate("Changes finished"), translate("Checking files"),
		translate("Command and web search finished"), translate("Compilation finished"),
		translate("Compiling"), translate("Editing"), translate("Editing code"),
		translate("File edit finished"), translate("File operations"), translate("File updated"),
		translate("Finished"), translate("Generating"), translate("Generation finished"),
		translate("Processing"), translate("Reading"), translate("Reading finished"),
		translate("Task canceled"), translate("Task finished"), translate("Tests"),
		translate("Tests failed"), translate("Tests passed"), translate("Tool operation"),
		translate("User input required"), translate("Waiting for command"),
		translate("Waiting for tool"), translate("Web search"), translate("Web search finished"),
		translate("Work"), translate("Writing"), translate("Writing finished"),
	)


def redactSensitive(text):
	text = " ".join(str(text or "").split())
	text = re.sub(r"(?i)(https?://[^\s?]+)\?\S+", r"\1?[query redacted]", text)
	text = re.sub(r"(?i)\b[\w.-]+@[\w.-]+\.[a-z]{2,}\b", "[email redacted]", text)
	secretValue = r'''(?:"[^"]*"|'[^']*'|[^\s;]+)'''
	text = re.sub(r"(?i)\b(api[_-]?key|token|secret|password|passwd|pwd|authorization)\s*[:=]\s*" + secretValue, r"\1=[redacted]", text)
	text = re.sub(
		r"(?i)(--?(?:api[_-]?key|token|secret|password|passwd|pwd|authorization))\s+" + secretValue,
		r"\1 [redacted]", text,
	)
	text = re.sub(r"(?i)(C:\\Users\\)[^\\]+", r"\1[user]", text)
	text = re.sub(r"(?i)(/home/|/users/)[^/\s]+", r"\1[user]", text)
	text = re.sub(r"(?i)\b(remote\s+(?:key|password)|connection\s+key)\s*[:=]\s*" + secretValue, r"\1=[redacted]", text)
	text = re.sub(r"(?i)\b(bearer)\s+[a-z0-9._~+/-]+=*", r"\1 [redacted]", text)
	return text


def standardFullMessage(label, translate=lambda text: text):
	"""Return an action-first Full message with useful targets, counts, and timing."""
	text = " ".join(str(label or "").split())
	lower = text.casefold()
	category, minimal = statusDetails(text)
	if not category:
		return ""
	details = []
	if category == "command" or lower.startswith("ran "):
		command = re.sub(
			r"(?i)^(?:(?:running|executing)(?:\s+(?:shell|terminal))?\s+command|ran)\s*:?\s*",
			"", text,
		)
		if command and command != text:
			executable = command.split()[0].strip("'\"")
			executable = re.split(r"[\\/]", executable)[-1]
			if executable:
				details.append(executable)
	else:
		fileMatch = re.search(r"(?i)(?:^|\s)([^\s<>|*?\"]+\.[a-z0-9]{1,8})(?:\s|$)", text)
		if fileMatch:
			details.append(re.split(r"[\\/]", fileMatch.group(1))[-1])
	countMatch = re.search(r"(?i)\b\d+\s+(?:files?|tests?|warnings?|errors?|failures?|passed|failed)\b", text)
	if countMatch and countMatch.group(0).casefold() not in {item.casefold() for item in details}:
		details.append(countMatch.group(0))
	seconds = elapsedSeconds(text)
	if seconds is not None and seconds >= 5:
		details.append(translate("{count} seconds").format(count=seconds))
	message = translate(minimal)
	return f"{message}: {', '.join(details)}" if details else message


def minimalProfileMessage(label, translate=lambda text: text, profile="balanced"):
	"""Return Essential, Balanced, or Informative Minimal speech."""
	text = " ".join(str(label or "").split())
	category, minimal = statusDetails(text)
	if not category:
		return ""
	lower = text.casefold()
	if profile == "essential":
		isFailure = isFailureText(lower)
		if category not in ("thinking", "attention") and not (
			category == "completion" and (isFailure or isTaskCompletionLabel(text))
		):
			return ""
	balanced = minimal
	if category == "file":
		if lower.startswith(("reading", "inspecting", "reviewing")):
			balanced = "Checking files"
		elif lower.startswith(("writing", "creating", "file edit", "editing", "updating", "modifying")):
			balanced = "Editing code"
	elif category == "completion":
		if isTaskCompletionLabel(text):
			balanced = "Task canceled" if lower.startswith(("cancelled", "canceled")) else "Task finished"
		elif lower.startswith(("file edit", "file edited", "edited", "updated", "modified", "applied", "patched")):
			balanced = "File updated"
	elif category == "other" and lower.startswith("waiting"):
		if "command" in lower or "process" in lower:
			balanced = "Waiting for command"
		elif "tool" in lower:
			balanced = "Waiting for tool"
	message = translate(balanced)
	if profile != "informative":
		return message
	details = []
	fileMatch = re.search(r"(?i)(?:^|\s)([^\s<>|*?\"]+\.[a-z0-9]{1,8})(?:\s|$)", text)
	if fileMatch:
		details.append(re.split(r"[\\/]", fileMatch.group(1))[-1])
	countMatch = re.search(r"(?i)\b\d+\s+(?:files?|tests?|warnings?|errors?|failures?|passed|failed)\b", text)
	if countMatch:
		details.append(countMatch.group(0))
	seconds = elapsedSeconds(text)
	if seconds is not None and seconds >= 10:
		details.append(translate("{count} seconds").format(count=seconds))
	return f"{message}: {', '.join(details)}" if details else message


def statusMessage(label, translate=lambda text: text, verbosity="minimal", redact=False, fullProfile="developer", minimalProfile="balanced"):
	text = " ".join(str(label or "").split())
	category, minimal = statusDetails(text)
	if not category:
		return ""
	if verbosity == "full":
		if fullProfile == "standard":
			message = standardFullMessage(text, translate)
		elif fullProfile == "raw":
			message = str(label or "").strip()
		else:
			message = text
		return redactSensitive(message) if redact else message
	return minimalProfileMessage(text, translate, minimalProfile)


def brailleStatusMessage(label, translate=lambda text: text, detail="full", redact=False):
	"""Format status independently for a Braille display."""
	detail = detail if detail in ("concise", "informative", "full") else "full"
	if detail == "concise":
		return statusMessage(label, translate, "minimal", redact, "developer", "balanced")
	if detail == "informative":
		return statusMessage(label, translate, "minimal", redact, "developer", "informative")
	return statusMessage(label, translate, "full", redact, "developer", "balanced")


def firstStatusLabel(*labels):
	for label in labels:
		text = " ".join(str(label or "").split())
		if statusDetails(text)[0]:
			return text
	return ""


def elapsedSeconds(label):
	"""Return total elapsed seconds, including hours and minutes such as "1m 30s"."""
	match = re.search(
		r"(?i)\b(?:(?P<hours>\d+)\s*h(?:ours?|rs?)?\s+)?(?:(?P<minutes>\d+)\s*m(?:in(?:ute)?s?)?\s+)?"
		r"(?P<seconds>\d+)\s*s(?:ec(?:ond)?s?)?\b",
		str(label or ""),
	)
	if not match:
		return None
	return (
		int(match.group("hours") or 0) * 3600
		+ int(match.group("minutes") or 0) * 60
		+ int(match.group("seconds"))
	)


def completedTextDelta(text, spokenOffset=0):
	"""Return newly completed streamed sentences and the updated offset."""
	text = " ".join(str(text or "").split())
	spokenOffset = min(max(int(spokenOffset or 0), 0), len(text))
	end = 0
	for match in re.finditer(r"[.!?](?:[\"'”’\)]*)($|\s)", text):
		end = match.end()
	if end <= spokenOffset:
		return "", spokenOffset
	return text[spokenOffset:end].strip(), end


def changelogForDisplay(markdownText):
	"""Convert the installed Markdown history into clean accessible text."""
	lines = []
	for rawLine in str(markdownText or "").splitlines():
		line = rawLine.strip()
		if line == "# Changelog":
			lines.append("Complete release history")
		elif line.startswith("## "):
			lines.extend(("", f"Version {line[3:].strip()}"))
		elif line.startswith("### "):
			lines.extend(("", line[4:].strip()))
		elif line.startswith("- "):
			lines.append(line[2:])
		else:
			lines.append(line)
	cleanLines = []
	for line in lines:
		if line or not cleanLines or cleanLines[-1]:
			cleanLines.append(line)
	return "\n".join(cleanLines).replace("**", "").replace("`", "").strip()


def viewerTitleMatches(expectedTitle, foregroundName):
	"""Return whether the intended browseable-message viewer is foreground."""
	expected = str(expectedTitle or "").strip().lower()
	foreground = str(foregroundName or "").strip().lower()
	return bool(expected and (foreground == expected or foreground.startswith(expected + " ")))


def previewSelection(items, selection):
	"""Return one preview item, falling back safely to the first item."""
	if not items:
		return None
	if not 0 <= selection < len(items):
		selection = 0
	return items[selection]


def formatCustomAnnouncement(template, message, activity="", seconds=0, duration=""):
	"""Format a user announcement without allowing unknown fields to break output."""
	template = str(template or "").strip()
	if not template:
		return str(message or "")
	duration = str(duration or formatElapsedDuration(seconds))
	try:
		return template.format(message=message, activity=activity, seconds=seconds, duration=duration)
	except (AttributeError, KeyError, IndexError, ValueError):
		return template
