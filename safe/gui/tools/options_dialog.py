# coding=utf-8
"""InaSAFE Options Dialog"""

import logging
# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
# noinspection PyPackageRequirements
from PyQt4 import QtGui, QtCore
# noinspection PyPackageRequirements
from PyQt4.QtCore import pyqtSignature, pyqtSlot, QVariant

from safe_extras.parameters.qt_widgets.parameter_container import (
    ParameterContainer)
from safe_extras.parameters.float_parameter import FloatParameter
from safe_extras.parameters.integer_parameter import IntegerParameter

from safe.definitions.utilities import all_default_fields
from safe.definitions.constants import qvariant_whole_numbers, GLOBAL
from safe.definitions.default_settings import inasafe_default_settings
from safe.definitions.messages import disclaimer
from safe.common.utilities import temp_dir
from safe.defaults import supporters_logo_path, default_north_arrow_path
from safe.impact_function.earthquake import EARTHQUAKE_FUNCTIONS
from safe.utilities.i18n import tr
from safe.utilities.resources import get_ui_class, html_header, html_footer
from safe.utilities.settings import setting, set_setting
from safe.common.version import get_version
from safe.gui.tools.help.options_help import options_help

from safe.utilities.settings import (
    set_inasafe_default_value_qsetting,
    get_inasafe_default_value_qsetting)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')
FORM_CLASS = get_ui_class('options_dialog_base.ui')


class OptionsDialog(QtGui.QDialog, FORM_CLASS):
    """Options dialog for the InaSAFE plugin."""

    def __init__(self, iface, dock=None, parent=None, qsetting=''):
        """Constructor for the dialog.

        :param iface: A Quantum GIS QGisAppInterface instance.
        :type iface: QGisAppInterface

        :param parent: Parent widget of this dialog
        :type parent: QWidget

        :param dock: Optional dock widget instance that we can notify of
            changes to the keywords.
        :type dock: Dock

        :param qsetting: String to specify the QSettings. By default,
            use empty string.
        :type qsetting: str
        """

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.setWindowTitle(self.tr('InaSAFE %s Options' % get_version()))
        # Save reference to the QGIS interface and parent
        self.iface = iface
        self.parent = parent
        self.dock = dock
        if qsetting:
            self.settings = QtCore.QSettings(qsetting)
        else:
            self.settings = QtCore.QSettings()

        # InaSAFE default values
        self.default_value_parameters = []
        self.default_value_parameter_container = None

        # List of setting key and control
        self.boolean_settings = {
            # 'useThreadingFlag': self.
            'visibleLayersOnlyFlag': self.cbxVisibleLayersOnly,
            'set_layer_from_title_flag': self.cbxSetLayerNameFromTitle,
            'setZoomToImpactFlag': self.cbxZoomToImpact,
            'setHideExposureFlag': self.cbxHideExposure,
            'useSelectedFeaturesOnly': self.cbxUseSelectedFeaturesOnly,
            'useSentry': self.cbxUseSentry,
            'template_warning_verbose': self.template_warning_checkbox,
            'showOrganisationLogoInDockFlag':
                self.organisation_on_dock_checkbox,
            'developer_mode': self.cbxDevMode
        }
        self.text_settings = {
            'keywordCachePath': self.leKeywordCachePath,
            'ISO19115_ORGANIZATION': self.iso19115_organization_le,
            'ISO19115_URL': self.iso19115_url_le,
            'ISO19115_EMAIL': self.iso19115_email_le,
            'ISO19115_TITLE': self.iso19115_title_le,
            'ISO19115_LICENSE': self.iso19115_license_le,
        }

        # Set up things for context help
        self.help_button = self.button_box.button(QtGui.QDialogButtonBox.Help)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)
        self.main_stacked_widget.setCurrentIndex(1)

        # Hide not implemented group
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

    def save_boolean_setting(self, key, check_box):
        """Save boolean setting according to check_box state.

        :param key: Key to retrieve setting value.
        :type key: str

        :param check_box: Check box to show and set the setting.
        :type check_box: PyQt4.QtGui.QCheckBox.QCheckBox
        """
        self.settings.setValue('inasafe/%s' % key, check_box.isChecked())

    def restore_boolean_setting(self, key, check_box):
        """Set check_box according to setting of key.

        :param key: Key to retrieve setting value.
        :type key: str

        :param check_box: Check box to show and set the setting.
        :type check_box: PyQt4.QtGui.QCheckBox.QCheckBox
        """
        flag = bool(self.settings.value(
            'inasafe/%s' % key, inasafe_default_settings[key], type=bool))
        check_box.setChecked(flag)

    def save_text_setting(self, key, line_edit):
        """Save text setting according to line_edit value.

        :param key: Key to retrieve setting value.
        :type key: str

        :param line_edit: Line edit for user to edit the setting
        :type line_edit: PyQt4.QtGui.QLineEdit.QLineEdit
        """
        self.settings.setValue('inasafe/%s' % key, line_edit.text())

    def restore_text_setting(self, key, line_edit):
        """Set line_edit text according to setting of key

        :param key: Key to retrieve setting value.
        :type key: str

        :param line_edit: Line edit for user to edit the setting
        :type line_edit: PyQt4.QtGui.QLineEdit.QLineEdit
        """
        value = self.settings.value(
            'inasafe/%s' % key, inasafe_default_settings[key], type=str)
        line_edit.setText(value)

    def restore_state(self):
        """Reinstate the options based on the user's stored session info."""
        flag = False
        self.cbxUseThread.setChecked(flag)

        # Restore boolean setting as check box.
        for key, check_box in self.boolean_settings.items():
            self.restore_boolean_setting(key, check_box)

        # Restore text setting as line edit.
        for key, line_edit in self.text_settings.items():
            self.restore_text_setting(key, line_edit)

        # Restore Organisation Logo Path
        org_logo_path = self.settings.value(
            'inasafe/organisation_logo_path',
            supporters_logo_path(),
            type=str)
        custom_org_logo_flag = (
            org_logo_path != supporters_logo_path())
        self.custom_org_logo_checkbox.setChecked(custom_org_logo_flag)
        self.leOrganisationLogoPath.setText(org_logo_path)

        # User Directory
        user_directory_path = self.settings.value(
            'inasafe/defaultUserDirectory',
            temp_dir('impacts'), type=str)
        custom_user_directory_flag = (
            user_directory_path != temp_dir('impacts'))
        self.custom_UseUserDirectory_checkbox.setChecked(
            custom_user_directory_flag)
        self.splitter_user_directory.setEnabled(custom_user_directory_flag)
        self.leUserDirectoryPath.setText(user_directory_path)

        # Earthquake function.
        # Populate the combobox first.
        for model in EARTHQUAKE_FUNCTIONS:
            self.earthquake_function.addItem(model['name'], model['key'])

        # Then make selected the default one.
        default_earthquake_function = setting('earthquake_function', str)
        keys = [model['key'] for model in EARTHQUAKE_FUNCTIONS]
        if default_earthquake_function not in keys:
            default_earthquake_function = EARTHQUAKE_FUNCTIONS[0]['key']
        index = self.earthquake_function.findData(default_earthquake_function)
        self.earthquake_function.setCurrentIndex(index)

        # Restore North Arrow Image Path
        north_arrow_path = self.settings.value(
            'inasafe/north_arrow_path', default_north_arrow_path(), type=str)
        custom_north_arrow_flag = (
            north_arrow_path != default_north_arrow_path())
        self.custom_north_arrow_checkbox.setChecked(custom_north_arrow_flag)
        self.leNorthArrowPath.setText(north_arrow_path)

        # Restore Report Template Directory Path
        report_template_dir = self.settings.value(
            'inasafe/reportTemplatePath', '', type=str)
        custom_templates_dir_flag = (report_template_dir != '')
        self.custom_templates_dir_checkbox.setChecked(
            custom_templates_dir_flag)
        self.leReportTemplatePath.setText(report_template_dir)

        # Restore Disclaimer
        org_disclaimer = self.settings.value(
            'inasafe/reportDisclaimer', disclaimer(), type=str)
        custom_org_disclaimer_flag = (org_disclaimer != disclaimer())
        self.custom_org_disclaimer_checkbox.setChecked(
            custom_org_disclaimer_flag)
        self.txtDisclaimer.setPlainText(org_disclaimer)

        # Restore InaSAFE default values
        self.restore_default_values_page()

    def save_state(self):
        """Store the options into the user's stored session info."""
        # Save boolean settings
        for key, check_box in self.boolean_settings.items():
            self.save_boolean_setting(key, check_box)
        # Save text settings
        for key, line_edit in self.text_settings.items():
            self.save_text_setting(key, line_edit)

        self.settings.setValue(
            'inasafe/useThreadingFlag', False)

        self.settings.setValue(
            'inasafe/north_arrow_path',
            self.leNorthArrowPath.text())
        self.settings.setValue(
            'inasafe/organisation_logo_path',
            self.leOrganisationLogoPath.text())
        self.settings.setValue(
            'inasafe/reportTemplatePath',
            self.leReportTemplatePath.text())
        self.settings.setValue(
            'inasafe/reportDisclaimer',
            self.txtDisclaimer.toPlainText())
        self.settings.setValue(
            'inasafe/defaultUserDirectory',
            self.leUserDirectoryPath.text())
        index = self.earthquake_function.currentIndex()
        value = self.earthquake_function.itemData(index)
        set_setting('earthquake_function', value)

        # Save InaSAFE default values
        self.save_default_values()

    def accept(self):
        """Method invoked when OK button is clicked."""
        self.save_state()
        # FIXME: Option dialog should be independent from dock.
        if self.dock:
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
            inasafe_default_settings['keywordCachePath'],
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
            self.tr(
                'Portable Network Graphics files (*.png *.PNG);;'
                'JPEG Images (*.jpg *.jpeg);;'
                'GIF Images (*.gif *.GIF);;'
                'SVG Images (*.svg *.SVG);;'))
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
            self.tr(
                'Portable Network Graphics files (*.png *.PNG);;'
                'JPEG Images (*.jpg *.jpeg);;'
                'GIF Images (*.gif *.GIF);;'
                'SVG Images (*.svg *.SVG);;'))
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
        is_checked = self.custom_org_logo_checkbox.isChecked()
        if is_checked:
            # Use previous org logo path
            path = self.settings.value(
                'inasafe/organisation_logo_path',
                supporters_logo_path(),
                type=str)
        else:
            # Set organisation path line edit to default one
            path = supporters_logo_path()

        self.leOrganisationLogoPath.setText(path)
        self.splitter_org_logo.setEnabled(is_checked)

    def set_north_arrow(self):
        """Auto-connect slot activated when north arrow checkbox is toggled."""
        is_checked = self.custom_north_arrow_checkbox.isChecked()
        if is_checked:
            # Show previous north arrow path
            path = self.settings.value(
                'inasafe/north_arrow_path',
                default_north_arrow_path(),
                type=str)
        else:
            # Set the north arrow line edit to default one
            path = default_north_arrow_path()

        self.leNorthArrowPath.setText(path)
        self.splitter_north_arrow.setEnabled(is_checked)

    def set_user_dir(self):
        """Auto-connect slot activated when user dir checkbox is toggled.
        """
        is_checked = self.custom_UseUserDirectory_checkbox.isChecked()
        if is_checked:
            # Show previous templates dir
            path = self.settings.value(
                'inasafe/defaultUserDirectory', '', type=str)
        else:
            # Set the template report dir to ''
            path = temp_dir('impacts')

        self.leUserDirectoryPath.setText(path)
        self.splitter_user_directory.setEnabled(is_checked)

    def set_templates_dir(self):
        """Auto-connect slot activated when templates dir checkbox is toggled.
        """
        is_checked = self.custom_templates_dir_checkbox.isChecked()
        if is_checked:
            # Show previous templates dir
            path = self.settings.value(
                'inasafe/reportTemplatePath', '', type=str)
        else:
            # Set the template report dir to ''
            path = ''

        self.leReportTemplatePath.setText(path)
        self.splitter_custom_report.setEnabled(is_checked)

    def set_org_disclaimer(self):
        """Auto-connect slot activated when org disclaimer checkbox is toggled.
        """
        is_checked = self.custom_org_disclaimer_checkbox.isChecked()
        if is_checked:
            # Show previous organisation disclaimer
            org_disclaimer = self.settings.value(
                'inasafe/reportDisclaimer', disclaimer(), type=str)
        else:
            # Set the organisation disclaimer to the default one
            org_disclaimer = disclaimer()

        self.txtDisclaimer.setPlainText(org_disclaimer)
        self.txtDisclaimer.setEnabled(is_checked)

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

    def restore_default_values_page(self):
        """Setup UI for default values setting."""
        default_fields = all_default_fields()
        for default_field in default_fields:
            if default_field.get('type') == QVariant.Double:
                parameter = FloatParameter()
            elif default_field.get('type') in qvariant_whole_numbers:
                parameter = IntegerParameter()
            else:
                continue
            default_value = default_field.get('default_value')
            if not default_value:
                message = (
                    'InaSAFE default field %s does not have default value'
                    % default_field.get('name'))
                LOGGER.exception(message)
                continue

            parameter.guid = default_field.get('key')
            parameter.name = default_value.get('name')
            parameter.is_required = True
            parameter.precision = default_field.get('precision')
            parameter.minimum_allowed_value = default_value.get(
                'min_value', 0)
            parameter.maximum_allowed_value = default_value.get(
                'max_value', 100000000)
            parameter.help_text = default_value.get('description')
            # Current value
            qsetting_default_value = get_inasafe_default_value_qsetting(
                self.settings, GLOBAL, default_field['key'])

            # To avoid python error
            if qsetting_default_value > parameter.maximum_allowed_value:
                qsetting_default_value = parameter.maximum_allowed_value
            if qsetting_default_value < parameter.minimum_allowed_value:
                qsetting_default_value = parameter.minimum_allowed_value

            parameter.value = qsetting_default_value

            self.default_value_parameters.append(parameter)

        description_text = tr(
            'In this options you can change the global default values for '
            'these variables.')
        self.default_value_parameter_container = ParameterContainer(
            self.default_value_parameters, description_text=description_text)
        self.default_value_parameter_container.setup_ui()
        self.default_values_layout.addWidget(
            self.default_value_parameter_container)

    def save_default_values(self):
        """Save InaSAFE default values."""
        parameters = self.default_value_parameter_container.get_parameters()
        for parameter in parameters:
            set_inasafe_default_value_qsetting(
                self.settings,
                GLOBAL,
                parameter.guid,
                parameter.value
            )
