; MurmurTone Installer Script for Inno Setup 6+
; https://jrsoftware.org/isinfo.php
;
; Build installer:
;   1. Install Inno Setup from https://jrsoftware.org/isdl.php
;   2. Run: python prepare_model.py (to bundle tiny.en model)
;   3. Run: pyinstaller murmurtone.spec (to build EXE)
;   4. Run: iscc installer.iss (to build installer)
;
; For code signing, set environment variables before running iscc:
;   SIGN_TOOL_PATH - Path to signtool.exe (from Windows SDK)
;   SIGN_CERT_PATH - Path to PFX certificate file
;   SIGN_CERT_PASS - Certificate password

#define MyAppName "MurmurTone"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "MurmurTone"
#define MyAppURL "https://murmurtone.com"
#define MyAppExeName "MurmurTone.exe"

[Setup]
; Basic app info
AppId={{B5E7F8C3-2D4A-4F9E-9B1C-8A7E6D5C4B3A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation directories
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes

; Output
OutputDir=installer_output
OutputBaseFilename=MurmurTone-{#MyAppVersion}-Setup
Compression=lzma2/ultra64
SolidCompression=yes

; Appearance
WizardStyle=modern
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Requirements
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.19041

; License
LicenseFile=LICENSE

; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Code signing (optional - requires environment variables)
#ifdef SIGN_TOOL_PATH
  #ifdef SIGN_CERT_PATH
    SignTool=custom /f "{#SIGN_CERT_PATH}" /p "{#SIGN_CERT_PASS}" /t http://timestamp.digicert.com /fd sha256 $f
    SignedUninstaller=yes
  #endif
#endif

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startuprun"; Description: "Launch {#MyAppName} at Windows startup"; GroupDescription: "Startup Options:"; Flags: unchecked
Name: "gpusupport"; Description: "Include NVIDIA GPU acceleration (adds ~1.6 GB)"; GroupDescription: "GPU Support:"; Flags: unchecked
Name: "ollamainstall"; Description: "Install Ollama for AI text cleanup (~300 MB download)"; GroupDescription: "AI Features:"; Flags: unchecked

[Files]
; Main application files (built by PyInstaller)
Source: "dist\MurmurTone\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; GPU libraries (optional - only if gpusupport task selected)
Source: "gpu_libs\*.dll"; DestDir: "{app}"; Tasks: gpusupport; Flags: ignoreversion skipifsourcedoesntexist

; Ollama installer (optional - only if ollamainstall task selected)
Source: "ollama\OllamaSetup.exe"; DestDir: "{tmp}"; Tasks: ollamainstall; Flags: deleteafterinstall skipifsourcedoesntexist

; Additional files
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "THIRD_PARTY_LICENSES.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Settings"; Filename: "{app}\{#MyAppExeName}"; Parameters: "--settings"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; Startup registry entry (optional task)
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: startuprun

[Run]
; Install Ollama silently if selected (runs before app launch)
Filename: "{tmp}\OllamaSetup.exe"; Parameters: "/VERYSILENT /NORESTART"; Tasks: ollamainstall; StatusMsg: "Installing Ollama..."; Flags: waituntilterminated skipifdoesntexist

; Option to launch app after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up config directory on uninstall
Type: filesandordirs; Name: "{userappdata}\{#MyAppName}"

[Code]
function InitializeSetup(): Boolean;
var
  OldVersion: String;
  UninstallPath: String;
  ResultCode: Integer;
begin
  Result := True;

  // Check if already installed
  if RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{B5E7F8C3-2D4A-4F9E-9B1C-8A7E6D5C4B3A}_is1', 'UninstallString', UninstallPath) or
     RegQueryStringValue(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\{B5E7F8C3-2D4A-4F9E-9B1C-8A7E6D5C4B3A}_is1', 'UninstallString', UninstallPath) then
  begin
    if MsgBox('MurmurTone is already installed. Do you want to uninstall the current version first?', mbConfirmation, MB_YESNO) = IDYES then
    begin
      UninstallPath := RemoveQuotes(UninstallPath);
      Exec(UninstallPath, '/SILENT', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      Result := ResultCode = 0;
    end
    else
    begin
      Result := False;
    end;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Kill any running instances before completing installation
    Exec('taskkill', '/F /IM MurmurTone.exe', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;
