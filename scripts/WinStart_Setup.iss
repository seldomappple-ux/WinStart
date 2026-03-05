[Setup]
AppId={{D11331A4-4B1E-4CD2-BDA5-7E94B7274D0F}
AppName=WinStart
AppVersion=1.0.0
AppPublisher=WinStart
DefaultDirName={autopf}\WinStart
DefaultGroupName=WinStart
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=WinStart_Setup
SetupIconFile=..\assets\app_icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\WinStart.exe

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务:"

[Files]
Source: "..\dist\WinStart.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\WinStart"; Filename: "{app}\WinStart.exe"
Name: "{autodesktop}\WinStart"; Filename: "{app}\WinStart.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\WinStart.exe"; Description: "启动 WinStart"; Flags: nowait postinstall skipifsilent
