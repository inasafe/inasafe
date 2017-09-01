# coding=utf-8
"""InaSAFE Options Dialog"""

import logging
# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import

from PyQt4.QtCore import pyqtSignature, pyqtSlot, QVariant, QSettings
from PyQt4.QtGui import (
    QDialog, QFileDialog, QDialogButtonBox, QGroupBox, QVBoxLayout,
    QScrollArea, QWidget)

from parameters.qt_widgets.parameter_container import ParameterContainer
from parameters.float_parameter import FloatParameter
from parameters.integer_parameter import IntegerParameter

from safe.definitions.utilities import all_default_fields
from safe.definitions.constants import qvariant_whole_numbers, GLOBAL
from safe.definitions.default_settings import inasafe_default_settings
from safe.definitions.messages import disclaimer
from safe.definitions.fields import (
    youth_ratio_field,
    adult_ratio_field,
    elderly_ratio_field
)
from safe.definitions.field_groups import all_field_groups
from safe.common.utilities import temp_dir
from safe.defaults import supporters_logo_path, default_north_arrow_path
from safe.definitions.earthquake import EARTHQUAKE_FUNCTIONS
from safe.definitions.currencies import currencies
from safe.utilities.default_values import (
    set_inasafe_default_value_qsetting, get_inasafe_default_value_qsetting)
from safe.utilities.i18n import tr
from safe.utilities.resources import get_ui_class, html_header, html_footer
from safe.utilities.settings import setting, set_setting
from safe.common.version import get_version
from safe.gui.tools.help.options_help import options_help


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')
FORM_CLASS = get_ui_class('options_dialog_base.ui')


class OptionsDialog(QDialog, FORM_CLASS):

    """Options dialog for the InaSAFE plugin."""

    def __init__(self, iface, parent=None, qsetting=''):
        """Constructor for the dialog.

        :param iface: A Quantum GIS QGisAppInterface instance.
        :type iface: QGisAppInterface

        :param parent: Parent widget of this dialog
        :type parent: QWidget

        :param qsetting: String to specify the QSettings. By default,
            use empty string.
        :type qsetting: str
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.setWindowTitle(self.tr('InaSAFE %s Options' % get_version()))
        # Save reference to the QGIS interface and parent
        self.iface = iface
        self.parent = parent
        if qsetting:
            self.settings = QSettings(qsetting)
        else:
            self.settings = QSettings()

        # InaSAFE default values
        self.default_value_parameters = []
        self.default_value_parameter_containers = []

        # Flag for restore default values
        self.is_restore_default = False

        # List of setting key and control
        self.boolean_settings = {
            'visibleLayersOnlyFlag': self.cbxVisibleLayersOnly,
            'set_layer_from_title_flag': self.cbxSetLayerNameFromTitle,
            'setZoomToImpactFlag': self.cbxZoomToImpact,
            'set_show_only_impact_on_report': self.cbx_show_only_impact,
            'print_atlas_report': self.cbx_print_atlas_report,
            'setHideExposureFlag': self.cbxHideExposure,
            'useSelectedFeaturesOnly': self.cbxUseSelectedFeaturesOnly,
            'useSentry': self.cbxUseSentry,
            'template_warning_verbose': self.template_warning_checkbox,
            'showOrganisationLogoInDockFlag':
                self.organisation_on_dock_checkbox,
            'developer_mode': self.cbxDevMode,
            'generate_report': self.checkbox_generate_reports,
            'memory_profile': self.check_box_memory
        }
        self.text_settings = {
            'keywordCachePath': self.leKeywordCachePath,
            'ISO19115_ORGANIZATION': self.iso19115_organization_le,
            'ISO19115_URL': self.iso19115_url_le,
            'ISO19115_EMAIL': self.iso19115_email_le,
            'ISO19115_LICENSE': self.iso19115_license_le,
        }

        # Set up things for context help
        self.help_button = self.button_box.button(QDialogButtonBox.Help)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)
        self.main_stacked_widget.setCurrentIndex(1)

        # Always set first tab to be open, 0-th index
        self.tabWidget.setCurrentIndex(0)

        # Hide not implemented group
        self.grpNotImplemented.hide()
        self.adjustSize()

        # Demographic tab
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.widget_container = QWidget()
        self.scroll_area.setWidget(self.widget_container)
        self.container_layout = QVBoxLayout()
        self.widget_container.setLayout(self.container_layout)
        self.default_values_layout.addWidget(self.scroll_area)

        self.restore_state()

        # Hide checkbox if not developers
        if not self.cbxDevMode.isChecked():
            self.checkbox_generate_reports.hide()

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

        # Set up listener for restore defaults button
        self.restore_defaults = self.button_box_restore_defaults.button(
            QDialogButtonBox.RestoreDefaults)
        self.restore_defaults.setCheckable(True)
        self.restore_defaults.clicked.connect(
            self.restore_defaults_ratio)

        # TODO: Hide this until behaviour is defined
        # hide template warning toggle
        self.template_warning_checkbox.hide()

        # hide custom template dir toggle
        self.custom_templates_dir_checkbox.hide()
        self.splitter_custom_report.hide()

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
        """Set line_edit text according to setting of key.

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

        # Currency
        # Populate the currency list
        for currency in currencies:
            self.currency_combo_box.addItem(currency['name'], currency['key'])

        # Then make selected the default one.
        default_currency = setting('currency', expected_type=str)
        keys = [currency['key'] for currency in currencies]
        if default_currency not in keys:
            default_earthquake_function = currencies[0]['key']
        index = self.currency_combo_box.findData(default_currency)
        self.currency_combo_box.setCurrentIndex(index)

        # Earthquake function.
        # Populate the combobox first.
        for model in EARTHQUAKE_FUNCTIONS:
            self.earthquake_function.addItem(model['name'], model['key'])

        # Then make selected the default one.
        default_earthquake_function = setting(
            'earthquake_function', expected_type=str)
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
        set_setting('earthquake_function', value, qsettings=self.settings)

        currency_index = self.currency_combo_box.currentIndex()
        currency_key = self.currency_combo_box.itemData(currency_index)
        set_setting('currency', currency_key, qsettings=self.settings)

        # Save InaSAFE default values
        self.save_default_values()

    def accept(self):
        """Method invoked when OK button is clicked."""
        self.save_state()
        super(OptionsDialog, self).accept()

    # noinspection PyPep8Naming
    @pyqtSignature('int')  # prevents actions being handled twice
    def on_earthquake_function_currentIndexChanged(self, current_index):
        """Auto-connect slot activated when earthquake model is changed."""
        self.label_earthquake_model()
        model = EARTHQUAKE_FUNCTIONS[current_index]
        notes = ''
        for note in model['notes']:
            notes += note + '\n\n'

        citations = ''
        for citation in model['citations']:
            citations += citation['text'] + '\n\n'

        text = tr('Description:\n\n%s\n\n'
            'Notes:\n\n%s\n\n'
            'Citations:\n\n%s') % (
            model['description'],
            notes,
            citations)

        self.earthquake_fatality_model_notes.setText(text)

    def label_earthquake_model(self):
        model = self.earthquake_function.currentText()
        help_text = tr(
            'Please select your preferred earthquake fatality model. The '
            'default fatality model is the {model}.').format(model=model)
        self.label_default_earthquake.setText(help_text)

    # noinspection PyPep8Naming
    @pyqtSignature('')  # prevents actions being handled twice
    def on_toolKeywordCachePath_clicked(self):
        """Auto-connect slot activated when cache file tool button is clicked.
        """
        # noinspection PyCallByClass,PyTypeChecker
        file_name = QFileDialog.getSaveFileName(
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
        dir_name = QFileDialog.getExistingDirectory(
            self,
            self.tr('Results directory'),
            '',
            QFileDialog.ShowDirsOnly)
        self.leUserDirectoryPath.setText(dir_name)

    # noinspection PyPep8Naming
    @pyqtSignature('')  # prevents actions being handled twice
    def on_toolNorthArrowPath_clicked(self):
        """Auto-connect slot activated when north arrow tool button is clicked.
        """
        # noinspection PyCallByClass,PyTypeChecker
        file_name = QFileDialog.getOpenFileName(
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
        file_name = QFileDialog.getOpenFileName(
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
        dir_name = QFileDialog.getExistingDirectory(
            self,
            self.tr('Templates directory'),
            '',
            QFileDialog.ShowDirsOnly)
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
        # Clear parameters so it doesn't add parameters when
        # restore from changes.
        if self.default_value_parameters:
            self.default_value_parameters = []
        if self.default_value_parameter_containers:
            self.default_value_parameter_containers = []

        default_fields = all_default_fields()

        for field_group in all_field_groups:
            settable_fields = []
            for field in field_group['fields']:
                if field not in default_fields:
                    continue
                else:
                    settable_fields.append(field)
                    default_fields.remove(field)

            if not settable_fields:
                continue
            # Create group box for each field group
            group_box = QGroupBox(self)
            group_box.setTitle(field_group['name'])
            self.container_layout.addWidget(group_box)
            parameters = []
            for settable_field in settable_fields:
                parameter = self.default_field_to_parameter(settable_field)
                if parameter:
                    parameters.append(parameter)
            parameter_container = ParameterContainer(
                parameters, description_text=field_group['description']
            )
            parameter_container.setup_ui(must_scroll=False)
            group_box_inner_layout = QVBoxLayout()
            group_box_inner_layout.addWidget(parameter_container)
            group_box.setLayout(group_box_inner_layout)

            # Add to attribute
            self.default_value_parameter_containers.append(parameter_container)

        # Only show non-groups default fields if there is one
        if len(default_fields) > 0:
            for default_field in default_fields:
                parameter = self.default_field_to_parameter(default_field)
                if parameter:
                    self.default_value_parameters.append(parameter)

            description_text = tr(
                'In this options you can change the global default values for '
                'these variables.')
            parameter_container = ParameterContainer(
                self.default_value_parameters,
                description_text=description_text)
            parameter_container.setup_ui(must_scroll=False)
            self.other_group_box = QGroupBox(tr('Non-group fields'))
            other_group_inner_layout = QVBoxLayout()
            other_group_inner_layout.addWidget(parameter_container)
            self.other_group_box.setLayout(other_group_inner_layout)
            self.container_layout.addWidget(self.other_group_box)

            # Add to attribute
            self.default_value_parameter_containers.append(parameter_container)

    def age_ratios(self):
        """Helper to get list of age ratio from the options dialog.

        :returns: List of age ratio.
        :rtype: list
        """
        # FIXME(IS) set a correct parameter container
        parameter_container = None

        youth_ratio = parameter_container.get_parameter_by_guid(
            youth_ratio_field['key']).value
        adult_ratio = parameter_container.get_parameter_by_guid(
            adult_ratio_field['key']).value
        elderly_ratio = parameter_container.get_parameter_by_guid(
            elderly_ratio_field['key']).value
        ratios = [youth_ratio, adult_ratio, elderly_ratio]

        return ratios

    def is_good_age_ratios(self):
        """Method to check the sum of age ratio is 1.

        :returns: True if the sum is 1 or the sum less than 1 but there is
            None.
        :rtype: bool
        """
        ratios = self.age_ratios()

        if None in ratios:
            # If there is None, just check to not exceeding 1
            clean_ratios = [x for x in ratios if x is not None]
            ratios.remove(None)
            if sum(clean_ratios) > 1:
                return False
        else:
            if sum(ratios) != 1:
                return False

        return True

    def save_default_values(self):
        """Save InaSAFE default values."""
        for parameter_container in self.default_value_parameter_containers:
            parameters = parameter_container.get_parameters()
            for parameter in parameters:
                set_inasafe_default_value_qsetting(
                    self.settings,
                    GLOBAL,
                    parameter.guid,
                    parameter.value
                )

    def restore_defaults_ratio(self):
        """Restore InaSAFE default ratio."""
        # Set the flag to true because user ask to.
        self.is_restore_default = True
        # remove current default ratio
        for i in reversed(range(self.container_layout.count())):
            widget = self.container_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # reload default ratio
        self.restore_default_values_page()

    def default_field_to_parameter(self, default_field):
        """Obtain parameter from default field.

        :param default_field: A default field definition.
        :type default_field: dict

        :returns: A parameter object.
        :rtype: FloatParameter, IntegerParameter
        """
        if default_field.get('type') == QVariant.Double:
            parameter = FloatParameter()
        elif default_field.get('type') in qvariant_whole_numbers:
            parameter = IntegerParameter()
        else:
            return
        default_value = default_field.get('default_value')
        if not default_value:
            message = (
                'InaSAFE default field %s does not have default value'
                % default_field.get('name'))
            LOGGER.exception(message)
            return

        parameter.guid = default_field.get('key')
        parameter.name = default_value.get('name')
        parameter.is_required = True
        parameter.precision = default_field.get('precision')
        parameter.minimum_allowed_value = default_value.get(
            'min_value', 0)
        parameter.maximum_allowed_value = default_value.get(
            'max_value', 100000000)
        parameter.help_text = default_value.get('help_text')
        parameter.description = default_value.get('description')

        # Check if user ask to restore to the most default value.
        if self.is_restore_default:
            parameter._value = default_value.get('default_value')
        else:
            # Current value
            qsetting_default_value = get_inasafe_default_value_qsetting(
                self.settings, GLOBAL, default_field['key'])

            # To avoid python error
            if qsetting_default_value > parameter.maximum_allowed_value:
                qsetting_default_value = parameter.maximum_allowed_value
            if qsetting_default_value < parameter.minimum_allowed_value:
                qsetting_default_value = parameter.minimum_allowed_value

            parameter.value = qsetting_default_value
        return parameter
