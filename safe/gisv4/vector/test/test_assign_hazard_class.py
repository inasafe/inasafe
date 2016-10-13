# coding=utf-8

import unittest

from safe.test.utilities import (
    get_qgis_app,
    load_test_vector_layer)
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.gisv4.vector.assign_hazard_class import assign_hazard_class
from safe.definitionsv4.fields import hazard_value_field, hazard_class_field

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestAssignHazardClass(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_assign_hazard_class(self):
        """Test we can assign hazard class according to hazard value."""

        hazard = load_test_vector_layer(
            'gisv4', 'hazard', 'unclassified_vector.geojson', clone=True)

        self.assertIn(
            hazard_value_field['key'], hazard.keywords['inasafe_fields'])

        layer = assign_hazard_class(hazard)

        self.assertNotIn(
            hazard_value_field['key'], hazard.keywords['inasafe_fields'])
        self.assertIn(
            hazard_class_field['key'], hazard.keywords['inasafe_fields'])

        self.assertIn(
            hazard.keywords['inasafe_fields'][hazard_class_field['key']],
            [f.name() for f in layer.fields().toList()]
        )
