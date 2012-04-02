"""
InaSAFE Disaster risk assessment tool developed by AusAid - **GUI Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.3.0'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
__type__ = 'alpha'  # beta, final etc will be shown in dock title

import numpy
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignature
from is_dock_base import Ui_ISDockBase
from is_help import ISHelp
from is_utilities import getExceptionWithStacktrace, getWGS84resolution
from qgis.core import (QgsMapLayer,
                       QgsVectorLayer,
                       QgsRasterLayer,
                       QgsMapLayerRegistry,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform)
from qgis.gui import QgsMapCanvasLayer
from is_impact_calculator import (ISImpactCalculator,
                              getKeywordFromFile,
                              getKeywordFromLayer,
                              availableFunctions)
from is_clipper import clipLayer
from is_impact_calculator import getOptimalExtent, getBufferedExtent
from is_exceptions import (KeywordNotFoundException,
                            InvalidParameterException)
from is_map import ISMap
from is_utilities import (getTempDir,
                          htmlHeader,
                          htmlFooter,
                          setVectorStyle,
                          setRasterStyle)
# Don't remove this even if it is flagged as unused by your ide
# it is needed for qrc:/ url resolution. See Qt Resources docs.
import resources

#see if we can import pydev - see development docs for details
try:
    from pydevd import *
    print 'Remote debugging is enabled.'
    DEBUG = True
except Exception, e:
    print 'Debugging was disabled'


class ISDock(QtGui.QDockWidget, Ui_ISDockBase):
    """Dock implementation class for the Risk In A Box plugin."""

    def __init__(self, iface):
        """Constructor for the dialog.

        This dialog will allow the user to select layers and scenario details
        and subsequently run their model.

        .. note:: We use the multiple inheritance approach from Qt4 so that
            for elements are directly accessible in the form context and we can
            use autoconnect to set up slots. See article below:
            http://doc.qt.nokia.com/4.7-snapshot/designer-using-a-ui-file.html


        Args:

           * iface - a Quantum GIS QGisAppInterface instance.

        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """
        #settrace()
        QtGui.QDockWidget.__init__(self, None)
        self.setupUi(self)
        self.setWindowTitle(self.tr('InaSAFE %s %s' % (
                                __version__, __type__)))
        # Save reference to the QGIS interface
        self.iface = iface
        self.header = None  # for storing html header template
        self.footer = None  # for storing html footer template
        self.calculator = ISImpactCalculator()
        self.runner = None
        self.helpDialog = None
        self.state = None
        self.runInThreadFlag = False
        self.showOnlyVisibleLayersFlag = True
        self.setLayerNameFromTitleFlag = True
        self.hazardLayers = None  # array of all hazard layers
        self.exposureLayers = None  # array of all exposure layers
        self.readSettings()
        self.getLayers()
        self.setOkButtonStatus()

        myButton = self.pbnHelp
        QtCore.QObject.connect(myButton, QtCore.SIGNAL('clicked()'),
                               self.showHelp)

        myButton = self.pbnPrint
        QtCore.QObject.connect(myButton, QtCore.SIGNAL('clicked()'),
                               self.printMap)
        #self.showHelp()
        myButton = self.pbnRunStop
        QtCore.QObject.connect(myButton, QtCore.SIGNAL('clicked()'),
                               self.accept)
        self.connectLayerListener()
        #myAttribute = QtWebKit.QWebSettings.DeveloperExtrasEnabled
        #QtWebKit.QWebSettings.setAttribute(myAttribute, True)

    def readSettings(self):
        """Set the dock state from QSettings. Do this on init and after
        changing options in the options dialog.
        Args:
            None
        Returns:
            None
        Raises:
        """

        mySettings = QtCore.QSettings()
        myFlag = mySettings.value(
                        'inasafe/useThreadingFlag', False).toBool()
        self.runInThreadFlag = myFlag

        myFlag = mySettings.value(
                        'inasafe/visibleLayersOnlyFlag', True).toBool()
        self.showOnlyVisibleLayersFlag = myFlag

        myFlag = mySettings.value(
                        'inasafe/setLayerNameFromTitleFlag', True).toBool()
        self.setLayerNameFromTitleFlag = myFlag

        self.getLayers()

    def connectLayerListener(self):
        """Establish a signal/slot to listen for changes in the layers loaded
        in QGIS.

        ..seealso:: disconnectLayerListener

        Args:
            None
        Returns:
            None
        Raises:
        """
        QtCore.QObject.connect(QgsMapLayerRegistry.instance(),
                               QtCore.SIGNAL('layerWillBeRemoved(QString)'),
                               self.getLayers)
        QtCore.QObject.connect(QgsMapLayerRegistry.instance(),
                               QtCore.SIGNAL('layerWasAdded(QgsMapLayer)'),
                               self.getLayers)
        QtCore.QObject.connect(QgsMapLayerRegistry.instance(),
                               QtCore.SIGNAL('layerWasAdded(QgsMapLayer)'),
                               self.getLayers)
        QtCore.QObject.connect(QgsMapLayerRegistry.instance(),
                               QtCore.SIGNAL('removedAll()'),
                               self.getLayers)
        QtCore.QObject.connect(self.iface,
                               QtCore.SIGNAL('projectRead()'),
                               self.getLayers)
        QtCore.QObject.connect(self.iface,
                               QtCore.SIGNAL('newProjectCreated()'),
                               self.getLayers)
        # to detect layer visibility changes which registry is ignorant of
        QtCore.QObject.connect(self.iface.mapCanvas(),
                               QtCore.SIGNAL('layersChanged()'),
                               self.canvasLayersetChanged)
        # old implementation - bad because it triggers with every layer
        # visibility change
        #QtCore.QObject.connect(self.iface.mapCanvas(),
        #                       QtCore.SIGNAL('layersChanged()'),
        #                       self.getLayers)

    def disconnectLayerListener(self):
        """Destroy the signal/slot to listen for changes in the layers loaded
        in QGIS.

        ..seealso:: connectLayerListener

        Args:
            None
        Returns:
            None
        Raises:
        """
        try:
            QtCore.QObject.disconnect(QgsMapLayerRegistry.instance(),
                               QtCore.SIGNAL('layerWillBeRemoved(QString)'),
                               self.getLayers)
        except:
            pass

        try:
            QtCore.QObject.disconnect(QgsMapLayerRegistry.instance(),
                               QtCore.SIGNAL('layerWasAdded(QgsMapLayer)'),
                               self.getLayers)
        except:
            pass

        try:
            QtCore.QObject.disconnect(QgsMapLayerRegistry.instance(),
                               QtCore.SIGNAL('removedAll()'),
                               self.getLayers)
        except:
            pass
        try:
            QtCore.QObject.disconnect(self.iface,
                               QtCore.SIGNAL('projectRead()'),
                               self.getLayers)
        except:
            pass

        try:
            QtCore.QObject.disconnect(self.iface,
                               QtCore.SIGNAL('newProjectCreated()'),
                               self.getLayers)
        except:
            pass

        try:
            QtCore.QObject.disconnect(self.iface.mapCanvas(),
                               QtCore.SIGNAL('layersChanged()'),
                               self.canvasLayersetChanged)
        except:
            pass
        # old implementation - bad because it triggers with every layer
        # visibility change
        #QtCore.QObject.disconnect(self.iface.mapCanvas(),
        #                       QtCore.SIGNAL('layersChanged()'),
        #                       self.getLayers)

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

               flag,myMessage = self.validate()

        Raises:
           no exceptions explicitly raised
        """
        myHazardIndex = self.cboHazard.currentIndex()
        myExposureIndex = self.cboExposure.currentIndex()
        if myHazardIndex == -1 or myExposureIndex == -1:
            myMessage = self.tr(
            '<span class="label label-notice">Getting started:'
            '</span> To use this tool you need to add some layers to your '
            'QGIS project. Ensure that at least one <em>hazard</em> layer '
            '(e.g. earthquake MMI) and one <em>exposure</em> layer (e.g. '
            'dwellings) re available. When you are ready, click the <em>'
            'run</em> button below.')
            return (False, myMessage)

        if self.cboFunction.currentIndex() == -1:
            myHazardFilename = str(self.getHazardLayer().source())
            myHazardKeywords = getKeywordFromFile(myHazardFilename)
            myExposureFilename = str(self.getExposureLayer().source())
            myExposureKeywords = getKeywordFromFile(myExposureFilename)
            myMessage = self.tr('<span class="label label-important">No valid '
                         'functions:'
                         '</span> No functions are available for the inputs '
                         'you have specified. '
                         'Try selecting a different combination of inputs. '
                         'Please consult the user manual <FIXME: add link> '
                         'for details on what constitute valid inputs for '
                         'a given risk function. <br>'
                         'Hazard keywords [%s]: %s <br>'
                         'Exposure keywords [%s]: %s' % (
                                myHazardFilename, myHazardKeywords,
                                myExposureFilename, myExposureKeywords))
            return (False, myMessage)
        else:
            myMessage = self.tr('<span class="label label-success">Ready:'
            '</span> You can now proceed to run your model by clicking '
            'the <em> Run</em> button.')
            return (True, myMessage)

    @pyqtSignature('int')  # prevents actions being handled twice
    def on_cboHazard_currentIndexChanged(self, theIndex):
        """Automatic slot executed when the Hazard combo is changed
        so that we can see if the ok button should be enabled.
        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        # Add any other logic you might like here...
        self.getFunctions()
        self.setOkButtonStatus()

    @pyqtSignature('int')  # prevents actions being handled twice
    def on_cboExposure_currentIndexChanged(self, theIndex):
        """Automatic slot executed when the Exposure combo is changed
        so that we can see if the ok button should be enabled.
        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        # Add any other logic you mught like here...
        self.getFunctions()
        self.setOkButtonStatus()

    @pyqtSignature('int')  # prevents actions being handled twice
    def on_cboFunction_currentIndexChanged(self, theIndex):
        """Automatic slot executed when the Function combo is changed
        so that we can see if the ok button should be enabled.
        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        # Add any other logic you mught like here...
        self.setOkButtonStatus()

    def setOkButtonStatus(self):
        """Helper function to set the ok button status if the
        form is valid and disable it if it is not.
        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        myButton = self.pbnRunStop
        myFlag, myMessage = self.validate()
        myButton.setEnabled(myFlag)
        if myMessage is not '':
            self.displayHtml(myMessage)

    def canvasLayersetChanged(self):
        """A helper slot to update the dock combos if the canvas layerset
        has been changed (e.g. one or more layer visibilities changed).
        If self.showOnlyVisibleLayersFlag is set to False this method will
        simply return, doing nothing.
        Args:
            None
        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        if self.showOnlyVisibleLayersFlag:
            self.getLayers()

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
        self.disconnectLayerListener()
        self.saveState()
        self.cboHazard.clear()
        self.cboExposure.clear()
        self.hazardLayers = []
        self.exposureLayers = []
        # Map registry may be invalid if QGIS is shutting down
        myRegistry = None
        try:
            myRegistry = QgsMapLayerRegistry.instance()
        except:
            return
        # mapLayers returns a QMap<QString id, QgsMapLayer layer>
        myLayers = myRegistry.mapLayers().values()
        for myLayer in myLayers:
        #for i in range(len(self.iface.mapCanvas().layers())):
            #myLayer = self.iface.mapCanvas().layer(i)
            if (self.showOnlyVisibleLayersFlag and myLayer not in
                self.iface.mapCanvas().layers()):
                continue

            """
            .. todo:: check raster is single band
            store uuid in user property of list widget for layers
            """

            myName = myLayer.name()
            mySource = str(myLayer.id())
            # See if there is a title for this layer, if not,
            # fallback to the layer's filename
            myTitle = None
            try:
                myTitle = getKeywordFromFile(str(myLayer.source()), 'title')
            except:
                myTitle = myName
            if myTitle and self.setLayerNameFromTitleFlag:
                myLayer.setLayerName(myTitle)

            # find out if the layer is a hazard or an exposure
            # layer by querying its keywords. If the query fails,
            # the layer will be ignored.
            try:
                myCategory = getKeywordFromFile(str(myLayer.source()),
                                                'category')
            except:
                # continue ignoring this layer
                continue
            if myCategory == 'hazard':
                self.addComboItemInOrder(self.cboHazard, myTitle, mySource)
                self.hazardLayers.append(myLayer)
            elif myCategory == 'exposure':
                self.addComboItemInOrder(self.cboExposure, myTitle, mySource)
                self.exposureLayers.append(myLayer)

        # Now populate the functions list based on the layers loaded
        self.getFunctions()
        self.restoreState()
        self.setOkButtonStatus()
        self.connectLayerListener()
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
        # remember what the current function is
        myOriginalFunction = self.cboFunction.currentText()
        self.cboFunction.clear()

        # Get the keyword dictionaries for hazard and exposure
        myHazardLayer = self.getHazardLayer()
        if myHazardLayer is None:
            return
        myHazardFile = myHazardLayer.source()
        myExposureLayer = self.getExposureLayer()
        if myExposureLayer is None:
            return
        myExposureFile = myExposureLayer.source()
        myHazardKeywords = getKeywordFromFile(str(myHazardFile))
        # We need to add the layer type to the returned keywords
        if myHazardLayer.type() == QgsMapLayer.VectorLayer:
            myHazardKeywords['layertype'] = 'vector'
        elif myHazardLayer.type() == QgsMapLayer.RasterLayer:
            myHazardKeywords['layertype'] = 'raster'

        myExposureKeywords = getKeywordFromFile(str(myExposureFile))
        # We need to add the layer type to the returned keywords
        if myExposureLayer.type() == QgsMapLayer.VectorLayer:
            myExposureKeywords['layertype'] = 'vector'
        elif myExposureLayer.type() == QgsMapLayer.RasterLayer:
            myExposureKeywords['layertype'] = 'raster'

        # Find out which functions can be used with these layers
        myList = [myHazardKeywords, myExposureKeywords]
        try:
            myDict = availableFunctions(myList)
            # Populate the hazard combo with the available functions
            for myFunction in myDict:  # Use only key
                self.addComboItemInOrder(self.cboFunction, myFunction)
        except Exception, e:
            raise e

        self.restoreFunctionState(myOriginalFunction)

    def readImpactLayer(self, myEngineImpactLayer):
        """Helper function to read and validate layer

        Args
            myEngineImpactLayer: Layer object as provided by the inasafe engine

        Returns
            validated qgis layer or None

        Raises
            Exception if layer is not valid
        """

        myMessage = ('Input argument must be a InaSAFE spatial object. '
               'I got %s' % type(myEngineImpactLayer))
        if not hasattr(myEngineImpactLayer, 'is_inasafe_spatial_object'):
            raise Exception(myMessage)
        if not myEngineImpactLayer.is_inasafe_spatial_object:
            raise Exception(myMessage)

        # Get associated filename and symbolic name
        myFilename = myEngineImpactLayer.get_filename()
        myName = myEngineImpactLayer.get_name()

        # Read layer
        if myEngineImpactLayer.is_vector:
            myQgisLayer = QgsVectorLayer(myFilename, myName, 'ogr')
        elif myEngineImpactLayer.is_raster:
            myQgisLayer = QgsRasterLayer(myFilename, myName)

        # Verify that new qgis layer is valid
        if myQgisLayer.isValid():
            return myQgisLayer
        else:
            myMessage = self.tr('Loaded impact layer "%s" is not'
                                ' valid' % myFilename)
            raise Exception(myMessage)

    def getHazardLayer(self):
        """Obtain qgsmaplayer id from the userrole of the QtCombo for exposure
        and return it as a QgsMapLayer"""
        myIndex = self.cboHazard.currentIndex()
        if myIndex < 0:
            return None
        myLayerId = self.cboHazard.itemData(myIndex,
                             QtCore.Qt.UserRole).toString()
        myLayer = QgsMapLayerRegistry.instance().mapLayer(myLayerId)
        return myLayer

    def getExposureLayer(self):
        """Obtain the name of the path to the exposure file from the
        userrole of the QtCombo for exposure."""

        myIndex = self.cboExposure.currentIndex()
        if myIndex < 0:
            return None
        myLayerId = self.cboExposure.itemData(myIndex,
                             QtCore.Qt.UserRole).toString()
        myLayer = QgsMapLayerRegistry.instance().mapLayer(myLayerId)
        return myLayer

    def setupCalculator(self):
        """Initialise the ISImpactCalculator based on the current
        state of the ui."""
        myHazardFilename = None
        myExposureFilename = None
        try:
            myHazardFilename, myExposureFilename = self.optimalClip()
        except Exception, e:
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            raise
        self.calculator.setHazardLayer(myHazardFilename)
        self.calculator.setExposureLayer(myExposureFilename)
        self.calculator.setFunction(self.cboFunction.currentText())

    def accept(self):
        """Execute analysis when ok button is clicked."""
        #.. todo:: FIXME (Tim) We may have to implement some polling logic
        # because the putton click accept() function and the updating
        # of the web view after model completion are asynchronous (when
        # threading mode is enabled especially)
        self.showBusy()
        myFlag, myMessage = self.validate()
        if not myFlag:
            self.displayHtml(myMessage)
            self.hideBusy()
            return

        try:
            self.setupCalculator()
        except Exception, e:
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            myMessage = self.tr('<p><span class="label label-important">'
                                'Error:</span> '
                                'An exception occurred when setting up the '
                                'impact calculator.')
            myMessage += getExceptionWithStacktrace(e, html=True)
            self.displayHtml(myMessage)
            return

        self.runner = self.calculator.getRunner()
        QtCore.QObject.connect(self.runner.notifier(),
                               QtCore.SIGNAL('done()'),
                               self.completed)

        try:
            QtGui.qApp.setOverrideCursor(
                    QtGui.QCursor(QtCore.Qt.WaitCursor))
            self.repaint()
            QtGui.qApp.processEvents()

            myTitle = self.tr('Calculating impact...')
            myMessage = self.tr('This may take a little while - we are '
                                'computing the areas that will be impacted '
                                'by the hazard and writing the result to '
                                'a new layer.')
            myProgress = 66
            self.showBusy(myTitle, myMessage, myProgress)
            if self.runInThreadFlag:
                self.runner.start()  # Run in different thread
            else:
                self.runner.run()  # Run in same thread
            QtGui.qApp.restoreOverrideCursor()
            # .. todo :: Disconnect done slot/signal
        except Exception, e:
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            myMessage = self.tr('<p><span class="label label-important">'
                                'Error:</span> '
                                'An exception occurred when starting'
                                ' the model.')
            myMessage += getExceptionWithStacktrace(e, html=True)
            self.displayHtml(myMessage)

    def completed(self):
        """Slot activated when the process is done."""

        # Try to run completion code
        try:
            myReport = self._completed()
        except Exception, e:
            # Display message and traceback
            myMessage = getExceptionWithStacktrace(e, html=True)
            self.displayHtml(myMessage)
        else:
            # On success, display generated report
            self.displayHtml(myReport)
        self.saveState()
        # Hide hour glass
        self.hideBusy()

    def _completed(self):
        """Helper function for slot activated when the process is done.

        Args
            None
        Returns
            Report to render on canvas
        Raises
            Exceptions on a range of error conditions

        Provides report out from impact_function to canvas
        """

        myTitle = self.tr('Loading results...')
        myMessage = self.tr('The impact assessment is complete - loading '
                            'the results into QGIS now...')
        myProgress = 99
        self.showBusy(myTitle, myMessage, myProgress)

        myMessage = self.runner.result()
        myEngineImpactLayer = self.runner.impactLayer()

        if myEngineImpactLayer is None:
            myMessage = self.tr('No impact layer was calculated. '
                   'Error message: %s\n' % str(myMessage))
            raise Exception(myMessage)

        # Get tabular information from impact layer
        myReport = getKeywordFromLayer(myEngineImpactLayer, 'impact_summary')

        # Get requested style for impact layer of either kind
        myStyle = myEngineImpactLayer.get_style_info()

        # Load impact layer into QGIS
        myQgisImpactLayer = self.readImpactLayer(myEngineImpactLayer)
        # Determine styling for QGIS layer
        if myEngineImpactLayer.is_vector:
            if not myStyle:
                # Set default style if possible
                pass
            else:
                setVectorStyle(myQgisImpactLayer, myStyle)
        elif myEngineImpactLayer.is_raster:
            if not myStyle:
                myQgisImpactLayer.setDrawingStyle(
                                QgsRasterLayer.SingleBandPseudoColor)
                myQgisImpactLayer.setColorShadingAlgorithm(
                                QgsRasterLayer.PseudoColorShader)
            else:
                setRasterStyle(myQgisImpactLayer, myStyle)

        else:
            myMessage = self.tr('Impact layer %s was neither a raster or a '
                   'vector layer' % myQgisImpactLayer.source())
            raise Exception(myMessage)
        # Finally, add layer to QGIS
        QgsMapLayerRegistry.instance().addMapLayer(myQgisImpactLayer)
        self.restoreState()
        # Return text to display in report pane
        return myReport

    def showHelp(self):
        """Load the help text into the wvResults widget"""
        if not self.helpDialog:
            self.helpDialog = ISHelp(self.iface.mainWindow(), 'dock')
        self.helpDialog.show()

    def showBusy(self, theTitle=None, theMessage=None, theProgress=0):
        """A helper function to indicate the plugin is processing.
        Args:
            * theTitle - an optional title for the status update. Should be
              plain text only
            * theMessage - an optional message to pass to the busy indicator.
              Can be an html snippet.
            * theProgress - a number between 0 and 100 indicating % complete

        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propagated.

        ..note:: Uses bootstrap css for progress bar.
        """
        #self.pbnRunStop.setText('Cancel')
        self.pbnRunStop.setEnabled(False)
        if theTitle is None:
            theTitle = self.tr('Analyzing this question...')
        myHtml = ('<div><span class="label label-success">'
                  + str(theTitle) + '</span></div>'
                  '<div>' + str(theMessage) + '</div>'
                  '<div class="progress">'
                  '  <div class="bar" '
                  '       style="width: ' + str(theProgress) + '%;">'
                  '  </div>'
                  '</div>')
        self.displayHtml(myHtml)
        self.repaint()
        QtGui.qApp.processEvents()
        self.grpQuestion.setEnabled(False)

    def hideBusy(self):
        """A helper function to indicate processing is done."""
        #self.pbnRunStop.setText('Run')
        if self.runner:
            QtCore.QObject.disconnect(self.runner.notifier(),
                               QtCore.SIGNAL('done()'),
                               self.completed)
            del self.runner
            self.runner = None

        self.grpQuestion.setEnabled(True)
        self.pbnRunStop.setEnabled(True)
        self.repaint()

    def enableBusyCursor(self):
        """Set the hourglass enabled."""
        QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))

    def disableBusyCursor(self):
        """Disable the hourglass cursor"""
        QtGui.qApp.restoreOverrideCursor()

    def optimalClip(self):
        """ A helper function to perform an optimal clip of the input data.
        Optimal extent should be considered as the intersection between
        the three inputs. The inasafe library will perform various checks
        to ensure that the extent is tenable, includes data from both
        etc.

        The result of this function will be two layers which are
        clipped and resampled if needed, and in the EPSG:4326 geographic
        coordinate reference system..

        Args:
            None
        Returns:
            A two-tuple containing the paths to the clipped hazard and
            exposure layers.

        Raises:
            Any exceptions raised by the InaSAFE library will be propogated.
        """

        # Get the hazard and exposure layers selected in the combos
        myHazardLayer = self.getHazardLayer()
        myExposureLayer = self.getExposureLayer()

        # Reproject all extents to EPSG:4326 if needed
        myGeoCrs = QgsCoordinateReferenceSystem()
        myGeoCrs.createFromEpsg(4326)

        # Get the current viewport extent as an array in EPSG:4326
        myViewportGeoExtent = self.viewportGeoArray()

        # Get the Hazard extents as an array in EPSG:4326
        myHazardGeoExtent = self.extentToGeoArray(myHazardLayer.extent(),
                                                  myHazardLayer.crs())

        # Get the Exposure extents as an array in EPSG:4326
        myExposureGeoExtent = self.extentToGeoArray(myExposureLayer.extent(),
                                                    myExposureLayer.crs())

        # Now work out the optimal extent between the two layers and
        # the current view extent. The optimal extent is the intersection
        # between the two layers and the viewport.
        myGeoExtent = None
        try:
            # Extent is returned as an array [xmin,ymin,xmax,ymax]
            # We will convert it to a QgsRectangle afterwards.
            myGeoExtent = getOptimalExtent(myHazardGeoExtent,
                                           myExposureGeoExtent,
                                           myViewportGeoExtent)
        except Exception, e:
            myMessage = self.tr('<p>There '
                   'was insufficient overlap between the input layers '
                   'and / or the layers and the viewport. Please select '
                   'two overlapping layers and zoom or pan to them. Full '
                   'details follow:</p>'
                   '<p>Failed to obtain the optimal extent given:</p>'
                   '<p>Hazard: %s</p>'
                   '<p>Exposure: %s</p>'
                   '<p>Viewport Geo Extent: %s</p>'
                   '<p>Hazard Geo Extent: %s</p>'
                   '<p>Exposure Geo Extent: %s</p>'
                   '<p>Details: %s</p>'
                   %
                   (myHazardLayer.source(),
                    myExposureLayer.source(),
                    myViewportGeoExtent,
                    myHazardGeoExtent,
                    myExposureGeoExtent,
                    str(e)))
            raise Exception(myMessage)

        # Next work out the ideal spatial resolution for rasters
        # in the analysis. If layers are not native WGS84, we estimate
        # this based on the geographic extents
        # rather than the layers native extents so that we can pass
        # the ideal WGS84 cell size and extents to the layer prep routines
        # and do all preprocessing in a single operation.
        # All this is done in the function getWGS84resolution
        myBufferedGeoExtent = myGeoExtent  # Bbox to use for hazard layer
        myCellSize = None
        extraExposureKeywords = {}
        if myHazardLayer.type() == QgsMapLayer.RasterLayer:

            # Hazard layer is raster
            myHazardGeoCellSize = getWGS84resolution(myHazardLayer,
                                                     myHazardGeoExtent)

            if myExposureLayer.type() == QgsMapLayer.RasterLayer:

                # In case of two raster layers establish common resolution
                myExposureGeoCellSize = getWGS84resolution(myExposureLayer,
                                                           myExposureGeoExtent)

                if myHazardGeoCellSize < myExposureGeoCellSize:
                    myCellSize = myHazardGeoCellSize
                else:
                    myCellSize = myExposureGeoCellSize

                # Record native resolution to allow rescaling of exposure data
                if not numpy.allclose(myCellSize, myExposureGeoCellSize):
                    extraExposureKeywords['resolution'] = myExposureGeoCellSize
            else:
                # If exposure is vector data grow hazard raster layer to
                # ensure there are enough pixels for points at the edge of
                # the view port to be interpolated correctly. This requires
                # resolution to be available
                if myExposureLayer.type() != QgsMapLayer.VectorLayer:
                    raise RuntimeError
                myBufferedGeoExtent = getBufferedExtent(myGeoExtent,
                                                        myHazardGeoCellSize)
        else:
            # Hazard layer is vector
            if myExposureLayer.type() == QgsMapLayer.RasterLayer:
                myMessage = self.tr('Raster exposure with vector hazard not '
                              'implemented')
                raise Exception(myMessage)
            else:
                # Both layers are vector
                pass

        # Make sure that we have EPSG:4326 versions of the input layers
        # that are clipped and (in the case of two raster inputs) resampled to
        # the best resolution.
        myTitle = self.tr('Preparing hazard data...')
        myMessage = self.tr('We are resampling and clipping the hazard'
                            'layer to match the intersection of the exposure'
                            'layer and the current view extents.')
        myProgress = 22
        self.showBusy(myTitle, myMessage, myProgress)
        myClippedHazardPath = clipLayer(myHazardLayer, myBufferedGeoExtent,
                                        myCellSize)

        myTitle = self.tr('Preparing exposure data...')
        myMessage = self.tr('We are resampling and clipping the exposure'
                            'layer to match the intersection of the hazard'
                            'layer and the current view extents.')
        myProgress = 44
        self.showBusy(myTitle, myMessage, myProgress)
        myClippedExposurePath = clipLayer(myExposureLayer,
                                          myGeoExtent, myCellSize,
                                          extraKeywords=extraExposureKeywords)

        return myClippedHazardPath, myClippedExposurePath

        ############################################################
        # logic checked to here..............
        ############################################################
        # .. todo:: Cleanup temporary working files, careful not to delete
        #            User's own data'

        # FIXME: Turn paths back into layers temporarily and print res
        #myExposureLayer = QgsRasterLayer(myClippedExposurePath, 'exp')
        #myHazardLayer = QgsRasterLayer(myClippedHazardPath, 'haz')

        #myHazardUPP = myHazardLayer.rasterUnitsPerPixel()
        #myExposureUPP = myExposureLayer.rasterUnitsPerPixel()

        # FIXME (Ole): This causes some strange failures. Revisit!
        # Check that resolutions are equal up to some precision

        #myMessage = ('Resampled pixels sizes did not match: '
        #       'Exposure pixel size = %.12f, '
        #       'Hazard pixel size = %.12f' % (myExposureUPP, myHazardUPP))
        #if not numpy.allclose(myExposureUPP, myHazardUPP,
        #                      # FIXME (Ole): I would like to make this tighter
        #                      rtol=1.0e-6, atol=1.0e-3):
        #    raise RuntimeError(myMessage)

        #print "Resampled Exposure Units Per Pixel: %s" % myExposureUPP
        #print "Resampled Hazard Units Per Pixel: %s" % myHazardUPP

    def viewportGeoArray(self):
        """Obtain the map canvas current extent in EPSG:4326"""

        # get the current viewport extent
        myCanvas = self.iface.mapCanvas()
        myRect = myCanvas.extent()

        myCrs = None

        if myCanvas.hasCrsTransformEnabled():
            myCrs = myCanvas.mapRenderer().destinationCrs()
        else:
            # some code duplication from extentToGeoArray here
            # in favour of clarity of logic...
            myCrs = QgsCoordinateReferenceSystem()
            myCrs.createFromEpsg(4326)

        return self.extentToGeoArray(myRect, myCrs)

    def extentToGeoArray(self, theExtent, theSourceCrs):
        """Convert the supplied extent to geographic and return as as array"""

        # FIXME (Ole): As there is no reference to self, this function
        #              should be a general helper outside the class
        myGeoCrs = QgsCoordinateReferenceSystem()
        myGeoCrs.createFromEpsg(4326)
        myXForm = QgsCoordinateTransform(
                            theSourceCrs,
                            myGeoCrs)

        # Get the clip area in the layer's crs
        myTransformedExtent = myXForm.transformBoundingBox(theExtent)

        myGeoExtent = [myTransformedExtent.xMinimum(),
                       myTransformedExtent.yMinimum(),
                       myTransformedExtent.xMaximum(),
                       myTransformedExtent.yMaximum()]
        return myGeoExtent

    def htmlHeader(self):
        """Get a standard html header for wrapping content in."""
        if self.header is None:
            self.header = htmlHeader()
        return self.header

    def htmlFooter(self):
        """Get a standard html footer for wrapping content in."""
        if self.footer is None:
            self.footer = htmlFooter()
        return self.footer

    def displayHtml(self, theMessage):
        """Given an html snippet, wrap it in a page header and footer
        and display it in the wvResults widget."""
        myHtml = self.htmlHeader() + theMessage + self.htmlFooter()
        #f = file('/tmp/h.thml', 'wa')  # for debugging
        #f.write(myHtml)
        #f.close()
        self.wvResults.setHtml(myHtml)

    def layerChanged(self, theLayer):
        """Handler for when the QGIS active layer is changed.
        If the active layer is changed and it has keywords and a report,
        show the report..

        .. see also:: :func:`IS.layerChanged`.

        Args:
           theLayer - the QgsMapLayer instance that is now active..
        Returns:
           None.
        Raises:
           no exceptions explicitly raised.
        """
        myReport = None
        if theLayer is not None:
            try:
                myReport = getKeywordFromFile(str(theLayer.source()),
                                              'impact_summary')
            except KeywordNotFoundException, e:
                self.setOkButtonStatus()
            except InvalidParameterException, e:
                self.setOkButtonStatus()
            except Exception, e:
                myReport = getExceptionWithStacktrace(e, html=True)
            if myReport is not None:
                self.displayHtml(myReport)
                self.pbnPrint.setEnabled(True)
            else:
                self.pbnPrint.setEnabled(False)

    def saveState(self):
        """Save the current state of the ui to an internal class member
        so that it can be restored again easily.

        Args:
            None
        Returns:
            None
        Raises:
            Any exceptions raised by the InaSAFE library will be propogated.
        """
        myStateDict = {'hazard': self.cboHazard.currentText(),
                       'exposure': self.cboExposure.currentText(),
                       'function': self.cboFunction.currentText(),
                       'report':
                           self.wvResults.page().currentFrame().toHtml()}
        self.state = myStateDict

    def restoreState(self):
        """Restore the state of the dock to the last known state.
        Args:
            None
        Returns:
            None
        Raises:
            Any exceptions raised by the InaSAFE library will be propogated.
        """
        if self.state is None:
            return
        for myCount in range(0, self.cboExposure.count()):
            myItemText = self.cboExposure.itemText(myCount)
            if myItemText == self.state['exposure']:
                self.cboExposure.setCurrentIndex(myCount)
                break
        for myCount in range(0, self.cboHazard.count()):
            myItemText = self.cboHazard.itemText(myCount)
            if myItemText == self.state['hazard']:
                self.cboHazard.setCurrentIndex(myCount)
                break
        self.restoreFunctionState(self.state['function'])
        self.wvResults.setHtml(self.state['report'])

    def restoreFunctionState(self, theOriginalFunction):
        """Restore the function combo to a known state.
        Args:
            theOriginalFunction - name of function that should be selected
        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        # Restore previous state of combo
        for myCount in range(0, self.cboFunction.count()):
            myItemText = self.cboFunction.itemText(myCount)
            if myItemText == theOriginalFunction:
                self.cboFunction.setCurrentIndex(myCount)
                break

    def printMap(self):
        """Slot to print map when print map button pressed.
        Args:
            None
        Returns:
            None
        Raises:
            Any exceptions raised by the InaSAFE library will be propogated.
        """
        myFilename = QtGui.QFileDialog.getSaveFileName(self,
                            self.tr('Write to pdf'),
                            getTempDir(),
                            self.tr('Pdf File (*.pdf)'))
        myMap = ISMap(self.iface)
        myMap.setImpactLayer(self.iface.activeLayer())
        self.showBusy()
        try:
            myMap.makePdf(myFilename)
            self.displayHtml(self.tr('<div><span class="label label-success">'
                             'PDF Created</div>'
                             'Your map was saved as %s' % myFilename))
            QtGui.QDesktopServices.openUrl(QtCore.QUrl('file:///' + myFilename,
                                 QtCore.QUrl.TolerantMode))
        except Exception, e:
            myReport = getExceptionWithStacktrace(e, html=True)
            if myReport is not None:
                self.displayHtml(myReport)

        self.hideBusy()
        myMap.showComposer()

    def addComboItemInOrder(self, theCombo, theItemText, theItemData=None):
        """Although QComboBox allows you to set an InsertAlphabetically enum
        this only has effect when a user interactively adds combo items to
        an editable combo. This we have this little function to ensure that
        combos are always sorted alphabetically.
        Args:
            * theCombo - combo box receiving the new item
            * theItemText - display text for the combo
            * theItemData - optional UserRole data to be associated with
              the item

        Returns:
            None
        Raises:

        ..todo:: Move this to utilities
        """
        mySize = theCombo.count()
        for myCount in range(0, mySize):
            myItemText = str(theCombo.itemText(myCount))
            # see if theItemText alphabetically precedes myItemText
            if cmp(theItemText, myItemText) < 0:
                theCombo.insertItem(myCount, theItemText, theItemData)
                return
        #otherwise just add it to the end
        theCombo.insertItem(mySize, theItemText, theItemData)
