import unittest
import os

from qgis.core import QgsVectorLayer, QgsMapLayerRegistry
from safe.test.utilities import standard_data_path, get_qgis_app
from PyQt4 import QtGui

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.gui.tools.multi_buffer_dialog import (
    MultiBufferDialog)

input_path = standard_data_path('hazard', 'volcano_point.geojson')
output_path = standard_data_path(
    'hazard', 'volcano_point_multi_buffer.geojson')


class MultiBufferTest(unittest.TestCase):

    def setUp(self):
        """Test initialisation run before each test."""
        pass

    def tearDown(self):
        """Run after each test."""
        pass

    def test_multi_buffer(self):
        """Test the functionality of the multi buffer tool."""
        dialog = MultiBufferDialog(PARENT)
        layer = QgsVectorLayer(
            input_path,
            os.path.basename(input_path),
            'ogr')
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        dialog.layer.setLayer(layer)
        self.assertEqual(output_path, dialog.output_form.text())

        classification = {
            500: 'high',
            1500: 'medium',
            2000: 'low'}

        for item in classification:
            dialog.radius_form.setValue(item)
            dialog.class_form.setText(classification[item])
            dialog.populate_hazard_classification()

        self.assertEqual(
            len(classification), dialog.hazard_class_form.count())

        dialog.accept()

        layer = QgsVectorLayer(
            output_path,
            os.path.basename(output_path),
            'ogr')

        self.assertEqual(len(classification), layer.featureCount())

    def test_button_behaviour(self):
        """Test behaviour of each button on multi buffer dialog."""
        dialog = MultiBufferDialog(PARENT)
        directory_button = dialog.directory_button
        add_class_button = dialog.add_class_button
        ok_button = dialog.button_box.button(QtGui.QDialogButtonBox.Ok)

        # Test every button without any input in the combo box.
        self.assertFalse(directory_button.isEnabled())
        self.assertFalse(add_class_button.isEnabled())
        self.assertFalse(ok_button.isEnabled())

        layer = QgsVectorLayer(
            input_path,
            os.path.basename(input_path),
            'ogr')
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        # Test directory button after a layer is selected
        dialog.layer.setLayer(layer)
        self.assertTrue(directory_button.isEnabled())

        # Test add class button after radius and class form is filled
        dialog.radius_form.setValue(500)
        dialog.class_form.setText('high')
        self.assertTrue(add_class_button.isEnabled())

        # Test ok button after hazard class is populated
        dialog.populate_hazard_classification()
        self.assertTrue(ok_button.isEnabled())
