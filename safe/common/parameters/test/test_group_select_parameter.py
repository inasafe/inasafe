# coding=utf-8
"""Tests for group select parameter."""

import unittest
from collections import OrderedDict

from safe.common.parameters.group_select_parameter import (
    GroupSelectParameter)

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestGroupSelectParameter(unittest.TestCase):

    """Test For Group Select Parameter."""

    def test_setup(self):
        """Test setup for group select parameter."""
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
                         'max': 1
                     }
             }),
            ('ratio fields',
             {
                 'label': 'Ratio fields',
                 'value': [],  # Taken from keywords
                 'type': 'multiple dynamic',
                 'constraint': {}
             })
        ])

        parameter = GroupSelectParameter()
        parameter.options = options

        self.assertEqual(parameter.value, None)
        parameter.selected = 'ratio fields'
        self.assertEqual(parameter.value, options['ratio fields']['value'])


if __name__ == '__main__':
    unittest.main()
