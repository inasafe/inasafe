# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Converter Test Cases.**

Contact : kolesov.dm@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'kolesov.dm@gmail.com'
__date__ = '20/01/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import unittest

from safe.engine.core import calculate_impact
from safe.storage.core import read_layer

from safe.common.testing import UNITDATA, get_qgis_app
from safe.common.utilities import OrderedDict
from safe.common.exceptions import GetDataError

from safe.impact_functions import get_plugins


# We need QGIS_APP started during the tests
# to convert SAFE layers to QGIS layers
from safe.storage.raster import qgis_imported
if qgis_imported:   # Import QgsRasterLayer if qgis is available
    QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class Test_gis_native_impact_functions(unittest.TestCase):

    def _get_impact_function(self,
                             hazard_filename,
                             exposure_filename,
                             plugin_name,
                             impact_parameters):
        """Helper to run impact function

        This method is based on
        safe.engine.test_engine.test_flood_population_evacuation
        """

        # Calculate impact using API
        hazard = read_layer(hazard_filename)
        exposure = read_layer(exposure_filename)

        plugin_list = get_plugins(plugin_name)
        assert len(plugin_list) == 1
        assert plugin_list[0].keys()[0] == plugin_name

        IF = plugin_list[0][plugin_name]
        # Set up IF extent
        hazard_extent = hazard.extent
        exposure_extent = exposure.extent
        extent = [
            max(hazard_extent[0], exposure_extent[0]),
            max(hazard_extent[2], exposure_extent[2]),
            min(hazard_extent[1], exposure_extent[1]),
            min(hazard_extent[3], exposure_extent[3])
        ]

        IF.parameters = impact_parameters

        # Call calculation engine
        impact_layer = calculate_impact(layers=[hazard, exposure],
                                        impact_fcn=IF,
                                        extent=extent)

        impact_filename = impact_layer.get_filename()
        I = read_layer(impact_filename)

        return I


    def test_building_native_impact_experrimental(self):
        """Test flood_building_native_impact_experimental
        """
        hazard_name = os.path.join(UNITDATA,
            'hazard',
            'multipart_polygons_osm_4326.shp')
        exposure_name = os.path.join(UNITDATA,
            'exposure',
            'buildings_osm_4326.shp')
        plugin_name = "FloodNativePolygonExperimentalFunction"

        params = OrderedDict(
            [
                ('target_field', 'FLOODED'),
                ('building_type_field', 'TYPE'),
                ('affected_field', 'FLOOD'),
                ('affected_value', 'YES')
            ]
        )

        # The params are not match field names of hazard
        self.assertRaises(
            GetDataError,
            self._get_impact_function,
            hazard_name,
            exposure_name,
            plugin_name,
            params
        )

        # Set up real field name
        params = OrderedDict(
            [
                ('target_field', 'FLOODED'),
                ('building_type_field', 'TYPE'),
                ('affected_field', 'FLOODPRONE'),
                ('affected_value', 'YES')
            ]
        )
        impact = self._get_impact_function(
            hazard_name,
            exposure_name,
            plugin_name,
            params
        )

        keywords = impact.get_keywords()
        self.assertEquals(
            params['target_field'],
            keywords['target_field']
        )

        # Count of flooded objects is calculated "by the hands"
        # the count = 68
        count = sum(impact.get_data(attribute=keywords['target_field']))
        self.assertEquals(count, 68)

    test_building_native_impact_experrimental.slow = True


if __name__ == '__main__':
    suite = unittest.makeSuite(Test_gis_native_impact_functions, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)