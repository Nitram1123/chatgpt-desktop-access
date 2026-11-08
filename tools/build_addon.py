"""Create a byte-for-byte reproducible NVDA add-on archive."""

from pathlib import Path
import argparse
import zipfile


FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
ROOT_FILES = ("manifest.ini", "readme.md", "changelog.md", "LICENSE.txt")
NORMALIZED_TEXT_SUFFIXES = {".ini", ".md", ".py", ".txt"}


def packageFiles(projectRoot):
	files = [projectRoot / path for path in ROOT_FILES]
	appModulesRoot = projectRoot / "appModules"
	files.extend(sorted(appModulesRoot.glob("*.py"), key=lambda path: path.name.casefold()))
	files.append(projectRoot / "globalPlugins" / "__init__.py")
	pluginRoot = projectRoot / "globalPlugins" / "codexStatusAnnouncer"
	files.extend(sorted(pluginRoot.glob("*.py"), key=lambda path: path.name.casefold()))
	localeRoot = projectRoot / "locale"
	files.extend(sorted(localeRoot.glob("*/LC_MESSAGES/nvda.mo"), key=lambda path: path.as_posix().casefold()))
	files.extend(sorted(localeRoot.glob("*/manifest.ini"), key=lambda path: path.as_posix().casefold()))
	soundsRoot = projectRoot / "globalPlugins" / "codexStatusAnnouncer" / "sounds"
	for level in ("soft", "normal", "loud"):
		files.extend(sorted((soundsRoot / level).glob("*.wav"), key=lambda path: path.name))
	return files


def packageData(path):
	data = path.read_bytes()
	if path.suffix.casefold() in NORMALIZED_TEXT_SUFFIXES:
		return data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
	return data


def buildPackage(projectRoot, outputPath):
	projectRoot = Path(projectRoot).resolve()
	outputPath = Path(outputPath).resolve()
	files = packageFiles(projectRoot)
	missing = [path for path in files if not path.is_file()]
	if missing:
		raise FileNotFoundError(f"Missing package file: {missing[0]}")
	outputPath.parent.mkdir(parents=True, exist_ok=True)
	with zipfile.ZipFile(outputPath, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
		for path in files:
			archiveName = path.relative_to(projectRoot).as_posix()
			info = zipfile.ZipInfo(archiveName, FIXED_TIMESTAMP)
			info.compress_type = zipfile.ZIP_DEFLATED
			info.create_system = 3
			info.external_attr = 0o100644 << 16
			archive.writestr(info, packageData(path), compresslevel=9)


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("output")
	args = parser.parse_args()
	root = Path(__file__).resolve().parents[1]
	buildPackage(root, args.output)
