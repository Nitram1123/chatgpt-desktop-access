param(
	[string]$Version = "2026.3.0",
	[string]$PythonPath = "python"
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$outputRoot = Join-Path $projectRoot "outputs"
if (-not (Test-Path -LiteralPath $outputRoot)) {
	New-Item -ItemType Directory -Path $outputRoot | Out-Null
}
$package = Join-Path $outputRoot "chatGPTDesktopAccess-$Version.nvda-addon"
$env:PYTHONDONTWRITEBYTECODE = "1"

Push-Location $projectRoot
try {
	& $PythonPath -m unittest discover -s .\tests -v
	if ($LASTEXITCODE -ne 0) { throw "Automated tests failed" }
	& $PythonPath .\tools\extract_messages.py --check
	if ($LASTEXITCODE -ne 0) { throw "Translation template validation failed" }
	& $PythonPath -c "from pathlib import Path; files=list(Path('.').rglob('*.py')); [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print(f'Syntax valid: {len(files)} Python files')"
	if ($LASTEXITCODE -ne 0) { throw "Python syntax validation failed" }
	& $PythonPath .\tools\build_addon.py $package
	if ($LASTEXITCODE -ne 0) { throw "Package creation failed" }
	& $PythonPath .\tools\audit_addon.py $package $Version
	if ($LASTEXITCODE -ne 0) { throw "Release audit failed" }
	$entries = tar -tf $package
	if ($entries -match "__pycache__|\.pyc$") { throw "Generated cache file found in package" }
	if (($entries | Where-Object { $_ -match "\.wav$" }).Count -ne 51) { throw "Expected 51 WAV files" }
	$packagedManifest = (tar -xOf $package manifest.ini) -join "`n"
	if ($packagedManifest -notmatch "(?m)^version = $([regex]::Escape($Version))$") { throw "Packaged manifest version mismatch" }
	Copy-Item -LiteralPath (Join-Path $projectRoot "changelog.md") -Destination (Join-Path $outputRoot "CHANGELOG-$Version.md") -Force
	Copy-Item -LiteralPath (Join-Path $projectRoot "readme.md") -Destination (Join-Path $outputRoot "README-$Version.md") -Force
	Get-FileHash -Algorithm SHA256 -LiteralPath $package
} finally {
	Pop-Location
}
