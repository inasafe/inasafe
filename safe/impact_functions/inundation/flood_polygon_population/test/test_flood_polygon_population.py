# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- *Flood Vector on Population Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'Rizky Maulana Nugraha'
__date__ = '20/03/2015'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import numpy

from safe.storage.core import read_layer
from safe.impact_functions.impact_function_manager \
    import ImpactFunctionManager
from safe.test.utilities import get_qgis_app, test_data_path
from safe.impact_functions.inundation.flood_polygon_population\
    .impact_function import FloodEvacuationVectorHazardFunction

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestFloodEvacuationVectorHazardFunction(unittest.TestCase):
    """Test for Flood Vector Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(FloodEvacuationVectorHazardFunction)

    def test_run(self):
        function = FloodEvacuationVectorHazardFunction.instance()

        hazard_path = test_data_path('hazard', 'flood_multipart_polygons.shp')
        exposure_path = test_data_path(
            'exposure', 'pop_binary_raster_20_20.asc')
        hazard_layer = read_layer(hazard_path)
        exposure_layer = read_layer(exposure_path)

        function.hazard = hazard_layer
        function.exposure = exposure_layer
        function.parameters['affected_field'] = 'FLOODPRONE'
        function.parameters['affected_value'] = 'YES'
        function.run()
        impact = function.impact

        keywords = impact.get_keywords()
        # print "keywords", keywords
        affected_population = numpy.nansum(impact.get_data())
        total_population = keywords['total_population']

        self.assertEqual(affected_population, 20)
        self.assertEqual(total_population, 200)

    def test_filter(self):
        """Test filtering IF from layer keywords"""
        hazard_keywords = {
            'layer_purpose': 'hazard',
            'layer_mode': 'classified',
            'layer_geometry': 'polygon',
            'hazard': 'flood',
            'hazard_category': 'single_event',
            'vector_hazard_classification': 'flood_vector_hazard_classes'
        }

        exposure_keywords = {
            'layer_purpose': 'exposure',
            'layer_mode': 'continuous',
            'layer_geometry': 'raster',
            'exposure': 'population',
            'exposure_unit': 'count'
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)

        retrieved_if = impact_functions[0].metadata().as_dict()['id']
        expected = ImpactFunctionManager().get_function_id(
            FloodEvacuationVectorHazardFunction)
        message = 'Expecting %s, but getting %s instead' % (
            expected, retrieved_if)
        self.assertEqual(expected, retrieved_if, message)
