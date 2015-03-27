# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Impact function Test Cases.**

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'akbargumbira@gmail.com'
__date__ = '11/12/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import os
import numpy

from qgis.core import QgsRasterLayer, QgsCoordinateReferenceSystem

from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.impact_functions.earthquake.itb_earthquake_fatality_model\
    .impact_function import ITBFatalityFunction
from safe.test.utilities import test_data_path
from safe.utilities.clipper import extent_to_geoarray, clip_layer
from safe.utilities.gis import get_wgs84_resolution
from safe.storage.core import read_layer
from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


def clip_layers(shake_raster_path, population_raster_path):
    """Clip population (exposure) layer to dimensions of shake data.

    It is possible (though unlikely) that the shake may be clipped too.

    :param shake_raster_path: Path to the shake raster.
    :type shake_raster_path: str

    :param population_raster_path: Path to the population raster.
    :type population_raster_path: str

    :return: Path to the clipped datasets (clipped shake, clipped pop).
    :rtype: tuple(str, str)

    :raise
        FileNotFoundError
    """
    base_name, _ = os.path.splitext(shake_raster_path)
    # noinspection PyCallingNonCallable
    hazard_layer = QgsRasterLayer(shake_raster_path, base_name)
    base_name, _ = os.path.splitext(population_raster_path)
    # noinspection PyCallingNonCallable
    exposure_layer = QgsRasterLayer(population_raster_path, base_name)

    # Reproject all extents to EPSG:4326 if needed
    # noinspection PyCallingNonCallable
    geo_crs = QgsCoordinateReferenceSystem()
    geo_crs.createFromId(4326, QgsCoordinateReferenceSystem.EpsgCrsId)

    # Get the Hazard extents as an array in EPSG:4326
    # Note that we will always clip to this extent regardless of
    # whether the exposure layer completely covers it.
    hazard_geo_extent = extent_to_geoarray(
        hazard_layer.extent(),
        hazard_layer.crs())

    # Next work out the ideal spatial resolution for rasters
    # in the analysis. If layers are not native WGS84, we estimate
    # this based on the geographic extents
    # rather than the layers native extents so that we can pass
    # the ideal WGS84 cell size and extents to the layer prep routines
    # and do all preprocessing in a single operation.
    # All this is done in the function getWGS84resolution
    extra_exposure_keywords = {}

    # Hazard layer is raster
    hazard_geo_cell_size, _ = get_wgs84_resolution(hazard_layer)

    # In case of two raster layers establish common resolution
    exposure_geo_cell_size, _ = get_wgs84_resolution(exposure_layer)

    if hazard_geo_cell_size < exposure_geo_cell_size:
        cell_size = hazard_geo_cell_size
    else:
        cell_size = exposure_geo_cell_size

    # Record native resolution to allow rescaling of exposure data
    if not numpy.allclose(cell_size, exposure_geo_cell_size):
        extra_exposure_keywords['resolution'] = exposure_geo_cell_size

    # The extents should already be correct but the cell size may need
    # resampling, so we pass the hazard layer to the clipper
    clipped_hazard = clip_layer(
        layer=hazard_layer,
        extent=hazard_geo_extent,
        cell_size=cell_size)

    clipped_exposure = clip_layer(
        layer=exposure_layer,
        extent=hazard_geo_extent,
        cell_size=cell_size,
        extra_keywords=extra_exposure_keywords)

    return clipped_hazard, clipped_exposure


class TestITBEarthquakeFatalityFunction(unittest.TestCase):
    """Test for Earthquake on Population Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(ITBFatalityFunction)

    def test_run(self):
        """TestITEarthquakeFatalityFunction: Test running the IF."""
        eq_path = test_data_path('hazard', 'earthquake.tif')
        population_path = test_data_path(
            'exposure', 'pop_binary_raster_20_20.asc')

        clipped_hazard, clipped_exposure = clip_layers(
            shake_raster_path=eq_path,
            population_raster_path=population_path)

        # noinspection PyUnresolvedReferences
        eq_layer = read_layer(
            str(clipped_hazard.source()))
        # noinspection PyUnresolvedReferences
        population_layer = read_layer(
            str(clipped_exposure.source()))

        impact_function = ITBFatalityFunction.instance()
        impact_function.hazard = eq_layer
        impact_function.exposure = population_layer
        impact_function.run()
        impact_layer = impact_function.impact
        # Check the question
        expected_question = ('In the event of earthquake how many '
                             'population might die or be displaced')
        message = 'The question should be %s, but it returns %s' % (
            expected_question, impact_function.question())
        self.assertEqual(expected_question, impact_function.question(), message)
        # Count by hand,
        # 1 = low, 2 = medium, 3 = high
        expected_exposed_per_mmi = {
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0,
            8: 200,
            9: 0
        }
        result = impact_layer.get_keywords('exposed_per_mmi')

        message = 'Expecting %s, but it returns %s' % (expected_exposed_per_mmi, result)
        self.assertEqual(expected_exposed_per_mmi, result, message)

    def test_filter(self):
        """TestITEarthquakeFatalityFunction: Test filtering IF"""
        hazard_keywords = {
            'category': 'hazard',
            'subcategory': 'earthquake',
            'layer_type': 'raster',
            'data_type': 'continuous',
            'unit': 'mmi'
        }

        exposure_keywords = {
            'category': 'exposure',
            'subcategory': 'population',
            'layer_type': 'raster',
            'data_type': 'continuous',
            'unit': 'people_per_pixel'
        }
        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)

        retrieved_if = impact_functions[0].metadata().as_dict()['id']
        expected = ImpactFunctionManager().get_function_id(
            ITBFatalityFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
