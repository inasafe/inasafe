# coding=utf-8
"""Test Dock"""

import codecs
import logging
import os
import sys
import unittest
from os.path import join
from unittest import TestCase, skipIf

# this import required to enable PyQt API v2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from qgis.core import (
    QgsVectorLayer,
    QgsMapLayerRegistry,
    QgsRectangle,
    QgsCoordinateReferenceSystem,
    QgsProject)
from PyQt4 import QtCore

from safe.test.utilities import get_qgis_app, get_dock

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
from safe.definitionsv4.constants import (
    HAZARD_EXPOSURE_VIEW, HAZARD_EXPOSURE, HAZARD_EXPOSURE_BOUNDINGBOX)
from safe.common.utilities import format_int, unique_filename
from safe.utilities.qgis_utilities import add_above_layer, layer_legend_index
from safe.test.utilities import (
    standard_data_path,
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
    set_small_jakarta_extent,
    TESTDATA,
    clone_shp_layer)

from safe.utilities.keyword_io import KeywordIO
from safe.utilities.styling import setRasterStyle

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


# noinspection PyArgumentList
class TestDock(TestCase):
    """Test the InaSAFE GUI."""

    @classmethod
    def setUpClass(cls):
        cls.dock = get_dock()

    def setUp(self):
        """Fixture run before all tests"""
        self.dock.show_only_visible_layers_flag = True
        load_standard_layers(self.dock)
        self.dock.hazard_layer_combo.setCurrentIndex(1)
        self.dock.exposure_layer_combo.setCurrentIndex(0)
        self.dock.show_only_visible_layers_flag = False
        self.dock.set_layer_from_title_flag = False
        self.dock.zoom_to_impact_flag = False
        self.dock.hide_exposure_flag = False
        self.dock.user_extent = None
        self.dock.user_extent_crs = None
        # For these tests we will generally use explicit overlap
        # between hazard, exposure and view, so make that default
        # see also safe/test/utilities.py where this is globally
        # set to HazardExposure
        settings = QtCore.QSettings()
        settings.setValue(
            'inasafe/analysis_extents_mode', HAZARD_EXPOSURE_VIEW)

    def tearDown(self):
        """Fixture run after each test"""
        QgsMapLayerRegistry.instance().removeAllMapLayers()
        self.dock.hazard_layer_combo.clear()
        self.dock.exposure_layer_combo.clear()
        # self.dock.aggregation_layer_combo.clear()
        # do not do this because the aggregation_layer_combo
        # need to be able to react to the status changes of the other combos

        # Make sure we reinstate globale default analysis extents mode of
        # hazard, exposure see also safe/test/utilities.py where this is
        # globally set to HazardExposure
        settings = QtCore.QSettings()
        settings.setValue(
            'inasafe/analysis_extents_mode', HAZARD_EXPOSURE)

    @unittest.expectedFailure
    def test_defaults(self):
        """Test the GUI in its default state"""
        # print combos_to_string(self.dock)
        self.assertEqual(self.dock.hazard_layer_combo.currentIndex(), 1)
        self.assertEqual(self.dock.exposure_layer_combo.currentIndex(), 0)
        self.assertEqual(self.dock.aggregation_layer_combo.currentIndex(), 0)

    def test_validate(self):
        """Validate function work as expected"""
        self.tearDown()
        # First check that we DON'T validate a clear self.dock
        flag, message = self.dock.validate()
        self.assertIsNotNone(message, 'No reason for failure given')

        message = 'Validation expected to fail on a cleared self.dock.'
        self.assertFalse(flag, message)

        # Now check we DO validate a populated self.dock
        populate_dock(self.dock)
        flag = self.dock.validate()
        message = (
            'Validation expected to pass on a populated dock with selections.')
        self.assertTrue(flag, message)

    def test_set_ok_button_status(self):
        """OK button changes properly according to self.dock validity"""
        # First check that we ok ISNT enabled on a clear self.dock
        self.tearDown()
        flag, message = self.dock.validate()

        self.assertIsNotNone(message, 'No reason for failure given')
        message = 'Validation expected to fail on a cleared self.dock.'
        self.assertFalse(flag, message)

        # Now check OK IS enabled on a populated self.dock
        populate_dock(self.dock)
        flag = self.dock.validate()
        message = (
            'Validation expected to pass on a populated self.dock with '
            'selections.')
        self.assertTrue(flag, message)

    @unittest.expectedFailure
    def test_insufficient_overlap(self):
        """Test Insufficient overlap errors are caught.

        ..note:: See https://github.com/AIFDR/inasafe/issues/372
        """
        # Push OK with the left mouse button
        button = self.dock.pbnRunStop

        message = 'Run button was not enabled'
        self.assertTrue(button.isEnabled(), message)
        set_jakarta_extent(self.dock)
        result, message = setup_scenario(
            self.dock,
            hazard='Continuous Flood',
            exposure='Population')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        # Zoom to an area where there is no overlap with layers
        rectangle = QgsRectangle(106.849, -6.153, 106.866, -6.134)
        CANVAS.setExtent(rectangle)
        crs = QgsCoordinateReferenceSystem('EPSG:4326')
        self.dock.define_user_analysis_extent(rectangle, crs)
        self.dock.show_next_analysis_extent()
        # Check that run button is disabled because extents do not overlap
        message = 'Run button was not disabled'
        self.assertFalse(button.isEnabled(), message)

    # disabled this test until further coding
    def xtest_print_map(self):
        """Test print map, especially on Windows."""
        settings = QtCore.QSettings()
        settings.setValue('inasafe/analysis_extents_mode', HAZARD_EXPOSURE)
        result, message = setup_scenario(
            self.dock,
            hazard='Classified Flood',
            exposure='Buildings')

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent(self.dock)

        self.assertTrue(result, message)

        # Press RUN
        button = self.dock.pbnRunStop
        # noinspection PyCallByClass,PyTypeChecker
        button.click()
        print_button = self.dock.pbnPrint

        try:
            # noinspection PyCallByClass,PyTypeChecker
            print_button.click()
        except OSError:
            LOGGER.debug('OSError')
            # pass
        except Exception, e:
            raise Exception('Exception is not expected, %s' % e)

    @unittest.expectedFailure
    def test_result_styling(self):
        """Test that colours and opacity from a model are correctly styled."""

        settings = QtCore.QSettings()
        settings.setValue('inasafe/analysis_extents_mode', HAZARD_EXPOSURE)

        result, message = setup_scenario(
            self.dock,
            hazard='Continuous Flood',
            exposure='Population')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent(self.dock)

        self.dock.accept()
        qgis_layer = self.dock.impact_function.impact
        style = qgis_layer.get_style_info()
        setRasterStyle(qgis_layer, style)
        # simple test for now - we could test explicitly for style state
        # later if needed.
        message = (
            'Raster layer was not assigned a Singleband pseudocolor '
            'renderer as expected.')
        self.assertEquals(
            qgis_layer.renderer().type(), 'singlebandpseudocolor', message)

        # Commenting out because we changed impact function to use floating
        # point quantities. Revisit in QGIS 2.0 where range based transparency
        # will have been implemented
        # message = ('Raster layer was not assigned transparency'
        #             'classes as expected.')
        # myTransparencyList = (qgis_layer.rasterTransparency().
        #        transparentSingleValuePixelList())
        # print "Transparency list:" + str(myTransparencyList)
        # assert (len(myTransparencyList) > 0)

    @unittest.expectedFailure
    def test_issue47(self):
        """Issue47: Hazard & exposure data are in different proj to viewport.

        See https://github.com/AIFDR/inasafe/issues/47
        """

        settings = QtCore.QSettings()
        settings.setValue('inasafe/analysis_extents_mode', HAZARD_EXPOSURE)

        result, message = setup_scenario(
            self.dock,
            hazard='Continuous Flood',
            exposure='Population')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GOOGLECRS, True)
        set_jakarta_google_extent(self.dock)

        # Press RUN
        self.dock.accept()

        result = self.dock.results_webview.page_to_text()

        message = 'Result not as expected: %s' % result
        # searching for values 6700 clean water [l] in result
        self.assertTrue(format_int(6700) in result, message)

    @unittest.expectedFailure
    def test_issue306(self):
        """Issue306: CANVAS doesnt add generated layers in tests.

        See https://github.com/AIFDR/inasafe/issues/306
        """

        settings = QtCore.QSettings()
        settings.setValue('inasafe/analysis_extents_mode', HAZARD_EXPOSURE)

        result, message = setup_scenario(
            self.dock,
            hazard='Continuous Flood',
            exposure='Population')
        self.assertTrue(result, message)
        # LOGGER.info("Canvas list before:\n%s" % canvas_list())
        # Enable on-the-fly reprojection
        set_canvas_crs(GOOGLECRS, True)
        set_jakarta_google_extent(self.dock)
        before_count = len(CANVAS.layers())

        # Press RUN
        self.dock.accept()

        # test issue #306
        after_count = len(CANVAS.layers())
        # LOGGER.info("Canvas list after:\n%s" % canvas_list())
        message = ('Layer was not added to canvas (%s before, %s after)' % (
            before_count, after_count))
        # print 'After count %s' % after_count
        self.assertEqual(before_count, after_count - 1, message)

    @unittest.expectedFailure
    def test_layer_legend_index(self):
        """Test we can get the legend index for a layer.

        .. versionadded:: 3.2

        """

        setup_scenario(
            self.dock,
            hazard='Continuous Flood',
            exposure='Population')
        layer = self.dock.get_exposure_layer()
        index = layer_legend_index(layer)
        self.assertEqual(index, 15)

    @unittest.expectedFailure
    def test_add_above_layer(self):
        """Test we can add one layer above another - see #2322

        .. versionadded:: 3.2
        """

        setup_scenario(
            self.dock,
            hazard='Continuous Flood',
            exposure='Population')
        layer_path = join(TESTDATA, 'polygon_0.shp')
        new_layer = QgsVectorLayer(layer_path, 'foo', 'ogr')
        exposure_layer = self.dock.get_exposure_layer()
        add_above_layer(new_layer, exposure_layer)
        root = QgsProject.instance().layerTreeRoot()
        id_list = root.findLayerIds()
        self.assertIn(new_layer.id(), id_list)
        new_layer_position = id_list.index(new_layer.id())
        existing_layer_position = id_list.index(exposure_layer.id())
        self.assertEqual(new_layer_position, existing_layer_position - 1)

    def test_load_layers(self):
        """Layers can be loaded and list widget was updated appropriately."""

        hazard_layer_count, exposure_layer_count = load_standard_layers()
        message = 'Expect %s layer(s) in hazard list widget but got %s' % (
            hazard_layer_count, self.dock.hazard_layer_combo.count())
        # pylint: disable=W0106
        self.assertEqual(
            self.dock.hazard_layer_combo.count(),
            hazard_layer_count, message)
        message = 'Expect %s layer(s) in exposure list widget but got %s' % (
            exposure_layer_count, self.dock.exposure_layer_combo.count())
        self.assertEqual(
            self.dock.exposure_layer_combo.count(),
            exposure_layer_count, message)
        # pylint: disable=W0106

    @unittest.expectedFailure
    def test_issue71(self):
        """Test issue #71 in github - cbo changes should update ok button."""
        # See https://github.com/AIFDR/inasafe/issues/71
        settings = QtCore.QSettings()
        settings.setValue('inasafe/analysis_extents_mode', HAZARD_EXPOSURE)
        self.tearDown()
        button = self.dock.pbnRunStop
        # First part of scenario should have enabled run
        file_list = [
            standard_data_path('hazard', 'continuous_flood_20_20.asc'),
            standard_data_path('exposure', 'pop_binary_raster_20_20.asc')
        ]
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
        path = os.path.join(TESTDATA, 'issue71.tif')
        file_list = [path]  # This layer has incorrect keywords
        clear_flag = False
        _, _ = load_layers(file_list, clear_flag)
        # set exposure to : Population Count (5kmx5km)
        # by moving one down
        self.dock.exposure_layer_combo.setCurrentIndex(
                self.dock.exposure_layer_combo.currentIndex() + 1)
        actual_dict = get_ui_state(self.dock)
        expected_dict = {
            'Run Button Enabled': False,
            'Impact Function Id': '',
            'Impact Function Title': '',
            'Hazard': 'Continuous Flood',
            'Exposure': 'Population Count (5kmx5km)'}
        message = ((
            'Run button was not disabled when exposure set to \n%s'
            '\nUI State: \n%s\nExpected State:\n%s\n%s') % (
                self.dock.exposure_layer_combo.currentText(),
                actual_dict,
                expected_dict,
                combos_to_string(self.dock)))

        self.assertTrue(expected_dict == actual_dict, message)

        # Now select again a valid layer and the run button
        # should be enabled
        self.dock.exposure_layer_combo.setCurrentIndex(
            self.dock.exposure_layer_combo.currentIndex() - 1)
        message = (
            'Run button was not enabled when exposure set to \n%s' %
            self.dock.exposure_layer_combo.currentText())
        self.assertTrue(button.isEnabled(), message)

    @unittest.skip('Skip unit test from InaSAFE v3.')
    def test_issue160(self):
        """Test that multipart features can be used in a scenario - GH #160"""
        exposure_layer = clone_shp_layer(
            name='buildings',
            include_keywords=True,
            source_directory=standard_data_path('exposure'))

        hazard_layer = clone_shp_layer(
            name='flood_multipart_polygons',
            include_keywords=True,
            source_directory=standard_data_path('hazard'))

        exposure_path = exposure_layer.source()
        hazard_path = hazard_layer.source()

        self.tearDown()
        button = self.dock.pbnRunStop
        # First part of scenario should have enabled run
        file_list = [hazard_path, exposure_path]
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
        path = os.path.join(TESTDATA, 'issue71.tif')
        file_list = [path]  # This layer has incorrect keywords
        clear_flag = False
        _, _ = load_layers(file_list, clear_flag)

        result, message = setup_scenario(
            self.dock,
            hazard='Flood Polygon',
            exposure='Buildings')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        expected_extent = QgsRectangle(
            106.80801, -6.19531, 106.83456946836641, -6.167526)
        CANVAS.setExtent(expected_extent)

        crs = QgsCoordinateReferenceSystem('EPSG:4326')
        self.dock.define_user_analysis_extent(expected_extent, crs)

        # Press RUN
        # noinspection PyCallByClass,PyCallByClass,PyTypeChecker
        self.dock.accept()
        result = self.dock.results_webview.page_to_text()

        message = 'Result not as expected: %s' % result
        self.assertTrue(format_int(33) in result, message)

    @unittest.expectedFailure
    def test_issue581(self):
        """Test issue #581 in github - Humanize can produce IndexError."""
        # See https://github.com/AIFDR/inasafe/issues/581

        settings = QtCore.QSettings()
        settings.setValue(
            'inasafe/analysis_extents_mode', HAZARD_EXPOSURE_BOUNDINGBOX)
        result, message = setup_scenario(
            self.dock,
            hazard='Continuous Flood',
            exposure='Population')
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_small_jakarta_extent(self.dock)
        # Press RUN
        self.dock.accept()
        result = self.dock.results_webview.page().currentFrame().toPlainText()

        message = 'Result not as expected: %s' % result
        self.assertTrue('IndexError' not in result, message)
        self.assertTrue(
            'It appears that no Population are affected by Continuous Flood.'
            in result, message)

    @unittest.skip('Skip unit test from InaSAFE v3.')
    def test_state(self):
        """Check if the save/restore state methods work. See also
        https://github.com/AIFDR/inasafe/issues/58
        """
        # default selected layer is the third layer exposure
        # so, decrease the index by one to change it
        self.dock.exposure_layer_combo.setCurrentIndex(
            self.dock.exposure_layer_combo.currentIndex() - 1)
        self.dock.save_state()
        expected_dict = get_ui_state(self.dock)
        # myState = self.dock.state
        # Now reset and restore and check that it gets the old state
        # Html is not considered in restore test since the ready
        # message overwrites it in dock implementation
        self.dock.exposure_layer_combo.setCurrentIndex(
            self.dock.exposure_layer_combo.currentIndex() - 1)
        self.dock.restore_state()
        result_dict = get_ui_state(self.dock)
        message = 'Got unexpected state: %s\nExpected: %s\n%s' % (
            result_dict, expected_dict, combos_to_string(self.dock))
        self.assertTrue(expected_dict == result_dict, message)

    @skipIf(sys.platform == 'win32', "Test cannot run on Windows")
    @unittest.expectedFailure
    def test_full_run_qgszstats(self):
        """Aggregation results are correct using native QGIS zonal stats.

        .. note:: We know this is going to fail (hence the decorator) as
            QGIS1.8 zonal stats are broken. We expect this to pass when we
            have ported to the QGIS 2.0 api at which time we can remove the
            decorator. TS July 2013

        """
        settings = QtCore.QSettings()
        settings.setValue(
            'inasafe/analysis_extents_mode', HAZARD_EXPOSURE)
        # TODO check that the values are similar enough to the python stats

        result, message = setup_scenario(
            self.dock,
            hazard='Continuous Flood',
            exposure='Population',
            function='Need evacuation',
            function_id='FloodEvacuationRasterHazardFunction',
            aggregation_layer=u'D\xedstr\xedct\'s of Jakarta',
            aggregation_enabled_flag=True)
        self.assertTrue(result, message)

        # Enable on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent(self.dock)
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        self.dock.accept()

        result = self.dock.results_webview.page_to_text()

        control_file_path = standard_data_path(
            'control',
            'files',
            'test-full-run-results-qgis.txt')
        expected_result = codecs.open(
            control_file_path,
            mode='r',
            encoding='utf-8').readlines()
        result = result.replace(
            '</td> <td>', ' ').replace('</td><td>', ' ')
        result = result.replace(
            '<th class="text-right">', ' ').replace('</th>', ' ')
        result = result.replace(
            '</td><td class="text-right">', ' ')
        for line in expected_result:
            line = line.replace('\n', '')
            self.assertIn(line, result)

    @unittest.expectedFailure
    def test_layer_changed(self):
        """Test the metadata is updated as the user highlights layers.

        For inasafe outputs, the table of results should be shown
        See also https://github.com/AIFDR/inasafe/issues/58
        """
        layer_path = os.path.join(TESTDATA, 'issue58.tif')
        layer, layer_purpose = load_layer(layer_path)
        message = (
            'Unexpected category for issue58.tif.\nGot:'
            ' %s\nExpected: undefined' % layer_purpose)

        self.assertTrue(layer_purpose == 'impact', message)
        self.dock.layer_changed(layer)
        self.dock.save_state()
        html = self.dock.state['report']
        expected = '4229'
        message = "%s\nDoes not contain:\n%s" % (
            html,
            expected)
        self.assertTrue(expected in html, message)

    def test_layer_saved_as_with_keywords_and_xml(self):
        """Check that auxiliary files are well copied when they exist and the
        'saved as' is used.
        """

        layer_path = os.path.join(TESTDATA, 'tsunami_building_assessment.shp')
        # pylint: disable=unused-variable
        layer, layer_type = load_layer(layer_path)
        # pylint: enable=unused-variable

        new_name = unique_filename(
            prefix='tsunami_building_assessment_saved_as_')
        self.dock.save_auxiliary_files(
            layer, join(TESTDATA, '%s.shp' % new_name))

        new_xml_filepath = os.path.join(TESTDATA, '%s.xml' % new_name)

        message = 'New auxiliary file does not exist : '
        self.assertTrue(os.path.isfile(new_xml_filepath), '%s xml' % message)

    def test_layer_saved_as_without_keywords_and_xml(self):
        """Check that auxiliary files aren't created when they don't exist.

        ... and the 'saved as' is used.
        """

        layer_path = os.path.join(TESTDATA, 'kecamatan_jakarta_osm.shp')
        # pylint: disable=unused-variable
        layer, layer_type = load_layer(layer_path)
        # pylint: enable=unused-variable

        new_name = unique_filename(prefix='kecamatan_jakarta_osm_saved_as')
        self.dock.save_auxiliary_files(
            layer, join(TESTDATA, '%s.shp' % new_name))
        new_xml_file_path = os.path.join(TESTDATA, '%s.xml' % new_name)

        message = 'New auxiliary file exist : '
        # Will automatically add xml file for the metadata.
        self.assertTrue(os.path.isfile(new_xml_file_path), '%s xml' % message)

    @unittest.expectedFailure
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

    @unittest.expectedFailure
    def test_issue317(self):
        """Points near the edge of a raster hazard layer are interpolated OK"""

        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent(self.dock)
        result, message = setup_scenario(
            self.dock,
            hazard='Continuous Flood',
            exposure='Buildings')
        self.assertTrue(result, message)

    # I disabled the test for now as checkMemory now returns None unless
    # there is a problem. TS
    def xtest_extents_changed(self):
        """Memory requirements are calculated correctly when extents change.
        """
        set_canvas_crs(GEOCRS, True)
        set_jakarta_extent(self.dock)
        setup_scenario(
            self.dock,
            hazard='A flood in Jakarta like in 2007',
            exposure='Penduduk Jakarta')
        result = self.dock.checkMemoryUsage()
        message = 'Expected "3mb" to apear in : %s' % result
        self.assertTrue(result is not None, 'Check memory reported None')
        self.assertTrue('3mb' in result, message)

    def test_cbo_aggregation_empty_project(self):
        """Aggregation combo changes properly according on no loaded layers"""
        self.tearDown()
        message = (
            'The aggregation combobox should have only the "Entire '
            'area" item when the project has no layer. Found:'
            ' %s' % (self.dock.aggregation_layer_combo.currentText()))

        self.assertEqual(
            self.dock.aggregation_layer_combo.currentText(),
            self.dock.tr('Entire area'), message)

        message = (
            'The aggregation combobox should be disabled when the '
            'project has no layer.')

        self.assertTrue(
            not self.dock.aggregation_layer_combo.isEnabled(), message)

    @unittest.expectedFailure
    def test_cbo_aggregation_toggle(self):
        """Aggregation Combobox toggles on and off as expected."""
        settings = QtCore.QSettings()
        settings.setValue(
            'inasafe/analysis_extents_mode', HAZARD_EXPOSURE)
        # With aggregation layer
        result, message = setup_scenario(
            self.dock,
            hazard='Continuous Flood',
            exposure='Population',
            aggregation_layer=u'D\xedstr\xedct\'s of Jakarta',
            aggregation_enabled_flag=True)
        message += ' when an aggregation layer is defined.'
        self.assertTrue(result, message)

        # With no aggregation layer
        layer = self.dock.get_aggregation_layer()
        layer_id = layer.id()
        QgsMapLayerRegistry.instance().removeMapLayer(layer_id)
        result, message = setup_scenario(
            self.dock,
            hazard='Continuous Flood',
            exposure='Population',
            aggregation_enabled_flag=False)
        message += ' when no aggregation layer is defined.'
        self.assertTrue(result, message)

    def test_set_dock_title(self):
        """Test the dock title gets set properly."""
        self.dock.set_dock_title()
        self.assertIn('InaSAFE', str(self.dock.windowTitle()))

    def wkt_to_coordinates(self, wkt):
        """Convert a wkt into a nested array of float pairs."""
        expected_coords = []
        wkt = wkt.replace('LINESTRING(', '').replace(')', '')
        # QGIS 2.10 replaced LINESTRING with LineString in WKT
        wkt = wkt.replace('LineString(', '').replace(')', '')
        # And in 2.16 (maybe earlier too?) it have a space before the bracket
        wkt = wkt.replace('LineString (', '')
        coords = wkt.split(',')
        for item in coords:
            item = item.strip()
            tokens = item.split(' ')
            # print tokens[0].strip()
            # print tokens[1].strip()
            expected_coords.append([
                float(tokens[0].strip()),
                float(tokens[1].strip())])
        return expected_coords

    @unittest.expectedFailure
    def test_rubber_bands(self):
        """Test that the rubber bands get updated."""
        settings = QtCore.QSettings()
        settings.setValue('inasafe/analysis_extents_mode', HAZARD_EXPOSURE)

        setup_scenario(
            self.dock,
            hazard='Continuous Flood',
            exposure='Population',
            aggregation_layer=u'D\xedstr\xedct\'s of Jakarta',
            aggregation_enabled_flag=True)

        self.dock.extent.show_rubber_bands = True
        expected_vertex_count = 5

        # 4326 with enabled on-the-fly reprojection - check next
        set_canvas_crs(GEOCRS, True)
        set_small_jakarta_extent(self.dock)
        self.dock.show_next_analysis_extent()
        next_band = self.dock.extent.next_analysis_rubberband
        self.assertEqual(expected_vertex_count, next_band.numberOfVertices())

        # 4326 with disabled on-the-fly reprojection - check next
        set_canvas_crs(GEOCRS, False)
        set_small_jakarta_extent(self.dock)
        self.dock.show_next_analysis_extent()
        next_band = self.dock.extent.next_analysis_rubberband
        self.assertEqual(expected_vertex_count, next_band.numberOfVertices())

        # 900913 with enabled on-the-fly reprojection - check next
        set_canvas_crs(GOOGLECRS, True)
        set_jakarta_google_extent(self.dock)
        next_band = self.dock.extent.next_analysis_rubberband
        self.assertEqual(expected_vertex_count, next_band.numberOfVertices())

        # 900913 with enabled on-the-fly reprojection - check last
        set_canvas_crs(GOOGLECRS, True)
        set_jakarta_google_extent(self.dock)
        # Press RUN
        # noinspection PyCallByClass,PyTypeChecker
        self.dock.accept()
        # self.dock.show_extent()
        last_band = self.dock.extent.last_analysis_rubberband
        geometry = last_band.asGeometry().exportToWkt()
        expected = (
            'LINESTRING(11889533.87392097897827625 -691251.80866545776370913, '
            '11893986.65355271473526955 -691251.80866545776370913, '
            '11893986.65355271473526955 -686773.02196401008404791, '
            '11889533.87392097897827625 -686773.02196401008404791, '
            '11889533.87392097897827625 -691251.80866545776370913)')
        expected_list = self.wkt_to_coordinates(expected)
        actual_list = self.wkt_to_coordinates(geometry)

        for item in xrange(0, len(expected_list)):
            # print item, expected_list[item], actual_list[item]
            self.assertAlmostEqual(
                expected_list[item][0],
                actual_list[item][0])
            self.assertAlmostEqual(
                expected_list[item][1],
                actual_list[item][1])

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
        extent = (
            'POLYGON (('
            '106.772279 -6.237576, '
            '106.772279 -6.165415, '
            '106.885165 -6.165415, '
            '106.885165 -6.237576, '
            '106.772279 -6.237576'
            '))')
        settings.setValue('inasafe/user_extent', extent)
        settings.setValue('inasafe/user_extent_crs', 'EPSG:4326')
        self.dock.read_settings()

        setup_scenario(
            self.dock,
            hazard='Continuous Flood',
            exposure='Population',
            aggregation_layer=u'D\xedstr\xedct\'s of Jakarta',
            aggregation_enabled_flag=True)

        self.dock.extent.show_rubber_bands = True
        expected_vertex_count = 2

        # 4326 with disabled on-the-fly reprojection
        set_canvas_crs(GEOCRS, True)
        # User extent should override this
        set_small_jakarta_extent(self.dock)
        self.dock.extent.show_user_analysis_extent()
        user_band = self.dock.extent._user_analysis_rubberband
        self.assertEqual(expected_vertex_count, user_band.numberOfVertices())

    @unittest.expectedFailure
    def test_issue1191(self):
        """Test setting a layer's title in the kw directly from qgis api"""
        settings = QtCore.QSettings()
        settings.setValue('inasafe/analysis_extents_mode', HAZARD_EXPOSURE)
        self.dock.set_layer_from_title_flag = True
        set_canvas_crs(GEOCRS, True)
        set_yogya_extent(self.dock)

        result, message = setup_scenario(
            self.dock,
            hazard='Earthquake',
            exposure='Buildings')
        self.assertTrue(result, message)

        layer = self.dock.get_hazard_layer()
        keyword_io = KeywordIO()

        original_title = 'Earthquake'
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
        self.dock.set_layer_from_title_flag = False


if __name__ == '__main__':
    suite = unittest.makeSuite(TestDock)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
