# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**InaSAFE Field Definitions**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
from __future__ import print_function
import unittest
from collections import OrderedDict
from safe.definitions.fields import (
    exposure_fields,
    hazard_fields,
    aggregation_fields,
    impact_fields
)
from qgis.PyQt.QtCore import QVariant

qvariant_type = type(QVariant.Int)

all_fields = OrderedDict([
    ('Exposure Fields', exposure_fields),
    ('Hazard Fields', hazard_fields),
    ('Aggregation Fields', aggregation_fields),
    ('Impact Fields', impact_fields)
])


def generate_field_table():
    """Generating all field table in markdown."""
    for key, fields in list(all_fields.items()):
        # fix_print_with_import
        print('### %s' % key)
        # fix_print_with_import
        print('| Key | Name | Field Name |')
        # fix_print_with_import
        print('| --- | ---- | ---------- |')
        for i in fields:
            # fix_print_with_import
            print('| %s | %s | %s |' % (i['key'], i['name'], i['field_name']))


def check_format(field):
    """Check the format of field is valid.
    :param field: Field definitions.
    :type field: dict

    :returns: True if valid, else False.
    :rtype: bool, str
    """
    mandatory_format = {
        'key': str,
        'name': str,
        'field_name': str,
        'precision': int,
        'length': int,
        'type': qvariant_type,
        'description': str,
        'citations': list,
        'replace_null': bool
    }
    for key, value in list(mandatory_format.items()):
        if key in list(field.keys()):
            if isinstance(field[key], value):
                continue
            elif isinstance(field[key], list) and key == 'type':
                if not all([isinstance(i, qvariant_type) for i in field[key]]):
                    message = (
                        'List of should only contain of type only. We '
                        'found invalid for field %s' % field)
                    return False, message
            else:
                message = (
                    'Key "%s" in field %s does not have valid type. It should '
                    'be "%s" but got "%s"') % (
                    key, field, value, type(field['key']))
                return False, message
        else:
            message = 'Key "%s" not found in field %s' % (key, field)
            return False, message
    return True, 'Format is valid.'


class TestFieldDefinitions(unittest.TestCase):
    """Test for Field definitions."""
    def test_field_format(self):
        """Test to check all field is valid."""
        for layer, fields in list(all_fields.items()):
            for field in fields:
                check = check_format(field)
                self.assertTrue(check[0], check[1])


if __name__ == '__main__':
    unittest.main()
