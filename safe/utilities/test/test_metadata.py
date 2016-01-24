import unittest
import os

from safe.test.utilities import test_data_path, clone_shp_layer
from safe.utilities.metadata import (
    write_iso19115_metadata,
    read_iso19115_metadata
)
from safe.definitions import inasafe_keyword_version


class TestMetadataUtilities(unittest.TestCase):
    """Test for Metadata Utilities module."""

    def test_write_iso19115_metadata(self):
        """Test for write_iso19115_metadata"""
        exposure_layer = clone_shp_layer(
            name='buildings',
            include_keywords=False,
            source_directory=test_data_path('exposure'))
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
            source_directory=test_data_path('exposure'))
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
            source_directory=test_data_path('exposure'))
        write_iso19115_metadata(layer.source(), keywords)

    def test_impact_layer_metadata(self):
        """Test for impact layer metadata specific."""
        impact_layer = clone_shp_layer(
            name='impact_report_metadata',
            include_keywords=True,
            source_directory=test_data_path('impact'))

        metadata = read_iso19115_metadata(impact_layer.source())
        report_path = (
            os.path.splitext(impact_layer.source())[0] + '_impact_report.html')
        with open(report_path) as f:
                impact_report = f.read()
        self.assertEqual(metadata['impact_summary'], impact_report)

if __name__ == '__main__':
    unittest.main()
