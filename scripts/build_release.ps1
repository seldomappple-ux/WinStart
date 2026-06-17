param(
    [string]$Version = "3.0.5"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$pyinstaller = Join-Path $repoRoot ".venv\Scripts\pyinstaller.exe"
$dist = Join-Path $repoRoot "dist"
$appDir = Join-Path $dist "WinStart"
$mainExe = Join-Path $appDir "WinStart.exe"
$versionedZip = Join-Path $dist "WinStart_v$Version.zip"
$legacyOnefileExe = Join-Path $dist "WinStart_v$Version.exe"
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

if (Test-Path $versionedZip) {
    Remove-Item -LiteralPath $versionedZip -Force
}
if (Test-Path $legacyOnefileExe) {
    Remove-Item -LiteralPath $legacyOnefileExe -Force
}
for ($attempt = 1; $attempt -le 5; $attempt++) {
    try {
        Compress-Archive -Path (Join-Path $appDir "*") -DestinationPath $versionedZip -Force
        break
    } catch {
        if ($attempt -eq 5) {
            throw
        }
        Start-Sleep -Seconds 2
    }
}

& $pyinstaller `
    --noconfirm `
    --onefile `
    --windowed `
    --name $setupName `
    --icon (Join-Path $repoRoot "assets\app_icon.ico") `
    --add-data "$appDir;WinStart_app" `
    (Join-Path $repoRoot "src\installer_gui.py")

if (-not (Test-Path $setupExe)) {
    throw "Setup executable was not built: $setupExe"
}

Write-Host "Built release artifacts:"
Write-Host "  $versionedZip"
Write-Host "  $setupExe"
