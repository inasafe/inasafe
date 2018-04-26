# coding=utf-8

"""Tests for metadata converter dialog."""

import unittest

from qgis.core import QgsProject
from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import get_qgis_app, load_test_vector_layer
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

from safe.gui.tools.metadata_converter_dialog import MetadataConverterDialog
from safe.test.utilities import load_standard_layers

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestMetadataConverterDialog(unittest.TestCase):

    """Tests for metadata converter dialog."""

    def test_init(self):
        """Test initialization with different layers.."""
        # No layer
        QgsProject.instance().removeAllMapLayers()
        dialog = MetadataConverterDialog(PARENT, IFACE)
        self.assertEqual(dialog.input_layer_combo_box.count(), 0)
        dialog.close()

        # Load many layers
        QgsProject.instance().removeAllMapLayers()
        load_standard_layers()
        dialog = MetadataConverterDialog(PARENT, IFACE)
        self.assertGreater(dialog.input_layer_combo_box.count(), 0)
        dialog.close()

        # Load aggregation layer
        QgsProject.instance().removeAllMapLayers()
        layer = load_test_vector_layer(
            'gisv4', 'aggregation', 'small_grid_complex.geojson', clone=True)
        QgsProject.instance().addMapLayer(layer)
        dialog = MetadataConverterDialog(PARENT, IFACE)
        dialog.input_layer_combo_box.setLayer(layer)
        self.assertEqual(dialog.input_layer_combo_box.count(), 1)
        self.assertFalse(dialog.target_exposure_combo_box.isEnabled())
        dialog.close()

        # Load hazard layer, must have the target exposure
        QgsProject.instance().removeAllMapLayers()
        layer = load_test_vector_layer(
            'gisv4', 'hazard', 'tsunami_vector.geojson', clone=True)
        QgsProject.instance().addMapLayer(layer)
        dialog = MetadataConverterDialog(PARENT, IFACE)
        dialog.input_layer_combo_box.setLayer(layer)
        self.assertEqual(dialog.input_layer_combo_box.count(), 1)
        num_exposures = len(layer.keywords['value_maps'])
        self.assertEqual(
            dialog.target_exposure_combo_box.count(), num_exposures)
        dialog.close()


if __name__ == '__main__':
    unittest.main()
