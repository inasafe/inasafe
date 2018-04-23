# coding=utf-8
"""This is a dialog to print a custom map report.
"""
import logging
from copy import deepcopy
from os import listdir
from os.path import join, exists, splitext, dirname

from qgis.PyQt import QtGui, QtCore, QtXml
from qgis.core import QgsApplication

from safe import messaging as m
from safe.common.signals import send_error_message, send_static_message
from safe.definitions.constants import ANALYSIS_FAILED_BAD_CODE
from safe.definitions.exposure import exposure_population
from safe.definitions.reports import (
    pdf_product_tag, final_product_tag, html_product_tag, qpt_product_tag)
from safe.definitions.reports.components import (
    map_report,
    infographic_report,
    standard_impact_report_metadata_pdf,
    all_default_report_components,
    standard_multi_exposure_impact_report_metadata_pdf,
    impact_report_pdf_component,
    action_checklist_pdf_component,
    analysis_provenance_details_pdf_component)
from safe.definitions.utilities import (
    override_component_template, definition, update_template_component)
from safe.gui.tools.help.impact_report_help import impact_report_help
from safe.impact_function.impact_function_utilities import report_urls
from safe.impact_function.multi_exposure_wrapper import (
    MultiExposureImpactFunction)
from safe.messaging import styles
from safe.report.impact_report import ImpactReport
from safe.report.report_metadata import (
    QgisComposerComponentsMetadata)
from safe.utilities.i18n import tr
from safe.utilities.resources import (
    get_ui_class, resources_path, html_header, html_footer)
from safe.utilities.settings import setting

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

INFO_STYLE = styles.BLUE_LEVEL_4_STYLE
FORM_CLASS = get_ui_class('print_report_dialog.ui')
LOGGER = logging.getLogger('InaSAFE')


class PrintReportDialog(QtGui.QDialog, FORM_CLASS):
    """Print report dialog for the InaSAFE plugin."""

    def __init__(self, impact_function, iface, dock=None, parent=None):
        """Constructor for the dialog.

        :param iface: A Quantum GIS QgisAppInterface instance.
        :type iface: QgisAppInterface

        :param parent: Parent widget of this dialog
        :type parent: QWidget

        :param dock: Optional dock widget instance that we can notify of
            changes to the keywords.
        :type dock: Dock

        .. versionadded: 4.3.0
        """

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        # Save reference to the QGIS interface and parent
        self.iface = iface
        self.parent = parent
        self.dock = dock
        self.impact_function = impact_function

        self.create_pdf = False

        self.all_checkboxes = {
            impact_report_pdf_component['key']:
                self.impact_summary_checkbox,
            action_checklist_pdf_component['key']:
                self.action_checklist_checkbox,
            analysis_provenance_details_pdf_component['key']:
                self.provenance_checkbox,
            infographic_report['key']:
                self.infographic_checkbox
        }

        # setup checkboxes, all checkboxes are checked by default
        for checkbox in list(self.all_checkboxes.values()):
            checkbox.setChecked(True)

        # override template is selected by default
        self.default_template_radio.setChecked(True)

        self.is_population = False
        self.is_multi_exposure = isinstance(
            self.impact_function, MultiExposureImpactFunction)

        override_template_found = None
        population_found = False
        if self.is_multi_exposure:
            self.override_template_radio.setEnabled(False)
            self.override_template_label.setEnabled(False)
            self.override_template_found_label.setEnabled(False)
            # below features are currently not applicable for multi-exposure IF
            self.action_checklist_checkbox.setEnabled(False)
            self.action_checklist_checkbox.setChecked(False)
            self.provenance_checkbox.setEnabled(False)
            self.provenance_checkbox.setChecked(False)

            provenances = [
                analysis.provenance for analysis in (
                    self.impact_function.impact_functions)]
            for provenance in provenances:
                exposure_keywords = provenance['exposure_keywords']
                exposure_type = definition(exposure_keywords['exposure'])
                if exposure_type == exposure_population:
                    population_found = True
                    break
            self.infographic_checkbox.setEnabled(population_found)
            self.infographic_checkbox.setChecked(population_found)

        else:
            # search for available override template
            hazard_type = definition(
                self.impact_function.provenance['hazard_keywords'][
                    'hazard'])
            exposure_type = definition(
                self.impact_function.provenance['exposure_keywords'][
                    'exposure'])
            # noinspection PyArgumentList
            custom_template_dir = join(
                QgsApplication.qgisSettingsDirPath(), 'inasafe')
            if exists(custom_template_dir) and hazard_type and exposure_type:
                for filename in listdir(custom_template_dir):

                    file_name, file_format = splitext(filename)
                    if file_format[1:] != (
                            QgisComposerComponentsMetadata.OutputFormat.QPT):
                        continue
                    if hazard_type['key'] in file_name and (
                            exposure_type['key'] in file_name):
                        override_template_found = filename

            # check for population exposure
            self.is_population = exposure_type == exposure_population

        self.infographic_checkbox.setEnabled(
            self.is_population or population_found)

        if override_template_found:
            string_format = tr('*Template override found: {template_path}')
            self.override_template_found_label.setText(
                string_format.format(template_path=override_template_found))
        else:
            self.override_template_radio.setEnabled(False)

        # additional buttons
        self.button_print_pdf = QtGui.QPushButton(tr('Open as PDF'))
        self.button_print_pdf.setObjectName('button_print_pdf')
        self.button_print_pdf.setToolTip(tr(
            'Write report to PDF and open it in default viewer'))
        self.button_box.addButton(
            self.button_print_pdf, QtGui.QDialogButtonBox.ActionRole)

        self.template_chooser.clicked.connect(self.template_chooser_clicked)
        self.button_print_pdf.clicked.connect(self.accept)
        self.button_open_composer.clicked.connect(self.accept)

        # self.no_map_radio.toggled.connect(self.toggle_template_selector)
        # self.no_map_radio.toggled.connect(
        #     self.button_open_composer.setDisabled)
        self.default_template_radio.toggled.connect(
            self.toggle_template_selector)
        self.override_template_radio.toggled.connect(
            self.toggle_template_selector)
        self.search_directory_radio.toggled.connect(
            self.toggle_template_selector)
        self.search_on_disk_radio.toggled.connect(
            self.toggle_template_selector)

        # Set up things for context help
        self.help_button = self.button_box.button(QtGui.QDialogButtonBox.Help)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)
        self.main_stacked_widget.setCurrentIndex(1)

        self.unwanted_templates = ['merged_report.qpt', 'infographic.qpt']

        # Load templates from resources...
        template_dir_path = resources_path('qgis-composer-templates')
        self.populate_template_combobox(
            template_dir_path, self.unwanted_templates)

        #  ...and user directory
        default_path = join(QgsApplication.qgisSettingsDirPath(), 'inasafe')
        path = setting(
            'inasafe/reportTemplatePath', default_path, expected_type=str)

        if exists(path):
            self.populate_template_combobox(path)

        self.restore_state()

    def populate_template_combobox(self, path, unwanted_templates=None):
        """Helper method for populating template combobox.

        :param unwanted_templates: List of templates that isn't an option.
        :type unwanted_templates: list

        .. versionadded: 4.3.0
        """
        templates_dir = QtCore.QDir(path)
        templates_dir.setFilter(
            QtCore.QDir.Files |
            QtCore.QDir.NoSymLinks |
            QtCore.QDir.NoDotAndDotDot)
        templates_dir.setNameFilters(['*.qpt', '*.QPT'])
        report_files = templates_dir.entryList()
        if not unwanted_templates:
            unwanted_templates = []
        for unwanted_template in unwanted_templates:
            if unwanted_template in report_files:
                report_files.remove(unwanted_template)

        for f in report_files:
            self.template_combo.addItem(
                QtCore.QFileInfo(f).baseName(), path + '/' + f)

    def restore_state(self):
        """Reinstate the options based on the user's stored session info.

        .. versionadded: 4.3.0
        """
        settings = QtCore.QSettings()

        flag = bool(settings.value(
            'inasafe/useDefaultTemplates', True, type=bool))
        self.default_template_radio.setChecked(flag)

        try:
            default_template_path = resources_path(
                'qgis-composer-templates', 'inasafe-map-report-portrait.qpt')
            path = settings.value(
                'inasafe/lastTemplate',
                default_template_path,
                type=str)
            self.template_combo.setCurrentIndex(
                self.template_combo.findData(path))
        except TypeError:
            self.template_combo.setCurrentIndex(2)

        try:
            path = settings.value('inasafe/lastCustomTemplate', '', type=str)
        except TypeError:
            path = ''
        self.template_path.setText(path)

    def save_state(self):
        """Store the options into the user's stored session info.

        .. versionadded: 4.3.0
        """
        settings = QtCore.QSettings()
        settings.setValue(
            'inasafe/useDefaultTemplates',
            self.default_template_radio.isChecked())
        settings.setValue(
            'inasafe/lastTemplate',
            self.template_combo.itemData(self.template_combo.currentIndex()))
        settings.setValue(
            'inasafe/lastCustomTemplate', self.template_path.text())

    def retrieve_paths(self, products, report_path, suffix=None):
        """Helper method to retrieve path from particular report metadata.

        :param products: Report products.
        :type products: list

        :param report_path: Path of the IF output.
        :type report_path: str

        :param suffix: Expected output product file type (extension).
        :type suffix: str

        :return: List of absolute path of the output product.
        :rtype: list
        """
        paths = []
        for product in products:
            path = ImpactReport.absolute_output_path(
                join(report_path, 'output'),
                products,
                product.key)
            if isinstance(path, list):
                for p in path:
                    paths.append(p)
            elif isinstance(path, dict):
                for p in list(path.values()):
                    paths.append(p)
            else:
                paths.append(path)
        if suffix:
            paths = [p for p in paths if p.endswith(suffix)]

        paths = [p for p in paths if exists(p)]
        return paths

    def open_as_pdf(self):
        """Print the selected report as a PDF product.

        .. versionadded: 4.3.0
        """
        # Get output path from datastore
        report_urls_dict = report_urls(self.impact_function)

        # get report urls for each product tag as list
        for key, value in list(report_urls_dict.items()):
            report_urls_dict[key] = list(value.values())

        if self.dock:
            # create message to user
            status = m.Message(
                m.Heading(self.dock.tr('Map Creator'), **INFO_STYLE),
                m.Paragraph(self.dock.tr(
                    'Your PDF was created....opening using the default PDF '
                    'viewer on your system.')),
                m.ImportantText(self.dock.tr(
                    'The generated pdfs were saved '
                    'as:')))

            for path in report_urls_dict.get(pdf_product_tag['key'], []):
                status.add(m.Paragraph(path))

            status.add(m.Paragraph(
                m.ImportantText(
                    self.dock.tr('The generated htmls were saved as:'))))

            for path in report_urls_dict.get(html_product_tag['key'], []):
                status.add(m.Paragraph(path))

            status.add(m.Paragraph(
                m.ImportantText(
                    self.dock.tr('The generated qpts were saved as:'))))

            for path in report_urls_dict.get(qpt_product_tag['key'], []):
                status.add(m.Paragraph(path))

            send_static_message(self.dock, status)

        for path in report_urls_dict.get(pdf_product_tag['key'], []):
            # noinspection PyCallByClass,PyTypeChecker,PyTypeChecker
            QtGui.QDesktopServices.openUrl(
                QtCore.QUrl.fromLocalFile(path))

    def open_in_composer(self):
        """Open map in composer given MapReport instance.

        .. versionadded: 4.3.0
        """
        impact_layer = self.impact_function.analysis_impacted
        report_path = dirname(impact_layer.source())

        impact_report = self.impact_function.impact_report
        custom_map_report_metadata = impact_report.metadata
        custom_map_report_product = (
            custom_map_report_metadata.component_by_tags(
                [final_product_tag, pdf_product_tag]))

        for template_path in self.retrieve_paths(
                custom_map_report_product,
                report_path=report_path,
                suffix='.qpt'):

            composer = self.iface.createNewComposer()

            with open(template_path) as template_file:
                template_content = template_file.read()

            document = QtXml.QDomDocument()
            document.setContent(template_content)

            # load composition object
            load_status = composer.composition().loadFromTemplate(document)

            if not load_status:
                # noinspection PyCallByClass,PyTypeChecker
                QtGui.QMessageBox.warning(
                    self,
                    tr('InaSAFE'),
                    tr('Error loading template: %s') % template_path)

                return

    def prepare_components(self):
        """Prepare components that are going to be generated based on
        user options.

        :return: Updated list of components.
        :rtype: dict
        """
        # Register the components based on user option
        # First, tabular report
        generated_components = deepcopy(all_default_report_components)
        # Rohmat: I need to define the definitions here, I can't get
        # the definition using definition helper method.
        component_definitions = {
            impact_report_pdf_component['key']:
                impact_report_pdf_component,
            action_checklist_pdf_component['key']:
                action_checklist_pdf_component,
            analysis_provenance_details_pdf_component['key']:
                analysis_provenance_details_pdf_component,
            infographic_report['key']: infographic_report
        }
        duplicated_report_metadata = None
        for key, checkbox in list(self.all_checkboxes.items()):
            if not checkbox.isChecked():
                component = component_definitions[key]
                if component in generated_components:
                    generated_components.remove(component)
                    continue

                if self.is_multi_exposure:
                    impact_report_metadata = (
                        standard_multi_exposure_impact_report_metadata_pdf)
                else:
                    impact_report_metadata = (
                        standard_impact_report_metadata_pdf)

                if component in impact_report_metadata['components']:
                    if not duplicated_report_metadata:
                        duplicated_report_metadata = deepcopy(
                            impact_report_metadata)
                    duplicated_report_metadata['components'].remove(
                        component)
                    if impact_report_metadata in generated_components:
                        generated_components.remove(
                            impact_report_metadata)
                        generated_components.append(
                            duplicated_report_metadata)

        # Second, custom and map report
        # Get selected template path to use
        selected_template_path = None
        if self.search_directory_radio.isChecked():
            selected_template_path = self.template_combo.itemData(
                self.template_combo.currentIndex())
        elif self.search_on_disk_radio.isChecked():
            selected_template_path = self.template_path.text()
            if not exists(selected_template_path):
                # noinspection PyCallByClass,PyTypeChecker
                QtGui.QMessageBox.warning(
                    self,
                    tr('InaSAFE'),
                    tr(
                        'Please select a valid template before printing. '
                        'The template you choose does not exist.'))

        if map_report in generated_components:
            # if self.no_map_radio.isChecked():
            #     generated_components.remove(map_report)
            if self.default_template_radio.isChecked():
                # make sure map report is there
                generated_components.append(
                    generated_components.pop(
                        generated_components.index(map_report)))
            elif self.override_template_radio.isChecked():
                hazard_type = definition(
                    self.impact_function.provenance['hazard_keywords'][
                        'hazard'])
                exposure_type = definition(
                    self.impact_function.provenance['exposure_keywords'][
                        'exposure'])
                generated_components.remove(map_report)
                generated_components.append(
                    update_template_component(
                        component=map_report,
                        hazard=hazard_type,
                        exposure=exposure_type))
            elif selected_template_path:
                generated_components.remove(map_report)
                generated_components.append(
                    override_component_template(
                        map_report, selected_template_path))

        return generated_components

    def accept(self):
        """Method invoked when OK button is clicked."""

        self.save_state()
        self.dock.show_busy()

        # The order of the components are matter.
        components = self.prepare_components()
        error_code, message = self.impact_function.generate_report(
            components, iface=self.iface)

        if error_code == ImpactReport.REPORT_GENERATION_FAILED:
            self.dock.hide_busy()
            LOGGER.info(tr(
                'The impact report could not be generated.'))
            send_error_message(self, message)
            LOGGER.info(message.to_text())
            return ANALYSIS_FAILED_BAD_CODE, message

        sender_name = self.sender().objectName()

        try:
            if sender_name == 'button_print_pdf':
                self.create_pdf = True
                self.open_as_pdf()
            else:
                self.create_pdf = False
                self.open_in_composer()
            self.dock.hide_busy()
        except Exception:
            self.dock.hide_busy()

        QtGui.QDialog.accept(self)

    def template_chooser_clicked(self):
        """Slot activated when report file tool button is clicked.

        .. versionadded: 4.3.0
        """
        path = self.template_path.text()
        if not path:
            path = setting('lastCustomTemplate', '', str)
        if path:
            directory = dirname(path)
        else:
            directory = ''
        # noinspection PyCallByClass,PyTypeChecker
        file_name = QtGui.QFileDialog.getOpenFileName(
            self,
            tr('Select report'),
            directory,
            tr('QGIS composer templates (*.qpt *.QPT)'))
        self.template_path.setText(file_name)

    def toggle_template_selector(self):
        """Slot for template selector elements behaviour.

        .. versionadded: 4.3.0
        """
        if self.search_directory_radio.isChecked():
            self.template_combo.setEnabled(True)
        else:
            self.template_combo.setEnabled(False)

        if self.search_on_disk_radio.isChecked():
            self.template_path.setEnabled(True)
            self.template_chooser.setEnabled(True)
        else:
            self.template_path.setEnabled(False)
            self.template_chooser.setEnabled(False)

    def help_toggled(self, flag):
        """Show or hide the help tab in the stacked widget.

        :param flag: Flag indicating whether help should be shown or hidden.
        :type flag: bool

        .. versionadded: 4.3.0
        """
        if flag:
            self.help_button.setText(tr('Hide Help'))
            self.show_help()
        else:
            self.help_button.setText(tr('Show Help'))
            self.hide_help()

    def hide_help(self):
        """Hide the usage info from the user.

        .. versionadded: 4.3.0
        """
        self.main_stacked_widget.setCurrentIndex(1)

    def show_help(self):
        """Show usage info to the user.

        .. versionadded: 4.3.0
        """
        # Read the header and footer html snippets
        self.main_stacked_widget.setCurrentIndex(0)
        header = html_header()
        footer = html_footer()

        string = header

        message = impact_report_help()

        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)
