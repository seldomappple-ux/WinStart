param(
    [string]$Version = "3.0.7",
    [string]$ReleaseNotesEn = "See the project changelog for this release.",
    [string]$ReleaseNotesZh = "请查看项目更新记录。"
)

$ErrorActionPreference = "Stop"

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
    }
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$pyinstaller = Join-Path $repoRoot ".venv\Scripts\pyinstaller.exe"
$dist = Join-Path $repoRoot "dist"
$appDir = Join-Path $dist "WinStart"
$mainExe = Join-Path $appDir "WinStart.exe"
$releaseDirName = "WinStart_v$Version"
$releaseDir = Join-Path $dist $releaseDirName
$portableDir = Join-Path $releaseDir $releaseDirName
$legacyZip = Join-Path $releaseDir "$releaseDirName.zip"
$legacyOnefileExe = Join-Path $dist "WinStart_v$Version.exe"
$setupName = "WinStart_Setup_v$Version"
$setupExe = Join-Path $dist "$setupName.exe"
$releaseSetupExe = Join-Path $releaseDir "$setupName.exe"
$releaseNoteName = "$([char]0x8BF4)$([char]0x660E).txt"
$readmeTxt = Join-Path $releaseDir "WinStart_v$Version`_$releaseNoteName"

if (-not (Test-Path $python)) {
    throw "Missing virtual environment Python: $python"
}

$runningFromDist = Get-CimInstance Win32_Process -Filter "Name = 'WinStart.exe'" |
    Where-Object { $_.ExecutablePath -and $_.ExecutablePath.StartsWith($appDir, [System.StringComparison]::OrdinalIgnoreCase) }
if ($runningFromDist) {
    throw "WinStart is running from $appDir. Close it before building so PyInstaller can replace the onedir files."
}

if (-not (Test-Path $pyinstaller)) {
    Invoke-Checked -FilePath $python -Arguments @("-m", "pip", "install", "-r", (Join-Path $repoRoot "requirements.txt"))
}

Invoke-Checked -FilePath $pyinstaller -Arguments @("--noconfirm", (Join-Path $repoRoot "WinStart.spec"))

if (-not (Test-Path $mainExe)) {
    throw "Main executable was not built: $mainExe"
}

if (Test-Path $releaseDir) {
    Remove-Item -LiteralPath $releaseDir -Recurse -Force
}
New-Item -ItemType Directory -Path $releaseDir | Out-Null

if (Test-Path $legacyZip) {
    Remove-Item -LiteralPath $legacyZip -Force
}
if (Test-Path $legacyOnefileExe) {
    Remove-Item -LiteralPath $legacyOnefileExe -Force
}
Copy-Item -LiteralPath $appDir -Destination $portableDir -Recurse -Force

$setupArgs = @(
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--name", $setupName,
    "--icon", (Join-Path $repoRoot "assets\app_icon.ico"),
    "--add-data", "$appDir;WinStart_app",
    (Join-Path $repoRoot "src\installer_gui.py")
)
Invoke-Checked -FilePath $pyinstaller -Arguments $setupArgs

if (-not (Test-Path $setupExe)) {
    throw "Setup executable was not built: $setupExe"
}

Move-Item -LiteralPath $setupExe -Destination $releaseSetupExe -Force

$portableHash = (Get-FileHash -LiteralPath (Join-Path $portableDir "WinStart.exe") -Algorithm SHA256).Hash
$setupHash = (Get-FileHash -LiteralPath $releaseSetupExe -Algorithm SHA256).Hash

$englishNote = @"
WinStart Release - v$Version

English

What's new in this version:
$ReleaseNotesEn

Files:
1. $setupName.exe
   Installer edition. Recommended for normal use. It installs the onedir app to %LOCALAPPDATA%\WinStart.

2. $releaseDirName\
   Portable edition. Run WinStart.exe from this folder.
   Do not copy only the exe. Keep the _internal folder beside WinStart.exe.

3. WinStart_v$Version`_$releaseNoteName
   This short release note.

Packaging:
- The main app is built with PyInstaller onedir to avoid onefile _MEI cleanup warnings.
- The installer is still built with PyInstaller onefile and is only a distribution helper.
- Every release must increment the version and create its own folder under dist.
- The release folder contains the installer, the portable onedir folder, and this versioned note file. It does not contain a portable zip.

SHA256:
$releaseDirName\WinStart.exe
$portableHash

$setupName.exe
$setupHash
"@

$chineseTemplateBase64 = "5Lit5paH6K+05piOCgrmnKzniYjmnKzljYfnuqflhoXlrrk6CntSRUxFQVNFX05PVEVTX1pIfQoK5paH5Lu26K+05piOOgoxLiB7U0VUVVB9CiAgIOWuieijheeJiOOAguaOqOiNkOaZrumAmueUqOaIt+S9v+eUqCwg5Lya5bCG55uu5b2V54mI5Li756iL5bqP5a6J6KOF5YiwICVMT0NBTEFQUERBVEElXFdpblN0YXJ044CCCgoyLiB7UE9SVEFCTEV9XAogICDkvr/mkLrniYjjgILor7fku47mraTmlofku7blpLnov5DooYwgV2luU3RhcnQuZXhl44CCCiAgIOS4jeimgeWPquWkjeWItuWNleS4qiBleGUsIOW/hemhu+S/neeVmSBXaW5TdGFydC5leGUg5peB6L6555qEIF9pbnRlcm5hbCDmlofku7blpLnjgIIKCjMuIHtOT1RFfQogICDlvZPliY3ov5nku73nroDnn63lj5HluIPor7TmmI7jgIIKCuaJk+WMheivtOaYjjoKLSDkuLvnqIvluo/kvb/nlKggUHlJbnN0YWxsZXIgb25lZGlyIOaWueW8j+aehOW7uiwg55So5LqO6KeE6YG/IG9uZWZpbGUgX01FSSDkuLTml7bnm67lvZXmuIXnkIblkYrorabjgIIKLSDlronoo4Xlmajku43kvb/nlKggUHlJbnN0YWxsZXIgb25lZmlsZSDmlrnlvI8sIOS7heS9nOS4uuS4gOasoeaAp+WIhuWPkeW3peWFt+OAggotIOavj+asoeWPkeW4g+mDveW/hemhu+mAkuWinueJiOacrOWPtywg5bm25ZyoIGRpc3Qg5LiL55Sf5oiQ54us56uL54mI5pys55uu5b2V44CCCi0g5Y+R5biD55uu5b2V5Y+q5YyF5ZCr5a6J6KOF54mI44CB5L6/5pC654mI55uu5b2V5ZKM6L+Z5Lu95bim54mI5pys5Y+355qE6K+05piO5paH5Lu2LCDkuI3ljIXlkKvkvr/mkLogemlw44CC"
$chineseNote = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($chineseTemplateBase64)).
    Replace("{SETUP}", "$setupName.exe").
    Replace("{PORTABLE}", $releaseDirName).
    Replace("{NOTE}", "WinStart_v$Version`_$releaseNoteName").
    Replace("{RELEASE_NOTES_ZH}", $ReleaseNotesZh)

$readme = "$englishNote`r`n`r`n---`r`n`r`n$chineseNote"

Set-Content -LiteralPath $readmeTxt -Value $readme -Encoding UTF8

Write-Host "Built release artifacts:"
Write-Host "  $portableDir"
Write-Host "  $releaseSetupExe"
Write-Host "  $readmeTxt"
