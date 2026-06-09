param(
    [string]$Version = "3.0.3"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$pyinstaller = Join-Path $repoRoot ".venv\Scripts\pyinstaller.exe"
$dist = Join-Path $repoRoot "dist"
$mainExe = Join-Path $dist "WinStart.exe"
$versionedMainExe = Join-Path $dist "WinStart_v$Version.exe"
$setupName = "WinStart_Setup_v$Version"
$setupExe = Join-Path $dist "$setupName.exe"

if (-not (Test-Path $python)) {
    throw "Missing virtual environment Python: $python"
}

if (-not (Test-Path $pyinstaller)) {
    & $python -m pip install -r (Join-Path $repoRoot "requirements.txt")
}

& $pyinstaller --noconfirm (Join-Path $repoRoot "WinStart.spec")

if (-not (Test-Path $mainExe)) {
    throw "Main executable was not built: $mainExe"
}

Copy-Item -LiteralPath $mainExe -Destination $versionedMainExe -Force

& $pyinstaller `
    --noconfirm `
    --onefile `
    --windowed `
    --name $setupName `
    --icon (Join-Path $repoRoot "assets\app_icon.ico") `
    --add-binary "$mainExe;." `
    (Join-Path $repoRoot "src\installer_gui.py")

if (-not (Test-Path $setupExe)) {
    throw "Setup executable was not built: $setupExe"
}

Write-Host "Built release artifacts:"
Write-Host "  $versionedMainExe"
Write-Host "  $setupExe"
