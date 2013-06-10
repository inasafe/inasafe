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
#for p in sys.path:
#    print p + '\n'

from PyQt4 import QtCore
from PyQt4.QtTest import QTest

from qgis.core import (QgsRasterLayer,
                       QgsVectorLayer,
                       QgsMapLayerRegistry,
                       QgsRectangle)
from safe_interface import (format_int,
                            HAZDATA, TESTDATA, UNITDATA, BOUNDDATA)

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
                                      loadLayer,
                                      loadStandardLayers,
                                      populatemyDock,
                                      combosToString,
                                      getUiState,
                                      setupScenario,
                                      loadLayers,
                                      canvasList)

from safe_qgis.dock import Dock
from safe_qgis.styling import setRasterStyle
from safe_qgis.utilities import qgisVersion


# Retired impact function for characterisation (Ole)
# So ignore unused import errors for these? (Tim)
# pylint: disable=W0611
# noinspection PyUnresolvedReferences
from safe.engine.impact_functions_for_testing import allen_fatality_model
# noinspection PyUnresolvedReferences
from safe.engine.impact_functions_for_testing import HKV_flood_study
# noinspection PyUnresolvedReferences
from safe.engine.impact_functions_for_testing import BNPB_earthquake_guidelines
# noinspection PyUnresolvedReferences
from safe.engine.impact_functions_for_testing import \
    categorised_hazard_building_impact
#from safe.engine.impact_functions_for_testing import error_raising_functions
# pylint: enable=W0611

LOGGER = logging.getLogger('InaSAFE')

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
DOCK = Dock(IFACE)

YOGYA2006_title = 'An earthquake in Yogyakarta like in 2006'
PADANG2009_title = 'An earthquake in Padang like in 2009'

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__),
                              'test_data/test_files')


#noinspection PyArgumentList
class DockTest(unittest.TestCase):
    """Test the InaSAFE GUI"""

    def setUp(self):
        """Fixture run before all tests"""
        os.environ['LANG'] = 'en'
        DOCK.showOnlyVisibleLayersFlag = True
        loadStandardLayers(DOCK)
        DOCK.cboHazard.setCurrentIndex(0)
        DOCK.cboExposure.setCurrentIndex(0)
        DOCK.cboFunction.setCurrentIndex(0)
        DOCK.runInThreadFlag = False
        DOCK.showOnlyVisibleLayersFlag = False
        DOCK.setLayerNameFromTitleFlag = False
        DOCK.zoomToImpactFlag = False
        DOCK.hideExposureFlag = False
        DOCK.showIntermediateLayers = False

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
        populatemyDock(DOCK)
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
        populatemyDock(DOCK)
        myFlag = DOCK.validate()
        myMessage = ('Validation expected to pass on a ' +
                     'populated DOCK with selections.')
        assert myFlag, myMessage

    def test_runEarthQuakeGuidelinesFunction(self):
        """GUI runs with Shakemap 2009 and Padang Buildings"""

        # Push OK with the left mouse button

        myButton = DOCK.pbnRunStop
        setCanvasCrs(GEOCRS, True)
        setPadangGeoExtent()

        myResult, myMessage = setupScenario(
            DOCK,
            theHazard=PADANG2009_title,
            theExposure='Padang WGS84',
            theFunction='Earthquake Guidelines Function',
            theFunctionId='Earthquake Guidelines Function')
        assert myResult, myMessage

        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.pageToText()
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
        assert format_int(2993) in myResult, myMessage

    def test_runEarthquakeFatalityFunction_small(self):
        """Padang 2009 fatalities estimated correctly (small extent)."""

        # Push OK with the left mouse button
        myButton = DOCK.pbnRunStop
        setCanvasCrs(GEOCRS, True)
        setPadangGeoExtent()

        myResult, myMessage = setupScenario(
            DOCK,
            theHazard=PADANG2009_title,
            theExposure='People',
            theFunction='Earthquake Fatality Function',
            theFunctionId='Earthquake Fatality Function')
        assert myResult, myMessage

        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)

        myResult = DOCK.wvResults.pageToText()

        # Check against expected output
        myMessage = ('Unexpected result returned for Earthquake Fatality '
                     'Function Expected: fatality count of '
                     '116 , received: \n %s' % myResult)
        assert format_int(116) in myResult, myMessage

        myMessage = ('Unexpected result returned for Earthquake Fatality '
                     'Function Expected: total population count of '
                     '847529 , received: \n %s' % myResult)
        assert format_int(847529) in myResult, myMessage

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

        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)

        myResult = DOCK.wvResults.pageToText()

        # Check against expected output
        myMessage = ('Unexpected result returned for Earthquake Fatality '
                     'Function Expected: fatality count of '
                     '500 , received: \n %s' % myResult)
        assert format_int(500) in myResult, myMessage

        myMessage = ('Unexpected result returned for Earthquake Fatality '
                     'Function Expected: total population count of '
                     '31372262 , received: \n %s' % myResult)
        assert format_int(31372262) in myResult, myMessage

    def test_runTsunamiBuildingImpactFunction(self):
        """Tsunami function runs in GUI as expected."""

        # Push OK with the left mouse button

        myButton = DOCK.pbnRunStop

        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        myResult, myMessage = setupScenario(
            DOCK,
            theHazard='Tsunami Max Inundation',
            theExposure='Tsunami Building Exposure',
            theFunction='Be flooded',
            theFunctionId='Flood Building Impact Function')
        assert myResult, myMessage

        setCanvasCrs(GEOCRS, True)
        setBatemansBayGeoExtent()

        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.pageToText()

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
        assert format_int(17) in myResult, myMessage
        assert format_int(7) in myResult, myMessage

    def test_InsufficientOverlapIssue372(self):
        """Test Insufficient overlap errors are caught as per issue #372.
        ..note:: See https://github.com/AIFDR/inasafe/issues/372
        """

        # Push OK with the left mouse button
        myButton = DOCK.pbnRunStop

        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        myResult, myMessage = setupScenario(
            DOCK,
            theHazard='A flood in Jakarta like in 2007',
            theExposure='Penduduk Jakarta',
            theFunction='HKVtest',
            theFunctionId='HKVtest')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        # Zoom to an area where there is no overlap with layers
        myRect = QgsRectangle(106.635434302702, -6.101567666986,
                              106.635434302817, -6.101567666888)
        CANVAS.setExtent(myRect)

        # Press RUN
        DOCK.accept()
        myResult = DOCK.wvResults.pageToText()

        # Check for an error containing InsufficientOverlapError
        myExpectedString = 'InsufficientOverlapError'
        myMessage = 'Result not as expected %s not in: %s' % (
            myExpectedString, myResult)
        # This is the expected impact number
        self.assertIn(myExpectedString, myResult, myMessage)

    def test_runFloodPopulationImpactFunction(self):
        """Flood function runs in GUI with Jakarta data
           Raster on raster based function runs as expected."""

        # Push OK with the left mouse button
        myButton = DOCK.pbnRunStop

        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        myResult, myMessage = setupScenario(
            DOCK,
            theHazard='A flood in Jakarta like in 2007',
            theExposure='Penduduk Jakarta',
            theFunction='HKVtest',
            theFunctionId='HKVtest')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()

        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.pageToText()

        # Check that the number is as what was calculated by
        # Marco Hartman form HKV
        myMessage = 'Result not as expected: %s' % myResult
        # This is the expected impact number
        assert format_int(2480) in myResult, myMessage

    def test_runFloodPopulationImpactFunction_scaling(self):
        """Flood function runs in GUI with 5x5km population data
           Raster on raster based function runs as expected with scaling."""

        myResult, myMessage = setupScenario(
            DOCK,
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
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.pageToText()

        myMessage = 'Result not as expected: %s' % myResult

        # Check numbers are OK (within expected errors from resampling)
        # These are expected impact number
        assert format_int(10484) in myResult, myMessage
        assert format_int(977) in myResult, myMessage

    def test_runFloodPopulationPolygonHazardImpactFunction(self):
        """Flood function runs in GUI with Jakarta polygon flood hazard data.
           Uses population raster exposure layer"""

        myResult, myMessage = setupScenario(
            DOCK,
            theHazard='A flood in Jakarta',
            theExposure='Penduduk Jakarta',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function Vector Hazard')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()

        # Press RUN
        myButton = DOCK.pbnRunStop
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.pageToText()

        myMessage = 'Result not as expected: %s' % myResult
        # This is the expected number of people needing evacuation
        assert format_int(1349000) in myResult, myMessage

    def test_runCategorizedHazardBuildingImpact(self):
        """Flood function runs in GUI with Flood in Jakarta hazard data
            Uses DKI buildings exposure data."""

        myResult, myMessage = setupScenario(
            DOCK,
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
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.pageToText()

        print myResult
        myMessage = 'Result not as expected: %s' % myResult
        # This is the expected number of building might be affected
        assert format_int(535) in myResult, myMessage
        assert format_int(453) in myResult, myMessage
        assert format_int(436) in myResult, myMessage

    def test_runCategorisedHazardPopulationImpactFunction(self):
        """Flood function runs in GUI with Flood in Jakarta hazard data
            Uses Penduduk Jakarta as exposure data."""

        myResult, myMessage = setupScenario(
            DOCK,
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
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.pageToText()

        myMessage = 'Result not as expected: %s' % myResult
        # This is the expected number of population might be affected
        assert format_int(30938000) in myResult, myMessage
        assert format_int(68280000) in myResult, myMessage
        assert format_int(157551000) in myResult, myMessage

    #noinspection PyArgumentList
    def test_runEarthquakeBuildingImpactFunction(self):
        """Earthquake function runs in GUI with An earthquake in Yogyakarta
        like in 2006 hazard data uses OSM Building Polygons exposure data."""

        myResult, myMessage = setupScenario(
            DOCK,
            theHazard='An earthquake in Yogyakarta like in 2006',
            theExposure='OSM Building Polygons',
            theFunction='Be affected',
            theFunctionId='Earthquake Building Impact Function')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setGeoExtent([101, -12, 119, -4])

        # Press RUN
        myButton = DOCK.pbnRunStop
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.pageToText()
        LOGGER.debug(myResult)

        myMessage = 'Result not as expected: %s' % myResult
        # This is the expected number of building might be affected
        assert format_int(786) in myResult, myMessage
        assert format_int(15528) in myResult, myMessage
        assert format_int(177) in myResult, myMessage

    def test_runVolcanoBuildingImpact(self):
        """Volcano function runs in GUI with An donut (merapi hazard map)
         hazard data uses OSM Building Polygons exposure data."""

        myResult, myMessage = setupScenario(
            DOCK,
            theHazard='donut',
            theExposure='OSM Building Polygons',
            theFunction='Be affected',
            theFunctionId='Volcano Building Impact')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setGeoExtent([110.01, -7.81, 110.78, -7.50])

        # Press RUN
        myButton = DOCK.pbnRunStop
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.pageToText()
        LOGGER.debug(myResult)

        myMessage = 'Result not as expected: %s' % myResult
        # This is the expected number of building might be affected
        assert format_int(288) in myResult, myMessage

    def test_runVolcanoPopulationImpact(self):
        """Volcano function runs in GUI with a donut (merapi hazard map)
         hazard data uses population density grid."""

        myResult, myMessage = setupScenario(
            DOCK,
            theHazard='donut',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Volcano Polygon Hazard Population')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setGeoExtent([110.01, -7.81, 110.78, -7.50])

        # Press RUN
        myButton = DOCK.pbnRunStop
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.pageToText()
        LOGGER.debug(myResult)

        myMessage = 'Result not as expected: %s' % myResult
        # This is the expected number of people affected
        # Kategori	Jumlah	Kumulatif
        # Kawasan Rawan Bencana III	45.000	45.000
        # Kawasan Rawan Bencana II	84.000	129.000
        # Kawasan Rawan Bencana I	28.000	157.000

        # We could also get a memory error here so there are
        # two plausible outcomes:

        # Outcome 1: we ran out of memory
        if 'system does not have sufficient memory' in myResult:
            return
            # Outcome 2: It ran so check the results
        assert format_int(45) in myResult, myMessage
        assert format_int(84) in myResult, myMessage
        assert format_int(28) in myResult, myMessage

    def test_runVolcanoCirclePopulation(self):
        """Volcano function runs in GUI with a circular evacuation zone.

        Uses population density grid as exposure."""

        # NOTE: We assume radii in impact function to be 3, 5 and 10 km

        myResult, myMessage = setupScenario(
            DOCK,
            theHazard='Merapi Alert',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Volcano Polygon Hazard Population')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setGeoExtent([110.01, -7.81, 110.78, -7.50])

        # Press RUN
        myButton = DOCK.pbnRunStop

        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.pageToText()
        LOGGER.debug(myResult)

        myMessage = 'Result not as expected: %s' % myResult
        myMemoryString = 'not have sufficient memory'
        if myMemoryString in myResult:
            # Test host did not have enough memory to run the test
            # and user was given a nice message stating this
            return
            # This is the expected number of people affected
        # Jarak [km]	Jumlah	Kumulatif
        # 3	     15.000	15.000
        # 5	     17.000	32.000
        # 10	124.000	156.000
        assert format_int(15000) in myResult, myMessage
        assert format_int(17000) in myResult, myMessage
        assert format_int(124000) in myResult, myMessage

    # disabled this test until further coding
    def Xtest_printMap(self):
        """Test print map, especially on Windows."""

        myResult, myMessage = setupScenario(
            DOCK,
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
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        printButton = DOCK.pbnPrint

        try:
            # noinspection PyCallByClass,PyTypeChecker
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
            DOCK,
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()

        # Run manually so we can get the output layer
        DOCK._prepareAggregator()
        DOCK.aggregator.validateKeywords()
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
        assert myQgisImpactLayer.colorShadingAlgorithm() == QgsRasterLayer.\
            ColorRampShader, myMessage

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
            DOCK,
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
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.pageToText()

        myMessage = 'Result not as expected: %s' % myResult
        assert format_int(2366) in myResult, myMessage

    def test_issue45(self):
        """Points near the edge of a raster hazard layer are interpolated OK"""

        myButton = DOCK.pbnRunStop
        setCanvasCrs(GEOCRS, True)
        setYogyaGeoExtent()

        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        myResult, myMessage = setupScenario(
            DOCK,
            theHazard='An earthquake in Yogyakarta like in 2006',
            theExposure='OSM Building Polygons',
            theFunction='Earthquake Guidelines Function',
            theFunctionId='Earthquake Guidelines Function')
        assert myResult, myMessage

        # This is the where nosetest sometims hangs when running the
        # guitest suite (Issue #103)
        # The QTest.mouseClick call some times never returns when run
        # with nosetest, but OK when run normally.
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.pageToText()

        # Check that none of these  get a NaN value:
        self.assertIn('Unknown', myResult)

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
        myHazardLayerCount, myExposureLayerCount = loadLayers(
            myFileList, theDataDirectory=None)

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
        _, _ = loadLayers(myFileList, myClearFlag)
        # set exposure to : Population Density Estimate (5kmx5km)
        # noinspection PyCallByClass,PyTypeChecker
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Down)
        # noinspection PyCallByClass,PyTypeChecker
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Enter)
        myDict = getUiState(DOCK)
        myExpectedDict = {'Run Button Enabled': False,
                          'Impact Function Id': '',
                          'Impact Function Title': '',
                          'Hazard': 'A flood in Jakarta like in 2007',
                          'Exposure': 'Population density (5kmx5km)'}
        myMessage = (('Run button was not disabled when exposure set to \n%s'
                      '\nUI State: \n%s\nExpected State:\n%s\n%s') %
                     (DOCK.cboExposure.currentText(), myDict, myExpectedDict,
                      combosToString(DOCK)))

        assert myExpectedDict == myDict, myMessage

        # Now select again a valid layer and the run button
        # should be enabled
        # noinspection PyCallByClass,PyTypeChecker
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Up)
        # noinspection PyCallByClass,PyTypeChecker
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
        myHazardLayerCount, myExposureLayerCount = loadLayers(
            myFileList, theDataDirectory=None)

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
        _, _ = loadLayers(myFileList, myClearFlag)
        # set exposure to : Population density (5kmx5km)
        # noinspection PyTypeChecker,PyCallByClass
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Down)
        # noinspection PyTypeChecker,PyCallByClass
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Enter)
        myDict = getUiState(DOCK)
        myExpectedDict = {'Run Button Enabled': False,
                          'Impact Function Id': '',
                          'Impact Function Title': '',
                          'Hazard': 'A flood in Jakarta like in 2007',
                          'Exposure': 'Population density (5kmx5km)'}
        myMessage = ('Run button was not disabled when exposure set to \n%s'
                     '\nUI State: \n%s\nExpected State:\n%s\n%s') % \
                    (DOCK.cboExposure.currentText(), myDict, myExpectedDict,
                     combosToString(DOCK))

        assert myExpectedDict == myDict, myMessage

        # Now select again a valid layer and the run button
        # should be enabled
        # noinspection PyTypeChecker,PyCallByClass
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Up)
        # noinspection PyTypeChecker,PyCallByClass
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
        myHazardLayerCount, myExposureLayerCount = loadLayers(
            myFileList, theDataDirectory=TESTDATA)

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
        _, _ = loadLayers(myFileList, myClearFlag)

        myResult, myMessage = setupScenario(
            DOCK,
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
        # noinspection PyCallByClass,PyCallByClass,PyTypeChecker
        QTest.mouseClick(myButton, QtCore.Qt.LeftButton)
        myResult = DOCK.wvResults.pageToText()

        myMessage = 'Result not as expected: %s' % myResult
        assert format_int(68) in myResult, myMessage

    def test_state(self):
        """Check if the save/restore state methods work. See also
        https://github.com/AIFDR/inasafe/issues/58
        """
        # noinspection PyCallByClass,PyTypeChecker
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Up)
        # noinspection PyTypeChecker,PyCallByClass
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Enter)
        DOCK.saveState()
        myExpectedDict = getUiState(DOCK)
        #myState = DOCK.state
        # Now reset and restore and check that it gets the old state
        # Html is not considered in restore test since the ready
        # message overwrites it in dock implementation
        # noinspection PyTypeChecker,PyCallByClass
        QTest.keyClick(DOCK.cboExposure, QtCore.Qt.Key_Up)
        # noinspection PyTypeChecker,PyCallByClass
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
        myHazardLayerCount, myExposureLayerCount = loadLayers(
            myFileList, theDataDirectory=None)
        assert myHazardLayerCount == 2
        assert myExposureLayerCount == 1
        DOCK.cboHazard.setCurrentIndex(0)
        # noinspection PyTypeChecker,PyCallByClass
        QTest.keyClick(DOCK.cboFunction, QtCore.Qt.Key_Down)
        # noinspection PyTypeChecker,PyCallByClass
        QTest.keyClick(DOCK.cboFunction, QtCore.Qt.Key_Enter)
        myExpectedFunction = str(DOCK.cboFunction.currentText())
        # Now move down one hazard in the combo then verify
        # the function remains unchanged
        # noinspection PyTypeChecker,PyCallByClass
        QTest.keyClick(DOCK.cboHazard, QtCore.Qt.Key_Down)
        # noinspection PyTypeChecker,PyCallByClass
        QTest.keyClick(DOCK.cboHazard, QtCore.Qt.Key_Enter)
        myCurrentFunction = str(DOCK.cboFunction.currentText())
        myMessage = ('Expected selected impact function to remain unchanged '
                     'when choosing a different hazard of the same category:'
                     ' %s\nExpected: %s\n%s' % (myExpectedFunction,
                                                myCurrentFunction,
                                                combosToString(DOCK)))

        assert myExpectedFunction == myCurrentFunction, myMessage
        # noinspection PyTypeChecker,PyCallByClass
        QTest.keyClick(DOCK.cboHazard, QtCore.Qt.Key_Down)
        # noinspection PyTypeChecker,PyCallByClass
        QTest.keyClick(DOCK.cboHazard, QtCore.Qt.Key_Enter)
        # Selected function should remain the same
        myExpectation = 'Need evacuation'
        myFunction = DOCK.cboFunction.currentText()
        myMessage = 'Expected: %s, Got: %s' % (myExpectation, myFunction)
        assert myFunction == myExpectation, myMessage

    def test_fullRunResults(self):
        """Aggregation results are correct."""
        myRunButton = DOCK.pbnRunStop
        myExpectedResult = open(
            TEST_FILES_DIR +
            '/test-full-run-results.txt',
            'r').read()

        myResult, myMessage = setupScenario(
            DOCK,
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregationLayer='kabupaten jakarta singlepart',
            theAggregationEnabledFlag=True)
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        DOCK.runtimeKeywordsDialog.accept()

        myResult = DOCK.wvResults.pageToText()
        myMessage = ('The aggregation report should be:\n%s\n\nFound:\n\n%s' %
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
            DOCK,
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
            DOCK,
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
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        #        DOCK.runtimeKeywordsDialog.accept()
        myExpectedResult = """Error:
An exception occurred when calculating the results
Problem:
Exception : AHAHAH I got you
Click for Diagnostic Information:
"""
        myResult = DOCK.wvResults.pageToText()
        myMessage = ('The result message should be:\n%s\nFound:\n%s' %
                     (myExpectedResult, myResult))
        self.assertEqual(myExpectedResult, myResult, myMessage)

    def Xtest_runnerIsNone(self):
        """Test for none runner exceptions"""
        myRunButton = DOCK.pbnRunStop

        myResult, myMessage = setupScenario(
            DOCK,
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
        # noinspection PyCallByClass,PyTypeChecker
        QTest.mouseClick(myRunButton, QtCore.Qt.LeftButton)
        #        DOCK.runtimeKeywordsDialog.accept()
        myExpectedResult = """Error:
An exception occurred when calculating the results
Problem:
AttributeError : 'NoneType' object has no attribute 'keywords'
Click for Diagnostic Information:
"""
        myResult = DOCK.wvResults.pageToText()
        myMessage = ('The result message should be:\n%s\nFound:\n%s' %
                     (myExpectedResult, myResult))
        self.assertEqual(myExpectedResult, myResult, myMessage)

    def test_hasParametersButtonDisabled(self):
        """Function configuration button is disabled
        when layers not compatible."""
        setCanvasCrs(GEOCRS, True)
        #add additional layers
        #myResult, myMessage = setupScenario(
        #    heHazard='An earthquake in Yogyakarta like in 2006',
        #    theExposure = 'Essential Buildings',
        #    theFunction = 'Be damaged depending on building type',
        #    theFunctionId = 'ITB Earthquake Building Damage Function')
        setupScenario(
            DOCK,
            theHazard='An earthquake in Yogyakarta like in 2006',
            theExposure='Essential Buildings',
            theFunction='Be damaged depending on building type',
            theFunctionId='ITB Earthquake Building Damage Function')
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
            DOCK,
            theHazard='A flood in Jakarta like in 2007',
            theExposure='Penduduk Jakarta',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function')
        myToolButton = DOCK.toolFunctionOptions
        myFlag = myToolButton.isEnabled()
        assert myFlag, ('Expected configuration options '
                        'button to be enabled')

    # I disabled the test for now as checkMemory now returns None unless
    # there is a problem. TS
    def Xtest_extentsChanged(self):
        """Memory requirements are calculated correctly when extents change.
        """
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()
        setupScenario(
            DOCK,
            theHazard='A flood in Jakarta like in 2007',
            theExposure='Penduduk Jakarta',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function')
        myResult = DOCK.checkMemoryUsage()
        myMessage = 'Expected "3mb" to apear in : %s' % myResult
        assert myResult is not None, 'Check memory reported None'
        assert '3mb' in myResult, myMessage

    def test_cboAggregationEmptyProject(self):
        """Aggregation combo changes properly according on no loaded layers"""
        self.tearDown()
        myMessage = ('The aggregation combobox should have only the "Entire '
                     'area" item when the project has no layer. Found:'
                     ' %s' % (DOCK.cboAggregation.currentText()))

        self.assertEqual(DOCK.cboAggregation.currentText(), DOCK.tr(
            'Entire area'), myMessage)

        myMessage = ('The aggregation combobox should be disabled when the '
                     'project has no layer.')

        assert not DOCK.cboAggregation.isEnabled(), myMessage

    def test_cboAggregationToggle(self):
        """Aggregation Combobox toggles on and off as expected."""

        # With aggregation layer
        myResult, myMessage = setupScenario(
            DOCK,
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregationLayer='kabupaten jakarta singlepart',
            theAggregationEnabledFlag=True)
        myMessage += ' when an aggregation layer is defined.'
        assert myResult, myMessage

        # With no aggregation layer
        myLayer = DOCK.getAggregationLayer()
        myId = myLayer.id()
        QgsMapLayerRegistry.instance().removeMapLayer(myId)
        myResult, myMessage = setupScenario(
            DOCK,
            theHazard='A flood in Jakarta like in 2007',
            theExposure='People',
            theFunction='Need evacuation',
            theFunctionId='Flood Evacuation Function',
            theAggregationEnabledFlag=False)
        myMessage += ' when no aggregation layer is defined.'
        assert myResult, myMessage

if __name__ == '__main__':
    suite = unittest.makeSuite(DockTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
