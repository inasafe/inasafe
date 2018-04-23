# coding=utf-8
"""Test Metadata Utilities."""
import unittest
from datetime import datetime
# Do not remove this, needed for QUrl
from qgis.utils import iface  # pylint: disable=W0621
from qgis.PyQt.QtCore import QUrl


from safe.definitions.versions import inasafe_keyword_version
from safe.test.utilities import (
    standard_data_path, clone_shp_layer, get_qgis_app)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
from safe.utilities.metadata import (
    write_iso19115_metadata,
    read_iso19115_metadata,
    active_classification,
    active_thresholds_value_maps,
    copy_layer_keywords,
    convert_metadata,
)
from safe.common.exceptions import MetadataConversionError

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

        # Version 3.5
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
        metadata = write_iso19115_metadata(
            exposure_layer.source(), keywords, version_35=True)
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

        # Version 3.5
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
        metadata = write_iso19115_metadata(
            exposure_layer.source(), keywords, version_35=True)

        read_metadata = read_iso19115_metadata(
            exposure_layer.source(), version_35=True)

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

        # Version 3.5
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
        write_iso19115_metadata(layer.source(), keywords, version_35=True)
        read_metadata = read_iso19115_metadata(layer.source(), version_35=True)
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

        # We change only the copy.
        copy_keywords['url'] = 'my.website.org'
        self.assertEqual(copy_keywords['url'], 'my.website.org')
        self.assertEqual(keywords['url'].toString(), 'inasafe.org')

        # We make keywords using a variable as a key
        key = 'url'
        keywords = {
            key: QUrl('inasafe.org'),
            'date': datetime(1990, 7, 13)
        }
        copy_keywords = copy_layer_keywords(keywords)

        self.assertEqual(keywords[key].toString(), copy_keywords[key])
        self.assertEqual(
            keywords['date'].date().isoformat(), copy_keywords['date'])

        # Using the key, we change the value only in the copy
        copy_keywords[key] = 'my.website.org'

        self.assertEqual(copy_keywords[key], 'my.website.org')
        self.assertEqual(keywords[key].toString(), 'inasafe.org')

    def test_convert_metadata(self):
        """Test convert_metadata method."""
        # Not convertible hazard
        new_keywords = {
            'hazard': 'earthquake',
            'hazard_category': 'multiple_event',
            'inasafe_fields': {'hazard_value_field': 'h_zone'},
            'keyword_version': '4.0',
            'layer_geometry': 'polygon',
            'layer_mode': 'classified',
            'layer_purpose': 'hazard',
            'title': 'Earthquake Polygon',
            'value_maps': {
                'road': {
                    'earthquake_mmi_scale': {
                        'active': True,
                        'classes': {
                            'IX': ['Low Hazard Zone'],
                            'VIII': ['Medium Hazard Zone'],
                            'X': ['High Hazard Zone']
                        }
                    }
                },
                'structure': {
                    'earthquake_mmi_scale': {
                        'active': True,
                        'classes': {
                            'IX': ['Low Hazard Zone'],
                            'VIII': ['Medium Hazard Zone'],
                            'X': ['High Hazard Zone']
                        }
                    }
                }
            }
        }
        with self.assertRaises(MetadataConversionError):
            convert_metadata(new_keywords, exposure='structure')

        # Aggregation keyword with field mapping and default values
        new_keywords = {
            'inasafe_default_values': {
                'adult_ratio_field': 0.659,
                'elderly_ratio_field': 0.087,
                'youth_ratio_field': 0.254
            },
            'inasafe_fields': {'aggregation_name_field': 'KAB_NAME'},
            'keyword_version': '4.0',
            'layer_geometry': 'polygon',
            'layer_purpose': 'aggregation',
            'title': "D\xedstr\xedct's of Jakarta"
        }
        expected_keyword = {
            'adult ratio default': 0.659,
            'aggregation attribute': 'KAB_NAME',
            'elderly ratio default': 0.087,
            'keyword_version': '3.5',
            'layer_geometry': 'polygon',
            'layer_purpose': 'aggregation',
            'title': "D\xedstr\xedct's of Jakarta",
            'youth ratio default': 0.254}
        old_keyword = convert_metadata(new_keywords)
        self.assertDictEqual(old_keyword, expected_keyword)

        new_keywords = {
            'inasafe_default_values': {
                'lactating_ratio_field': 0.03,
                'pregnant_ratio_field': 0.02
            },
            'inasafe_fields': {
                'aggregation_id_field': 'area_id',
                'aggregation_name_field': 'area_name',
                'female_ratio_field': ['ratio_female']},
            'keyword_version': '4.1',
            'layer_geometry': 'polygon',
            'layer_purpose': 'aggregation',
            'source': 'InaSAFE v4 GeoJSON test layer',
            'title': 'small grid'
        }
        expected_keyword = {
            'aggregation attribute': 'area_name',
            'female ratio attribute': 'ratio_female',
            'keyword_version': '3.5',
            'layer_geometry': 'polygon',
            'layer_purpose': 'aggregation',
            'source': 'InaSAFE v4 GeoJSON test layer',
            'title': 'small grid'
        }

        old_keyword = convert_metadata(new_keywords)
        self.assertDictEqual(old_keyword, expected_keyword)

        # Convertible hazard
        new_keywords = {
            'hazard': 'volcano',
            'hazard_category': 'multiple_event',
            'inasafe_fields': {
                'hazard_name_field': 'volcano',
                'hazard_value_field': 'KRB'
            },
            'keyword_version': '4.0',
            'layer_geometry': 'polygon',
            'layer_mode': 'classified',
            'layer_purpose': 'hazard',
            'title': 'Volcano KRB',
            'value_maps': {
                'land_cover': {
                    'volcano_hazard_classes': {
                        'active': True,
                        'classes': {
                            'high': ['Kawasan Rawan Bencana III'],
                            'low': ['Kawasan Rawan Bencana I'],
                            'medium': ['Kawasan Rawan Bencana II']
                        }
                    }
                },
                'place': {
                    'volcano_hazard_classes': {
                        'active': True,
                        'classes': {
                            'high': ['Kawasan Rawan Bencana III'],
                            'low': ['Kawasan Rawan Bencana I'],
                            'medium': ['Kawasan Rawan Bencana II']
                        }
                    }
                },
                'population': {
                    'volcano_hazard_classes': {
                        'active': True,
                        'classes': {
                            'high': ['Kawasan Rawan Bencana III'],
                            'low': ['Kawasan Rawan Bencana I'],
                            'medium': ['Kawasan Rawan Bencana II']
                        }
                    }
                },
                'road': {
                    'volcano_hazard_classes': {
                        'active': True,
                        'classes': {
                            'high': ['Kawasan Rawan Bencana III'],
                            'low': ['Kawasan Rawan Bencana I'],
                            'medium': ['Kawasan Rawan Bencana II']
                        }
                    }
                },
                'structure': {
                    'volcano_hazard_classes': {
                        'active': True,
                        'classes': {
                            'high': ['Kawasan Rawan Bencana III'],
                            'low': ['Kawasan Rawan Bencana I'],
                            'medium': ['Kawasan Rawan Bencana II']
                        }
                    }
                }
            }
        }
        # Without exposure target, must raise exception
        with self.assertRaises(MetadataConversionError):
            convert_metadata(new_keywords)
        # With exposure target
        expected_keyword = {
            'field': 'KRB',
            'hazard': 'volcano',
            'hazard_category': 'multiple_event',
            'keyword_version': '3.5',
            'layer_geometry': 'polygon',
            'layer_mode': 'classified',
            'layer_purpose': 'hazard',
            'title': 'Volcano KRB',
            'value_map': {
                'high': ['Kawasan Rawan Bencana III'],
                'low': ['Kawasan Rawan Bencana I'],
                'medium': ['Kawasan Rawan Bencana II']},
            'vector_hazard_classification': 'volcano_vector_hazard_classes',
            'volcano_name_field': 'volcano'
        }
        old_keyword = convert_metadata(new_keywords, exposure='structure')
        self.assertDictEqual(old_keyword, expected_keyword)

        # Exposure structure
        new_keywords = {
            'classification': 'generic_structure_classes',
            'exposure': 'structure',
            'inasafe_fields': {'exposure_type_field': 'TYPE'},
            'keyword_version': '4.0',
            'layer_geometry': 'polygon',
            'layer_mode': 'classified',
            'layer_purpose': 'exposure',
            'license': 'Open Data Commons Open Database License (ODbL)',
            'source': 'OpenStreetMap - www.openstreetmap.org',
            'title': 'Buildings',
            'value_map': {
                'commercial': ['Commercial', 'Industrial'],
                'education': ['School'],
                'government': ['Government'],
                'health': ['Clinic/Doctor'],
                'place of worship': ['Place of Worship - Islam'],
                'residential': ['Residential']
            }
        }
        expected_keyword = {
            'exposure': 'structure',
            'keyword_version': '3.5',
            'layer_geometry': 'polygon',
            'layer_mode': 'classified',
            'layer_purpose': 'exposure',
            'license': 'Open Data Commons Open Database License (ODbL)',
            'source': 'OpenStreetMap - www.openstreetmap.org',
            'structure_class_field': 'TYPE',
            'title': 'Buildings',
            'value_mapping': {
                'commercial': ['Commercial', 'Industrial'],
                'education': ['School'],
                'government': ['Government'],
                'health': ['Clinic/Doctor'],
                'place of worship': ['Place of Worship - Islam'],
                'residential': ['Residential']
            }
        }
        old_keyword = convert_metadata(new_keywords)
        self.assertDictEqual(old_keyword, expected_keyword)

        # Exposure population polygon
        new_keywords = {'exposure': 'population',
         'exposure_unit': 'count',
         'inasafe_fields': {'population_count_field': 'population'},
         'keyword_version': '4.0',
         'layer_geometry': 'polygon',
         'layer_mode': 'continuous',
         'layer_purpose': 'exposure',
         'source': 'NBS',
         'title': 'Census',
         'url': 'http://nbs.go.tz'}
        expected_keyword = {
            'exposure': 'population',
            'exposure_unit': 'count',
            'keyword_version': '3.5',
            'layer_geometry': 'polygon',
            'layer_mode': 'continuous',
            'layer_purpose': 'exposure',
            'population_field': 'population',
            'source': 'NBS',
            'title': 'Census',
            'url': 'http://nbs.go.tz'
        }
        old_keyword = convert_metadata(new_keywords)
        self.assertDictEqual(old_keyword, expected_keyword)

        # Exposure population raster
        new_keywords = {
            'exposure': 'population',
            'exposure_unit': 'count',
            'inasafe_fields': {},
            'keyword_version': '4.2',
            'layer_geometry': 'raster',
            'layer_mode': 'continuous',
            'layer_purpose': 'exposure',
            'source': 'HKV',
            'title': 'People allow resampling'
        }
        expected_keyword = {
            'datatype': 'count',
            'exposure': 'population',
            'exposure_unit': 'count',
            'keyword_version': '3.5',
            'layer_geometry': 'raster',
            'layer_mode': 'continuous',
            'layer_purpose': 'exposure',
            'source': 'HKV',
            'title': 'People allow resampling'
        }
        old_keyword = convert_metadata(new_keywords)
        self.assertDictEqual(old_keyword, expected_keyword)

        # Exposure place
        new_keywords = {
            'classification': 'generic_place_classes',
            'exposure': 'place',
            'inasafe_fields': {
                'exposure_name_field': 'Name',
                'exposure_type_field': 'Type',
                'female_count_field': ['Female'],
                'male_count_field': ['Male'],
                'population_count_field': 'Population'
            },
            'keyword_version': '4.3',
            'layer_geometry': 'point',
            'layer_mode': 'classified',
            'layer_purpose': 'exposure',
            'license': 'Open Data Commons Open Database License (ODbL)',
            'source': 'Fictional Places',
            'title': 'Places',
            'value_map': {
                'Village': ['Village'],
                'city': ['Capital City', 'City'],
                'other': [
                    'Bus stop',
                    'Commercial',
                    'Public Area',
                    'Train Station']
            }
        }
        expected_keyword = {
            'exposure': 'place',
            'structure_class_field': 'Type',
            'keyword_version': '3.5',
            'layer_geometry': 'point',
            'layer_mode': 'classified',
            'layer_purpose': 'exposure',
            'license': 'Open Data Commons Open Database License (ODbL)',
            'name_field': 'Name',
            'population_field': 'Population',
            'source': 'Fictional Places',
            'title': 'Places',
            'value_mapping': {
                'Village': ['Village'],
                'city': ['Capital City', 'City'],
                'other': [
                    'Bus stop',
                    'Commercial',
                    'Public Area',
                    'Train Station']
            }
        }
        old_keyword = convert_metadata(new_keywords)
        self.assertDictEqual(old_keyword, expected_keyword)


if __name__ == '__main__':
    unittest.main()
