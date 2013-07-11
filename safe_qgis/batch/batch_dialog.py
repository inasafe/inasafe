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
from PyQt4.QtCore import (pyqtSignature, QSettings, QVariant, Qt)
from PyQt4.QtGui import (QDialog, QFileDialog, QTableWidgetItem)

from qgis.core import QgsRectangle

from safe_qgis.ui.batch_dialog_base import Ui_BatchDialogBase

from safe_qgis.report.map import Map
from safe_qgis.report.html_renderer import HtmlRenderer
from safe_qgis.exceptions import FileNotFoundError
from safe_qgis.safe_interface import temp_dir
from safe_qgis.utilities.utilities import read_impact_layer

LOGGER = logging.getLogger('InaSAFE')

defaultSourceDir = temp_dir()


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
        self.iface = iface
        self.dock = dock

        self.setupUi(self)

        myHeaderView = self.tblScript.horizontalHeader()
        myHeaderView.setResizeMode(0, QtGui.QHeaderView.Stretch)
        myHeaderView.setResizeMode(1, QtGui.QHeaderView.Interactive)

        self.tblScript.setColumnWidth(0, 200)
        self.tblScript.setColumnWidth(1, 125)

        self.gboOptions.setVisible(False)

        self.restore_state()

        # preventing error if the user delete the directory
        if not os.path.exists(self.leSourceDir.text()):
            self.leSourceDir.setText(defaultSourceDir)
        if not os.path.exists(self.leOutputDir.text()):
            self.leOutputDir.setText(defaultSourceDir)
        self.populate_table(self.leSourceDir.text())

        # connect signal to slot
        # noinspection PyUnresolvedReferences
        self.leOutputDir.textChanged.connect(self.save_state)
        # noinspection PyUnresolvedReferences
        self.leSourceDir.textChanged.connect(self.save_state)
        # noinspection PyUnresolvedReferences
        self.leSourceDir.textChanged.connect(self.populate_table)
        # noinspection PyUnresolvedReferences
        self.leSourceDir.textChanged.connect(self.update_default_output_dir)

        # Setup run all button in button box (repurposes yes to all)
        self.run_all_button = self.buttonBox.button(
            QtGui.QDialogButtonBox.YesToAll)
        self.run_all_button.setText(self.tr('Run all'))
        self.run_all_button.clicked.connect(self.run_all_clicked)

        # Setup run selected button in button box (repurposes yes button)
        self.run_selected_button = self.buttonBox.button(
            QtGui.QDialogButtonBox.Yes)
        self.run_selected_button.setText(self.tr('Run selected'))
        self.run_selected_button.clicked.connect(
            self.run_selected_clicked)
        self.run_selected_button.setEnabled(True)

    def restore_state(self):
        """Restore GUI state from configuration file"""

        mySettings = QSettings()

        # restore last source path
        myLastSourcePath = mySettings.value(
            'inasafe/lastSourceDir', defaultSourceDir)
        self.leSourceDir.setText(myLastSourcePath.toString())

        # restore path pdf output
        myLastOutputDir = mySettings.value(
            'inasafe/lastOutputDir', defaultSourceDir)
        self.leOutputDir.setText(myLastOutputDir.toString())

        # restore default output dir combo box
        myUseDefaultOutputDir = mySettings.value(
            'inasafe/useDefaultOutputDir', True)
        self.cbDefaultOutputDir.setChecked(myUseDefaultOutputDir.toBool())

    def save_state(self):
        """Save current state of GUI to configuration file"""

        mySettings = QSettings()

        mySettings.setValue('inasafe/lastSourceDir', self.leSourceDir.text())
        mySettings.setValue('inasafe/lastOutputDir', self.leOutputDir.text())
        mySettings.setValue(
            'inasafe/useDefaultOutputDir',
            self.cbDefaultOutputDir.isChecked())

    def choose_directory(self, line_edit, title):
        """ Show a directory selection dialog.
        This function will show the dialog then set line_edit widget
        text with output from the dialog.

        :param line_edit: Widget whose text should be updated.
        :type line_edit: QLineEdit

        :param title: title of dialog
        :type title: str, QString
        """
        myPath = line_edit.text()
        # noinspection PyCallByClass,PyTypeChecker
        myNewPath = QFileDialog.getExistingDirectory(
            self, title, myPath, QFileDialog.ShowDirsOnly)
        if myNewPath is not None and os.path.exists(myNewPath):
            line_edit.setText(myNewPath)

    def populate_table(self, scenario_directory):
        """ Populate table with files from scenario_directory directory.

        :param scenario_directory: Path where .txt & .py reside.
        :type scenario_directory: QString
        """

        LOGGER.info("populate_table from %s" % scenario_directory)
        parsedFiles = []
        unparsedFiles = []
        self.tblScript.clearContents()

        # NOTE(gigih): need this line to remove existing rows
        self.tblScript.setRowCount(0)

        myPath = str(scenario_directory)

        # only support .py and .txt files
        for myFile in os.listdir(myPath):
            myExt = os.path.splitext(myFile)[1]
            myAbsPath = os.path.join(myPath, myFile)

            if myExt == '.py':
                append_row(self.tblScript, myFile, myAbsPath)
            elif myExt == '.txt':
                # insert scenarios from file into table widget
                try:
                    for myKey, myValue in read_scenarios(myAbsPath).iteritems():
                        append_row(self.tblScript, myKey, myValue)
                    parsedFiles.append(myFile)
                except ParsingError:
                    unparsedFiles.append(myFile)

        LOGGER.info(self.show_parser_results(parsedFiles, unparsedFiles))

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
        scenarioDirectory = str(self.leSourceDir.text())

        myPaths = []
        if 'hazard' in theItem:
            myPaths.append(theItem['hazard'])
        if 'exposure' in theItem:
            myPaths.append(theItem['exposure'])
        if 'aggregation' in theItem:
            myPaths.append(theItem['aggregation'])

        # always run in new project
        self.iface.newProject()

        try:
            scenario_runner.addLayers(scenarioDirectory, myPaths)
        except FileNotFoundError:
            # set status to 'fail'
            LOGGER.exception('Loading layers failed: \nRoot: %s\n%s' % (
                scenarioDirectory, myPaths))
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
                myMessage = 'Extent need exactly 4 value but got %s ' \
                            'instead' % myCount
                LOGGER.error(myMessage)
                return False

            # parse the value to float type
            try:
                myCoordinate = [float(i) for i in myCoordinate]
            except ValueError as e:
                myMessage = e.message
                LOGGER.error(myMessage)
                return False

            # set the extent according the value
            myExtent = QgsRectangle(*myCoordinate)

            myMessage = 'set layer extent to %s ' % myExtent.asWktCoordinates()
            LOGGER.info(myMessage)

            self.iface.mapCanvas().setExtent(myExtent)

        myResult = scenario_runner.runScenario(self.dock)

        return myResult

    def reset_status(self):
        """Set all scenarios' status to empty in the table
        """
        for myRow in range(self.tblScript.rowCount()):
            myStatusItem = self.tblScript.item(myRow, 1)
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
        for myRow in range(self.tblScript.rowCount()):
            myItem = self.tblScript.item(myRow, 0)
            myStatusItem = self.tblScript.item(myRow, 1)
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
        :type report: str

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
        myOutputDir = self.leOutputDir.text()
        myPath = os.path.join(str(myOutputDir), batchFileName)

        try:
            myReportFile = file(myPath, 'wt')
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

            LOGGER.info('Log written to %s' % myPath)
            return myPath
        except IOError:
            raise IOError

    def show_report(self, report_path):
        """Show batch report file in batchReportFileName using an external app.

        This method uses QDesktop services to display the report (typically
        using gedit or similar text editor).

        :param report_path: Path to the file of batch report.
        :type report_path: str
        """
        myUrl = QtCore.QUrl('file:///' + report_path)
        # noinspection PyTypeChecker,PyCallByClass,PyArgumentList
        QtGui.QDesktopServices.openUrl(myUrl)

    def run_repeatedly(self, task_item, status_item, count):
        """Run a task repeatedly - mainly intended for stress testing InaSAFE.

        :param task_item: Item for task to be run.
        :type task_item: QTableWidgetItem

        :param status_item: Item for status cell of task to be run.
        :type status_item: QTableWidgetItem

        :param count: Integer represent how many time a task should run.
        :type count: int
        """
        myReport = []
        myFailCount = 0
        myPassCount = 0

        for i in xrange(count):
            myCount = i + 1
            myResult = self.run_task(task_item, status_item, count=myCount)
            if myResult:
                myPassCount += 1
                myReport.append('Run number %s: Passed.\n' % myCount)
            else:
                myFailCount += 1
                myReport.append('Run number %s: Failed.\n' % myCount)

        batchReportFilePath = self.write_report(
            myReport, myPassCount, myFailCount)
        self.show_report(batchReportFilePath)

    def run_task(self, task_item, status_item, count=0, index=''):
        """Run a single task.

        :param task_item: Table task_item containing task name / details.
        :type task_item: QTableWidgetItem

        :param status_item: Table task_item that holds the task status.
        :type status_item: QTableWidgetItem

        :param count: Count of scenarios thats have been run.
        :type count:

        :param index: integer for representing an index when run all
        scenarios
        :type index:

        :returns: Flag indicating if the task succeeded or not.
        :rtype: bool
        """

        self.enable_busy_cursor()
        # set status to 'running'
        status_item.setText(self.tr('Running'))

        # .. see also:: :func:`appendRow` to understand the next 2 lines
        myVariant = task_item.data(QtCore.Qt.UserRole)
        myValue = myVariant.toPyObject()[0]

        myResult = True

        if isinstance(myValue, str):
            myFilename = myValue
            # run script
            try:
                self.run_script(myFilename)
                # set status to 'OK'
                status_item.setText(self.tr('Script OK'))
            except Exception as e:  # pylint: disable=W0703
                # set status to 'fail'
                status_item.setText(self.tr('Script Fail'))

                LOGGER.exception('Running macro failed. The exception: ' +
                                 str(e))
                myResult = False
        elif isinstance(myValue, dict):
            myPath = str(self.leOutputDir.text())
            myTitle = str(task_item.text())

            # Its a dict containing files for a scenario
            myResult = self.run_scenario(myValue)
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
                        myTitle, myPath, myQGISImpactLayer, count, index)
                    status_item.setText(self.tr('Report Ok'))
                except Exception:  # pylint: disable=W0703
                    LOGGER.exception('Unable to render map: "%s"' % myValue)
                    status_item.setText(self.tr('Report Failed'))
                    myResult = False
        else:
            LOGGER.exception('Data type not supported: "%s"' % myValue)
            myResult = False

        self.disable_busy_cursor()
        return myResult

    def report_path(self, directory, title, count=0, index=''):
        """Get PDF report filename given directory, title and optional index.

        :param directory: Directory of pdf report file.
        :type directory: str

        :param title: Title of report.
        :type title: str

        :param count: The number of scenario run.
        :type count: int

        :param index: The index for the beginning of the file name. TODO
            Explain this better.
        :type index: str

        :returns: A tuple containing the pdf report filenames like this:
            ('/home/foo/data/title.pdf', '/home/foo/data/title_table.pdf')
        :rtype: tuple
        """
        if index != '':
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
                   index=''):
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

        :param index: The prefix for the beginning of the file name. Note we
            need a better explanation of this param.
        :type index: str

        See also:
            Dock.printMap()
        """

        myMap = Map(self.iface)

        # FIXME: check if impact_layer is the real impact layer...
        myMap.setImpactLayer(impact_layer)

        LOGGER.debug('Create Report: %s' % title)
        myMapPath, myTablePath = self.report_path(
            output_directory, title, count, index)

        # create map pdf
        myMap.printToPdf(myMapPath)

        # create table report pdf
        myHtmlRenderer = HtmlRenderer(myMap.pageDpi)
        myKeywords = myMap.keywordIO.read_keywords(impact_layer)
        myHtmlRenderer.printImpactTable(myKeywords, myTablePath)
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
        parsedMessage = self.tr('The file(s) below are parsed successfully:\n')
        unparsedMessage = self.tr('The file(s) below are not parsed '
                                  'successfully:\n')
        parsedContents = '\n'.join(parsed_list)
        unparsedContents = '\n'.join(unparsed_list)
        if parsedContents == '':
            parsedContents = 'No successful parsed files\n'
        if unparsedContents == '':
            unparsedContents = 'No failure in parsing files\n'
        fullMessages = (parsedMessage + parsedContents + '\n\n' +
                        unparsedMessage + unparsedContents)
        return fullMessages

    def update_default_output_dir(self):
        """Update output dir if set to default
        """
        if self.cbDefaultOutputDir.isChecked():
            self.leOutputDir.setText(self.leSourceDir.text())

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
        myCurrentRow = self.tblScript.currentRow()
        myItem = self.tblScript.item(myCurrentRow, 0)
        myStatusItem = self.tblScript.item(myCurrentRow, 1)
        numRepeat = self.sboCount.value()
        if numRepeat == 1:
            self.run_task(myItem, myStatusItem)
        else:
            self.run_repeatedly(myItem, myStatusItem, numRepeat)
        self.disable_busy_cursor()

    @pyqtSignature('bool')
    def on_pbnAdvanced_toggled(self, flag):
        """Autoconnect slot activated when advanced button is clicked.

        :param flag: Flag indicating whether the button was toggled on or off.
        :type flag: bool
        """

        if flag:
            self.pbnAdvanced.setText(self.tr('Hide advanced options'))
        else:
            self.pbnAdvanced.setText(self.tr('Show advanced options'))

        self.gboOptions.setVisible(flag)

    @pyqtSignature('bool')
    def on_cbDefaultOutputDir_toggled(self, flag):
        """Autoconnect slot activated when cbDefaultOutputDir is checked.

        :param flag: Flag indicating whether the checkbox was toggled on or
            off.
        :type flag: bool
        """
        if flag:
            self.leOutputDir.setText(self.leSourceDir.text())
        self.tbOutputDir.setEnabled(not flag)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_toolSourceDir_clicked(self):
        """Autoconnect slot activated when tbSourceDir is clicked """

        myTitle = self.tr('Set the source directory for script and scenario')
        self.choose_directory(self.leSourceDir, myTitle)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_toolOutputDir_clicked(self):
        """Autoconnect slot activated when tbOutputDiris clicked """

        myTitle = self.tr('Set the output directory for pdf report files')
        self.choose_directory(self.leOutputDir, myTitle)


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
    myFilename = os.path.abspath(filename)

    myBlocks = {}
    myParser = ConfigParser()

    # Parse the file content.
    # if the content don't have section header
    # we use the filename.
    try:
        myParser.read(myFilename)
    except MissingSectionHeaderError:
        myBaseName = os.path.basename(filename)
        myName = os.path.splitext(myBaseName)[0]
        mySection = '[%s]\n' % myName
        myContent = mySection + open(myFilename).read()
        myParser.readfp(StringIO(myContent))

    # convert to dictionary
    for mySection in myParser.sections():
        myItems = myParser.items(mySection)
        myBlocks[mySection] = {}
        for myKey, myValue in myItems:
            myBlocks[mySection][myKey] = myValue

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
    :type data: QVariant
    """
    myRow = table.rowCount()
    table.insertRow(table.rowCount())

    myItem = QTableWidgetItem(label)

    # see for details of why we follow this pattern
    # http://stackoverflow.com/questions/9257422/
    # how-to-get-the-original-python-data-from-qvariant
    # Make the value immutable.
    myVariant = QVariant((data,))
    # To retrieve it again you would need to do:
    #myValue = myVariant.toPyObject()[0]
    myItem.setData(Qt.UserRole, myVariant)

    table.setItem(myRow, 0, myItem)
    table.setItem(myRow, 1, QTableWidgetItem(''))
