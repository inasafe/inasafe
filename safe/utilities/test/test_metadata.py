# coding=utf-8
import unittest

from safe.definitionsv4.versions import inasafe_keyword_version
from safe.definitionsv4.fields import elderly_ratio_field, exposure_class_field
from safe.test.utilities import standard_data_path, clone_shp_layer
from safe.utilities.metadata import (
    write_iso19115_metadata,
    read_iso19115_metadata,
    metadata_migration
)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestMetadataUtilities(unittest.TestCase):
    """Test for Metadata Utilities module."""

    def test_write_iso19115_metadata(self):
        """Test for write_iso19115_metadata"""
        exposure_layer = clone_shp_layer(
            name='buildings',
            include_keywords=False,
            source_directory=standard_data_path('exposure'))
        keywords = {
            'date': '26-03-2015 14:03',
            'exposure': 'structure',
            'keyword_version': '3.2',
            'layer_geometry': 'polygon',
            'layer_mode': 'classified',
            'layer_purpose': 'exposure',
            'license': 'Open Data Commons Open Database License (ODbL)',
            'source': 'OpenStreetMap - www.openstreetmap.org',
            'structure_class_field': 'TYPE',
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
            'structure_class_field': 'TYPE',
            'title': 'Buildings'
        }
        metadata = write_iso19115_metadata(exposure_layer.source(), keywords)

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
            'keyword_version': '3.2',
            'layer_geometry': 'polygon',
            'layer_mode': 'classified',
            'layer_purpose': 'exposure',
            'license': 'Open Data Commons Open Database License (ODbL)',
            'source': 'OpenStreetMap - www.openstreetmap.org',
            'structure_class_field': 'TYPE',
            'title': 'Buildings'
        }
        layer = clone_shp_layer(
            name='buildings',
            include_keywords=False,
            source_directory=standard_data_path('exposure'))
        write_iso19115_metadata(layer.source(), keywords)

    def test_metadata_migration(self):
        """Test metadata_migration."""
        old_metadata = {
            'exposure': 'structure',
            'keyword_version': '3.5',
            'layer_geometry': 'polygon',
            'layer_mode': 'classified',
            'layer_purpose': 'exposure',
            'license': 'Open Data Commons Open Database License (ODbL)',
            'source': 'OpenStreetMap - www.openstreetmap.org',
            'structure_class_field': 'TYPE',
            'title': 'Buildings',
            'elderly ratio attribute': 'elderly'
        }
        expected_metadata_v4 = {
            'exposure': 'structure',
            'keyword_version': '4.0',
            'layer_geometry': 'polygon',
            'layer_mode': 'classified',
            'layer_purpose': 'exposure',
            'license': 'Open Data Commons Open Database License (ODbL)',
            'source': 'OpenStreetMap - www.openstreetmap.org',
            'title': 'Buildings',
            'inasafe_fields': {
                exposure_class_field['key']: 'TYPE',
                elderly_ratio_field['key']: 'elderly'
            }
        }
        new_metadata = metadata_migration(old_metadata, '3.5')
        self.assertDictEqual(old_metadata, new_metadata)

        new_metadata = metadata_migration(old_metadata, '4.0')
        self.assertDictEqual(expected_metadata_v4, new_metadata)


if __name__ == '__main__':
    unittest.main()
