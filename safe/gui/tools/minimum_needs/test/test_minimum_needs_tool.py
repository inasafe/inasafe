# coding=utf-8
"""
Minimum Needs Tool Test Cases.

InaSAFE Disaster risk assessment tool developed by AusAid and World Bank

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'ismail@kartoza.com'
__date__ = '14/09/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# this import required to enable PyQt API v2 - DO NOT REMOVE!
# noinspection PyUnresolvedReferences
import unittest
import os

from qgis.core import QgsMapLayerRegistry, QgsVectorLayer

from safe.test.utilities import standard_data_path, get_qgis_app
from safe.definitions.fields import displaced_field
from safe.definitions.layer_purposes import layer_purpose_aggregation
from safe.gis.vector.prepare_vector_layer import rename_remove_inasafe_fields
from PyQt4 import QtGui

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.gui.tools.minimum_needs.needs_calculator_dialog import (
    NeedsCalculatorDialog)

shapefile_path = standard_data_path('other', 'minimum_needs.shp')
result_path_base = standard_data_path('other', 'minimum_needs_perka7')


class MinimumNeedsTest(unittest.TestCase):
    """Test class to facilitate importing shakemaps."""

    def setUp(self):
        """Test initialisation run before each test."""
        pass

    def tearDown(self):
        """Run after each test."""
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().removeAllMapLayers()
        for extension in ['shp', 'shx', 'dbf', 'prj', 'keywords']:
            path = result_path_base + '.' + extension
            if os.path.exists(path):
                os.remove(path)

    def test_minimum_needs_calculator(self):
        """Test behaviour of the minimum needs function."""
        dialog = NeedsCalculatorDialog(PARENT)
        layer = QgsVectorLayer(
            shapefile_path,
            os.path.basename(shapefile_path),
            'ogr')
        QgsMapLayerRegistry.instance().addMapLayers([layer])

        # Set selected layer and displaced field
        dialog.layer.setLayer(layer)
        dialog.displaced.setField(u'displaced')

        # run minimum needs function
        dialog.accept()

        # get output layer
        layer = dialog.result_layer

        assert layer is not None
        field_names = [field.name() for field in layer.pendingFields()]
        for feature in layer.getFeatures():
            value = [attribute for attribute in feature.attributes()]

        actual_attributes = dict(zip(field_names, value))

        expected_attributes = {
            'displaced': 1000,
            'minimum_needs__rice': 2800,
            'minimum_needs__drinking_water': 17500,
            'minimum_needs__clean_water': 67000,
            'minimum_needs__family_kits': 200,
            'minimum_needs__toilets': 50}

        self.assertDictEqual(expected_attributes, actual_attributes)

    def test_ok_button(self):
        """Test behaviour of Ok button."""
        # Test Ok button without any input in the combo box
        dialog = NeedsCalculatorDialog(PARENT)
        ok_button = dialog.button_box.button(QtGui.QDialogButtonBox.Ok)

        self.assertFalse(ok_button.isEnabled())

        input_layer = QgsVectorLayer(
            shapefile_path,
            os.path.basename(shapefile_path),
            'ogr')
        QgsMapLayerRegistry.instance().addMapLayers([input_layer])

        # Test Ok button with layer and displaced field
        # selected in the combo box
        dialog.layer.setLayer(input_layer)
        dialog.displaced.setField(u'displaced')

        self.assertTrue(ok_button.isEnabled())

if __name__ == "__main__":
    # noinspection PyArgumentEqualDefault
    suite = unittest.makeSuite(MinimumNeedsTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
