"""
Disaster risk assessment tool developed by AusAid - **GUI Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')


from PyQt4 import QtGui, QtCore
from ui_riabdock import Ui_RiabDock
import os

# Check if a pydevpath.txt file exists in the plugin folder (you
# need to rename it from settings.txt.templ in the standard plugin
# distribution) and if it does, read the pydevd path from it and
# enable the debug flag to true. Please see:
# http://linfiniti.com/2011/12/remote-debugging-qgis-python-plugins-with-pydev/
# for notes on setting up the debugging environment.
ROOT = os.path.dirname(__file__)
PATH = os.path.abspath(os.path.join(ROOT, 'pydevpath.txt'))
DEBUG = False
if os.path.isfile(PATH):
    try:
        PYDEVD_PATH = file(PATH, 'rt').readline()
        DEBUG = True
        import sys
        sys.path.append(PYDEVD_PATH)
        from pydevd import *
        print 'Debugging is enabled.'
        #print sys.path
    except:
        #fail silently
        pass

from qgis.core import (QgsMapLayer, QgsVectorLayer,
                QgsMapLayerRegistry, QgsGraduatedSymbolRendererV2,
                QgsSymbolV2, QgsRendererRangeV2)
from impactcalculator import ImpactCalculator
import tempfile


class RiabDock(QtGui.QDockWidget):
    """Dock implementation class for the Risk In A Box plugin."""

    def __init__(self, iface, guiContext=True):
        """Constructor for the dialog.

        This dialog will allow the user to select layers and scenario details
        and subsequently run their model.

        Args:

           * iface - a Quantum GIS QGisAppInterface instance.
           * guidContext - an optional paramter, defaults to True. Set to
             False if you do not wish to see popup messages etc. Used
             mainly by init tests.

        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """
        if DEBUG:
            # settrace()
            pass
        QtGui.QDockWidget.__init__(self, None)

        # Save reference to the QGIS interface
        self.iface = iface
        self.suppressDialogsFlag = guiContext
        self.calculator = ImpactCalculator()
        self.runner = None
        # Set up the user interface from Designer.
        self.ui = Ui_RiabDock()
        self.ui.setupUi(self)
        self.getLayers()
        self.getFunctions()
        self.setOkButtonStatus()
        myButton = self.ui.pbnHelp
        QtCore.QObject.connect(myButton, QtCore.SIGNAL('clicked()'),
                                self.showHelp)
        #self.showHelp()
        myButton = self.ui.pbnRunStop
        QtCore.QObject.connect(myButton, QtCore.SIGNAL('clicked()'),
                                self.accept)
        QtCore.QObject.connect(self.iface.mapCanvas(),
                               QtCore.SIGNAL('layersChanged()'),
                               self.getLayers)

    def validate(self):
        """Helper method to evaluate the current state of the dialog and
        determine if it is appropriate for the OK button to be enabled
        or not.

        .. note:: The enabled state of the OK button on the dialog will
           NOT be updated (set True or False) depending on the outcome of
           the UI readiness tests performed - **only** True or False
           will be returned by the function.

        Args:
           None.
        Returns:
           A two-tuple consisting of:

           * Boolean reflecting the results of the valudation tests.
           * A message indicating any reason why the validation may
             have failed.

           Example::

               flag,msg = self.ui.validate()

        Raises:
           no exceptions explicitly raised
        """
        myHazardIndex = self.ui.cboHazard.currentIndex()
        myExposureIndex = self.ui.cboExposure.currentIndex()
        if myHazardIndex == -1 or myExposureIndex == -1:
            myMessage = 'Please ensure both Hazard layer and ' + \
            'Exposure layer are set before clicking Run.'
            return (False, myMessage)
        else:
            return (True, '')

    def setOkButtonStatus(self):
        """Helper function to set the ok button status if the
        form is valid and disable it if it is not.
        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        myButton = self.ui.pbnRunStop
        myFlag, myMessage = self.validate()
        myButton.setEnabled(myFlag)
        if myMessage is not '':
            self.ui.wvResults.setHtml(myMessage)

    def getLayers(self):
        """Helper function to obtain a list of layers currently loaded in QGIS.

        On invocation, this method will populate cboHazard and
        cboExposure on the dialog with a list of available layers. Only
        **singleband raster** layers will be added to the hazard layer list,
        and only **point vector** layers will be added to the exposure layer
        list.

        Args:
           None.
        Returns:
           None
        Raises:
           no
        """
        self.ui.cboHazard.clear()
        self.ui.cboExposure.clear()
        for i in range(len(self.iface.mapCanvas().layers())):
            try:
                myLayer = self.iface.mapCanvas().layer(i)
                """
                .. todo:: check raster is single band
                          store uuid in user property of list widget for layers
                """
                if myLayer.type() == QgsMapLayer.RasterLayer:
                    myName = myLayer.name()
                    mySource = myLayer.source()
                    self.ui.cboHazard.addItem(myName, mySource)

                elif myLayer.type() == QgsMapLayer.VectorLayer:
                    myName = myLayer.name()
                    mySource = myLayer.source()
                    self.ui.cboExposure.addItem(myName, mySource)
                else:
                    pass  # skip the layer
            except:
                pass
        self.setOkButtonStatus()
        return

    def getFunctions(self):
        """Helper function to obtain a list of impact functions from
        the impact calculator.

        Args:
           None.
        Returns:
           None
        Raises:
           no
        """
        try:
            myList = self.calculator.availableFunctions()
            for myFunction in myList:
                self.ui.cboFunction.addItem(myFunction)
        except Exception, e:
            if not self.suppressDialogsFlag:
                raise e
            else:
                QtGui.QMessageBox.critical(self,
                  'Function list retireval error', str(e))

    def accept(self):
        """Execute analysis when ok button is clicked."""
        self.showBusy()
        #QtGui.QMessageBox.information(self, "Risk In A Box", "testing...")
        myFlag, myMessage = self.validate()
        if not myFlag:
            self.ui.wvResults.setHtml(myMessage)
            self.hideBusy()
            return
        try:
            myHazardIndex = self.ui.cboHazard.currentIndex()
            myHazardFileName = self.ui.cboHazard.itemData(myHazardIndex,
                                 QtCore.Qt.UserRole).toString()
            self.calculator.setHazardLayer(myHazardFileName)

            myExposureIndex = self.ui.cboExposure.currentIndex()
            myExposureFileName = self.ui.cboExposure.itemData(myExposureIndex,
                                 QtCore.Qt.UserRole).toString()
            self.calculator.setExposureLayer(myExposureFileName)

            self.calculator.setFunction(self.ui.cboFunction.currentText())
            # start it in its own thread
            self.runner = self.calculator.getRunner()

            QtCore.QObject.connect(self.runner.notifier(),
                               QtCore.SIGNAL('done()'),
                               self.completed)
            self.runner.start()

        except Exception, e:
            self.hideBusy()
            msg = 'An exception occurred when starting the model: %s' % (
                    (str(e)))
            self.ui.wvResults.setHtml(msg)

    def completed(self):
        """Slot activated when the process is done."""
        #settrace()
        myMessage = self.runner.result()
        myImpactLayer = self.runner.impactLayer()
        myReport = ''
        if myImpactLayer:
            myFilename = myImpactLayer.get_filename()
            try:
                myReport = self.calculator.getMetadata(
                                            myImpactLayer, 'caption')
                self.ui.wvResults.setHtml(myMessage + '\n' +
                        myFilename +
                        '\n' + myReport)
                myVectorPath = os.path.join(tempfile.gettempdir(),
                        myFilename)
                myName = (self.ui.cboExposure.currentText() + 'X' +
                          self.ui.cboHazard.currentText() + 'X' +
                          self.ui.cboFunction.currentText())
                myVectorLayer = QgsVectorLayer(myVectorPath, myName, 'ogr')
                if not myVectorLayer.isValid():
                    msg = 'Vector layer "%s" is not valid' % myFilename
                    self.ui.wvResults.setHtml(msg)
                    self.hideBusy()
                    return

                myStyle = myImpactLayer.get_style_info()
                myTargetField = myStyle['target_field']
                myClasses = myStyle['style_classes']
                myRangeList = []
                for myClass in myClasses:
                    myOpacity = myClass['opacity']
                    myMax = myClass['max']
                    myMin = myClass['min']
                    myColour = myClass['colour']
                    myLabel = myClass['label']
                    myColour = QtGui.QColor(myColour)
                    mySymbol = QgsSymbolV2.defaultSymbol(
                                myVectorLayer.geometryType())
                    mySymbol.setColor(myColour)
                    mySymbol.setAlpha(myOpacity)
                    myRange = QgsRendererRangeV2(
                                myMin,
                                myMax,
                                mySymbol,
                                myLabel)
                    myRangeList.append(myRange)
                myRenderer = QgsGraduatedSymbolRendererV2(
                                '', myRangeList)
                myRenderer.setMode(
                        QgsGraduatedSymbolRendererV2.EqualInterval)
                myRenderer.setClassAttribute(myTargetField)

                myVectorLayer.setRendererV2(myRenderer)
                QgsMapLayerRegistry.instance().addMapLayer(myVectorLayer)
                #QtGui.QMessageBox.information(
                #                self, 'Risk in a box', str(myStyle))
            except Exception, e:
                self.ui.wvResults.setHtml(myMessage + '\n' + myFilename +
                                 '\nError:\n' + str(e))

        self.hideBusy()

    def showHelp(self):
        """Load the help text into the wvResults widget"""
        myPath = os.path.abspath(os.path.join(ROOT, 'docs', 'build',
                                            'html', 'README.html'))
        self.ui.wvResults.setUrl(QtCore.QUrl('file:///' + myPath))

    def showBusy(self):
        """A helper function to indicate the plugin is processing."""
        #self.ui.pbnRunStop.setText('Cancel')
        self.ui.pbnRunStop.setEnabled(False)
        myHtml = ('<center><p>Analyzing this question...</p>' +
                   '<img src="qrc:/plugins/riab/ajax-loader.gif" />' +
                   '</center>')
        self.ui.wvResults.setHtml(myHtml)
        self.ui.grpQuestion.setEnabled(False)

    def hideBusy(self):
        """A helper function to indicate processing is done."""
        #self.ui.pbnRunStop.setText('Run')
        if self.runner:
            del self.runner

        self.ui.grpQuestion.setEnabled(True)
        self.ui.pbnRunStop.setEnabled(True)
        self.repaint()

    def resetForm(self):
        """Reset the form contents to their onload state."""
        self.ui.cboFunction.setCurrentIndex(0)
        self.ui.cboHazard.setCurrentIndex(0)
        self.ui.cboExposure.setCurrentIndex(0)
        self.showHelp()

    def enableBusyCursor(self):
        """Set the hourglass enabled."""
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

    def disableBusyCursor(self):
        """Disable the hourglass cursor"""
        QtGui.qApp.restoreOverrideCursor()
