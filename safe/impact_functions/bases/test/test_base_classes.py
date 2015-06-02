# coding=utf-8
import unittest

from safe.common.exceptions import NoAttributeInLayerError
from safe.impact_functions.bases.layer_types.classified_vector_exposure import \
    ClassifiedVectorExposureMixin
from safe.impact_functions.bases.layer_types.classified_vector_hazard import \
    ClassifiedVectorHazardMixin
from safe.impact_functions.bases.layer_types.continuous_vector_exposure import \
    ContinuousVectorExposureMixin
from safe.impact_functions.bases.layer_types.continuous_vector_hazard import \
    ContinuousVectorHazardMixin
from safe.storage.core import read_layer
from safe.test.utilities import test_data_path, get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/05/15'


class TestBaseClassesMixin(unittest.TestCase):

    def test_vector_attribute_checker(self):

        generic_polygon_path = test_data_path(
            'hazard', 'classified_generic_polygon.shp')
        building_path = test_data_path('exposure', 'buildings.shp')

        hazard_layer = read_layer(generic_polygon_path)
        exposure_layer = read_layer(building_path)

        classified_vh = ClassifiedVectorHazardMixin()
        classified_vh.set_up_hazard_layer(hazard_layer)

        continuous_vh = ContinuousVectorHazardMixin()
        continuous_vh.set_up_hazard_layer(hazard_layer)

        classified_ve = ClassifiedVectorExposureMixin()
        classified_ve.set_up_exposure_layer(exposure_layer)

        continuous_ve = ContinuousVectorExposureMixin()
        continuous_ve.set_up_exposure_layer(exposure_layer)

        with self.assertRaises(NoAttributeInLayerError):
            # test wrong attribute
            classified_vh.hazard_class_attribute = 'KRB'
        try:
            # test correct attribute
            classified_vh.hazard_class_attribute = 'h_zone'
        except Exception as e:
            self.fail(e.message)

        # we don't have continuous vector, so just use previous vector hazard

        with self.assertRaises(NoAttributeInLayerError):
            # test wrong attribute
            continuous_vh.hazard_value_attribute = 'KRB'
        try:
            # test correct attribute
            continuous_vh.hazard_value_attribute = 'h_zone'
        except Exception as e:
            self.fail(e.message)

        with self.assertRaises(NoAttributeInLayerError):
            # test wrong attribute
            classified_ve.exposure_class_attribute = 'TYP'
        try:
            # test correct attribute
            classified_ve.exposure_class_attribute = 'TYPE'
            expected_unique_values = 7
            actual_unique_values = len(classified_ve.exposure_unique_values)
            message = 'Expecting %d unique values. Got %d instead' % (
                expected_unique_values,
                len(classified_ve.exposure_unique_values))
            self.assertEqual(
                expected_unique_values,
                actual_unique_values,
                message)
        except Exception as e:
            self.fail(e.message)

        # we also don't have continuous vector exposure sample. Just use
        # previous vector exposure

        with self.assertRaises(NoAttributeInLayerError):
            # test wrong attribute
            continuous_ve.exposure_value_attribute = 'LEVEL'
        try:
            # test correct attribute
            continuous_ve.exposure_value_attribute = 'LEVELS'
            expected_max_value = 7
            expected_min_value = 1
            actual_max_value = continuous_ve.exposure_max_value
            actual_min_value = continuous_ve.exposure_min_value
            message = 'Expecting max %s value. Got %s instead' % (
                expected_max_value,
                actual_max_value)
            self.assertEqual(
                expected_max_value,
                actual_max_value,
                message)

            message = 'Expecting min %s value. Got %s instead' % (
                expected_min_value,
                actual_min_value)
            self.assertEqual(
                expected_min_value,
                actual_min_value,
                message)
        except Exception as e:
            self.fail(e.message)
