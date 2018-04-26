# coding=utf-8

"""Test for Multi Exposure Impact Function."""

import qgis  # NOQA
import getpass
import unittest
import logging
from copy import deepcopy
from socket import gethostname


from osgeo import gdal
from qgis.PyQt.Qt import PYQT_VERSION_STR
from qgis.PyQt.QtCore import QT_VERSION_STR

from safe.common.version import get_version
from safe.definitions.constants import (
    PREPARE_FAILED_BAD_INPUT,
    PREPARE_SUCCESS,
    ANALYSIS_SUCCESS,
)
from safe.definitions.provenance import (
    provenance_aggregation_keywords,
    provenance_aggregation_layer,
    provenance_aggregation_layer_id,
    provenance_analysis_extent,
    provenance_data_store_uri,
    provenance_duration,
    provenance_end_datetime,
    # provenance_exposure_keywords,
    # provenance_exposure_layer,
    # provenance_exposure_layer_id,
    provenance_gdal_version,
    provenance_hazard_keywords,
    provenance_hazard_layer,
    provenance_hazard_layer_id,
    provenance_host_name,
    provenance_impact_function_name,
    provenance_inasafe_version,
    provenance_os,
    provenance_pyqt_version,
    provenance_qgis_version,
    provenance_qt_version,
    # provenance_requested_extent,
    provenance_start_datetime,
    provenance_user,
    provenance_layer_aggregation_summary,
    provenance_layer_analysis_impacted,
)
from safe.definitions.utilities import definition
from safe.definitions.layer_purposes import (
    layer_purpose_analysis_impacted,
    layer_purpose_aggregation_summary,
    layer_purpose_aggregate_hazard_impacted,
    layer_purpose_exposure_summary,
    layer_purpose_exposure_summary_table,
    layer_purpose_profiling,
)
from safe.test.utilities import qgis_iface, load_test_vector_layer
from safe.utilities.gis import qgis_version
from safe.utilities.utilities import readable_os_version
from safe.impact_function.multi_exposure_wrapper import (
    MultiExposureImpactFunction)


LOGGER = logging.getLogger('InaSAFE')

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


qgis_iface()


class TestMultiExposureImpactFunction(unittest.TestCase):

    """Test Multi Exposure Impact Function."""

    def assertEqualImpactFunction(self, first, second, msg=None):
        """Special assert for impact function equality."""
        if not isinstance(first, MultiExposureImpactFunction):
            message = (
                'First object is not an ImpactFunction object, but a %s' %
                type(second))
            self.fail(self._formatMessage(msg, message))
        if not isinstance(second, MultiExposureImpactFunction):
            message = (
                'Second object is not an ImpactFunction object, but a %s' %
                type(second))
            self.fail(self._formatMessage(msg, message))

        equal, message = first.is_equal(second)
        if not equal:
            self.fail(self._formatMessage('%s\n%s' % (msg, message), message))

    def test_bad_multi(self):
        """Test that the 'prepare' state can failed."""
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        population_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'population.geojson')
        population_bis = load_test_vector_layer(
            'gisv4', 'exposure', 'population_multi_fields.geojson')
        roads_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'roads.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        # Same population exposure
        impact_function = MultiExposureImpactFunction()
        impact_function.hazard = hazard_layer
        impact_function.exposures = [population_layer, population_bis]
        impact_function.aggregation = aggregation_layer
        self.assertTrue(
            impact_function.prepare()[0] == PREPARE_FAILED_BAD_INPUT)
        self.assertDictEqual({}, impact_function.output_layers_expected())

        # Missing exposure layer
        impact_function = MultiExposureImpactFunction()
        impact_function.hazard = hazard_layer
        impact_function.exposures = []
        impact_function.aggregation = aggregation_layer
        self.assertTrue(
            impact_function.prepare()[0] == PREPARE_FAILED_BAD_INPUT)
        self.assertDictEqual({}, impact_function.output_layers_expected())

        # Normal multi exposure
        impact_function = MultiExposureImpactFunction()
        impact_function.hazard = hazard_layer
        impact_function.exposures = [population_layer, roads_layer]
        impact_function.aggregation = aggregation_layer
        self.assertTrue(
            impact_function.prepare()[0] == PREPARE_SUCCESS)

        expected_layers = {
            'Generic Hazard Polygon On Population Polygon': [
                layer_purpose_exposure_summary['key'],
                layer_purpose_aggregate_hazard_impacted['key'],
                layer_purpose_aggregation_summary['key'],
                layer_purpose_analysis_impacted['key'],
                layer_purpose_profiling['key']
            ],
            impact_function.name: [
                layer_purpose_aggregation_summary['key'],
                layer_purpose_analysis_impacted['key']
            ],
            'Generic Hazard Polygon On Roads Line': [
                layer_purpose_exposure_summary['key'],
                layer_purpose_aggregate_hazard_impacted['key'],
                layer_purpose_aggregation_summary['key'],
                layer_purpose_analysis_impacted['key'],
                layer_purpose_exposure_summary_table['key'],
                layer_purpose_profiling['key']
            ]
        }
        self.assertDictEqual(
            expected_layers, impact_function.output_layers_expected())

    def test_equality(self):
        """Testing IF equal operator."""
        new_impact_function = MultiExposureImpactFunction()
        self.assertEqualImpactFunction(
            new_impact_function, new_impact_function)

    def test_multi_exposure(self):
        """Test we can run a multi exposure analysis."""
        hazard_layer = load_test_vector_layer(
            'gisv4', 'hazard', 'classified_vector.geojson')
        building_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'building-points.geojson')
        population_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'population.geojson')
        roads_layer = load_test_vector_layer(
            'gisv4', 'exposure', 'roads.geojson')
        aggregation_layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        impact_function = MultiExposureImpactFunction()
        impact_function.hazard = hazard_layer
        impact_function.exposures = [
            building_layer, population_layer, roads_layer]
        impact_function.aggregation = aggregation_layer

        code, message = impact_function.prepare()
        self.assertEqual(code, PREPARE_SUCCESS, message)

        code, message, exposure = impact_function.run()
        self.assertEqual(code, ANALYSIS_SUCCESS, message)

        # Test provenance
        hazard = definition(hazard_layer.keywords['hazard'])
        # exposure = definition(exposure_layer.keywords['exposure'])
        hazard_category = definition(hazard_layer.keywords['hazard_category'])

        expected_provenance = {
            provenance_gdal_version['provenance_key']: gdal.__version__,
            provenance_host_name['provenance_key']: gethostname(),
            provenance_user['provenance_key']: getpass.getuser(),
            provenance_os['provenance_key']: readable_os_version(),
            provenance_pyqt_version['provenance_key']: PYQT_VERSION_STR,
            provenance_qgis_version['provenance_key']: qgis_version(),
            provenance_qt_version['provenance_key']: QT_VERSION_STR,
            provenance_inasafe_version['provenance_key']: get_version(),
            provenance_aggregation_layer['provenance_key']:
                aggregation_layer.source(),
            provenance_aggregation_layer_id['provenance_key']:
                aggregation_layer.id(),
            # provenance_exposure_layer['provenance_key']:
            #     exposure_layer.source(),
            # provenance_exposure_layer_id['provenance_key']:
            #     exposure_layer.id(),
            provenance_hazard_layer['provenance_key']: hazard_layer.source(),
            provenance_hazard_layer_id['provenance_key']: hazard_layer.id(),
            provenance_aggregation_keywords['provenance_key']: deepcopy(
                aggregation_layer.keywords),
            # provenance_exposure_keywords['provenance_key']:
            #     deepcopy(exposure_layer.keywords),
            provenance_hazard_keywords['provenance_key']: deepcopy(
                hazard_layer.keywords),
        }

        self.maxDiff = None

        expected_provenance.update({
            provenance_analysis_extent['provenance_key']:
                impact_function.analysis_extent.asWkt(),
            provenance_impact_function_name['provenance_key']:
                impact_function.name,
            # provenance_requested_extent['provenance_key']: impact_function.
            #     requested_extent,
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
            provenance_layer_aggregation_summary['provenance_key'],
            provenance_layer_analysis_impacted['provenance_key'],
        ]

        for key in output_layer_provenance_keys:
            self.assertIn(key, list(impact_function.provenance.keys()))

        # Test serialization/deserialization
        output_metadata = impact_function.aggregation_summary.keywords
        new_impact_function = MultiExposureImpactFunction. \
            load_from_output_metadata(output_metadata)
        self.assertEqualImpactFunction(
            impact_function, new_impact_function)

        # Check the analysis layer id equal with the actual layer
        old_analysis_layer_id = impact_function.provenance[
            provenance_layer_analysis_impacted['provenance_key']]
        new_analysis_layer_id = new_impact_function.provenance[
            provenance_layer_analysis_impacted['provenance_key']]
        self.assertEqual(old_analysis_layer_id, new_analysis_layer_id)
