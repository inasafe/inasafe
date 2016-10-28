# coding=utf-8
"""**Tests for safe layer class**"""

__author__ = 'Ismail Sunni <ismail@kartoza.com>'
__revision__ = '$Format:%H$'
__date__ = '20/05/2016'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import unittest
from safe.test.utilities import get_qgis_app, standard_data_path

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsMapLayer

from safe.storage.safe_layer import SafeLayer
from safe.common.exceptions import InvalidLayerError, KeywordNotFoundError
from safe.test.utilities import clone_shp_layer


class SafeLayerTest(unittest.TestCase):
    def test_safe_layer_attributes(self):
        """Test creating safe layer."""
        self.maxDiff = None
        building_path = standard_data_path('exposure', 'buildings.shp')

        building_layer = clone_shp_layer(
            name='buildings',
            include_keywords=True,
            source_directory=standard_data_path('exposure'))

        # building_layer = read_layer(building_path)

        exposure = SafeLayer(building_layer)
        # Expect InvalidLayerError
        self.assertRaises(InvalidLayerError, SafeLayer, None)
        # Expect KeywordNotFoundError
        self.assertRaises(KeywordNotFoundError, exposure.keyword, 'dummy')

        self.assertEquals(exposure.name, 'Buildings')
        expected_keywords = {
            'license': u'Open Data Commons Open Database License (ODbL)',
            'keyword_version': u'3.5',
            'value_map': {
                u'residential': [u'Residential'],
                u'education': [u'School'],
                u'health': [u'Clinic/Doctor'],
                u'place of worship': [u'Place of Worship - Islam'],
                u'government': [u'Government'],
                u'commercial': [u'Commercial', u'Industrial'],
            },
            # 'structure_class_field': u'TYPE',
            'inasafe_fields': {u'exposure_type_field': u'TYPE'},
            'title': u'Buildings',
            'source': u'OpenStreetMap - www.openstreetmap.org',
            'layer_geometry': u'polygon',
            'layer_purpose': u'exposure',
            'layer_mode': u'classified',
            'exposure': u'structure',
            'classification': u'generic_structure_classes',
        }

        self.assertEquals(exposure.keywords, expected_keywords)
        self.assertTrue(exposure.is_qgsvectorlayer())
        self.assertTrue(isinstance(exposure.qgis_layer(), QgsMapLayer))
        self.assertTrue(isinstance(exposure.qgis_layer(), QgsVectorLayer))
        self.assertFalse(isinstance(exposure.qgis_layer(), QgsRasterLayer))
        self.assertEquals(exposure.crs().authid(), 'EPSG:4326')
        self.assertEquals(
            exposure.extent().asWktCoordinates(),
            u'106.80645110100005013 -6.18730753857923688, '
            u'106.82525023478235937 -6.17267712704860294')
        self.assertEquals(exposure.layer_type(), 0)
        self.assertEquals(exposure.geometry_type(), 2)


if __name__ == '__main__':
    unittest.main()
