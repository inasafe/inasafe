# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- *Flood Raster on Population Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'akbargumbira@gmail.com'
__date__ = '11/12/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import unittest
# pylint: disable=unused-import
from collections import OrderedDict
# pylint: enable=unused-import

from safe.storage.core import read_layer
from safe.engine.core import calculate_impact
from safe.impact_functions import get_plugin
from safe.test.utilities import TESTDATA, get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class TestFloodPopulationEvacuation(unittest.TestCase):
    """Test for Flood Building Impact Function."""

    def setUp(self):
        """Run before each test."""
        pass

    def test_flood_population_evacuation(self):
        """Flood population evacuation"""
        population = 'people_jakarta_clip.tif'
        flood_data = 'flood_jakarta_clip.tif'
        plugin_name = 'FloodEvacuationFunction'

        hazard_filename = os.path.join(TESTDATA, flood_data)
        exposure_filename = os.path.join(TESTDATA, population)

        # Calculate impact using API
        hazard_layer = read_layer(hazard_filename)
        exposure_layer = read_layer(exposure_filename)
        impact_function = get_plugin(plugin_name)

        # Call calculation engine
        impact_layer = calculate_impact(
            layers=[hazard_layer, exposure_layer], impact_fcn=impact_function)
        impact_filename = impact_layer.get_filename()
        impact_layer = read_layer(impact_filename)

        keywords = impact_layer.get_keywords()
        # print "keywords", keywords
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
