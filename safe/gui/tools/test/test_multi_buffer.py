import unittest
import os

from safe.definitions.constants import INASAFE_TEST
from safe.definitions.fields import buffer_distance_field, hazard_class_field
from safe.test.utilities import (
    load_test_vector_layer,
    standard_data_path,
    get_qgis_app)
from qgis.PyQt import QtGui

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

from safe.gui.tools.multi_buffer_dialog import (
    MultiBufferDialog)


class MultiBufferTest(unittest.TestCase):

    def setUp(self):
        """Test initialisation run before each test."""
        self.output_path = standard_data_path(
            'hazard', 'volcano_point_multi_buffer.geojson')

    def multi_buffer_test(self, output_path):
        """Function to test the functionality of multi buffer tool.

        :param output_path: The output path given by user on multi buffer
                            dialog.
        :type output_path: str
        """
        dialog = MultiBufferDialog(PARENT, IFACE)
        layer = load_test_vector_layer('hazard', 'volcano_point.geojson')
        QgsProject.instance().addMapLayers([layer])

        dialog.layer.setLayer(layer)
        if output_path:
            dialog.output_form.setText(output_path)

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

        # don't launch keyword wizard. otherwise, the test will hang
        dialog.keyword_wizard_checkbox.setChecked(False)

        dialog.accept()

        layer = dialog.data_store.layer(dialog.output_filename)

        self.assertEqual(len(classification), layer.featureCount())

        # test new fields that generated from the tool
        expected_fields_name = [
            hazard_class_field['field_name'],
            buffer_distance_field['field_name']]

        actual_field_names = [field.name() for field in layer.fields()]
        new_field_names = actual_field_names[-2:]

        self.assertEqual(expected_fields_name, new_field_names)

        # We need to clean generated files
        try:
            os.remove(self.output_path)
            os.remove(self.output_path.replace('.geojson', '.xml'))
        except OSError:
            # With the test_temp_output test, these files don't exist.
            pass

    def test_temp_output(self):
        """Test the multi buffer tool if user do not provide
           specific output path.
        """
        self.multi_buffer_test('')

    def test_user_output(self):
        """Test the multi buffer tool if user provide specific output path."""
        self.multi_buffer_test(self.output_path)

    # This test is failing on some QGIS docker image used for testing.
    @unittest.skipIf(
        os.environ.get('ON_TRAVIS', False),
        'This test is failing in travis, not sure why (since 13 Dec 2017).')
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

        layer = load_test_vector_layer('hazard', 'volcano_point.geojson')
        QgsProject.instance().addMapLayers([layer])

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
