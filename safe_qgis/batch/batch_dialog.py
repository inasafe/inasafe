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

    def __init__(self, theParent=None, theIface=None, theDock=None):
        """Constructor for the dialog.

        Args:
           theParent - Optional widget to use as parent.
        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """
        QDialog.__init__(self, theParent)
        self.iface = theIface
        self.dock = theDock

        self.setupUi(self)

        myHeaderView = self.tblScript.horizontalHeader()
        myHeaderView.setResizeMode(0, QtGui.QHeaderView.Stretch)
        myHeaderView.setResizeMode(1, QtGui.QHeaderView.Interactive)

        self.tblScript.setColumnWidth(0, 200)
        self.tblScript.setColumnWidth(1, 125)

        self.gboOptions.setVisible(False)

        self.restoreState()

        # preventing error if the user delete the directory
        if not os.path.exists(self.leSourceDir.text()):
            self.leSourceDir.setText(defaultSourceDir)
        if not os.path.exists(self.leOutputDir.text()):
            self.leOutputDir.setText(defaultSourceDir)
        self.populateTable(self.leSourceDir.text())

        # connect signal to slot
        # noinspection PyUnresolvedReferences
        self.leOutputDir.textChanged.connect(self.saveState)
        # noinspection PyUnresolvedReferences
        self.leSourceDir.textChanged.connect(self.saveState)
        # noinspection PyUnresolvedReferences
        self.leSourceDir.textChanged.connect(self.populateTable)
        # noinspection PyUnresolvedReferences
        self.leSourceDir.textChanged.connect(self.updateDefaultOutputDir)

        self.btnRunSelected.setEnabled(True)

    def restoreState(self):
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

    def saveState(self):
        """Save current state of GUI to configuration file"""

        mySettings = QSettings()

        mySettings.setValue('inasafe/lastSourceDir', self.leSourceDir.text())
        mySettings.setValue('inasafe/lastOutputDir', self.leOutputDir.text())
        mySettings.setValue('inasafe/useDefaultOutputDir',
                            self.cbDefaultOutputDir.isChecked())

    def showDirectoryDialog(self, theLineEdit, theTitle):
        """ Show a directory selection dialog.
        This function will show the dialog then set theLineEdit widget
        text with output from the dialog.

        :param theLineEdit: QLineEdit widget instance
        :param theTitle: title of dialog
        """
        myPath = theLineEdit.text()
        # noinspection PyCallByClass,PyTypeChecker
        myNewPath = QFileDialog.getExistingDirectory(
            self, theTitle, myPath, QFileDialog.ShowDirsOnly)
        if myNewPath is not None and os.path.exists(myNewPath):
            theLineEdit.setText(myNewPath)

    def populateTable(self, theScenarioDirectory):
        """ Populate table with files from theBasePath directory.

        :param theScenarioDirectory: QString - path where .txt & .py reside
        """

        LOGGER.info("populateTable from %s" % theScenarioDirectory)
        parsedFiles = []
        unparsedFiles = []
        self.tblScript.clearContents()

        # NOTE(gigih): need this line to remove existing rows
        self.tblScript.setRowCount(0)

        myPath = str(theScenarioDirectory)

        # only support .py and .txt files
        for myFile in os.listdir(myPath):
            myExt = os.path.splitext(myFile)[1]
            myAbsPath = os.path.join(myPath, myFile)

            if myExt == '.py':
                appendRow(self.tblScript, myFile, myAbsPath)
            elif myExt == '.txt':
                # insert scenarios from file into table widget
                try:
                    for myKey, myValue in readScenarios(myAbsPath).iteritems():
                        appendRow(self.tblScript, myKey, myValue)
                    parsedFiles.append(myFile)
                except ParsingError:
                    unparsedFiles.append(myFile)

        LOGGER.info(self.getPopulateScenarioLog(parsedFiles, unparsedFiles))

    def runScriptTask(self, theFilename):
        """ Run a python script in QGIS to exercise InaSAFE functionality.

        This functionality was originally intended for verifying that the key
        elements are InaSAFE are loading correctly and available. However,
        the utility of this function is such that you can run any arbitrary
        python scripts with it. As such you can use it it automate
        activities in QGIS, for example automatically running an impact
        assessment in response to an event.

        :param theFilename: str - the script filename.
        """

        # import script module
        LOGGER.info('Run script task' + theFilename)
        myModule, _ = os.path.splitext(theFilename)
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

    def runSimpleTask(self, theItem):
        """Run a simple scenario.

        :param theItem: A dictionary contains the scenario configuration
        :returns: True if success, otherwise return False.
        :rtype: bool
        """
        LOGGER.info('Run simple task' + str(theItem))
        scenarioDirectory = str(self.leSourceDir.text())
        # dummy file
        dummyScenarioFilePath = os.path.join(scenarioDirectory, 'dummy.txt')

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
            scenario_runner.addLayers(dummyScenarioFilePath, myPaths)
        except FileNotFoundError:
            # set status to 'fail'
            LOGGER.exception('Loading layers failed: \nRoot: %s\n%s' % (
                dummyScenarioFilePath, myPaths))
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
                dummyScenarioFilePath, theItem['aggregation'])[0]
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

    def setAllScenarioEmptyStatus(self):
        """Set all scenarios' status to empty in the table
        """
        for myRow in range(self.tblScript.rowCount()):
            myStatusItem = self.tblScript.item(myRow, 1)
            myStatusItem.setText(self.tr(''))

    @pyqtSignature('')
    def on_pbnRunAll_clicked(self):
        """Run all scenario when pbRunAll is clicked.
        """
        self.setAllScenarioEmptyStatus()

        self.enableBusyCursor()
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
                myResult = self.runTask(myItem, myStatusItem, theIndex=myIndex)
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
                self.disableBusyCursor()

        try:
            batchReportFilePath = self.writeBatchReport(
                myReport, myPassCount, myFailCount)
            self.showBatchReport(batchReportFilePath)
        except IOError:
            # noinspection PyArgumentList,PyCallByClass,PyTypeChecker
            QtGui.QMessageBox.question(self, 'Error',
                                       'Failed to write report file.')
            self.disableBusyCursor()
        self.disableBusyCursor()

    def writeBatchReport(self, myReport, myPassCount, myFailCount):
        """Write a report status of Batch Runner
        For convenience, the name will use current time
        :param myReport: the report. a list of each scenario
        :param myPassCount: number of pass scenario
        :param myFailCount: number of failed scenario
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
            for myLine in myReport:
                myReportFile.write(myLine)
            myReportFile.write(lineSeparator)
            myReportFile.write('Total passed: %s\n' % myPassCount)
            myReportFile.write('Total failed: %s\n' % myFailCount)
            myReportFile.write('Total tasks: %s\n' % len(myReport))
            myReportFile.write(lineSeparator)
            myReportFile.close()

            LOGGER.info('Log written to %s' % myPath)
            return myPath
        except IOError:
            raise IOError

    def showBatchReport(self, batchReportFilePath):
        """Show batch report file in batchReportFileName
        :param batchReportFilePath: string to the file of batch report
        """
        myUrl = QtCore.QUrl('file:///' + batchReportFilePath)
        # noinspection PyTypeChecker,PyCallByClass,PyArgumentList
        QtGui.QDesktopServices.openUrl(myUrl)

    def runTaskMany(self, theItem, theStatusItem, numRepeat):
        """Run a task numRun times
        :param theItem:
        :param theStatusItem:
        :param numRepeat: integer represent how many time a scenario run
        """
        myReport = []
        myFailCount = 0
        myPassCount = 0

        for i in xrange(numRepeat):
            myCount = i + 1
            myResult = self.runTask(theItem, theStatusItem, theCount=myCount)
            if myResult:
                myPassCount += 1
                myReport.append('Run number %s: Passed.\n' % myCount)
            else:
                myFailCount += 1
                myReport.append('Run number %s: Failed.\n' % myCount)

        batchReportFilePath = self.writeBatchReport(
            myReport, myPassCount, myFailCount)
        self.showBatchReport(batchReportFilePath)

    def runTask(self, theItem, theStatusItem, theCount=0, theIndex=''):
        """Run a single task
        :param theItem:
        :param theStatusItem:
        :param theCount: integer represent count number of scenario has been
        run
        :param theIndex: integer for representing an index when run all
        scenarios
        """

        self.enableBusyCursor()
        # set status to 'running'
        theStatusItem.setText(self.tr('Running'))

        # .. see also:: :func:`appendRow` to understand the next 2 lines
        myVariant = theItem.data(QtCore.Qt.UserRole)
        myValue = myVariant.toPyObject()[0]

        myResult = True

        if isinstance(myValue, str):
            myFilename = myValue
            # run script
            try:
                self.runScriptTask(myFilename)
                # set status to 'OK'
                theStatusItem.setText(self.tr('Script OK'))
            except Exception as e:  # pylint: disable=W0703
                # set status to 'fail'
                theStatusItem.setText(self.tr('Script Fail'))

                LOGGER.exception('Running macro failed. The exception: ' +
                                 str(e))
                myResult = False
        elif isinstance(myValue, dict):
            myPath = str(self.leOutputDir.text())
            myTitle = str(theItem.text())

            # Its a dict containing files for a scenario
            myResult = self.runSimpleTask(myValue)
            if not myResult:
                theStatusItem.setText(self.tr('Analysis Fail'))
            else:
                # NOTE(gigih):
                # Usually after analysis is done, the impact layer
                # become the active layer. <--- WRONG
                myImpactLayer = self.dock.runner.impact_layer()
                # Load impact layer into QGIS
                myQGISImpactLayer = read_impact_layer(myImpactLayer)

                # noinspection PyBroadException
                try:
                    theStatusItem.setText(self.tr('Analysis Ok'))
                    self.createPDFReport(
                        myTitle, myPath, myQGISImpactLayer, theCount, theIndex)
                    theStatusItem.setText(self.tr('Report Ok'))
                except Exception:  # pylint: disable=W0703
                    LOGGER.exception('Unable to render map: "%s"' % myValue)
                    theStatusItem.setText(self.tr('Report Failed'))
                    myResult = False
        else:
            LOGGER.exception('Data type not supported: "%s"' % myValue)
            myResult = False

        self.disableBusyCursor()
        return myResult

    def reportPath(self, theDirectory, theTitle, theCount=0, theIndex=''):
        """Get PDF report filename based on theDirectory and theTitle and the
        index if given

        :param theDirectory: the directory of pdf report file
        :param theTitle: title of report
        :param theCount: the number of as scenario has been run
        :param theIndex: the index for the beginning of the file name

        :returns a tuple contains the pdf report filename like this
        ('/home/foo/data/title.pdf', '/home/foo/data/title_table.pdf')
        """
        if theIndex != '':
            theIndex = str(theIndex) + '_'
        myFileName = theTitle.replace(' ', '_')
        if theCount != 0:
            myFileName += '_' + str(theCount)
        myFileName += '.pdf'
        myMapPath = os.path.join(theDirectory, theIndex + myFileName)
        myTablePath = os.path.splitext(myMapPath)[0] + '_table.pdf'

        return myMapPath, myTablePath

    def createPDFReport(self, theTitle, theOutputDirectory, theImpactLayer,
                        theCount=0, theIndex=''):
        """Create PDF report from impact layer.
        Create map & table report PDF based from theImpactLayer data.

        :param theTitle: the report title.
        :param theOutputDirectory: output directory
        :param theImpactLayer: impact layer instance.
        :param theCount: the number of as scenario has been run
        :param theIndex: the index for the beginning of the file name

        See also:
            Dock.printMap()
        """

        myMap = Map(self.iface)

        # FIXME: check if theImpactLayer is the real impact layer...
        myMap.setImpactLayer(theImpactLayer)

        LOGGER.debug('Create Report: %s' % theTitle)
        myMapPath, myTablePath = self.reportPath(
            theOutputDirectory, theTitle, theCount, theIndex)

        # create map pdf
        myMap.printToPdf(myMapPath)

        # create table report pdf
        myHtmlRenderer = HtmlRenderer(myMap.pageDpi)
        myKeywords = myMap.keywordIO.read_keywords(theImpactLayer)
        myHtmlRenderer.printImpactTable(myKeywords, myTablePath)
        LOGGER.debug("Report done %s %s" % (myMapPath, myTablePath))

    def getPopulateScenarioLog(self, parsedFiles, unparsedFiles):
        """A method to show a message box that shows list of successfully
        parsed files and unsuccessfully parsed files
        :param parsedFiles:
        :param unparsedFiles:
        """
        parsedMessage = self.tr('The file(s) below are parsed successfully:\n')
        unparsedMessage = self.tr('The file(s) below are not parsed '
                                  'successfully:\n')
        parsedContents = '\n'.join(parsedFiles)
        unparsedContents = '\n'.join(unparsedFiles)
        if parsedContents == '':
            parsedContents = 'No successful parsed files\n'
        if unparsedContents == '':
            unparsedContents = 'No failure in parsing files\n'
        fullMessages = (parsedMessage + parsedContents + '\n\n' +
                        unparsedMessage + unparsedContents)
        return fullMessages

    def updateDefaultOutputDir(self):
        """Update output dir if set to default
        """
        if self.cbDefaultOutputDir.isChecked():
            self.leOutputDir.setText(self.leSourceDir.text())

    def enableBusyCursor(self):
        """Set the hourglass enabled."""
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

    def disableBusyCursor(self):
        """Disable the hourglass cursor."""
        QtGui.qApp.restoreOverrideCursor()

    @pyqtSignature('')
    def on_btnRunSelected_clicked(self):
        """Run the selected scenario. """
        self.enableBusyCursor()
        myCurrentRow = self.tblScript.currentRow()
        myItem = self.tblScript.item(myCurrentRow, 0)
        myStatusItem = self.tblScript.item(myCurrentRow, 1)
        numRepeat = self.sboCount.value()
        if numRepeat == 1:
            self.runTask(myItem, myStatusItem)
        else:
            self.runTaskMany(myItem, myStatusItem, numRepeat)
        self.disableBusyCursor()

    @pyqtSignature('bool')
    def on_pbnAdvanced_toggled(self, theFlag):
        """Autoconnect slot activated when advanced button is clicked
        :param theFlag:
        """

        if theFlag:
            self.pbnAdvanced.setText(self.tr('Hide advanced options'))
        else:
            self.pbnAdvanced.setText(self.tr('Show advanced options'))

        self.gboOptions.setVisible(theFlag)

    @pyqtSignature('bool')
    def on_cbDefaultOutputDir_toggled(self, theFlag):
        """Autoconnect slot activated when cbDefaultOutputDir is checked
        :param theFlag:
        """
        if theFlag:
            self.leOutputDir.setText(self.leSourceDir.text())
        self.tbOutputDir.setEnabled(not theFlag)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_tbSourceDir_clicked(self):
        """ Autoconnect slot activated when tbSourceDir is clicked """

        myTitle = self.tr('Set the source directory for script and scenario')
        self.showDirectoryDialog(self.leSourceDir, myTitle)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_tbOutputDir_clicked(self):
        """ Autoconnect slot activated when tbOutputDiris clicked """

        myTitle = self.tr('Set the output directory for pdf report files')
        self.showDirectoryDialog(self.leOutputDir, myTitle)


def readScenarios(theFileName):
    """Read keywords dictionary from file

    :param theFileName: Name of file holding scenarios .

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
    myFilename = os.path.abspath(theFileName)

    myBlocks = {}
    myParser = ConfigParser()

    # Parse the file content.
    # if the content don't have section header
    # we use the filename.
    try:
        myParser.read(myFilename)
    except MissingSectionHeaderError:
        myBaseName = os.path.basename(theFileName)
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


def appendRow(theTable, theLabel, theData):
    """ Append new row to table widget.
    :param theTable: a QTable instance
    :param theLabel: label for the row
    :param theData: custom data associated with theLabel value.
    """
    myRow = theTable.rowCount()
    theTable.insertRow(theTable.rowCount())

    myItem = QTableWidgetItem(theLabel)

    # see for details of why we follow this pattern
    # http://stackoverflow.com/questions/9257422/
    # how-to-get-the-original-python-data-from-qvariant
    # Make the value immutable.
    myVariant = QVariant((theData,))
    # To retrieve it again you would need to do:
    #myValue = myVariant.toPyObject()[0]
    myItem.setData(Qt.UserRole, myVariant)

    theTable.setItem(myRow, 0, myItem)
    theTable.setItem(myRow, 1, QTableWidgetItem(''))
