# coding=utf-8
"""InaSAFE Disaster risk assessment tool developed by AusAid -
  **Test class for resource_parameter.py.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""
__author__ = 'imajimatika@gmail.com'
__version__ = '3.0'
__revision__ = '$Format:%H$'
__date__ = '12/15/14'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import unittest

from safe.common.resource_parameter import ResourceParameter
from safe_extras.parameters.unit import Unit


class TestResourceParameter(unittest.TestCase):
    """Test for Resource Parameter."""
    def test_all(self):
        """Basic test of all properties."""
        unit = Unit()
        unit.name = 'meter'
        unit.plural = 'metres'
        unit.abbreviation = 'm'
        unit.description = (
            '<b>metres</b> are a metric unit of measure. There are 100 '
            'centimetres in 1 metre.'),
        unit.help_text = 'Help for meter unit'

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
