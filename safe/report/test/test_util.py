# coding=utf-8
"""Unittest for report utilities."""
import logging
import unittest

from safe.definitions.exposure import (
    exposure_structure,
    exposure_population,
    exposure_road)
from safe.definitions.exposure_classifications import (
    generic_structure_classes,
    generic_road_classes)
from safe.definitions.hazard import (
    hazard_generic,
    hazard_earthquake,
    hazard_tsunami,
    hazard_cyclone)
from safe.definitions.hazard_classifications import (
    generic_hazard_classes,
    earthquake_mmi_scale,
    tsunami_hazard_classes,
    cyclone_au_bom_hazard_classes)
from safe.report.extractors.util import (
    layer_definition_type,
    layer_hazard_classification,
    resolve_from_dictionary,
    retrieve_exposure_classes_lists)
from safe.test.utilities import (
    standard_data_path,
    get_qgis_app)
from safe.gis.tools import load_layer

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


LOGGER = logging.getLogger('InaSAFE')


class TestReportUtil(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.layer_paths_list = [
            ['gisv4', 'hazard', 'classified_vector.geojson'],
            ['gisv4', 'hazard', 'earthquake.asc'],
            ['gisv4', 'hazard', 'tsunami_vector.geojson'],
            ['gisv4', 'hazard', 'cyclone_AUBOM_km_h.asc'],
            ['gisv4', 'exposure', 'building-points.geojson'],
            ['gisv4', 'exposure', 'buildings.geojson'],
            ['gisv4', 'exposure', 'population.geojson'],
            ['gisv4', 'exposure', 'roads.geojson'],
        ]

    def test_layer_definition_type(self):
        """Test layer_definition_type method.

        .. versionadded:: 4.0
        """
        layer_paths = self.layer_paths_list
        expected_definitions = [
            hazard_generic,
            hazard_earthquake,
            hazard_tsunami,
            hazard_cyclone,
            exposure_structure,
            exposure_structure,
            exposure_population,
            exposure_road,
        ]
        for layer_path, expected_definition in zip(
                layer_paths, expected_definitions):
            path = standard_data_path(*layer_path)
            layer, _ = load_layer(path)
            actual_definition = layer_definition_type(layer)
            try:
                self.assertEqual(expected_definition, actual_definition)
            except Exception as e:
                LOGGER.error('Layer path: {path}'.format(
                    path=path))
                LOGGER.error('Expected {name}'.format(
                    **expected_definition))
                LOGGER.error('Actual {name}'.format(
                    **actual_definition))
                raise e

    # We are using multi hazard classification so this test will fail
    # the layer needs to run on impact function first or we can inject
    # the classification for this test.
    def test_layer_hazard_classification(self):
        """Test layer_hazard_classification method.

        .. versionadded:: 4.0
        """
        layer_paths = self.layer_paths_list
        expected_classifications = [
            generic_hazard_classes,
            earthquake_mmi_scale,
            tsunami_hazard_classes,
            cyclone_au_bom_hazard_classes,
            None,
            None,
            None,
            None,
        ]

        for layer_path, expected_classification in zip(
                layer_paths, expected_classifications):
            path = standard_data_path(*layer_path)
            layer, _ = load_layer(path)
            # inject classification keyword
            if expected_classification:
                layer.keywords['classification'] = (
                    expected_classification['key'])
            actual_classification = layer_hazard_classification(layer)
            try:
                self.assertEqual(
                    expected_classification, actual_classification)
            except Exception as e:
                LOGGER.error('Layer path: {path}'.format(
                    path=path))
                LOGGER.error('Expected {name}'.format(
                    **expected_classification))
                LOGGER.error('Actual {name}'.format(
                    **actual_classification))
                raise e

    def test_resolve_from_dictionary(self):
        """Test resolve_from_dictionary method.

        .. versionadded:: 4.0
        """
        test_dict = {
            'foo': {
                'bar': {
                    'bin': {
                        'baz': 1
                    }
                }
            },
            'foobar': 10
        }

        # test nested resolve
        expected = 1
        actual = resolve_from_dictionary(test_dict, [
            'foo', 'bar', 'bin', 'baz'])

        self.assertEqual(expected, actual)

        # test single resolve using list

        expected = 10
        actual = resolve_from_dictionary(test_dict, ['foobar'])

        self.assertEqual(expected, actual)

        # test single resolve using shorthand notation

        expected = 10
        actual = resolve_from_dictionary(test_dict, 'foobar')

        self.assertEqual(expected, actual)

    def test_retrieve_exposure_classes_lists(self):
        """Test retrieve_exposure_classes_lists method.

        .. versionadded:: 4.0
        """
        layer_paths = self.layer_paths_list
        expected_classes_lists = [
            None,
            None,
            None,
            None,
            generic_structure_classes['classes'],
            generic_structure_classes['classes'],
            None,
            generic_road_classes['classes']
        ]

        for layer_path, expected_classes in zip(
                layer_paths, expected_classes_lists):
            path = standard_data_path(*layer_path)
            layer, _ = load_layer(path)
            actual_classes = retrieve_exposure_classes_lists(layer.keywords)
            try:
                self.assertEqual(
                    expected_classes, actual_classes)
            except Exception as e:
                LOGGER.error('Layer path: {path}'.format(
                    path=path))
                LOGGER.error('Expected {classes}'.format(
                    classes=expected_classes))
                LOGGER.error('Actual {classes}'.format(
                    classes=actual_classes))
                raise e
