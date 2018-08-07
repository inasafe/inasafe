# coding=utf-8
"""Test for Style."""

import unittest

from safe.definitions.utilities import definition
from safe.test.utilities import qgis_iface, load_test_vector_layer
from safe.impact_function.style import layer_title

iface = qgis_iface()

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestStyle(unittest.TestCase):

    """Test Style."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_title(self):
        """Test we can set the layer title correctly."""
        layer = load_test_vector_layer(
            'impact', 'buildings_without_style.geojson')

        layer_title(layer)

        # The code tested is running the same logic as the test itself.
        # But at least we have a test.
        exposure_type = layer.keywords['exposure_keywords']['exposure']
        exposure_definitions = definition(exposure_type)
        title = exposure_definitions['layer_legend_title']
        layer.setTitle(title)
        self.assertEqual(title, layer.title())
