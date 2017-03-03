# coding=utf-8

import unittest

from safe.test.utilities import (
    load_test_vector_layer, load_test_raster_layer, qgis_iface)

from safe.definitions.utilities import definition
from safe.definitions.fields import (
    total_field,
    exposure_class_field,
    hazard_class_field,
    hazard_count_field,
    exposure_count_field
)
from safe.definitions.constants import PREPARE_SUCCESS, ANALYSIS_SUCCESS
from safe.gis.vector.tools import read_dynamic_inasafe_field
from safe.gis.vector.summary_1_aggregate_hazard import (
    aggregate_hazard_summary)
from safe.gis.vector.summary_2_aggregation import aggregation_summary
from safe.gis.vector.summary_3_analysis import analysis_summary
from safe.gis.vector.summary_4_exposure_summary_table import (
    exposure_summary_table)
from safe.impact_function.impact_function import ImpactFunction
from safe.gis.sanity_check import check_inasafe_fields

qgis_iface()

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestAggregateSummary(unittest.TestCase):

    """Summary calculation tests."""

    def test_impact_summary(self):
        """Test we can aggregate the impact to the aggregate hazard."""
        impact = load_test_vector_layer(
            'gisv4',
            'impacts',
            'building-points-classified-vector.geojson')

        aggregate_hazard = load_test_vector_layer(
            'gisv4',
            'intermediate',
            'aggregate_classified_hazard.geojson',
            clone=True)

        aggregate_hazard.keywords['hazard_keywords'] = {
            'classification': 'generic_hazard_classes'
        }
        impact.keywords['classification'] = {
            'classification': 'generic_structure_classes'
        }

        number_of_fields = aggregate_hazard.fields().count()

        layer = aggregate_hazard_summary(impact, aggregate_hazard)

        self.assertIn(total_field['key'], layer.keywords['inasafe_fields'])

        check_inasafe_fields(layer)

        fields = impact.keywords['inasafe_fields']
        exposure_class = fields[exposure_class_field['key']]
        exposure_class_index = impact.fieldNameIndex(exposure_class)
        unique_exposure = impact.uniqueValues(exposure_class_index)

        # One field per exposure type
        # Number of previous fields in the layer
        # 3 : 1 fields for absolute values, 2 fields for affected and total.
        self.assertEqual(
            layer.fields().count(),
            len(unique_exposure) + number_of_fields + 3
        )

    def test_aggregation_summary(self):
        """Test we can aggregate the aggregate hazard to the aggregation."""
        aggregate_hazard = load_test_vector_layer(
            'gisv4',
            'intermediate',
            'aggregate_classified_hazard_summary.geojson')

        aggregation = load_test_vector_layer(
            'gisv4',
            'aggregation',
            'aggregation_cleaned.geojson',
            clone=True)

        number_of_fields = aggregation.fields().count()

        layer = aggregation_summary(aggregate_hazard, aggregation)

        check_inasafe_fields(layer)

        # I need the number of unique exposure
        pattern = exposure_count_field['key']
        pattern = pattern.replace('%s', '')
        unique_exposure = []
        inasafe_fields = aggregate_hazard.keywords['inasafe_fields']
        for key, name_field in inasafe_fields.iteritems():
            if key.endswith(pattern):
                unique_exposure.append(key.replace(pattern, ''))

        self.assertEqual(
            layer.fields().count(),
            len(unique_exposure) + number_of_fields + 1
        )

    def test_analysis_summary(self):
        """Test we can aggregate the aggregate hazard to the analysis."""
        aggregate_hazard = load_test_vector_layer(
            'gisv4',
            'intermediate',
            'aggregate_classified_hazard_summary.geojson')

        aggregate_hazard.keywords['hazard_keywords'] = {
            'classification': 'generic_hazard_classes'
        }

        analysis = load_test_vector_layer(
            'gisv4',
            'intermediate',
            'analysis.geojson',
            clone=True)

        number_of_fields = analysis.fields().count()

        layer = analysis_summary(aggregate_hazard, analysis)

        check_inasafe_fields(layer)

        fields = aggregate_hazard.keywords['inasafe_fields']
        hazard_class = fields[hazard_class_field['key']]
        hazard_class_index = aggregate_hazard.fieldNameIndex(hazard_class)
        unique_hazard = aggregate_hazard.uniqueValues(hazard_class_index)

        # expected number of fields:
        # - one field for each hazard class
        # - 2 fields for analysis id and analysis name
        # - 4 fields for total affected, not_affected, not exposed and total
        self.assertEqual(
            layer.fields().count(),
            len(unique_hazard) + number_of_fields + 4
        )

    def test_exposure_summary_table(self):
        """Test we can produce the breakdown for the exposure type."""
        aggregate_hazard = load_test_vector_layer(
            'gisv4',
            'intermediate',
            'aggregate_classified_hazard_summary.geojson')

        aggregate_hazard.keywords['hazard_keywords'] = {
            'classification': 'generic_hazard_classes'
        }

        # I need the number of unique exposure
        unique_exposure = read_dynamic_inasafe_field(
            aggregate_hazard.keywords['inasafe_fields'],
            exposure_count_field)

        # I need the number of unique hazard
        fields = aggregate_hazard.keywords['inasafe_fields']
        hazard_class = fields[hazard_class_field['key']]
        hazard_class_index = aggregate_hazard.fieldNameIndex(hazard_class)
        unique_hazard = aggregate_hazard.uniqueValues(hazard_class_index)

        layer = exposure_summary_table(aggregate_hazard)

        check_inasafe_fields(layer)

        self.assertEqual(len(unique_exposure), layer.featureCount())

        # We should have
        # one column per hazard
        # one for the exposure
        # one for total affected
        # one for total not affected
        # one for total not exposed
        # one for total
        self.assertEqual(layer.fields().count(), len(unique_hazard) + 5)

    def test_analysis_earthquake_summary(self):
        """Test we can compute summary after an EQ on population."""
        hazard = load_test_raster_layer('gisv4', 'hazard', 'earthquake.asc')
        exposure = load_test_raster_layer(
            'gisv4', 'exposure', 'raster', 'population.asc')
        aggregation = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid.geojson')

        impact_function = ImpactFunction()
        impact_function.hazard = hazard
        impact_function.exposure = exposure
        impact_function.aggregation = aggregation
        status, message = impact_function.prepare()
        self.assertEqual(PREPARE_SUCCESS, status, message)
        status, message = impact_function.run()
        self.assertEqual(ANALYSIS_SUCCESS, status, message)

        layer = impact_function.analysis_impacted
        classification = hazard.keywords['classification']
        classes = definition(classification)['classes']
        for hazard_class in classes:
            field_name = hazard_count_field['field_name'] % hazard_class['key']
            message = '%s is not found in the EQ summary layer.' % field_name
            self.assertNotEqual(-1, layer.fieldNameIndex(field_name), message)

        check_inasafe_fields(impact_function.analysis_impacted)
        check_inasafe_fields(impact_function.aggregation_summary)
