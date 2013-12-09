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
from safe_qgis.batch import scenario_runner

__author__ = 'bungcip@gmail.com & tim@linfiniti.com & imajimatika@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '01/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

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

        myHeaderView = self.table.horizontalHeader()
        myHeaderView.setResizeMode(0, QtGui.QHeaderView.Stretch)
        myHeaderView.setResizeMode(1, QtGui.QHeaderView.Interactive)

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

        mySettings = QSettings()

        # restore last source path
        myLastSourcePath = mySettings.value(
            'inasafe/lastSourceDir', self.default_directory)
        self.source_directory.setText(myLastSourcePath)

        # restore path pdf output
        myLastOutputDir = mySettings.value(
            'inasafe/lastOutputDir', self.default_directory)
        self.output_directory.setText(myLastOutputDir)

        # restore default output dir combo box
        myUseDefaultOutputDir = bool(mySettings.value(
            'inasafe/useDefaultOutputDir', True))
        self.scenario_directory_radio.setChecked(myUseDefaultOutputDir)

    def save_state(self):
        """Save current state of GUI to configuration file"""

        mySettings = QSettings()

        mySettings.setValue(
            'inasafe/lastSourceDir', self.source_directory.text())
        mySettings.setValue(
            'inasafe/lastOutputDir', self.output_directory.text())
        mySettings.setValue(
            'inasafe/useDefaultOutputDir',
            self.scenario_directory_radio.isChecked())

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
        myNewPath = QFileDialog.getExistingDirectory(
            self, title, path, QFileDialog.ShowDirsOnly)
        if myNewPath is not None and os.path.exists(myNewPath):
            line_edit.setText(myNewPath)

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
        for myFile in os.listdir(path):
            myExt = os.path.splitext(myFile)[1]
            myAbsPath = os.path.join(path, myFile)

            if myExt == '.py':
                append_row(self.table, str(myFile), myAbsPath)
            elif myExt == '.txt':
                # insert scenarios from file into table widget
                try:
                    for key, value\
                            in read_scenarios(myAbsPath).iteritems():
                        append_row(self.table, key, value)
                    parsed_files.append(myFile)
                except ParsingError:
                    unparsed_files.append(myFile)

        LOGGER.info(self.show_parser_results(parsed_files, unparsed_files))

    def run_script(self, filename):
        """ Run a python script in QGIS to exercise InaSAFE functionality.

        This functionality was originally intended for verifying that the key
        elements are InaSAFE are loading correctly and available. However,
        the utility of this function is such that you can run any arbitrary
        python scripts with it. As such you can use it it automate
        activities in QGIS, for example automatically running an impact
        assessment in response to an event.

        :param filename: str - the script filename.
        """

        # import script module
        LOGGER.info('Run script task' + filename)
        myModule, _ = os.path.splitext(filename)
        if myModule in sys.modules:
            myScript = reload(sys.modules[myModule])
        else:
            myScript = __import__(myModule)

        # run as a new project
        self.iface.newProject()

        # run entry function
        myFunction = myScript.runScript
        if myFunction.func_code.co_argcount == 1:
            myFunction(self.iface)
        else:
            myFunction()

    def run_scenario(self, theItem):
        """Run a simple scenario.

        :param theItem: A dictionary contains the scenario configuration.
        :returns: True if success, otherwise return False.
        :rtype: bool
        """
        LOGGER.info('Run simple task' + str(theItem))
        scenarioDirectory = str(self.source_directory.text())

        paths = []
        if 'hazard' in theItem:
            paths.append(theItem['hazard'])
        if 'exposure' in theItem:
            paths.append(theItem['exposure'])
        if 'aggregation' in theItem:
            paths.append(theItem['aggregation'])

        # always run in new project
        self.iface.newProject()

        try:
            scenario_runner.addLayers(scenarioDirectory, paths)
        except FileNotFoundError:
            # set status to 'fail'
            LOGGER.exception('Loading layers failed: \nRoot: %s\n%s' % (
                scenarioDirectory, paths))
            return False

        # See if we have a preferred impact function
        if 'function' in theItem:
            myFunctionId = theItem['function']
            myResult = scenario_runner.setFunctionId(
                myFunctionId, theDock=self.dock)
            if not myResult:
                return False

        if 'aggregation' in theItem:
            absAggregationPath = scenario_runner.extractPath(
                scenarioDirectory, theItem['aggregation'])[0]
            myResult = scenario_runner.setAggregationLayer(
                absAggregationPath, self.dock)
            if not myResult:
                return False

        # set extent if exist
        if 'extent' in theItem:
            # split extent string
            myCoordinate = theItem['extent'].replace(' ', '').split(',')
            myCount = len(myCoordinate)
            if myCount != 4:
                message = 'Extent need exactly 4 value but got %s ' \
                            'instead' % myCount
                LOGGER.error(message)
                return False

            # parse the value to float type
            try:
                myCoordinate = [float(i) for i in myCoordinate]
            except ValueError as e:
                message = e.message
                LOGGER.error(message)
                return False

            # set the extent according the value
            self.iface.mapCanvas().mapRenderer().setProjectionsEnabled(True)

            myExtent = QgsRectangle(*myCoordinate)

            message = 'set layer extent to %s ' % myExtent.asWktCoordinates()
            LOGGER.info(message)

            self.iface.mapCanvas().setExtent(myExtent)

        myResult = scenario_runner.runScenario(self.dock)

        return myResult

    def reset_status(self):
        """Set all scenarios' status to empty in the table
        """
        for myRow in range(self.table.rowCount()):
            myStatusItem = self.table.item(myRow, 1)
            myStatusItem.setText(self.tr(''))

    @pyqtSignature('')
    def run_all_clicked(self):
        """Run all scenario when pbRunAll is clicked.
        """
        self.reset_status()

        self.enable_busy_cursor()
        myReport = []
        myFailCount = 0
        myPassCount = 0

        myIndex = 0
        for myRow in range(self.table.rowCount()):
            myItem = self.table.item(myRow, 0)
            myStatusItem = self.table.item(myRow, 1)
            myNameItem = myItem.text()

            try:
                myIndex += 1
                myResult = self.run_task(myItem, myStatusItem, index=myIndex)
                if myResult:
                    # P for passed
                    myReport.append('P: %s\n' % str(myNameItem))
                    myPassCount += 1
                else:
                    myReport.append('F: %s\n' % str(myNameItem))
                    myFailCount += 1
            except Exception, e:  # pylint: disable=W0703
                LOGGER.exception('Batch execution failed. The exception: ' +
                                 str(e))
                myReport.append('F: %s\n' % str(myNameItem))
                myFailCount += 1
                self.disable_busy_cursor()

        try:
            batchReportFilePath = self.write_report(
                myReport, myPassCount, myFailCount)
            self.show_report(batchReportFilePath)
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
        lineSeparator = '-----------------------------\n'
        currentTime = datetime.now().strftime('%Y%m%d%H%M%S')
        batchFileName = 'batch-report-' + currentTime + '.txt'
        myOutputDir = self.output_directory.text()
        path = os.path.join(str(myOutputDir), batchFileName)

        try:
            myReportFile = file(path, 'wt')
            myReportFile.write('InaSAFE Batch Report File\n')
            myReportFile.write(lineSeparator)
            for myLine in report:
                myReportFile.write(myLine)
            myReportFile.write(lineSeparator)
            myReportFile.write('Total passed: %s\n' % pass_count)
            myReportFile.write('Total failed: %s\n' % fail_count)
            myReportFile.write('Total tasks: %s\n' % len(report))
            myReportFile.write(lineSeparator)
            myReportFile.close()

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
            myUrl = QtCore.QUrl('file:///' + report_path)
            # noinspection PyTypeChecker,PyCallByClass,PyArgumentList
            QtGui.QDesktopServices.openUrl(myUrl)
        else:
            report = open(report_path, 'rt').read()
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
        myVariant = task_item.data(QtCore.Qt.UserRole)
        value = myVariant[0]

        myResult = True

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
                myResult = False
        elif isinstance(value, dict):
            path = str(self.output_directory.text())
            myTitle = str(task_item.text())

            # Its a dict containing files for a scenario
            myResult = self.run_scenario(value)
            if not myResult:
                status_item.setText(self.tr('Analysis Fail'))
            else:
                # NOTE(gigih):
                # Usually after analysis is done, the impact layer
                # become the active layer. <--- WRONG
                myImpactLayer = self.dock.runner.impact_layer()
                # Load impact layer into QGIS
                myQGISImpactLayer = read_impact_layer(myImpactLayer)

                # noinspection PyBroadException
                try:
                    status_item.setText(self.tr('Analysis Ok'))
                    self.create_pdf(
                        myTitle, path, myQGISImpactLayer, count, index)
                    status_item.setText(self.tr('Report Ok'))
                except Exception:  # pylint: disable=W0703
                    LOGGER.exception('Unable to render map: "%s"' % value)
                    status_item.setText(self.tr('Report Failed'))
                    myResult = False
        else:
            LOGGER.exception('Data type not supported: "%s"' % value)
            myResult = False

        self.disable_busy_cursor()
        return myResult

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
        myFileName = title.replace(' ', '_')
        if count != 0:
            myFileName += '_' + str(count)
        myFileName += '.pdf'
        myMapPath = os.path.join(directory, index + myFileName)
        myTablePath = os.path.splitext(myMapPath)[0] + '_table.pdf'

        return myMapPath, myTablePath

    def create_pdf(self,
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

        myMap = Map(self.iface)

        # FIXME: check if impact_layer is the real impact layer...
        myMap.set_impact_layer(impact_layer)

        LOGGER.debug('Create Report: %s' % title)
        myMapPath, myTablePath = self.report_path(
            output_directory, title, count, index)

        # create map pdf
        myMap.make_pdf(myMapPath)

        # create table report pdf
        myHtmlRenderer = HtmlRenderer(myMap.page_dpi)
        keywords = myMap.keyword_io.read_keywords(impact_layer)
        myHtmlRenderer.print_impact_table(keywords, myTablePath)
        LOGGER.debug("Report done %s %s" % (myMapPath, myTablePath))

    def show_parser_results(self, parsed_list, unparsed_list):
        """Compile a formatted list of un/successfully parsed files.

        :param parsed_list: A list of files that were parsed successfully.
        :type parsed_list: list(str)

        :param unparsed_list: A list of files that were not parsable.
        :type unparsed_list: list(str)

        :returns: A formatted message outlining what could be parsed.
        :rtype: str
        """
        parsedMessage = self.tr(
            'The file(s) below were parsed successfully:\n')
        unparsedMessage = self.tr(
            'The file(s) below were not parsed successfully:\n')
        parsedContents = '\n'.join(parsed_list)
        unparsedContents = '\n'.join(unparsed_list)
        if parsedContents == '':
            parsedContents = 'No successfully parsed files\n'
        if unparsedContents == '':
            unparsedContents = 'No failures in parsing files\n'
        fullMessages = (parsedMessage + parsedContents + '\n\n' +
                        unparsedMessage + unparsedContents)
        return fullMessages

    def update_default_output_dir(self):
        """Update output dir if set to default
        """
        if self.scenario_directory_radio.isChecked():
            self.output_directory.setText(self.source_directory.text())

    def enable_busy_cursor(self):
        """Set the hourglass enabled."""
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

    def disable_busy_cursor(self):
        """Disable the hourglass cursor."""
        QtGui.qApp.restoreOverrideCursor()

    @pyqtSignature('')
    def run_selected_clicked(self):
        """Run the selected scenario. """
        self.enable_busy_cursor()
        myCurrentRow = self.table.currentRow()
        myItem = self.table.item(myCurrentRow, 0)
        myStatusItem = self.table.item(myCurrentRow, 1)
        self.run_task(myItem, myStatusItem)
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

        myTitle = self.tr('Set the source directory for script and scenario')
        self.choose_directory(self.source_directory, myTitle)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_output_directory_chooser_clicked(self):
        """Autoconnect slot activated when tbOutputDiris clicked """

        myTitle = self.tr('Set the output directory for pdf report files')
        self.choose_directory(self.output_directory, myTitle)


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

    myBlocks = {}
    myParser = ConfigParser()

    # Parse the file content.
    # if the content don't have section header
    # we use the filename.
    try:
        myParser.read(filename)
    except MissingSectionHeaderError:
        myBaseName = os.path.basename(filename)
        myName = os.path.splitext(myBaseName)[0]
        mySection = '[%s]\n' % myName
        myContent = mySection + open(filename).read()
        myParser.readfp(StringIO(myContent))

    # convert to dictionary
    for mySection in myParser.sections():
        myItems = myParser.items(mySection)
        myBlocks[mySection] = {}
        for key, value in myItems:
            myBlocks[mySection][key] = value

    # Ok we have generated a structure that looks like this:
    # myBlocks = {{ 'foo' : { 'a': 'b', 'c': 'd'},
    #           { 'bar' : { 'd': 'e', 'f': 'g'}}
    # where foo and bar are scenarios and their dicts are the options for
    # that scenario (e.g. hazard, exposure etc)
    return myBlocks


def append_row(table, label, data):
    """Append new row to table widget.

    :param table: The table that shall have the row added to it.
    :type table: QTableWidget

    :param label: Label for the row.
    :type label: str

    :param data: custom data associated with label value.
    :type data: str
    """
    myRow = table.rowCount()
    table.insertRow(table.rowCount())

    myItem = QTableWidgetItem(label)

    # see for details of why we follow this pattern
    # http://stackoverflow.com/questions/9257422/
    # how-to-get-the-original-python-data-from-qvariant
    # Make the value immutable.
    myVariant = (data,)
    # To retrieve it again you would need to do:
    #value = myVariant.toPyObject()[0]
    myItem.setData(Qt.UserRole, myVariant)

    table.setItem(myRow, 0, myItem)
    table.setItem(myRow, 1, QTableWidgetItem(''))
