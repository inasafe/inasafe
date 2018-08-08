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
# TODO(IS): currently only install to default profile directory.
InstallDir $DOCUMENTS\..\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\inasafe

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

LangString WELCOME_TITLE ${LANG_INDONESIAN} "Instalatur InaSAFE [[VERSION]]"
LangString WELCOME_TITLE ${LANG_ENGLISH} "InaSAFE [[VERSION]] Installer"
!define MUI_WELCOMEPAGE_TITLE $(WELCOME_TITLE)

LangString WELCOME_TEXT ${LANG_INDONESIAN} "Alat pengaturan ini akan memandu Anda melalui proses menginstal plugin InaSAFE. Perhatikan bahwa itu tidak menginstal QGIS sendiri - Anda harus melakukannya secara terpisah."
LangString WELCOME_TEXT ${LANG_ENGLISH} "This setup tool will guide you through the process of installing the InaSAFE plugin. Note that it does not install QGIS itself - you must do that separately."
!define MUI_WELCOMEPAGE_TEXT $(WELCOME_TEXT)


!define MUI_TEXT_WELCOME_INFO_TEXT "InaSAFE is free software that was developed jointly by Indonesia (BNPB), Australia (Australian Government) and the World Bank (GFDRR)."
!define MUI_INNERTEXT_LICENSE_BOTTOM "Scroll down to view the complete license"
!define MUI_TEXT_LICENSE_TITLE "InaSAFE is Free Software"
!define MUI_TEXT_LICENSE_SUBTITLE "Licensed under the GPL Version 3.0 or better"
!define MUI_INNERTEXT_LICENSE_TOP "License text"
!define MUI_TEXT_INSTALLING_TITLE "InaSAFE [[VERSION]] is busy installing"
!define MUI_TEXT_INSTALLING_SUBTITLE "Installation should only take a minute or two!"
!define MUI_TEXT_FINISH_TITLE "InaSAFE [[VERSION]] is installed!]]"
!define MUI_TEXT_FINISH_SUBTITLE ""
!define MUI_TEXT_ABORT_TITLE "Cancel"
!define MUI_TEXT_ABORT_SUBTITLE "Cancel installation"
!define MUI_BUTTONTEXT_FINISH "Finish"
!define MUI_TEXT_FINISH_INFO_TITLE "InaSAFE [[VERSION]] is installed"
!define MUI_TEXT_FINISH_INFO_REBOOT "Not used"
!define MUI_TEXT_FINISH_REBOOTNOW "Not used"
!define MUI_TEXT_FINISH_REBOOTLATER "Not used"
# !define MUI_TEXT_FINISH_INFO_TEXT "To use InaSAFE, start QGIS and you should find it installed under the Plugins -> InaSAFE menu."
!define MUI_TEXT_FINISH_INFO_TEXT "To use InaSAFE, start QGIS, go to Plugins -> Manage and Install Plugins, find InaSAFE and enable it by checking the check box next to it. After that you should find it installed under the Plugins -> InaSAFE menu."
!define MUI_UNTEXT_WELCOME_INFO_TITLE "Uninstall InaSAFE [[VERSION]]"
!define MUI_UNTEXT_WELCOME_INFO_TEXT "Press the next button below to continue with the uninstall process. Please note that any additional files you might have put into the InaSAFE plugins folder will be deleted!"
!define MUI_UNTEXT_CONFIRM_TITLE "Confirm you wish to uninstall"
!define MUI_UNTEXT_CONFIRM_SUBTITLE "Any files placed in the inasafe plugin director subsequent to installation will be removed!"
!define MUI_UNTEXT_UNINSTALLING_TITLE "Uninstalling InaSAFE [[VERSION]]"
!define MUI_UNTEXT_UNINSTALLING_SUBTITLE "Uninstallation in progress"
!define MUI_UNTEXT_FINISH_TITLE "Uninstall completed"
!define MUI_UNTEXT_FINISH_SUBTITLE "Thank you for using InaSAFE!"
!define MUI_UNTEXT_ABORT_TITLE "Cancel uninstall"
!define MUI_UNTEXT_ABORT_SUBTITLE ""
!define MUI_UNTEXT_FINISH_INFO_TITLE "Finish uninstallation"
!define MUI_UNTEXT_FINISH_INFO_REBOOT ""
!define MUI_UNTEXT_FINISH_INFO_TEXT "InaSAFE uninstallation completed"
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
    # No longer works, since the config is managed per profile in config file
    ;Added by Tim to set the reg key so that the plugin is enabled by default
    # WriteRegStr HKEY_CURRENT_USER "Software\QGIS\QGIS3\PythonPlugins" "inasafe" "true"

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
