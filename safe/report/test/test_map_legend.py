# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Map  Legend test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@kartoza.com'
__date__ = '12/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import logging

from qgis.core import QgsMapLayerRegistry, QgsFillSymbolV2
from PyQt4 import QtGui

from safe.common.utilities import temp_dir, unique_filename
from safe.test.utilities import (
    check_images,
    load_layer,
    get_qgis_app,
    test_data_path)
from safe.report.map_legend import MapLegend

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
LOGGER = logging.getLogger('InaSAFE')


class MapLegendTest(unittest.TestCase):
    """Test the InaSAFE Map generator"""
    def setUp(self):
        """Setup fixture run before each tests"""
        # noinspection PyArgumentList
        registry = QgsMapLayerRegistry.instance()
        for layer in registry.mapLayers():
            registry.removeMapLayer(layer)

    def test_get_legend(self):
        """Getting a legend for a generic layer works."""
        impact_layer_path = test_data_path(
            'impact', 'buildings_inundated_entire_area.shp')
        layer, _ = load_layer(impact_layer_path)
        map_legend = MapLegend(layer)
        self.assertTrue(map_legend.layer is not None)
        legend = map_legend.get_legend()
        path = unique_filename(
            prefix='get_legend',
            suffix='.png',
            dir=temp_dir('test'))
        legend.save(path, 'PNG')

        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so myControlImages is a list
        # of 'known good' renders.
        tolerance = 0  # to allow for version number changes in disclaimer

        flag, message = check_images('get_legend', path, tolerance)
        message += (
            '\nWe want these images to match, if they do already '
            'copy the test image generated to create a new control '
            'image.')
        self.assertTrue(flag, message)

    def test_get_vector_legend(self):
        """Getting a legend for a vector layer works.

        .. note:: This test is not related do thousand separator since we
            insert our own legend notes and our own layer.
        """
        vector_layer_path = test_data_path(
            'impact', 'population_affected_district_jakarta.shp')
        layer, _ = load_layer(vector_layer_path)
        map_legend = MapLegend(
            layer,
            legend_notes='Thousand separator represented by \',\'',
            legend_units='(people per cell)')
        image = map_legend.vector_legend()
        path = unique_filename(
            prefix='get_vector_legend',
            suffix='.png',
            dir=temp_dir('test'))
        image.save(path, 'PNG')
        LOGGER.debug(path)
        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so myControlImages is a list
        # of 'known good' renders.

        tolerance = 0  # to allow for version number changes in disclaimer
        flag, message = check_images(
            'get_vector_legend', path, tolerance)
        message += (
            '\nWe want these images to match, if they do already '
            'copy the test image generated to create a new control image.')
        self.assertTrue(flag, message)

    def test_get_raster_legend(self):
        """Getting a legend for a raster layer works."""
        raster_path = test_data_path(
            'impact', 'flood_on_population.tif')
        layer, _ = load_layer(raster_path)
        map_legend = MapLegend(layer)
        image = map_legend.raster_legend()
        path = unique_filename(
            prefix='get_raster_legend',
            suffix='.png',
            dir=temp_dir('test'))
        image.save(path, 'PNG')
        LOGGER.debug(path)
        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so myControlImages is a list
        # of 'known good' renders.

        tolerance = 0  # to allow for version number changes in disclaimer
        flag, message = check_images(
            'get_raster_legend', path, tolerance)
        message += (
            '\nWe want these images to match, if they do already copy the test'
            ' image generated to create a new control image.')
        self.assertTrue(flag, message)

    def test_add_symbol_to_legend(self):
        """Test we can add a symbol to the legend."""
        raster_path = test_data_path(
            'impact', 'flood_on_population.tif')
        layer, _ = load_layer(raster_path)
        map_legend = MapLegend(layer)
        symbol = QgsFillSymbolV2()
        symbol.setColor(QtGui.QColor(12, 34, 56))
        map_legend.add_symbol(
            symbol,
            minimum=0,
            # expect 2.0303 in legend
            maximum=2.02030,
            label='Foo')
        path = unique_filename(
            prefix='add_symbol_to_legend',
            suffix='.png',
            dir=temp_dir('test'))
        map_legend.get_legend().save(path, 'PNG')
        LOGGER.debug(path)
        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so myControlImages is a list
        # of 'known good' renders.

        tolerance = 0  # to allow for version number changes in disclaimer
        flag, message = check_images(
            'add_symbol_to_legend', path, tolerance)
        message += (
            '\nWe want these images to match, if they do already, copy the '
            'test image generated to create a new control image.')
        self.assertTrue(flag, message)

    def test_add_class_to_legend(self):
        """Test we can add a class to the map legend."""
        raster_path = test_data_path(
            'impact', 'flood_on_population.tif')
        layer, _ = load_layer(raster_path)
        map_legend = MapLegend(layer)
        colour = QtGui.QColor(12, 34, 126)
        map_legend.add_class(
            colour,
            label='bar')
        map_legend.add_class(
            colour,
            label='foo')
        path = unique_filename(
            prefix='add_class_to_legend',
            suffix='.png',
            dir=temp_dir('test'))
        map_legend.get_legend().save(path, 'PNG')
        LOGGER.debug(path)
        # As we have discovered, different versions of Qt and
        # OS platforms cause different output, so place any other possible
        # variants in the safe_qgis/test_data/images/ dir e.g.
        # addClassToLegend-variantUbuntu13.04.png
        tolerance = 0  # to allow for version number changes in disclaimer
        flag, message = check_images(
            'add_class_to_legend', path, tolerance)
        message += (
            '\nWe want these images to match, if they do already copy the test'
            ' image generated to create a new control image.')
        self.assertTrue(flag, message)

if __name__ == '__main__':
    suite = unittest.makeSuite(MapLegendTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
