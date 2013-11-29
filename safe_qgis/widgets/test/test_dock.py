# coding=utf-8
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
from os.path import join

from unittest import TestCase, skipIf
from PyQt4 import QtCore

from safe_qgis.safe_interface import temp_dir, unique_filename
from safe.common.testing import TESTDATA, BOUNDDATA

# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)
#for p in sys.path:
#    print p + '\n'
from qgis.core import (
    QgsVectorLayer,
    QgsMapLayerRegistry,
    QgsRectangle)
from safe_qgis.safe_interface import (
    format_int, HAZDATA, UNITDATA)

from safe_qgis.utilities.utilities_for_testing import (
    get_qgis_app,
    set_canvas_crs,
    set_padang_extent,
    set_batemans_bay_extent,
    set_jakarta_extent,
    set_yogya_extent,
    set_jakarta_google_extent,
    set_small_jakarta_extent,
    set_geo_extent,
    GEOCRS,
    GOOGLECRS,
    load_layer,
    load_standard_layers,
    populate_dock,
    combos_to_string,
    get_ui_state,
    setup_scenario,
    load_layers,
    canvas_list)

from safe_qgis.widgets.dock import Dock
from safe_qgis.utilities.styling import setRasterStyle
from safe_qgis.utilities.utilities import qgis_version, read_impact_layer


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

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
DOCK = Dock(IFACE)

YOGYA2006_title = 'An earthquake in Yogyakarta like in 2006'
PADANG2009_title = 'An earthquake in Padang like in 2009'

TEST_FILES_DIR = os.path.join(os.path.dirname(__file__),
                              '../../test/test_data/test_files')


#noinspection PyArgumentList
class TestDock(TestCase):
    """Test the InaSAFE GUI."""

    def setUp(self):
        """Fixture run before all tests"""
        os.environ['LANG'] = 'en'
        DOCK.show_only_visible_layers_flag = True
        load_standard_layers(DOCK)
        DOCK.cboHazard.setCurrentIndex(0)
        DOCK.cboExposure.setCurrentIndex(0)
        DOCK.cboFunction.setCurrentIndex(0)
        DOCK.run_in_thread_flag = False
        DOCK.show_only_visible_layers_flag = False
        DOCK.set_layer_from_title_flag = False
        DOCK.zoom_to_impact_flag = False
        DOCK.hide_exposure_flag = False
        DOCK.show_intermediate_layers = False

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
        populate_dock(DOCK)
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
        populate_dock(DOCK)
        myFlag = DOCK.validate()
        myMessage = ('Validation expected to pass on a ' +
                     'populated DOCK with selections.')
        assert myFlag, myMessage

    def test_runEarthQuakeGuidelinesFunction(self):
        """GUI runs with Shakemap 2009 and Padang Buildings"""

        # Push OK with the left mouse button
        set_canvas_crs(GEOCRS, True)
        set_padang_extent()

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard=PADANG2009_title,
            exposure='Padang WGS84',
            function='Earthquake Guidelines Function',
            function_id='Earthquake Guidelines Function')
        assert myResult, myMessage

        DOCK.accept()
        myResult = DOCK.wvResults.page_to_text()
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
        set_canvas_crs(GEOCRS, True)
        set_padang_extent()

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard=PADANG2009_title,
            exposure='People',
            function='Earthquake Fatality Function',
            function_id='Earthquake Fatality Function')
        assert myResult, myMessage

        DOCK.accept()

        myResult = DOCK.wvResults.page_to_text()

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
        set_canvas_crs(GEOCRS, True)
        set_geo_extent([96, -5, 105, 2])  # This covers all of the 2009 shaking
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
                     'found: ' + combos_to_string(DOCK))
        assert myIndex != -1, myMessage
        DOCK.cboFunction.setCurrentIndex(myIndex)

        myDict = get_ui_state(DOCK)
        myExpectedDict = {
            'Hazard': PADANG2009_title,
            'Exposure': 'People',
            'Impact Function Id': 'Earthquake Fatality Function',
            'Impact Function Title': 'Earthquake Fatality Function',
            'Run Button Enabled': True}
        myMessage = 'Got unexpected state: %s\nExpected: %s\n%s' % (
            myDict, myExpectedDict, combos_to_string(DOCK))
        assert myDict == myExpectedDict, myMessage

        DOCK.accept()

        myResult = DOCK.wvResults.page_to_text()

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

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='Tsunami Max Inundation',
            exposure='Tsunami Building Exposure',
            function='Be flooded',
            function_id='Flood Building Impact Function')
        assert myResult, myMessage

        set_canvas_crs(GEOCRS, True)
        set_batemans_bay_extent()

        # Press RUN
        DOCK.accept()
        myResult = DOCK.wvResults.page_to_text()

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

    def test_insufficientOverlapIssue372(self):
        """Test Insufficient overlap errors are caught as per issue #372.
        ..note:: See https://github.com/AIFDR/inasafe/issues/372
        """

        # Push OK with the left mouse button
        myButton = DOCK.pbnRunStop

        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='Penduduk Jakarta',
            function='HKVtest',
            function_id='HKVtest')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        # Zoom to an area where there is no overlap with layers
        myRect = QgsRectangle(106.635434302702, -6.101567666986,
                              106.635434302817, -6.101567666888)
        CANVAS.setExtent(myRect)

        # Press RUN
        DOCK.accept()
        myResult = DOCK.wvResults.page_to_text()

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

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='Penduduk Jakarta',
            function='HKVtest',
            function_id='HKVtest')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        # Press RUN
        DOCK.accept()
        myResult = DOCK.wvResults.page_to_text()

        # Check that the number is as what was calculated by
        # Marco Hartman form HKV
        myMessage = 'Result not as expected: %s' % myResult
        # This is the expected impact number
        assert format_int(2480) in myResult, myMessage

    def test_runFloodPopulationImpactFunction_scaling(self):
        """Flood function runs in GUI with 5x5km population data
           Raster on raster based function runs as expected with scaling."""

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        # Press RUN
        myButton = DOCK.pbnRunStop
        myButton.click()
        myResult = DOCK.wvResults.page_to_text()

        myMessage = 'Result not as expected: %s' % myResult

        # Check numbers are OK (within expected errors from resampling)
        # These are expected impact number
        assert format_int(10484) in myResult, myMessage
        assert format_int(977) in myResult, myMessage

    def test_runFloodPopulationPolygonHazardImpactFunction(self):
        """Flood function runs in GUI with Jakarta polygon flood hazard data.
           Uses population raster exposure layer"""

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta',
            exposure='Penduduk Jakarta',
            function='Need evacuation',
            function_id='Flood Evacuation Function Vector Hazard')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        # Press RUN
        DOCK.accept()
        myResult = DOCK.wvResults.page_to_text()

        myMessage = 'Result not as expected: %s' % myResult
        # This is the expected number of people needing evacuation
        assert format_int(1349000) in myResult, myMessage

    def test_runCategorizedHazardBuildingImpact(self):
        """Flood function runs in GUI with Flood in Jakarta hazard data
            Uses DKI buildings exposure data."""

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='Flood in Jakarta',
            exposure='Essential buildings',
            function='Be affected',
            function_id='Categorised Hazard Building Impact Function')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        # Press RUN
        DOCK.accept()
        myResult = DOCK.wvResults.page_to_text()

        myMessage = 'Result not as expected: %s' % myResult
        # This is the expected number of building might be affected
        assert format_int(535) in myResult, myMessage
        assert format_int(453) in myResult, myMessage
        assert format_int(436) in myResult, myMessage

    def test_runCategorisedHazardPopulationImpactFunction(self):
        """Flood function runs in GUI with Flood in Jakarta hazard data
            Uses Penduduk Jakarta as exposure data."""

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='Flood in Jakarta',
            exposure='Penduduk Jakarta',
            function='Be impacted',
            function_id='Categorised Hazard Population Impact Function')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        # Press RUN
        DOCK.accept()
        myResult = DOCK.wvResults.page_to_text()

        myMessage = 'Result not as expected: %s' % myResult
        # This is the expected number of population might be affected
        assert format_int(30938000) in myResult, myMessage
        assert format_int(68280000) in myResult, myMessage
        assert format_int(157551000) in myResult, myMessage

    #noinspection PyArgumentList
    def test_runEarthquakeBuildingImpactFunction(self):
        """Earthquake function runs in GUI with An earthquake in Yogyakarta
        like in 2006 hazard data uses OSM Building Polygons exposure data."""

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='An earthquake in Yogyakarta like in 2006',
            exposure='OSM Building Polygons',
            function='Be affected',
            function_id='Earthquake Building Impact Function')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_geo_extent([101, -12, 119, -4])

        # Press RUN
        DOCK.accept()
        myResult = DOCK.wvResults.page_to_text()
        LOGGER.debug(myResult)

        myMessage = 'Result not as expected: %s' % myResult
        # This is the expected number of building might be affected
        assert format_int(786) in myResult, myMessage
        assert format_int(15528) in myResult, myMessage
        assert format_int(177) in myResult, myMessage

    def test_runVolcanoBuildingImpact(self):
        """Volcano function runs in GUI with An donut (merapi hazard map)
         hazard data uses OSM Building Polygons exposure data."""

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='donut',
            exposure='OSM Building Polygons',
            function='Be affected',
            function_id='Volcano Building Impact')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_geo_extent([110.01, -7.81, 110.78, -7.50])

        # Press RUN
        DOCK.accept()
        myResult = DOCK.wvResults.page_to_text()
        LOGGER.debug(myResult)

        myMessage = 'Result not as expected: %s' % myResult
        # This is the expected number of building might be affected
        assert format_int(288) in myResult, myMessage

    def test_runVolcanoPopulationImpact(self):
        """Volcano function runs in GUI with a donut (merapi hazard map)
         hazard data uses population density grid."""

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='donut',
            exposure='People',
            function='Need evacuation',
            function_id='Volcano Polygon Hazard Population')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_geo_extent([110.01, -7.81, 110.78, -7.50])

        # Press RUN
        DOCK.accept()
        myResult = DOCK.wvResults.page_to_text()
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

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='Merapi Alert',
            exposure='People',
            function='Need evacuation',
            function_id='Volcano Polygon Hazard Population')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_geo_extent([110.01, -7.81, 110.78, -7.50])

        # Press RUN
        DOCK.accept()
        myResult = DOCK.wvResults.page_to_text()
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

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='Flood in Jakarta',
            exposure='Essential buildings',
            function='Be affected',
            function_id='Categorised Hazard Building Impact Function')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        # Press RUN
        myButton = DOCK.pbnRunStop
        # noinspection PyCallByClass,PyTypeChecker
        myButton.click()
        printButton = DOCK.pbnPrint

        try:
            # noinspection PyCallByClass,PyTypeChecker
            printButton.click()
        except OSError:
            LOGGER.debug('OSError')
            # pass
        except Exception, e:
            raise Exception('Exception is not expected, %s' % e)

    def test_resultStyling(self):
        """Test that ouputs from a model are correctly styled (colours and
        opacity. """

        # Push OK with the left mouse button

        print '--------------------'
        print combos_to_string(DOCK)

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        # Run manually so we can get the output layer
        DOCK.prepare_aggregator()
        DOCK.aggregator.validate_keywords()
        DOCK.setup_calculator()
        myRunner = DOCK.calculator.get_runner()
        myRunner.run()  # Run in same thread
        myEngineImpactLayer = myRunner.impact_layer()
        myQgisImpactLayer = read_impact_layer(myEngineImpactLayer)
        myStyle = myEngineImpactLayer.get_style_info()
        setRasterStyle(myQgisImpactLayer, myStyle)
        # simple test for now - we could test explicity for style state
        # later if needed.
        myMessage = ('Raster layer was not assigned a Singleband pseudocolor'
                     ' renderer as expected.')
        assert myQgisImpactLayer.renderer().type() == \
            'singlebandpseudocolor', myMessage

        # Commenting out because we changed impact function to use floating
        # point quantities. Revisit in QGIS 2.0 where range based transparency
        # will have been implemented
        #myMessage = ('Raster layer was not assigned transparency'
        #             'classes as expected.')
        #myTransparencyList = (myQgisImpactLayer.rasterTransparency().
        #        transparentSingleValuePixelList())
        #print "Transparency list:" + str(myTransparencyList)
        #assert (len(myTransparencyList) > 0)

    def test_issue47(self):
        """Issue47: Hazard & exposure data are in different proj to viewport.
        See https://github.com/AIFDR/inasafe/issues/47"""

        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='Penduduk Jakarta',
            function='HKVtest',
            function_id='HKVtest')
        assert result, message

        # Enable on-the-fly reprojection
        set_canvas_crs(GOOGLECRS, True)
        set_jakarta_google_extent()

        # Press RUN
        DOCK.accept()

        result = DOCK.wvResults.page_to_text()

        message = 'Result not as expected: %s' % result
        assert format_int(2366) in result, message

    @unittest.expectedFailure
    # FIXME (MB) check 306 and see what behaviour timlinux wants
    def test_issue306(self):
        """Issue306: CANVAS doesnt add generate layers in tests
        See https://github.com/AIFDR/inasafe/issues/306"""

        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='Penduduk Jakarta',
            function='HKVtest',
            function_id='HKVtest')
        assert result, message

        # Enable on-the-fly reprojection
        set_canvas_crs(GOOGLECRS, True)
        set_jakarta_google_extent()
        before_count = len(CANVAS.layers())

        # Press RUN
        DOCK.accept()

        # test issue #306
        after_count = len(CANVAS.layers())
        LOGGER.info("Canvas list after:\n%s" % canvas_list())
        message = ('Layer was not added to canvas (%s before, %s after)' % (
            before_count, after_count))
        assert before_count == after_count - 1, message

    def test_issue45(self):
        """Points near the edge of a raster hazard layer are interpolated."""

        myButton = DOCK.pbnRunStop
        set_canvas_crs(GEOCRS, True)
        set_yogya_extent()

        myMessage = 'Run button was not enabled'
        assert myButton.isEnabled(), myMessage

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='An earthquake in Yogyakarta like in 2006',
            exposure='OSM Building Polygons',
            function='Earthquake Guidelines Function',
            function_id='Earthquake Guidelines Function')
        assert myResult, myMessage

        # This is the where nosetest sometims hangs when running the
        # guitest suite (Issue #103)
        # The QTest.mouseClick call some times never returns when run
        # with nosetest, but OK when run normally.
        # noinspection PyCallByClass,PyTypeChecker
        DOCK.accept()
        myResult = DOCK.wvResults.page_to_text()

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

        myHazardLayerCount, myExposureLayerCount = load_standard_layers()
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

    def test_issue71(self):
        """Test issue #71 in github - cbo changes should update ok button."""
        # See https://github.com/AIFDR/inasafe/issues/71
        # Push OK with the left mouse button
        print 'Using QGIS: %s' % qgis_version()
        self.tearDown()
        myButton = DOCK.pbnRunStop
        # First part of scenario should have enabled run
        myFileList = [join(HAZDATA,
                           'Flood_Current_Depth_Jakarta_geographic.asc'),
                      join(TESTDATA,
                           'Population_Jakarta_geographic.asc')]
        myHazardLayerCount, myExposureLayerCount = load_layers(
            myFileList, data_directory=None)

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
        _, _ = load_layers(myFileList, myClearFlag)
        # set exposure to : Population Density Estimate (5kmx5km)
        # by moving one down
        DOCK.cboExposure.setCurrentIndex(DOCK.cboExposure.currentIndex() + 1)
        myDict = get_ui_state(DOCK)
        myExpectedDict = {'Run Button Enabled': False,
                          'Impact Function Id': '',
                          'Impact Function Title': '',
                          'Hazard': 'A flood in Jakarta like in 2007',
                          'Exposure': 'Population density (5kmx5km)'}
        myMessage = (('Run button was not disabled when exposure set to \n%s'
                      '\nUI State: \n%s\nExpected State:\n%s\n%s') %
                     (DOCK.cboExposure.currentText(), myDict, myExpectedDict,
                      combos_to_string(DOCK)))

        assert myExpectedDict == myDict, myMessage

        # Now select again a valid layer and the run button
        # should be enabled
        DOCK.cboExposure.setCurrentIndex(DOCK.cboExposure.currentIndex() - 1)
        myMessage = ('Run button was not enabled when exposure set to \n%s' %
                     DOCK.cboExposure.currentText())
        assert myButton.isEnabled(), myMessage

    def test_issue160(self):
        """Test that multipart features can be used in a scenario - issue #160
        """

        myExposure = os.path.join(UNITDATA, 'exposure',
                                  'buildings_osm_4326.shp')
        myHazard = os.path.join(UNITDATA, 'hazard',
                                'multipart_polygons_osm_4326.shp')
        # See https://github.com/AIFDR/inasafe/issues/71
        # Push OK with the left mouse button
        print 'Using QGIS: %s' % qgis_version()
        self.tearDown()
        myButton = DOCK.pbnRunStop
        # First part of scenario should have enabled run
        myFileList = [myHazard, myExposure]
        myHazardLayerCount, myExposureLayerCount = load_layers(myFileList)

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
        _, _ = load_layers(myFileList, myClearFlag)

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='multipart_polygons_osm_4326',
            exposure='buildings_osm_4326',
            function='Be flooded',
            function_id='Flood Building Impact Function')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        IFACE.mapCanvas().setExtent(
            QgsRectangle(106.788, -6.193, 106.853, -6.167))

        # Press RUN
        # noinspection PyCallByClass,PyCallByClass,PyTypeChecker
        DOCK.accept()
        myResult = DOCK.wvResults.page_to_text()

        myMessage = 'Result not as expected: %s' % myResult
        assert format_int(68) in myResult, myMessage

    def test_issue581(self):
        """Test issue #581 in github - Humanize can produce IndexError : list
        index out of range
        """
        # See https://github.com/AIFDR/inasafe/issues/581

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_small_jakarta_extent()
        # Press RUN
        DOCK.accept()
        myResult = DOCK.wvResults.page().currentFrame().toPlainText()

        myMessage = 'Result not as expected: %s' % myResult
        assert 'IndexError' not in myResult, myMessage
        assert 'It appears that no People are affected by A flood in ' \
               'Jakarta like in 2007. You may want to consider:' in myResult

    def test_state(self):
        """Check if the save/restore state methods work. See also
        https://github.com/AIFDR/inasafe/issues/58
        """
        DOCK.cboExposure.setCurrentIndex(DOCK.cboExposure.currentIndex() + 1)
        DOCK.save_state()
        myExpectedDict = get_ui_state(DOCK)
        #myState = DOCK.state
        # Now reset and restore and check that it gets the old state
        # Html is not considered in restore test since the ready
        # message overwrites it in dock implementation
        DOCK.cboExposure.setCurrentIndex(DOCK.cboExposure.currentIndex() + 1)
        DOCK.restore_state()
        myResultDict = get_ui_state(DOCK)
        myMessage = 'Got unexpected state: %s\nExpected: %s\n%s' % (
            myResultDict, myExpectedDict, combos_to_string(DOCK))
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
        myHazardLayerCount, myExposureLayerCount = load_layers(
            myFileList, data_directory=None)
        assert myHazardLayerCount == 2
        assert myExposureLayerCount == 1
        DOCK.cboFunction.setCurrentIndex(1)
        DOCK.cboHazard.setCurrentIndex(0)
        DOCK.cboExposure.setCurrentIndex(0)
        myExpectedFunction = str(DOCK.cboFunction.currentText())
        # Now move down one hazard in the combo then verify
        # the function remains unchanged
        DOCK.cboHazard.setCurrentIndex(1)
        myCurrentFunction = str(DOCK.cboFunction.currentText())
        myMessage = (
            'Expected selected impact function to remain unchanged when '
            'choosing a different hazard of the same category:'
            ' %s\nExpected: %s\n%s' % (
                myExpectedFunction, myCurrentFunction, combos_to_string(DOCK)))

        assert myExpectedFunction == myCurrentFunction, myMessage
        DOCK.cboHazard.setCurrentIndex(0)
        # Selected function should remain the same
        myExpectation = 'Need evacuation'
        myFunction = DOCK.cboFunction.currentText()
        myMessage = 'Expected: %s, Got: %s' % (myExpectation, myFunction)
        assert myFunction == myExpectation, myMessage

    def test_full_run_pyzstats(self):
        """Aggregation results correct using our own python zonal stats code.
        """
        myFileList = ['kabupaten_jakarta.shp']
        load_layers(myFileList, clear_flag=False, data_directory=BOUNDDATA)

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function',
            aggregation_layer='kabupaten jakarta',
            aggregation_enabled_flag=True)
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        DOCK.accept()

        myResult = DOCK.wvResults.page_to_text()

        myExpectedResult = open(
            TEST_FILES_DIR +
            '/test-full-run-results.txt',
            'r').readlines()
        myResult = myResult.replace(
            '</td> <td>', ' ').replace('</td><td>', ' ')
        for line in myExpectedResult:
            line = line.replace('\n', '')
            self.assertIn(line, myResult)

    @skipIf(sys.platform == 'win32', "Test cannot run on Windows")
    def test_full_run_qgszstats(self):
        """Aggregation results are correct using native QGIS zonal stats.

        .. note:: We know this is going to fail (hence the decorator) as
            QGIS1.8 zonal stats are broken. We expect this to pass when we
            have ported to the QGIS 2.0 api at which time we can remove the
            decorator. TS July 2013

        """

        # TODO check that the values are similar enough to the python stats
        myFileList = ['kabupaten_jakarta.shp']
        load_layers(myFileList, clear_flag=False, data_directory=BOUNDDATA)

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function',
            aggregation_layer='kabupaten jakarta',
            aggregation_enabled_flag=True)
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker

        # use QGIS zonal stats only in the test
        useNativeZonalStatsFlag = bool(QtCore.QSettings().value(
            'inasafe/use_native_zonal_stats', False))
        QtCore.QSettings().setValue('inasafe/use_native_zonal_stats', True)
        DOCK.accept()
        QtCore.QSettings().setValue('inasafe/use_native_zonal_stats',
                                    useNativeZonalStatsFlag)

        myResult = DOCK.wvResults.page_to_text()

        myExpectedResult = open(
            TEST_FILES_DIR +
            '/test-full-run-results-qgis.txt',
            'r').readlines()
        myResult = myResult.replace(
            '</td> <td>', ' ').replace('</td><td>', ' ')
        for line in myExpectedResult:
            line = line.replace('\n', '')
            self.assertIn(line, myResult)

    def test_layerChanged(self):
        """Test the metadata is updated as the user highlights different
        QGIS layers. For inasafe outputs, the table of results should be shown
        See also
        https://github.com/AIFDR/inasafe/issues/58
        """
        myLayer, myType = load_layer('issue58.tif')
        myMessage = ('Unexpected category for issue58.tif.\nGot:'
                     ' %s\nExpected: undefined' % myType)

        assert myType == 'undefined', myMessage
        DOCK.layer_changed(myLayer)
        DOCK.save_state()
        myHtml = DOCK.state['report']
        myExpectedString = '4229'
        myMessage = "%s\nDoes not contain:\n%s" % (
            myHtml,
            myExpectedString)
        assert myExpectedString in myHtml, myMessage

    def test_newLayersShowInCanvas(self):
        """Check that when we add a layer we can see it in the canvas list."""
        LOGGER.info("Canvas list before:\n%s" % canvas_list())
        myBeforeCount = len(CANVAS.layers())
        myPath = join(TESTDATA, 'polygon_0.shp')
        myLayer = QgsVectorLayer(myPath, 'foo', 'ogr')
        QgsMapLayerRegistry.instance().addMapLayer(myLayer)
        myAfterCount = len(CANVAS.layers())
        LOGGER.info("Canvas list after:\n%s" % canvas_list())
        myMessage = ('Layer was not added to canvas (%s before, %s after)' %
                     (myBeforeCount, myAfterCount))
        assert myBeforeCount == myAfterCount - 1, myMessage
        QgsMapLayerRegistry.instance().removeMapLayer(myLayer.id())

    def test_issue317(self):
        """Points near the edge of a raster hazard layer are interpolated OK"""

        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()
        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='OSM Building Polygons',
            function='Be flooded',
            function_id='Flood Building Impact Function')
        DOCK.get_functions()
        assert myResult, myMessage

    def Xtest_runnerExceptions(self):
        """Test runner exceptions"""

        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Exception riser',
            function_id='Exception Raising Impact Function',
            aggregation_enabled_flag=True)
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        DOCK.accept()
        #        DOCK.runtime_keywords_dialog.accept()
        myExpectedResult = """Error:
An exception occurred when calculating the results
Problem:
Exception : AHAHAH I got you
Click for Diagnostic Information:
"""
        myResult = DOCK.wvResults.page_to_text()
        myMessage = ('The result message should be:\n%s\nFound:\n%s' %
                     (myExpectedResult, myResult))
        self.assertEqual(myExpectedResult, myResult, myMessage)

    def Xtest_runnerIsNone(self):
        """Test for none runner exceptions"""
        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='None returner',
            function_id='None Returning Impact Function',
            aggregation_enabled_flag=True)
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        DOCK.accept()
        #        DOCK.runtime_keywords_dialog.accept()
        myExpectedResult = """Error:
An exception occurred when calculating the results
Problem:
AttributeError : 'NoneType' object has no attribute 'keywords'
Click for Diagnostic Information:
"""
        myResult = DOCK.wvResults.page_to_text()
        myMessage = ('The result message should be:\n%s\nFound:\n%s' %
                     (myExpectedResult, myResult))
        self.assertEqual(myExpectedResult, myResult, myMessage)

    def test_hasParametersButtonDisabled(self):
        """Function configuration button is disabled
        when layers not compatible."""
        set_canvas_crs(GEOCRS, True)
        #add additional layers
        #myResult, myMessage = setupScenario(
        #    heHazard='An earthquake in Yogyakarta like in 2006',
        #    theExposure = 'Essential Buildings',
        #    theFunction = 'Be damaged depending on building type',
        #    theFunctionId = 'ITB Earthquake Building Damage Function')
        setup_scenario(
            DOCK,
            hazard='An earthquake in Yogyakarta like in 2006',
            exposure='Essential Buildings',
            function='Be damaged depending on building type',
            function_id='ITB Earthquake Building Damage Function')
        myToolButton = DOCK.toolFunctionOptions
        myFlag = myToolButton.isEnabled()
        assert not myFlag, ('Expected configuration options '
                            'button to be disabled')

    def test_hasParametersButtonEnabled(self):
        """Function configuration button is enabled when layers are compatible.
        """
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()
        setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='Penduduk Jakarta',
            function='Need evacuation',
            function_id='Flood Evacuation Function')
        myToolButton = DOCK.toolFunctionOptions
        myFlag = myToolButton.isEnabled()
        assert myFlag, 'Expected configuration options button to be enabled'

    # I disabled the test for now as checkMemory now returns None unless
    # there is a problem. TS
    def Xtest_extentsChanged(self):
        """Memory requirements are calculated correctly when extents change.
        """
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()
        setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='Penduduk Jakarta',
            function='Need evacuation',
            function_id='Flood Evacuation Function')
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
        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function',
            aggregation_layer='kabupaten jakarta singlepart',
            aggregation_enabled_flag=True)
        myMessage += ' when an aggregation layer is defined.'
        assert myResult, myMessage

        # With no aggregation layer
        myLayer = DOCK.get_aggregation_layer()
        myId = myLayer.id()
        QgsMapLayerRegistry.instance().removeMapLayer(myId)
        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function',
            aggregation_enabled_flag=False)
        myMessage += ' when no aggregation layer is defined.'
        assert myResult, myMessage

    def test_saveCurrentScenario(self):
        """Test saving Current scenario
        """
        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='Flood in Jakarta',
            exposure='Penduduk Jakarta',
            function='Be impacted',
            function_id='Categorised Hazard Population Impact Function')
        assert myResult, myMessage

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        # create unique file
        myScenarioFile = unique_filename(
            prefix='scenarioTest', suffix='.txt', dir=temp_dir('test'))
        DOCK.save_current_scenario(scenario_file_path=myScenarioFile)
        with open(myScenarioFile, 'rt') as f:
            data = f.readlines()
        myTitle = data[0][:-1]
        myExposure = data[1][:-1]
        myHazard = data[2][:-1]
        myFunction = data[3][:-1]
        myExtent = data[4][:-1]
        assert os.path.exists(myScenarioFile), \
            'File %s does not exist' % myScenarioFile
        assert myTitle == '[Flood in Jakarta]', 'Title is not the same'
        assert myExposure.startswith('exposure =') and myExposure.endswith(
            'Population_Jakarta_geographic.asc'), 'Exposure is not the same'
        assert myHazard.startswith('hazard =') and myHazard.endswith(
            'jakarta_flood_category_123.asc'), 'Hazard is not the same'
        assert myFunction == 'function = Categorised Hazard Population ' \
                             'Impact Function', 'Impact function is not same'
        myExpectedExtent = (
            'extent = 106.313333, -6.380000, 107.346667, -6.070000')
        self.assertEqual(myExpectedExtent, myExtent)

    def test_set_dock_title(self):
        """Test the dock title gets set properly."""
        DOCK.set_dock_title()
        self.assertIn('InaSAFE', str(DOCK.windowTitle()))

    def test_scenario_layer_paths(self):
        """Test we calculate the relative paths correctly when saving scenario.
        """
        myResult, myMessage = setup_scenario(
            DOCK,
            hazard='Flood in Jakarta',
            exposure='Penduduk Jakarta',
            function='Be impacted',
            function_id='Categorised Hazard Population Impact Function')
        assert myResult, myMessage
        fake_dir = os.path.dirname(TESTDATA)
        myScenarioFile = unique_filename(
            prefix='scenarioTest', suffix='.txt', dir=fake_dir)
        myExposureLayer = str(DOCK.get_exposure_layer().publicSource())
        myHazardLayer = str(DOCK.get_hazard_layer().publicSource())

        relative_exposure, relative_hazard = DOCK.scenario_layer_paths(
            myExposureLayer,
            myHazardLayer,
            myScenarioFile)

        if 'win32' in sys.platform:
            # windows
            self.assertEqual(
                'test\\Population_Jakarta_geographic.asc',
                relative_exposure)
            self.assertEqual(
                'hazard\\jakarta_flood_category_123.asc',
                relative_hazard)

        else:
            self.assertEqual(
                'test/Population_Jakarta_geographic.asc',
                relative_exposure)
            self.assertEqual(
                'hazard/jakarta_flood_category_123.asc',
                relative_hazard)

if __name__ == '__main__':
    suite = unittest.makeSuite(TestDock)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
