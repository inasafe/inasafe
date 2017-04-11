# coding=utf-8
"""Test Metadata Utilities."""
import unittest
from datetime import datetime
# Do not remove this, needed for QUrl
from qgis.utils import iface  # pylint: disable=W0621
from PyQt4.QtCore import QUrl

from safe.definitions.versions import inasafe_keyword_version
from safe.test.utilities import standard_data_path, clone_shp_layer
from safe.utilities.metadata import (
    write_iso19115_metadata,
    read_iso19115_metadata,
    active_classification,
    active_thresholds_value_maps,
    copy_layer_keywords
)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestMetadataUtilities(unittest.TestCase):

    """Test for Metadata Utilities module."""

    maxDiff = None

    def test_write_iso19115_metadata(self):
        """Test for write_iso19115_metadata."""
        exposure_layer = clone_shp_layer(
            name='buildings',
            include_keywords=False,
            source_directory=standard_data_path('exposure'))
        keywords = {
            'date': '26-03-2015 14:03',
            'exposure': 'structure',
            'keyword_version': inasafe_keyword_version,
            'layer_geometry': 'polygon',
            'layer_mode': 'classified',
            'layer_purpose': 'exposure',
            'license': 'Open Data Commons Open Database License (ODbL)',
            'source': 'OpenStreetMap - www.openstreetmap.org',
            'title': 'Buildings'
        }
        metadata = write_iso19115_metadata(exposure_layer.source(), keywords)
        self.assertEqual(metadata.exposure, 'structure')

    def test_read_iso19115_metadata(self):
        """Test for read_iso19115_metadata method."""
        exposure_layer = clone_shp_layer(
            name='buildings',
            include_keywords=False,
            source_directory=standard_data_path('exposure'))
        keywords = {
            # 'date': '26-03-2015 14:03',
            'exposure': 'structure',
            'keyword_version': inasafe_keyword_version,
            'layer_geometry': 'polygon',
            'layer_mode': 'classified',
            'layer_purpose': 'exposure',
            'license': 'Open Data Commons Open Database License (ODbL)',
            'source': 'OpenStreetMap - www.openstreetmap.org',
            'title': 'Buildings'
        }
        write_iso19115_metadata(exposure_layer.source(), keywords)

        read_metadata = read_iso19115_metadata(exposure_layer.source())

        for key in set(keywords.keys()) & set(read_metadata.keys()):
            self.assertEqual(read_metadata[key], keywords[key])
        for key in set(keywords.keys()) - set(read_metadata.keys()):
            message = 'key %s is not found in ISO metadata' % key
            self.assertEqual(read_metadata[key], keywords[key], message)
        for key in set(read_metadata.keys()) - set(keywords.keys()):
            message = 'key %s is not found in old keywords' % key
            self.assertEqual(read_metadata[key], keywords[key], message)

    def test_write_read_iso_19115_metadata(self):
        """Test for write_read_iso_19115_metadata."""
        keywords = {
            # 'date': '26-03-2015 14:03',
            'exposure': 'structure',
            'keyword_version': inasafe_keyword_version,
            'layer_geometry': 'polygon',
            'layer_mode': 'classified',
            'layer_purpose': 'exposure',
            'license': 'Open Data Commons Open Database License (ODbL)',
            'source': 'OpenStreetMap - www.openstreetmap.org',
            'title': 'Buildings',
            'inasafe_fields': {
                'youth_count_field': [
                    'POP_F_0-4', 'POP_F_5-6', 'POP_F_7-12',
                ]
            }
        }
        layer = clone_shp_layer(
            name='buildings',
            include_keywords=False,
            source_directory=standard_data_path('exposure'))
        write_iso19115_metadata(layer.source(), keywords)

        read_metadata = read_iso19115_metadata(layer.source())
        self.assertDictEqual(keywords, read_metadata)

    def test_active_classification_thresholds_value_maps(self):
        """Test for active_classification and thresholds value maps method."""
        keywords = {
            'layer_mode': 'continuous',
            'thresholds': {
                'structure': {
                    'ina_structure_flood_hazard_classification': {
                        'classes': {
                            'low': [1, 2],
                            'medium': [3, 4],
                            'high': [5, 6]
                        },
                        'active': False
                    },
                    'ina_structure_flood_hazard_4_class_classification': {
                        'classes': {
                            'low': [1, 2],
                            'medium': [3, 4],
                            'high': [5, 6],
                            'very_high': [7, 8]
                        },
                        'active': False

                    }
                },
                'population': {
                    'ina_population_flood_hazard_classification': {
                        'classes': {
                            'low': [1, 2.5],
                            'medium': [2.5, 4.5],
                            'high': [4.5, 6]
                        },
                        'active': False
                    },
                    'ina_population_flood_hazard_4_class_classification': {
                        'classes': {
                            'low': [1, 2.5],
                            'medium': [2.5, 4],
                            'high': [4, 6],
                            'very_high': [6, 8]
                        },
                        'active': True
                    }
                }
            }
        }
        classification = active_classification(keywords, 'population')
        self.assertEqual(
            classification,
            'ina_population_flood_hazard_4_class_classification')

        classification = active_classification(keywords, 'road')
        self.assertIsNone(classification)

        classification = active_classification(keywords, 'structure')
        self.assertIsNone(classification)

        thresholds = active_thresholds_value_maps(keywords, 'population')
        expected_thresholds = {
            'low': [1, 2.5],
            'medium': [2.5, 4],
            'high': [4, 6],
            'very_high': [6, 8]}
        self.assertDictEqual(thresholds, expected_thresholds)

        classification = active_thresholds_value_maps(keywords, 'road')
        self.assertIsNone(classification)

        classification = active_thresholds_value_maps(keywords, 'structure')
        self.assertIsNone(classification)

    def test_copy_layer_keywords(self):
        """Test for copy_layer_keywords."""
        keywords = {
            'url': QUrl('inasafe.org'),
            'date': datetime(1990, 7, 13)
        }
        copy_keywords = copy_layer_keywords(keywords)

        self.assertEqual(keywords['url'].toString(), copy_keywords['url'])
        self.assertEqual(
            keywords['date'].date().isoformat(), copy_keywords['date'])

if __name__ == '__main__':
    unittest.main()
