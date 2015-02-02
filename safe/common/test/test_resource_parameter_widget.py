# coding=utf-8
"""InaSAFE Disaster risk assessment tool developed by AusAid -
  **Test class for resource_parameter_widget.py.**

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
from safe_extras.parameters.unit import Unit
from safe_extras.parameters.metadata import unit_feet_depth, unit_metres_depth
from safe.common.resource_parameter import ResourceParameter
from safe.common.resource_parameter_widget import ResourceParameterWidget

# noinspection PyPackageRequirements
from PyQt4.QtGui import QApplication

application = QApplication([])


class TestResourceParameterWidget(unittest.TestCase):
    def test_init(self):
        unit_feet = Unit('130790')
        unit_feet.load_dictionary(unit_feet_depth)

        unit_metres = Unit('900713')
        unit_metres.load_dictionary(unit_metres_depth)

        resource_parameter = ResourceParameter()
        resource_parameter.name = 'Flood Depth'
        resource_parameter.is_required = True
        resource_parameter.precision = 3
        resource_parameter.minimum_allowed_value = 1.0
        resource_parameter.maximum_allowed_value = 2.0
        resource_parameter.help_text = 'The depth of flood.'
        resource_parameter.description = (
            'A <b>test _description</b> that is very long so that you need '
            'to read it for one minute and you will be tired after read this '
            'description. You are the best user so far. Even better if you '
            'read this description loudly so that all of your friends will be '
            'able to hear you')
        resource_parameter.unit = unit_feet
        resource_parameter.allowed_units = [unit_metres, unit_feet]
        resource_parameter.value = 1.12

        widget = ResourceParameterWidget(resource_parameter)

        expected_value = resource_parameter.name
        real_value = widget._label.text()
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        expected_value = resource_parameter.value
        real_value = widget.get_parameter().value
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        widget.set_value(1.5)

        expected_value = 1.5
        real_value = widget.get_parameter().value
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        widget.set_value(1.55555)

        expected_value = 1.556
        real_value = widget.get_parameter().value
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)

        widget.set_value(7)

        expected_value = 2
        real_value = widget.get_parameter().value
        message = 'Expected %s get %s' % (expected_value, real_value)
        self.assertEqual(expected_value, real_value, message)


if __name__ == '__main__':
    unittest.main()
