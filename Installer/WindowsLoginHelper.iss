; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "Windows 登录辅助工具"
#define MyAppPublisher "Wilson.Huang"
#define MyAppURL "https://github.com/WilsonHuangDev/Windows-Login-Helper"
#define MyAppExeName "WinLoginHelper.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{9C3855D5-331B-4846-B374-ED3EDF04F1C6}
AppName={#MyAppName}
AppVerName={#MyAppName}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName=‌{win}\WindowsLoginHelper
UninstallDisplayIcon={app}\{#MyAppExeName}
DefaultGroupName={#MyAppName}
; Uncomment the following line to run in non administrative install mode (install for current user only).
;PrivilegesRequired=lowest
OutputDir=.\
OutputBaseFilename=WindowsLoginHelper_Setup
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "chinesesimplified"; MessagesFile: ".\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\CustomTextDisplayTool\Assets\*"; DestDir: "{app}\Assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\CustomTextDisplayTool\LICENCE.rtf"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\CustomTextDisplayTool\README.rtf"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\CustomTextDisplayTool\Bin\*"; DestDir: "{app}\Bin"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 删除文件，{app}：安装目录
Type: files; Name: "{userappdata}\CustomTextDisplayTool\config.json";
Type: dirifempty; Name: "{userappdata}\CustomTextDisplayTool";

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  InstallDir: String;
begin
  // 获取安装目录
  InstallDir := ExpandConstant('{app}');

  case CurUninstallStep of
    usUninstall:
      begin
        // 如果安装目录存在，则删除整个目录及其内容
        if DirExists(InstallDir) then
          DelTree(InstallDir, True, True, True);

        // 删除安装根目录
        RemoveDir(ExtractFileDir(InstallDir));
      end;
  end;
end;
