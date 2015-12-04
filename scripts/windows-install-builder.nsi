; Use the modern UI
!include "MUI2.nsh"
; Added by Tim to get optimal compression
SetCompressor /SOLID lzma
!define COMPLETE_NAME "InaSAFE [[VERSION]]"

!addplugindir osgeo4w/untgz
!addplugindir osgeo4w/nsis

;----------------------------------------------------------------------------------------------------------------------------

;Publisher variables

!define PUBLISHER "InaSAFE"
!define WEB_SITE "http://inasafe.org"

;----------------------------------------------------------------------------------------------------------------------------

;General Definitions

;Name of the application shown during install
Name "InaSAFE [[VERSION]]"
# define name of installer
OutFile "InaSAFE-[[VERSION]]-plugin.exe"

# define installation directory
InstallDir $DOCUMENTS\..\.qgis2\python\plugins\inasafe

# For removing Start Menu shortcut in Windows 7
RequestExecutionLevel user

;--------------------------------
;Interface Settings

;Show all languages, despite user's codepage
!define MUI_LANGDLL_ALLLANGUAGES

;--------------------------------
;Language Selection Dialog Settings

;Remember the installer language
!define MUI_LANGDLL_REGISTRY_ROOT "HKCU"
!define MUI_LANGDLL_REGISTRY_KEY "Software\Modern UI InaSAFE"
!define MUI_LANGDLL_REGISTRY_VALUENAME "Installer Language"

;----------------------------------------------------------------------------------------------------------------------------

;Reserve Files

;If you are using solid compression, files that are required before
;the actual installation should be stored first in the data block,
;because this will make your installer start faster.

!insertmacro MUI_RESERVEFILE_LANGDLL
;--------------------------------
;Interface Settings

!define MUI_ABORTWARNING


;----------------------------------------------------------------------------------------------------------------------------
;Interface Settings

!define MUI_ICON ".\Installer-Files\install-inasafe.ico"
!define MUI_UNICON ".\Installer-Files\uninstall-inasafe.ico"
!define MUI_HEADERIMAGE_BITMAP_NOSTRETCH ".\Installer-Files\InstallHeaderImage.bmp"
!define MUI_HEADERIMAGE_UNBITMAP_NOSTRETCH ".\Installer-Files\UnInstallHeaderImage.bmp"
!define MUI_WELCOMEFINISHPAGE_BITMAP ".\Installer-Files\WelcomeFinishPage.bmp"
!define MUI_UNWELCOMEFINISHPAGE_BITMAP ".\Installer-Files\WelcomeFinishPage.bmp"

LangString WELCOME_TITLE ${LANG_INDONESIAN} "Indonesian title"
LangString WELCOME_TEXT ${LANG_ENGLISH} "InaSAFE [[VERSION]] Installer"
!define MUI_WELCOMEPAGE_TITLE $(WELCOME_TITLE)

LangString WELCOME_TEXT ${LANG_INDONESIAN} "FOO BAR"
LangString WELCOME_TEXT ${LANG_ENGLISH} "This setup tool will guide you through the process of installing the InaSAFE plugin. Note that it does not install QGIS itself - you must do that separately."
!define MUI_WELCOMEPAGE_TEXT $(WELCOME_TEXT)
!define MUI_TEXT_WELCOME_INFO_TEXT
!define MUI_INNERTEXT_LICENSE_BOTTOM
!define MUI_TEXT_LICENSE_TITLE
!define MUI_TEXT_LICENSE_SUBTITLE
!define MUI_INNERTEXT_LICENSE_TOP
!define MUI_TEXT_INSTALLING_TITLE
!define MUI_TEXT_INSTALLING_SUBTITLE
!define MUI_TEXT_FINISH_TITLE
!define MUI_TEXT_FINISH_SUBTITLE
!define MUI_TEXT_ABORT_TITLE
!define MUI_TEXT_ABORT_SUBTITLE
!define MUI_BUTTONTEXT_FINISH
!define MUI_TEXT_FINISH_INFO_TITLE
!define MUI_TEXT_FINISH_INFO_REBOOT
!define MUI_TEXT_FINISH_REBOOTNOW
!define MUI_TEXT_FINISH_REBOOTLATER
!define MUI_TEXT_FINISH_INFO_TEXT
!define MUI_UNTEXT_WELCOME_INFO_TITLE
!define MUI_UNTEXT_WELCOME_INFO_TEXT
!define MUI_UNTEXT_CONFIRM_TITLE
!define MUI_UNTEXT_CONFIRM_SUBTITLE
!define MUI_UNTEXT_UNINSTALLING_TITLE
!define MUI_UNTEXT_UNINSTALLING_SUBTITLE
!define MUI_UNTEXT_FINISH_TITLE
!define MUI_UNTEXT_FINISH_SUBTITLE
!define MUI_UNTEXT_ABORT_TITLE
!define MUI_UNTEXT_ABORT_SUBTITLE
!define MUI_UNTEXT_FINISH_INFO_TITLE
!define MUI_UNTEXT_FINISH_INFO_REBOOT
!define MUI_UNTEXT_FINISH_INFO_TEXT
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

;Installer Functions
Function .onInit

  !insertmacro MUI_LANGDLL_DISPLAY

FunctionEnd

# uninstaller section start
Section "uninstall"
    Delete "$INSTDIR\uninstall.exe"
    Delete "$SMPROGRAMS\Uninstall InaSAFE.lnk"
    RMDir /r $INSTDIR
SectionEnd

;Uninstaller Functions
Function un.onInit

  !insertmacro MUI_UNGETLANGUAGE

FunctionEnd


;----------------------------------------------------------------------------------------------------------------------------

; Language files - first listed is default
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "Indonesian"
