; Use the modern UI
!include "MUI2.nsh"
; Added by Tim to get optimal compression
SetCompressor /SOLID lzma

# define name of installer
OutFile "InaSAFE-3.2.4-plugin.exe"

# define installation directory
InstallDir $DOCUMENTS\..\.qgis2\python\plugins\inasafe

# For removing Start Menu shortcut in Windows 7
RequestExecutionLevel user

;----------------------------------------------------------------------------------------------------------------------------

;Interface Settings

!define MUI_ABORTWARNING
!define MUI_ICON ".\Installer-Files\install-inasafe.ico"
!define MUI_UNICON ".\Installer-Files\uninstall-inasafe.ico"
!define MUI_HEADERIMAGE_BITMAP_NOSTRETCH ".\Installer-Files\InstallHeaderImage.bmp"
!define MUI_HEADERIMAGE_UNBITMAP_NOSTRETCH ".\Installer-Files\UnInstallHeaderImage.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP ".\Installer-Files\WelcomeFinishPage.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP ".\Installer-Files\WelcomeFinishPage.bmp"

;----------------------------------------------------------------------------------------------------------------------------

;Installer Pages

!define MUI_WELCOMEPAGE_TITLE_3LINES
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE.txt"
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_TITLE_3LINES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

# start default section
Section
    ;Added by Tim to set the reg key so that the plugin is enabled by default
    WriteRegStr HKEY_CURRENT_USER "Software\QGIS\QGIS2\PythonPlugins" "inasafe" "true"

    SetOutPath $INSTDIR
    File /r /tmp/nsis-data/inasafe/*
    WriteUninstaller "$INSTDIR\uninstall.exe"
    CreateShortCut "$SMPROGRAMS\Uninstall InaSAFE.lnk" "$INSTDIR\uninstall.exe"
SectionEnd

# uninstaller section start
Section "uninstall"
    Delete "$INSTDIR\uninstall.exe"
    Delete "$SMPROGRAMS\Uninstall InaSAFE.lnk"
    RMDir /r $INSTDIR
SectionEnd


;----------------------------------------------------------------------------------------------------------------------------
