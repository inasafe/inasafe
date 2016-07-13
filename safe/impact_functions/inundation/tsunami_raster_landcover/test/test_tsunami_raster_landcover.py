# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- *Classified Hazard Land Cover Impact Function Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

import unittest
from qgis.core import QgsVectorLayer, QgsRasterLayer
from safe.test.utilities import get_qgis_app, standard_data_path
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
from safe.impact_functions.inundation.tsunami_raster_landcover. \
    impact_function import TsunamiRasterLandcoverFunction
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.storage.utilities import safe_to_qgis_layer
from safe.utilities.pivot_table import PivotTable, FlatTable


class TestTsunamiRasterLandCoverFunction(unittest.TestCase):
    """Test for Tsunami Raster Land Cover Impact Function."""

    def setUp(self):
        registry = ImpactFunctionManager().registry
        registry.clear()
        registry.register(TsunamiRasterLandcoverFunction)

    def test_run(self):
        function = TsunamiRasterLandcoverFunction.instance()

        hazard_path = standard_data_path('hazard', 'tsunami_wgs84.tif')
        exposure_path = standard_data_path('exposure', 'landcover.shp')
        # noinspection PyCallingNonCallable
        hazard_layer = QgsRasterLayer(hazard_path, 'Tsunami')
        # noinspection PyCallingNonCallable
        exposure_layer = QgsVectorLayer(exposure_path, 'Land Cover', 'ogr')
        self.assertTrue(hazard_layer.isValid())
        self.assertTrue(exposure_layer.isValid())

        rect_extent = [106.5, -6.5, 107, -6]
        function.hazard = hazard_layer
        function.exposure = exposure_layer
        function.requested_extent = rect_extent
        function.run()
        impact = function.impact
        impact = safe_to_qgis_layer(impact)

        expected = {
            'data':
                [[u'Population', u'Dry Zone', None, 793.6916054134609],
                 [u'Water', u'Low Hazard Zone', None, 16.298813953855912],
                 [u'Population', u'Very High Hazard Zone', None,
                  12.45623642166847],
                 [u'Water', u'Very High Hazard Zone', None,
                  0.08036139883589728],
                 [u'Water', u'Medium Hazard Zone', None, 12.1033540507973],
                 [u'Population', u'Low Hazard Zone', None, 28.866862427357326],
                 [u'Water', u'Dry Zone', None, 164.67113858186028],
                 [u'Meadow', u'Dry Zone', None, 249.95443689559693],
                 [u'Population', u'Medium Hazard Zone', None,
                  30.69211822286981],
                 [u'Water', u'High Hazard Zone', None, 5.835228232982915],
                 [u'Population', u'High Hazard Zone', None, 29.72789895440279],
                 [u'Forest', u'Dry Zone', None, 99.489344261353]],
            'groups': ('landcover', 'hazard', 'zone')}
        ordered_columns = function.impact.impact_data.get('ordered columns')
        affected_columns = function.impact.impact_data.get('affected columns')
        expected = FlatTable().from_dict(
                groups=expected['groups'],
                data=expected['data'],)
        expected = PivotTable(
            expected,
            row_field='landcover',
            column_field='hazard',
            columns=ordered_columns,
            affected_columns=affected_columns)

        self.assertEqual(impact.dataProvider().featureCount(), 72)
        table = function.impact.impact_data['impact table']
        table = FlatTable().from_dict(
            groups=table['groups'],
            data=table['data'],)
        table = PivotTable(
            table,
            row_field='landcover',
            column_field='hazard',
            columns=ordered_columns,
            affected_columns=affected_columns)
        self.assertListEqual(expected.total_rows, table.total_rows)
        self.assertListEqual(expected.total_columns, table.total_columns)
        self.assertListEqual(expected.total_rows_affected, table.total_rows_affected)
        self.assertEqual(expected.total_affected, table.total_affected)
        self.assertListEqual(expected.rows, table.rows)
        self.assertListEqual(expected.columns, table.columns)
        self.assertListEqual(expected.affected_columns, table.affected_columns)
        self.assertListEqual(expected.data, table.data)

    def test_keywords(self):

        exposure_keywords = {
            'layer_purpose': 'exposure',
            'layer_mode': 'classified',
            'layer_geometry': 'polygon',
            'exposure': 'land_cover',
            'field': 'FCODE',
        }

        hazard_keywords = {
            'layer_purpose': 'hazard',
            'layer_mode': 'continuous',
            'layer_geometry': 'raster',
            'hazard': 'tsunami',
            'hazard_category': 'single_event',
            'continuous_hazard_unit': 'metres'
        }

        impact_functions = ImpactFunctionManager().filter_by_keywords(
            hazard_keywords, exposure_keywords)
        message = 'There should be 1 impact function, but there are: %s' % \
                  len(impact_functions)
        self.assertEqual(1, len(impact_functions), message)
