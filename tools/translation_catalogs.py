"""Export, import, validate, and compile the add-on's translation catalogs.

export LANGUAGE OUTPUT
	Write the strings LANGUAGE still lacks as numbered lines, ``N<TAB>"json string"``.
	Lines named ``manifest:description`` and ``manifest:changelog`` stand for
	the fields of ``locale/LANGUAGE/manifest.ini``.
import LANGUAGE INPUT [--note TEXT]
	Read translated lines in the same form, check them against the English
	strings, merge them into ``locale/LANGUAGE/LC_MESSAGES/nvda.po`` and write
	``locale/LANGUAGE/manifest.ini``. Nothing is written if a line fails a check.
compile
	Rebuild every ``nvda.mo`` from its ``nvda.po``, as GNU msgfmt does.
check
	Confirm every catalog's placeholders, shortcut keys, and compiled file.
"""

import argparse
import ast
import json
import re
import struct
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCALE_ROOT = PROJECT_ROOT / "locale"
TEMPLATE_PATH = LOCALE_ROOT / "chatGPTDesktopAccess.pot"
MANIFEST_KEYS = ("manifest:description", "manifest:changelog")
PLACEHOLDER_PATTERN = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")


def parseCatalog(path):
	"""Return {msgid: msgstr} and the header text from a .po or .pot file."""
	entries = {}
	entry = {}
	section = None
	fuzzy = False

	def finish():
		nonlocal entry, fuzzy
		if "msgid" in entry and not fuzzy:
			entries[entry["msgid"]] = entry.get("msgstr", "")
		entry = {}
		fuzzy = False

	for raw in Path(path).read_text(encoding="utf-8").splitlines():
		line = raw.strip()
		if line.startswith("#,") and "fuzzy" in line:
			fuzzy = True
			continue
		if not line or line.startswith("#"):
			if not line and "msgid" in entry:
				finish()
			continue
		if line.startswith('"'):
			entry[section] += ast.literal_eval(line)
			continue
		keyword, _, value = line.partition(" ")
		if keyword in ("msgctxt", "msgid") and "msgstr" in entry:
			finish()
		if keyword not in ("msgid", "msgstr"):
			raise ValueError(f"{path}: unsupported entry {keyword}")
		section = keyword
		entry[section] = ast.literal_eval(value)
	finish()
	header = entries.pop("", "")
	return entries, header


def templateMessages():
	"""Return the template's strings with their source references, in template order."""
	messages = []
	entries, _header = parseCatalog(TEMPLATE_PATH)
	text = TEMPLATE_PATH.read_text(encoding="utf-8")
	for block in text.split("\n\n")[1:]:
		lines = block.strip().splitlines()
		refs = next((line[3:] for line in lines if line.startswith("#: ")), "")
		idLines = []
		inId = False
		for line in lines:
			if line.startswith("msgid "):
				inId = True
				idLines.append(ast.literal_eval(line[6:]))
			elif line.startswith("msgstr"):
				inId = False
			elif inId and line.startswith('"'):
				idLines.append(ast.literal_eval(line))
		message = "".join(idLines)
		if message:
			messages.append((message, refs))
	assert len(messages) == len(entries), "template parse mismatch"
	return messages


def manifestFields(path):
	"""Read description and changelog from a manifest.ini, keeping triple-quoted text."""
	text = Path(path).read_text(encoding="utf-8")
	fields = {}
	for key in ("description", "changelog"):
		match = re.search(rf'(?m)^{key} = (""".*?"""|".*?")$', text, re.S)
		if match:
			value = match.group(1)
			fields[key] = value[3:-3] if value.startswith('"""') else value[1:-1]
	return fields


def shortcutKeys(text):
	return len(re.findall(r"&(?!&)", text.replace("&&", "")))


def validate(source, translation):
	"""Return a list of problems with one translation of one English string."""
	problems = []
	if not translation.strip():
		problems.append("empty translation")
	if sorted(PLACEHOLDER_PATTERN.findall(source)) != sorted(PLACEHOLDER_PATTERN.findall(translation)):
		problems.append("placeholders differ")
	if shortcutKeys(source) != shortcutKeys(translation):
		problems.append("shortcut key (&) count differs")
	if source.count("\n") != translation.count("\n"):
		problems.append("line count differs")
	if source[:1].isspace() != translation[:1].isspace() or source[-1:].isspace() != translation[-1:].isspace():
		problems.append("leading or trailing space differs")
	return problems


def quote(text):
	"""Render a gettext string, splitting at line breaks as msgfmt prefers."""
	if "\n" not in text[:-1]:
		return json.dumps(text, ensure_ascii=False)
	lines = text.splitlines(keepends=True)
	return '""\n' + "\n".join(json.dumps(line, ensure_ascii=False) for line in lines)


def writeCatalog(language, translations, note):
	"""Write locale/LANGUAGE/LC_MESSAGES/nvda.po in template order."""
	path = LOCALE_ROOT / language / "LC_MESSAGES" / "nvda.po"
	version = re.search(r"Project-Id-Version: ([^\\\n]+)", TEMPLATE_PATH.read_text(encoding="utf-8")).group(1)
	header = [
		f"Project-Id-Version: {version}",
		f"Language: {language}",
		"MIME-Version: 1.0",
		"Content-Type: text/plain; charset=UTF-8",
		"Content-Transfer-Encoding: 8bit",
	]
	if note:
		header.append(f"X-Translation-Note: {note}")
	parts = ['msgid ""\nmsgstr ""\n' + "".join(json.dumps(line + "\n", ensure_ascii=False) + "\n" for line in header)]
	for message, refs in templateMessages():
		if message in translations:
			parts.append(f"#: {refs}\nmsgid {quote(message)}\nmsgstr {quote(translations[message])}\n")
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text("\n".join(parts), encoding="utf-8", newline="\n")
	return path


def compileCatalog(poPath):
	"""Compile one .po file beside itself as nvda.mo."""
	entries, header = parseCatalog(poPath)
	entries = {key: value for key, value in entries.items() if value}
	entries[""] = header
	keys = sorted(entries)
	ids = strs = b""
	offsets = []
	for key in keys:
		idBytes, strBytes = key.encode("utf-8"), entries[key].encode("utf-8")
		offsets.append((len(ids), len(idBytes), len(strs), len(strBytes)))
		ids += idBytes + b"\0"
		strs += strBytes + b"\0"
	count = len(keys)
	keyStart = 7 * 4 + 16 * count
	valueStart = keyStart + len(ids)
	table = []
	for idOffset, idLength, _strOffset, _strLength in offsets:
		table += [idLength, idOffset + keyStart]
	for _idOffset, _idLength, strOffset, strLength in offsets:
		table += [strLength, strOffset + valueStart]
	output = struct.pack("Iiiiiii", 0x950412DE, 0, count, 7 * 4, 7 * 4 + count * 8, 0, 0)
	output += struct.pack(f"{len(table)}i", *table) + ids + strs
	moPath = Path(poPath).with_suffix(".mo")
	moPath.write_bytes(output)
	return moPath


def exportStrings(language, outputPath):
	poPath = LOCALE_ROOT / language / "LC_MESSAGES" / "nvda.po"
	existing = parseCatalog(poPath)[0] if poPath.exists() else {}
	lines = []
	for index, (message, _refs) in enumerate(templateMessages(), 1):
		if not existing.get(message):
			lines.append(f"{index}\t{json.dumps(message, ensure_ascii=False)}")
	manifestPath = LOCALE_ROOT / language / "manifest.ini"
	if not manifestPath.exists():
		english = manifestFields(PROJECT_ROOT / "manifest.ini")
		for key in MANIFEST_KEYS:
			lines.append(f"{key}\t{json.dumps(english[key.split(':')[1]], ensure_ascii=False)}")
	Path(outputPath).write_text("\n".join(lines) + "\n", encoding="utf-8")
	print(f"{len(lines)} strings to translate for {language} written to {outputPath}")


def importStrings(language, inputPath, note):
	messages = templateMessages()
	english = manifestFields(PROJECT_ROOT / "manifest.ini")
	poPath = LOCALE_ROOT / language / "LC_MESSAGES" / "nvda.po"
	translations = parseCatalog(poPath)[0] if poPath.exists() else {}
	manifest = {}
	problems = []
	for number, raw in enumerate(Path(inputPath).read_text(encoding="utf-8-sig").splitlines(), 1):
		if not raw.strip():
			continue
		key, _, value = raw.partition("\t")
		try:
			translation = json.loads(value)
		except ValueError as error:
			problems.append(f"line {number}: not a JSON string ({error})")
			continue
		if key in MANIFEST_KEYS:
			source = english[key.split(":")[1]]
			manifest[key.split(":")[1]] = translation
		else:
			source = messages[int(key) - 1][0]
			translations[source] = translation
		problems.extend(f"line {number} ({key}): {problem}" for problem in validate(source, translation))
	if problems:
		print("\n".join(problems))
		sys.exit(f"{len(problems)} problems; nothing written")
	path = writeCatalog(language, {key: value for key, value in translations.items() if value}, note)
	compileCatalog(path)
	if manifest:
		manifestText = (
			f'description = "{manifest["description"]}"\n'
			f'changelog = """{manifest["changelog"]}"""\n'
		)
		(LOCALE_ROOT / language / "manifest.ini").write_text(manifestText, encoding="utf-8", newline="\n")
	missing = sum(1 for message, _refs in messages if not translations.get(message))
	print(f"{language}: {len(messages) - missing} of {len(messages)} strings translated; {missing} missing")


def checkAll():
	import gettext
	messages = [message for message, _refs in templateMessages()]
	failures = 0
	for poPath in sorted(LOCALE_ROOT.glob("*/LC_MESSAGES/nvda.po")):
		entries = parseCatalog(poPath)[0]
		language = poPath.parents[1].name
		for source, translation in entries.items():
			if translation:
				for problem in validate(source, translation):
					failures += 1
					print(f"{language}: {problem}: {source[:60]!r}")
		with poPath.with_suffix(".mo").open("rb") as moFile:
			compiled = gettext.GNUTranslations(moFile)._catalog
		expected = {key: value for key, value in entries.items() if value}
		if any(compiled.get(key) != value for key, value in expected.items()):
			failures += 1
			print(f"{language}: nvda.mo is out of date")
		done = sum(1 for message in messages if entries.get(message))
		print(f"{language}: {done}/{len(messages)} translated")
	if failures:
		sys.exit(f"{failures} problems")


def main():
	parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	commands = parser.add_subparsers(dest="command", required=True)
	exportParser = commands.add_parser("export")
	exportParser.add_argument("language")
	exportParser.add_argument("output")
	importParser = commands.add_parser("import")
	importParser.add_argument("language")
	importParser.add_argument("input")
	importParser.add_argument("--note", default="")
	commands.add_parser("compile")
	commands.add_parser("check")
	arguments = parser.parse_args()
	if arguments.command == "export":
		exportStrings(arguments.language, arguments.output)
	elif arguments.command == "import":
		importStrings(arguments.language, arguments.input, arguments.note)
	elif arguments.command == "compile":
		for poPath in sorted(LOCALE_ROOT.glob("*/LC_MESSAGES/nvda.po")):
			print(compileCatalog(poPath))
	else:
		checkAll()


if __name__ == "__main__":
	main()
