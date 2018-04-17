# coding=utf-8
"""Test Dock."""

import logging
import os
import unittest
# this import required to enable PyQt API v2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from qgis.core import QgsMapLayerRegistry
from PyQt4 import QtCore
from safe.test.utilities import get_qgis_app, get_dock
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting='InaSAFETest')
from safe.definitions.constants import (
    HAZARD_EXPOSURE_VIEW, HAZARD_EXPOSURE)
from safe.common.utilities import unique_filename
from safe.test.utilities import (
    load_standard_layers,
    load_test_vector_layer,
    setup_scenario,
    set_canvas_crs,
    populate_dock,
    GEOCRS,
    set_small_jakarta_extent)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


# noinspection PyArgumentList
class TestDock(unittest.TestCase):
    """Test the InaSAFE GUI."""

    @classmethod
    def setUpClass(cls):
        cls.dock = get_dock()

    def setUp(self):
        """Fixture run before all tests."""
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
        """Fixture run after each test."""
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
        """Test the GUI in its default state."""
        self.assertEqual(self.dock.hazard_layer_combo.currentIndex(), 1)
        self.assertEqual(self.dock.exposure_layer_combo.currentIndex(), 0)
        self.assertEqual(self.dock.aggregation_layer_combo.currentIndex(), 0)

    def test_validate(self):
        """Validate function work as expected."""
        self.tearDown()
        # First check that we DON'T validate a clear self.dock
        flag, message = self.dock._validate_question_area()
        self.assertIsNotNone(message, 'No reason for failure given')

        message = 'Validation expected to fail on a cleared self.dock.'
        self.assertFalse(flag, message)

        # Now check we DO validate a populated self.dock
        populate_dock(self.dock)
        flag = self.dock._validate_question_area()
        message = (
            'Validation expected to pass on a populated dock with selections.')
        self.assertTrue(flag, message)

    def test_set_ok_button_status(self):
        """OK button changes properly according to self.dock validity."""
        # First check that we ok ISNT enabled on a clear self.dock
        self.tearDown()
        flag, message = self.dock._validate_question_area()

        self.assertIsNotNone(message, 'No reason for failure given')
        message = 'Validation expected to fail on a cleared self.dock.'
        self.assertFalse(flag, message)

        # Now check OK IS enabled on a populated self.dock
        populate_dock(self.dock)
        flag = self.dock._validate_question_area()
        message = (
            'Validation expected to pass on a populated self.dock with '
            'selections.')
        self.assertTrue(flag, message)

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

    # @skipIf(sys.platform == 'win32', "Test cannot run on Windows")
    def test_layer_saved_as_with_keywords_and_xml(self):
        """Check that auxiliary files are well copied when they exist and the
        'saved as' is used.
        """
        # This layer has keywords.
        layer = load_test_vector_layer('exposure', 'airports.shp')

        new_name = unique_filename(prefix='airports_layer_saved_as_')
        new_shapefile_path = '%s.shp' % new_name
        new_xml_filepath = '%s.xml' % new_name

        self.dock.save_auxiliary_files(layer, new_shapefile_path)

        message = 'New auxiliary file does not exist : '
        self.assertTrue(os.path.isfile(new_xml_filepath), '%s xml' % message)

    def test_layer_saved_as_without_keywords_and_xml(self):
        """Check that auxiliary files aren't created when they don't exist and
        the 'saved as' is used.
        """
        # This layer does not have keywords.
        layer = load_test_vector_layer('other', 'keywordless_layer.shp')

        new_name = unique_filename(prefix='keywordless_layer_saved_as_')
        new_shapefile_path = '%s.shp' % new_name
        new_xml_filepath = '%s.xml' % new_name

        self.dock.save_auxiliary_files(layer, new_shapefile_path)

        message = 'New auxiliary file exists !'
        self.assertFalse(os.path.isfile(new_xml_filepath), '%s xml' % message)

    def test_cbo_aggregation_empty_project(self):
        """Aggregation combo changes properly according on no loaded layers."""
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
        self.dock.extent.display_user_extent()
        user_band = self.dock.extent._user_analysis_rubberband
        self.assertEqual(expected_vertex_count, user_band.numberOfVertices())


if __name__ == '__main__':
    suite = unittest.makeSuite(TestDock)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
