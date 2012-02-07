"""
Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import sys
import os

# Add parent directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)


from PyQt4 import QtGui, QtCore
from PyQt4.QtTest import QTest
from qgis.core import (QgsVectorLayer,
                       QgsRasterLayer,
                       QgsMapLayerRegistry,
                       QgsRectangle,
                       QgsCoordinateReferenceSystem)
from qgis.gui import QgsMapCanvas, QgsMapCanvasLayer
from qgisinterface import QgisInterface
from utilities_test import getQgisTestApp
from gui.riabdock import RiabDock
from storage.utilities import read_keywords

# Get QGis app handle
QGISAPP = getQgisTestApp()

# Set form to test against
parent = QtGui.QWidget()
canvas = QgsMapCanvas(parent)
canvas.resize(QtCore.QSize(400, 400))
# QgisInterface is a stub implementation of the QGIS plugin interface
iface = QgisInterface(canvas)
myGuiContextFlag = False
form = RiabDock(iface, myGuiContextFlag)
GEOCRS = 4326  # constant for EPSG:GEOCRS Geographic CRS id
GOOGLECRS = 900913  # constant for EPSG:GOOGLECRS Google Mercator id


def getUiState(ui):
    """Get state of the 3 combos on the form ui
    """

    myHazard = str(ui.cboHazard.currentText())
    myExposure = str(ui.cboExposure.currentText())
    myImpactFunction = str(ui.cboFunction.currentText())

    myRunButton = ui.pbnRunStop.isEnabled()

    return {'Hazard': myHazard,
            'Exposure': myExposure,
            'Impact Function': myImpactFunction,
            'Run Button Enabled': myRunButton}


def clearForm():
    """Helper function to  set all form elements to default state"""
    form.cboHazard.clear()
    form.cboExposure.clear()


def populateForm():
    """A helper function to populate the form and set it to a valid state.
    """
    loadStandardLayers()
    form.cboHazard.setCurrentIndex(0)
    form.cboExposure.setCurrentIndex(0)
    #QTest.mouseClick(myHazardItem, Qt.LeftButton)
    #QTest.mouseClick(myExposureItem, Qt.LeftButton)


def loadStandardLayers():
    """Helper function to load standard layers into the dialog."""
    # List all layers in the correct order.
    # NOTE: New layers *must* be added to the end of this list, otherwise
    #       tests will break.
    myFileList = ['Padang_WGS84.shp',
                  'glp10ag.asc',
                  'Shakemap_Padang_2009.asc',
                  'tsunami_max_inundation_depth_BB_utm.asc',
                  'tsunami_exposure_BB.shp',
                  'Flood_Current_Depth_Jakarta_geographic.asc',
                  'Population_Jakarta_geographic.asc',
                  'eq_yogya_2006.asc',
                  'OSM_building_polygons_20110905.shp']
    myHazardLayerCount, myExposureLayerCount = loadLayers(myFileList)
    return myHazardLayerCount, myExposureLayerCount


def loadLayers(theLayerList, theClearFlag=True):
    """Helper function to load layers as defined in a python list."""
    # First unload any layers that may already be loaded
    if theClearFlag:
        for myLayer in QgsMapLayerRegistry.instance().mapLayers():
            QgsMapLayerRegistry.instance().removeMapLayer(myLayer)

    # FIXME (Ole): Use environment variable
    myRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    myData = os.path.join(myRoot, 'riab_test_data')

    # Now go ahead and load our layers
    myExposureLayerCount = 0
    myHazardLayerCount = 0
    myCanvasLayers = []
    # Now create our new layers
    for myFile in theLayerList:
        # Extract basename and absolute path
        myBaseName, myExt = os.path.splitext(myFile)
        myPath = os.path.join(myData, myFile)
        myKeywordPath = myPath[:-4] + '.keywords'

        # Determine if layer is hazard or exposure
        myKeywords = read_keywords(myKeywordPath)
        msg = 'Could not read %s' % myKeywordPath
        assert myKeywords is not None, msg
        if myKeywords['category'] == 'hazard':
            myHazardLayerCount += 1
        elif myKeywords['category'] == 'exposure':
            myExposureLayerCount += 1

        # Create QGis Layer Instance
        if myExt in ['.asc', '.tif']:
            myLayer = QgsRasterLayer(myPath, myBaseName)
        elif myExt in ['.shp']:
            myLayer = QgsVectorLayer(myPath, myBaseName, 'ogr')
        else:
            myMessage = 'File %s had illegal extension' % myPath
            raise Exception(myMessage)

        myMessage = 'Layer "%s" is not valid' % str(myLayer.source())
        assert myLayer.isValid(), myMessage

        # Add layer to the registry (that QGis knows about)
        QgsMapLayerRegistry.instance().addMapLayer(myLayer)

        # Create Map Canvas Layer Instance and add to list
        myCanvasLayers.append(QgsMapCanvasLayer(myLayer))

    # Quickly add any existing canvas layers to our list first
    for myLayer in canvas.layers():
        myCanvasLayers.append(QgsMapCanvasLayer(myLayer))
    # now load all these layers in the canvas
    canvas.setLayerSet(myCanvasLayers)
    form.getLayers()

    # Add MCL's to the canvas
    return myHazardLayerCount, myExposureLayerCount


def setCanvasCrs(theEpsgId, theOtfpFlag=False):
    """Helper to set the crs for the canvas before a test is run.

    Args:

        * theEpsgId  - Valid EPSG identifier (int)
        * theOtfpFlag - whether on the fly projections should be enabled
                        on the canvas. Default to False.
    """
        # Enable on-the-fly reprojection
    canvas.mapRenderer().setProjectionsEnabled(theOtfpFlag)

    # Create CRS Instance
    myCrs = QgsCoordinateReferenceSystem()
    myCrs.createFromId(theEpsgId, QgsCoordinateReferenceSystem.EpsgCrsId)

    # Reproject all layers to WGS84 geographic CRS
    canvas.mapRenderer().setDestinationCrs(myCrs)


def setPadangGeoExtent():
    """Zoom to an area known to be occupied by both both Padang layers"""
    myRect = QgsRectangle(100.21, -1.05, 100.63, -0.84)
    canvas.setExtent(myRect)


def setJakartaGeoExtent():
    """Zoom to an area know to be occupied by both Jakarta layers in Geo"""
    myRect = QgsRectangle(106.52, -6.38, 107.14, -6.07)
    canvas.setExtent(myRect)


def setJakartaGoogleExtent():
    """Zoom to an area know to be occupied by both Jakarta layers in 900913 crs
    """
    myRect = QgsRectangle(11873524, -695798, 11913804, -675295)
    canvas.setExtent(myRect)


def setBatemansBayGeoExtent():
    """Zoom to an area know to be occupied by both Batemans Bay
     layers in geo crs"""
    myRect = QgsRectangle(150.162, -35.741, 150.207, -35.719)
    canvas.setExtent(myRect)


def setYogyaGeoExtent():
    """Zoom to an area know to be occupied by both Jakarta layers in Geo"""
    myRect = QgsRectangle(110.348, -7.732, 110.368, -7.716)
    canvas.setExtent(myRect)


class RiabDockTest(unittest.TestCase):
    """Test the risk in a box GUI"""

    def test_defaults(self):
        """Test the GUI in its default state"""
        clearForm()
        self.assertEqual(form.cboHazard.currentIndex(), -1)
        self.assertEqual(form.cboExposure.currentIndex(), -1)
        self.assertEqual(form.cboFunction.currentIndex(), -1)

    def test_validate(self):
        """Validate function work as expected"""

        # First check that we DONT validate a clear form
        clearForm()
        myFlag, myMessage = form.validate()
        assert myMessage is not None, 'No reason for failure given'

        myMessage = 'Validation expected to fail on a cleared form.'
        self.assertEquals(myFlag, False, myMessage)

        # Now check we DO validate a populated form
        populateForm()
        myFlag = form.validate()
        myMessage = ('Validation expected to pass on' +
                     ' a populated for with selections.')
        assert(myFlag), myMessage

    def test_setOkButtonStatus(self):
        """OK button changes properly according to form validity"""

        # First check that we ok ISNT enabled on a clear form
        clearForm()
        myFlag, myMessage = form.validate()

        assert myMessage is not None, 'No reason for failure given'
        myMessage = 'Validation expected to fail on a cleared form.'
        self.assertEquals(myFlag, False, myMessage)

        # Now check OK IS enabled on a populated form
        populateForm()
        myFlag = form.validate()
        myMessage = ('Validation expected to pass on a ' +
                     'populated form with selections.')
        assert(myFlag), myMessage

    def test_runEarthQuakeGuidelinesFunction(self):
        """GUI runs with Shakemap 2009 and Padang Buildings"""

        # Push OK with the left mouse button
        clearForm()
        loadStandardLayers()
        myButton = form.pbnRunStop
        setCanvasCrs(GEOCRS, True)
        setPadangGeoExtent()
        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        myDict = getUiState(form)

        myMessage = 'Got unexpected state: %s' % str(myDict)
        assert myDict == {'Hazard': 'Shakemap_Padang_2009',
                     'Exposure': 'Padang_WGS84',
                     'Impact Function': 'Earthquake Guidelines Function',
                     'Run Button Enabled': True}, myMessage

        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = form.wvResults.page().currentFrame().toPlainText()
        # Expected output:
        #Buildings    Total
        #All:    3160
        #Low damage (10-25%):    0
        #Medium damage (25-50%):    0
        #Pre merge of clip on steroids branch:
        #High damage (50-100%):    3160
        # Post merge of clip on steoids branch:
        #High damage (50-100%):    2993
        myMessage = ('Unexpected result returned for Earthquake guidelines'
               'function. Expected:\n "All" count of 2993, '
               'received: \n %s' % myResult)
        assert '2993' in myResult, myMessage

    def test_runEarthquakeFatalityFunction(self):
        """Earthquake fatality function runs in GUI with Shakemap 2009"""
        """Raster on analysis runs as expected"""

        # Push OK with the left mouse button
        clearForm()
        loadStandardLayers()
        myButton = form.pbnRunStop
        setCanvasCrs(GEOCRS, True)
        setPadangGeoExtent()

        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        # now let's simulate a choosing another combo item and running
        # the model again...
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Enter)
        myDict = getUiState(form)

        myMessage = 'Got unexpected state: %s' % str(myDict)
        assert myDict == {'Hazard': 'Shakemap_Padang_2009',
                     'Exposure': 'Population Density Estimate (5kmx5km)',
                     'Impact Function': 'Earthquake Fatality Function',
                     'Run Button Enabled': True}, myMessage

        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)

        myResult = form.wvResults.page().currentFrame().toPlainText()
        # Expected output:
        # Pre clip refactor:
        # Jumlah Penduduk:    20771496
        # Perkiraan Orang Meninggal:    2687
        # Post Clip Refactor:
        # Jumlah Penduduk:    21189932
        # Perkiraan Orang Meninggal:    2903

        myMessage = ('Unexpected result returned for Earthquake Fatality '
               'Function Expected:\n "Jumlah Penduduk" count of 21189932 '
               ', received: \n %s' % myResult)
        # Pre clip refactor
        #assert '20771496' in myResult, myMessage
        assert '21189932' in myResult, myMessage

    def test_runTsunamiBuildingImpactFunction(self):
        """Tsunami function runs in GUI with Batemans Bay model"""
        """Raster and vector based function runs as expected."""

        # Push OK with the left mouse button
        clearForm()
        loadStandardLayers()
        myButton = form.pbnRunStop

        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        # Hazard layers
        QTest.keyClick(form.cboHazard, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboHazard, QtCore.Qt.Key_Enter)

        # Exposure layers
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Enter)

        # Check that layers and impact function are correct
        myDict = getUiState(form)

        myMessage = 'Got unexpected state: %s' % str(myDict)
        assert myDict == {'Run Button Enabled': True,
                     'Impact Function': 'Tsunami Building Impact Function',
                     'Hazard': 'tsunami_max_inundation_depth_BB_utm',
                     'Exposure': 'tsunami_exposure_BB'}, myMessage

        setCanvasCrs(GEOCRS, True)
        setBatemansBayGeoExtent()

        # Press RUN
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = form.wvResults.page().currentFrame().toPlainText()

        #print myResult
        # Post clip on steroids refactor
        # < 1 m:    1923
        # 1 - 3 m:    89
        # > 3 m:    0
        myMessage = 'Result not as expected: %s' % myResult
        assert '1923' in myResult, myMessage
        assert '89' in myResult, myMessage
        assert '0' in myResult, myMessage

    def test_runFloodPopulationImpactFunction(self):
        """Flood function runs in GUI with Jakarta data
           Raster on raster based function runs as expected."""

        # Push OK with the left mouse button
        clearForm()
        loadStandardLayers()
        myButton = form.pbnRunStop

        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        # Hazard layers
        QTest.keyClick(form.cboHazard, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboHazard, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboHazard, QtCore.Qt.Key_Enter)

        # Exposure layers
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Enter)

        # Choose impact function (second item in the list)
        QTest.keyClick(form.cboFunction, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboFunction, QtCore.Qt.Key_Enter)

        # Check that layers and impact function are correct
        myDict = getUiState(form)

        myMessage = 'Got unexpected state: %s' % str(myDict)
        assert myDict == {'Run Button Enabled': True,
                     'Impact Function': 'Terdampak',
                     'Hazard': 'Banjir Jakarta seperti 2007',
                     'Exposure': 'Penduduk Jakarta'}, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()

        # Press RUN
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = form.wvResults.page().currentFrame().toPlainText()

        #Apabila terjadi "Flood Depth (current) Jakarta"
        # perkiraan dampak terhadap "clip_CCaFFQ" kemungkinan yang terjadi:
        #Terdampak (x 1000):    1

        # Pre clipping fix scores:

        #Catatan:
        #- Jumlah penduduk Jakarta 2 <-- should be about 8000
        #- Jumlah dalam ribuan
        #- Penduduk dianggap terdampak ketika banjir
        #lebih dari 0.1 m.  <-- expecting around 2400
        #Terdampak (x 1000): 2479

        # Post clipping fix scores

        #Catatan:
        #- Jumlah penduduk Jakarta 356018
        #- Jumlah dalam ribuan
        #- Penduduk dianggap terdampak ketika banjir lebih dari 0.1 m.
        #print myResult

        msg = 'Result not as expected: %s' % myResult
        assert '356018' in myResult, msg
        assert '2479' in myResult, msg  # These are expected impact number

    def test_runFloodPopulationImpactFunction_scaling(self):
        """Flood function runs in GUI with 5x5km population data
           Raster on raster based function runs as expected with scaling."""

        # Push OK with the left mouse button
        clearForm()
        loadStandardLayers()
        myButton = form.pbnRunStop

        msg = 'Run button was not enabled'
        assert myButton.isEnabled(), msg

        # Hazard layers
        QTest.keyClick(form.cboHazard, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboHazard, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboHazard, QtCore.Qt.Key_Enter)

        # Exposure layers
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Down)
        #QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Down)
        #QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Enter)

        # Choose impact function (second item in the list)
        QTest.keyClick(form.cboFunction, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboFunction, QtCore.Qt.Key_Enter)

        # Check that layers and impact function are correct
        myDict = getUiState(form)

        msg = 'Got unexpected state: %s' % str(myDict)
        assert myDict == {'Run Button Enabled': True,
                     'Impact Function': 'Terdampak',
                     'Hazard': 'Banjir Jakarta seperti 2007',
                     'Exposure': 'Population Density Estimate (5kmx5km)'}, msg

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()

        # Press RUN
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = form.wvResults.page().currentFrame().toPlainText()

        msg = 'Result not as expected: %s' % myResult

        # FIXME (Adjust these numbers - they don't need to be exact)
        assert '356018' in myResult, msg
        assert '2479' in myResult, msg  # These are expected impact number

    def test_Issue47(self):
        """Issue47: Problem when hazard & exposure data are in different
        proj to viewport.
        See https://github.com/AIFDR/risk_in_a_box/issues/47"""

        clearForm()
        loadStandardLayers()
        myButton = form.pbnRunStop

        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        # Hazard layers
        QTest.keyClick(form.cboHazard, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboHazard, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboHazard, QtCore.Qt.Key_Enter)

        # Exposure layers
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Enter)

        # Choose impact function (second item in the list)
        QTest.keyClick(form.cboFunction, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboFunction, QtCore.Qt.Key_Enter)

        # Check that layers and impact function are correct
        myDict = getUiState(form)

        myMessage = 'Got unexpected state: %s' % str(myDict)
        assert myDict == {'Run Button Enabled': True,
                     'Impact Function': 'Terdampak',
                     'Hazard': 'Banjir Jakarta seperti 2007',
                     'Exposure': 'Penduduk Jakarta'}, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GOOGLECRS, True)
        setJakartaGoogleExtent()

        # Press RUN
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = form.wvResults.page().currentFrame().toPlainText()

        myMessage = 'Result not as expected: %s' % myResult
        #Terdampak (x 1000):    2366
        assert '2366' in myResult, myMessage

    def test_issue45(self):
        """Points near the edge of a raster hazard layer are interpolated OK"""

        clearForm()
        loadStandardLayers()
        myButton = form.pbnRunStop
        setCanvasCrs(GEOCRS, True)
        setYogyaGeoExtent()

        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        # Hazard layers
        QTest.keyClick(form.cboHazard, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboHazard, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboHazard, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboHazard, QtCore.Qt.Key_Enter)

        # Exposure layers
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Enter)

        # Choose impact function
        QTest.keyClick(form.cboFunction, QtCore.Qt.Key_Enter)

        # Check that layers and impact function are correct
        myDict = getUiState(form)
        myMessage = 'Got unexpected state: %s' % str(myDict)
        assert myDict == {'Hazard': 'Yogya2006',
                          'Exposure': 'OSM_building_polygons_20110905',
                          'Impact Function': 'Earthquake Guidelines Function',
                          'Run Button Enabled': True}, myMessage

        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = form.wvResults.page().currentFrame().toPlainText()

        # Check that none of these  get a NaN value:
        assert 'Unknown' in myResult

        myMessage = ('Some buildings returned by Earthquake guidelines '
                     'function '
                     'had NaN values. Result: \n %s' % myResult)
        assert 'Unknown (NaN):	196' not in myResult, myMessage

        # FIXME (Ole): A more robust test would be to load the
        #              result layer and check that all buildings
        #              have values.
        #              Tim, how do we get the output filename?

    def test_loadLayers(self):
        """Layers can be loaded and list widget was updated appropriately
        """

        clearForm()
        myHazardLayerCount, myExposureLayerCount = loadStandardLayers()
        myMessage = 'Expect %s layer(s) in hazard list widget but got %s' \
                     % (myHazardLayerCount, form.cboHazard.count())
        self.assertEqual(form.cboHazard.count(),
                         myHazardLayerCount), myMessage

        myMessage = 'Expect %s layer(s) in exposure list widget but got %s' \
              % (myExposureLayerCount, form.cboExposure.count())
        self.assertEqual(form.cboExposure.count(),
                         myExposureLayerCount), myMessage

    def test_Issue71(self):
        """Test issue #71 in githib - cbo changes should update ok button."""
        # See https://github.com/AIFDR/risk_in_a_box/issues/71
        # Push OK with the left mouse button
        clearForm()
        myButton = form.pbnRunStop
        # First part of scenario should have enabled run
        myFileList = ['Flood_Current_Depth_Jakarta_geographic.asc',
                      'Population_Jakarta_geographic.asc']
        myHazardLayerCount, myExposureLayerCount = loadLayers(myFileList)

        myMessage = ("Incorrect number of Hazard layers: expected 1 got %s"
                     % myHazardLayerCount)
        assert myHazardLayerCount == 1, myMessage

        myMessage = ("Incorrect number of Exposure layers: expected 1 got %s"
                     % myExposureLayerCount)
        assert myExposureLayerCount == 1, myMessage
        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage
        # Second part of scenario - run disables when adding invalid layer
        # and select it - run should be disabled
        myFileList = ['issue71.tif']  # this layer has incorrect keywords
        myClearFlag = False
        myHazardLayerCount, myExposureLayerCount = (
            loadLayers(myFileList, myClearFlag))
        myDict = getUiState(form)
        myMessage = ('Run button was not disabled when exposure set to \n%s'
                    '\nUI State: \n%s') % (form.cboExposure.currentText(),
                    myDict)
        assert myButton.isEnabled() == False, myMessage
        # Now select again a valid layer and the run button
        # should be enabled
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Down)
        QTest.keyClick(form.cboExposure, QtCore.Qt.Key_Enter)
        myMessage = 'Run button was not ensabled when exposure set to \n%s' % \
            form.cboExposure.currentText()
        assert myButton.isEnabled(), myMessage


if __name__ == '__main__':
    suite = unittest.makeSuite(RiabDockTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
