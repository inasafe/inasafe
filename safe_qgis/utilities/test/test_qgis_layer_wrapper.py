"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Qgis layer wrapper Test Cases.**

Contact : kolesov.dm@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'kolesov.dm@gmail.com'
__date__ = '23/01/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import unittest

from qgis.core import QgsVectorLayer

from safe_qgis.safe_interface import UNITDATA
from safe_qgis.utilities.qgis_layer_wrapper import QgisWrapper
from safe_qgis.exceptions import KeywordNotFoundError


class QgisLayerWrapperTest(unittest.TestCase):
    """Test that context help works."""

    def setUp(self):
        data_path = os.path.join(
            UNITDATA,
            'impact',
            'aggregation_test_roads.shp')
        self.layer = QgsVectorLayer(
            data_path,
            'test vector',
            'ogr')
        self.wrapper = QgisWrapper(self.layer)

    def test_get_keywords(self):
        """Test get_keywords work
        """
        expected = {
            'map_title': 'Roads inundated',
            'target_field': 'flooded',
            'title': 'aggregation_test_roads'
        }
        keywords = self.wrapper.get_keywords()
        self.assertEquals(keywords, expected)

        expected = 'flooded'
        keyword = self.wrapper.get_keywords('target_field')
        self.assertEquals(keyword, expected)

        self.assertRaises(
            KeywordNotFoundError,
            self.wrapper.get_keywords,
            'ThisKeyDoesNotExist'
        )

    def test_get_name(self):
        """Test get_name work
        """
        name = self.wrapper.get_name()
        expected = 'aggregation_test_roads'
        self.assertEquals(name, expected)

        name = 'NewName'
        self.wrapper.set_name(name)
        self.assertEquals(self.wrapper.get_name(), name)

    def test_get_layer(self):
        """Test get_layer work
        """
        layer = self.wrapper.get_layer()
        self.assertEquals(self.layer, layer)

if __name__ == '__main__':
    suite = unittest.makeSuite(QgisLayerWrapperTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
