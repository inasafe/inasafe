# coding=utf-8

import unittest

from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.gisv4.vector.assign_inasafe_values import assign_inasafe_values
from safe.definitionsv4.fields import (
    hazard_value_field,
    hazard_class_field,
    exposure_type_field,
    exposure_class_field
)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestAssignHazardClass(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_assign_hazard_values(self):
        """Test we can assign hazard values."""

        hazard = load_test_vector_layer(
            'gisv4', 'hazard', 'unclassified_vector.geojson', clone=True)

        self.assertIn(
            hazard_value_field['key'], hazard.keywords['inasafe_fields'])

        layer = assign_inasafe_values(hazard)

        self.assertNotIn(
            hazard_value_field['key'], hazard.keywords['inasafe_fields'])
        self.assertIn(
            hazard_class_field['key'], hazard.keywords['inasafe_fields'])

        self.assertIn(
            hazard.keywords['inasafe_fields'][hazard_class_field['key']],
            [f.name() for f in layer.fields().toList()]
        )

    def test_assign_exposure_values(self):
        """Test we can assign exposure values."""

        exposure = load_test_vector_layer(
            'gisv4', 'exposure', 'roads.geojson', clone=True)

        self.assertIn(
            exposure_type_field['key'], exposure.keywords['inasafe_fields'])

        layer = assign_inasafe_values(exposure)

        self.assertNotIn(
            exposure_type_field['key'], exposure.keywords['inasafe_fields'])
        self.assertIn(
            exposure_class_field['key'], exposure.keywords['inasafe_fields'])

        self.assertIn(
            exposure.keywords['inasafe_fields'][exposure_class_field['key']],
            [f.name() for f in layer.fields().toList()]
        )
