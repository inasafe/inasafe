# coding=utf-8

import unittest

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

from safe.gis.vector.recompute_counts import recompute_counts

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestRecomputeCounts(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_recompute_counts(self):
        """Test we can recompute counts in a layer."""
        layer = load_test_vector_layer(
            'gisv4', 'intermediate', 'impact_before_recount.geojson',
            clone=True)
        layer.keywords['exposure_keywords'] = {
            'exposure': 'population'
        }
        count_fields = layer.fields().count()

        layer = recompute_counts(layer)

        self.assertEqual(count_fields, layer.fields().count())
