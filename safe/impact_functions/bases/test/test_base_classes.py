# coding=utf-8
""""Test Base Classes Mixin."""

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/05/15'

import unittest
from safe.test.utilities import standard_data_path, get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.common.exceptions import NoAttributeInLayerError
from safe.impact_functions.bases.layer_types.classified_vector_exposure \
    import ClassifiedVectorExposureMixin
from safe.storage.core import read_layer
from safe.storage.safe_layer import SafeLayer


class TestBaseClassesMixin(unittest.TestCase):

    def test_vector_attribute_checker(self):
        """Test vector attribute checker."""
        building_path = standard_data_path('exposure', 'buildings.shp')

        exposure_layer = read_layer(building_path)

        classified_ve = ClassifiedVectorExposureMixin()
        classified_ve.exposure = SafeLayer(exposure_layer)

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
        # pylint: disable=broad-except
        except Exception as e:
            self.fail(e.message)
