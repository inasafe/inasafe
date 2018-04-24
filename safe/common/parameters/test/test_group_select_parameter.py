# coding=utf-8
"""Tests for group select parameter."""

import unittest
from collections import OrderedDict

from safe.common.parameters.group_select_parameter import (
    GroupSelectParameter)
from safe.definitions.constants import (
    DO_NOT_REPORT,
    CUSTOM_VALUE,
    GLOBAL_DEFAULT,
    FIELDS,
    STATIC,
    SINGLE_DYNAMIC,
    MULTIPLE_DYNAMIC)

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestGroupSelectParameter(unittest.TestCase):

    """Test For Group Select Parameter."""

    def test_setup(self):
        """Test setup for group select parameter."""
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

        self.assertEqual(parameter.value, None)
        parameter.selected = FIELDS
        self.assertEqual(parameter.value, options[FIELDS]['value'])


if __name__ == '__main__':
    unittest.main()
