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

from qgis.core import QgsMapLayerRegistry

from safe.test.utilities import standard_data_path, get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.storage.core import read_layer as safe_read_layer
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

    def test_minimum_needs(self):
        """Test behaviour of the minimum needs function.
        """
        dialog = NeedsCalculatorDialog(PARENT)
        layer = safe_read_layer(shapefile_path)
        attribute = 'displaced'
        new_layer = dialog.minimum_needs(layer, attribute)
        assert new_layer is not None
        attributes = {
            'Drinking Water': 17500,
            'Family Kits': 200,
            'Rice': 2800,
            'Toilets': 50,
            'Clean Water': 67000}
        self.assertDictEqual(attributes, dict(new_layer.data[0]))

    # def Xtest_accept(self):
    #     """Test behaviour of the ok button.
    #
    #     TODO: Make this test useful - Tim
    #     """
    #     # print shapefile_path
    #     layer = QgsVectorLayer(
    #         os.path.basename(shapefile_path),
    #         os.path.dirname(shapefile_path),
    #         'ogr')
    #     layer = None
    #     dialog = MinimumNeeds(PARENT)
    #     dialog.accept()


if __name__ == "__main__":
    # noinspection PyArgumentEqualDefault
    suite = unittest.makeSuite(MinimumNeedsTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
