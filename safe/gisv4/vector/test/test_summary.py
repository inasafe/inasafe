# coding=utf-8

import unittest

from safe.test.utilities import (
    get_qgis_app,
    check_inasafe_fields,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.definitionsv4.fields import (
    total_field, exposure_class_field, hazard_class_field)
from safe.gisv4.vector.summary_1_impact import impact_summary
from safe.gisv4.vector.summary_3_analysis import analysis_summary

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestAggregateSummary(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

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

        number_of_fields = aggregate_hazard.fields().count()

        layer = impact_summary(impact, aggregate_hazard)

        self.assertIn(total_field['key'], layer.keywords['inasafe_fields'])

        result = check_inasafe_fields(layer)
        self.assertTrue(result[0], result[1])

        fields = impact.keywords['inasafe_fields']
        exposure_class = fields[exposure_class_field['key']]
        exposure_class_index = impact.fieldNameIndex(exposure_class)
        unique_exposure = impact.uniqueValues(exposure_class_index)

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

        result = check_inasafe_fields(layer)
        self.assertTrue(result[0], result[1])

        fields = aggregate_hazard.keywords['inasafe_fields']
        hazard_class = fields[hazard_class_field['key']]
        hazard_class_index = aggregate_hazard.fieldNameIndex(hazard_class)
        unique_hazard = aggregate_hazard.uniqueValues(hazard_class_index)

        self.assertEqual(
            layer.fields().count(),
            len(unique_hazard) + number_of_fields + 2
        )
