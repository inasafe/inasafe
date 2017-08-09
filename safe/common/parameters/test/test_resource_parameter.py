# coding=utf-8
"""Test Resource Parameter."""

import unittest

from parameters.unit import Unit

from safe.common.parameters.resource_parameter import ResourceParameter


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestResourceParameter(unittest.TestCase):

    """Test for Resource Parameter."""

    def test_all(self):
        """Basic test of all properties."""
        unit = Unit()
        unit.name = 'metre'
        unit.plural = 'metres'
        unit.abbreviation = 'm'
        unit.description = (
            '<b>metres</b> are a metric unit of measure. There are 100 '
            'centimetres in 1 metre.'),
        unit.help_text = 'Help for metre unit'

        parameter = ResourceParameter()
        parameter.is_required = True
        parameter.minimum_allowed_value = 1.0
        parameter.maximum_allowed_value = 2.0
        parameter.value = 1.123
        parameter.frequency = 'weekly'
        parameter.unit = unit

        self.assertEqual(1.123, parameter.value)
        self.assertDictEqual(unit.serialize(), parameter.unit.serialize())
        self.assertEqual('weekly', parameter.frequency)


if __name__ == '__main__':
    unittest.main()
