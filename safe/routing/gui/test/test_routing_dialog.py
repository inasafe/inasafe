# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid / DFAT -
**New Metadata for SAFE.**

Contact : etienne@kartoza.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

# noinspection PyUnresolvedReferences
import unittest
import logging

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from os import remove
from os.path import dirname, join, exists
from safe.test.utilities import load_layers, get_qgis_app, test_data_path
from qgis.core import QGis
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
LOGGER = logging.getLogger('InaSAFE')

from safe.routing.gui.routing_dialog import RoutingDialog
from safe.common.utilities import unique_filename

@unittest.skipIf(
    QGis.QGIS_VERSION_INT < 20900, 'Need QGIS 2.9 for running the unit tests')
class RoutingDialogTest(unittest.TestCase):
    """Test Routing Dialog widget."""

    def setUp(self):
        self.dialog = RoutingDialog(PARENT, IFACE)

    def tearDown(self):
        pass

    def test_validate(self):
        """Validate function work as expected."""

        # No layers in the map canvas.
        self.assertFalse(self.dialog.validate())

        idp_file_path = test_data_path('idp', 'potential-idp.shp')
        flood_file_path = test_data_path(
            'hazard', 'flood_multipart_polygons.shp')
        roads_file_path = test_data_path('exposure', 'roads.shp')

        layers = [idp_file_path, flood_file_path, roads_file_path]
        load_layers(layers, True)
        self.dialog.populate_combo()
        self.assertTrue(self.dialog.validate())

        layers = [flood_file_path, roads_file_path]
        load_layers(layers, True)
        self.dialog.populate_combo()
        self.assertFalse(self.dialog.validate())

        layers = [idp_file_path, roads_file_path]
        load_layers(layers, True)
        self.dialog.populate_combo()
        self.assertFalse(self.dialog.validate())

        layers = [idp_file_path, flood_file_path]
        load_layers(layers, True)
        self.dialog.populate_combo()
        self.assertFalse(self.dialog.validate())

    def test_replace_value(self):
        """Test if we can replace a value in a file."""
        file_path = unique_filename(suffix='.txt')
        f = open(file_path, 'w')
        f.write('foobarfoo')
        f.close()

        self.dialog.replace_value(file_path, 'bar', 'foo')

        f = open(file_path, 'r')
        self.assertEqual(f.read(), 'foofoofoo')
        f.close()
        remove(file_path)

    def test_processing_model(self):
        """Test against the processing model."""
        routable_model = join(dirname(
            dirname(dirname(__file__))), 'models', 'inasafe_network.model')

        # We can't test the method because Processing it not fully loaded.
        self.assertTrue(exists(routable_model))
