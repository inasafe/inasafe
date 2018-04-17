# coding=utf-8
"""Test Resource Parameter Widget."""

import unittest

from parameters.metadata import unit_feet_depth, unit_metres_depth
from parameters.unit import Unit

from safe.common.parameters.resource_parameter_widget import (
    ResourceParameterWidget)
from safe.common.parameters.resource_parameter import ResourceParameter
from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting='InaSAFETest')

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestResourceParameterWidget(unittest.TestCase):

    """Test Resource Parameter Widget."""

    def test_init(self):
        """Test init."""
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
        real_value = widget.label.text()
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
