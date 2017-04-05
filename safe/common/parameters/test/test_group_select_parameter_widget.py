# coding=utf-8
"""Test class for group_select_parameter_widget."""


import unittest
from collections import OrderedDict

from safe.common.parameters.group_select_parameter import (
    GroupSelectParameter)
from safe.common.parameters.group_select_parameter_widget import (
    GroupSelectParameterWidget)

from safe.test.utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestGroupSelectParameterWidget(unittest.TestCase):

    """Test for GroupSelectParameterWidget."""

    def test_init(self):
        """Test init."""

        options = OrderedDict([
            ('do not use',
             {
                 'label': 'Do not use',
                 'value': None,
                 'type': 'static',
                 'constraint': {}
             }),
            ('global default',
             {
                 'label': 'Global default',
                 'value': 0.5,
                 'type': 'static',
                 'constraint': {}
             }),
            ('custom value',
             {
                 'label': 'Custom',
                 'value': 0.7,  # Taken from keywords / recent value
                 'type': 'single dynamic',
                 'constraint':
                     {
                         'min': 0,
                         'max': 1,
                         'step': 0.1
                     }
             }),
            ('ratio fields',
             {
                 'label': 'Ratio fields',
                 'value': ['field A', 'field B', 'field C'],
                 'type': 'multiple dynamic',
                 'constraint': {}
             })
        ])

        parameter = GroupSelectParameter()
        parameter.options = options
        parameter.selected = 'ratio fields'

        self.widget = GroupSelectParameterWidget(parameter)

        self.widget.select_radio_button('custom value')
        self.assertEqual(self.widget.get_parameter().value, 0.7)

        self.widget.spin_boxes['custom value'].setValue(0.6)
        self.assertEqual(self.widget.get_parameter().value, 0.6)

        self.widget.select_radio_button('global default')
        self.assertEqual(self.widget.get_parameter().value, 0.5)

        self.widget.select_radio_button('do not use')
        self.assertEqual(self.widget.get_parameter().value, None)

        self.widget.select_radio_button('ratio fields')
        self.assertListEqual(
            self.widget.get_parameter().value,
            ['field A', 'field B', 'field C'])
