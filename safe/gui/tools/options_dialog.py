# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid - **Options Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""
__author__ = 'tim@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
# noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore
# noinspection PyPackageRequirements
from PyQt4.QtCore import pyqtSignature, pyqtSlot

from safe.common.utilities import temp_dir
from safe.defaults import (
    disclaimer,
    supporters_logo_path,
    default_north_arrow_path,
    get_defaults)
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.resources import get_ui_class, html_header, html_footer
from safe.common.version import get_version
from safe.gui.tools.help.options_help import options_help

FORM_CLASS = get_ui_class('options_dialog_base.ui')


class OptionsDialog(QtGui.QDialog, FORM_CLASS):
    """Options dialog for the InaSAFE plugin."""

    def __init__(self, iface, dock=None, parent=None):
        """Constructor for the dialog.

        :param iface: A Quantum GIS QGisAppInterface instance.
        :type iface: QGisAppInterface

        :param parent: Parent widget of this dialog
        :type parent: QWidget

        :param dock: Optional dock widget instance that we can notify of
            changes to the keywords.
        :type dock: Dock
        """

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr('InaSAFE %s Options' % get_version()))
        # Save reference to the QGIS interface and parent
        self.iface = iface
        self.parent = parent
        self.dock = dock
        self.keyword_io = KeywordIO()
        self.defaults = get_defaults()

        # Set up things for context help
        self.help_button = self.button_box.button(QtGui.QDialogButtonBox.Help)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)
        self.main_stacked_widget.setCurrentIndex(1)

        self.grpNotImplemented.hide()
        self.adjustSize()
        self.restore_state()
        # hack prevent showing use thread visible and set it false see #557
        self.cbxUseThread.setChecked(True)
        self.cbxUseThread.setVisible(False)

        # Set up listener for various UI
        self.custom_org_logo_checkbox.toggled.connect(
            self.set_organisation_logo)
        self.custom_north_arrow_checkbox.toggled.connect(self.set_north_arrow)
        self.custom_UseUserDirectory_checkbox.toggled.connect(
            self.set_user_dir)
        self.custom_templates_dir_checkbox.toggled.connect(
            self.set_templates_dir)
        self.custom_org_disclaimer_checkbox.toggled.connect(
            self.set_org_disclaimer)

    def restore_state(self):
        """Reinstate the options based on the user's stored session info.
        """
        settings = QtCore.QSettings()
        # flag = settings.value(
        #     'inasafe/useThreadingFlag', False)
        # hack set use thread to false see #557
        flag = False
        self.cbxUseThread.setChecked(flag)

        flag = bool(settings.value(
            'inasafe/visibleLayersOnlyFlag', True, type=bool))
        self.cbxVisibleLayersOnly.setChecked(flag)

        flag = bool(settings.value(
            'inasafe/set_layer_from_title_flag', True, type=bool))
        self.cbxSetLayerNameFromTitle.setChecked(flag)

        flag = bool(settings.value(
            'inasafe/setZoomToImpactFlag', True, type=bool))
        self.cbxZoomToImpact.setChecked(flag)
        # whether exposure layer should be hidden after model completes
        flag = bool(settings.value(
            'inasafe/setHideExposureFlag', False, type=bool))
        self.cbxHideExposure.setChecked(flag)

        flag = bool(settings.value(
            'inasafe/clip_hard', False, type=bool))
        self.cbxClipHard.setChecked(flag)

        flag = bool(settings.value(
            'inasafe/useSentry', False, type=bool))
        self.cbxUseSentry.setChecked(flag)

        flag = bool(settings.value(
            'inasafe/show_intermediate_layers', False, type=bool))
        self.cbxShowPostprocessingLayers.setChecked(flag)

        ratio = self.defaults['FEMALE_RATIO']
        self.dsbFemaleRatioDefault.setValue(ratio)

        path = settings.value(
            'inasafe/keywordCachePath',
            self.keyword_io.default_keyword_db_path(), type=str)
        self.leKeywordCachePath.setText(path)

        flag = bool(settings.value(
            'inasafe/template_warning_verbose', True, type=bool))
        self.template_warning_checkbox.setChecked(flag)

        # Restore Organisation Logo Path
        org_logo_path = settings.value(
            'inasafe/organisation_logo_path',
            supporters_logo_path(),
            type=str)
        custom_org_logo_flag = (
            org_logo_path != supporters_logo_path())
        self.custom_org_logo_checkbox.setChecked(custom_org_logo_flag)
        self.leOrganisationLogoPath.setText(org_logo_path)

        user_directory_path = settings.value(
            'inasafe/defaultUserDirectory',
            temp_dir('impacts'), type=str)
        custom_user_directory_flag = (
            user_directory_path != temp_dir('impacts'))
        self.custom_UseUserDirectory_checkbox.setChecked(
            custom_user_directory_flag)
        self.splitter_user_directory.setEnabled(custom_user_directory_flag)
        self.leUserDirectoryPath.setText(user_directory_path)

        # Restore Show Organisation Logo in Dock Flag
        flag = bool(settings.value(
            'inasafe/showOrganisationLogoInDockFlag', False, type=bool))
        self.organisation_on_dock_checkbox.setChecked(flag)

        # Restore North Arrow Image Path
        north_arrow_path = settings.value(
            'inasafe/north_arrow_path', default_north_arrow_path(), type=str)
        custom_north_arrow_flag = (
            north_arrow_path != default_north_arrow_path())
        self.custom_north_arrow_checkbox.setChecked(custom_north_arrow_flag)
        self.leNorthArrowPath.setText(north_arrow_path)

        # Restore Report Template Directory Path
        report_template_dir = settings.value(
            'inasafe/reportTemplatePath',
            '',
            type=str)
        custom_templates_dir_flag = (report_template_dir != '')
        self.custom_templates_dir_checkbox.setChecked(
            custom_templates_dir_flag)
        self.leReportTemplatePath.setText(report_template_dir)

        # Restore Disclaimer
        org_disclaimer = settings.value(
            'inasafe/reportDisclaimer', disclaimer(), type=str)
        custom_org_disclaimer_flag = (org_disclaimer != disclaimer())
        self.custom_org_disclaimer_checkbox.setChecked(
            custom_org_disclaimer_flag)
        self.txtDisclaimer.setPlainText(org_disclaimer)

        flag = bool(
            settings.value('inasafe/developer_mode', False, type=bool))
        self.cbxDevMode.setChecked(flag)

        flag = bool(
            settings.value('inasafe/use_native_zonal_stats', False, type=bool))
        self.cbxNativeZonalStats.setChecked(flag)

        # Restore ISO19115 metadata tab
        value = self.defaults['ISO19115_ORGANIZATION']
        self.iso19115_organization_le.setText(value)
        value = self.defaults['ISO19115_URL']
        self.iso19115_url_le.setText(value)
        value = self.defaults['ISO19115_EMAIL']
        self.iso19115_email_le.setText(value)
        value = self.defaults['ISO19115_TITLE']
        self.iso19115_title_le.setText(value)
        value = self.defaults['ISO19115_LICENSE']
        self.iso19115_license_le.setText(value)

    def save_state(self):
        """Store the options into the user's stored session info.
        """
        settings = QtCore.QSettings()
        settings.setValue(
            'inasafe/useThreadingFlag', False)
        settings.setValue(
            'inasafe/visibleLayersOnlyFlag',
            self.cbxVisibleLayersOnly.isChecked())
        settings.setValue(
            'inasafe/set_layer_from_title_flag',
            self.cbxSetLayerNameFromTitle.isChecked())
        settings.setValue(
            'inasafe/setZoomToImpactFlag',
            self.cbxZoomToImpact.isChecked())
        settings.setValue(
            'inasafe/setHideExposureFlag',
            self.cbxHideExposure.isChecked())
        settings.setValue(
            'inasafe/clip_hard',
            self.cbxClipHard.isChecked())
        settings.setValue(
            'inasafe/useSentry',
            self.cbxUseSentry.isChecked())
        settings.setValue(
            'inasafe/show_intermediate_layers',
            self.cbxShowPostprocessingLayers.isChecked())
        settings.setValue(
            'inasafe/defaultFemaleRatio',
            self.dsbFemaleRatioDefault.value())
        settings.setValue(
            'inasafe/keywordCachePath',
            self.leKeywordCachePath.text())
        settings.setValue(
            'inasafe/template_warning_verbose',
            self.template_warning_checkbox.isChecked())
        settings.setValue(
            'inasafe/north_arrow_path',
            self.leNorthArrowPath.text())
        settings.setValue(
            'inasafe/organisation_logo_path',
            self.leOrganisationLogoPath.text())
        settings.setValue(
            'inasafe/showOrganisationLogoInDockFlag',
            self.organisation_on_dock_checkbox.isChecked())
        settings.setValue(
            'inasafe/reportTemplatePath',
            self.leReportTemplatePath.text())
        settings.setValue(
            'inasafe/reportDisclaimer',
            self.txtDisclaimer.toPlainText())
        settings.setValue(
            'inasafe/developer_mode',
            self.cbxDevMode.isChecked())
        settings.setValue(
            'inasafe/use_native_zonal_stats',
            self.cbxNativeZonalStats.isChecked())
        settings.setValue(
            'inasafe/defaultUserDirectory',
            self.leUserDirectoryPath.text())

        # save metadata values
        settings.setValue(
            'inasafe/ISO19115_ORGANIZATION',
            self.iso19115_organization_le.text())
        settings.setValue(
            'inasafe/ISO19115_URL',
            self.iso19115_url_le.text())
        settings.setValue(
            'inasafe/ISO19115_EMAIL',
            self.iso19115_email_le.text())
        settings.setValue(
            'inasafe/ISO19115_TITLE',
            self.iso19115_title_le.text())
        settings.setValue(
            'inasafe/ISO19115_LICENSE',
            self.iso19115_license_le.text())

    def accept(self):
        """Method invoked when OK button is clicked."""
        self.save_state()
        self.dock.read_settings()
        self.close()

    # noinspection PyPep8Naming
    @pyqtSignature('')  # prevents actions being handled twice
    def on_toolKeywordCachePath_clicked(self):
        """Auto-connect slot activated when cache file tool button is clicked.
        """
        # noinspection PyCallByClass,PyTypeChecker
        file_name = QtGui.QFileDialog.getSaveFileName(
            self,
            self.tr('Set keyword cache file'),
            self.keyword_io.default_keyword_db_path(),
            self.tr('Sqlite DB File (*.db)'))
        self.leKeywordCachePath.setText(file_name)

    # noinspection PyPep8Naming
    @pyqtSignature('')  # prevents actions being handled twice
    def on_toolUserDirectoryPath_clicked(self):
        """Auto-connect slot activated when user directory tool button is
        clicked.
        """
        # noinspection PyCallByClass,PyTypeChecker
        dir_name = QtGui.QFileDialog.getExistingDirectory(
            self,
            self.tr('Results directory'),
            '',
            QtGui.QFileDialog.ShowDirsOnly)
        self.leUserDirectoryPath.setText(dir_name)

    # noinspection PyPep8Naming
    @pyqtSignature('')  # prevents actions being handled twice
    def on_toolNorthArrowPath_clicked(self):
        """Auto-connect slot activated when north arrow tool button is clicked.
        """
        # noinspection PyCallByClass,PyTypeChecker
        file_name = QtGui.QFileDialog.getOpenFileName(
            self,
            self.tr('Set north arrow image file'),
            '',
            self.tr('Portable Network Graphics files (*.png *.PNG)'))
        if file_name != '':
            self.leNorthArrowPath.setText(file_name)

    # noinspection PyPep8Naming
    @pyqtSignature('')  # prevents actions being handled twice
    def on_toolOrganisationLogoPath_clicked(self):
        """Auto-connect slot activated when logo file tool button is clicked.
        """
        # noinspection PyCallByClass,PyTypeChecker
        file_name = QtGui.QFileDialog.getOpenFileName(
            self,
            self.tr('Set organisation logo file'),
            '',
            self.tr('Portable Network Graphics files (*.png *.PNG)'))
        if file_name != '':
            self.leOrganisationLogoPath.setText(file_name)

    # noinspection PyPep8Naming
    @pyqtSignature('')  # prevents actions being handled twice
    def on_toolReportTemplatePath_clicked(self):
        """Auto-connect slot activated when report file tool button is clicked.
        """
        # noinspection PyCallByClass,PyTypeChecker
        dir_name = QtGui.QFileDialog.getExistingDirectory(
            self,
            self.tr('Templates directory'),
            '',
            QtGui.QFileDialog.ShowDirsOnly)
        self.leReportTemplatePath.setText(dir_name)

    def set_organisation_logo(self):
        """Auto-connect slot activated when org logo checkbox is toggled."""
        settings = QtCore.QSettings()
        if self.custom_org_logo_checkbox.isChecked():
            # Use previous org logo path
            path = settings.value(
                'inasafe/organisation_logo_path',
                supporters_logo_path(),
                type=str)
        else:
            # Set organisation path line edit to default one
            path = supporters_logo_path()

        self.leOrganisationLogoPath.setText(path)

    def set_north_arrow(self):
        """Auto-connect slot activated when north arrow checkbox is toggled."""
        settings = QtCore.QSettings()
        if self.custom_north_arrow_checkbox.isChecked():
            # Show previous north arrow path
            path = settings.value(
                'inasafe/north_arrow_path',
                default_north_arrow_path(),
                type=str)
        else:
            # Set the north arrow line edit to default one
            path = default_north_arrow_path()

        self.leNorthArrowPath.setText(path)

    def set_user_dir(self):
        """Auto-connect slot activated when user dir checkbox is toggled.
        """
        settings = QtCore.QSettings()
        if self.custom_UseUserDirectory_checkbox.isChecked():
            # Show previous templates dir
            path = settings.value(
                'inasafe/defaultUserDirectory',
                '',
                type=str)
        else:
            # Set the template report dir to ''
            path = temp_dir('impacts')

        self.leUserDirectoryPath.setText(path)

    def set_templates_dir(self):
        """Auto-connect slot activated when templates dir checkbox is toggled.
        """
        settings = QtCore.QSettings()
        if self.custom_templates_dir_checkbox.isChecked():
            # Show previous templates dir
            path = settings.value(
                'inasafe/reportTemplatePath',
                '',
                type=str)
        else:
            # Set the template report dir to ''
            path = ''

        self.leReportTemplatePath.setText(path)

    def set_org_disclaimer(self):
        """Auto-connect slot activated when org disclaimer checkbox is toggled.
        """
        settings = QtCore.QSettings()
        if self.custom_org_disclaimer_checkbox.isChecked():
            # Show previous organisation disclaimer
            org_disclaimer = settings.value(
                'inasafe/reportDisclaimer',
                disclaimer(),
                type=str)
        else:
            # Set the organisation disclaimer to the default one
            org_disclaimer = disclaimer()

        self.txtDisclaimer.setPlainText(org_disclaimer)

    @pyqtSlot()
    @pyqtSignature('bool')  # prevents actions being handled twice
    def help_toggled(self, flag):
        """Show or hide the help tab in the stacked widget.

        .. versionadded: 3.2.1

        :param flag: Flag indicating whether help should be shown or hidden.
        :type flag: bool
        """
        if flag:
            self.help_button.setText(self.tr('Hide Help'))
            self.show_help()
        else:
            self.help_button.setText(self.tr('Show Help'))
            self.hide_help()

    def hide_help(self):
        """Hide the usage info from the user.

        .. versionadded: 3.2.1
        """
        self.main_stacked_widget.setCurrentIndex(1)

    def show_help(self):
        """Show usage info to the user."""
        # Read the header and footer html snippets
        self.main_stacked_widget.setCurrentIndex(0)
        header = html_header()
        footer = html_footer()

        string = header

        message = options_help()

        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)
