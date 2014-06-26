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

# this import required to enable PyQt API v2 - DO NOT REMOVE!
#noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611

import unittest
import sys
import os
import logging
from os.path import join

# this import required to enable PyQt API v2
import qgis  # pylint: disable=W0611

from unittest import TestCase, skipIf
# noinspection PyPackageRequirements
from PyQt4 import QtCore

from safe.common.testing import TESTDATA, BOUNDDATA, get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

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
        print combos_to_string(DOCK)
        self.assertEqual(DOCK.cboHazard.currentIndex(), 0)
        self.assertEqual(DOCK.cboExposure.currentIndex(), 0)
        self.assertEqual(DOCK.cboFunction.currentIndex(), 0)
        self.assertEqual(DOCK.cboAggregation.currentIndex(), 0)

    def test_validate(self):
        """Validate function work as expected"""
        self.tearDown()
        # First check that we DONT validate a clear DOCK
        flag, message = DOCK.validate()
        self.assertTrue(message is not None, 'No reason for failure given')

        message = 'Validation expected to fail on a cleared DOCK.'
        self.assertEquals(flag, False, message)

        # Now check we DO validate a populated DOCK
        populate_dock(DOCK)
        flag = DOCK.validate()
        message = (
            'Validation expected to pass on a populated dock with selections.')
        self.assertTrue(flag, message)

    def test_set_ok_button_status(self):
        """OK button changes properly according to DOCK validity"""
        # First check that we ok ISNT enabled on a clear DOCK
        self.tearDown()
        flag, message = DOCK.validate()

        self.assertTrue(message is not None, 'No reason for failure given')
        message = 'Validation expected to fail on a cleared DOCK.'
        self.assertEquals(flag, False, message)

        # Now check OK IS enabled on a populated DOCK
        populate_dock(DOCK)
        flag = DOCK.validate()
        message = (
            'Validation expected to pass on a populated DOCK with selections.')
        self.assertTrue(flag, message)

    def test_run_earthquake_guidelines_function(self):
        """GUI runs with Shakemap 2009 and Padang Buildings"""

        # Push OK with the left mouse button
        set_canvas_crs(GEOCRS, True)
        set_padang_extent()

        result, message = setup_scenario(
            DOCK,
            hazard=PADANG2009_title,
            exposure='Padang WGS84',
            function='Earthquake Guidelines Function',
            function_id='Earthquake Guidelines Function')
        self.assertTrue(result, message)

        DOCK.accept()
        result = DOCK.wvResults.page_to_text()
        # Expected output:
        #Buildings    Total
        #All:    3160
        #Low damage (10-25%):    0
        #Medium damage (25-50%):    0
        #Pre merge of clip on steroids branch:
        #High damage (50-100%):    3160
        # Post merge of clip on steoids branch:
        #High damage (50-100%):    2993
        message = (
            'Unexpected result returned for Earthquake guidelines'
            'function. Expected:\n "All" count of 2993, '
            'received: \n %s' % result)
        self.assertTrue(format_int(2993) in result, message)

    def test_run_earthquake_fatality_function_small(self):
        """Padang 2009 fatalities estimated correctly (small extent)."""

        # Push OK with the left mouse button
        set_canvas_crs(GEOCRS, True)
        set_padang_extent()

        result, message = setup_scenario(
            DOCK,
            hazard=PADANG2009_title,
            exposure='People',
            function='Earthquake Fatality Function',
            function_id='Earthquake Fatality Function')
        self.assertTrue(result, message)

        DOCK.accept()

        result = DOCK.wvResults.page_to_text()

        # Check against expected output
        message = (
            'Unexpected result returned for Earthquake Fatality '
            'Function Expected: fatality count of '
            '116 , received: \n %s' % result)
        self.assertTrue(format_int(116) in result, message)

        message = (
            'Unexpected result returned for Earthquake Fatality '
            'Function Expected: total population count of '
            '847596 , received: \n %s' % result)
        print format_int(847529), 'expect'
        self.assertTrue(format_int(847596) in result, message)

    def test_run_earthquake_fatality_function_padang_full(self):
        """Padang 2009 fatalities estimated correctly (large extent)"""

        # Push OK with the left mouse button

        button = DOCK.pbnRunStop
        set_canvas_crs(GEOCRS, True)
        set_geo_extent([96, -5, 105, 2])  # This covers all of the 2009 shaking
        message = 'Run button was not enabled'
        self.assertTrue(button.isEnabled(), message)

        # Hazard layers
        index = DOCK.cboHazard.findText(PADANG2009_title)
        self.assertTrue(
            index != -1, 'Padang 2009 scenario hazard layer not found')
        DOCK.cboHazard.setCurrentIndex(index)

        # Exposure layers
        index = DOCK.cboExposure.findText('People')
        self.assertTrue(index != -1, 'People')
        DOCK.cboExposure.setCurrentIndex(index)

        # Choose impact function
        index = DOCK.cboFunction.findText('Earthquake Fatality Function')
        message = (
            'Earthquake Fatality Function not '
            'found: ' + combos_to_string(DOCK))
        self.assertTrue(index != -1, message)
        DOCK.cboFunction.setCurrentIndex(index)

        actual_dict = get_ui_state(DOCK)
        expected_dict = {
            'Hazard': PADANG2009_title,
            'Exposure': 'People',
            'Impact Function Id': 'Earthquake Fatality Function',
            'Impact Function Title': 'Earthquake Fatality Function',
            'Run Button Enabled': True}
        message = 'Got unexpected state: %s\nExpected: %s\n%s' % (
            actual_dict, expected_dict, combos_to_string(DOCK))
        self.assertTrue(actual_dict == expected_dict, message)

        DOCK.accept()

        result = DOCK.wvResults.page_to_text()

        # Check against expected output
        message = (
            'Unexpected result returned for Earthquake Fatality '
            'Function Expected: fatality count of '
            '500 , received: \n %s' % result)
        self.assertTrue(format_int(500) in result, message)

        message = (
            'Unexpected result returned for Earthquake Fatality '
            'Function Expected: total population count of '
            '31374747 , received: \n %s' % result)
        self.assertTrue(format_int(31374747) in result, message)

    def test_run_tsunami_building_impact_function(self):
        """Tsunami function runs in GUI as expected."""

        # Push OK with the left mouse button

        button = DOCK.pbnRunStop

        message = 'Run button was not enabled'
        self.assertTrue(button.isEnabled(), message)

        result, message = setup_scenario(
            DOCK,
            hazard='Tsunami Max Inundation',
            exposure='Tsunami Building Exposure',
            function='Be flooded',
            function_id='Flood Building Impact Function')
        self.assertTrue(result, message)

        set_canvas_crs(GEOCRS, True)
        set_batemans_bay_extent()

        # Press RUN
        DOCK.accept()
        result = DOCK.wvResults.page_to_text()

        #print result
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

        message = 'Result not as expected: %s' % result
        self.assertTrue(format_int(17) in result, message)
        self.assertTrue(format_int(7) in result, message)

    def test_insufficient_overlap_issue_372(self):
        """Test Insufficient overlap errors are caught as per issue #372.
        ..note:: See https://github.com/AIFDR/inasafe/issues/372
        """

        # Push OK with the left mouse button
        button = DOCK.pbnRunStop

        message = 'Run button was not enabled'
        self.assertTrue(button.isEnabled(), message)

        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='Penduduk Jakarta',
            function='HKVtest',
            function_id='HKVtest')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        # Zoom to an area where there is no overlap with layers
        rectangle = QgsRectangle(
            106.635434302702, -6.101567666986,
            106.635434302817, -6.101567666888)
        CANVAS.setExtent(rectangle)

        # Press RUN
        DOCK.accept()
        result = DOCK.wvResults.page_to_text()

        # Check for an error containing InsufficientOverlapError
        expected_string = 'InsufficientOverlapError'
        message = 'Result not as expected %s not in: %s' % (
            expected_string, result)
        # This is the expected impact number
        self.assertIn(expected_string, result, message)

    def test_run_flood_population_impact_function(self):
        """Flood function runs in GUI with Jakarta data
           Raster on raster based function runs as expected."""

        # Push OK with the left mouse button
        button = DOCK.pbnRunStop

        message = 'Run button was not enabled'
        self.assertTrue(button.isEnabled(), message)

        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='Penduduk Jakarta',
            function='HKVtest',
            function_id='HKVtest')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        # Press RUN
        DOCK.accept()
        result = DOCK.wvResults.page_to_text()

        # Check that the number is as what was calculated by
        # Marco Hartman form HKV
        message = 'Result not as expected: %s' % result
        # This is the expected impact number
        self.assertTrue(format_int(2480) in result, message)

    def test_run_flood_population_impact_function_scaling(self):
        """Flood function runs in GUI with 5x5km population data
           Raster on raster based function runs as expected with scaling."""

        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        # Press RUN
        button = DOCK.pbnRunStop
        button.click()
        result = DOCK.wvResults.page_to_text()

        message = 'Result not as expected: %s' % result

        # Check numbers are OK (within expected errors from resampling)
        # These are expected impact number
        self.assertTrue(format_int(10473000) in result, message)
        self.assertTrue(format_int(978000) in result, message)

    def test_run_flood_population_polygon_hazard_impact_function(self):
        """Flood function runs in GUI with Jakarta polygon flood hazard data.
           Uses population raster exposure layer"""

        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta',
            exposure='Penduduk Jakarta',
            function='Need evacuation',
            function_id='Flood Evacuation Function Vector Hazard')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        # Press RUN
        DOCK.accept()
        result = DOCK.wvResults.page_to_text()

        message = 'Result not as expected: %s' % result
        # This is the expected number of people needing evacuation
        self.assertTrue(format_int(1349000) in result, message)

    def test_run_categorized_hazard_building_impact(self):
        """Flood function runs in GUI with Flood in Jakarta hazard data
            Uses DKI buildings exposure data."""

        result, message = setup_scenario(
            DOCK,
            hazard='Flood in Jakarta',
            exposure='Essential buildings',
            function='Be affected',
            function_id='Categorised Hazard Building Impact Function')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        # Press RUN
        DOCK.accept()
        result = DOCK.wvResults.page_to_text()

        message = 'Result not as expected: %s' % result
        # This is the expected number of building might be affected
        self.assertTrue(format_int(535) in result, message)
        self.assertTrue(format_int(453) in result, message)
        self.assertTrue(format_int(436) in result, message)

    def test_run_categorised_hazard_population_impact_function(self):
        """Flood function runs in GUI with Flood in Jakarta hazard data
            Uses Penduduk Jakarta as exposure data."""

        result, message = setup_scenario(
            DOCK,
            hazard='Flood in Jakarta',
            exposure='Penduduk Jakarta',
            function='Be impacted',
            function_id='Categorised Hazard Population Impact Function')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        # Press RUN
        DOCK.accept()
        result = DOCK.wvResults.page_to_text()

        message = ('Result not as expected: %s' % result)
        # This is the expected number of population might be affected
        self.assertTrue(format_int(30938000) in result, message)  # high
        #self.assertTrue(format_int(68280000) in result, message)
        #self.assertTrue(format_int(157551000) in result, message)
        # The 2 asserts above are not valid anymore after the fix we made to
        # CategorisedHazardPopulationImpactFunction
        # Look at the fix here:
        # (https://github.com/AIFDR/inasafe/commit/aa5b3d72145c031c91f4d101b830
        # 8228915c248d#diff-378093670f4ebd60b4487af9b7c2e164)
        # New Asserts
        self.assertTrue(format_int(0) in result, message)  # medium
        self.assertTrue(format_int(256769000) in result, message)  # low

    #noinspection PyArgumentList
    def test_run_earthquake_building_impact_function(self):
        """Earthquake function runs in GUI with An earthquake in Yogyakarta
        like in 2006 hazard data uses OSM Building Polygons exposure data."""

        result, message = setup_scenario(
            DOCK,
            hazard='An earthquake in Yogyakarta like in 2006',
            exposure='OSM Building Polygons',
            function='Be affected',
            function_id='Earthquake Building Impact Function')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_geo_extent([101, -12, 119, -4])

        # Press RUN
        DOCK.accept()
        result = DOCK.wvResults.page_to_text()
        LOGGER.debug(result)

        message = ('Result not as expected: %s' % result)
        # This is the expected number of building might be affected
        self.assertTrue(format_int(786) in result, message)
        self.assertTrue(format_int(15528) in result, message)
        self.assertTrue(format_int(177) in result, message)

    def test_run_volcano_building_impact(self):
        """Volcano function runs in GUI with An donut (merapi hazard map)
         hazard data uses OSM Building Polygons exposure data."""

        result, message = setup_scenario(
            DOCK,
            hazard='donut',
            exposure='OSM Building Polygons',
            function='Be affected',
            function_id='Volcano Building Impact')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_geo_extent([110.01, -7.81, 110.78, -7.50])

        # Press RUN
        DOCK.accept()
        result = DOCK.wvResults.page_to_text()
        LOGGER.debug(result)

        message = ('Result not as expected: %s' % result)
        # This is the expected number of building might be affected
        self.assertTrue(format_int(288) in result, message)

    def test_run_volcano_population_impact(self):
        """Volcano function runs in GUI with a donut (merapi hazard map)
         hazard data uses population density grid."""

        result, message = setup_scenario(
            DOCK,
            hazard='donut',
            exposure='People',
            function='Need evacuation',
            function_id='Volcano Polygon Hazard Population')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_geo_extent([110.01, -7.81, 110.78, -7.50])

        # Press RUN
        DOCK.accept()
        result = DOCK.wvResults.page_to_text()
        LOGGER.debug(result)

        message = ('Result not as expected: %s' % result)
        # This is the expected number of people affected
        # Kategori	Jumlah	Kumulatif
        # Kawasan Rawan Bencana III	45.000	45.000
        # Kawasan Rawan Bencana II	84.000	129.000
        # Kawasan Rawan Bencana I	28.000	157.000

        # We could also get a memory error here so there are
        # two plausible outcomes:

        # Outcome 1: we ran out of memory
        if 'system does not have sufficient memory' in result:
            return
            # Outcome 2: It ran so check the results
        self.assertTrue(format_int(45) in result, message)
        self.assertTrue(format_int(84) in result, message)
        self.assertTrue(format_int(28) in result, message)

    def test_run_volcano_circle_population(self):
        """Volcano function runs in GUI with a circular evacuation zone.

        Uses population density grid as exposure."""

        # NOTE: We assume radii in impact function to be 3, 5 and 10 km

        result, message = setup_scenario(
            DOCK,
            hazard='Merapi Alert',
            exposure='People',
            function='Need evacuation',
            function_id='Volcano Polygon Hazard Population')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_geo_extent([110.01, -7.81, 110.78, -7.50])

        # Press RUN
        DOCK.accept()
        result = DOCK.wvResults.page_to_text()
        LOGGER.debug(result)

        message = 'Result not as expected: %s' % result
        memory_string = 'not have sufficient memory'
        if memory_string in result:
            # Test host did not have enough memory to run the test
            # and user was given a nice message stating this
            return
            # This is the expected number of people affected
        # Jarak [km]	Jumlah	Kumulatif
        # 3	     15.000	15.000
        # 5	     17.000	32.000
        # 10	124.000	156.000
        self.assertTrue(format_int(15000) in result, message)
        self.assertTrue(format_int(17000) in result, message)
        self.assertTrue(format_int(124000) in result, message)

    # disabled this test until further coding
    def xtest_print_map(self):
        """Test print map, especially on Windows."""

        result, message = setup_scenario(
            DOCK,
            hazard='Flood in Jakarta',
            exposure='Essential buildings',
            function='Be affected',
            function_id='Categorised Hazard Building Impact Function')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        # Press RUN
        button = DOCK.pbnRunStop
        # noinspection PyCallByClass,PyTypeChecker
        button.click()
        print_button = DOCK.pbnPrint

        try:
            # noinspection PyCallByClass,PyTypeChecker
            print_button.click()
        except OSError:
            LOGGER.debug('OSError')
            # pass
        except Exception, e:
            raise Exception('Exception is not expected, %s' % e)

    def test_result_styling(self):
        """Test that ouputs from a model are correctly styled (colours and
        opacity. """

        # Push OK with the left mouse button

        print '--------------------'
        print combos_to_string(DOCK)

        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        # Run manually so we can get the output layer
        DOCK.clip_parameters = DOCK.get_clip_parameters()
        DOCK.prepare_aggregator()
        DOCK.aggregator.validate_keywords()
        DOCK.setup_calculator()
        test_runner = DOCK.calculator.get_runner()
        test_runner.run()  # Run in same thread
        safe_layer = test_runner.impact_layer()
        qgis_layer = read_impact_layer(safe_layer)
        style = safe_layer.get_style_info()
        setRasterStyle(qgis_layer, style)
        # simple test for now - we could test explicity for style state
        # later if needed.
        message = (
            'Raster layer was not assigned a Singleband pseudocolor'
            ' renderer as expected.')
        self.assertTrue(
            qgis_layer.renderer().type() == 'singlebandpseudocolor', message)

        # Commenting out because we changed impact function to use floating
        # point quantities. Revisit in QGIS 2.0 where range based transparency
        # will have been implemented
        #message = ('Raster layer was not assigned transparency'
        #             'classes as expected.')
        #myTransparencyList = (qgis_layer.rasterTransparency().
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
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GOOGLECRS, True)
        set_jakarta_google_extent()

        # Press RUN
        DOCK.accept()

        result = DOCK.wvResults.page_to_text()

        message = 'Result not as expected: %s' % result
        self.assertTrue(format_int(2366) in result, message)

    def test_issue306(self):
        """Issue306: CANVAS doesnt add generated layers in tests.

        See https://github.com/AIFDR/inasafe/issues/306"""

        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='Penduduk Jakarta',
            function='HKVtest',
            function_id='HKVtest')
        self.assertTrue(result, message)
        LOGGER.info("Canvas list before:\n%s" % canvas_list())
        # Enable on-the-fly reprojection
        set_canvas_crs(GOOGLECRS, True)
        set_jakarta_google_extent()
        before_count = len(CANVAS.layers())
        #print 'Before count %s' % before_count

        # Press RUN
        DOCK.accept()

        # test issue #306
        after_count = len(CANVAS.layers())
        LOGGER.info("Canvas list after:\n%s" % canvas_list())
        message = ('Layer was not added to canvas (%s before, %s after)' % (
            before_count, after_count))
        #print 'After count %s' % after_count
        self.assertTrue(before_count == after_count - 1, message)

    def test_issue45(self):
        """Points near the edge of a raster hazard layer are interpolated."""

        button = DOCK.pbnRunStop
        set_canvas_crs(GEOCRS, True)
        set_yogya_extent()

        message = 'Run button was not enabled'
        self.assertTrue(button.isEnabled(), message)

        result, message = setup_scenario(
            DOCK,
            hazard='An earthquake in Yogyakarta like in 2006',
            exposure='OSM Building Polygons',
            function='Earthquake Guidelines Function',
            function_id='Earthquake Guidelines Function')
        self.assertTrue(result, message)

        # This is the where nosetest sometims hangs when running the
        # guitest suite (Issue #103)
        # The QTest.mouseClick call some times never returns when run
        # with nosetest, but OK when run normally.
        # noinspection PyCallByClass,PyTypeChecker
        DOCK.accept()
        result = DOCK.wvResults.page_to_text()

        # Check that none of these  get a NaN value:
        self.assertIn('Unknown', result)

        message = (
            'Some buildings returned by Earthquake guidelines function '
            'had NaN values. Result: \n %s' % result)
        self.assertTrue('Unknown (NaN):	196' not in result, message)

        # FIXME (Ole): A more robust test would be to load the
        #              result layer and check that all buildings
        #              have values.
        #              Tim, how do we get the output filename?
        # ANSWER
        #DOCK.calculator.impactLayer()

    def test_load_layers(self):
        """Layers can be loaded and list widget was updated appropriately
        """

        hazard_layer_count, exposure_layer_count = load_standard_layers()
        message = 'Expect %s layer(s) in hazard list widget but got %s' % (
            hazard_layer_count, DOCK.cboHazard.count())
        # pylint: disable=W0106
        self.assertEqual(DOCK.cboHazard.count(),
                         hazard_layer_count), message
        message = 'Expect %s layer(s) in exposure list widget but got %s' % (
            exposure_layer_count, DOCK.cboExposure.count())
        self.assertEqual(DOCK.cboExposure.count(),
                         exposure_layer_count), message
        # pylint: disable=W0106

    def test_issue71(self):
        """Test issue #71 in github - cbo changes should update ok button."""
        # See https://github.com/AIFDR/inasafe/issues/71
        # Push OK with the left mouse button
        print 'Using QGIS: %s' % qgis_version()
        self.tearDown()
        button = DOCK.pbnRunStop
        # First part of scenario should have enabled run
        file_list = [
            join(HAZDATA, 'Flood_Current_Depth_Jakarta_geographic.asc'),
            join(TESTDATA, 'Population_Jakarta_geographic.asc')]
        hazard_layer_count, exposure_layer_count = load_layers(
            file_list, data_directory=None)

        message = (
            'Incorrect number of Hazard layers: expected 1 got %s'
            % hazard_layer_count)
        self.assertTrue(hazard_layer_count == 1, message)

        message = (
            'Incorrect number of Exposure layers: expected 1 got %s'
            % exposure_layer_count)
        self.assertTrue(exposure_layer_count == 1, message)

        message = 'Run button was not enabled'
        self.assertTrue(button.isEnabled(), message)

        # Second part of scenario - run disabled when adding invalid layer
        # and select it - run should be disabled
        file_list = ['issue71.tif']  # This layer has incorrect keywords
        clear_flag = False
        _, _ = load_layers(file_list, clear_flag)
        # set exposure to : Population Density Estimate (5kmx5km)
        # by moving one down
        DOCK.cboExposure.setCurrentIndex(DOCK.cboExposure.currentIndex() + 1)
        actual_dict = get_ui_state(DOCK)
        expected_dict = {
            'Run Button Enabled': False,
            'Impact Function Id': '',
            'Impact Function Title': '',
            'Hazard': 'A flood in Jakarta like in 2007',
            'Exposure': 'Population density (5kmx5km)'}
        message = ((
            'Run button was not disabled when exposure set to \n%s'
            '\nUI State: \n%s\nExpected State:\n%s\n%s') %
            (
                DOCK.cboExposure.currentText(),
                actual_dict,
                expected_dict,
                combos_to_string(DOCK)))

        self.assertTrue(expected_dict == actual_dict, message)

        # Now select again a valid layer and the run button
        # should be enabled
        DOCK.cboExposure.setCurrentIndex(DOCK.cboExposure.currentIndex() - 1)
        message = (
            'Run button was not enabled when exposure set to \n%s' %
            DOCK.cboExposure.currentText())
        self.assertTrue(button.isEnabled(), message)

    def test_issue160(self):
        """Test that multipart features can be used in a scenario - issue #160
        """

        exposure = os.path.join(
            UNITDATA, 'exposure', 'buildings_osm_4326.shp')
        hazard = os.path.join(
            UNITDATA, 'hazard', 'multipart_polygons_osm_4326.shp')
        # See https://github.com/AIFDR/inasafe/issues/71
        # Push OK with the left mouse button
        #print 'Using QGIS: %s' % qgis_version()
        self.tearDown()
        button = DOCK.pbnRunStop
        # First part of scenario should have enabled run
        file_list = [hazard, exposure]
        hazard_layer_count, exposure_layer_count = load_layers(file_list)

        message = (
            'Incorrect number of Hazard layers: expected 1 got %s'
            % hazard_layer_count)
        self.assertTrue(hazard_layer_count == 1, message)

        message = (
            'Incorrect number of Exposure layers: expected 1 got %s'
            % exposure_layer_count)
        self.assertTrue(exposure_layer_count == 1, message)

        message = 'Run button was not enabled'
        self.assertTrue(button.isEnabled(), message)

        # Second part of scenario - run disabled when adding invalid layer
        # and select it - run should be disabled
        file_list = ['issue71.tif']  # This layer has incorrect keywords
        clear_flag = False
        _, _ = load_layers(file_list, clear_flag)

        result, message = setup_scenario(
            DOCK,
            hazard='multipart_polygons_osm_4326',
            exposure='buildings_osm_4326',
            function='Be flooded',
            function_id='Flood Building Impact Function')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        IFACE.mapCanvas().setExtent(
            QgsRectangle(106.788, -6.193, 106.853, -6.167))

        # Press RUN
        # noinspection PyCallByClass,PyCallByClass,PyTypeChecker
        DOCK.accept()
        result = DOCK.wvResults.page_to_text()

        message = 'Result not as expected: %s' % result
        self.assertTrue(format_int(68) in result, message)

    def test_issue581(self):
        """Test issue #581 in github - Humanize can produce IndexError : list
        index out of range
        """
        # See https://github.com/AIFDR/inasafe/issues/581

        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_small_jakarta_extent()
        # Press RUN
        DOCK.accept()
        result = DOCK.wvResults.page().currentFrame().toPlainText()

        message = 'Result not as expected: %s' % result
        self.assertTrue('IndexError' not in result, message)
        self.assertTrue(
            'It appears that no People are affected by A flood in '
            'Jakarta like in 2007. You may want to consider:' in result)

    def test_state(self):
        """Check if the save/restore state methods work. See also
        https://github.com/AIFDR/inasafe/issues/58
        """
        DOCK.cboExposure.setCurrentIndex(DOCK.cboExposure.currentIndex() + 1)
        DOCK.save_state()
        expected_dict = get_ui_state(DOCK)
        #myState = DOCK.state
        # Now reset and restore and check that it gets the old state
        # Html is not considered in restore test since the ready
        # message overwrites it in dock implementation
        DOCK.cboExposure.setCurrentIndex(DOCK.cboExposure.currentIndex() + 1)
        DOCK.restore_state()
        result_dict = get_ui_state(DOCK)
        message = 'Got unexpected state: %s\nExpected: %s\n%s' % (
            result_dict, expected_dict, combos_to_string(DOCK))
        self.assertTrue(expected_dict == result_dict, message)

        # Corner case test when two layers can have the
        # same functions - when switching layers the selected function should
        # remain unchanged
        self.tearDown()
        file_list = [
            join(HAZDATA, 'Flood_Design_Depth_Jakarta_geographic.asc'),
            join(HAZDATA, 'Flood_Current_Depth_Jakarta_geographic.asc'),
            join(TESTDATA, 'Population_Jakarta_geographic.asc')]
        hazard_layer_count, exposure_layer_count = load_layers(
            file_list, data_directory=None)
        self.assertTrue(hazard_layer_count == 2)
        self.assertTrue(exposure_layer_count == 1)
        DOCK.cboFunction.setCurrentIndex(1)
        DOCK.cboHazard.setCurrentIndex(0)
        DOCK.cboExposure.setCurrentIndex(0)
        expected_function = str(DOCK.cboFunction.currentText())
        # Now move down one hazard in the combo then verify
        # the function remains unchanged
        DOCK.cboHazard.setCurrentIndex(1)
        current_function = str(DOCK.cboFunction.currentText())
        message = (
            'Expected selected impact function to remain unchanged when '
            'choosing a different hazard of the same category:'
            ' %s\nExpected: %s\n%s' % (
                expected_function, current_function, combos_to_string(DOCK)))

        self.assertTrue(expected_function == current_function, message)
        DOCK.cboHazard.setCurrentIndex(0)
        # Selected function should remain the same
        expected = 'Need evacuation'
        function = DOCK.cboFunction.currentText()
        message = 'Expected: %s, Got: %s' % (expected, function)
        self.assertTrue(function == expected, message)

    def test_full_run_pyzstats(self):
        """Aggregation results correct using our own python zonal stats code.
        """
        file_list = ['kabupaten_jakarta.shp']
        load_layers(file_list, clear_flag=False, data_directory=BOUNDDATA)

        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function',
            aggregation_layer='kabupaten jakarta',
            aggregation_enabled_flag=True)
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        DOCK.accept()

        result = DOCK.wvResults.page_to_text()

        expected_result = open(
            TEST_FILES_DIR +
            '/test-full-run-results.txt',
            'r').readlines()
        result = result.replace(
            '</td> <td>', ' ').replace('</td><td>', ' ')
        for line in expected_result:
            line = line.replace('\n', '')
            self.assertIn(line, result)

    @skipIf(sys.platform == 'win32', "Test cannot run on Windows")
    def test_full_run_qgszstats(self):
        """Aggregation results are correct using native QGIS zonal stats.

        .. note:: We know this is going to fail (hence the decorator) as
            QGIS1.8 zonal stats are broken. We expect this to pass when we
            have ported to the QGIS 2.0 api at which time we can remove the
            decorator. TS July 2013

        """

        # TODO check that the values are similar enough to the python stats
        file_list = ['kabupaten_jakarta.shp']
        load_layers(file_list, clear_flag=False, data_directory=BOUNDDATA)

        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function',
            aggregation_layer='kabupaten jakarta',
            aggregation_enabled_flag=True)
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker

        # use QGIS zonal stats only in the test
        qgis_zonal_flag = bool(QtCore.QSettings().value(
            'inasafe/use_native_zonal_stats', False, type=bool))
        QtCore.QSettings().setValue('inasafe/use_native_zonal_stats', True)
        DOCK.accept()
        QtCore.QSettings().setValue('inasafe/use_native_zonal_stats',
                                    qgis_zonal_flag)

        result = DOCK.wvResults.page_to_text()

        expected_result = open(
            TEST_FILES_DIR +
            '/test-full-run-results-qgis.txt', 'rb').readlines()
        result = result.replace(
            '</td> <td>', ' ').replace('</td><td>', ' ')
        for line in expected_result:
            line = line.replace('\n', '')
            self.assertIn(line, result)

    def test_layer_changed(self):
        """Test the metadata is updated as the user highlights different
        QGIS layers. For inasafe outputs, the table of results should be shown
        See also
        https://github.com/AIFDR/inasafe/issues/58
        """
        layer, layer_type = load_layer('issue58.tif')
        message = (
            'Unexpected category for issue58.tif.\nGot:'
            ' %s\nExpected: undefined' % layer_type)

        self.assertTrue(layer_type == 'undefined', message)
        DOCK.layer_changed(layer)
        DOCK.save_state()
        html = DOCK.state['report']
        expected = '4229'
        message = "%s\nDoes not contain:\n%s" % (
            html,
            expected)
        self.assertTrue(expected in html, message)

    def test_new_layers_show_in_canvas(self):
        """Check that when we add a layer we can see it in the canvas list."""
        LOGGER.info("Canvas list before:\n%s" % canvas_list())
        before_count = len(CANVAS.layers())
        layer_path = join(TESTDATA, 'polygon_0.shp')
        layer = QgsVectorLayer(layer_path, 'foo', 'ogr')
        QgsMapLayerRegistry.instance().addMapLayers([layer])
        after_count = len(CANVAS.layers())
        LOGGER.info("Canvas list after:\n%s" % canvas_list())
        message = (
            'Layer was not added to canvas (%s before, %s after)' %
            (before_count, after_count))
        self.assertTrue(before_count == after_count - 1, message)
        QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

    def test_issue317(self):
        """Points near the edge of a raster hazard layer are interpolated OK"""

        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()
        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='OSM Building Polygons',
            function='Be flooded',
            function_id='Flood Building Impact Function')
        DOCK.get_functions()
        self.assertTrue(result, message)

    def Xtest_runner_exceptions(self):
        """Test runner exceptions"""

        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Exception riser',
            function_id='Exception Raising Impact Function',
            aggregation_enabled_flag=True)
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        DOCK.accept()
        #        DOCK.runtime_keywords_dialog.accept()
        expected_result = """Error:
An exception occurred when calculating the results
Problem:
Exception : AHAHAH I got you
Click for Diagnostic Information:
"""
        result = DOCK.wvResults.page_to_text()
        message = (
            'The result message should be:\n%s\nFound:\n%s' %
            (expected_result, result))
        self.assertEqual(expected_result, result, message)

    def xtest_runner_is_none(self):
        """Test for none runner exceptions"""
        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='None returner',
            function_id='None Returning Impact Function',
            aggregation_enabled_flag=True)
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent()

        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        DOCK.accept()
        #        DOCK.runtime_keywords_dialog.accept()
        expected_result = """Error:
An exception occurred when calculating the results
Problem:
AttributeError : 'NoneType' object has no attribute 'keywords'
Click for Diagnostic Information:
"""
        result = DOCK.wvResults.page_to_text()
        message = (
            'The result message should be:\n%s\nFound:\n%s' %
            (expected_result, result))
        self.assertEqual(expected_result, result, message)

    def test_has_parameters_button_disabled(self):
        """Function configuration button is disabled
        when layers not compatible."""
        set_canvas_crs(GEOCRS, True)
        #add additional layers
        #result, message = setupScenario(
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
        tool_button = DOCK.toolFunctionOptions
        flag = tool_button.isEnabled()
        self.assertTrue(
            not flag,
            'Expected configuration options button to be disabled')

    def test_has_parameters_button_enabled(self):
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
        tool_button = DOCK.toolFunctionOptions
        flag = tool_button.isEnabled()
        self.assertTrue(
            flag,
            'Expected configuration options button to be enabled')

    # I disabled the test for now as checkMemory now returns None unless
    # there is a problem. TS
    def xtest_extents_changed(self):
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
        result = DOCK.checkMemoryUsage()
        message = 'Expected "3mb" to apear in : %s' % result
        self.assertTrue(result is not None, 'Check memory reported None')
        self.assertTrue('3mb' in result, message)

    def test_cbo_aggregation_empty_project(self):
        """Aggregation combo changes properly according on no loaded layers"""
        self.tearDown()
        message = (
            'The aggregation combobox should have only the "Entire '
            'area" item when the project has no layer. Found:'
            ' %s' % (DOCK.cboAggregation.currentText()))

        self.assertEqual(DOCK.cboAggregation.currentText(), DOCK.tr(
            'Entire area'), message)

        message = (
            'The aggregation combobox should be disabled when the '
            'project has no layer.')

        self.assertTrue(not DOCK.cboAggregation.isEnabled(), message)

    def test_cbo_aggregation_toggle(self):
        """Aggregation Combobox toggles on and off as expected."""

        # With aggregation layer
        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function',
            aggregation_layer='kabupaten jakarta singlepart',
            aggregation_enabled_flag=True)
        message += ' when an aggregation layer is defined.'
        self.assertTrue(result, message)

        # With no aggregation layer
        layer = DOCK.get_aggregation_layer()
        layer_id = layer.id()
        QgsMapLayerRegistry.instance().removeMapLayer(layer_id)
        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function',
            aggregation_enabled_flag=False)
        message += ' when no aggregation layer is defined.'
        self.assertTrue(result, message)

    def test_set_dock_title(self):
        """Test the dock title gets set properly."""
        DOCK.set_dock_title()
        self.assertIn('InaSAFE', str(DOCK.windowTitle()))

    def test_generate_insufficient_overlap_message(self):
        """Test we generate insufficent overlap messages nicely."""

        class FakeLayer(object):
            layer_source = None

            def source(self):
                return self.layer_source

        exposure_layer = FakeLayer()
        exposure_layer.layer_source = 'Fake exposure layer'

        hazard_layer = FakeLayer()
        hazard_layer.layer_source = 'Fake hazard layer'

        message = DOCK.generate_insufficient_overlap_message(
            Exception('Dummy exception'),
            exposure_geoextent=[10.0, 10.0, 20.0, 20.0],
            exposure_layer=exposure_layer,
            hazard_geoextent=[15.0, 15.0, 20.0, 20.0],
            hazard_layer=hazard_layer,
            viewport_geoextent=[5.0, 5.0, 12.0, 12.0])
        self.assertIn('insufficient overlap', message.to_text())

    def test_rubber_bands(self):
        """Test that the rubber bands get updated."""

        setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function',
            aggregation_layer='kabupaten jakarta singlepart',
            aggregation_enabled_flag=True)

        DOCK.show_rubber_bands = True
        expected_vertex_count = 5

        # 4326 with disabled on-the-fly reprojection - check next
        set_canvas_crs(GEOCRS, True)
        set_small_jakarta_extent()
        DOCK.show_next_analysis_extent()
        next_band = DOCK.next_analysis_rubberband
        self.assertEqual(expected_vertex_count, next_band.numberOfVertices())

        # 4326 with enabled on-the-fly reprojection - check next
        set_canvas_crs(GEOCRS, False)
        set_small_jakarta_extent()
        DOCK.show_next_analysis_extent()
        next_band = DOCK.next_analysis_rubberband
        self.assertEqual(expected_vertex_count, next_band.numberOfVertices())

        # 900913 with enabled on-the-fly reprojection - check next
        set_canvas_crs(GOOGLECRS, True)
        set_jakarta_google_extent()
        next_band = DOCK.next_analysis_rubberband
        self.assertEqual(expected_vertex_count, next_band.numberOfVertices())

        # 900913 with enabled on-the-fly reprojection - check last
        set_canvas_crs(GOOGLECRS, True)
        set_jakarta_google_extent()
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        DOCK.accept()
        #DOCK.show_extent()
        last_band = DOCK.last_analysis_rubberband
        geometry = last_band.asGeometry().exportToWkt()
        expected_wkt = (
            'LINESTRING(11876228.33329810947179794 -695798.00000000046566129, '
            '11908350.67106631398200989 -695798.00000000046566129, '
            '11908350.67106631398200989 -678083.54461829818319529, '
            '11876228.33329810947179794 -678083.54461829818319529, '
            '11876228.33329810947179794 -695798.00000000046566129)')
        self.assertEqual(geometry, expected_wkt)
        self.assertEqual(
            expected_vertex_count,
            last_band.numberOfVertices()
        )


if __name__ == '__main__':
    suite = unittest.makeSuite(TestDock)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
