"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Script runner dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'bungcip@gmail.com & tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '01/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import sys
import logging

from StringIO import StringIO
from ConfigParser import ConfigParser, MissingSectionHeaderError

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import (pyqtSignature, QSettings, QVariant, Qt)
from PyQt4.QtGui import (QDialog, QFileDialog, QTableWidgetItem, QMessageBox)

from qgis.core import QgsRectangle

from script_dialog_base import Ui_ScriptDialogBase

from safe_qgis.map import Map
from safe_qgis.html_renderer import HtmlRenderer
from safe_qgis.exceptions import QgisPathError
from safe_qgis.safe_interface import temp_dir
from safe_qgis.utilities import getAbsolutePath

from safe_qgis import macro

LOGGER = logging.getLogger('InaSAFE')

myRoot = os.path.dirname(__file__)
defaultSourceDir = os.path.abspath(os.path.join(myRoot, '..', 'script_runner'))


class ScriptDialog(QDialog, Ui_ScriptDialogBase):
    """Script Dialog for InaSAFE."""

    def __init__(self, theParent=None, theIface=None):
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

        self.setupUi(self)

        myHeaderView = self.tblScript.horizontalHeader()
        myHeaderView.setResizeMode(0, QtGui.QHeaderView.Stretch)
        myHeaderView.setResizeMode(1, QtGui.QHeaderView.Interactive)

        self.tblScript.setColumnWidth(0, 200)
        self.tblScript.setColumnWidth(1, 75)

        self.gboOptions.setVisible(False)

        self.adjustSize()

        self.restoreState()

        # preventing error if the user delete the directory
        if not os.path.exists(self.leSourceDir.text()):
            self.leSourceDir.setText(defaultSourceDir)
        self.populateTable(self.leSourceDir.text())

        # connect signal to slot
        self.leOutputDir.textChanged.connect(self.saveState)
        self.leSourceDir.textChanged.connect(self.saveState)
        self.leSourceDir.textChanged.connect(self.populateTable)
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

        Params:
            * theLineEdit - QLineEdit widget instance
            * theTitle - title of dialog
        """
        myPath = theLineEdit.text()
        # noinspection PyCallByClass,PyTypeChecker
        myNewPath = QFileDialog.getExistingDirectory(
            self, theTitle, myPath, QFileDialog.ShowDirsOnly)
        if myNewPath is not None and os.path.exists(myNewPath):
            theLineEdit.setText(myNewPath)

    def populateTable(self, theBasePath):
        """ Populate table with files from theBasePath directory.

        Args:
            theBasePath : QString - path where .txt & .py reside

        Returns:
            None

        Raises:
            None
        """

        LOGGER.info("populateTable from %s" % theBasePath)

        self.tblScript.clearContents()

        # NOTE(gigih): need this line to remove existing rows
        self.tblScript.setRowCount(0)

        myPath = str(theBasePath)

        # only support .py and .txt files
        for myFile in os.listdir(myPath):
            myExt = os.path.splitext(myFile)[1]
            myAbsPath = os.path.join(myPath, myFile)

            if myExt == '.py':
                appendRow(self.tblScript, myFile, myAbsPath)
            elif myExt == '.txt':
                # insert scenarios from file into table widget
                for myKey, myValue in readScenarios(myAbsPath).iteritems():
                    appendRow(self.tblScript, myKey, myValue)

    def runScriptTask(self, theFilename, theCount=1):
        """ Run a python script in QGIS to exercise InaSAFE functionality.

        This functionality was originally intended for verifying that the key
        elements are InaSAFE are loading correctly and available. However,
        the utility of this function is such that you can run any arbitrary
        python scripts with it. As such you can use it it automate
        activities in QGIS, for example automatically running an impact
        assessment in response to an event.

        Args:
           * theFilename: str - the script filename.
           * theCount: int - the number of times the script must be run.

        Returns:
           not applicable

        Raises:
           no exceptions explicitly raised
        """

        # import script module
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

        Params:
            theItem - a dictionary contains the scenario configuration
        Returns:
            True if success, otherwise return False.
        """
        outputDirectory = str(self.leOutputDir.text())
        scenarioDirectory = str(self.leSourceDir.text())
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
        #
        # myMessage = 'Loading layers: \nRoot: %s\n%s' % (scenarioDirectory,
        #                                                 myPaths)
        # LOGGER.info(myMessage)

        try:
            macro.addLayers(dummyScenarioFilePath, myPaths)
        except QgisPathError:
            # set status to 'fail'
            LOGGER.exception('Loading layers failed: \nRoot: %s\n%s' % (
                dummyScenarioFilePath, myPaths))
            return False

        # See if we have a preferred impact function
        if 'function' in theItem:
            myFunctionId = theItem['function']
            myResult = macro.setFunctionId(myFunctionId)
            if not myResult:
                return False

        if 'aggregation' in theItem:
            myResult = macro.setAggregationLayer(theItem['aggregation'])
            if not myResult:
                return False

        # set extent if exist
        if 'extent' in theItem:
            # split extent string
            myCoordinate = theItem['extent'].replace(' ', '').split(',')
            myCount = len(myCoordinate)
            if myCount != 4:
                myMessage = 'extent need exactly 4 value but ' \
                            'got %s instead' % myCount
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

        macro.runScenario()

        return True

    @pyqtSignature('')
    def on_pbnRunAll_clicked(self):
        """Run all scenario wehn pbRunAll is clicked.
        """
        myReport = []
        myFailCount = 0
        myPassCount = 0

        for myRow in range(self.tblScript.rowCount()):
            myItem = self.tblScript.item(myRow, 0)
            myStatusItem = self.tblScript.item(myRow, 1)

            try:
                myResult = self.runTask(myItem, myStatusItem)
                if myResult:
                    # P for passed
                    myReport.append('P: %s\n' % str(myItem))
                    myPassCount += 1
                else:
                    myReport.append('F: %s\n' % str(myItem))
                    myFailCount += 1
            except Exception, e:
                LOGGER.exception('Batch execution failed. The exception: ' +
                                 str(e))
                myReport.append('F: %s\n' % str(myItem))
                myFailCount += 1

        self.showBatchReport(myReport, myPassCount, myFailCount)

    def showBatchReport(self, myReport, myPassCount, myFailCount):
        """Display a report status of Batch Runner"""

        myPath = os.path.join(temp_dir(), 'batch-report.txt')
        myReportFile = file(myPath, 'wt')
        myReportFile.write(' InaSAFE Batch Report File\n')
        myReportFile.write('-----------------------------\n')
        for myLine in myReport:
            myReportFile.write(myLine)
        myReportFile.write('-----------------------------\n')
        myReportFile.write('Total passed: %s\n' % myPassCount)
        myReportFile.write('Total failed: %s\n' % myFailCount)
        myReportFile.write('Total tasks: %s\n' % len(myReport))
        myReportFile.write('-----------------------------\n')
        myReportFile.close()
        LOGGER.info('Log written to %s' % myPath)
        myUrl = QtCore.QUrl('file:///' + myPath)
        # noinspection PyTypeChecker,PyCallByClass,PyArgumentList
        QtGui.QDesktopServices.openUrl(myUrl)

    def runTask(self, theItem, theStatusItem, theCount=1):
        """Run a single task """

        # set status to 'running'
        theStatusItem.setText(self.tr('Running'))

        # .. seealso:: :func:`appendRow` to understand the next 2 lines
        myVariant = theItem.data(QtCore.Qt.UserRole)
        myValue = myVariant.toPyObject()[0]

        myResult = True

        if isinstance(myValue, str):
            myFilename = myValue
            # run script
            try:
                self.runScriptTask(myFilename, theCount)
                # set status to 'OK'
                theStatusItem.setText(self.tr('OK'))
            except Exception as e:
                # set status to 'fail'
                theStatusItem.setText(self.tr('Fail'))

                LOGGER.exception('Running macro failed. The exception: ' +
                                 str(e))
                myResult = False
        elif isinstance(myValue, dict):
            myPath = str(self.leOutputDir.text())
            myTitle = str(theItem.text())

            # check existing pdf report
            myResult = self.checkExistingPDFReport(myPath, [myTitle])
            if myResult is False:
                return False

            # Its a dict containing files for a scenario
            myResult = self.runSimpleTask(myValue)
            if not myResult:
                theStatusItem.setText(self.tr('Fail'))
                myResult = False
            else:

                # NOTE(gigih):
                # Usually after analysis is done, the impact layer
                # become the active layer. <--- WRONG
                myImpactLayer = self.iface.activeLayer()
                self.createPDFReport(myTitle, myPath, myImpactLayer)
        else:
            LOGGER.exception('data type not supported: "%s"' % myValue)
            myResult = False

        return myResult

    def getPDFReportPath(self, theBasePath, theTitle):
        """Get PDF report filename based on theBasePath and theTitle.
        Params:
            * theBasePath - base path of pdf report file
            * theTitle - title of report
        Returns:
            a tuple contains the pdf report filename like this
            ('/home/foo/data/title.pdf', '/home/foo/data/title_table.pdf')
        """

        myFileName = theTitle.replace(' ', '_')
        myFileName += '.pdf'
        myMapPath = os.path.join(theBasePath, myFileName)
        myTablePath = os.path.splitext(myMapPath)[0] + '_table.pdf'

        return myMapPath, myTablePath

    def checkExistingPDFReport(self, theBasePath, theTitles):
        """ Check the existence of pdf report in theBasePath.

        Params:
            * theBasePath - base path of pdf report file
            * theTitle - list of report titles
        Returns:
            True if theBasePath contains no reports or User
            agree to overwrite the report, otherwise return False.
        """

        myPaths = []
        for theTitle in theTitles:
            myPDFPaths = self.getPDFReportPath(theBasePath, theTitle)
            myPDFPaths = [x for x in myPDFPaths if os.path.exists(x)]
            myPaths.extend(myPDFPaths)

        # if reports are not founds, just return True
        if len(myPaths) == 0:
            return True

        # setup message box widget
        myMessage = self.tr(
            "PDF Report already exist in %1. Rewrite the files?")
        myMessage = myMessage.arg(theBasePath)

        myDetail = 'Existing PDF Report: \n'
        myDetail += '\n'.join(myPaths)

        myMsgBox = QMessageBox(self)
        myMsgBox.setIcon(QMessageBox.Question)
        myMsgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        myMsgBox.setText(myMessage)
        myMsgBox.setDetailedText(myDetail)

        # return the result
        myResult = myMsgBox.exec_()
        return myResult == QMessageBox.Yes

    def createPDFReport(self, theTitle, theBasePath, theImpactLayer):
        """Create PDF report from impact layer.
        Create map & table report PDF based from theImpactLayer data.

        Params:
            * theTitle : the report title.
                         Output filename is based from this variable.
            * theBasePath : output directory
            * theImpactLayer : impact layer instance.

        See also:
            Dock.printMap()
        """

        myMap = Map(self.iface)

        # FIXME: check if theImpactLayer is the real impact layer...
        myMap.setImpactLayer(theImpactLayer)

        LOGGER.debug('Create Report: %s' % theTitle)
        myMapPath, myTablePath = self.getPDFReportPath(theBasePath, theTitle)

        # create map pdf
        myMap.printToPdf(myMapPath)

        # create table report pdf
        myHtmlRenderer = HtmlRenderer(myMap.pageDpi)
        myKeywords = myMap.keywordIO.readKeywords(theImpactLayer)
        myHtmlRenderer.printImpactTable(myKeywords, myTablePath)

        LOGGER.debug("report done %s %s" % (myMapPath, myTablePath))

    def updateDefaultOutputDir(self):
        """Update output dir if set to default
        """
        if self.cbDefaultOutputDir.isChecked():
            self.leOutputDir.setText(self.leSourceDir.text())

    @pyqtSignature('')
    def on_btnRunSelected_clicked(self):
        """Run the selected item. """
        myCurrentRow = self.tblScript.currentRow()
        myItem = self.tblScript.item(myCurrentRow, 0)
        myStatusItem = self.tblScript.item(myCurrentRow, 1)
        myCount = self.sboCount.value()

        self.runTask(myItem, myStatusItem, myCount)

    @pyqtSignature('bool')
    def on_pbnAdvanced_toggled(self, theFlag):
        """Autoconnect slot activated when advanced button is clicked"""

        if theFlag:
            self.pbnAdvanced.setText(self.tr('Hide advanced options'))
        else:
            self.pbnAdvanced.setText(self.tr('Show advanced options'))

        self.gboOptions.setVisible(theFlag)
        self.adjustSize()

    @pyqtSignature('bool')
    def on_cbDefaultOutputDir_toggled(self, theFlag):
        """Autoconnect slot activated when cbDefaultOutputDir is checked"""
        if theFlag:
            self.leOutputDir.setText(self.leSourceDir.text())
        self.tbOutputDir.setEnabled(not theFlag)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_tbBaseDataDir_clicked(self):
        """Autoconnect slot activated when the select cache file tool button is
        clicked.
        """
        myTitle = self.tr('Set the base directory for data packages')
        self.showDirectoryDialog(self.leOutputDir, myTitle)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_tbSourceDir_clicked(self):
        """ Autoconnect slot activated when tbSourceDir is clicked """

        myTitle = self.tr('Set the source directory for script and scenario')
        self.showDirectoryDialog(self.leSourceDir, myTitle)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_tbOutputDir_clicked(self):
        """ Autoconnect slot activated when tbSourceDir is clicked """

        myTitle = self.tr('Set the output directory for pdf files')
        self.showDirectoryDialog(self.leOutputDir, myTitle)


def readScenarios(theFileName):
    """Read keywords dictionary from file

    Args:
        theFilename: Name of file holding scenarios .

    Returns:
        Dictionary of with structure like this
        {{ 'foo' : { 'a': 'b', 'c': 'd'},
            { 'bar' : { 'd': 'e', 'f': 'g'}}

    Raises: None

    A scenarios file may look like this:

        [jakarta_flood]
        hazard: /path/to/hazard.tif
        exposure: /path/to/exposure.tif
        function: function_id
        aggregation: /path/to/aggregation_layer.tif
        extent: minx, miny, maxx, maxy
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
     Args:
        * theTable - a QTable instance
        * theLabel - label for the row.
        * theData  - custom data associated with theLabel value.
     Returns:
        None
     Raises:
        None
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

if __name__ == '__main__':
    # from PyQt4.QtGui import QApplication
    # from PyQt4.QtCore import QCoreApplication
    # import sys
    #
    # QCoreApplication.setOrganizationDomain('aifdr')
    # QCoreApplication.setApplicationName('inasafe')
    #
    # app = QApplication(sys.argv)
    # a = ScriptDialog()
    # #a.show()
    #
    # a.saveCurrentScenario()
    #
    # app.exec_()
    pass
