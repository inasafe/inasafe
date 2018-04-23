# coding=utf-8

"""Test for Impact Function."""


import getpass
import json
import logging
import os
import unittest
from copy import deepcopy
from datetime import datetime
from os import listdir
from os.path import join, isfile
from socket import gethostname

from safe.common.version import get_version
from safe.datastore.datastore import DataStore
from safe.definitions.default_values import female_ratio_default_value
from safe.definitions.fields import (
    exposure_type_field,
    female_ratio_field,
    female_count_field,
    youth_ratio_field,
    adult_ratio_field,
    elderly_ratio_field,
    female_displaced_count_field,
    youth_displaced_count_field,
    displaced_field,
)
from safe.definitions.layer_purposes import (
    layer_purpose_profiling,
    layer_purpose_analysis_impacted,
    layer_purpose_aggregate_hazard_impacted,
    layer_purpose_exposure_summary,
    layer_purpose_exposure_summary_table,
    layer_purpose_aggregation_summary,
)
from safe.definitions.minimum_needs import minimum_needs_fields
from safe.definitions.provenance import (
    provenance_action_checklist,
    provenance_aggregation_keywords,
    provenance_aggregation_layer,
    provenance_aggregation_layer_id,
    provenance_analysis_extent,
    provenance_analysis_question,
    provenance_data_store_uri,
    provenance_duration,
    provenance_end_datetime,
    provenance_exposure_keywords,
    provenance_exposure_layer,
    provenance_exposure_layer_id,
    provenance_gdal_version,
    provenance_hazard_keywords,
    provenance_hazard_layer,
    provenance_hazard_layer_id,
    provenance_host_name,
    provenance_impact_function_name,
    provenance_impact_function_title,
    provenance_inasafe_version,
    provenance_map_legend_title,
    provenance_map_title,
    provenance_notes,
    provenance_os,
    provenance_pyqt_version,
    provenance_qgis_version,
    provenance_qt_version,
    provenance_requested_extent,
    provenance_start_datetime,
    provenance_user,
    provenance_layer_exposure_summary,
    provenance_layer_aggregate_hazard_impacted,
    provenance_layer_aggregation_summary,
    provenance_layer_analysis_impacted,
    provenance_layer_exposure_summary_table
)
from safe.definitions.utilities import definition
from safe.impact_function.provenance_utilities import (
    get_map_title,
    get_analysis_question,
)
from safe.test.debug_helper import print_attribute_table
from safe.test.utilities import (
    get_control_text,
    load_test_raster_layer,
    get_qgis_app,
    standard_data_path,
    load_test_vector_layer,
    compare_wkt
)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qgis.core import (
    QgsVectorLayer,
    QgsRasterLayer,
    QgsMapLayer,
    QgsCoordinateReferenceSystem,
    QgsGeometry,
    Qgis)
from osgeo import gdal
from PyQt4.QtCore import QT_VERSION_STR
from PyQt4.Qt import PYQT_VERSION_STR
from safe.processors import post_processor_size
from safe.processors.population_post_processors import (
    post_processor_female,
    post_processor_male,
    post_processor_youth,
    post_processor_adult,
    post_processor_elderly)
from safe.definitions.constants import (
    PREPARE_SUCCESS,
    ANALYSIS_SUCCESS,
    ANALYSIS_FAILED_BAD_INPUT,
)
from safe.gis.sanity_check import check_inasafe_fields
from safe.utilities.str import byteify
from safe.utilities.gis import wkt_to_rectangle
from safe.utilities.utilities import readable_os_version
from safe.impact_function.impact_function import ImpactFunction
from safe.impact_function.impact_function_utilities import check_input_layer
from safe.definitions.exposure import exposure_population

LOGGER = logging.getLogger('InaSAFE')

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def read_json_flow(json_path):
    """Helper method to read json file that contains a scenario.

    :param json_path: Path to json file.
    :type json_path: unicode, str

    :returns: Tuple of dictionary contains a scenario and expected result.
    :rtype: (dict, dict, dict)
    """
    with open(json_path) as json_data:
        data = byteify(json.load(json_data))
    return data['scenario'], data['expected_steps'], data['expected_outputs']


def run_scenario(scenario, use_debug=False):
    """Run scenario.

    :param scenario: Dictionary of hazard, exposure, and aggregation.
    :type scenario: dict

    :param use_debug: If we should use debug_mode when we run the scenario.
    :type use_debug: bool

    :returns: Tuple(status, Flow dictionary, outputs, computed number of
                outputs).
    :rtype: list
    """
    if os.path.exists(scenario['exposure']):
        exposure_path = scenario['exposure']
    elif os.path.exists(standard_data_path('exposure', scenario['exposure'])):
        exposure_path = standard_data_path('exposure', scenario['exposure'])
    elif os.path.exists(
            standard_data_path(*(scenario['exposure'].split('/')))):
        exposure_path = standard_data_path(*(scenario['exposure'].split('/')))
    else:
        raise IOError('No exposure file')

    if os.path.exists(scenario['hazard']):
        hazard_path = scenario['hazard']
    elif os.path.exists(standard_data_path('hazard', scenario['hazard'])):
        hazard_path = standard_data_path('hazard', scenario['hazard'])
    elif os.path.exists(standard_data_path(*(scenario['hazard'].split('/')))):
        hazard_path = standard_data_path(*(scenario['hazard'].split('/')))
    else:
        raise IOError('No hazard file')

    if not scenario['aggregation']:
        aggregation_path = None
    else:
        if os.path.exists(scenario['aggregation']):
            aggregation_path = scenario['aggregation']
        elif os.path.exists(standard_data_path(
                'aggregation', scenario['aggregation'])):
            aggregation_path = standard_data_path(
                'aggregation', scenario['aggregation'])
        elif os.path.exists(
                standard_data_path(*(scenario['aggregation'].split('/')))):
            aggregation_path = standard_data_path(
                *(scenario['aggregation'].split('/')))
        else:
            raise IOError('No aggregation file')

    impact_function = ImpactFunction()
    impact_function.debug_mode = use_debug

    layer = QgsVectorLayer(hazard_path, 'Hazard', 'ogr')
    if not layer.isValid():
        layer = QgsRasterLayer(hazard_path, 'Hazard')
    impact_function.hazard = layer

    layer = QgsVectorLayer(exposure_path, 'Exposure', 'ogr')
    if not layer.isValid():
        layer = QgsRasterLayer(exposure_path, 'Exposure')
    impact_function.exposure = layer

    if aggregation_path:
        impact_function.aggregation = QgsVectorLayer(
            aggregation_path, 'Aggregation', 'ogr')
    else:
        impact_function.crs = QgsCoordinateReferenceSystem(4326)

    status, message = impact_function.prepare()
    if status != 0:
        raise Exception(message)

    counts = len(impact_function.output_layers_expected())

    status, message = impact_function.run()
    if status != 0:
        raise Exception(message)

    for layer in impact_function.outputs:
        if layer.type() == QgsMapLayer.VectorLayer:
            check_inasafe_fields(layer)

    return (
        status,
        impact_function.state,
        impact_function.outputs,
        counts,
        impact_function
    )


class TestImpactFunction(unittest.TestCase):

    """Test Impact Function."""

    def assertEqualImpactFunction(self, first, second, msg=None):
        """Special assert for impact function equality."""
        if not isinstance(first, ImpactFunction):
            message = (
                'First object is not an ImpactFunction object, but a %s' %
                type(second))
            self.fail(self._formatMessage(msg, message))
        if not isinstance(second, ImpactFunction):
            message = (
                'Second object is not an ImpactFunction object, but a %s' %
                type(second))
            self.fail(self._formatMessage(msg, message))

        equal, message = first.is_equal(second)
        if not equal:
            self.fail(self._formatMessage('%s\n%s' % (msg, message), message))

    def test_keyword_monkey_patch(self):
        """Test behaviour of generating keywords."""
        exposure_path = standard_data_path('exposure', 'building-points.shp')
        # noinspection PyCallingNonCallable
        exposure_layer = QgsVectorLayer(exposure_path, 'Building', 'ogr')

        check_input_layer(exposure_layer, 'exposure')

        expected_inasafe_fields = {
            exposure_type_field['key']: 'TYPE',
        }
        self.assertDictEqual(
            exposure_layer.keywords['inasafe_fields'], expected_inasafe_fields)

        fields = list(exposure_layer.dataProvider().fieldNameMap().keys())
        self.assertIn(
            exposure_layer.keywords['inasafe_fields']['exposure_type_field'],
            fields
        )
        # We check that this key exists in the dictionary.
        self.assertIn('inasafe_fields', list(exposure_layer.keywords.keys()))

    def test_impact_function_behaviour(self):
        """Test behaviour of impact function."""
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_layer = load_test_vector_layer('exposure', 'roads.shp')

        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.crs = QgsCoordinateReferenceSystem(4326)
        impact_function.prepare()
        self.assertEqual(impact_function.name, 'Flood Polygon On Roads Line')
        self.assertEqual(impact_function.title, 'be affected')

        expected_layers = [
            layer_purpose_exposure_summary['key'],
            layer_purpose_aggregate_hazard_impacted['key'],
            layer_purpose_aggregation_summary['key'],
            layer_purpose_analysis_impacted['key'],
            layer_purpose_exposure_summary_table['key'],
            layer_purpose_profiling['key'],
        ]
        self.assertListEqual(
            expected_layers, impact_function.output_layers_expected())

    def test_minimum_extent(self):
        """Test we can compute the minimum extent in the IF."""
        # Without aggregation layer
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_layer = load_test_vector_layer('exposure', 'roads.shp')
        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.crs = QgsCoordinateReferenceSystem(4326)
        status, message = impact_function.prepare()
        self.assertEqual(PREPARE_SUCCESS, status, message)
        message = (
            'Test about the minimum extent without an aggregation layer is '
            'failing.')
        self.assertTrue(
            compare_wkt(
                'Polygon (('
                '106.8080099999999959 -6.19531000000000009, '
                '106.8080099999999959 -6.16752599999999962, '
                '106.83456946836641066 -6.16752599999999962, '
                '106.83456946836641066 -6.19531000000000009, '
                '106.8080099999999959 -6.19531000000000009))',
                impact_function.analysis_extent.exportToWkt()),
            message
        )

        # Without aggregation layer but with a requested_extent
        hazard_layer = load_test_vector_layer(
            'hazard', 'flood_multipart_polygons.shp')
        exposure_layer = load_test_vector_layer('exposure', 'roads.shp')
        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.requested_extent = wkt_to_rectangle(
            'POLYGON (('
            '106.772279 -6.237576, '
            '106.772279 -6.165415, '
            '106.885165 -6.165415, '
            '106.885165 -6.237576, '
            '106.772279 -6.237576'
            '))')
        impact_function.crs = QgsCoordinateReferenceSystem(4326)

        status, message = impact_function.prepare()
        self.assertEqual(PREPARE_SUCCESS, status, message)
        message = (
            'Test about the minimum extent without an aggregation layer but '
            'with a requested extent is failing.')
        self.assertTrue(
            compare_wkt(
                'Polygon (('
                '106.8080099999999959 -6.19531000000000009, '
                '106.8080099999999959 -6.16752599999999962, '
                '106.83456946836641066 -6.16752599999999962, '
                '106.83456946836641066 -6.19531000000000009, '
                '106.8080099999999959 -6.19531000000000009))',
                impact_function.analysis_extent.exportToWkt()),
            message
        )

        # With an aggregation layer, without selection
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')
        impact_function = ImpactFunction()
        impact_function.aggregation = aggregation_layer
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.use_selected_features_only = False
        impact_function.aggregation.select(0)
        status, message = impact_function.prepare()
        self.assertEqual(PREPARE_SUCCESS, status, message)
        message = (
            'Test about the minimum extent with an aggregation layer is '
            'failing.')
        self.assertTrue(
            compare_wkt(
                'Polygon ((106.9033179652593617 -6.18324454090033182, '
                '106.90331796525939012 -6.2725478115989306, '
                '106.72365490843547775 -6.2725478115989306, '
                '106.72365490843547775 -6.18324645462287137, '
                '106.72365490843547775 -6.09392810187095257, '
                '106.81348643684744104 -6.09392810187095257, '
                '106.9033179652593617 -6.09392810187095257, '
                '106.9033179652593617 -6.18324454090033182))',
                impact_function.analysis_extent.exportToWkt()),
            message
        )

        # With an aggregation layer, with selection
        impact_function.use_selected_features_only = True
        impact_function.aggregation = aggregation_layer
        status, message = impact_function.prepare()
        self.assertEqual(PREPARE_SUCCESS, status, message)
        message = (
            'Test about the minimum extent with an aggregation layer and '
            'a selection is failing.')
        self.assertTrue(
            compare_wkt(
                'Polygon ((106.72365490843547775 -6.09392810187095257, '
                '106.81348643684744104 -6.09392810187095257, '
                '106.81348643684744104 -6.18324645462287137, '
                '106.72365490843547775 -6.18324645462287137, '
                '106.72365490843547775 -6.09392810187095257))',
                impact_function.analysis_extent.exportToWkt()),
            message
        )

    def test_not_exposed_exposure(self):
        """Test if we can run 0 exposed features over a raster hazard."""
        hazard_layer = load_test_raster_layer(
            'gisv4', 'hazard', 'earthquake.asc')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'airport_outside_of_extent.geojson')
        crs = QgsCoordinateReferenceSystem(4326)
        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.crs = crs
        impact_function.debug_mode = False
        status, message = impact_function.prepare()
        message = message.to_text() if message is not None else message
        self.assertEqual(PREPARE_SUCCESS, status, message)

        # Test extent, as the hazard extent is smaller than the exposure,
        # extent must be equal to the hazard extent
        # self.assertTrue(
        #     compare_wkt(
        #         hazard_layer.extent().asWktPolygon(),
        #         impact_function.analysis_extent.exportToWkt()))

        status, message = impact_function.run()
        message = message.to_text() if message is not None else message
        self.assertEqual(ANALYSIS_SUCCESS, status, message)

    def test_ratios_with_vector_exposure(self):
        """Test if we can add defaults to a vector exposure."""
        # First test, if we do not provide an aggregation,
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'population.geojson')

        # Set up impact function
        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.crs = QgsCoordinateReferenceSystem(4326)
        impact_function.prepare()
        # Let's remove one field from keywords.
        # We monkey patch keywords for testing after `prepare` & before `run`.
        fields = impact_function.exposure.keywords['inasafe_fields']
        del fields[female_count_field['key']]
        expected_layers = [
            layer_purpose_exposure_summary['key'],
            layer_purpose_aggregate_hazard_impacted['key'],
            layer_purpose_aggregation_summary['key'],
            layer_purpose_analysis_impacted['key'],
            layer_purpose_profiling['key'],
        ]
        self.assertListEqual(
            expected_layers, impact_function.output_layers_expected())
        status, message = impact_function.run()
        self.assertEqual(ANALYSIS_SUCCESS, status, message)

        impact = impact_function.impact

        # We check the field exist after the IF with only one value.
        field = impact.fieldNameIndex(
            female_ratio_field['field_name'])
        self.assertNotEqual(-1, field)
        unique_ratio = impact.uniqueValues(field)
        self.assertEqual(1, len(unique_ratio), unique_ratio)
        self.assertEqual(
            unique_ratio[0], female_ratio_default_value['default_value'])

        # Second test, if we provide an aggregation without a default ratio 0.2
        expected_ratio = 1.0
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'population.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        # Set up impact function
        impact_function = ImpactFunction()
        impact_function.aggregation = aggregation_layer
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.debug_mode = True
        impact_function.prepare()
        # The `prepare` reads keywords from the file.
        impact_function.aggregation.keywords['inasafe_default_values'] = {
            elderly_ratio_field['key']: expected_ratio
        }
        fields = impact_function.exposure.keywords['inasafe_fields']
        del fields[female_count_field['key']]
        status, message = impact_function.run()
        self.assertEqual(ANALYSIS_SUCCESS, status, message)
        impact = impact_function.impact

        # We check the field exist after the IF with only original values.
        field = impact.fieldNameIndex(
            female_ratio_field['field_name'])
        self.assertNotEqual(-1, field)
        unique_ratio = impact.uniqueValues(field)
        self.assertEqual(3, len(unique_ratio), unique_ratio)

        # We check the field exist after the IF with only one value.
        field = impact.fieldNameIndex(
            elderly_ratio_field['field_name'])
        self.assertNotEqual(-1, field)
        unique_ratio = impact.uniqueValues(field)
        self.assertEqual(1, len(unique_ratio), unique_ratio)
        self.assertEqual(expected_ratio, unique_ratio[0])

        # Third test, if we provide an aggregation with a ratio and the
        # exposure has a count, we should a have a ratio from the exposure
        # count.
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'population.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        # Set up impact function
        impact_function = ImpactFunction()
        impact_function.debug_mode = True
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.aggregation = aggregation_layer
        impact_function.prepare()
        status, message = impact_function.run()
        self.assertEqual(ANALYSIS_SUCCESS, status, message)

        impact = impact_function.impact

        # Check that we have don't have only one unique value since the ratio
        # depends on the "population / female count" and we should have at
        # least different ratios.
        field = impact.fieldNameIndex(
            female_ratio_field['field_name'])
        self.assertNotEqual(-1, field)
        unique_ratio = impact.uniqueValues(field)
        self.assertNotEqual(1, len(unique_ratio), unique_ratio)

    def test_ratios_with_raster_exposure(self):
        """Test if we can add defaults to a raster exposure.

        See ticket #3851 how to manage ratios with a raster exposure.
        """
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'tsunami_vector.geojson')
        exposure_layer = load_test_raster_layer(
            'gisv4', 'exposure', 'raster', 'population.asc')

        # Set up impact function
        impact_function = ImpactFunction()
        impact_function.debug_mode = True
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.crs = QgsCoordinateReferenceSystem(4326)
        impact_function.prepare()
        expected_layers = [
            layer_purpose_aggregate_hazard_impacted['key'],
            layer_purpose_aggregation_summary['key'],
            layer_purpose_analysis_impacted['key'],
            layer_purpose_profiling['key'],
        ]
        self.assertListEqual(
            expected_layers, impact_function.output_layers_expected())
        status, message = impact_function.run()
        self.assertEqual(ANALYSIS_SUCCESS, status, message)

        for layer in impact_function.outputs:
            if layer.keywords['layer_purpose'] == (
                    layer_purpose_analysis_impacted['key']):
                analysis = layer
            if layer.keywords['layer_purpose'] == (
                    layer_purpose_aggregate_hazard_impacted['key']):
                impact = layer

        # We check in the impact layer if we have :
        # female default ratio with the default value
        index = impact.fieldNameIndex(female_ratio_field['field_name'])
        self.assertNotEqual(-1, index)
        unique_values = impact.uniqueValues(index)
        self.assertEqual(1, len(unique_values))
        female_ratio = unique_values[0]

        # female displaced count and youth displaced count
        self.assertNotEqual(
            -1, impact.fieldNameIndex(
                female_displaced_count_field['field_name']))
        self.assertNotEqual(
            -1, impact.fieldNameIndex(
                youth_displaced_count_field['field_name']))

        # Check that we have more than 0 female displaced in the analysis layer
        index = analysis.fieldNameIndex(
            female_displaced_count_field['field_name'])
        female_displaced = analysis.uniqueValues(index)[0]
        self.assertGreater(female_displaced, 0)

        # Let's check computation
        index = analysis.fieldNameIndex(
            displaced_field['field_name'])
        displaced_population = analysis.uniqueValues(index)[0]
        self.assertEqual(
            int(displaced_population * female_ratio), female_displaced)

        # Check that we have more than 0 youth displaced in the analysis layer
        index = analysis.fieldNameIndex(
            female_displaced_count_field['field_name'])
        value = analysis.uniqueValues(index)[0]
        self.assertGreater(value, 0)

        # Let do another test with the special aggregation layer
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'tsunami_vector.geojson')
        exposure_layer = load_test_raster_layer(
            'gisv4', 'exposure', 'raster', 'population.asc')

        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid_ratios.geojson')
        # This aggregation layer has :
        # * a field for female ratio : 1, 0.5 and 0
        # * use global default for youth ratio
        # * do not ust for adult ratio
        # * use custom 0.75 for elderly ratio

        # Set up impact function
        impact_function = ImpactFunction()
        impact_function.debug_mode = True
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.aggregation = aggregation_layer
        status, message = impact_function.prepare()
        self.assertEqual(PREPARE_SUCCESS, status, message)
        status, message = impact_function.run()
        self.assertEqual(ANALYSIS_SUCCESS, status, message)

        impact = impact_function.impact

        # We should have a female_ratio with many values
        index = impact.fieldNameIndex(female_ratio_field['field_name'])
        self.assertNotEqual(-1, index)
        values = impact.uniqueValues(index)
        self.assertEqual(3, len(values))

        # We should have a youth_ratio with global default
        index = impact.fieldNameIndex(youth_ratio_field['field_name'])
        self.assertNotEqual(-1, index)
        values = impact.uniqueValues(index)
        self.assertEqual(1, len(values))

        # We should not have an adult_ratio
        index = impact.fieldNameIndex(adult_ratio_field['field_name'])
        self.assertEqual(-1, index)

        # We should have a elderly_ratio = 0.75
        index = impact.fieldNameIndex(elderly_ratio_field['field_name'])
        self.assertNotEqual(-1, index)
        values = impact.uniqueValues(index)
        self.assertEqual(1, len(values))
        self.assertEqual(0.75, values[0])

    def test_profiling(self):
        """Test running impact function on test data."""
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        # Set up impact function
        impact_function = ImpactFunction()
        impact_function.aggregation = aggregation_layer
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        status, message = impact_function.run()
        self.assertEqual(ANALYSIS_FAILED_BAD_INPUT, status, message)
        impact_function.prepare()
        status, message = impact_function.run()
        self.assertEqual(ANALYSIS_SUCCESS, status, message)
        message = impact_function.performance_log_message().to_text()
        expected_result = get_control_text(
            'test-profiling-logs.txt')

        for line in expected_result:
            line = line.replace('\n', '')
            if line == '' or line == '-':
                continue
            self.assertIn(line, message)

        # Notes(IS): For some unknown reason I need to do this to make
        # test_provenance pass
        del hazard_layer

    def test_scenario(
            self, scenario_path=None, use_debug=True, test_loader=False):
        """Run test single scenario."""
        self.maxDiff = None

        if not scenario_path:
            scenario_path = standard_data_path(
                'scenario',
                'polygon_classified_on_line.json')

        LOGGER.info('Running the scenario : %s' % scenario_path)
        scenario, expected_steps, expected_outputs = read_json_flow(
            scenario_path)
        status, steps, outputs, computed_nb_outputs, impact_function = (
            run_scenario(scenario, use_debug))
        self.assertEqual(0, status, steps)
        # self.assertDictEqual(expected_steps, steps, scenario_path)
        try:
            self.assertDictEqual(byteify(expected_steps), byteify(steps))
        except AssertionError:
            LOGGER.info('Exception found in ' + scenario_path)
            raise
        # - 1 because I added the profiling table, and this table is not
        # counted in the JSON file.
        self.assertEqual(len(outputs) - 1, expected_outputs['count'])
        self.assertEqual(len(outputs), computed_nb_outputs)
        self.assertEqual(
            impact_function.crs.authid(),
            impact_function.impact.crs().authid())

        # Test deserialization
        if test_loader:
            LOGGER.debug('Test deserialization.')
            output_metadata = impact_function.impact.keywords
            new_impact_function = ImpactFunction. \
                load_from_output_metadata(output_metadata)
            message = "Exception found in " + scenario_path
            self.assertEqualImpactFunction(
                impact_function, new_impact_function, message)

        return impact_function

    @unittest.skipIf(
        os.environ.get('ON_TRAVIS', False),
        'Duplicate test of test_scenario_directory.')
    def test_scenarios(self):
        """Test manually a directory.

        This function is like test_directory, but you can control manually
        which scenario you want to launch.

        Let's keep booleans to False by default.
        """
        scenarios = {
            'earthquake_raster_on_raster_population': False,
            'earthquake_raster_on_vector_places': False,
            'earthquake_raster_on_vector_population': False,
            'polygon_classified_on_line': False,
            'polygon_classified_on_point': False,
            'polygon_classified_on_vector_population': False,
            'polygon_classified_on_vector_population_multi_fields': False,
            'polygon_continuous_on_line': False,
            'raster_classified_on_classified_raster': False,
            'raster_classified_on_indivisible_polygons_with_grid': False,
            'raster_classified_on_line_with_grid': False,
            'raster_classified_on_vector_population_multi_fields': False,
            'raster_continuous_on_divisible_polygons_with_grid': False,
            'raster_continuous_on_line': False,
            'raster_continuous_on_raster_population': False,
        }

        # If we want to invert the selection.
        invert = False
        # If we want to also test the IF loader / deserialization.
        test_loader = False

        path = standard_data_path('scenario')
        # Sort it to make it easy to debug
        for scenario in sorted(scenarios.keys()):
            enabled = scenarios[scenario]
            if (not invert and enabled) or (invert and not enabled):
                self.test_scenario(
                    join(path, scenario + '.json'), test_loader=test_loader)

        json_files = [
            join(path, f) for f in listdir(path)
            if isfile(join(path, f)) and f.endswith('.json')
        ]
        self.assertEqual(len(json_files), len(scenarios))

    def test_scenario_directory(self):
        """Run test scenario in directory."""
        path = standard_data_path('scenario')

        json_files = [
            join(path, f) for f in listdir(path)
            if isfile(join(path, f)) and f.endswith('.json')
        ]

        count = 0
        for json_file in json_files:
            scenario, expected_steps, expected_outputs = read_json_flow(
                json_file)
            if scenario.get('enable', True):
                # fix_print_with_import
                print("Test JSON scenario : ")
                # fix_print_with_import
                print(json_file)
                self.test_scenario(json_file, test_loader=True)
                count += 1
        self.assertEqual(len(json_files), count)

    def test_old_fields_keywords(self):
        """The IF is not ready with we have some wrong inasafe_fields."""
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson',
            clone=True)
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        impact_function = ImpactFunction()
        impact_function.aggregation = aggregation_layer
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        status, message = impact_function.prepare()

        # The layer should be fine.
        self.assertEqual(PREPARE_SUCCESS, status, message)

        # Now, we remove one field
        exposure_layer.startEditing()
        field = list(exposure_layer.keywords['inasafe_fields'].values())[0]
        index = exposure_layer.fieldNameIndex(field)
        exposure_layer.deleteAttribute(index)
        exposure_layer.commitChanges()

        # It shouldn't be fine as we removed one field which
        # was in inasafe_fields
        status, message = impact_function.prepare()
        self.assertNotEqual(PREPARE_SUCCESS, status, message)

    def test_post_processor(self):
        """Test for running post processor."""
        impact_layer = load_test_vector_layer(
            'impact',
            'indivisible_polygon_impact.geojson',
            clone_to_memory=True)

        impact_layer.keywords['hazard_keywords'] = {
            'classification': 'flood_hazard_classes'
        }
        impact_layer.keywords['exposure_keywords'] = {
            'exposure': exposure_population['key'],
        }

        def debug_layer(layer, add_to_datastore):
            """Monkey patching because we can't check inasafe_fields.

            :param layer: The layer.
            :type layer: QgsVectorLayer

            :param add_to_datastore: Flag
            :type add_to_datastore: bool
            """
            # We do nothing here.
            return layer, add_to_datastore

        impact_function = ImpactFunction()
        impact_function.debug_layer = debug_layer

        impact_function.post_process(impact_layer)

        used_post_processors = [
            post_processor_size,
            post_processor_male,
            post_processor_female,
            post_processor_youth,
            post_processor_adult,
            post_processor_elderly,
        ]

        # Check if new field is added
        impact_fields = list(impact_layer.dataProvider().fieldNameMap().keys())
        for post_processor in used_post_processors:
            # noinspection PyTypeChecker
            for output_value in list(post_processor['output'].values()):
                field_name = output_value['value']['field_name']
                self.assertIn(field_name, impact_fields)
        print_attribute_table(impact_layer, 1)

    def test_provenance_with_aggregation(self):
        """Test provenance of impact function with aggregation."""
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        hazard = definition(hazard_layer.keywords['hazard'])
        exposure = definition(exposure_layer.keywords['exposure'])
        hazard_category = definition(hazard_layer.keywords['hazard_category'])

        expected_provenance = {
            provenance_gdal_version['provenance_key']: gdal.__version__,
            provenance_host_name['provenance_key']: gethostname(),
            provenance_map_title['provenance_key']: get_map_title(
                hazard, exposure, hazard_category),
            provenance_map_legend_title['provenance_key']: exposure[
                'layer_legend_title'],
            provenance_user['provenance_key']: getpass.getuser(),
            provenance_os['provenance_key']: readable_os_version(),
            provenance_pyqt_version['provenance_key']: PYQT_VERSION_STR,
            provenance_qgis_version['provenance_key']: Qgis.QGIS_VERSION,
            provenance_qt_version['provenance_key']: QT_VERSION_STR,
            provenance_inasafe_version['provenance_key']: get_version(),
            provenance_aggregation_layer['provenance_key']:
                aggregation_layer.source() + '|qgis_provider=ogr',
            provenance_aggregation_layer_id['provenance_key']:
                aggregation_layer.id(),
            provenance_exposure_layer['provenance_key']:
                exposure_layer.source() + '|qgis_provider=ogr',
            provenance_exposure_layer_id['provenance_key']:
                exposure_layer.id(),
            provenance_hazard_layer['provenance_key']:
                hazard_layer.source() + '|qgis_provider=ogr',
            provenance_hazard_layer_id['provenance_key']: hazard_layer.id(),
            provenance_analysis_question['provenance_key']:
                get_analysis_question(hazard, exposure),
            provenance_aggregation_keywords['provenance_key']: deepcopy(
                aggregation_layer.keywords),
            provenance_exposure_keywords['provenance_key']:
                deepcopy(exposure_layer.keywords),
            provenance_hazard_keywords['provenance_key']: deepcopy(
                hazard_layer.keywords),
        }

        # Set up impact function
        impact_function = ImpactFunction()
        impact_function.aggregation = aggregation_layer
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        self.assertDictEqual({}, impact_function.provenance)
        status, message = impact_function.prepare()
        self.assertEqual(PREPARE_SUCCESS, status, message)
        self.assertDictEqual({}, impact_function.provenance)
        status, message = impact_function.run()
        self.assertEqual(ANALYSIS_SUCCESS, status, message)

        self.maxDiff = None

        expected_provenance.update({
            provenance_action_checklist['provenance_key']:
                impact_function.action_checklist(),
            provenance_analysis_extent['provenance_key']:
                impact_function.analysis_extent.exportToWkt(),
            provenance_impact_function_name['provenance_key']:
                impact_function.name,
            provenance_impact_function_title['provenance_key']:
                impact_function.title,
            provenance_notes['provenance_key']: impact_function.notes(),
            provenance_requested_extent['provenance_key']: impact_function.
                requested_extent,
            provenance_data_store_uri['provenance_key']: impact_function.
                datastore.uri_path,
            provenance_start_datetime['provenance_key']: impact_function.
                start_datetime,
            provenance_end_datetime['provenance_key']:
                impact_function.end_datetime,
            provenance_duration['provenance_key']: impact_function.duration
        })

        self.assertDictContainsSubset(
            expected_provenance, impact_function.provenance)

        output_layer_provenance_keys = [
            provenance_layer_exposure_summary['provenance_key'],
            provenance_layer_aggregate_hazard_impacted['provenance_key'],
            provenance_layer_aggregation_summary['provenance_key'],
            provenance_layer_analysis_impacted['provenance_key'],
            provenance_layer_exposure_summary_table['provenance_key']
        ]

        for key in output_layer_provenance_keys:
            self.assertIn(key, list(impact_function.provenance.keys()))

        # Future reference: I comment out these lines since the keywords
        # properties are used in the report generation. Removing it will make
        # the report generation fail. I will just make sure that the other
        # tools will read from keywords file not from layer properties.
        # Test to make sure the monkey patch is not updated #4128
        # self.assertDictEqual(
        #     expected_provenance['aggregation_keywords'],
        #     aggregation_layer.keywords
        # )
        # self.assertDictEqual(
        #     expected_provenance['hazard_keywords'],
        #     hazard_layer.keywords
        # )
        # self.assertDictEqual(
        #     expected_provenance['exposure_keywords'],
        #     exposure_layer.keywords
        # )

    def test_provenance_without_aggregation(self):
        """Test provenance of impact function without aggregation."""
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson')

        hazard = definition(hazard_layer.keywords['hazard'])
        exposure = definition(exposure_layer.keywords['exposure'])
        hazard_category = definition(hazard_layer.keywords['hazard_category'])

        expected_provenance = {
            provenance_gdal_version['provenance_key']: gdal.__version__,
            provenance_host_name['provenance_key']: gethostname(),
            provenance_map_title['provenance_key']: get_map_title(
                hazard, exposure, hazard_category),
            provenance_map_legend_title['provenance_key']: exposure[
                'layer_legend_title'],
            provenance_user['provenance_key']: getpass.getuser(),
            provenance_os['provenance_key']: readable_os_version(),
            provenance_pyqt_version['provenance_key']: PYQT_VERSION_STR,
            provenance_qgis_version['provenance_key']: Qgis.QGIS_VERSION,
            provenance_qt_version['provenance_key']: QT_VERSION_STR,
            provenance_inasafe_version['provenance_key']: get_version(),
            provenance_aggregation_layer['provenance_key']: None,
            provenance_aggregation_layer_id['provenance_key']: None,
            provenance_exposure_layer['provenance_key']:
                exposure_layer.source() + '|qgis_provider=ogr',
            provenance_exposure_layer_id['provenance_key']:
                exposure_layer.id(),
            provenance_hazard_layer['provenance_key']:
                hazard_layer.source() + '|qgis_provider=ogr',
            provenance_hazard_layer_id['provenance_key']: hazard_layer.id(),
            provenance_analysis_question['provenance_key']:
                get_analysis_question(hazard, exposure),
            provenance_aggregation_keywords['provenance_key']: None,
            provenance_exposure_keywords['provenance_key']:
                deepcopy(exposure_layer.keywords),
            provenance_hazard_keywords['provenance_key']: deepcopy(
                hazard_layer.keywords),
        }

        # Set up impact function
        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.crs = QgsCoordinateReferenceSystem(4326)
        status, message = impact_function.prepare()
        self.assertEqual(PREPARE_SUCCESS, status, message)
        status, message = impact_function.run()
        self.assertEqual(ANALYSIS_SUCCESS, status, message)

        self.maxDiff = None

        expected_provenance.update({
            provenance_action_checklist['provenance_key']:
                impact_function.action_checklist(),
            provenance_analysis_extent['provenance_key']:
                impact_function.analysis_extent.exportToWkt(),
            provenance_impact_function_name['provenance_key']:
                impact_function.name,
            provenance_impact_function_title['provenance_key']:
                impact_function.title,
            provenance_notes['provenance_key']: impact_function.notes(),
            provenance_requested_extent['provenance_key']: impact_function.
                requested_extent,
            provenance_data_store_uri['provenance_key']: impact_function.
                datastore.uri_path,
            provenance_start_datetime['provenance_key']: impact_function.
                start_datetime,
            provenance_end_datetime['provenance_key']:
                impact_function.end_datetime,
            provenance_duration['provenance_key']: impact_function.duration
        })

        self.assertDictContainsSubset(
            expected_provenance, impact_function.provenance)

        output_layer_provenance_keys = [
            provenance_layer_exposure_summary['provenance_key'],
            provenance_layer_aggregate_hazard_impacted['provenance_key'],
            provenance_layer_aggregation_summary['provenance_key'],
            provenance_layer_analysis_impacted['provenance_key'],
            provenance_layer_exposure_summary_table['provenance_key']
        ]

        for key in output_layer_provenance_keys:
            self.assertIn(key, list(impact_function.provenance.keys()))

    def test_vector_post_minimum_needs_value_generation(self):
        """Test minimum needs postprocessors on vector exposure.

        Test with vector exposure data with population_count_field exists.

        Minimum needs postprocessors is defined to only generate values when
        exposure contains population data.
        """
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'tsunami_vector.geojson')
        exposure_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'population.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        impact_function = ImpactFunction()
        impact_function.aggregation = aggregation_layer
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        status, message = impact_function.prepare()
        self.assertEqual(PREPARE_SUCCESS, status, message)
        return_code, message = impact_function.run()

        self.assertEqual(return_code, ANALYSIS_SUCCESS, message)

        # minimum needs fields should exists in the results
        self._check_minimum_fields_exists(impact_function)

        expected_value = {
            'population': 69,
            'total': 9.0,
            'minimum_needs__rice': 491,
            'minimum_needs__clean_water': 11763,
            'minimum_needs__toilets': 8,
            'minimum_needs__drinking_water': 3072,
            'minimum_needs__family_kits': 35,
            'male': 34,
            'female': 34,
            'youth': 17,
            'adult': 45,
            'elderly': 6,
            'total_affected': 6.0,
        }

        self._check_minimum_fields_value(expected_value, impact_function)

    # expected to fail until raster postprocessor calculation in analysis
    # impacted is fixed
    @unittest.expectedFailure
    def test_raster_post_minimum_needs_value_generation(self):
        """Test minimum needs postprocessors on raster exposure.

        Minimum needs postprocessors is defined to only generate values
        when exposure contains population data.
        Especially important to test, since on raster exposure the population
        field is generated on the fly.
        The postprocessors need to expect generated population field exists.
        """

        # # #
        # Test with raster exposure data with population_exposure_count
        # exists.
        # # #

        hazard_layer = load_test_raster_layer(
            'hazard', 'tsunami_wgs84.tif')
        exposure_layer = load_test_raster_layer(
            'exposure', 'pop_binary_raster_20_20.asc')

        impact_function = ImpactFunction()
        impact_function.exposure = exposure_layer
        impact_function.hazard = hazard_layer
        impact_function.crs = QgsCoordinateReferenceSystem(4326)
        impact_function.prepare()
        return_code, message = impact_function.run()

        self.assertEqual(return_code, ANALYSIS_SUCCESS, message)

        # minimum needs fields should exists in the results
        self._check_minimum_fields_exists(impact_function)

        # TODO: should include demographic postprocessor value too
        expected_value = {
            'total_affected': 9.208200000039128,
            'minimum_needs__rice': 25,
            'minimum_needs__toilets': 0,
            'minimum_needs__drinking_water': 161,
            'minimum_needs__clean_water': 616,
            'male': 4,
            'female': 4,
            'youth': 2,
            'adult': 6,
            'elderly': 0,
            'total': 162.7667000000474,
            'minimum_needs__family_kits': 1,
            'total_not_affected': 153.55850000000828,
        }

        self._check_minimum_fields_value(expected_value, impact_function)

    def _check_minimum_fields_value(self, expected_value, impact_function):
        """Private method for checking minimum needs value."""
        analysis_impacted = impact_function.analysis_impacted
        feature = next(analysis_impacted.getFeatures())
        inasafe_fields = analysis_impacted.keywords['inasafe_fields']
        for field in minimum_needs_fields:
            field_name = inasafe_fields[field['key']]
            field_index = analysis_impacted.fieldNameIndex(field_name)
            value = float(feature[field_index])
            expected = expected_value[field_name]
            self.assertEqual(expected, value)

    def _check_minimum_fields_exists(self, impact_function):
        """Private methods for checking existing minimum fields."""
        message = '{field_key} not exists'
        skip_layers = [layer_purpose_profiling['key']]
        for layer in impact_function.outputs:
            if layer.keywords['layer_purpose'] in skip_layers:
                continue

            inasafe_fields = layer.keywords['inasafe_fields']
            for field in minimum_needs_fields:
                # check fields exists
                self.assertIn(
                    field['key'],
                    inasafe_fields,
                    message.format(field_key=field['key']))

    def test_equality(self):
        """Testing IF equal operator."""
        new_impact_function = ImpactFunction()
        self.assertEqualImpactFunction(
            new_impact_function, new_impact_function)

    @unittest.skipIf(
        not os.path.exists('/Users/ismailsunni/dev/python/inasafe-dev'),
        'The path is not absolute from the output layer metadata.')
    def test_load_from_metadata(self):
        """Test load from metadata."""
        analysis_summary = load_test_vector_layer(
            'output',
            'FloodRasterOnLandCoverPolygon_13October2017_13h16-20.167673',
            'analysis_summary.geojson')
        self.assertEqual(
            analysis_summary.keywords['layer_purpose'],
            layer_purpose_analysis_impacted['key'])
        output_metadata = analysis_summary.keywords
        impact_function = ImpactFunction.load_from_output_metadata(
            output_metadata)
        self.assertIsNotNone(impact_function.exposure)
        self.assertIsNotNone(impact_function.hazard)
        self.assertIsNotNone(impact_function.aggregation)
        self.assertIsNone(impact_function.requested_extent)
        self.assertIsInstance(impact_function.analysis_extent, QgsGeometry)
        self.assertIsInstance(impact_function.datastore, DataStore)
        self.assertIsInstance(impact_function.start_datetime, datetime)
        self.assertIsInstance(impact_function.end_datetime, datetime)
        self.assertLess(0, impact_function.duration)
        self.assertIsNone(impact_function.earthquake_function)
        # Output layers
        self.assertIsInstance(impact_function.exposure_summary, QgsVectorLayer)
        self.assertIsInstance(
            impact_function.aggregate_hazard_impacted, QgsVectorLayer)
        self.assertIsInstance(
            impact_function.aggregation_summary, QgsVectorLayer)
        self.assertIsInstance(
            impact_function.analysis_impacted, QgsVectorLayer)
        self.assertIsInstance(
            impact_function.exposure_summary_table, QgsVectorLayer)
        self.assertIsInstance(impact_function.profiling, QgsVectorLayer)
        self.assertIsInstance(impact_function.impact, QgsVectorLayer)
        self.assertEqual(len(impact_function.outputs), 6)



if __name__ == '__main__':
    unittest.main()
