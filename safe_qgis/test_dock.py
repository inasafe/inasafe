"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import sys
import os
import logging
from unittest import expectedFailure

from os.path import join
# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

from PyQt4 import QtCore
from PyQt4.QtTest import QTest

from qgis.core import (QgsRasterLayer,
                       QgsVectorLayer,
                       QgsMapLayerRegistry,
                       QgsRectangle)
# TODO: get this via api
from safe.impact_functions.core import format_int
from safe.common.testing import HAZDATA, EXPDATA, TESTDATA, UNITDATA

from safe_qgis.utilities_test import (getQgisTestApp,
                                setCanvasCrs,
                                setPadangGeoExtent,
                                setBatemansBayGeoExtent,
                                setJakartaGeoExtent,
                                setYogyaGeoExtent,
                                setJakartaGoogleExtent,
                                setGeoExtent,
                                GEOCRS,
                                GOOGLECRS,
                                loadLayer)

from safe_qgis.dock import Dock
from safe_qgis.utilities import (setRasterStyle,
                          qgisVersion,
                          getDefaults)


# Retired impact function for characterisation (Ole)
# So ignore unused import errors for these? (Tim)
# pylint: disable=W0611
from safe.engine.impact_functions_for_testing import allen_fatality_model
from safe.engine.impact_functions_for_testing import HKV_flood_study
from safe.engine.impact_functions_for_testing import BNPB_earthquake_guidelines
#from safe.engine.impact_functions_for_testing import error_raising_functions
# pylint: enable=W0611

LOGGER = logging.getLogger('InaSAFE')

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
DOCK = Dock(IFACE)

YOGYA2006_title = 'An earthquake in Yogyakarta like in 2006'
PADANG2009_title = 'An earthquake in Padang like in 2009'

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__),
    'test_data/test_files')


def getUiState(ui):
    """Get state of the 3 combos on the DOCK ui. This method is purely for
    testing and not to be confused with the saveState and restoreState methods
    of inasafedock.
    """

    myHazard = str(ui.cboHazard.currentText())
    myExposure = str(ui.cboExposure.currentText())
    myImpactFunctionTitle = str(ui.cboFunction.currentText())
    myImpactFunctionId = DOCK.getFunctionID()
    myRunButton = ui.pbnRunStop.isEnabled()

    return {'Hazard': myHazard,
            'Exposure': myExposure,
            'Impact Function Title': myImpactFunctionTitle,
            'Impact Function Id': myImpactFunctionId,
            'Run Button Enabled': myRunButton}


def formattedList(theList):
    """Return a string representing a list of layers (in correct order)
    but formatted with line breaks between each entry."""
    myListString = ''
    for myItem in theList:
        myListString += myItem + '\n'
    return myListString


def canvasList():
    """Return a string representing the list of canvas layers (in correct
    order) but formatted with line breaks between each entry."""
    myListString = ''
    for myLayer in CANVAS.layers():
        myListString += str(myLayer.name()) + '\n'
    return myListString


def combosToString(theUi):
    """Helper to return a string showing the state of all combos (all their
    entries"""

    myString = 'Hazard Layers\n'
    myString += '-------------------------\n'
    myCurrentId = theUi.cboHazard.currentIndex()
    for myCount in range(0, theUi.cboHazard.count()):
        myItemText = theUi.cboHazard.itemText(myCount)
        if myCount == myCurrentId:
            myString += '>> '
        else:
            myString += '   '
        myString += str(myItemText) + '\n'
    myString += '\n'
    myString += 'Exposure Layers\n'
    myString += '-------------------------\n'
    myCurrentId = theUi.cboExposure.currentIndex()
    for myCount in range(0, theUi.cboExposure.count()):
        myItemText = theUi.cboExposure.itemText(myCount)
        if myCount == myCurrentId:
            myString += '>> '
        else:
            myString += '   '
        myString += str(myItemText) + '\n'

    myString += '\n'
    myString += 'Functions\n'
    myString += '-------------------------\n'
    myCurrentId = theUi.cboFunction.currentIndex()
    for myCount in range(0, theUi.cboFunction.count()):
        myItemText = theUi.cboFunction.itemText(myCount)
        if myCount == myCurrentId:
            myString += '>> '
        else:
            myString += '   '
        myString += '%s (Function ID: %s)\n' % (
            str(myItemText), DOCK.getFunctionID(myCurrentId))

    myString += '\n'
    myString += 'Aggregation Layers\n'
    myString += '-------------------------\n'
    myCurrentId = theUi.cboAggregation.currentIndex()
    for myCount in range(0, theUi.cboAggregation.count()):
        myItemText = theUi.cboAggregation.itemText(myCount)
        if myCount == myCurrentId:
            myString += '>> '
        else:
            myString += '   '
        myString += str(myItemText) + '\n'

    myString += '\n\n >> means combo item is selected'
    return myString


def setupScenario(theHazard, theExposure, theFunction, theFunctionId,
                  theOkButtonFlag=True, theAggregation=None,
                  theAggregationEnabledFlag=None):
    """Helper function to set the gui state to a given scenario.

    Args:
        theHazard str - (Required) name of the hazard combo entry to set.
        theExposure str - (Required) name of exposure combo entry to set.
        theFunction - (Required) name of the function combo entry to set.
        theFunctionId - (Required) the impact function id that should be used.
        theOkButtonFlag - (Optional) Whether the ok button should be enabled
          after this scenario is set up.
        theAggregationLayer - (Optional) which layer should be used for
        aggregation

    We require both theFunction and theFunctionId because safe allows for
    multiple functions with the same name but different id's so we need to be
    sure we have the right one.

    Returns: bool - Indicating if the setup was successful
            str - A message indicating why it may have failed.

    Raises: None
    """

    if theHazard is not None:
        myIndex = DOCK.cboHazard.findText(theHazard)
        myMessage = ('\nHazard Layer Not Found: %s\n Combo State:\n%s' %
                     (theHazard, combosToString(DOCK)))
        if myIndex == -1:
            return False, myMessage
        DOCK.cboHazard.setCurrentIndex(myIndex)

    if theExposure is not None:
        myIndex = DOCK.cboExposure.findText(theExposure)
        myMessage = ('\nExposure Layer Not Found: %s\n Combo State:\n%s' %
                     (theExposure, combosToString(DOCK)))
        if myIndex == -1:
            return False, myMessage
        DOCK.cboExposure.setCurrentIndex(myIndex)

    if theFunction is not None:
        myIndex = DOCK.cboFunction.findText(theFunction)
        myMessage = ('\nImpact Function Not Found: %s\n Combo State:\n%s' %
                     (theFunction, combosToString(DOCK)))
        if myIndex == -1:
            return False, myMessage
        DOCK.cboFunction.setCurrentIndex(myIndex)

    if theAggregation is not None:
        myIndex = DOCK.cboAggregation.findText(theAggregation)
        myMessage = ('Aggregation layer Not Found: %s\n Combo State:\n%s' %
                     (theAggregation, combosToString(DOCK)))
        if myIndex == -1:
            return False, myMessage
        DOCK.cboAggregation.setCurrentIndex(myIndex)

    if theAggregationEnabledFlag is not None:
        if DOCK.cboAggregation.isEnabled() != theAggregationEnabledFlag:
            myMessage = ('The aggregation combobox should be %s' %
                ('enabled' if theAggregationEnabledFlag else 'disabled'))
            return False, myMessage

    # Check that layers and impact function are correct
    myDict = getUiState(DOCK)

    myExpectedDict = {'Run Button Enabled': theOkButtonFlag,
                      'Impact Function Title': theFunction,
                      'Impact Function Id': theFunctionId,
                      'Hazard': theHazard,
                      'Exposure': theExposure}

    myMessage = 'Expected versus Actual State\n'
    myMessage += '--------------------------------------------------------\n'

    for myKey in myExpectedDict.keys():
        myMessage += 'Expected %s: %s\n' % (myKey, myExpectedDict[myKey])
        myMessage += 'Actual   %s: %s\n' % (myKey, myDict[myKey])
        myMessage += '----\n'
    myMessage += '--------------------------------------------------------\n'
    myMessage += combosToString(DOCK)

    if myDict != myExpectedDict:
        return False, myMessage

    return True, 'Matched ok.'


def populatemyDock():
    """A helper function to populate the DOCK and set it to a valid state.
    """
    loadStandardLayers()
    DOCK.cboHazard.setCurrentIndex(0)
    DOCK.cboExposure.setCurrentIndex(0)
    #QTest.mouseClick(myHazardItem, Qt.LeftButton)
    #QTest.mouseClick(myExposureItem, Qt.LeftButton)


def loadStandardLayers():
    """Helper function to load standard layers into the dialog."""
    # NOTE: Adding new layers here may break existing tests since
    # combos are populated alphabetically. Each test will
    # provide a detailed diagnostic if you break it so make sure
    # to consult that and clean up accordingly.
    #
    # Update on above. We are refactoring tests so they use find on combos
    # to set them appropriately, instead of relative in combo position
    # so you should be able to put datasets in any order below.
    # If chancing the order does cause tests to fail, please update the tests
    # to also use find instead of relative position. (Tim)
    myFileList = [join(TESTDATA, 'Padang_WGS84.shp'),
                  join(EXPDATA, 'glp10ag.asc'),
                  join(HAZDATA, 'Shakemap_Padang_2009.asc'),
                  join(TESTDATA, 'tsunami_max_inundation_depth_utm56s.tif'),
                  join(TESTDATA, 'tsunami_building_exposure.shp'),
                  join(HAZDATA, 'Flood_Current_Depth_Jakarta_geographic.asc'),
                  join(TESTDATA, 'Population_Jakarta_geographic.asc'),
                  join(HAZDATA, 'eq_yogya_2006.asc'),
                  join(HAZDATA, 'Jakarta_RW_2007flood.shp'),
                  join(TESTDATA, 'OSM_building_polygons_20110905.shp'),
                  join(EXPDATA, 'DKI_buildings.shp'),
                  join(HAZDATA, 'jakarta_flood_category_123.asc'),
                  join(TESTDATA, 'roads_Maumere.shp'),
                  join(TESTDATA, 'kabupaten_jakarta_singlepart.shp')]
    myHazardLayerCount, myExposureLayerCount = loadLayers(myFileList,
                                                       theDataDirectory=None)
    #FIXME (MB) -1 is untill we add the aggregation category because of
    # kabupaten_jakarta_singlepart not being either hayard nor exposure layer
    assert myHazardLayerCount + myExposureLayerCount == len(myFileList) - 1

    return myHazardLayerCount, myExposureLayerCount


def loadLayers(theLayerList, theClearFlag=True, theDataDirectory=TESTDATA):
    """Helper function to load layers as defined in a python list."""
    # First unload any layers that may already be loaded
    if theClearFlag:
        QgsMapLayerRegistry.instance().removeAllMapLayers()

    # Now go ahead and load our layers
    myExposureLayerCount = 0
    myHazardLayerCount = 0

    # Now create our new layers
    for myFile in theLayerList:

        myLayer, myType = loadLayer(myFile, theDataDirectory)
        if myType == 'hazard':
            myHazardLayerCount += 1
        elif myType == 'exposure':
            myExposureLayerCount += 1
        # Add layer to the registry (that QGis knows about) a slot
        # in qgis_interface will also ensure it gets added to the canvas
        QgsMapLayerRegistry.instance().addMapLayer(myLayer)

    DOCK.getLayers()

    # Add MCL's to the CANVAS
    return myHazardLayerCount, myExposureLayerCount


class DockTest(unittest.TestCase):
    """Test the InaSAFE GUI"""

    def setUp(self):
        """Fixture run before all tests"""
        os.environ['LANG'] = 'en'
        DOCK.showOnlyVisibleLayersFlag = True
        loadStandardLayers()
        DOCK.cboHazard.setCurrentIndex(0)
        DOCK.cboExposure.setCurrentIndex(0)
        DOCK.cboFunction.setCurrentIndex(0)
        DOCK.runInThreadFlag = False
        DOCK.showOnlyVisibleLayersFlag = False
        DOCK.setLayerNameFromTitleFlag = False
        DOCK.zoomToImpactFlag = False
        DOCK.hideExposureFlag = False
        DOCK.showPostProcLayers = False

    def tearDown(self):
        """Fixture run after each test"""
        QgsMapLayerRegistry.instance().removeAllMapLayers()
        DOCK.cboHazard.clear()
        DOCK.cboExposure.clear()
        #DOCK.cboAggregation.clear() #dont do this because the cboAggregation
        # need to be able to react to the status changes of the other combos

    def test_defaults(self):
        """Test the GUI in its default state"""
        self.assertEqual(DOCK.cboHazard.currentIndex(), 0)
        self.assertEqual(DOCK.cboExposure.currentIndex(), 0)
        self.assertEqual(DOCK.cboFunction.currentIndex(), 0)
        self.assertEqual(DOCK.cboAggregation.currentIndex(), 0)

    def test_validate(self):
        """Validate function work as expected"""
        self.tearDown()
        # First check that we DONT validate a clear DOCK
        myFlag, myMessage = DOCK.validate()
        assert myMessage is not None, 'No reason for failure given'

        myMessage = 'Validation expected to fail on a cleared DOCK.'
        self.assertEquals(myFlag, False, myMessage)

        # Now check we DO validate a populated DOCK
        populatemyDock()
        myFlag = DOCK.validate()
        myMessage = ('Validation expected to pass on '
                     'a populated for with selections.')
        assert myFlag, myMessage

    def test_setOkButtonStatus(self):
        """OK button changes properly according to DOCK validity"""
        # First check that we ok ISNT enabled on a clear DOCK
        self.tearDown()
        myFlag, myMessage = DOCK.validate()

        assert myMessage is not None, 'No reason for failure given'
        myMessage = 'Validation expected to fail on a cleared DOCK.'
        self.assertEquals(myFlag, False, myMessage)

        # Now check OK IS enabled on a populated DOCK
        populatemyDock()
        myFlag = DOCK.validate()
        myMessage = ('Validation expected to pass on a ' +
                     'populated DOCK with selections.')
        assert myFlag, myMessage

    def test_cboAggregationEmptyProject(self):
        """Aggregation combo changes properly according on no loaded layers"""
        self.tearDown()
        myMessage = ('The aggregation combobox should have only the "Entire '
                     'area" item when the project has no layer. Found:'
                     ' %s' % (DOCK.cboAggregation.currentText()))

        self.assertEqual(DOCK.cboAggregation.currentText(), DOCK.tr(
            'Entire area'), myMessage)

        assert not DOCK.cboAggregation.isEnabled(), 'The aggregation ' \
            'combobox should be disabled when the project has no layer.'

    def test_cboAggregationLoadedProject(self):
        """Aggregation combo changes properly according loaded layers"""
        myLayerList = [DOCK.tr('Entire area'),
                       DOCK.tr('A flood in Jakarta'),
                       DOCK.tr('Essential buildings'),
                       DOCK.tr('kabupaten jakarta singlepart'),
                       DOCK.tr('OSM Building Polygons')]
        currentLayers = [DOCK.cboAggregation.itemText(i) for i in range(DOCK
        .cboAggregation.count())]

        myMessage = ('The aggregation combobox should have:\n %s \nFound: %s'
                     % (myLayerList, currentLayers))
        self.assertEquals(currentLayers, myLayerList, myMessage)

    #FIXME (MB) this is actually wrong, when calling the test directly it works
    # in nosetest it fails at the second assert
    @expectedFailure
    def test_cboAggregationToggle(self):
        """Aggregation Combobox toggles on and off as expected."""
        #raster hazard
        #raster exposure
        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregationEnabledFlag=True)
        myMessage += ' when the when hazard and exposure layer are raster'
        assert myResult, myMessage

        #vector hazard
        #raster exposure
        myResult, myMessage = setupScenario(
            theHazard=('A flood in Jakarta'),
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function Vector Hazard',
            theAggregationEnabledFlag=False)
        myMessage += ' when the when hazard is vector and exposure is raster'
        assert myResult, myMessage

        #raster hazard
        #vector exposure
        myResult, myMessage = setupScenario(
            theHazard='Tsunami Max Inundation',
            theExposure='Tsunami Building Exposure',
            theFunction='Be flooded',
            theFunctionId='Flood Building Impact Function',
            theAggregationEnabledFlag=False)
        myMessage += ' when the when hazard is raster and exposure is vector'
        assert myResult, myMessage

        #vector hazard
        #vector exposure
        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta',
            theExposure='Essential buildings',
            theFunction='Be flooded',
            theFunctionId='Flood Building Impact Function',
            theAggregationEnabledFlag=False)
        myMessage += ' when the when hazard and exposure layer are vector'
        assert myResult, myMessage

    def test_checkAggregationAttributeInKW(self):
        """Aggregation attribute is chosen correctly when present
            in kezwords."""
        myRunButton = DOCK.pbnRunStop
        myAttrKey = getDefaults('AGGR_ATTR_KEY')

        # with KAB_NAME aggregation attribute defined in .keyword using
        # kabupaten_jakarta_singlepart.shp
        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregation='kabupaten jakarta singlepart',
            theAggregationEnabledFlag=True)
        assert myResult, myMessage
        # Press RUN
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        DOCK.runtimeKWDialog.accept()
        myAttribute = DOCK.postprocAttributes[myAttrKey]
        myMessage = ('The aggregation should be KAB_NAME. Found: %s' %
                     (myAttribute))
        self.assertEqual(myAttribute, 'KAB_NAME', myMessage)

    def test_checkAggregationAttribute1Attr(self):
        """Aggregation attribute is chosen correctly when there is only
        one attr available."""
        myRunButton = DOCK.pbnRunStop
        myFileList = ['kabupaten_jakarta_singlepart_1_good_attr.shp']
        #add additional layers
        loadLayers(myFileList, theClearFlag=False, theDataDirectory=TESTDATA)
        myAttrKey = getDefaults('AGGR_ATTR_KEY')

        # with 1 good aggregation attribute using
        # kabupaten_jakarta_singlepart_1_good_attr.shp
        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregation='kabupaten jakarta singlepart 1 good attr')
        assert myResult, myMessage
        # Press RUN
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        DOCK.runtimeKWDialog.accept()
        myAttribute = DOCK.postprocAttributes[myAttrKey]
        myMessage = ('The aggregation should be KAB_NAME. Found: %s' %
                     (myAttribute))
        self.assertEqual(myAttribute, 'KAB_NAME', myMessage)

    def test_checkAggregationAttributeNoAttr(self):
        """Aggregation attribute is chosen correctly when there is no
        attr available."""

        myRunButton = DOCK.pbnRunStop
        myFileList = ['kabupaten_jakarta_singlepart_0_good_attr.shp']
        #add additional layers
        loadLayers(myFileList, theClearFlag=False, theDataDirectory=TESTDATA)
        myAttrKey = getDefaults('AGGR_ATTR_KEY')
        # with no good aggregation attribute using
        # kabupaten_jakarta_singlepart_0_good_attr.shp
        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregation='kabupaten jakarta singlepart 0 good attr')
        assert myResult, myMessage
        # Press RUN
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        DOCK.runtimeKWDialog.accept()
        myAttribute = DOCK.postprocAttributes[myAttrKey]
        myMessage = ('The aggregation should be None. Found: %s' %
                     (myAttribute))
        assert myAttribute is None, myMessage

    def test_checkAggregationAttributeNoneAttr(self):
        """Aggregation attribute is chosen correctly when there None in the
            kezwords"""

        myRunButton = DOCK.pbnRunStop
        myFileList = ['kabupaten_jakarta_singlepart_with_None_keyword.shp']
        #add additional layers
        loadLayers(myFileList, theClearFlag=False, theDataDirectory=TESTDATA)
        myAttrKey = getDefaults('AGGR_ATTR_KEY')
        # with None aggregation attribute defined in .keyword using
        # kabupaten_jakarta_singlepart_with_None_keyword.shp
        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregation='kabupaten jakarta singlepart with None keyword')
        assert myResult, myMessage
        # Press RUN
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        DOCK.runtimeKWDialog.accept()
        myAttribute = DOCK.postprocAttributes[myAttrKey]
        myMessage = ('The aggregation should be None. Found: %s' %
                     (myAttribute))
        assert myAttribute is None, myMessage

    #the generated layers are not added to the map registry
    def test_checkPostProcessingLayersVisibility(self):
        myRunButton = DOCK.pbnRunStop

        # with KAB_NAME aggregation attribute defined in .keyword using
        # kabupaten_jakarta_singlepart.shp
        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregation='kabupaten jakarta singlepart',
            theOkButtonFlag=True)
        assert myResult, myMessage
        myBeforeCount = len(CANVAS.layers())
        #LOGGER.info("Canvas list before:\n%s" % canvasList())
        print [str(l.name()) for l in
               QgsMapLayerRegistry.instance().mapLayers().values()]
        LOGGER.info("Registry list before:\n%s" %
                    len(QgsMapLayerRegistry.instance().mapLayers()))
        # Press RUN
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        myAfterCount = len(CANVAS.layers())
        LOGGER.info("Registry list after:\n%s" %
                    len(QgsMapLayerRegistry.instance().mapLayers()))
#        print [str(l.name()) for l in QgsMapLayerRegistry.instance(
#           ).mapLayers().values()]
        #LOGGER.info("Canvas list after:\n%s" % canvasList())
        myMessage = ('Expected %s items in canvas, got %s' %
                     (myBeforeCount + 1, myAfterCount))
        assert myBeforeCount + 1 == myAfterCount, myMessage

        # Now run again showing intermediate layers

        DOCK.showPostProcLayers = True
        myBeforeCount = len(CANVAS.layers())
        # Press RUN
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        myAfterCount = len(CANVAS.layers())
        LOGGER.info("Canvas list after:\n %s" % canvasList())
        myMessage = ('Expected %s items in canvas, got %s' %
                     (myBeforeCount + 2, myAfterCount))
        # We expect two more since we enabled showing intermedate layers
        assert myBeforeCount + 2 == myAfterCount, myMessage

    def test_runEarthQuakeGuidelinesFunction(self):
        """GUI runs with Shakemap 2009 and Padang Buildings"""

        # Push OK with the left mouse button

        myButton = DOCK.pbnRunStop
        setCanvasCrs(GEOCRS, True)
        setPadangGeoExtent()
        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        #QTest.keyClick(DOCK.cboHazard, QtCore.Qt.Key_Down)
        #QTest.keyClick(DOCK.cboHazard, QtCore.Qt.Key_Enter)
        #
        #QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Down)
        #QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Enter)

        # Hazard layer
        myIndex = DOCK.cboHazard.findText(PADANG2009_title)
        assert myIndex != -1, 'Padang 2009 scenario hazard layer not found'
        DOCK.cboHazard.setCurrentIndex(myIndex)

        # Exposure layer
        myIndex = DOCK.cboExposure.findText('Padang_WGS84')
        myMessage = ('Could not find layer Padang_WGS84:\n'
                     '%s' % (combosToString(DOCK)))
        assert myIndex != -1, myMessage
        DOCK.cboExposure.setCurrentIndex(myIndex)

        # Impact function
        myIndex = DOCK.cboFunction.findText('Earthquake Guidelines Function')
        myMessage = ('Earthquake Guidelines function not '
               'found: ' + combosToString(DOCK))
        assert myIndex != -1, myMessage
        DOCK.cboFunction.setCurrentIndex(myIndex)

        myDict = getUiState(DOCK)
        myExpectedDict = {'Hazard': PADANG2009_title,
                          'Exposure': 'Padang_WGS84',
                          'Impact Function Id':
                              'Earthquake Guidelines Function',
                          'Impact Function Title':
                              'Earthquake Guidelines Function',
                          'Run Button Enabled': True}
        myMessage = 'Got:\n %s\nExpected:\n%s\n%s' % (
                        myDict, myExpectedDict, combosToString(DOCK))
        assert myDict == myExpectedDict, myMessage

        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.page().currentFrame().toPlainText()
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

    def test_runEarthquakeFatalityFunction_small(self):
        """Padang 2009 fatalities estimated correctly (small extent)"""

        # Push OK with the left mouse button

        myButton = DOCK.pbnRunStop
        setCanvasCrs(GEOCRS, True)
        setPadangGeoExtent()

        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        # Simulate choosing another combo item and running
        # the model again
        myIndex = DOCK.cboHazard.findText(PADANG2009_title)
        assert myIndex != -1, 'Padang 2009 scenario hazard layer not found'
        DOCK.cboHazard.setCurrentIndex(myIndex)

        # Exposure layers
        myIndex = DOCK.cboExposure.findText('People')
        assert myIndex != -1, 'People'
        DOCK.cboExposure.setCurrentIndex(myIndex)

        # Choose impact function
        myIndex = DOCK.cboFunction.findText('Earthquake Fatality Function')
        myMessage = ('Earthquake Fatality Function not '
               'found: ' + combosToString(DOCK))
        assert myIndex != -1, myMessage
        DOCK.cboFunction.setCurrentIndex(myIndex)

        myDict = getUiState(DOCK)
        myExpectedDict = {'Hazard': PADANG2009_title,
                          'Exposure': 'People',
                          'Impact Function Id': 'Earthquake Fatality Function',
                          'Impact Function Title':
                              'Earthquake Fatality Function',
                          'Run Button Enabled': True}
        myMessage = 'Got unexpected state: %s\nExpected: %s\n%s' % (
                            myDict, myExpectedDict, combosToString(DOCK))
        assert myDict == myExpectedDict, myMessage

        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)

        myResult = DOCK.wvResults.page().currentFrame().toPlainText()

        # Check against expected output
        myMessage = ('Unexpected result returned for Earthquake Fatality '
                     'Function Expected: fatality count of '
                     '116 , received: \n %s' % myResult)
        assert '116' in myResult, myMessage

        myMessage = ('Unexpected result returned for Earthquake Fatality '
                     'Function Expected: total population count of '
                     '847529 , received: \n %s' % myResult)
        assert '847529' in myResult, myMessage

    def test_runEarthquakeFatalityFunction_Padang_full(self):
        """Padang 2009 fatalities estimated correctly (large extent)"""

        # Push OK with the left mouse button

        myButton = DOCK.pbnRunStop
        setCanvasCrs(GEOCRS, True)
        setGeoExtent([96, -5, 105, 2])  # This covers all of the 2009 shaking
        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        # Hazard layers
        myIndex = DOCK.cboHazard.findText(PADANG2009_title)
        assert myIndex != -1, 'Padang 2009 scenario hazard layer not found'
        DOCK.cboHazard.setCurrentIndex(myIndex)

        # Exposure layers
        myIndex = DOCK.cboExposure.findText('People')
        assert myIndex != -1, 'People'
        DOCK.cboExposure.setCurrentIndex(myIndex)

        # Choose impact function
        myIndex = DOCK.cboFunction.findText('Earthquake Fatality Function')
        myMessage = ('Earthquake Fatality Function not '
               'found: ' + combosToString(DOCK))
        assert myIndex != -1, myMessage
        DOCK.cboFunction.setCurrentIndex(myIndex)

        myDict = getUiState(DOCK)
        myExpectedDict = {'Hazard': PADANG2009_title,
                          'Exposure': 'People',
                          'Impact Function Id':
                              'Earthquake Fatality Function',
                          'Impact Function Title':
                              'Earthquake Fatality Function',
                          'Run Button Enabled': True}
        myMessage = 'Got unexpected state: %s\nExpected: %s\n%s' % (
                            myDict, myExpectedDict, combosToString(DOCK))
        assert myDict == myExpectedDict, myMessage

        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)

        myResult = DOCK.wvResults.page().currentFrame().toPlainText()

        # Check against expected output
        myMessage = ('Unexpected result returned for Earthquake Fatality '
                     'Function Expected: fatality count of '
                     '500 , received: \n %s' % myResult)
        assert '500' in myResult, myMessage

        myMessage = ('Unexpected result returned for Earthquake Fatality '
                     'Function Expected: total population count of '
                     '31372262 , received: \n %s' % myResult)
        assert '31372262' in myResult, myMessage

    def test_runTsunamiBuildingImpactFunction(self):
        """Tsunami function runs in GUI as expected."""

        # Push OK with the left mouse button

        myButton = DOCK.pbnRunStop

        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        myResult, myMessage = setupScenario(
            theHazard='Tsunami Max Inundation',
            theExposure='Tsunami Building Exposure',
            theFunction='Be flooded',
            theFunctionId='Flood Building Impact Function')
        assert myResult, myMessage

        setCanvasCrs(GEOCRS, True)
        setBatemansBayGeoExtent()

        # Press RUN
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.page().currentFrame().toPlainText()

        #print myResult
        # Post clip on steroids refactor
        # < 1 m:    1923
        # 1 - 3 m:    89
        # > 3 m:    0
        # Post replacement of Batemans Bay dataset
        #< 1 m:  10
        #1 - 3 m:    7
        #> 3 m:  0
        # Post rewrite of impact function
        #Building type	 closed	Total
        #All	        7	                17

        myMessage = 'Result not as expected: %s' % myResult
        assert '17' in myResult, myMessage
        assert '7' in myResult, myMessage

    def test_runFloodPopulationImpactFunction(self):
        """Flood function runs in GUI with Jakarta data
           Raster on raster based function runs as expected."""

        # Push OK with the left mouse button
        myButton = DOCK.pbnRunStop

        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='Penduduk Jakarta',
            theFunction='HKVtest',
            theFunctionId='HKVtest')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()

        # Press RUN
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.page().currentFrame().toPlainText()

        # Check that the number is as what was calculated by
        # Marco Hartman form HKV
        myMessage = 'Result not as expected: %s' % myResult
        # This is the expected impact number
        assert '2480' in myResult, myMessage

    def test_runFloodPopulationImpactFunction_scaling(self):
        """Flood function runs in GUI with 5x5km population data
           Raster on raster based function runs as expected with scaling."""

        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()

        # Press RUN
        myButton = DOCK.pbnRunStop
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.page().currentFrame().toPlainText()

        myMessage = 'Result not as expected: %s' % myResult

        # Check numbers are OK (within expected errors from resampling)
        assert format_int(10484) in myResult, myMessage
        assert '977' in myResult, myMessage  # These are expected impact number

    def test_runFloodPopulationPolygonHazardImpactFunction(self):
        """Flood function runs in GUI with Jakarta polygon flood hazard data.
           Uses population raster exposure layer"""

        myResult, myMessage = setupScenario(
            theHazard=('A flood in Jakarta'),
            theExposure='Penduduk Jakarta',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function Vector Hazard')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()

        # Press RUN
        myButton = DOCK.pbnRunStop
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.page().currentFrame().toPlainText()

        myMessage = 'Result not as expected: %s' % myResult
        # This is the expected number of people needing evacuation
        assert '134953000' in myResult, myMessage

    def test_runCategorizedHazardBuildingImpact(self):
        """Flood function runs in GUI with Flood in Jakarta hazard data
            Uses DKI buildings exposure data."""

        myResult, myMessage = setupScenario(
            theHazard='Flood in Jakarta',
            theExposure='Essential buildings',
            theFunction='Be affected',
            theFunctionId='Categorised Hazard Building Impact Function')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()

        # Press RUN
        myButton = DOCK.pbnRunStop
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.page().currentFrame().toPlainText()

        myMessage = 'Result not as expected: %s' % myResult
        # This is the expected number of building might be affected
        assert '535' in myResult, myMessage
        assert '453' in myResult, myMessage
        assert '436' in myResult, myMessage

    def test_runCategorisedHazardPopulationImpactFunction(self):
        """Flood function runs in GUI with Flood in Jakarta hazard data
            Uses Penduduk Jakarta as exposure data."""

        myResult, myMessage = setupScenario(
            theHazard='Flood in Jakarta',
            theExposure='Penduduk Jakarta',
            theFunction='Be impacted',
            theFunctionId='Categorised Hazard Population Impact Function')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()

        # Press RUN
        myButton = DOCK.pbnRunStop
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.page().currentFrame().toPlainText()

        myMessage = 'Result not as expected: %s' % myResult
        # This is the expected number of population might be affected
        assert '30938000' in myResult, myMessage
        assert '68280000' in myResult, myMessage
        assert '157551000' in myResult, myMessage

    def test_runEarthquakeBuildingImpactFunction(self):
        """Flood function runs in GUI with An earthquake in Yogyakarta like in
            2006 hazard data uses OSM Building Polygons exposure data."""

        myResult, myMessage = setupScenario(
            theHazard='An earthquake in Yogyakarta like in 2006',
            theExposure='OSM Building Polygons',
            theFunction='Be affected',
            theFunctionId='Earthquake Building Impact Function')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setGeoExtent([101, -12 , 119, -4])

        # Press RUN
        myButton = DOCK.pbnRunStop
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.page().currentFrame().toPlainText()
        LOGGER.debug(myResult)

        myMessage = 'Result not as expected: %s' % myResult
        # This is the expected number of building might be affected
        assert '786' in myResult, myMessage
        assert '15528' in myResult, myMessage
        assert '177' in myResult, myMessage

    # disabled this test until further coding
    def Xtest_printMap(self):
        """Test print map, especially on Windows."""

        myResult, myMessage = setupScenario(
            theHazard='Flood in Jakarta',
            theExposure='Essential buildings',
            theFunction='Be affected',
            theFunctionId='Categorised Hazard Building Impact Function')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()

        # Press RUN
        myButton = DOCK.pbnRunStop
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        printButton = DOCK.pbnPrint

        try:
            QTest.mouseClick(printButton, QtCore.Qt.LeftButton)
        except OSError:
            LOGGER.debug('OSError')
            # pass
        except Exception, e:
            raise Exception('Exception is not expected, %s' % e)

    def test_ResultStyling(self):
        """Test that ouputs from a model are correctly styled (colours and
        opacity. """

        # Push OK with the left mouse button

        print '--------------------'
        print combosToString(DOCK)

        myResult, myMessage = setupScenario(
            theHazard=('A flood in Jakarta like in 2007'),
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()

        # Run manually so we can get the output layer
        DOCK.setupCalculator()
        myRunner = DOCK.calculator.getRunner()
        myRunner.run()  # Run in same thread
        myEngineImpactLayer = myRunner.impactLayer()
        myQgisImpactLayer = DOCK.readImpactLayer(myEngineImpactLayer)
        myStyle = myEngineImpactLayer.get_style_info()
        #print myStyle
        setRasterStyle(myQgisImpactLayer, myStyle)
        # simple test for now - we could test explicity for style state
        # later if needed.
        myMessage = ('Raster layer was not assigned a ColorRampShader'
                     ' as expected.')
        assert myQgisImpactLayer.colorShadingAlgorithm() == \
                QgsRasterLayer.ColorRampShader, myMessage

        # Commenting out because we changed impact function to use floating
        # point quantities. Revisit in QGIS 2.0 where range based transparency
        # will have been implemented
        #myMessage = ('Raster layer was not assigned transparency'
        #             'classes as expected.')
        #myTransparencyList = (myQgisImpactLayer.rasterTransparency().
        #        transparentSingleValuePixelList())
        #print "Transparency list:" + str(myTransparencyList)
        #assert (len(myTransparencyList) > 0)

    def test_Issue47(self):
        """Issue47: Problem when hazard & exposure data are in different
        proj to viewport.
        See https://github.com/AIFDR/inasafe/issues/47"""

        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='Penduduk Jakarta',
            theFunction='HKVtest',
            theFunctionId='HKVtest')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GOOGLECRS, True)
        setJakartaGoogleExtent()

        # Press RUN
        myButton = DOCK.pbnRunStop
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.page().currentFrame().toPlainText()

        myMessage = 'Result not as expected: %s' % myResult
        assert '2366' in myResult, myMessage

    def test_issue45(self):
        """Points near the edge of a raster hazard layer are interpolated OK"""

        myButton = DOCK.pbnRunStop
        setCanvasCrs(GEOCRS, True)
        setYogyaGeoExtent()

        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        myResult, myMessage = setupScenario(
            theHazard='An earthquake in Yogyakarta like in 2006',
            theExposure='OSM Building Polygons',
            theFunction='Earthquake Guidelines Function',
            theFunctionId='Earthquake Guidelines Function')
        assert myResult, myMessage

        # This is the where nosetest sometims hangs when running the
        # guitest suite (Issue #103)
        # The QTest.mouseClick call some times never returns when run
        # with nosetest, but OK when run normally.
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.page().currentFrame().toPlainText()

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
        # ANSWER
        #DOCK.calculator.impactLayer()

    def test_loadLayers(self):
        """Layers can be loaded and list widget was updated appropriately
        """

        myHazardLayerCount, myExposureLayerCount = loadStandardLayers()
        myMessage = 'Expect %s layer(s) in hazard list widget but got %s' \
                     % (myHazardLayerCount, DOCK.cboHazard.count())
        # pylint: disable=W0106
        self.assertEqual(DOCK.cboHazard.count(),
                         myHazardLayerCount), myMessage
        myMessage = 'Expect %s layer(s) in exposure list widget but got %s' \
              % (myExposureLayerCount, DOCK.cboExposure.count())
        self.assertEqual(DOCK.cboExposure.count(),
                         myExposureLayerCount), myMessage
        # pylint: disable=W0106

    def test_Issue71(self):
        """Test issue #71 in github - cbo changes should update ok button."""
        # See https://github.com/AIFDR/inasafe/issues/71
        # Push OK with the left mouse button
        print 'Using QGIS: %s' % qgisVersion()
        self.tearDown()
        myButton = DOCK.pbnRunStop
        # First part of scenario should have enabled run
        myFileList = [join(HAZDATA,
                           'Flood_Current_Depth_Jakarta_geographic.asc'),
                      join(TESTDATA,
                           'Population_Jakarta_geographic.asc')]
        myHazardLayerCount, myExposureLayerCount = loadLayers(myFileList,
                                                    theDataDirectory=None)

        myMessage = ('Incorrect number of Hazard layers: expected 1 got %s'
                     % myHazardLayerCount)
        assert myHazardLayerCount == 1, myMessage

        myMessage = ('Incorrect number of Exposure layers: expected 1 got %s'
                     % myExposureLayerCount)
        assert myExposureLayerCount == 1, myMessage
        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        # Second part of scenario - run disabled when adding invalid layer
        # and select it - run should be disabled
        myFileList = ['issue71.tif']  # This layer has incorrect keywords
        myClearFlag = False
        myHazardLayerCount, myExposureLayerCount = (
            loadLayers(myFileList, myClearFlag))
        # set exposure to : Population Density Estimate (5kmx5km)
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Down)
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Enter)
        myDict = getUiState(DOCK)
        myExpectedDict = {'Run Button Enabled': False,
                          'Impact Function Id': '',
                          'Impact Function Title': '',
                          'Hazard': 'A flood in Jakarta like in 2007',
                          'Exposure': 'Population density (5kmx5km)'}
        myMessage = ('Run button was not disabled when exposure set to \n%s'
                     '\nUI State: \n%s\nExpected State:\n%s\n%s') % (
            DOCK.cboExposure.currentText(),
            myDict,
            myExpectedDict,
            combosToString(DOCK))

        assert myExpectedDict == myDict, myMessage

        # Now select again a valid layer and the run button
        # should be enabled
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Up)
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Enter)
        myMessage = ('Run button was not enabled when exposure set to \n%s' %
            DOCK.cboExposure.currentText())
        assert myButton.isEnabled(), myMessage

    def test_Issue95(self):
        """Test issue #95 in github -check crs of impact layer."""
        # See https://github.com/AIFDR/inasafe/issues/95
        # Push OK with the left mouse button
        self.tearDown()
        myButton = DOCK.pbnRunStop
        # First part of scenario should have enabled run
        myFileList = [join(HAZDATA,
                           'Flood_Current_Depth_Jakarta_geographic.asc'),
                      join(TESTDATA,
                           'Population_Jakarta_geographic.asc')]
        myHazardLayerCount, myExposureLayerCount = loadLayers(myFileList,
                                                theDataDirectory=None)

        myMessage = ('Incorrect number of Hazard layers: expected 1 got %s'
                     % myHazardLayerCount)
        assert myHazardLayerCount == 1, myMessage

        myMessage = ('Incorrect number of Exposure layers: expected 1 got %s'
                     % myExposureLayerCount)
        assert myExposureLayerCount == 1, myMessage
        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        # Second part of scenario - run disables when adding invalid layer
        # and select it - run should be disabled
        myFileList = ['issue71.tif']  # This layer has incorrect keywords
        myClearFlag = False
        myHazardLayerCount, myExposureLayerCount = (
            loadLayers(myFileList, myClearFlag))
        # set exposure to : Population density (5kmx5km)
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Down)
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Enter)
        myDict = getUiState(DOCK)
        myExpectedDict = {'Run Button Enabled': False,
                          'Impact Function Id': '',
                          'Impact Function Title': '',
                          'Hazard': 'A flood in Jakarta like in 2007',
                          'Exposure': 'Population density (5kmx5km)'}
        myMessage = ('Run button was not disabled when exposure set to \n%s'
                     '\nUI State: \n%s\nExpected State:\n%s\n%s') % (
            DOCK.cboExposure.currentText(),
            myDict,
            myExpectedDict,
            combosToString(DOCK))

        assert myExpectedDict == myDict, myMessage

        # Now select again a valid layer and the run button
        # should be enabled
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Up)
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Enter)
        myMessage = ('Run button was not enabled when exposure set to \n%s' %
            DOCK.cboExposure.currentText())
        assert myButton.isEnabled(), myMessage

    def test_issue_160(self):
        """Test that multipart features can be used in a scenario - issue #160
        """

        myExposure = os.path.join(UNITDATA, 'exposure',
                                  'buildings_osm_4326.shp')
        myHazard = os.path.join(UNITDATA, 'hazard',
                                  'multipart_polygons_osm_4326.shp')
                # See https://github.com/AIFDR/inasafe/issues/71
        # Push OK with the left mouse button
        print 'Using QGIS: %s' % qgisVersion()
        self.tearDown()
        myButton = DOCK.pbnRunStop
        # First part of scenario should have enabled run
        myFileList = [myHazard, myExposure]
        myHazardLayerCount, myExposureLayerCount = loadLayers(myFileList,
                                            theDataDirectory=TESTDATA)

        myMessage = ('Incorrect number of Hazard layers: expected 1 got %s'
                     % myHazardLayerCount)
        assert myHazardLayerCount == 1, myMessage

        myMessage = ('Incorrect number of Exposure layers: expected 1 got %s'
                     % myExposureLayerCount)
        assert myExposureLayerCount == 1, myMessage

        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        # Second part of scenario - run disabled when adding invalid layer
        # and select it - run should be disabled
        myFileList = ['issue71.tif']  # This layer has incorrect keywords
        myClearFlag = False
        myHazardLayerCount, myExposureLayerCount = (
            loadLayers(myFileList, myClearFlag))

        myResult, myMessage = setupScenario(
            theHazard='multipart_polygons_osm_4326',
            theExposure='buildings_osm_4326',
            theFunction='Be flooded',
            theFunctionId='Flood Building Impact Function')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        IFACE.mapCanvas().setExtent(
                                QgsRectangle(106.788, -6.193, 106.853, -6.167))

        # Press RUN
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.page().currentFrame().toPlainText()

        myMessage = 'Result not as expected: %s' % myResult
        assert '68' in myResult, myMessage

    def test_state(self):
        """Check if the save/restore state methods work. See also
        https://github.com/AIFDR/inasafe/issues/58
        """
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Up)
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Enter)
        DOCK.saveState()
        myExpectedDict = getUiState(DOCK)
        #myState = DOCK.state
        # Now reset and restore and check that it gets the old state
        # Html is not considered in restore test since the ready
        # message overwrites it in dock implementation
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Up)
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Enter)
        DOCK.restoreState()
        myResultDict = getUiState(DOCK)
        myMessage = 'Got unexpected state: %s\nExpected: %s\n%s' % (
                            myResultDict, myExpectedDict, combosToString(DOCK))
        assert myExpectedDict == myResultDict, myMessage

        # Corner case test when two layers can have the
        # same functions - when switching layers the selected function should
        # remain unchanged
        self.tearDown()
        myFileList = [join(HAZDATA,
                           'Flood_Design_Depth_Jakarta_geographic.asc'),
                      join(HAZDATA,
                           'Flood_Current_Depth_Jakarta_geographic.asc'),
                      join(TESTDATA,
                           'Population_Jakarta_geographic.asc')]
        myHazardLayerCount, myExposureLayerCount = loadLayers(myFileList,
                                                  theDataDirectory=None)
        assert myHazardLayerCount == 2
        assert myExposureLayerCount == 1
        DOCK.cboHazard.setCurrentIndex(0)
        QTest.keyClick(DOCK.cboFunction, QtCore.Qt.Key_Down)
        QTest.keyClick(DOCK.cboFunction, QtCore.Qt.Key_Enter)
        myExpectedFunction = str(DOCK.cboFunction.currentText())
        # Now move down one hazard in the combo then verify
        # the function remains unchanged
        QTest.keyClick(DOCK.cboHazard, QtCore.Qt.Key_Down)
        QTest.keyClick(DOCK.cboHazard, QtCore.Qt.Key_Enter)
        myCurrentFunction = str(DOCK.cboFunction.currentText())
        myMessage = ('Expected selected impact function to remain unchanged '
                     'when choosing a different hazard of the same category:'
                     ' %s\nExpected: %s\n%s' % (
                myExpectedFunction,
                myCurrentFunction,
                combosToString(DOCK)))

        assert myExpectedFunction == myCurrentFunction, myMessage
        QTest.keyClick(DOCK.cboHazard, QtCore.Qt.Key_Down)
        QTest.keyClick(DOCK.cboHazard, QtCore.Qt.Key_Enter)
        # Selected function should remain the same
        myExpectation = 'Need evacuation'
        myFunction = DOCK.cboFunction.currentText()
        myMessage = 'Expected: %s, Got: %s' % (myExpectation, myFunction)
        assert myFunction == myExpectation, myMessage

    #FIXME (MB) this is actually wrong, when calling the test directly it works
    # in nosetest it fails at the first assert
    @expectedFailure
    def test_aggregationResults(self):
        """Aggregation results are correct."""
        myRunButton = DOCK.pbnRunStop
        myExpectedResult = open(TEST_FILES_DIR +
                                '/test-aggregation-results.txt',
                                'r').read()

        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregation='kabupaten jakarta singlepart',
            theAggregationEnabledFlag=True)
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()
        # Press RUN
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        DOCK.runtimeKWDialog.accept()

        myResult = DOCK.wvResults.page().currentFrame().toPlainText()
        myMessage = ('The postprocessing report should be:\n%s\nFound:\n%s' %
                     (myExpectedResult, myResult))
        self.assertEqual(myExpectedResult, myResult, myMessage)

    def test_layerChanged(self):
        """Test the metadata is updated as the user highlights different
        QGIS layers. For inasafe outputs, the table of results should be shown
        See also
        https://github.com/AIFDR/inasafe/issues/58
        """
        myLayer, myType = loadLayer('issue58.tif')
        myMessage = ('Unexpected category for issue58.tif.\nGot:'
                     ' %s\nExpected: undefined' % myType)

        assert myType == 'undefined', myMessage
        DOCK.layerChanged(myLayer)
        DOCK.saveState()
        myHtml = DOCK.state['report']
        myExpectedString = '4229'
        myMessage = "%s\nDoes not contain:\n%s" % (
                                myHtml,
                                myExpectedString)
        assert myExpectedString in myHtml, myMessage

    def test_newLayersShowInCanvas(self):
        """Check that when we add a layer we can see it in the canvas list."""
        LOGGER.info("Canvas list before:\n%s" % canvasList())
        myBeforeCount = len(CANVAS.layers())
        myPath = join(TESTDATA, 'polygon_0.shp')
        myLayer = QgsVectorLayer(myPath, 'foo', 'ogr')
        QgsMapLayerRegistry.instance().addMapLayer(myLayer)
        myAfterCount = len(CANVAS.layers())
        LOGGER.info("Canvas list after:\n%s" % canvasList())
        myMessage = ('Layer was not added to canvas (%s before, %s after)' %
                     (myBeforeCount, myAfterCount))
        assert myBeforeCount == myAfterCount - 1, myMessage
        QgsMapLayerRegistry.instance().removeMapLayer(myLayer.id())

    def test_issue317(self):
        """Points near the edge of a raster hazard layer are interpolated OK"""

        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()
        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='OSM Building Polygons',
            theFunction='Be flooded',
            theFunctionId='Flood Building Impact Function')
        DOCK.getFunctions()
        assert myResult, myMessage

    def Xtest_runnerExceptions(self):
        """Test runner exceptions"""
        myRunButton = DOCK.pbnRunStop

        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Exception riser',
            theFunctionId='Exception Raising Impact Function',
            theAggregationEnabledFlag=True)
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()
        # Press RUN
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
#        DOCK.runtimeKWDialog.accept()
        myExpectedResult = """Error:
An exception occurred when calculating the results
Problem:
Exception : AHAHAH I got you
Click for Diagnostic Information:
"""
        myResult = DOCK.wvResults.page().currentFrame().toPlainText()
        myMessage = ('The result message should be:\n%s\nFound:\n%s' %
                     (myExpectedResult, myResult))
        self.assertEqual(myExpectedResult, myResult, myMessage)

    def Xtest_runnerIsNone(self):
        """Test for none runner exceptions"""
        myRunButton = DOCK.pbnRunStop

        myResult, myMessage = setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='None returner',
            theFunctionId='None Returning Impact Function',
            theAggregationEnabledFlag=True)
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()

        # Press RUN
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        #        DOCK.runtimeKWDialog.accept()
        myExpectedResult = """Error:
An exception occurred when calculating the results
Problem:
AttributeError : 'NoneType' object has no attribute 'keywords'
Click for Diagnostic Information:
"""
        myResult = DOCK.wvResults.page().currentFrame().toPlainText()
        myMessage = ('The result message should be:\n%s\nFound:\n%s' %
                     (myExpectedResult, myResult))
        self.assertEqual(myExpectedResult, myResult, myMessage)

    def test_hasParametersButtonDisabled(self):
        """Function configuration button is disabled
        when layers not compatible."""
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()
        #myResult, myMessage = setupScenario(
        #    theHazard='A flood in Jakarta like in 2007',
        #    theExposure='Essential Buildings',
        #    theFunction='Be flooded',
        #    theFunctionId='Flood Building Impact Function')
        setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='Essential Buildings',
            theFunction='Be flooded',
            theFunctionId='Flood Building Impact Function')
        myToolButton = DOCK.toolFunctionOptions
        myFlag = myToolButton.isEnabled()
        assert not myFlag, ('Expected configuration options '
                            'button to be disabled')

    def test_hasParametersButtonEnabled(self):
        """Function configuration button is enabled when layers are compatible.
        """
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()
        #myResult, myMessage = setupScenario(
        #    theHazard='A flood in Jakarta like in 2007',
        #    theExposure='Penduduk Jakarta',
        #    theFunction='Need evacuation',
        #    theFunctionId='Flood Evacuation Function')
        setupScenario(
            theHazard='A flood in Jakarta like in 2007',
            theExposure='Penduduk Jakarta',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function')
        myToolButton = DOCK.toolFunctionOptions
        myFlag = myToolButton.isEnabled()
        assert myFlag, ('Expected configuration options '
                            'button to be enabled')

if __name__ == '__main__':
    suite = unittest.makeSuite(DockTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
