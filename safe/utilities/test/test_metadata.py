# coding=utf-8
"""Test Metadata Utilities."""
import unittest
from datetime import datetime
# Do not remove this, needed for QUrl
from qgis.utils import iface  # pylint: disable=W0621
from qgis.PyQt.QtCore import QUrl

from safe.definitions.constants import INASAFE_TEST
from safe.definitions.versions import inasafe_keyword_version
from safe.test.utilities import (
    standard_data_path, clone_shp_layer, get_qgis_app)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)
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
            'hazard': u'earthquake',
            'hazard_category': u'multiple_event',
            'inasafe_fields': {u'hazard_value_field': u'h_zone'},
            'keyword_version': u'4.0',
            'layer_geometry': u'polygon',
            'layer_mode': u'classified',
            'layer_purpose': u'hazard',
            'title': u'Earthquake Polygon',
            'value_maps': {
                u'road': {
                    u'earthquake_mmi_scale': {
                        u'active': True,
                        u'classes': {
                            u'IX': [u'Low Hazard Zone'],
                            u'VIII': [u'Medium Hazard Zone'],
                            u'X': [u'High Hazard Zone']
                        }
                    }
                },
                u'structure': {
                    u'earthquake_mmi_scale': {
                        u'active': True,
                        u'classes': {
                            u'IX': [u'Low Hazard Zone'],
                            u'VIII': [u'Medium Hazard Zone'],
                            u'X': [u'High Hazard Zone']
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
                u'adult_ratio_field': 0.659,
                u'elderly_ratio_field': 0.087,
                u'youth_ratio_field': 0.254
            },
            'inasafe_fields': {u'aggregation_name_field': u'KAB_NAME'},
            'keyword_version': u'4.0',
            'layer_geometry': u'polygon',
            'layer_purpose': u'aggregation',
            'title': u"D\xedstr\xedct's of Jakarta"
        }
        expected_keyword = {
            'adult ratio default': 0.659,
            'aggregation attribute': u'KAB_NAME',
            'elderly ratio default': 0.087,
            'keyword_version': '3.5',
            'layer_geometry': u'polygon',
            'layer_purpose': u'aggregation',
            'title': u"D\xedstr\xedct's of Jakarta",
            'youth ratio default': 0.254}
        old_keyword = convert_metadata(new_keywords)
        self.assertDictEqual(old_keyword, expected_keyword)

        new_keywords = {
            'inasafe_default_values': {
                u'lactating_ratio_field': 0.03,
                u'pregnant_ratio_field': 0.02
            },
            'inasafe_fields': {
                u'aggregation_id_field': u'area_id',
                u'aggregation_name_field': u'area_name',
                u'female_ratio_field': [u'ratio_female']},
            'keyword_version': u'4.1',
            'layer_geometry': u'polygon',
            'layer_purpose': u'aggregation',
            'source': u'InaSAFE v4 GeoJSON test layer',
            'title': u'small grid'
        }
        expected_keyword = {
            'aggregation attribute': u'area_name',
            'female ratio attribute': u'ratio_female',
            'keyword_version': '3.5',
            'layer_geometry': u'polygon',
            'layer_purpose': u'aggregation',
            'source': u'InaSAFE v4 GeoJSON test layer',
            'title': u'small grid'
        }

        old_keyword = convert_metadata(new_keywords)
        self.assertDictEqual(old_keyword, expected_keyword)

        # Convertible hazard
        new_keywords = {
            'hazard': u'volcano',
            'hazard_category': u'multiple_event',
            'inasafe_fields': {
                u'hazard_name_field': u'volcano',
                u'hazard_value_field': u'KRB'
            },
            'keyword_version': u'4.0',
            'layer_geometry': u'polygon',
            'layer_mode': u'classified',
            'layer_purpose': u'hazard',
            'title': u'Volcano KRB',
            'value_maps': {
                u'land_cover': {
                    u'volcano_hazard_classes': {
                        u'active': True,
                        u'classes': {
                            u'high': [u'Kawasan Rawan Bencana III'],
                            u'low': [u'Kawasan Rawan Bencana I'],
                            u'medium': [u'Kawasan Rawan Bencana II']
                        }
                    }
                },
                u'place': {
                    u'volcano_hazard_classes': {
                        u'active': True,
                        u'classes': {
                            u'high': [u'Kawasan Rawan Bencana III'],
                            u'low': [u'Kawasan Rawan Bencana I'],
                            u'medium': [u'Kawasan Rawan Bencana II']
                        }
                    }
                },
                u'population': {
                    u'volcano_hazard_classes': {
                        u'active': True,
                        u'classes': {
                            u'high': [u'Kawasan Rawan Bencana III'],
                            u'low': [u'Kawasan Rawan Bencana I'],
                            u'medium': [u'Kawasan Rawan Bencana II']
                        }
                    }
                },
                u'road': {
                    u'volcano_hazard_classes': {
                        u'active': True,
                        u'classes': {
                            u'high': [u'Kawasan Rawan Bencana III'],
                            u'low': [u'Kawasan Rawan Bencana I'],
                            u'medium': [u'Kawasan Rawan Bencana II']
                        }
                    }
                },
                u'structure': {
                    u'volcano_hazard_classes': {
                        u'active': True,
                        u'classes': {
                            u'high': [u'Kawasan Rawan Bencana III'],
                            u'low': [u'Kawasan Rawan Bencana I'],
                            u'medium': [u'Kawasan Rawan Bencana II']
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
            'field': u'KRB',
            'hazard': u'volcano',
            'hazard_category': u'multiple_event',
            'keyword_version': '3.5',
            'layer_geometry': u'polygon',
            'layer_mode': u'classified',
            'layer_purpose': u'hazard',
            'title': u'Volcano KRB',
            'value_map': {
                u'high': [u'Kawasan Rawan Bencana III'],
                u'low': [u'Kawasan Rawan Bencana I'],
                u'medium': [u'Kawasan Rawan Bencana II']},
            'vector_hazard_classification': 'volcano_vector_hazard_classes',
            'volcano_name_field': u'volcano'
        }
        old_keyword = convert_metadata(new_keywords, exposure='structure')
        self.assertDictEqual(old_keyword, expected_keyword)

        # Exposure structure
        new_keywords = {
            'classification': u'generic_structure_classes',
            'exposure': u'structure',
            'inasafe_fields': {u'exposure_type_field': u'TYPE'},
            'keyword_version': u'4.0',
            'layer_geometry': u'polygon',
            'layer_mode': u'classified',
            'layer_purpose': u'exposure',
            'license': u'Open Data Commons Open Database License (ODbL)',
            'source': u'OpenStreetMap - www.openstreetmap.org',
            'title': u'Buildings',
            'value_map': {
                u'commercial': [u'Commercial', u'Industrial'],
                u'education': [u'School'],
                u'government': [u'Government'],
                u'health': [u'Clinic/Doctor'],
                u'place of worship': [u'Place of Worship - Islam'],
                u'residential': [u'Residential']
            }
        }
        expected_keyword = {
            'exposure': u'structure',
            'keyword_version': '3.5',
            'layer_geometry': u'polygon',
            'layer_mode': u'classified',
            'layer_purpose': u'exposure',
            'license': u'Open Data Commons Open Database License (ODbL)',
            'source': u'OpenStreetMap - www.openstreetmap.org',
            'structure_class_field': u'TYPE',
            'title': u'Buildings',
            'value_mapping': {
                u'commercial': [u'Commercial', u'Industrial'],
                u'education': [u'School'],
                u'government': [u'Government'],
                u'health': [u'Clinic/Doctor'],
                u'place of worship': [u'Place of Worship - Islam'],
                u'residential': [u'Residential']
            }
        }
        old_keyword = convert_metadata(new_keywords)
        self.assertDictEqual(old_keyword, expected_keyword)

        # Exposure population polygon
        new_keywords = {'exposure': u'population',
         'exposure_unit': u'count',
         'inasafe_fields': {u'population_count_field': u'population'},
         'keyword_version': u'4.0',
         'layer_geometry': u'polygon',
         'layer_mode': u'continuous',
         'layer_purpose': u'exposure',
         'source': u'NBS',
         'title': u'Census',
         'url': u'http://nbs.go.tz'}
        expected_keyword = {
            'exposure': u'population',
            'exposure_unit': u'count',
            'keyword_version': '3.5',
            'layer_geometry': u'polygon',
            'layer_mode': u'continuous',
            'layer_purpose': u'exposure',
            'population_field': u'population',
            'source': u'NBS',
            'title': u'Census',
            'url': u'http://nbs.go.tz'
        }
        old_keyword = convert_metadata(new_keywords)
        self.assertDictEqual(old_keyword, expected_keyword)

        # Exposure population raster
        new_keywords = {
            'exposure': u'population',
            'exposure_unit': u'count',
            'inasafe_fields': {},
            'keyword_version': u'4.2',
            'layer_geometry': u'raster',
            'layer_mode': u'continuous',
            'layer_purpose': u'exposure',
            'source': u'HKV',
            'title': u'People allow resampling'
        }
        expected_keyword = {
            'datatype': 'count',
            'exposure': u'population',
            'exposure_unit': u'count',
            'keyword_version': '3.5',
            'layer_geometry': u'raster',
            'layer_mode': u'continuous',
            'layer_purpose': u'exposure',
            'source': u'HKV',
            'title': u'People allow resampling'
        }
        old_keyword = convert_metadata(new_keywords)
        self.assertDictEqual(old_keyword, expected_keyword)

        # Exposure place
        new_keywords = {
            'classification': u'generic_place_classes',
            'exposure': u'place',
            'inasafe_fields': {
                u'exposure_name_field': u'Name',
                u'exposure_type_field': u'Type',
                u'female_count_field': [u'Female'],
                u'male_count_field': [u'Male'],
                u'population_count_field': u'Population'
            },
            'keyword_version': u'4.3',
            'layer_geometry': u'point',
            'layer_mode': u'classified',
            'layer_purpose': u'exposure',
            'license': u'Open Data Commons Open Database License (ODbL)',
            'source': u'Fictional Places',
            'title': u'Places',
            'value_map': {
                u'Village': [u'Village'],
                u'city': [u'Capital City', u'City'],
                u'other': [
                    u'Bus stop',
                    u'Commercial',
                    u'Public Area',
                    u'Train Station']
            }
        }
        expected_keyword = {
            'exposure': u'place',
            'structure_class_field': u'Type',
            'keyword_version': '3.5',
            'layer_geometry': u'point',
            'layer_mode': u'classified',
            'layer_purpose': u'exposure',
            'license': u'Open Data Commons Open Database License (ODbL)',
            'name_field': u'Name',
            'population_field': u'Population',
            'source': u'Fictional Places',
            'title': u'Places',
            'value_mapping': {
                u'Village': [u'Village'],
                u'city': [u'Capital City', u'City'],
                u'other': [
                    u'Bus stop',
                    u'Commercial',
                    u'Public Area',
                    u'Train Station']
            }
        }
        old_keyword = convert_metadata(new_keywords)
        self.assertDictEqual(old_keyword, expected_keyword)


if __name__ == '__main__':
    unittest.main()
