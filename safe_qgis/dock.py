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
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import numpy
import logging
import uuid

from functools import partial

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSlot

from qgis.core import (QgsMapLayer,
                       QgsVectorLayer,
                       QgsRasterLayer,
                       QgsGeometry,
                       QgsMapLayerRegistry,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsFeature,
                       QgsRectangle,
                       QgsPoint,
                       QgsField)
from qgis.analysis import QgsZonalStatistics

from safe_qgis.dock_base import Ui_DockBase
from safe_qgis.help import Help
from safe_qgis.utilities import (getExceptionWithStacktrace,
                                 getWGS84resolution,
                                 isLayerPolygonal,
                                 getLayerAttributeNames,
                                 setVectorStyle,
                                 htmlHeader,
                                 htmlFooter,
                                 setRasterStyle,
                                 qgisVersion,
                                 getDefaults,
                                 impactLayerAttribution)

from safe_qgis.impact_calculator import ImpactCalculator
from safe_qgis.safe_interface import (availableFunctions,
                                      getFunctionTitle,
                                      getOptimalExtent,
                                      getBufferedExtent,
                                      getSafeImpactFunctions,
                                      safeTr,
                                      get_version,
                                      temp_dir,
                                      ReadLayerError)
from safe_qgis.keyword_io import KeywordIO
from safe_qgis.clipper import clipLayer
from safe_qgis.exceptions import (KeywordNotFoundException,
                                  InsufficientOverlapException,
                                  InvalidParameterException,
                                  InsufficientParametersException,
                                  HashNotFoundException,
                                  CallGDALError,
                                  NoFeaturesInExtentException,
                                  InvalidProjectionException)

from safe_qgis.map import Map
from safe_qgis.html_renderer import HtmlRenderer
from safe_qgis.function_options_dialog import (
   FunctionOptionsDialog)
from safe_qgis.keywords_dialog import KeywordsDialog

from safe.postprocessors import get_post_processors

# Don't remove this even if it is flagged as unused by your ide
# it is needed for qrc:/ url resolution. See Qt Resources docs.
import safe_qgis.resources  # pylint: disable=W0611

LOGGER = logging.getLogger('InaSAFE')


class Dock(QtGui.QDockWidget, Ui_DockBase):
    """Dock implementation class for the inaSAFE plugin."""

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

        QtGui.QDockWidget.__init__(self, None)
        self.setupUi(self)
        myLongVersion = get_version()
        LOGGER.debug('Version: %s' % myLongVersion)
        myTokens = myLongVersion.split('.')
        myVersion = '%s.%s.%s' % (myTokens[0], myTokens[1], myTokens[2])
        try:
            myVersionType = myTokens[3].split('2')[0]
        except IndexError:
            myVersionType = 'final'
        # Allowed version names: ('alpha', 'beta', 'rc', 'final')
        self.setWindowTitle(self.tr('InaSAFE %1 %2').arg(
            myVersion, myVersionType))
        # Save reference to the QGIS interface
        self.iface = iface
        self.header = None  # for storing html header template
        self.footer = None  # for storing html footer template
        self.calculator = ImpactCalculator()
        self.keywordIO = KeywordIO()
        self.runner = None
        self.helpDialog = None
        self.state = None
        self.lastUsedFunction = ''
        self.runInThreadFlag = False
        self.showOnlyVisibleLayersFlag = True
        self.setLayerNameFromTitleFlag = True
        self.zoomToImpactFlag = True
        self.hideExposureFlag = True
        self.hazardLayers = None  # array of all hazard layers
        self.exposureLayers = None  # array of all exposure layers
        self.readSettings()  # getLayers called by this
        self.setOkButtonStatus()
        self._aggregationPrefix = 'aggr_'
        self.pbnPrint.setEnabled(False)
        # used by configurable function options button
        self.activeFunction = None

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
            None
        """

        mySettings = QtCore.QSettings()
        myFlag = mySettings.value('inasafe/useThreadingFlag',
                                  False).toBool()
        self.runInThreadFlag = myFlag

        myFlag = mySettings.value(
                        'inasafe/visibleLayersOnlyFlag', True).toBool()
        self.showOnlyVisibleLayersFlag = myFlag

        myFlag = mySettings.value(
                        'inasafe/setLayerNameFromTitleFlag', True).toBool()
        self.setLayerNameFromTitleFlag = myFlag

        myFlag = mySettings.value(
                            'inasafe/setZoomToImpactFlag', True).toBool()
        self.zoomToImpactFlag = myFlag
        # whether exposure layer should be hidden after model completes
        myFlag = mySettings.value(
                            'inasafe/setHideExposureFlag', False).toBool()
        self.hideExposureFlag = myFlag

        # whether to clip hazard and exposure layers to the viewport
        myFlag = mySettings.value(
                            'inasafe/clipToViewport', True).toBool()
        self.clipToViewport = myFlag

        # whether to show or not postprocessing generated layers
        myFlag = mySettings.value(
                            'inasafe/showPostProcLayers', False).toBool()
        self.showPostProcLayers = myFlag

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
            None

        """
        if qgisVersion() >= 10800:  # 1.8 or newer
            QgsMapLayerRegistry.instance().layersWillBeRemoved.connect(
                                                self.layersWillBeRemoved)
            QgsMapLayerRegistry.instance().layersAdded.connect(
                                                 self.layersAdded)
        # All versions of QGIS
        QtCore.QObject.connect(self.iface.mapCanvas(),
                               QtCore.SIGNAL('layersChanged()'),
                               self.getLayers)

    # pylint: disable=W0702
    def disconnectLayerListener(self):
        """Destroy the signal/slot to listen for changes in the layers loaded
        in QGIS.

        ..seealso:: connectLayerListener

        Args:
            None

        Returns:
            None

        Raises:
            None

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
            QgsMapLayerRegistry.instance().layersWillBeRemoved.disconnect(
                                                self.layersWillBeRemoved)
            QgsMapLayerRegistry.instance().layersAdded.disconnect(
                                                 self.layersAdded)
        except:
            pass

        try:
            QtCore.QObject.disconnect(self.iface.mapCanvas(),
                               QtCore.SIGNAL('layersChanged()'),
                               self.getLayers)
        except:
            pass
    # pylint: enable=W0702

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
            myMessage = '<table class="condensed">'
            myNotes = self.tr(
            'To use this tool you need to add some layers to your '
            'QGIS project. Ensure that at least one <em>hazard</em> layer '
            '(e.g. earthquake MMI) and one <em>exposure</em> layer (e.g. '
            'dwellings) re available. When you are ready, click the <em>'
            'run</em> button below.')
            myMessage += ('<tr><th class="info button-cell">'
                  + self.tr('Getting started:') + '</th></tr>\n'
                  '<tr><td>' + myNotes + '</td></tr>\n')
            myMessage += '</table>'
            return (False, myMessage)

        if self.cboFunction.currentIndex() == -1:
            #myHazardFilename = self.getHazardLayer().source()
            myHazardKeywords = QtCore.QString(str(self.keywordIO.readKeywords(
                                                    self.getHazardLayer())))
            #myExposureFilename = self.getExposureLayer().source()
            myExposureKeywords = QtCore.QString(
                                            str(self.keywordIO.readKeywords(
                                                self.getExposureLayer())))
            # TODO refactor impact_functions so it is accessible and user here
            myMessage = '<table class="condensed">'
            myNotes = self.tr('No functions are available for the inputs '
                         'you have specified. '
                         'Try selecting a different combination of inputs. '
                         'Please consult the user manual <FIXME: add link> '
                         'for details on what constitute valid inputs for '
                         'a given risk function.')
            myMessage += ('<tr><th class="warning button-cell">'
                  + self.tr('No valid functions:') + '</th></tr>\n'
                  '<tr><td>' + myNotes + '</td></tr>\n')
            myMessage += ('<tr><th class="info button-cell">'
                  + self.tr('Hazard keywords:') + '</th></tr>\n'
                  '<tr><td>' + myHazardKeywords + '</td></tr>\n')
            myMessage += ('<tr><th class="info button-cell">'
                  + self.tr('Exposure keywords:') + '</th></tr>\n'
                  '<tr><td>' + myExposureKeywords + '</td></tr>\n')
            myMessage += '</table>'
            return (False, myMessage)
        else:
            # TODO refactor impact_functions so it is accessible and user here
            myMessage = '<table class="condensed">'
            myNotes = self.tr('You can now proceed to run your model by'
                                ' clicking the <em>Run</em> button.')
            myMessage += ('<tr><th class="info button-cell">'
                  + self.tr('Ready') + '</th></tr>\n'
                  '<tr><td>' + myNotes + '</td></tr>\n')
            myMessage += '</table>'
            return (True, myMessage)

    def on_cboHazard_currentIndexChanged(self, theIndex):
        """Automatic slot executed when the Hazard combo is changed
        so that we can see if the ok button should be enabled.

        .. note:: Don't use the @pyqtSlot() decorator for autoslots!

        Args:
            None.

        Returns:
            None.

        Raises:
            No exceptions explicitly raised.

        """
        # Add any other logic you might like here...
        del theIndex
        self.getFunctions()
        self._toggleCboAggregation()
        self.setOkButtonStatus()

    def on_cboExposure_currentIndexChanged(self, theIndex):
        """Automatic slot executed when the Exposure combo is changed
        so that we can see if the ok button should be enabled.

        .. note:: Don't use the @pyqtSlot() decorator for autoslots!

        Args:
           None.

        Returns:
           None.

        Raises:
           No exceptions explicitly raised.

        """
        # Add any other logic you mught like here...
        del theIndex
        self.getFunctions()
        self._toggleCboAggregation()
        self.setOkButtonStatus()

    @pyqtSlot(QtCore.QString)
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
        if not theIndex.isNull or not theIndex == '':
            myFunctionID = self.getFunctionID()

            myFunctions = getSafeImpactFunctions(myFunctionID)
            self.activeFunction = myFunctions[0][myFunctionID]
            self.functionParams = None
            if hasattr(self.activeFunction, 'parameters'):
                self.functionParams = self.activeFunction.parameters
            self.setToolFunctionOptionsButton()
        else:
            del theIndex
        self._toggleCboAggregation()
        self.setOkButtonStatus()

    def _toggleCboAggregation(self):
        """Helper function to toggle the aggregation combo depending on the
        current dock status

        Args:
           None.
        Returns:
           None
        Raises:
           no
        """
        #FIXME (MB) remove hazardlayer and exposure layer type check when
        # vector aggregation is supported
        selectedHazardLayer = self.getHazardLayer()
        selectedExposureLayer = self.getExposureLayer()

        #more than 1 because No aggregation is always there
        if (self.cboAggregation.count() > 1 and
            selectedHazardLayer is not None and
            selectedExposureLayer is not None and
            selectedHazardLayer.type() == QgsMapLayer.RasterLayer and
            selectedExposureLayer.type() == QgsMapLayer.RasterLayer):
            self.cboAggregation.setEnabled(True)
        else:
            self.cboAggregation.setCurrentIndex(0)
            self.cboAggregation.setEnabled(False)

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

    def setToolFunctionOptionsButton(self):
        """Helper function to set the tool function button
        status if there is function parameters to configure
        then enable it, otherwise disable it.

        Args:
           None.
        Returns:
           None.
        Raises:
           no exceptions explicitly raised."""
        # Check if functionParams intialized
        if self.functionParams is None:
            self.toolFunctionOptions.setEnabled(False)
        else:
            self.toolFunctionOptions.setEnabled(True)

    @pyqtSlot()
    def on_toolFunctionOptions_clicked(self):
        """Automatic slot executed when the tool button for configuring
        impact functions is clicked (when available) to open the dialog

        Args:
           None.

        Returns:
           None.

        Raises:
           no exceptions explicitly raised."""
        myDialog = FunctionOptionsDialog(self)
        myDialog.setDialogInfo(self.getFunctionID())
        myDialog.buildForm(self.activeFunction, self.functionParams)
        myDialog.showNormal()

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

    @pyqtSlot()
    def layersWillBeRemoved(self):
        """Slot for the new (QGIS 1.8 and beyond api) to notify us when
        a group of layers is are removed. This is optimal since if many layers
        are removed this slot gets called only once. This slot simply
        delegates to getLayers and is only implemented here to make the
        connections between the different signals and slots clearer and
        better documented."""
        self.getLayers()

    @pyqtSlot()
    def layersAdded(self, theLayers=None):
        """Slot for the new (QGIS 1.8 and beyond api) to notify us when
        a group of layers is are added. This is optimal since if many layers
        are added this slot gets called only once. This slot simply
        delegates to getLayers and is only implemented here to make the
        connections between the different signals and slots clearer and
        better documented."""
        del theLayers
        self.getLayers()

    @pyqtSlot()
    def layerWillBeRemoved(self):
        """Slot for the old (pre QGIS 1.8 api) to notify us when
        a layer is removed. This is suboptimal since if many layers are
        removed this slot gets called multiple times. This slot simply
        delegates to getLayers and is only implemented here to make the
        connections between the different signals and slots clearer and
        better documented."""
        self.getLayers()

    @pyqtSlot()
    def layerWasAdded(self):
        """Slot for the old (pre QGIS 1.8 api) to notify us when
        a layer is added. This is suboptimal since if many layers are
        added this slot gets called multiple times. This slot simply
        delegates to getLayers and is only implemented here to make the
        connections between the different signals and slots clearer and
        better documented."""
        self.getLayers()

    def getLayers(self):
        """Helper function to obtain a list of layers currently loaded in QGIS.

        On invocation, this method will populate cboHazard,
        cboExposure and cboAggregate on the dialog with a list of available
        layers.
        Only **singleband raster** layers will be added to the hazard layer
        list,only **point vector** layers will be added to the exposure layer
        list and Only **polygon vector** layers will be added to the aggregate
        list

        Args:
           None.
        Returns:
           None
        Raises:
           no
        """
        self.disconnectLayerListener()
        self.blockSignals(True)
        self.saveState()
        self.cboHazard.clear()
        self.cboExposure.clear()
        self.cboAggregation.clear()
        self.hazardLayers = []
        self.exposureLayers = []
        self.aggregationLayers = []
        # Map registry may be invalid if QGIS is shutting down
        myRegistry = None
        # pylint: disable=W0702
        try:
            myRegistry = QgsMapLayerRegistry.instance()
        except:
            return
        # pylint: enable=W0702

        myCanvasLayers = self.iface.mapCanvas().layers()

        # MapLayers returns a QMap<QString id, QgsMapLayer layer>
        myLayers = myRegistry.mapLayers().values()
        for myLayer in myLayers:
            if (self.showOnlyVisibleLayersFlag and
                myLayer not in myCanvasLayers):
                continue

         # .. todo:: check raster is single band
         #    store uuid in user property of list widget for layers

            myName = myLayer.name()
            mySource = str(myLayer.id())
            # See if there is a title for this layer, if not,
            # fallback to the layer's filename

            try:
                myTitle = self.keywordIO.readKeywords(myLayer, 'title')
            except:  # pylint: disable=W0702
                myTitle = myName
            else:
                # Lookup internationalised title if available
                myTitle = safeTr(myTitle)
            # Register title with layer
            if myTitle and self.setLayerNameFromTitleFlag:
                myLayer.setLayerName(myTitle)

            #check if layer is a vector polygon layer
            layer = myRegistry.mapLayer(mySource)
            if isLayerPolygonal(layer):
                self.addComboItemInOrder(self.cboAggregation, myTitle,
                    mySource)
                self.aggregationLayers.append(myLayer)

            # Find out if the layer is a hazard or an exposure
            # layer by querying its keywords. If the query fails,
            # the layer will be ignored.
            try:
                myCategory = self.keywordIO.readKeywords(myLayer, 'category')
            except:  # pylint: disable=W0702
                # continue ignoring this layer
                continue

            if myCategory == 'hazard':
                self.addComboItemInOrder(self.cboHazard, myTitle, mySource)
                self.hazardLayers.append(myLayer)
            elif myCategory == 'exposure':
                self.addComboItemInOrder(self.cboExposure, myTitle, mySource)
                self.exposureLayers.append(myLayer)

        #handle the cboAggregation combo
        self.cboAggregation.insertItem(0, self.tr('Entire area'))
        self.cboAggregation.setCurrentIndex(0)
        self._toggleCboAggregation()

        # Now populate the functions list based on the layers loaded
        self.getFunctions()
        self.restoreState()
        self.setOkButtonStatus()
        # Note: Don't change the order of the next two lines otherwise there
        # will be a lot of unneeded looping around as the signal is handled
        self.connectLayerListener()
        self.blockSignals(False)
        self.getPostprocLayer()
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
        myExposureLayer = self.getExposureLayer()
        if myExposureLayer is None:
            return
        myHazardKeywords = self.keywordIO.readKeywords(myHazardLayer)
        # We need to add the layer type to the returned keywords
        if myHazardLayer.type() == QgsMapLayer.VectorLayer:
            myHazardKeywords['layertype'] = 'vector'
        elif myHazardLayer.type() == QgsMapLayer.RasterLayer:
            myHazardKeywords['layertype'] = 'raster'

        myExposureKeywords = self.keywordIO.readKeywords(myExposureLayer)
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
            for myFunctionID in myDict:
                myFunction = myDict[myFunctionID]
                myFunctionTitle = getFunctionTitle(myFunction)

                # KEEPING THESE STATEMENTS FOR DEBUGGING UNTIL SETTLED
                #print
                #print 'myFunction (ID)', myFunctionID
                #print 'myFunction', myFunction
                #print 'Function title:', myFunctionTitle

                # Provide function title and ID to function combo:
                # myFunctionTitle is the text displayed in the combo
                # myFunctionID is the canonical identifier
                self.addComboItemInOrder(self.cboFunction,
                                         myFunctionTitle,
                                         theItemData=myFunctionID)
        except Exception, e:
            raise e

        self.restoreFunctionState(myOriginalFunction)

    def readImpactLayer(self, myEngineImpactLayer):
        """Helper function to read and validate layer.

        Args
            myEngineImpactLayer: Layer object as provided by the inasafe engine

        Returns
            validated qgis layer or None

        Raises
            Exception if layer is not valid
        """

        myMessage = self.tr('Input argument must be a InaSAFE spatial object. '
               'I got %1').arg(str(type(myEngineImpactLayer)))
        if not hasattr(myEngineImpactLayer, 'is_inasafe_spatial_object'):
            raise Exception(myMessage)
        if not myEngineImpactLayer.is_inasafe_spatial_object:
            raise Exception(myMessage)

        # Get associated filename and symbolic name
        myFilename = myEngineImpactLayer.get_filename()
        myName = myEngineImpactLayer.get_name()

        myQgisLayer = None
        # Read layer
        if myEngineImpactLayer.is_vector:
            myQgisLayer = QgsVectorLayer(myFilename, myName, 'ogr')
        elif myEngineImpactLayer.is_raster:
            myQgisLayer = QgsRasterLayer(myFilename, myName)

        # Verify that new qgis layer is valid
        if myQgisLayer.isValid():
            return myQgisLayer
        else:
            myMessage = self.tr('Loaded impact layer "%1" is not'
                                ' valid').arg(myFilename)
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

    def getPostprocLayer(self):
        """Obtain the name of the path to the aggregation file from the
        userrole of the QtCombo for aggregation.

        Args: None

        Returns:
            - None if no aggregation is selected or cboAggregation is
        disabled
            - else a polygon layer
        """

        myNoSelectionValue = 0
        myIndex = self.cboAggregation.currentIndex()
        if myIndex <= myNoSelectionValue:
            return None
        myLayerId = self.cboAggregation.itemData(myIndex,
            QtCore.Qt.UserRole).toString()
        myLayer = QgsMapLayerRegistry.instance().mapLayer(myLayerId)
        return myLayer

    def getAggregationFieldNameCount(self):
        return self._aggregationPrefix + 'count'

    def getAggregationFieldNameMean(self):
        return self._aggregationPrefix + 'mean'

    def getAggregationFieldNameSum(self):
        return self._aggregationPrefix + 'sum'

    def setupCalculator(self):
        """Initialise the ImpactCalculator based on the current
        state of the ui.

        Args: None

        Returns: None

        Raises: Propagates any error from :func:optimalClip()
        """
        try:
            myHazardFilename, myExposureFilename = self.optimalClip()
        except CallGDALError, e:
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            raise e
        except IOError, e:
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            raise e
        except:
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            raise

        # Identify input layers
        self.calculator.setHazardLayer(myHazardFilename)
        self.calculator.setExposureLayer(myExposureFilename)

        # Use canonical function name to identify selected function
        myFunctionID = self.getFunctionID()
        self.calculator.setFunction(myFunctionID)

    def accept(self):
        """Execute analysis when ok button is clicked."""
        #.. todo:: FIXME (Tim) We may have to implement some polling logic
        # because the button click accept() function and the updating
        # of the web view after model completion are asynchronous (when
        # threading mode is enabled especially)

        self.showBusy()
        myFlag, myMessage = self.validate()
        if not myFlag:
            self.displayHtml(myMessage)
            self.hideBusy()
            return

        self.postprocLayer = self.getPostprocLayer()
        try:
            myOrigKeywords = self.keywordIO.readKeywords(self.postprocLayer)
        except AttributeError:
            myOrigKeywords = {}
        except InvalidParameterException:
            #no kw file has ben found for postprocLayer. create an empty one
            myOrigKeywords = {}
            self.keywordIO.writeKeywords(self.postprocLayer, myOrigKeywords)

        #check and generate keywords for the aggregation layer
        self.defaults = getDefaults()
        LOGGER.debug('my pre dialog keywords' + str(myOrigKeywords))
        self.initPostproc()

        self.doZonalAggregation = True
        if self.postprocLayer is None:
            # generate on the fly a memory layer to be used in postprocessing
            # this is needed because we always want a vectoril layer to store
            # information
            self.doZonalAggregation = False
            myGeoCrs = QgsCoordinateReferenceSystem()
            myGeoCrs.createFromEpsg(4326)
            crs = myGeoCrs.authid().toLower()
            myUUID = str(uuid.uuid4())
            uri = 'Polygon?crs=%s&index=yes&uuid=%s' % (crs, myUUID)
            myName = 'tmpPostprocessingLayer'
            myLayer = QgsVectorLayer(uri, myName, 'memory')
            LOGGER.debug('created' + myLayer.name())

            if not myLayer.isValid():
                myMessage = self.tr('An exception occurred when creating the '
                                    'Entire area layer.')
                self.displayHtml(myMessage)
                return
            myProvider = myLayer.dataProvider()
            myLayer.startEditing()
            myAttrName = self.tr('Area')
            myProvider.addAttributes([QgsField(myAttrName,
                QtCore.QVariant.String)])
            myLayer.commitChanges()

            self.postprocLayer = myLayer
            self.keywordIO.appendKeywords(self.postprocLayer, {self.defaults[
                                                'AGGR_ATTR_KEY']: myAttrName})

        LOGGER.debug('Do zonal aggregation: ' + str(self.doZonalAggregation))

        self.runtimeKWDialog = KeywordsDialog(
            self.iface.mainWindow(),
            self.iface,
            self,
            self.postprocLayer)

        QtCore.QObject.connect(self.runtimeKWDialog,
            QtCore.SIGNAL('accepted()'),
            self.run)

        QtCore.QObject.connect(self.runtimeKWDialog,
            QtCore.SIGNAL('rejected()'),
            partial(self.acceptCancelled, myOrigKeywords))
        # go check if our postprocessing layer has any keywords set and if not
        # prompt for them. if a prompt is shown myContinue will be false
        # and the run method is called by the accepted signal
        myContinue = self._checkPostprocAttributes()
        if myContinue:
            self.run()

    def acceptCancelled(self, theOldKeywords):
        LOGGER.debug('Setting old dictionary: ' + str(theOldKeywords))
        self.keywordIO.writeKeywords(self.postprocLayer, theOldKeywords)
        self.hideBusy()
        self.setOkButtonStatus()

    def run(self):
        """Execute analysis when ok button on settings is clicked."""

        self.enableBusyCursor()

        # Attributes that will not be deleted from the postprocessing layer
        # attribute table
        self.postprocAttributes = {}

        self.postprocAttributes[self.defaults['AGGR_ATTR_KEY']] = (
            self.keywordIO.readKeywords(self.postprocLayer,
                                        self.defaults['AGGR_ATTR_KEY']))

        myDefaultFemRatioKey = self.defaults['FEM_RATIO_ATTR_KEY']
        myFemRatioAttr = self.keywordIO.readKeywords(self.postprocLayer,
                                                     myDefaultFemRatioKey)
        if (myFemRatioAttr != self.tr('Don\'t use') and
            myFemRatioAttr != self.tr('Use default')):
            self.postprocAttributes[myDefaultFemRatioKey] = myFemRatioAttr

        # Start the analysis
        try:
            self.setupCalculator()
        except CallGDALError, e:
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            myMessage = self.tr('An error occurred when call GDAL command')
            myMessage = getExceptionWithStacktrace(e,
                                                   html=True,
                                                   context=myMessage)
            self.displayHtml(myMessage)
            return
        except IOError, e:
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            myMessage = self.tr('An error occurred when write clip file')
            myMessage = getExceptionWithStacktrace(e,
                                                   html=True,
                                                   context=myMessage)
            self.displayHtml(myMessage)
            return
        except InsufficientOverlapException, e:
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            myMessage = self.tr('An exception occurred when setting up the '
                                'impact calculator.')
            myMessage = getExceptionWithStacktrace(e,
                                                   html=True,
                                                   context=myMessage)
            self.displayHtml(myMessage)
            return
        except NoFeaturesInExtentException, e:
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            myMessage = self.tr('An error occurred because there are no '
                                'features visible in the current view. Try '
                                'zooming out or panning until some features '
                                'become visible.')
            myMessage = getExceptionWithStacktrace(e,
                                                   html=True,
                                                   context=myMessage)
            self.displayHtml(myMessage)
            return
        except InvalidProjectionException, e:
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            myMessage = self.tr('An error occurred because you are using a '
                                'layer containing density data (e.g. '
                                'population density) which will not scale '
                                'accurately if we re-project it from its '
                                'native coordinate reference system to'
                                'WGS84/GeoGraphic.')
            myMessage = getExceptionWithStacktrace(e,
                                                   html=True,
                                                   context=myMessage)
            self.displayHtml(myMessage)
            return

        try:
            self.runner = self.calculator.getRunner()
        except InsufficientParametersException, e:
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            myContext = self.tr('An exception occurred when setting up the '
                                ' model runner.')
            myMessage = getExceptionWithStacktrace(e, html=True,
                                                   context=myContext)
            self.displayHtml(myMessage)
            return

        QtCore.QObject.connect(self.runner,
                               QtCore.SIGNAL('done()'),
                               self.postprocess)
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

        try:
            self.showBusy(myTitle, myMessage, myProgress)
            if self.runInThreadFlag:
                self.runner.start()  # Run in different thread
            else:
                self.runner.run()  # Run in same thread
            QtGui.qApp.restoreOverrideCursor()
            # .. todo :: Disconnect done slot/signal
        except Exception, e:  # pylint: disable=W0703

            # FIXME (Ole): This branch is not covered by the tests
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            myContext = self.tr('An exception occurred when starting'
                                ' the model.')
            myMessage = getExceptionWithStacktrace(e, html=True,
                                                   context=myContext)
            self.displayHtml(myMessage)

    def postprocess(self):
        """
        Called on self.runner SIGNAL('done()') starts all postprocessing steps
        Args: None

        Returns: None
        """

        if self.runner.impactLayer() is None:
            # Done was emitted, but no impact layer was calculated
            myResult = self.runner.result()
            myMessage = str(self.tr('No impact layer was calculated. '
                                    'Error message: %s\n' % str(myResult)))
            myException = self.runner.lastException()
            if myException is not None:
                myContext = self.tr('An exception occurred when calculating '
                                    'the results')
                myMessage = getExceptionWithStacktrace(myException,
                    html=True,
                    context=myContext)
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            self.displayHtml(myMessage)
            return

        try:
            self._aggregateResults()
            if self.aggregationErrorSkipPostprocessing is None:
                self._startPostprocessors()
            QtGui.qApp.restoreOverrideCursor()
        except Exception, e:  # pylint: disable=W0703
            QtGui.qApp.restoreOverrideCursor()
            self.hideBusy()
            myContext = self.tr(
                'An exception occurred when postprocessing the results')
            myMessage = getExceptionWithStacktrace(e, html=True,
                context=myContext)
            self.displayHtml(myMessage)
            return
        self.completed()

    def initPostproc(self):
        """
        initializes and clears self.postprocOutput. needs to run at the
         end of postprocess

        Returns: None
        """

        self.postprocOutput = {}
        self.aggregationErrorSkipPostprocessing = None
        try:
            if (self.postprocLayer is not None and
                self.lastUsedFunction != self.getFunctionID()):
                # remove category keyword so we force the keyword editor to
                # popup. see the beginning of _checkPostprocAttributes to see
                # how the popup decision is made
                self.keywordIO.deleteKeyword(self.postprocLayer, 'category')
        except AttributeError:
            #first run, self.lastUsedFunction does not exist yet
            pass

    def getPostprocOutput(self, asOneBigTable=False):
        """
        gets the of the postprocOutput

        Args: None

        Returns: a string containing the html in the requested format
        """

        LOGGER.debug(self.postprocOutput)
        if self.aggregationErrorSkipPostprocessing is not None:
            myHTML = ('<table class="table table-striped condensed">'
            '    <tr>'
            '       <td>'
            '         <strong>'
            + self.tr('Postprocessing report skipped') +
            '         </strong>'
            '       </td>'
            '    </tr>'
            '    <tr>'
            '       <td>'
            + self.tr('Due to a problem while processing the results,'
                      ' the detailed postprocessing report is unavailable:'
                      ' %1').arg(self.aggregationErrorSkipPostprocessing) +
            '       </td>'
            '    </tr>'
            '</table>')
            return myHTML

        if asOneBigTable:
            return self._parsePostProcOutputAsOneBigTables()
        else:
            return self._parsePostProcOutputAsMultipleTables()

    def _parsePostProcOutputAsOneBigTables(self):
        """
        parses the postprocessing output as one table with all postprocessors

        Args: None

        Returns: a string containing the html
        """

        #FIXME, return a parsed HTML
        return str(self.postprocOutput)

    def _parsePostProcOutputAsMultipleTables(self):
        """
        parses the postprocessing output as one table per postprocessor

        Args: None

        Returns: a string containing the html
        """

        myHTML = ''
        for proc, resList in self.postprocOutput.iteritems():
            #sorting using the first indicator of a postprocessor
            myFirstKey = resList[0][1].keyAt(0)
            try:
            # [1]['Total']['value']
            # resList is for example:
            # [
            #    (PyQt4.QtCore.QString(u'Entire area'), OrderedDict([
            #        (u'Total', {'value': 977536, 'metadata': {}}),
            #        (u'Female population', {'value': 508319, 'metadata': {}}),
            #        (u'Weekly hygiene packs', {'value': 403453, 'metadata': {
            #         'description': 'Females hygiene packs for weekly use'}})
            #    ]))
            #]
                myEndOfList = -1
                resList = sorted(
                    resList,
                    key=lambda d: (
                    # return -1 if the postprocessor returns NO_DATA to put at
                    # the end of the list
                    # d[1] is the orderedDict
                    # d[1][myFirstKey] is the 1st indicator in the orderedDict
                        myEndOfList if d[1][myFirstKey]['value'] ==
                                       self.defaults['NO_DATA']
                        else d[1][myFirstKey]['value']),
                    reverse=True)
            except KeyError:
                LOGGER.debug('Skipping sorting as the postprocessor did not '
                             'have a "Total" field')
            myHTML += ('<table class="table table-striped condensed">'
                       '  <tbody>'
                       '    <tr>'
                       '       <td colspan="100%">'
                       '         <strong>'
                       + self.tr('Detailed %1 report').arg(
                                 self.tr(proc)) +
                       '         </strong>'
                       '       </td>'
                       '    </tr>'
                       '    <tr>'
                       '      <th width="25%">'
                       + self.aggrAttrTitle +
                       '      </th>')
            # add th according to the ammount of calculation done by each
            # postprocessor
            for calculationName in resList[0][1]:
                myHTML += ('      <th>'
                                          + self.tr(calculationName) +
                                          '      </th>')
                #close header row
            myHTML += '    </tr>'
            for zoneName, calc in resList:
                myHTML += '    <tr><td>' + zoneName + '</td> '
                for calculationName, calculationData in calc.iteritems():
                    myHTML += ('      <td>'
                                          + str(calculationData['value']) +
                                          '      </td>')
                    #close header row
                myHTML += '    </tr>'

            #close table
            myHTML += ('</tbody></table>')

        return myHTML

    def _aggregateResults(self):
        """
        Performs Aggregation postprocessing step by
         - creating a copy of the dataset clipped by the impactlayer bounding
          box
         - stripping all attributes beside the aggregation attribute
         - delegating to the appropriate aggregator for raster and vectors

        Args: None

        Returns: None
        """
        impactLayer = self.runner.impactLayer()
        impactLayerBB = impactLayer.get_bounding_box()
        #[West, South, East, North]

        myTitle = self.tr('Aggregating results...')
        myMessage = self.tr('This may take a little while - we are '
                            ' aggregating the hazards by %1').arg(
            self.cboAggregation.currentText())
        myProgress = 88
        self.showBusy(myTitle, myMessage, myProgress)

        if not self.doZonalAggregation:
            self.postprocLayer.startEditing()
            myProvider = self.postprocLayer.dataProvider()
            # add a feature the size of the impact layer bounding box
            myFeat = QgsFeature()
            myFeat.setGeometry(QgsGeometry.fromRect(QgsRectangle(
                QgsPoint(impactLayerBB[0], impactLayerBB[1]),
                QgsPoint(impactLayerBB[2], impactLayerBB[3]))))
            myFeat.setAttributeMap({0: QtCore.QVariant(
                self.tr('Entire area'))})
            myProvider.addFeatures([myFeat])
            self.postprocLayer.commitChanges()

        myQgisImpactLayer = self.readImpactLayer(impactLayer)
        if not myQgisImpactLayer.isValid():
            myMessage = self.tr('Error when reading %1').arg(myQgisImpactLayer)
            raise ReadLayerError(myMessage)
        lName = str(self.tr('%1 aggregated to %2')
                .arg(myQgisImpactLayer.name())
                .arg(self.postprocLayer.name()))

        # in case aggregation layer is larger than the impact layer let's
        # trimm it down to  avoid extra calculations
        clippedAggregationLayerPath = clipLayer(
            self.postprocLayer,
            impactLayerBB, explodeMultipart=False)

        self.postprocLayer = QgsVectorLayer(
            clippedAggregationLayerPath, lName, 'ogr')
        if not self.postprocLayer.isValid():
            myMessage = self.tr('Error when reading %1').arg(
                self.postprocLayer.lastError())
            raise ReadLayerError(myMessage)

            #delete unwanted fields
        myProvider = self.postprocLayer.dataProvider()
        myFields = myProvider.fields()
        toDel = []
        for i in myFields:
            if myFields[i].name() not in self.postprocAttributes.values():
                toDel.append(i)
        LOGGER.debug('Removing this attributes: ' + str(toDel))
        try:
            self.postprocLayer.startEditing()
            myProvider.deleteAttributes(toDel)
            self.postprocLayer.commitChanges()
        # FIXME (Ole): Disable pylint check for the moment
        # Need to work out what exceptions we will catch here, though.
        except:  # pylint: disable=W0702
            myMessage = self.tr('Could not remove the unneded fields')
            LOGGER.debug(myMessage)

        del toDel, myProvider, myFields
        self.keywordIO.appendKeywords(self.postprocLayer, {'title': lName})

        #call the correct aggregator
        if myQgisImpactLayer.type() == QgsMapLayer.VectorLayer:
            self._aggregateResultsVector(myQgisImpactLayer)
        elif myQgisImpactLayer.type() == QgsMapLayer.RasterLayer:
            self._aggregateResultsRaster(myQgisImpactLayer)
        else:
            myMessage = self.tr('%1 is %2 but it should be either vector or '
                                'raster').arg(myQgisImpactLayer.name()).arg(
                                myQgisImpactLayer.type())
            raise ReadLayerError(myMessage)

        if self.showPostProcLayers and self.doZonalAggregation:
            myProvider = self.postprocLayer.dataProvider()
            myAttr = self.getAggregationFieldNameSum()
            myAttrIndex = myProvider.fieldNameIndex(myAttr)
            myProvider.select([myAttrIndex], QgsRectangle(), False)
            myFeat = QgsFeature()
            myHighestVal = 0

            while myProvider.nextFeature(myFeat):
                myAttrMap = myFeat.attributeMap()
                myVal, ok = myAttrMap[myAttrIndex].toInt()
                if ok and myVal > myHighestVal:
                    myHighestVal = myVal

            myClasses = []
            myColors = ['#fecc5c', '#fd8d3c', '#f31a1c']
            myStep = int(myHighestVal / len(myColors))
            LOGGER.debug('Max val %s, my step %s' % (myHighestVal, myStep))
            myCounter = 0
            for myColor in myColors:
                myMin = myCounter
                myCounter += myStep
                myMax = myCounter

                myClasses.append(
                    {'min': myMin,
                     'max': myMax,
                     'colour': myColor,
                     'transparency': 30,
                     'label': '%s - %s' % (myMin, myMax)})
                myCounter += 1

            myStyle = {'target_field': myAttr,
                       'style_classes': myClasses}

            setVectorStyle(self.postprocLayer, myStyle)

    def _aggregateResultsVector(self, myQgisImpactLayer):
        """
        Performs Aggregation postprocessing step on vectorial impact layers
        Args:
            * myQgisImpactLayer a valid QgsRasterLayer

        Returns: None
        """
        #TODO implement polygon to polygon aggregation (dissolve,
        # line in polygon, point in polygon)
        try:
            myTargetField = self.keywordIO.readKeywords(myQgisImpactLayer,
                'target_field')
        except KeywordNotFoundException:
            myMessage = self.tr('No "target_field" keyword found in the impact'
                                ' layer %1 keywords. The impact function'
                                ' should define this.').arg(
                                myQgisImpactLayer.name())
            LOGGER.debug('Skipping postprocessing due to: %s' % myMessage)
            self.aggregationErrorSkipPostprocessing = myMessage
            return
        myImpactProvider = myQgisImpactLayer.dataProvider()
        myTargetFieldIndex = myQgisImpactLayer.fieldNameIndex(myTargetField)
        #if a feature has no field called
        if myTargetFieldIndex == -1:
            myMessage = self.tr('No attribute "%1" was found in the attribute '
                                'table for layer "%2". The impact function '
                                'must define this attribute for '
                                'postprocessing to work.').arg(myTargetField,
                                myQgisImpactLayer.name())
            LOGGER.debug('Skipping postprocessing due to: %s' % myMessage)
            self.aggregationErrorSkipPostprocessing = myMessage
            return

        # start data retreival: fetch no geometry and
        # 1 attr for each feature
        myImpactProvider.select([myTargetFieldIndex], QgsRectangle(), False)
        myFeat = QgsFeature()
        myTotal = 0

        if self.doZonalAggregation:
            myMessage = self.tr('Vector aggregation not implemented yet. '
                                'Called on %1').arg(myQgisImpactLayer.name())
            LOGGER.debug('Skipping postprocessing due to: %s' % myMessage)
            self.aggregationErrorSkipPostprocessing = myMessage
            return
        else:
            #loop over all features in impact layer
            while myImpactProvider.nextFeature(myFeat):
                myVal, ok = myFeat.attributeMap()[myTargetFieldIndex].toInt()
                if ok:
                    myTotal += myVal

            #add the total to the postprocLayer
            myPostprocessorProvider = self.postprocLayer.dataProvider()
            self.postprocLayer.startEditing()
            myAggrField = self.getAggregationFieldNameSum()
            myPostprocessorProvider.addAttributes([QgsField(myAggrField,
                QtCore.QVariant.Int)])
            self.postprocLayer.commitChanges()
            myAggrFieldIndex = self.postprocLayer.fieldNameIndex(
                myAggrField)
            attrs = {myAggrFieldIndex: QtCore.QVariant(myTotal)}
            myFID = 0
            self.postprocLayer.startEditing()
            myPostprocessorProvider.changeAttributeValues({myFID: attrs})
            self.postprocLayer.commitChanges()

        return

    def _aggregateResultsRaster(self, myQgisImpactLayer):
        """
        Performs Aggregation postprocessing step on raster impact layers by
        calling QgsZonalStatistics
        Args:
            * myQgisImpactLayer a valid QgsVectorLayer

        Returns: None
        """
        zonStat = QgsZonalStatistics(
            self.postprocLayer,
            myQgisImpactLayer.dataProvider().dataSourceUri(),
            self._aggregationPrefix)
        progressDialog = QtGui.QProgressDialog(
            self.tr('Calculating zonal statistics'),
            self.tr('Abort...'),
            0,
            0)
        zonStat.calculateStatistics(progressDialog)
        if progressDialog.wasCanceled():
            QtGui.QMessageBox.error(self, self.tr('ZonalStats: Error'),
                self.tr(
                    'You aborted aggregation, '
                    'so there are no data for analysis. Exiting...'))

        return

    def _startPostprocessors(self):
        #instantiate postprocessors if they are requested by the function
        try:
            myRequestedPostprocessors = self.functionParams['postprocessors']
            myPostprocessors = get_post_processors(myRequestedPostprocessors)
        except (TypeError, KeyError):
            # TypeError is for when functionParams is none
            # KeyError is for when ['postprocessors'] is unavailable
            myPostprocessors = {}
        LOGGER.debug('Running this postprocessors: ' + str(myPostprocessors))

        myFeatureNameAttribute = self.postprocAttributes[self.defaults[
                                                         'AGGR_ATTR_KEY']]
        if myFeatureNameAttribute is None:
            self.aggrAttrTitle = self.tr('Aggregation unit')
        else:
            self.aggrAttrTitle = myFeatureNameAttribute

        myNameFieldIndex = self.postprocLayer.fieldNameIndex(
            myFeatureNameAttribute)
        mySumFieldIndex = self.postprocLayer.fieldNameIndex(
            self.getAggregationFieldNameSum())

        if 'Gender' in myPostprocessors:
            #look if we need to look for a variable female ratio in a layer
            myFemRatioIsVariable = False
            try:
                myFemRatioField = self.postprocAttributes[self.defaults[
                                                     'FEM_RATIO_ATTR_KEY']]
                myFemRatioFieldIndex = self.postprocLayer.fieldNameIndex(
                    myFemRatioField)
                myFemRatioIsVariable = True

            except KeyError:
                myFemRatio = self.keywordIO.readKeywords(self.postprocLayer,
                    self.defaults['FEM_RATIO_KEY'])

        #iterate zone features
        provider = self.postprocLayer.dataProvider()
        allAttrs = provider.attributeIndexes()
        # start data retreival: fetch no geometry and all attributes for each
        # feature
        provider.select(allAttrs, QgsRectangle(), False)
        feat = QgsFeature()
        while provider.nextFeature(feat):
            #get all attributes of a feature
            attrMap = feat.attributeMap()

            #if a feature has no field called
            if myNameFieldIndex == -1:
                zoneName = str(feat.id())
            else:
                zoneName = attrMap[myNameFieldIndex].toString()

            aggrSum, ok = attrMap[mySumFieldIndex].toDouble()
            LOGGER.debug('Reading: %s %s' % (aggrSum, ok))
            myGeneralParams = {'population_total': aggrSum}

            for n, p in myPostprocessors.iteritems():
                myParams = myGeneralParams
                try:
                    #look if params are available for this postprocessor
                    myParams.update(
                        self.functionParams['postprocessors'][n]['params'])
                except KeyError:
                    pass

                if n == 'Gender':
                    if myFemRatioIsVariable:
                        myFemRatio, success = attrMap[
                                        myFemRatioFieldIndex].toDouble()
                        if not success:
                            myFemRatio = self.defaults['FEM_RATIO']
                        LOGGER.debug(success)
                    myParams['female_ratio'] = myFemRatio

                p.setup(myParams)
                p.process()
                myResults = p.results()
                p.clear()
                LOGGER.debug(myResults)
                try:
                    self.postprocOutput[n].append((zoneName, myResults))
                except KeyError:
                    self.postprocOutput[n] = []
                    self.postprocOutput[n].append((zoneName, myResults))

    def _checkPostprocAttributes(self):
        """checks if the postprocessing layer has all attribute
        keyword. If not it calls _promptPostprocAttributes to prompt for
        inputs

        Args: None

        Returns: None

        Raises: Propogates any error
        """

        try:
            myKeywords = self.keywordIO.readKeywords(self.postprocLayer)
        #discussed with tim,in this case its ok to be generic
        except Exception:  # pylint: disable=W0703
            myKeywords = {}

        #myKeywords are already complete
        if ('category' in myKeywords and
            myKeywords['category'] == 'postprocessing' and
            self.defaults['AGGR_ATTR_KEY'] in myKeywords and
            self.defaults['FEM_RATIO_ATTR_KEY'] in myKeywords and
            (self.defaults['FEM_RATIO_ATTR_KEY'] != self.tr(
                    'Use default') or
             self.defaults['FEM_RATIO_KEY'] in myKeywords)):
            return True
        #some keywords are needed
        else:
            #set the default values by writing to the myKeywords
            myKeywords['category'] = 'postprocessing'

            myAttrs, _ = getLayerAttributeNames(
                self.postprocLayer,
                [QtCore.QVariant.Int, QtCore.QVariant.String])
            if self.defaults['AGGR_ATTR_KEY'] not in myKeywords:
                myKeywords[self.defaults['AGGR_ATTR_KEY']] = myAttrs[0]

            if self.defaults['FEM_RATIO_ATTR_KEY'] not in myKeywords:
                myKeywords[self.defaults['FEM_RATIO_ATTR_KEY']] = self.tr(
                    'Use default')

            if self.defaults['FEM_RATIO_KEY'] not in myKeywords:
                myKeywords[self.defaults['FEM_RATIO_KEY']] = self.defaults[
                                                             'FEM_RATIO']

#            delete = self.keywordIO.deleteKeyword(self.postprocLayer,
#               'subcategory')
#            LOGGER.debug('Deleted: ' + str(delete))
            self.keywordIO.appendKeywords(self.postprocLayer, myKeywords)
            if self.doZonalAggregation:
                #prompt user for a choice
                myTitle = self.tr(
                    'Waiting for attribute selection...')
                myMessage = self.tr('Please select which attribute you want to'
                                    ' use as ID for the aggregated results')
                myProgress = 1
                self.showBusy(myTitle, myMessage, myProgress)

                self.disableBusyCursor()
                self.runtimeKWDialog.setLayer(self.postprocLayer)
                #disable gui elements that should not be applicable for this
                self.runtimeKWDialog.radExposure.setEnabled(False)
                self.runtimeKWDialog.radHazard.setEnabled(False)
                self.runtimeKWDialog.pbnAdvanced.setEnabled(False)
                self.runtimeKWDialog.setModal(True)
                self.runtimeKWDialog.show()

                return False
            else:
                return True

    def completed(self):
        """Slot activated when the process is done."""
        #save the ID of the function that just runned

        self.lastUsedFunction = self.getFunctionID()

        # Try to run completion code
        try:
            myReport = self._completed()
        except Exception, e:  # pylint: disable=W0703

            # FIXME (Ole): This branch is not covered by the tests

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

        # Load impact layer into QGIS
        myQgisImpactLayer = self.readImpactLayer(myEngineImpactLayer)

        myKeywords = self.keywordIO.readKeywords(myQgisImpactLayer)
        #write postprocessing report to keyword
        myKeywords['postprocessing_report'] = self.getPostprocOutput()
        self.keywordIO.writeKeywords(myQgisImpactLayer, myKeywords)

        # Get tabular information from impact layer
        myReport = self.keywordIO.readKeywords(myQgisImpactLayer,
                                               'impact_summary')
        myReport += impactLayerAttribution(myKeywords)

        # Get requested style for impact layer of either kind
        myStyle = myEngineImpactLayer.get_style_info()

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
            myMessage = self.tr('Impact layer %1 was neither a raster or a '
                   'vector layer').arg(myQgisImpactLayer.source())
            raise ReadLayerError(myMessage)

        # Add layers to QGIS
        myLayersToAdd = []
        if self.showPostProcLayers and self.doZonalAggregation:
            myLayersToAdd.append(self.postprocLayer)
        myLayersToAdd.append(myQgisImpactLayer)
        QgsMapLayerRegistry.instance().addMapLayers(myLayersToAdd)
        # then zoom to it
        if self.zoomToImpactFlag:
            self.iface.zoomToActiveLayer()
        if self.hideExposureFlag:
            myExposureLayer = self.getExposureLayer()
            myLegend = self.iface.legendInterface()
            myLegend.setLayerVisible(myExposureLayer, False)
        self.restoreState()

        #append postprocessing report
        myReport += self.getPostprocOutput()

        # Return text to display in report panel
        return myReport

    def showHelp(self):
        """Load the help text into the wvResults widget"""
        if self.helpDialog:
            del self.helpDialog
        self.helpDialog = Help(theParent=self.iface.mainWindow(),
                               theContext='dock')

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
        myHtml = ('<table class="condensed">'
                  '  <tr>'
                  '    <th class="info button-cell">'
                  + str(theTitle) +
                  '    </th>'
                  '  </tr>'
                  '  <tr>'
                  '    <td>'
                  + str(theMessage) +
                  '    </td>'
                  '  </tr>'
                  '  <tr>'
                  '    <td>'
                  '      <div class="progress">'
                  '          <div class="bar" '
                  '               style="width: ' + str(theProgress) + '%;">'
                  '          </div>'
                  '      </div>'
                  '    </td>'
                  '  </tr>'
                  '</table>')
        self.displayHtml(myHtml)
        self.repaint()
        QtGui.qApp.processEvents()
        self.grpQuestion.setEnabled(False)

    def hideBusy(self):
        """A helper function to indicate processing is done."""
        #self.pbnRunStop.setText('Run')
        if self.runner:
            QtCore.QObject.disconnect(self.runner,
                               QtCore.SIGNAL('done()'),
                               self.postprocess)
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
        coordinate reference system.

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
            if self.clipToViewport:
                myGeoExtent = getOptimalExtent(myHazardGeoExtent,
                                               myExposureGeoExtent,
                                               myViewportGeoExtent)
            else:
                myGeoExtent = getOptimalExtent(myHazardGeoExtent,
                    myExposureGeoExtent)

        except InsufficientOverlapException, e:
            # FIXME (MB): This branch is not covered by the tests
            myMessage = self.tr('<p>There '
                   'was insufficient overlap between the input layers '
                   'and / or the layers and the viewable area. Please select '
                   'two overlapping layers and zoom or pan to them or disable'
                   ' viewable area clipping in the options dialog'
                   '. Full details follow:</p>'
                   '<p>Failed to obtain the optimal extent given:</p>'
                   '<p>Hazard: %1</p>'
                   '<p>Exposure: %2</p>'
                   '<p>Viewable area Geo Extent: %3</p>'
                   '<p>Hazard Geo Extent: %4</p>'
                   '<p>Exposure Geo Extent: %5</p>'
                   '<p>Viewable area clipping enabled: %6</p>'
                   '<p>Details: %7</p>').arg(
                        myHazardLayer.source()).arg(
                        myExposureLayer.source()).arg(
                        QtCore.QString(str(myViewportGeoExtent))).arg(
                        QtCore.QString(str(myHazardGeoExtent))).arg(
                        QtCore.QString(str(myExposureGeoExtent))).arg(
                        QtCore.QString(str(self.clipToViewport))).arg(
                        str(e))
            raise InsufficientOverlapException(myMessage)

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
            myHazardGeoCellSize = getWGS84resolution(myHazardLayer)

            if myExposureLayer.type() == QgsMapLayer.RasterLayer:

                # In case of two raster layers establish common resolution
                myExposureGeoCellSize = getWGS84resolution(myExposureLayer)

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

            # FIXME (Ole): Check that it is a polygon layer

            # FIXME (Ole): This should say something like this (issue #285)
            #if myHazardLayer.geometry() == QgsMapLayer.Point:
            #    myGeoExtent = myExposureGeoExtent
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
        try:
            myClippedHazardPath = clipLayer(myHazardLayer, myBufferedGeoExtent,
                                            myCellSize)
        except CallGDALError, e:
            raise e
        except IOError, e:
            raise e

        myTitle = self.tr('Preparing exposure data...')
        myMessage = self.tr('We are resampling and clipping the exposure'
                            'layer to match the intersection of the hazard'
                            'layer and the current view extents.')
        myProgress = 44
        self.showBusy(myTitle, myMessage, myProgress)
        myClippedExposurePath = clipLayer(
            myExposureLayer,
            myGeoExtent, myCellSize,
            theExtraKeywords=extraExposureKeywords)

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
        myReport = ('<table class="table table-striped condensed'
                        ' bordered-table">')  # will be overridden if needed
        if theLayer is not None:
            try:
                myKeywords = self.keywordIO.readKeywords(theLayer)

                if 'impact_summary' in myKeywords:
                    myReport = myKeywords['impact_summary']
                    if 'postprocessing_report' in myKeywords:
                        myReport += myKeywords['postprocessing_report']
                            # append properties of the result layer

                    myReport += impactLayerAttribution(myKeywords)

                    self.pbnPrint.setEnabled(True)

                    # TODO: Shouldn't this line be in the start of the else
                    #     block below? (TS)
                    myReport += ('<table class="table table-striped condensed'
                                 ' bordered-table">')

                else:
                    self.pbnPrint.setEnabled(False)
                    for myKeyword in myKeywords:
                        myValue = myKeywords[myKeyword]

                        # Translate titles explicitly if possible
                        if myKeyword == 'title':
                            myValue = safeTr(myValue)

                        # Add this keyword to report
                        myReport += ('<tr>'
                                     # FIXME (Ole): Not sure if this will work
                                     # with translations
                                       '<th>' + self.tr(myKeyword.capitalize())
                                       + '</th>'
                                     '</tr>'
                                     '<tr>'
                                       '<td>' + str(myValue) + '</td>'
                                     '</tr>')
                    myReport += '</table>'
            except (KeywordNotFoundException, HashNotFoundException,
                    InvalidParameterException), e:
                myContext = self.tr('No keywords have been defined'
                        ' for this layer yet. If you wish to use it as'
                        ' an impact or hazard layer in a scenario, please'
                        ' use the keyword editor. You can open the keyword'
                        ' editor by clicking on the'
                        ' <img src="qrc:/plugins/inasafe/keywords.png" '
                        ' width="16" height="16"> icon'
                        ' in the toolbar, or choosing Plugins -> InaSAFE'
                        ' -> Keyword Editor from the menus.')
                myReport += getExceptionWithStacktrace(e, html=True,
                                                       context=myContext)
            except Exception, e:
                myReport += getExceptionWithStacktrace(e, html=True)
            if myReport is not None:
                self.displayHtml(myReport)

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
                       'aggregation': self.cboAggregation.currentText(),
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
        for myCount in range(0, self.cboAggregation.count()):
            myItemText = self.cboAggregation.itemText(myCount)
            if myItemText == self.state['aggregation']:
                self.cboAggregation.setCurrentIndex(myCount)
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
        myMap = Map(self.iface)
        if self.iface.activeLayer() is None:
            QtGui.QMessageBox.warning(self,
                                self.tr('InaSAFE'),
                                self.tr('Please select a valid impact layer'
                                        ' before trying to print.'))
            return

        self.showBusy(self.tr('Map Creator'),
                      self.tr('Preparing map and report'),
                      theProgress=20)

        myMap.setImpactLayer(self.iface.activeLayer())
        LOGGER.debug('Map Title: %s' % myMap.getMapTitle())
        myMapFilename = QtGui.QFileDialog.getSaveFileName(self,
                            self.tr('Write to PDF'),
                            os.path.join(temp_dir(),
                                         myMap.getMapTitle() + '.pdf'),
                            self.tr('Pdf File (*.pdf)'))
        myMapFilename = str(myMapFilename)

        if myMapFilename is None:
            self.showBusy(self.tr('Map Creator'),
                          self.tr('Printing cancelled!'),
                          theProgress=100)
            self.hideBusy()
            return

        myTableFilename = os.path.splitext(myMapFilename)[0] + '_table.pdf'
        myHtmlRenderer = HtmlRenderer(thePageDpi=myMap.pageDpi)
        myKeywords = self.keywordIO.readKeywords(self.iface.activeLayer())
        myHtmlPdfPath = myHtmlRenderer.printImpactTable(
            myKeywords, theFilename=myTableFilename)

        try:
            myMapPdfPath = myMap.printToPdf(myMapFilename)
        # FIXME (Sunni) : just temporal solution. Needs to create a robust one
        # for print map to pdf, especially for Windows.
        except OSError, e:
            errorContext = ('There is permission issue. Please re-run QGIS as '
                            'administrator. Save your work if needed.')
            myReport = getExceptionWithStacktrace(e, html=True,
                                                  context=errorContext)
            if myReport is not None:
                self.displayHtml(myReport)
            return
        except Exception, e:  # pylint: disable=W0703
            # FIXME (Ole): This branch is not covered by the tests
            myReport = getExceptionWithStacktrace(e, html=True)
            if myReport is not None:
                self.displayHtml(myReport)
            return

        myStatus = self.tr('Your PDF was created....opening using '
                           'the default PDF viewer on your system. '
                           'The generated pdfs were saved as:%1'
                           '%2%1 and %1%3').arg(
                           '<br>').arg(QtCore.QString(
                           myMapPdfPath)).arg(QtCore.QString(
                           myHtmlPdfPath))

        self.showBusy(self.tr('Map Creator'),
                      myStatus,
                      theProgress=80)

        QtGui.QDesktopServices.openUrl(
            QtCore.QUrl('file:///' + myHtmlPdfPath,
            QtCore.QUrl.TolerantMode))
        QtGui.QDesktopServices.openUrl(
            QtCore.QUrl('file:///' + myMapPdfPath,
            QtCore.QUrl.TolerantMode))

        self.showBusy(self.tr('Map Creator'),
                      myStatus,
                      theProgress=100)

        self.hideBusy()
        #myMap.showComposer()

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
            if cmp(str(theItemText).lower(), myItemText.lower()) < 0:
                theCombo.insertItem(myCount, theItemText, theItemData)
                return
        #otherwise just add it to the end
        theCombo.insertItem(mySize, theItemText, theItemData)

    def getFunctionID(self, theIndex=None):
        """Get the canonical impact function ID for the currently selected
           function (or the specified combo entry if theIndex is supplied.
        Args:
            theIndex int - Optional index position in the combo that you
                want the function id for. Defaults to None. If not set / None
                the currently selected combo item's function id will be
                returned.
        Returns:
            myFunctionID str - String that identifies the function
        Raises:
           None
        """
        if theIndex is None:
            myIndex = self.cboFunction.currentIndex()
        else:
            myIndex = theIndex
        myItemData = self.cboFunction.itemData(myIndex, QtCore.Qt.UserRole)
        myFunctionID = str(myItemData.toString())
        return myFunctionID
