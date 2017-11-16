# coding=utf-8
"""This is a dialog to print a custom map report.
"""
import logging
import os

from os.path import join, exists
from PyQt4 import QtGui, QtCore, QtXml
from qgis.core import QgsApplication, QgsExpressionContextUtils

from safe import messaging as m
from safe.common.signals import send_error_message, send_static_message
from safe.definitions.constants import ANALYSIS_FAILED_BAD_CODE
from safe.definitions.reports import (
    pdf_product_tag, final_product_tag, html_product_tag, qpt_product_tag)
from safe.definitions.reports.components import (
    map_report,
    infographic_report,
    standard_impact_report_metadata_pdf,
    all_default_report_components)
from safe.definitions.utilities import (
    override_component_template, definition, update_template_component)
from safe.gui.tools.help.impact_report_help import impact_report_help
from safe.messaging import styles
from safe.report.impact_report import ImpactReport
from safe.report.report_metadata import ReportMetadata
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

        :param iface: A Quantum GIS QGisAppInterface instance.
        :type iface: QGisAppInterface

        :param parent: Parent widget of this dialog
        :type parent: QWidget

        :param dock: Optional dock widget instance that we can notify of
            changes to the keywords.
        :type dock: Dock

        .. versionadded: 4.3.0
        """

        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        # additional buttons
        self.button_print_pdf = QtGui.QPushButton(self.tr('Print as PDF'))
        self.button_print_pdf.setObjectName('button_print_pdf')
        self.button_print_pdf.setToolTip(self.tr(
            'Write report to PDF and open it in default viewer'))
        self.button_box.addButton(
            self.button_print_pdf, QtGui.QDialogButtonBox.ActionRole)

        self.button_open_composer = QtGui.QPushButton(
            self.tr('Open in composer'))
        self.button_open_composer.setObjectName('button_open_composer')
        self.button_open_composer.setToolTip(
            self.tr('Prepare report and open it in QGIS composer'))
        self.button_box.addButton(
            self.button_open_composer, QtGui.QDialogButtonBox.ActionRole)

        self.template_chooser.clicked.connect(self.template_chooser_clicked)
        self.button_print_pdf.clicked.connect(self.accept)
        self.button_open_composer.clicked.connect(self.accept)

        # Save reference to the QGIS interface and parent
        self.iface = iface
        self.parent = parent
        self.dock = dock
        self.impact_function = impact_function

        self.create_pdf = False

        self.default_template_radio.toggled.connect(
            self.toggle_template_selectors)

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
        self.custom_template_radio.setChecked(not flag)

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
                os.path.join(report_path, 'output'),
                products,
                product.key)
            if isinstance(path, list):
                for p in path:
                    paths.append(p)
            elif isinstance(path, dict):
                for p in path.itervalues():
                    paths.append(p)
            else:
                paths.append(path)
        if suffix:
            paths = [p for p in paths if p.endswith(suffix)]

        paths = [p for p in paths if os.path.exists(p)]
        return paths

    def print_as_pdf(self):
        """Print the selected report as a PDF product.

        .. versionadded: 4.3.0
        """
        impact_layer = self.impact_function.analysis_impacted

        # Get output path from datastore
        # Fetch report for pdfs report
        report_path = os.path.dirname(impact_layer.source())

        # Get the hazard and exposure definition used in current IF
        hazard = definition(
            QgsExpressionContextUtils.projectScope().variable(
                'hazard_keywords__hazard'))
        exposure = definition(
            QgsExpressionContextUtils.projectScope().variable(
                'exposure_keywords__exposure'))

        standard_impact_report_metadata = ReportMetadata(
            metadata_dict=standard_impact_report_metadata_pdf)
        standard_map_report_metadata = ReportMetadata(
            metadata_dict=update_template_component(
                component=map_report,
                hazard=hazard,
                exposure=exposure
            ))
        standard_infographic_report_metadata = ReportMetadata(
            metadata_dict=update_template_component(infographic_report))

        impact_report = self.impact_function.impact_report
        custom_map_report_metadata = impact_report.metadata

        standard_report_metadata = [
            standard_impact_report_metadata,
            standard_map_report_metadata,
            standard_infographic_report_metadata,
            custom_map_report_metadata
        ]

        def retrieve_components(tags):
            """Retrieve components from report metadata."""
            products = []
            for report_metadata in standard_report_metadata:
                products += (report_metadata.component_by_tags(tags))
            return products

        def wrap_output_paths(paths):
            """Make sure the file paths can wrap nicely."""
            return [p.replace(os.sep, '<wbr>' + os.sep) for p in paths]

        pdf_products = retrieve_components(
            [final_product_tag, pdf_product_tag])
        pdf_output_paths = self.retrieve_paths(
            pdf_products, report_path=report_path, suffix='.pdf')

        html_products = retrieve_components(
            [final_product_tag, html_product_tag])
        html_output_paths = self.retrieve_paths(
            html_products, report_path=report_path, suffix='.html')

        qpt_products = retrieve_components(
            [final_product_tag, qpt_product_tag])
        qpt_output_paths = self.retrieve_paths(
            qpt_products, report_path=report_path, suffix='.qpt')

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

            for path in wrap_output_paths(pdf_output_paths):
                status.add(m.Paragraph(path))

            status.add(m.Paragraph(
                m.ImportantText(
                    self.dock.tr('The generated htmls were saved as:'))))

            for path in wrap_output_paths(html_output_paths):
                status.add(m.Paragraph(path))

            status.add(m.Paragraph(
                m.ImportantText(
                    self.dock.tr('The generated qpts were saved as:'))))

            for path in wrap_output_paths(qpt_output_paths):
                status.add(m.Paragraph(path))

            send_static_message(self.dock, status)

        for path in pdf_output_paths:
            # noinspection PyCallByClass,PyTypeChecker,PyTypeChecker
            QtGui.QDesktopServices.openUrl(
                QtCore.QUrl.fromLocalFile(path))

    def open_in_composer(self):
        """Open map in composer given MapReport instance.

        .. versionadded: 4.3.0
        """
        impact_layer = self.impact_function.analysis_impacted
        report_path = os.path.dirname(impact_layer.source())

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
                    self.tr('InaSAFE'),
                    self.tr('Error loading template: %s') % template_path)

                return

    def accept(self):
        """Method invoked when OK button is clicked."""

        self.save_state()
        # Get selected template path to use
        if self.default_template_radio.isChecked():
            self.selected_template_path = self.template_combo.itemData(
                self.template_combo.currentIndex())
        else:
            self.selected_template_path = self.template_path.text()
            if not exists(self.selected_template_path):
                # noinspection PyCallByClass,PyTypeChecker
                QtGui.QMessageBox.warning(
                    self,
                    self.tr('InaSAFE'),
                    self.tr('Please select a valid template before printing. '
                            'The template you choose does not exist.'))

        self.dock.show_busy()

        # The order of the components are matter.
        generated_components = all_default_report_components + [
            override_component_template(
                map_report, self.selected_template_path)]
        error_code, message = self.impact_function.generate_report(
            generated_components, iface=self.iface)

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
                self.print_as_pdf()
            else:
                self.create_pdf = False
                self.open_in_composer()
            self.dock.hide_busy()
        except Exception:
            self.dock.hide_busy()

        QtGui.QDialog.accept(self)

    def template_chooser_clicked(self):
        """Auto-connect slot activated when report file tool button is clicked.

        .. versionadded: 4.3.0
        """
        # noinspection PyCallByClass,PyTypeChecker
        file_name = QtGui.QFileDialog.getOpenFileName(
            self,
            self.tr('Select report'),
            '',
            self.tr('QGIS composer templates (*.qpt *.QPT)'))
        self.template_path.setText(file_name)

    def toggle_template_selectors(self, checked):
        if checked:
            self.template_combo.setEnabled(True)
            self.template_path.setEnabled(False)
            self.template_chooser.setEnabled(False)
        else:
            self.template_combo.setEnabled(False)
            self.template_path.setEnabled(True)
            self.template_chooser.setEnabled(True)

    def help_toggled(self, flag):
        """Show or hide the help tab in the stacked widget.

        :param flag: Flag indicating whether help should be shown or hidden.
        :type flag: bool

        .. versionadded: 4.3.0
        """
        if flag:
            self.help_button.setText(self.tr('Hide Help'))
            self.show_help()
        else:
            self.help_button.setText(self.tr('Show Help'))
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
