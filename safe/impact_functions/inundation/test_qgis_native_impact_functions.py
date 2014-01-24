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
if qgis_imported:
    QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
    from qgis.core import QgsVectorLayer, QgsRasterLayer


class Wrapper():
    """
    A wrapper around qgis layers. It implements get_layer method of
    safe_qgis.utilities.qgis_layer_wrapper.QgisWrapper

    Also it provides a stub for get_keyword
    """

    def __init__(self, layer, keyword='hazard', name="Test"):
        """Create the wrapper

        :param layer:       Qgis layer
        :type layer:        QgsMapLayer

        :param keyword:     A layer's category keyword
        :type keyword:      Basestring or None
        """

        self.data = layer

        self.keywords = {'category': keyword}
        self.name = name

    def get_name(self):
        return self.name

    def get_keywords(self, key=None):
        if key is None:
            return self.keywords
        return self.keywords[key]

    def get_layer(self):
        return self.data


class Test_gis_native_impact_functions(unittest.TestCase):

    def _get_impact_function(self,
                             qgis_hazard,
                             qgis_exposure,
                             plugin_name,
                             impact_parameters):
        """Helper to run impact function

        This method is based on
        safe.engine.test_engine.test_flood_population_evacuation
        """

        # Calculate impact using API
        # hazard = read_layer(hazard_filename)
        # exposure = read_layer(exposure_filename)

        hazard = Wrapper(qgis_hazard, 'hazard', 'Hazard')
        exposure = Wrapper(qgis_exposure, 'exposure', 'Exposure')

        plugin_list = get_plugins(plugin_name)
        assert len(plugin_list) == 1
        assert plugin_list[0].keys()[0] == plugin_name

        IF = plugin_list[0][plugin_name]
        # Set up IF extent
        hazard_extent = hazard.get_layer().extent()
        hazard_extent = [
            hazard_extent.xMinimum(),
            hazard_extent.yMinimum(),
            hazard_extent.xMaximum(),
            hazard_extent.yMaximum()
        ]
        exposure_extent = exposure.get_layer().extent()
        exposure_extent = [
            exposure_extent.xMinimum(),
            exposure_extent.yMinimum(),
            exposure_extent.xMaximum(),
            exposure_extent.yMaximum()
        ]
        extent = [
            max(hazard_extent[0], exposure_extent[0]),
            max(hazard_extent[1], exposure_extent[1]),
            min(hazard_extent[2], exposure_extent[2]),
            min(hazard_extent[3], exposure_extent[3])
        ]

        IF.parameters = impact_parameters

        # Call calculation engine
        impact_layer = calculate_impact(layers=[hazard, exposure],
                                        impact_fcn=IF,
                                        extent=extent,
                                        check_integrity=False)

        impact_filename = impact_layer.get_filename()
        I = read_layer(impact_filename)

        return I

    def test_building_native_impact_experimental(self):
        """Test flood_building_native_impact_experimental
        """
        hazard_name = os.path.join(UNITDATA,
            'hazard',
            'multipart_polygons_osm_4326.shp')
        qgis_hazard = QgsVectorLayer(
            hazard_name,
            'HAZARD',
            'ogr'
        )

        exposure_name = os.path.join(UNITDATA,
            'exposure',
            'buildings_osm_4326.shp')
        qgis_exposure = QgsVectorLayer(
            exposure_name,
            'EXPOSURE',
            'ogr'
        )

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
            qgis_hazard,
            qgis_exposure,
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
            qgis_hazard,
            qgis_exposure,
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

    test_building_native_impact_experimental.slow = True


if __name__ == '__main__':
    suite = unittest.makeSuite(Test_gis_native_impact_functions, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
