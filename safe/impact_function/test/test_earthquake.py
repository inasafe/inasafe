# coding=utf-8

"""Test for Impact Function."""

import unittest

from safe.definitions.hazard_classifications import (
    earthquake_mmi_hazard_classes)
from safe.impact_function.earthquake import from_mmi_to_hazard_class

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H'


class TestEarthquake(unittest.TestCase):

    """Earthquake function tests."""

    def test_from_mmi_hazard_class_key(self):
        """Test we can get the hazard class key given a MMI level."""
        self.assertEqual(
            'medium',
            from_mmi_to_hazard_class(8, earthquake_mmi_hazard_classes['key']))
        self.assertIsNone(
            from_mmi_to_hazard_class(2, earthquake_mmi_hazard_classes['key']))
