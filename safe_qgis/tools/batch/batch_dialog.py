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
__author__ = 'bungcip@gmail.com & tim@linfiniti.com & imajimatika@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '01/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# this import required to enable PyQt API v2 - DO NOT REMOVE!
#noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611

import os
import sys
import logging
from datetime import datetime

from StringIO import StringIO
from ConfigParser import ConfigParser, MissingSectionHeaderError, ParsingError

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignature, pyqtSlot, QSettings, Qt
from PyQt4.QtGui import (
    QDialog,
    QFileDialog,
    QTableWidgetItem,
    QPushButton,
    QDialogButtonBox)

from qgis.core import QgsRectangle

from safe_qgis.ui.batch_dialog_base import Ui_BatchDialogBase
from safe_qgis.tools.batch import scenario_runner
from safe_qgis.report.map import Map
from safe_qgis.report.html_renderer import HtmlRenderer
from safe_qgis.exceptions import FileNotFoundError
from safe_qgis.safe_interface import temp_dir
from safe_qgis.utilities.utilities import read_impact_layer
from safe_qgis.utilities.help import show_context_help

LOGGER = logging.getLogger('InaSAFE')


class BatchDialog(QDialog, Ui_BatchDialogBase):
    """Script Dialog for InaSAFE."""

    def __init__(self, parent=None, iface=None, dock=None):
        """Constructor for the dialog.

        :param parent: Widget to use as parent.
        :type parent: PyQt4.QtGui.QWidget

        :param iface: A QGisAppInterface instance we use to access QGIS via.
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
        header_view.setResizeMode(0, QtGui.QHeaderView.Stretch)
        header_view.setResizeMode(1, QtGui.QHeaderView.Interactive)

        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 125)

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

        # Set up things for context help
        help_button = self.button_box.button(QtGui.QDialogButtonBox.Help)
        QtCore.QObject.connect(
            help_button, QtCore.SIGNAL('clicked()'), self.show_help)

        self.restore_state()

    def restore_state(self):
        """Restore GUI state from configuration file"""

        settings = QSettings()

        # restore last source path
        last_source_path = settings.value(
            'inasafe/lastSourceDir', self.default_directory, type=str)
        self.source_directory.setText(last_source_path)

        # restore path pdf output
        last_output_dir = settings.value(
            'inasafe/lastOutputDir', self.default_directory, type=str)
        self.output_directory.setText(last_output_dir)

        # restore default output dir combo box
        use_default_output_dir = bool(settings.value(
            'inasafe/useDefaultOutputDir', True, type=bool))
        self.scenario_directory_radio.setChecked(
            use_default_output_dir)

    def save_state(self):
        """Save current state of GUI to configuration file"""

        settings = QSettings()

        settings.setValue(
            'inasafe/lastSourceDir', self.source_directory.text())
        settings.setValue(
            'inasafe/lastOutputDir', self.output_directory.text())
        settings.setValue(
            'inasafe/useDefaultOutputDir',
            self.scenario_directory_radio.isChecked())

    # noinspection PyMethodMayBeStatic
    def show_help(self):
        """Show context help for the batch dialog."""
        show_context_help('batch_runner')

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

        LOGGER.info("populate_table from %s" % scenario_directory)
        parsed_files = []
        unparsed_files = []
        self.table.clearContents()

        # NOTE(gigih): need this line to remove existing rows
        self.table.setRowCount(0)

        path = str(scenario_directory)

        if not os.path.exists(path):
            LOGGER.info('Scenario directory does not exist: %s' % path)
            return

        # only support .py and .txt files
        for current_path in os.listdir(path):
            extension = os.path.splitext(current_path)[1]
            absolute_path = os.path.join(path, current_path)

            if extension == '.py':
                append_row(self.table, str(current_path), absolute_path)
            elif extension == '.txt':
                # insert scenarios from file into table widget
                try:
                    scenarios = read_scenarios(absolute_path)
                    for key, value in scenarios.iteritems():
                        append_row(self.table, key, value)
                    parsed_files.append(current_path)
                except ParsingError:
                    unparsed_files.append(current_path)

        LOGGER.info(self.show_parser_results(parsed_files, unparsed_files))

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

        # import script module
        LOGGER.info('Run script task' + filename)
        module, _ = os.path.splitext(filename)
        if module in sys.modules:
            script = reload(sys.modules[module])
        else:
            script = __import__(module)

        # run as a new project
        self.iface.newProject()

        # run entry function
        function = script.runScript
        if function.func_code.co_argcount == 1:
            function(self.iface)
        else:
            function()

    def run_scenario(self, items):
        """Run a simple scenario.

        :param items: A dictionary containing the scenario configuration
            as table items.
        :type items: dict

        :returns: True if success, otherwise return False.
        :rtype: bool
        """
        LOGGER.info('Run simple task' + str(items))
        scenario_directory = str(self.source_directory.text())

        paths = []
        if 'hazard' in items:
            paths.append(items['hazard'])
        if 'exposure' in items:
            paths.append(items['exposure'])
        if 'aggregation' in items:
            paths.append(items['aggregation'])

        # always run in new project
        self.iface.newProject()

        try:
            scenario_runner.add_layers(scenario_directory, paths)
        except FileNotFoundError:
            # set status to 'fail'
            LOGGER.exception('Loading layers failed: \nRoot: %s\n%s' % (
                scenario_directory, paths))
            return False

        # See if we have a preferred impact function
        if 'function' in items:
            function_id = items['function']
            result = scenario_runner.set_function_id(
                function_id, dock=self.dock)
            if not result:
                return False

        if 'aggregation' in items:
            aggregation_path = scenario_runner.extract_path(
                scenario_directory, items['aggregation'])[0]
            result = scenario_runner.set_aggregation_layer(
                aggregation_path, self.dock)
            if not result:
                return False

        # set extent if exist
        if 'extent' in items:
            # split extent string
            coordinates = items['extent'].replace(' ', '').split(',')
            count = len(coordinates)
            if count != 4:
                message = (
                    'Extent need exactly 4 value but got %s instead' % count)
                LOGGER.error(message)
                return False

            # parse the value to float type
            try:
                coordinates = [float(i) for i in coordinates]
            except ValueError as e:
                message = e.message
                LOGGER.error(message)
                return False

            # set the extent according the value
            self.iface.mapCanvas().mapRenderer().setProjectionsEnabled(True)

            extent = QgsRectangle(*coordinates)

            message = 'set layer extent to %s ' % extent.asWktCoordinates()
            LOGGER.info(message)

            self.iface.mapCanvas().setExtent(extent)

        result = scenario_runner.run_scenario(self.dock)

        return result

    def reset_status(self):
        """Set all scenarios' status to empty in the table
        """
        for row in range(self.table.rowCount()):
            status_item = self.table.item(row, 1)
            status_item.setText(self.tr(''))

    @pyqtSignature('')
    def run_all_clicked(self):
        """Run all scenario when pbRunAll is clicked.
        """
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
                    report.append('P: %s\n' % str(name_item))
                    pass_count += 1
                else:
                    report.append('F: %s\n' % str(name_item))
                    fail_count += 1
            except Exception, e:  # pylint: disable=W0703
                LOGGER.exception('Batch execution failed. The exception: ' +
                                 str(e))
                report.append('F: %s\n' % str(name_item))
                fail_count += 1
                self.disable_busy_cursor()

        try:
            report_path = self.write_report(
                report, pass_count, fail_count)
            self.show_report(report_path)
        except IOError:
            # noinspection PyArgumentList,PyCallByClass,PyTypeChecker
            QtGui.QMessageBox.question(self, 'Error',
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
        path = os.path.join(str(output_path), report_path)

        try:
            report_file = file(path, 'w')
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

            LOGGER.info('Log written to %s' % path)
            return path
        except IOError:
            raise IOError

    def show_report(self, report_path):
        """Show batch report file in batchReportFileName using an external app.

        This method uses QDesktop services to display the report (typically
        using gedit or similar text editor).

        :param report_path: Path to the file of batch report.
        :type report_path: str
        """
        if self.show_results_popup:
            url = QtCore.QUrl('file:///' + report_path)
            # noinspection PyTypeChecker,PyCallByClass,PyArgumentList
            QtGui.QDesktopServices.openUrl(url)
        else:
            report = open(report_path).read()
            LOGGER.info(report)

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

                LOGGER.exception('Running macro failed. The exception: ' +
                                 str(e))
                result = False
        elif isinstance(value, dict):
            path = str(self.output_directory.text())
            title = str(task_item.text())

            # Its a dict containing files for a scenario
            result = self.run_scenario(value)
            if not result:
                status_item.setText(self.tr('Analysis Fail'))
            else:
                # NOTE(gigih):
                # Usually after analysis is done, the impact layer
                # become the active layer. <--- WRONG
                # noinspection PyUnresolvedReferences
                impact_layer = self.dock.runner.impact_layer()
                # Load impact layer into QGIS
                qgis_layer = read_impact_layer(impact_layer)

                # noinspection PyBroadException
                try:
                    status_item.setText(self.tr('Analysis Ok'))
                    self.create_pdf(
                        title, path, qgis_layer, count, index)
                    status_item.setText(self.tr('Report Ok'))
                except Exception:  # pylint: disable=W0703
                    LOGGER.exception('Unable to render map: "%s"' % value)
                    status_item.setText(self.tr('Report Failed'))
                    result = False
        else:
            LOGGER.exception('Data type not supported: "%s"' % value)
            result = False

        self.disable_busy_cursor()
        return result

    # noinspection PyMethodMayBeStatic
    def report_path(self, directory, title, count=0, index=None):
        """Get PDF report filename given directory, title and optional index.

        :param directory: Directory of pdf report file.
        :type directory: str

        :param title: Title of report.
        :type title: str

        :param count: The number of scenario run.
        :type count: int

        :param index: A sequential number for the beginning of the file name.
        :type index: int, None

        :returns: A tuple containing the pdf report filenames like this:
            ('/home/foo/data/title.pdf', '/home/foo/data/title_table.pdf')
        :rtype: tuple
        """
        if index is not None:
            index = str(index) + '_'
        file_name = title.replace(' ', '_')
        if count != 0:
            file_name += '_' + str(count)
        file_name += '.pdf'
        map_path = os.path.join(directory, index + file_name)
        table_path = os.path.splitext(map_path)[0] + '_table.pdf'

        return map_path, table_path

    def create_pdf(
            self,
            title,
            output_directory,
            impact_layer,
            count=0,
            index=None):
        """Create PDF report from impact layer.

        Create map & table report PDF based from impact_layer data.

        :param title: Report title.
        :type title: str

        :param output_directory: Output directory.
        :type output_directory: str

        :param impact_layer: Impact layer instance.
        :type impact_layer: QgsMapLayer

        :param count: The number of scenarios that were run.
        :type count: int

        :param index: A sequential number to place at the beginning of the
            file name.
        :type index: int, None

        See also:
            Dock.printMap()
        """

        inasafe_map = Map(self.iface)

        # FIXME: check if impact_layer is the real impact layer...
        inasafe_map.set_impact_layer(impact_layer)

        LOGGER.debug('Create Report: %s' % title)
        map_path, table_path = self.report_path(
            output_directory, title, count, index)

        # create map pdf
        inasafe_map.make_pdf(map_path)

        # create table report pdf
        html_renderer = HtmlRenderer(inasafe_map.page_dpi)
        keywords = inasafe_map.keyword_io.read_keywords(impact_layer)
        html_renderer.print_impact_table(keywords, table_path)
        LOGGER.debug("Report done %s %s" % (map_path, table_path))

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

    def update_default_output_dir(self):
        """Update output dir if set to default
        """
        if self.scenario_directory_radio.isChecked():
            self.output_directory.setText(self.source_directory.text())

    # noinspection PyMethodMayBeStatic
    def enable_busy_cursor(self):
        """Set the hourglass enabled."""
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

    # noinspection PyMethodMayBeStatic
    def disable_busy_cursor(self):
        """Disable the hourglass cursor."""
        QtGui.qApp.restoreOverrideCursor()

    @pyqtSignature('')
    def run_selected_clicked(self):
        """Run the selected scenario. """
        self.enable_busy_cursor()
        current_row = self.table.currentRow()
        item = self.table.item(current_row, 0)
        status_item = self.table.item(current_row, 1)
        self.run_task(item, status_item)
        self.disable_busy_cursor()

    @pyqtSignature('bool')
    def on_scenario_directory_radio_toggled(self, flag):
        """Autoconnect slot activated when scenario_directory_radio is checked.

        :param flag: Flag indicating whether the checkbox was toggled on or
            off.
        :type flag: bool
        """
        if flag:
            self.output_directory.setText(self.source_directory.text())
        self.output_directory_chooser.setEnabled(not flag)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_source_directory_chooser_clicked(self):
        """Autoconnect slot activated when tbSourceDir is clicked """

        title = self.tr('Set the source directory for script and scenario')
        self.choose_directory(self.source_directory, title)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_output_directory_chooser_clicked(self):
        """Autoconnect slot activated when tbOutputDiris clicked """

        title = self.tr('Set the output directory for pdf report files')
        self.choose_directory(self.output_directory, title)


def read_scenarios(filename):
    """Read keywords dictionary from file

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
        blocks[section] = {}
        for key, value in items:
            blocks[section][key] = value

    # Ok we have generated a structure that looks like this:
    # blocks = {{ 'foo' : { 'a': 'b', 'c': 'd'},
    #           { 'bar' : { 'd': 'e', 'f': 'g'}}
    # where foo and bar are scenarios and their dicts are the options for
    # that scenario (e.g. hazard, exposure etc)
    return blocks


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
    #value = myVariant.toPyObject()[0]
    items.setData(Qt.UserRole, variant)

    # noinspection PyUnresolvedReferences
    table.setItem(count, 0, items)
    # noinspection PyUnresolvedReferences
    table.setItem(count, 1, QTableWidgetItem(''))
