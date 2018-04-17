# coding=utf-8
"""Test class for group_select_parameter_widget."""

import unittest
from collections import OrderedDict

from safe.common.parameters.group_select_parameter import (
    GroupSelectParameter)
from safe.common.parameters.group_select_parameter_widget import (
    GroupSelectParameterWidget)

from safe.definitions.constants import (
    DO_NOT_REPORT,
    CUSTOM_VALUE,
    GLOBAL_DEFAULT,
    FIELDS,
    STATIC,
    SINGLE_DYNAMIC,
    MULTIPLE_DYNAMIC)

from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting='InaSAFETest')

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestGroupSelectParameterWidget(unittest.TestCase):

    """Test for GroupSelectParameterWidget."""

    def test_init(self):
        """Test init."""
        options = OrderedDict([
            (DO_NOT_REPORT,
             {
                 'label': 'Do not report',
                 'value': None,
                 'type': STATIC,
                 'constraint': {}
             }),
            (GLOBAL_DEFAULT,
             {
                 'label': 'Global default',
                 'value': 0.5,
                 'type': STATIC,
                 'constraint': {}
             }),
            (CUSTOM_VALUE,
             {
                 'label': 'Custom',
                 'value': 0.7,  # Taken from keywords / recent value
                 'type': SINGLE_DYNAMIC,
                 'constraint':
                     {
                         'min': 0,
                         'max': 1
                     }
             }),
            (FIELDS,
             {
                 'label': 'Ratio fields',
                 'value': ['field A', 'field B', 'field C'],
                 # Taken from keywords
                 'type': MULTIPLE_DYNAMIC,
                 'constraint': {}
             })
        ])

        parameter = GroupSelectParameter()
        parameter.options = options
        parameter.selected = FIELDS

        self.widget = GroupSelectParameterWidget(parameter)

        self.widget.select_radio_button(CUSTOM_VALUE)
        self.assertEqual(self.widget.get_parameter().value, 0.7)
        self.assertEqual(
            self.widget.get_parameter().selected_option_type(), SINGLE_DYNAMIC)

        self.widget.spin_boxes[CUSTOM_VALUE].setValue(0.6)
        self.assertEqual(self.widget.get_parameter().value, 0.6)
        self.assertEqual(
            self.widget.get_parameter().selected_option_type(), SINGLE_DYNAMIC)

        self.widget.select_radio_button(GLOBAL_DEFAULT)
        self.assertEqual(self.widget.get_parameter().value, 0.5)
        self.assertEqual(
            self.widget.get_parameter().selected_option_type(), STATIC)

        self.widget.select_radio_button(DO_NOT_REPORT)
        self.assertEqual(self.widget.get_parameter().value, None)
        self.assertEqual(
            self.widget.get_parameter().selected_option_type(), STATIC)

        self.widget.select_radio_button(FIELDS)
        self.assertListEqual(
            self.widget.get_parameter().value,
            ['field A', 'field B', 'field C'])
        self.assertEqual(
            self.widget.get_parameter().selected_option_type(),
            MULTIPLE_DYNAMIC)
