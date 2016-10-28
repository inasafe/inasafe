# coding=utf-8

import unittest

from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.definitionsv4.fields import total_field, exposure_count_field
from safe.gisv4.vector.aggregate_summary import aggregate_summary


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestAggregateSummary(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_aggregate_summary(self):
        """Test we can aggregate the impact to the aggregation."""

        aggregate_hazard = load_test_vector_layer(
            'gisv4',
            'intermediate',
            'aggregate_classified_hazard.geojson',
            clone=True)

        impact = load_test_vector_layer(
            'gisv4',
            'impacts',
            'building-points-classified-vector.geojson')

        layer = aggregate_summary(aggregate_hazard, impact)

        self.assertIn(total_field['key'], layer.keywords['inasafe_fields'])
