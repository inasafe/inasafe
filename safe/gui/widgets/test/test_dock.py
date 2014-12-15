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
from safe.utilities.gis import qgis_version

__author__ = 'tim@kartoza.com'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import unittest
import sys
import os
import logging
from os.path import join
from unittest import TestCase, skipIf

# this import required to enable PyQt API v2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611
from qgis.core import (
    QgsVectorLayer,
    QgsMapLayerRegistry,
    QgsRectangle,
    QgsCoordinateReferenceSystem)
# noinspection PyPackageRequirements
from PyQt4 import QtCore

from safe.common.testing import TESTDATA, BOUNDDATA, get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.common.utilities import format_int
from safe.common.testing import HAZDATA, UNITDATA
from safe.gui.widgets.dock import Dock
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.styling import setRasterStyle
from safe.utilities.gis import read_impact_layer
from safe.utilities.utilities_for_testing import (
    load_standard_layers,
    setup_scenario,
    set_canvas_crs,
    combos_to_string,
    populate_dock,
    canvas_list,
    GEOCRS,
    GOOGLECRS,
    load_layer,
    load_layers,
    set_jakarta_extent,
    set_jakarta_google_extent,
    set_yogya_extent,
    get_ui_state,
    set_small_jakarta_extent)

# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

LOGGER = logging.getLogger('InaSAFE')
DOCK = Dock(IFACE)

YOGYA2006_title = 'An earthquake in Yogyakarta like in 2006'
PADANG2009_title = 'An earthquake in Padang like in 2009'

TEST_FILES_DIR = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'test',
    'test_data',
    'test_files')


# noinspection PyArgumentList
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
        DOCK.user_extent = None
        DOCK.user_extent_crs = None

    def tearDown(self):
        """Fixture run after each test"""
        QgsMapLayerRegistry.instance().removeAllMapLayers()
        DOCK.cboHazard.clear()
        DOCK.cboExposure.clear()
        # DOCK.cboAggregation.clear() #dont do this because the cboAggregation
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

    def test_insufficient_overlap(self):
        """Test Insufficient overlap errors are caught.

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
            function='Need evacuation',
            function_id='Flood Evacuation Function')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        # Zoom to an area where there is no overlap with layers
        rectangle = QgsRectangle(
            106.635434302702, -6.101567666986,
            106.635434302817, -6.101567666888)
        CANVAS.setExtent(rectangle)
        crs = QgsCoordinateReferenceSystem('EPSG:4326')
        DOCK.define_user_analysis_extent(rectangle, crs)

        # Press RUN
        DOCK.accept()
        result = DOCK.wvResults.page_to_text()

        # Check for an error containing InsufficientOverlapError
        expected_string = 'InsufficientOverlapError'
        message = 'Result not as expected %s not in: %s' % (
            expected_string, result)
        # This is the expected impact number
        self.assertIn(expected_string, result, message)

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
        set_jakarta_extent(DOCK)

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
        set_jakarta_extent(DOCK)

        DOCK.accept()
        # DOCK.analysis.get_impact_layer()
        safe_layer = DOCK.analysis.get_impact_layer()
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
        # message = ('Raster layer was not assigned transparency'
        #             'classes as expected.')
        # myTransparencyList = (qgis_layer.rasterTransparency().
        #        transparentSingleValuePixelList())
        # print "Transparency list:" + str(myTransparencyList)
        # assert (len(myTransparencyList) > 0)

    def test_issue47(self):
        """Issue47: Hazard & exposure data are in different proj to viewport.
        See https://github.com/AIFDR/inasafe/issues/47"""

        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='Penduduk Jakarta',
            function='Need evacuation',
            function_id='Flood Evacuation Function')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GOOGLECRS, True)
        set_jakarta_google_extent(DOCK)

        # Press RUN
        DOCK.accept()

        result = DOCK.wvResults.page_to_text()

        message = 'Result not as expected: %s' % result
        self.assertTrue(format_int(35793) in result, message)

    def test_issue306(self):
        """Issue306: CANVAS doesnt add generated layers in tests.

        See https://github.com/AIFDR/inasafe/issues/306"""

        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='Penduduk Jakarta',
            function='Need evacuation',
            function_id='Flood Evacuation Function')
        self.assertTrue(result, message)
        LOGGER.info("Canvas list before:\n%s" % canvas_list())
        # Enable on-the-fly reprojection
        set_canvas_crs(GOOGLECRS, True)
        set_jakarta_google_extent(DOCK)
        before_count = len(CANVAS.layers())
        # print 'Before count %s' % before_count

        # Press RUN
        DOCK.accept()

        # test issue #306
        after_count = len(CANVAS.layers())
        LOGGER.info("Canvas list after:\n%s" % canvas_list())
        message = ('Layer was not added to canvas (%s before, %s after)' % (
            before_count, after_count))
        # print 'After count %s' % after_count
        self.assertTrue(before_count == after_count - 1, message)

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
        # set exposure to : Population Count (5kmx5km)
        # by moving one down
        DOCK.cboExposure.setCurrentIndex(DOCK.cboExposure.currentIndex() + 1)
        actual_dict = get_ui_state(DOCK)
        expected_dict = {
            'Run Button Enabled': False,
            'Impact Function Id': '',
            'Impact Function Title': '',
            'Hazard': 'A flood in Jakarta like in 2007',
            'Exposure': 'Population Count (5kmx5km)'}
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
        # print 'Using QGIS: %s' % qgis_version()
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
        set_small_jakarta_extent(DOCK)
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
        # myState = DOCK.state
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
        DOCK.cboFunction.setCurrentIndex(0)
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
        set_jakarta_extent(DOCK)
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
        set_jakarta_extent(DOCK)
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
        set_jakarta_extent(DOCK)
        result, message = setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='OSM Building Polygons',
            function='Be flooded',
            function_id='Flood Building Impact Function')
        DOCK.get_functions()
        self.assertTrue(result, message)

    def test_has_parameters_button_disabled(self):
        """Function configuration button is disabled when layers not
        compatible."""
        set_canvas_crs(GEOCRS, True)
        setup_scenario(
            DOCK,
            hazard='An earthquake in Yogyakarta like in 2006',
            exposure='roads Maumere',
            function='',
            function_id='')
        tool_button = DOCK.toolFunctionOptions
        flag = tool_button.isEnabled()
        self.assertTrue(
            not flag,
            'Expected configuration options button to be disabled')

    def test_has_parameters_button_enabled(self):
        """Function configuration button is enabled when layers are compatible.
        """
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent(DOCK)
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
        set_jakarta_extent(DOCK)
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

        DOCK.extent.show_rubber_bands = True
        expected_vertex_count = 5

        # 4326 with enabled on-the-fly reprojection - check next
        set_canvas_crs(GEOCRS, True)
        set_small_jakarta_extent(DOCK)
        DOCK.show_next_analysis_extent()
        next_band = DOCK.extent.next_analysis_rubberband
        self.assertEqual(expected_vertex_count, next_band.numberOfVertices())

        # 4326 with disabled on-the-fly reprojection - check next
        set_canvas_crs(GEOCRS, False)
        set_small_jakarta_extent(DOCK)
        DOCK.show_next_analysis_extent()
        next_band = DOCK.extent.next_analysis_rubberband
        self.assertEqual(expected_vertex_count, next_band.numberOfVertices())

        # 900913 with enabled on-the-fly reprojection - check next
        set_canvas_crs(GOOGLECRS, True)
        set_jakarta_google_extent(DOCK)
        next_band = DOCK.extent.next_analysis_rubberband
        self.assertEqual(expected_vertex_count, next_band.numberOfVertices())

        # 900913 with enabled on-the-fly reprojection - check last
        set_canvas_crs(GOOGLECRS, True)
        set_jakarta_google_extent(DOCK)
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        DOCK.accept()
        # DOCK.show_extent()
        last_band = DOCK.extent.last_analysis_rubberband
        geometry = last_band.asGeometry().exportToWkt()
        expected_wkt = (
            'LINESTRING(11876228.33329810947179794 -695807.82839082507416606, '
            '11908350.67106631398200989 -695807.82839082507416606, '
            '11908350.67106631398200989 -678083.54461829655338079, '
            '11876228.33329810947179794 -678083.54461829655338079, '
            '11876228.33329810947179794 -695807.82839082507416606)')
        self.assertEqual(geometry, expected_wkt)
        self.assertEqual(
            expected_vertex_count,
            last_band.numberOfVertices()
        )

    def test_user_defined_extent(self):
        """Test that analysis honours user defined extents.

        Note that when testing on a desktop system this will overwrite your
        user defined analysis extent.

        """

        settings = QtCore.QSettings()
        extents = '106.772279, -6.237576, 106.885165, -6.165415'
        settings.setValue('inasafe/analysis_extent', extents)
        settings.setValue('inasafe/analysis_extent_crs', 'EPSG:4326')
        DOCK.read_settings()

        setup_scenario(
            DOCK,
            hazard='A flood in Jakarta like in 2007',
            exposure='People',
            function='Need evacuation',
            function_id='Flood Evacuation Function',
            aggregation_layer='kabupaten jakarta singlepart',
            aggregation_enabled_flag=True)

        DOCK.extent.show_rubber_bands = True
        expected_vertex_count = 5

        # 4326 with disabled on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        # User extent should override this
        set_small_jakarta_extent(DOCK)
        DOCK.extent.show_user_analysis_extent()
        user_band = DOCK.extent.user_analysis_rubberband
        self.assertEqual(expected_vertex_count, user_band.numberOfVertices())

    def test_issue1191(self):
        """Test setting a layer's title in the kw directly from qgis api"""
        DOCK.set_layer_from_title_flag = True
        set_canvas_crs(GEOCRS, True)
        set_yogya_extent(DOCK)

        result, message = setup_scenario(
            DOCK,
            hazard='An earthquake in Yogyakarta like in 2006',
            exposure='OSM Building Polygons',
            function='Be affected',
            function_id='Earthquake Building Impact Function')
        self.assertTrue(result, message)

        layer = DOCK.get_hazard_layer()
        keyword_io = KeywordIO()

        original_title = 'An earthquake in Yogyakarta like in 2006'
        title = keyword_io.read_keywords(layer, 'title')
        self.assertEqual(title, original_title)

        # change layer name as if done in the legend
        expected_title = 'TEST'
        layer.setLayerName(expected_title)
        title = keyword_io.read_keywords(layer, 'title')
        self.assertEqual(title, expected_title)

        # reset KW file to original state
        layer.setLayerName(original_title)
        title = keyword_io.read_keywords(layer, 'title')
        self.assertEqual(title, original_title)
        DOCK.set_layer_from_title_flag = False


if __name__ == '__main__':
    suite = unittest.makeSuite(TestDock)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
