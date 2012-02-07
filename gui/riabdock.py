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
from PyQt4.QtCore import pyqtSignature
from ui_riabdock import Ui_RiabDock
from riabhelp import RiabHelp
from utilities import getExceptionWithStacktrace, getWGS84resolution
from qgis.core import (QGis, QgsMapLayer, QgsVectorLayer, QgsRasterLayer,
                       QgsMapLayerRegistry, QgsGraduatedSymbolRendererV2,
                       QgsSymbolV2, QgsRendererRangeV2,
                       QgsSymbolLayerV2Registry, QgsColorRampShader,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform)
from impactcalculator import ImpactCalculator
from riabclipper import clipLayer
from impactcalculator import getOptimalExtent, getBufferedExtent

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


def setVectorStyle(qgisVectorLayer, style):
    """Set QGIS vector style based on RIAB style dictionary

    Input
        qgisVectorLayer: Qgis layer
        style: Dictionary of the form as in the example below

        {'target_field': 'DMGLEVEL',
        'style_classes':
        [{'opacity': 1, 'max': 1.5, 'colour': '#fecc5c',
          'min': 0.5, 'label': 'Low damage'},
        {'opacity': 1, 'max': 2.5, 'colour': '#fd8d3c',
         'min': 1.5, 'label': 'Medium damage'},
        {'opacity': 1, 'max': 3.5, 'colour': '#f31a1c',
         'min': 2.5, 'label': 'High damage'}]}

    Output
        Sets and saves style for qgisVectorLayer

    """
    myTargetField = style['target_field']
    myClasses = style['style_classes']
    myGeometryType = qgisVectorLayer.geometryType()

    myRangeList = []
    for myClass in myClasses:
        myOpacity = myClass['opacity']
        myMax = myClass['max']
        myMin = myClass['min']
        myColour = myClass['colour']
        myLabel = myClass['label']
        myColour = QtGui.QColor(myColour)
        mySymbol = QgsSymbolV2.defaultSymbol(myGeometryType)
        myColourString = "%s, %s, %s" % (
                         myColour.red(),
                         myColour.green(),
                         myColour.blue())
        # Work around for the fact that QgsSimpleMarkerSymbolLayerV2
        # python bindings are missing from the QGIS api.
        # .. see:: http://hub.qgis.org/issues/4848
        # We need to create a custom symbol layer as
        # the border colour of a symbol can not be set otherwise
        myRegistry = QgsSymbolLayerV2Registry.instance()
        if myGeometryType == QGis.Point:
            myMetadata = myRegistry.symbolLayerMetadata("SimpleMarker")
            # note that you can get a list of available layer properties
            # that you can set by doing e.g.
            # QgsSimpleMarkerSymbolLayerV2.properties()
            mySymbolLayer = myMetadata.createSymbolLayer({"color_border":
                                                          myColourString})
            mySymbol.changeSymbolLayer(0, mySymbolLayer)
        elif myGeometryType == QGis.Polygon:
            myMetadata = myRegistry.symbolLayerMetadata("SimpleFill")
            mySymbolLayer = myMetadata.createSymbolLayer({"color_border":
                                                          myColourString})
            mySymbol.changeSymbolLayer(0, mySymbolLayer)
        else:
            # for lines we do nothing special as the property setting
            # below should give us what we require.
            pass

        mySymbol.setColor(myColour)
        mySymbol.setAlpha(myOpacity)
        myRange = QgsRendererRangeV2(myMin,
                                     myMax,
                                     mySymbol,
                                     myLabel)
        myRangeList.append(myRange)

    myRenderer = QgsGraduatedSymbolRendererV2('', myRangeList)
    myRenderer.setMode(QgsGraduatedSymbolRendererV2.EqualInterval)
    myRenderer.setClassAttribute(myTargetField)
    qgisVectorLayer.setRendererV2(myRenderer)
    qgisVectorLayer.saveDefaultStyle()


def setRasterStyle(theQgsRasterLayer, theStyle):
    """Set QGIS raster style based on RIAB style dictionary

    Input
        theQgsRasterLayer: Qgis layer
        style: Dictionary of the form as in the example below
        style_classes = [dict(colour='#ffffff', quantity=-9999, opacity=0),
                         dict(colour='#38A800', quantity=2, opacity=0),
                         dict(colour='#38A800', quantity=5, opacity=1),
                         dict(colour='#79C900', quantity=10, opacity=1),
                         dict(colour='#CEED00', quantity=20, opacity=1),
                         dict(colour='#FFCC00', quantity=50, opacity=1),
                         dict(colour='#FF6600', quantity=100, opacity=1),
                         dict(colour='#FF0000', quantity=200, opacity=1),
                         dict(colour='#7A0000', quantity=300, opacity=1)]

    Output
        Sets and saves style for theQgsRasterLayer

    """
    theQgsRasterLayer.setDrawingStyle(QgsRasterLayer.PalettedColor)
    myClasses = theStyle['style_classes']
    myRangeList = []
    for myClass in myClasses:
        myMax = myClass['quantity']
        myColour = QtGui.QColor(myClass['colour'])
        #myColour = myClass['opacity']  # ?
        #myLabel = myClass['label']
        myShader = QgsColorRampShader.ColorRampItem(myMax, myColour)
        myRangeList.append(myShader)

    # Apply the shading algorithm and design their ramp
    theQgsRasterLayer.setColorShadingAlgorithm(QgsRasterLayer.ColorRampShader)
    myFunction = theQgsRasterLayer.rasterShader().rasterShaderFunction()
    myFunction.setColorRampType(QgsColorRampShader.DISCRETE)
    myFunction.setColorRampItemList(myRangeList)


class RiabDock(QtGui.QDockWidget, Ui_RiabDock):
    """Dock implementation class for the Risk In A Box plugin."""

    def __init__(self, iface, guiContext=True):
        """Constructor for the dialog.

        This dialog will allow the user to select layers and scenario details
        and subsequently run their model.

        .. note:: We use the multiple inheritance approach from Qt4 so that
            for elements are directly accessible in the form context and we can
            use autoconnect to set up slots. See article below:
            http://doc.qt.nokia.com/4.7-snapshot/designer-using-a-ui-file.html


        Args:

           * iface - a Quantum GIS QGisAppInterface instance.
           * guiContext - an optional paramter, defaults to True. Set to
             False if you do not wish to see popup messages etc. Used
             mainly by init tests.

        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """
        QtGui.QDockWidget.__init__(self, None)
        self.setupUi(self)
        # Save reference to the QGIS interface
        self.iface = iface
        self.header = None  # for storing html header template
        self.footer = None  # for storing html footer template
        self.suppressDialogsFlag = guiContext
        self.calculator = ImpactCalculator()
        self.runner = None
        self.helpDialog = None
        self.getLayers()
        self.setOkButtonStatus()

        myButton = self.pbnHelp
        QtCore.QObject.connect(myButton, QtCore.SIGNAL('clicked()'),
                               self.showHelp)
        #self.showHelp()
        myButton = self.pbnRunStop
        QtCore.QObject.connect(myButton, QtCore.SIGNAL('clicked()'),
                               self.accept)
        QtCore.QObject.connect(self.iface.mapCanvas(),
                               QtCore.SIGNAL('layersChanged()'),
                               self.getLayers)
        #myAttribute = QtWebKit.QWebSettings.DeveloperExtrasEnabled
        #QtWebKit.QWebSettings.setAttribute(myAttribute, True)

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

               flag,msg = self.validate()

        Raises:
           no exceptions explicitly raised
        """
        myHazardIndex = self.cboHazard.currentIndex()
        myExposureIndex = self.cboExposure.currentIndex()
        if myHazardIndex == -1 or myExposureIndex == -1:
            myMessage = (
            '<span class="label notice">Getting started:'
            '</span> To use this tool you need to add some layers to your '
            'QGIS project. Ensure that at least one <em>hazard</em> layer '
            '(e.g. earthquake MMI) and one <em>exposure</em> layer (e.g. '
            'dwellings) re available. When you are ready, click the <em>'
            'run</em> button below.')
            return (False, myMessage)

        if self.cboFunction.currentIndex() == -1:
            myHazardFunction = str(self.getHazardLayer().source())
            myHazardKeywords = self.calculator.getKeywordFromFile(
                                                            myHazardFunction)
            myExposureFunction = str(self.getExposureLayer().source())
            myExposureKeywords = self.calculator.getKeywordFromFile(
                                                            myExposureFunction)
            myMessage = ('<span class="label important">No valid functions:'
                         '</span> No functions are available for the inputs '
                         'you have specified. '
                         'Try selecting a different combination of inputs. '
                         'Please consult the user manual <FIXME: add link> '
                         'for details on what constitute valid inputs for '
                         'a given risk function. <br>'
                         'Hazard keywords [%s]: %s <br>'
                         'Exposure keywords [%s]: %s' % (
                                myHazardFunction, myHazardKeywords,
                                myExposureFunction, myExposureKeywords))
            return (False, myMessage)
        else:
            myMessage = ('<span class="label success">Ready:</span> '
            'You can now proceed to run your model by clicking the <em> '
            'Run</em> button.')
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
        # Add any other logic you mught like here...
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
        self.cboHazard.clear()
        self.cboExposure.clear()
        for i in range(len(self.iface.mapCanvas().layers())):

            myLayer = self.iface.mapCanvas().layer(i)
            """
            .. todo:: check raster is single band
            store uuid in user property of list widget for layers
            """

            myName = myLayer.name()
            mySource = str(myLayer.id())
            # find out if the layer is a hazard or an exposure
            # layer by querying its keywords. If the query fails,
            # the layer will be ignored.
            try:
                myCategory = self.calculator.getKeywordFromFile(
                                str(myLayer.source()), 'category')
            except:
                # continue ignoring this layer
                continue
            # See if there is a title for this layer, if not,
            # fallback to the layer's filename
            myTitle = None
            try:
                myTitle = self.calculator.getKeywordFromFile(
                            str(myLayer.source()), 'title')
            except:
                myTitle = myName

            if myCategory == 'hazard':
                self.cboHazard.addItem(myTitle, mySource)
            elif myCategory == 'exposure':
                self.cboExposure.addItem(myTitle, mySource)

        # Now populate the functions list based on the layers loaded
        self.getFunctions()
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
        myHazardKeywords = self.calculator.getKeywordFromFile(
                                            str(myHazardFile))
        # We need to add the layer type to the returned keywords
        if myHazardLayer.type() == QgsMapLayer.VectorLayer:
            myHazardKeywords['layertype'] = 'vector'
        elif myHazardLayer.type() == QgsMapLayer.RasterLayer:
            myHazardKeywords['layertype'] = 'raster'

        myExposureKeywords = self.calculator.getKeywordFromFile(
                                            str(myExposureFile))
        # We need to add the layer type to the returned keywords
        if myExposureLayer.type() == QgsMapLayer.VectorLayer:
            myExposureKeywords['layertype'] = 'vector'
        elif myExposureLayer.type() == QgsMapLayer.RasterLayer:
            myExposureKeywords['layertype'] = 'raster'

        # Find out which functions can be used with these layers
        myList = [myHazardKeywords, myExposureKeywords]
        try:
            myDict = self.calculator.availableFunctions(myList)
            # Populate the hazard combo with the available functions
            for myFunction in myDict:  # Use only key
                self.cboFunction.addItem(myFunction)
        except Exception, e:
            raise e

    def readImpactLayer(self, engineImpactLayer):
        """Helper function to read and validate layer

        Args
            engineImpactLayer: Layer object as provided by the riab engine

        Returns
            validated qgis layer or None

        Raises
            Exception if layer is not valid
        """

        msg = ('Input argument must be a RIAB spatial object. '
               'I got %s' % type(engineImpactLayer))
        if not hasattr(engineImpactLayer, 'is_riab_spatial_object'):
            raise Exception(msg)
        if not engineImpactLayer.is_riab_spatial_object:
            raise Exception(msg)

        # Get associated filename and symbolic name
        myFilename = engineImpactLayer.get_filename()
        myName = engineImpactLayer.get_name()

        # Read layer
        if engineImpactLayer.is_vector:
            qgisLayer = QgsVectorLayer(myFilename, myName, 'ogr')
        elif engineImpactLayer.is_raster:
            qgisLayer = QgsRasterLayer(myFilename, myName)

        # Verify that new qgis layer is valid
        if qgisLayer.isValid():
            return qgisLayer
        else:
            msg = 'Loaded impact layer "%s" is not valid' % myFilename
            raise Exception(msg)

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

    def accept(self):
        """Execute analysis when ok button is clicked."""
        #.. todo:: FIXME (Tim) We may have to implement some polling logic
        # because the putton click accept() function and the updating
        # of the web view after model completion are asynchronous.
        self.showBusy()
        myFlag, myMessage = self.validate()
        if not myFlag:
            self.displayHtml(myMessage)
            self.hideBusy()
            return

        myHazardFilename = None
        myExposureFilename = None
        try:
            myHazardFilename, myExposureFilename = self.optimalClip()
        except Exception, e:
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            msg = ('<p><span class="label important">Error:</span> '
                   'An exception occurred when creating layer '
                   'subsets clipped to the optimal extent: %s</p>' %
                   ((str(e))))
            msg += getExceptionWithStacktrace(e, html=True)
            self.displayHtml(msg)
            return

        self.calculator.setHazardLayer(myHazardFilename)
        self.calculator.setExposureLayer(myExposureFilename)
        self.calculator.setFunction(self.cboFunction.currentText())

        # Start it in its own thread
        self.runner = self.calculator.getRunner()
        QtCore.QObject.connect(self.runner.notifier(),
                               QtCore.SIGNAL('done()'),
                               self.completed)
        #self.runner.start()  # Run in different thread
        try:
            QtGui.qApp.setOverrideCursor(
                    QtGui.QCursor(QtCore.Qt.WaitCursor))
            self.repaint()
            QtGui.qApp.processEvents()
            self.runner.run()  # Run in same thread
            #self.runner.start() # Run in separate thread
            QtGui.qApp.restoreOverrideCursor()
            # .. todo :: Disconnect done slot/signal
        except Exception, e:
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            msg = 'An exception occurred when starting the model: %s' % (
                    (str(e)))
            self.displayHtml(msg)

    def completed(self):
        """Slot activated when the process is done."""

        # Try to run completion code
        try:
            myReport = self._completed()
        except Exception, e:
            # Display message and traceback
            msg = getExceptionWithStacktrace(e, html=True)
            self.displayHtml(msg)
        else:
            # On succes, display generated report
            self.displayHtml(myReport)

        # Hide hourglass
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

        myMessage = self.runner.result()
        engineImpactLayer = self.runner.impactLayer()

        if engineImpactLayer is None:
            msg = ('No impact layer was calculated. '
                   'Error message: %s\n' % str(myMessage))
            raise Exception(msg)

        # Get tabular information from impact layer
        myReport = self.calculator.getKeywordFromLayer(engineImpactLayer,
                                               'caption')

        # Get requested style for impact layer of either kind
        myStyle = engineImpactLayer.get_style_info()

        # Load impact layer into QGIS
        qgisImpactLayer = self.readImpactLayer(engineImpactLayer)

        # Determine styling for QGIS layer
        if engineImpactLayer.is_vector:
            if not myStyle:
                # Set default style if possible
                pass
            else:
                setVectorStyle(qgisImpactLayer, myStyle)
        elif engineImpactLayer.is_raster:
            if not myStyle:
                qgisImpactLayer.setDrawingStyle(
                                QgsRasterLayer.SingleBandPseudoColor)
                qgisImpactLayer.setColorShadingAlgorithm(
                                QgsRasterLayer.PseudoColorShader)
            else:
                setRasterStyle(qgisImpactLayer, myStyle)

        else:
            msg = ('Impact layer %s was neither a raster or a '
                   'vector layer' % qgisImpactLayer.source())
            raise Exception(msg)

        # Finally, add layer to QGIS
        QgsMapLayerRegistry.instance().addMapLayer(qgisImpactLayer)

        # Return text to display in report pane
        return myReport

    def showHelp(self):
        """Load the help text into the wvResults widget"""
        if not self.helpDialog:
            self.helpDialog = RiabHelp(self.iface.mainWindow())
        self.helpDialog.show()

    def showBusy(self):
        """A helper function to indicate the plugin is processing."""
        #self.pbnRunStop.setText('Cancel')
        self.pbnRunStop.setEnabled(False)
        myHtml = ('<div><span class="label success">'
                   'Analyzing this question...</span></div>'
                   '<div><img src="qrc:/plugins/riab/ajax-loader.gif" />'
                   '</div>')
        self.displayHtml(myHtml)
        self.repaint()
        QtGui.qApp.processEvents()
        self.grpQuestion.setEnabled(False)

    def hideBusy(self):
        """A helper function to indicate processing is done."""
        #self.pbnRunStop.setText('Run')
        if self.runner:
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
        the three inputs. The riab library will perform various checks
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
            Any exceptions raised by the RIAB library will be propogated.
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
            msg = ('<p>There '
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
            raise Exception(msg)

        # Next work out the ideal spatial resolution for rasters
        # in the analysis. If layers are not native WGS84, we estimate
        # this based on the geographic extents
        # rather than the layers native extents so that we can pass
        # the ideal WGS84 cell size and extents to the layer prep routines
        # and do all preprocessing in a single operation.
        # All this is done in the function getWGS84resolution
        myBufferedGeoExtent = myGeoExtent  # Bbox to use for hazard layer
        myCellSize = None
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
            else:
                # If exposure is vector data grow hazard raster layer to
                # ensure there are enough pixels for points at the edge of
                # the view port to be interpolated correctly. This requires
                # resolution to be available
                assert myExposureLayer.type() == QgsMapLayer.VectorLayer
                myBufferedGeoExtent = getBufferedExtent(myGeoExtent,
                                                        myHazardGeoCellSize)
        else:
            # Hazard layer is vector
            if myExposureLayer.type() == QgsMapLayer.RasterLayer:
                msg = 'Raster exposure with vector hazard not implemented'
                raise Exception(msg)
            else:
                # Both layers are vector
                pass

        # Make sure that we have EPSG:4326 versions of the input layers
        # that are clipped and (in the case of two raster inputs) resampled to
        # the best resolution.
        myClippedHazardPath = clipLayer(myHazardLayer,
                                        myBufferedGeoExtent, myCellSize)
        myClippedExposurePath = clipLayer(myExposureLayer,
                                          myGeoExtent, myCellSize)

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

        #msg = ('Resampled pixels sizes did not match: '
        #       'Exposure pixel size = %.12f, '
        #       'Hazard pixel size = %.12f' % (myExposureUPP, myHazardUPP))
        #assert numpy.allclose(myExposureUPP, myHazardUPP,
        #                      # FIXME (Ole): I would like to make this tighter
        #                      rtol=1.0e-6, atol=1.0e-3), msg

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
            myFile = QtCore.QFile(':/plugins/riab/header.html')
            if not myFile.open(QtCore.QIODevice.ReadOnly):
                return '----'
            myStream = QtCore.QTextStream(myFile)
            self.header = myStream.readAll()
            myFile.close()
        return self.header

    def htmlFooter(self):
        """Get a standard html footer for wrapping content in."""
        if self.footer is None:
            myFile = QtCore.QFile(':/plugins/riab/footer.html')
            if not myFile.open(QtCore.QIODevice.ReadOnly):
                return '----'
            myStream = QtCore.QTextStream(myFile)
            self.footer = myStream.readAll()
            myFile.close()
        return self.footer

    def displayHtml(self, theMessage):
        """Given an html snippet, wrap it in a page header and footer
        and display it in the wvResults widget."""
        self.wvResults.setHtml(self.htmlHeader() + theMessage +
                                  self.htmlFooter())
