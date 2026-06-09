[Setup]
AppId={{D11331A4-4B1E-4CD2-BDA5-7E94B7274D0F}
AppName=WinStart
AppVersion=3.0.4
AppPublisher=WinStart
DefaultDirName={localappdata}\WinStart
DefaultGroupName=WinStart
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=WinStart_Setup_v3.0.4
SetupIconFile=..\assets\app_icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\WinStart.exe
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create desktop shortcut / 创建桌面快捷方式"; GroupDescription: "Additional tasks / 附加任务:"

[Files]
Source: "..\dist\WinStart\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "WinStart"; ValueData: """{app}\WinStart.exe"""; Flags: uninsdeletevalue

[Icons]
Name: "{autoprograms}\WinStart"; Filename: "{app}\WinStart.exe"
Name: "{autodesktop}\WinStart"; Filename: "{app}\WinStart.exe"; Tasks: desktopicon

[Run]
Filename: "{cmd}"; Parameters: "/C reg add ""HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"" /v ""WinStart"" /t REG_BINARY /d 030000000000000000000000 /f"; Flags: runhidden
Filename: "{app}\WinStart.exe"; Description: "Launch WinStart / 启动 WinStart"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{cmd}"; Parameters: "/C reg delete ""HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"" /v ""WinStart"" /f"; Flags: runhidden; RunOnceId: "DeleteStartupApproved"
