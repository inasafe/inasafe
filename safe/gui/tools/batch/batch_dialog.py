# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Script runner dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import logging
import os
import sys
from configparser import ConfigParser, MissingSectionHeaderError, Error
from datetime import datetime
from importlib import reload
from io import StringIO

from future import standard_library
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsProject,
    QgsRasterLayer,
    QgsRectangle,
    QgsVectorLayer,
    QgsApplication)
from qgis.PyQt import QtCore, QtGui
from qgis.PyQt.QtCore import Qt, pyqtSlot
from qgis.PyQt.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QPushButton,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView)

from safe.common.signals import send_error_message
from safe.common.utilities import temp_dir
from safe.datastore.folder import Folder
from safe.definitions.constants import (ANALYSIS_FAILED_BAD_CODE,
                                        ANALYSIS_FAILED_BAD_INPUT,
                                        ANALYSIS_SUCCESS, PREPARE_SUCCESS)
from safe.definitions.layer_purposes import (layer_purpose_aggregation,
                                             layer_purpose_exposure,
                                             layer_purpose_hazard)
from safe.definitions.reports.components import (all_default_report_components,
                                                 map_report,
                                                 standard_impact_report_metadata_pdf)
from safe.definitions.utilities import update_template_component
from safe.gui.tools.help.batch_help import batch_help
from safe.impact_function.impact_function import ImpactFunction
from safe.messaging import styles
from safe.report.impact_report import ImpactReport
from safe.report.report_metadata import ReportMetadata
from safe.utilities.gis import extent_string_to_array
from safe.utilities.qgis_utilities import display_critical_message_box
from safe.utilities.resources import get_ui_class, html_footer, html_header
from safe.utilities.settings import set_setting, setting

standard_library.install_aliases()

__author__ = 'bungcip@gmail.com & tim@kartoza.com & ismail@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '01/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

INFO_STYLE = styles.BLUE_LEVEL_4_STYLE
LOGGER = logging.getLogger('InaSAFE')
FORM_CLASS = get_ui_class('batch_dialog_base.ui')


class BatchDialog(QDialog, FORM_CLASS):
    """Script Dialog for InaSAFE."""

    def __init__(self, parent=None, iface=None, dock=None):
        """Constructor for the dialog.

        :param parent: Widget to use as parent.
        :type parent: PyQt5.QtWidgets.QWidget

        :param iface: A QgisAppInterface instance we use to access QGIS via.
        :type iface: QgsAppInterface

        :param dock: A Dock widget needed to run the scenarios with. On
            our road map is to figure out how to get rid of this parameter.
        :type dock: Dock
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowModality(Qt.ApplicationModal)
        self.iface = iface
        self.dock = dock

        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.Stretch)
        header_view.setSectionResizeMode(1, QHeaderView.Interactive)

        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 125)

        # select the whole row instead of one cell
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # initiate layer group creation
        self.root = QgsProject.instance().layerTreeRoot()
        # container for all layer group
        self.layer_group_container = []

        # preventing error if the user delete the directory
        self.default_directory = temp_dir()
        if not os.path.exists(self.source_directory.text()):
            self.source_directory.setText(self.default_directory)
        if not os.path.exists(self.output_directory.text()):
            self.output_directory.setText(self.default_directory)
        self.populate_table(self.source_directory.text())

        # Setting this to False will suppress the popup of the results table
        self.show_results_popup = True

        # connect signal to slot
        # noinspection PyUnresolvedReferences
        self.output_directory.textChanged.connect(self.save_state)
        # noinspection PyUnresolvedReferences
        self.source_directory.textChanged.connect(self.save_state)
        # noinspection PyUnresolvedReferences
        self.source_directory.textChanged.connect(self.populate_table)
        # noinspection PyUnresolvedReferences
        self.source_directory.textChanged.connect(
            self.update_default_output_dir)

        # Setup run all button in button box
        self.run_all_button = QPushButton('Run all')
        self.run_all_button.clicked.connect(self.run_all_clicked)
        self.button_box.addButton(
            self.run_all_button, QDialogButtonBox.ActionRole)

        # Setup run selected button in button box
        self.run_selected_button = QPushButton('Run selected')
        self.run_selected_button.clicked.connect(self.run_selected_clicked)
        self.button_box.addButton(
            self.run_selected_button, QDialogButtonBox.ActionRole)

        # Set up new project settings
        self.start_in_new_project = False

        # Set up context help
        self.help_button = self.button_box.button(QDialogButtonBox.Help)
        # Allow toggling the help button
        self.help_button.setCheckable(True)
        self.help_button.toggled.connect(self.help_toggled)
        self.main_stacked_widget.setCurrentIndex(1)

        self.restore_state()

    def restore_state(self):
        """Restore GUI state from configuration file."""
        # restore last source path
        last_source_path = setting(
            'lastSourceDir', self.default_directory, expected_type=str)
        self.source_directory.setText(last_source_path)

        # restore path pdf output
        last_output_dir = setting(
            'lastOutputDir', self.default_directory, expected_type=str)
        self.output_directory.setText(last_output_dir)

        # restore default output dir combo box
        use_default_output_dir = bool(setting(
            'useDefaultOutputDir', True, expected_type=bool))
        self.scenario_directory_radio.setChecked(
            use_default_output_dir)

    def save_state(self):
        """Save current state of GUI to configuration file."""
        set_setting('lastSourceDir', self.source_directory.text())
        set_setting('lastOutputDir', self.output_directory.text())
        set_setting(
            'useDefaultOutputDir', self.scenario_directory_radio.isChecked())

    def choose_directory(self, line_edit, title):
        """ Show a directory selection dialog.
        This function will show the dialog then set line_edit widget
        text with output from the dialog.

        :param line_edit: Widget whose text should be updated.
        :type line_edit: QLineEdit

        :param title: title of dialog
        :type title: str, QString
        """
        path = line_edit.text()
        # noinspection PyCallByClass,PyTypeChecker
        new_path = QFileDialog.getExistingDirectory(
            self, title, path, QFileDialog.ShowDirsOnly)
        if new_path is not None and os.path.exists(new_path):
            line_edit.setText(new_path)

    @pyqtSlot(str)
    def populate_table(self, scenario_directory):
        """ Populate table with files from scenario_directory directory.

        :param scenario_directory: Path where .txt & .py reside.
        :type scenario_directory: QString
        """
        parsed_files = []
        unparsed_files = []
        self.table.clearContents()

        # Block signal to allow update checking only when the table is ready
        self.table.blockSignals(True)
        # NOTE(gigih): need this line to remove existing rows
        self.table.setRowCount(0)

        if not os.path.exists(scenario_directory):
            # LOGGER.info('Scenario directory does not exist: %s' % path)
            return

        # only support .py and .txt files
        for current_path in os.listdir(scenario_directory):
            extension = os.path.splitext(current_path)[1]
            absolute_path = os.path.join(scenario_directory, current_path)

            if extension == '.py':
                append_row(self.table, current_path, absolute_path)
            elif extension == '.txt':
                # insert scenarios from file into table widget
                try:
                    scenarios = read_scenarios(absolute_path)
                    validate_scenario(scenarios, scenario_directory)
                    for key, value in list(scenarios.items()):
                        append_row(self.table, key, value)
                    parsed_files.append(current_path)
                except Error:
                    unparsed_files.append(current_path)

        # unblock signal
        self.table.blockSignals(False)
        # LOGGER.info(self.show_parser_results(parsed_files, unparsed_files))

    def run_script(self, filename):
        """ Run a python script in QGIS to exercise InaSAFE functionality.

        This functionality was originally intended for verifying that the key
        elements are InaSAFE are loading correctly and available. However,
        the utility of this function is such that you can run any arbitrary
        python scripts with it. As such you can use it it automate
        activities in QGIS, for example automatically running an impact
        assessment in response to an event.

        :param filename: the script filename.
        :type filename: str
        """
        module, _ = os.path.splitext(filename)
        if module in sys.modules:
            script = reload(sys.modules[module])
        else:
            script = __import__(module)

        # run entry function
        function = script.runScript
        if function.__code__.co_argcount == 1:
            function(self.iface)
        else:
            function()

    def reset_status(self):
        """Set all scenarios' status to empty in the table."""
        for row in range(self.table.rowCount()):
            status_item = self.table.item(row, 1)
            status_item.setText(self.tr(''))

    def prepare_task(self, items):
        """Prepare scenario for impact function variable.

        :param items: Dictionary containing settings for impact function.
        :type items: Python dictionary.

        :return: A tuple containing True and dictionary containing parameters
                 if post processor success. Or False and an error message
                 if something went wrong.
        """

        status = True
        message = ''
        # get hazard
        if 'hazard' in items:
            hazard_path = items['hazard']
            hazard = self.define_layer(hazard_path)
            if not hazard:
                status = False
                message = self.tr(
                    'Unable to find {hazard_path}').format(
                    hazard_path=hazard_path)
        else:
            hazard = None
            LOGGER.warning('Scenario does not contain hazard path')

        # get exposure
        if 'exposure' in items:
            exposure_path = items['exposure']
            exposure = self.define_layer(exposure_path)
            if not exposure:
                status = False
                if message:
                    message += '\n'
                message += self.tr(
                    'Unable to find {exposure_path}').format(
                    exposure_path=exposure_path)
        else:
            exposure = None
            LOGGER.warning('Scenario does not contain hazard path')

        # get aggregation
        if 'aggregation' in items:
            aggregation_path = items['aggregation']
            aggregation = self.define_layer(aggregation_path)
        else:
            aggregation = None
            LOGGER.info('Scenario does not contain aggregation path')

        # get extent
        if 'extent' in items:
            LOGGER.info('Extent coordinate is found')
            coordinates = items['extent']
            array_coord = extent_string_to_array(coordinates)
            extent = QgsRectangle(*array_coord)
        else:
            extent = None
            LOGGER.info('Scenario does not contain extent coordinates')

        # get extent crs id
        if 'extent_crs' in items:
            LOGGER.info('Extent CRS is found')
            crs = items['extent_crs']
            extent_crs = QgsCoordinateReferenceSystem(crs)
        else:
            LOGGER.info('Extent crs is not found, assuming crs to EPSG:4326')
            extent_crs = QgsCoordinateReferenceSystem('EPSG:4326')

        # make sure at least hazard and exposure data are available in
        # scenario. Aggregation and extent checking will be done when
        # assigning layer to impact_function
        if status:
            parameters = {
                layer_purpose_hazard['key']: hazard,
                layer_purpose_exposure['key']: exposure,
                layer_purpose_aggregation['key']: aggregation,
                'extent': extent,
                'crs': extent_crs
            }
            return True, parameters
        else:
            LOGGER.warning(message)
            display_critical_message_box(
                title=self.tr('Error while preparing scenario'),
                message=message)
            return False, None

    def define_layer(self, layer_path):
        """Create QGIS layer (either vector or raster) from file path input.

        :param layer_path: Full path to layer file.
        :type layer_path: str

        :return: QGIS layer.
        :rtype: QgsMapLayer
        """
        scenario_dir = self.source_directory.text()
        joined_path = os.path.join(scenario_dir, layer_path)
        full_path = os.path.normpath(joined_path)
        file_name = os.path.split(layer_path)[-1]

        # get extension and basename to create layer
        base_name, extension = os.path.splitext(file_name)

        # load layer in scenario
        layer = QgsRasterLayer(full_path, base_name)
        if layer.isValid():
            return layer
        else:
            layer = QgsVectorLayer(full_path, base_name, 'ogr')
            if layer.isValid():
                return layer
            # if layer is not vector nor raster
            else:
                LOGGER.warning('Input in scenario is not recognized/supported')
                return

    @staticmethod
    def set_layer_visible(layer, visible):
        """Sets a layer in the project visible or not

        :param layer: layer to change
        :type layer: QgsMapLayer

        :param visible: True to show layer, False to hide layer
        :type visible: bool
        """
        QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(visible)

    def run_task(self, task_item, status_item, count=0, index=''):
        """Run a single task.

        :param task_item: Table task_item containing task name / details.
        :type task_item: QTableWidgetItem

        :param status_item: Table task_item that holds the task status.
        :type status_item: QTableWidgetItem

        :param count: Count of scenarios that have been run already.
        :type count:

        :param index: The index for the table item that will be run.
        :type index: int

        :returns: Flag indicating if the task succeeded or not.
        :rtype: bool
        """
        self.enable_busy_cursor()
        for layer_group in self.layer_group_container:
            layer_group.setItemVisibilityChecked(False)

        # set status to 'running'
        status_item.setText(self.tr('Running'))

        # .. see also:: :func:`appendRow` to understand the next 2 lines
        variant = task_item.data(QtCore.Qt.UserRole)
        value = variant[0]
        result = True

        if isinstance(value, str):
            filename = value
            # run script
            try:
                self.run_script(filename)
                # set status to 'OK'
                status_item.setText(self.tr('Script OK'))
            except Exception as e:  # pylint: disable=W0703
                # set status to 'fail'
                status_item.setText(self.tr('Script Fail'))

                LOGGER.exception(
                    'Running macro failed. The exception: ' + str(e))
                result = False
        elif isinstance(value, dict):
            # start in new project if toggle is active
            if self.start_in_new_project:
                self.iface.newProject()
            # create layer group
            group_name = value['scenario_name']
            self.layer_group = self.root.addGroup(group_name)
            self.layer_group_container.append(self.layer_group)

            # Its a dict containing files for a scenario
            success, parameters = self.prepare_task(value)
            if not success:
                # set status to 'running'
                status_item.setText(self.tr('Please update scenario'))
                self.disable_busy_cursor()
                return False

            directory = self.output_directory.text()
            if self.scenario_directory_radio.isChecked():
                directory = self.source_directory.text()

            output_directory = os.path.join(directory, group_name)
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)

            # If impact function parameters loaded successfully, initiate IF.
            impact_function = ImpactFunction()
            impact_function.datastore = Folder(output_directory)
            impact_function.datastore.default_vector_format = "geojson"
            impact_function.hazard = parameters[layer_purpose_hazard['key']]
            impact_function.exposure = (
                parameters[layer_purpose_exposure['key']])
            if parameters[layer_purpose_aggregation['key']]:
                impact_function.aggregation = (
                    parameters[layer_purpose_aggregation['key']])
            elif parameters['extent']:
                impact_function.requested_extent = parameters['extent']
                impact_function.crs = parameters['crs']
            prepare_status, prepare_message = impact_function.prepare()
            if prepare_status == PREPARE_SUCCESS:
                LOGGER.info('Impact function ready')
                status, message = impact_function.run()
                if status == ANALYSIS_SUCCESS:
                    status_item.setText(self.tr('Analysis Success'))
                    impact_layer = impact_function.impact
                    if impact_layer.isValid():
                        layer_list = [
                            impact_layer,
                            impact_function.analysis_impacted,
                            parameters[layer_purpose_hazard['key']],
                            parameters[layer_purpose_exposure['key']],
                            parameters[layer_purpose_aggregation['key']]]
                        QgsProject.instance().addMapLayers(
                            layer_list, False)
                        for layer in layer_list:
                            self.layer_group.addLayer(layer)
                        map_canvas = QgsProject.instance().mapLayers()
                        for layer in map_canvas:
                            # turn of layer visibility if not impact layer
                            if map_canvas[layer].id() == impact_layer.id():
                                self.set_layer_visible(
                                    map_canvas[layer], True)
                            else:
                                self.set_layer_visible(
                                    map_canvas[layer], False)

                        # we need to set analysis_impacted as an active layer
                        # because we need to get all qgis variables that we
                        # need from this layer for infographic.
                        if self.iface:
                            self.iface.setActiveLayer(
                                impact_function.analysis_impacted)

                        report_directory = os.path.join(
                            output_directory, 'output')

                        # generate map report and impact report
                        try:
                            error_code, message = (
                                impact_function.generate_report(
                                    all_default_report_components,
                                    report_directory))

                        except BaseException:
                            status_item.setText(
                                self.tr('Report failed to generate.'))
                    else:
                        LOGGER.info('Impact layer is invalid')

                elif status == ANALYSIS_FAILED_BAD_INPUT:
                    LOGGER.info('Bad input detected')

                elif status == ANALYSIS_FAILED_BAD_CODE:
                    LOGGER.info('Impact function encountered a bug: %s' % message)

            else:
                LOGGER.warning('Impact function not ready')
                send_error_message(self, prepare_message)

        else:
            LOGGER.exception('Data type not supported: "%s"' % value)
            result = False

        self.disable_busy_cursor()
        return result

    def show_parser_results(self, parsed_list, unparsed_list):
        """Compile a formatted list of un/successfully parsed files.

        :param parsed_list: A list of files that were parsed successfully.
        :type parsed_list: list(str)

        :param unparsed_list: A list of files that were not parsable.
        :type unparsed_list: list(str)

        :returns: A formatted message outlining what could be parsed.
        :rtype: str
        """
        parsed_message = self.tr(
            'The file(s) below were parsed successfully:\n')
        unparsed_message = self.tr(
            'The file(s) below were not parsed successfully:\n')
        parsed_contents = '\n'.join(parsed_list)
        unparsed_contents = '\n'.join(unparsed_list)
        if parsed_contents == '':
            parsed_contents = 'No successfully parsed files\n'
        if unparsed_contents == '':
            unparsed_contents = 'No failures in parsing files\n'
        full_messages = (
            parsed_message + parsed_contents + '\n\n' +
            unparsed_message + unparsed_contents)
        return full_messages

    @pyqtSlot()
    def run_selected_clicked(self):
        """Run the selected scenario."""
        # get all selected rows
        rows = sorted(set(index.row() for index in
                          self.table.selectedIndexes()))
        self.enable_busy_cursor()
        # iterate over selected rows
        for row in rows:
            current_row = row
            item = self.table.item(current_row, 0)
            status_item = self.table.item(current_row, 1)
            self.run_task(item, status_item)
        self.disable_busy_cursor()

    @pyqtSlot()
    def run_all_clicked(self):
        """Run all scenario when pbRunAll is clicked."""
        self.reset_status()

        self.enable_busy_cursor()
        report = []
        fail_count = 0
        pass_count = 0

        index = 0
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            status_item = self.table.item(row, 1)
            name_item = item.text()

            try:
                index += 1
                result = self.run_task(item, status_item, index=index)
                if result:
                    # P for passed
                    report.append('P: %s\n' % name_item)
                    pass_count += 1
                else:
                    report.append('F: %s\n' % name_item)
                    fail_count += 1
            except Exception as e:  # pylint: disable=W0703
                LOGGER.exception('Batch execution failed. The exception: ' +
                                 str(e))
                report.append('F: %s\n' % name_item)
                fail_count += 1
                self.disable_busy_cursor()

        try:
            report_path = self.write_report(
                report, pass_count, fail_count)
            self.show_report(report_path)
        except IOError:
            # noinspection PyArgumentList,PyCallByClass,PyTypeChecker
            QMessageBox.question(self, 'Error',
                                       'Failed to write report file.')
            self.disable_busy_cursor()
        self.disable_busy_cursor()

    def write_report(self, report, pass_count, fail_count):
        """Write a report status of Batch Runner.

        For convenience, the name will use current time.

        :param report: A list of each scenario and its status.
        :type report: list

        :param pass_count: Number of passing scenarios.
        :type pass_count: int

        :param fail_count: Number of failed scenarios.
        :type fail_count: int

        :returns: A string containing the path to the report file.
        :rtype: str

        :raises: IOError
        """
        separator = '-----------------------------\n'
        current_time = datetime.now().strftime('%Y%m%d%H%M%S')
        report_path = 'batch-report-' + current_time + '.txt'
        output_path = self.output_directory.text()
        path = os.path.join(output_path, report_path)

        try:
            report_file = open(path, 'w')
            report_file.write('InaSAFE Batch Report File\n')
            report_file.write(separator)
            for myLine in report:
                report_file.write(myLine)
            report_file.write(separator)
            report_file.write('Total passed: %s\n' % pass_count)
            report_file.write('Total failed: %s\n' % fail_count)
            report_file.write('Total tasks: %s\n' % len(report))
            report_file.write(separator)
            report_file.close()

            # LOGGER.info('Log written to %s' % path)
            return path
        except IOError:
            raise IOError

    def generate_pdf_report(self, impact_function, iface, scenario_name):
        """Generate and store map and impact report from impact function.

        Directory where the report stored is specified by user input from the
        dialog. This function is adapted from analysis_utilities.py

        :param impact_function: Impact Function.
        :type impact_function: ImpactFunction()

        :param iface: iface.
        :type iface: iface

        :param scenario_name: name of the scenario
        :type scenario_name: str
        """
        # output folder
        output_dir = self.output_directory.text()
        file_path = os.path.join(output_dir, scenario_name)

        # create impact table report instance
        table_report_metadata = ReportMetadata(
            metadata_dict=standard_impact_report_metadata_pdf)
        impact_table_report = ImpactReport(
            iface,
            table_report_metadata,
            impact_function=impact_function)
        impact_table_report.output_folder = file_path
        impact_table_report.process_components()

        # create impact map report instance
        map_report_metadata = ReportMetadata(
            metadata_dict=update_template_component(map_report))
        impact_map_report = ImpactReport(
            iface,
            map_report_metadata,
            impact_function=impact_function)
        # TODO: Get from settings file

        # get the extent of impact layer
        impact_map_report.qgis_composition_context.extent = \
            impact_function.impact.extent()
        impact_map_report.output_folder = file_path
        impact_map_report.process_components()

    def show_report(self, report_path):
        """Show batch report file in batchReportFileName using an external app.

        This method uses QDesktop services to display the report (typically
        using gedit or similar text editor).

        :param report_path: Path to the file of batch report.
        :type report_path: str
        """
        if self.show_results_popup:
            url = QtCore.QUrl.fromLocalFile(report_path)
            # noinspection PyTypeChecker,PyCallByClass,PyArgumentList
            QtGui.QDesktopServices.openUrl(url)
        else:
            # report = open(report_path).read()
            # LOGGER.info(report)
            pass

    def update_default_output_dir(self):
        """Update output dir if set to default."""
        if self.scenario_directory_radio.isChecked():
            self.output_directory.setText(self.source_directory.text())

    # noinspection PyMethodMayBeStatic
    def enable_busy_cursor(self):
        """Set the hourglass enabled."""
        QgsApplication.instance().setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

    # noinspection PyMethodMayBeStatic
    def disable_busy_cursor(self):
        """Disable the hourglass cursor."""
        QgsApplication.instance().restoreOverrideCursor()

    @pyqtSlot(bool)
    def on_scenario_directory_radio_toggled(self, flag):
        """Autoconnect slot activated when scenario_directory_radio is checked.

        :param flag: Flag indicating whether the checkbox was toggled on or
            off.
        :type flag: bool
        """
        if flag:
            self.output_directory.setText(self.source_directory.text())
        self.output_directory_chooser.setEnabled(not flag)

    @pyqtSlot()  # prevents actions being handled twice
    def on_source_directory_chooser_clicked(self):
        """Autoconnect slot activated when tbSourceDir is clicked."""

        title = self.tr('Set the source directory for script and scenario')
        self.choose_directory(self.source_directory, title)

    @pyqtSlot()  # prevents actions being handled twice
    def on_output_directory_chooser_clicked(self):
        """Auto  connect slot activated when tbOutputDiris clicked."""
        title = self.tr('Set the output directory for pdf report files')
        self.choose_directory(self.output_directory, title)

    def on_toggle_new_project_toggled(self):
        if self.start_in_new_project:
            self.start_in_new_project = False
        else:
            self.start_in_new_project = True

    @pyqtSlot(bool)  # prevents actions being handled twice
    def help_toggled(self, flag):
        """Show or hide the help tab in the main stacked widget.

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

        .. versionadded:: 3.2.1
        """
        self.main_stacked_widget.setCurrentIndex(1)

    def show_help(self):
        """Show usage info to the user."""
        # Read the header and footer html snippets
        self.main_stacked_widget.setCurrentIndex(0)
        header = html_header()
        footer = html_footer()

        string = header

        message = batch_help()

        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)


def read_scenarios(filename):
    """Read keywords dictionary from file.

    :param filename: Name of file holding scenarios .

    :return Dictionary of with structure like this
        {{ 'foo' : { 'a': 'b', 'c': 'd'},
            { 'bar' : { 'd': 'e', 'f': 'g'}}

    A scenarios file may look like this:

        [jakarta_flood]
        hazard: /path/to/hazard.tif
        exposure: /path/to/exposure.tif
        function: function_id
        aggregation: /path/to/aggregation_layer.tif
        extent: minx, miny, maxx, maxy

    Notes:
        path for hazard, exposure, and aggregation are relative to scenario
        file path
    """
    # Input checks
    filename = os.path.abspath(filename)

    blocks = {}
    parser = ConfigParser()

    # Parse the file content.
    # if the content don't have section header
    # we use the filename.
    try:
        parser.read(filename)
    except MissingSectionHeaderError:
        base_name = os.path.basename(filename)
        name = os.path.splitext(base_name)[0]
        section = '[%s]\n' % name
        content = section + open(filename).read()
        parser.readfp(StringIO(content))

    # convert to dictionary
    for section in parser.sections():
        items = parser.items(section)
        # add section as scenario name
        items.append(('scenario_name', section))
        # add full path to the blocks
        items.append(('full_path', filename))
        blocks[section] = {}
        for key, value in items:
            blocks[section][key] = value

    # Ok we have generated a structure that looks like this:
    # blocks = {{ 'foo' : { 'a': 'b', 'c': 'd'},
    #           { 'bar' : { 'd': 'e', 'f': 'g'}}
    # where foo and bar are scenarios and their dicts are the options for
    # that scenario (e.g. hazard, exposure etc)
    return blocks


def validate_scenario(blocks, scenario_directory):
    """Function to validate input layer stored in scenario file.

    Check whether the files that are used in scenario file need to be
    updated or not.

    :param blocks: dictionary from read_scenarios
    :type blocks: dictionary

    :param scenario_directory: directory where scenario text file is saved
    :type scenario_directory: file directory

    :return: pass message to dialog and log detailed status
    """
    # dictionary to temporary contain status message
    blocks_update = {}
    for section, section_item in list(blocks.items()):
        ready = True
        for item in section_item:
            if item in ['hazard', 'exposure', 'aggregation']:
                # get relative path
                rel_path = section_item[item]
                full_path = os.path.join(scenario_directory, rel_path)
                filepath = os.path.normpath(full_path)
                if not os.path.exists(filepath):
                    blocks_update[section] = {
                        'status': 'Please update scenario'}
                    LOGGER.info(section + ' needs to be updated')
                    LOGGER.info('Unable to find ' + filepath)
                    ready = False
        if ready:
            blocks_update[section] = {'status': 'Scenario ready'}
            # LOGGER.info(section + " scenario is ready")
    for section, section_item in list(blocks_update.items()):
        blocks[section]['status'] = blocks_update[section]['status']


def append_row(table, label, data):
    """Append new row to table widget.

    :param table: The table that shall have the row added to it.
    :type table: QTableWidget

    :param label: Label for the row.
    :type label: str

    :param data: custom data associated with label value.
    :type data: str
    """
    # noinspection PyUnresolvedReferences
    count = table.rowCount()
    # noinspection PyUnresolvedReferences
    table.insertRow(table.rowCount())

    items = QTableWidgetItem(label)

    # see for details of why we follow this pattern
    # http://stackoverflow.com/questions/9257422/
    # how-to-get-the-original-python-data-from-qvariant
    # Make the value immutable.
    variant = (data,)
    # To retrieve it again you would need to do:
    # value = myVariant.toPyObject()[0]
    items.setData(Qt.UserRole, variant)
    # set scenario status (ready or not) into table
    # noinspection PyUnresolvedReferences
    table.setItem(count, 0, items)
    # noinspection PyUnresolvedReferences
    table.setItem(count, 1, QTableWidgetItem(data['status']))
