# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Test for Flood Population Evacuation Raster Impact Function.**

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

import os
import unittest

from safe.storage.core import read_layer
from safe.impact_functions.impact_function_manager \
    import ImpactFunctionManager
from safe.impact_functions.inundation\
    .flood_population_evacuation_raster_hazard.impact_function import \
    FloodEvacuationRasterHazardFunction
from safe.test.utilities import TESTDATA, get_qgis_app
from safe.common.utilities import OrderedDict

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestFloodEvacuationFunctionRasterHazard(unittest.TestCase):
    """Test for Flood Vector Building Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.register(FloodEvacuationRasterHazardFunction)

    def test_run(self):
        function = FloodEvacuationRasterHazardFunction.instance()

        population = 'people_jakarta_clip.tif'
        flood_data = 'flood_jakarta_clip.tif'

        hazard_filename = os.path.join(TESTDATA, flood_data)
        exposure_filename = os.path.join(TESTDATA, population)
        hazard_layer = read_layer(hazard_filename)
        exposure_layer = read_layer(exposure_filename)
        # Let's set the extent to the hazard extent
        function.hazard = hazard_layer
        function.exposure = exposure_layer
        function.run()
        impact = function.impact

        # Count of flooded objects is calculated "by the hands"
        # print "keywords", keywords
        keywords = impact.get_keywords()
        evacuated = float(keywords['evacuated'])
        total_needs_full = keywords['total_needs']
        total_needs_weekly = OrderedDict([
            [x['table name'], x['amount']] for x in
            total_needs_full['weekly']
        ])
        total_needs_single = OrderedDict([
            [x['table name'], x['amount']] for x in
            total_needs_full['single']
        ])

        expected_evacuated = 63400
        self.assertEqual(evacuated, expected_evacuated)
        self.assertEqual(total_needs_weekly['Rice [kg]'], 177520)
        self.assertEqual(total_needs_weekly['Family Kits'], 12680)
        self.assertEqual(total_needs_weekly['Drinking Water [l]'], 1109500)
        self.assertEqual(total_needs_weekly['Clean Water [l]'], 4247800)
        self.assertEqual(total_needs_single['Toilets'], 3170)

    def test_filter(self):
        """Test filtering IF from layer keywords"""
        hazard_keywords = {
            'subcategory': 'flood',
            'unit': 'metres_depth',
            'layer_type': 'raster',
            'data_type': 'continuous'
        }

        exposure_keywords = {
            'subcategory': 'population',
            'layer_type': 'raster',
            'data_type': 'continuous'
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)
        retrieved_IF = impact_functions[0].metadata().as_dict()['id']
        self.assertEqual('FloodEvacuationRasterHazardFunction',
                         retrieved_IF,
                         'Expecting FloodEvacuationRasterHazardFunction.'
                         'But got %s instead' %
                         retrieved_IF)
