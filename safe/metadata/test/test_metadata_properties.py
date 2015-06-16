# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Exception Classes.**

Custom exception classes for the IS application.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '12/10/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from unittest import TestCase

from PyQt4.QtCore import QDate, QUrl

from safe.common.exceptions import MetadataInvalidPathError
from safe.metadata.property.base_property import BaseProperty


class TestMetadataProperty(TestCase):

    def test_value_date(self):
        test_property = BaseProperty(
            'test name',
            QDate.currentDate(),
            '',
            'gco:Date'
        )

        test_property.value = QDate.fromString('2015-06-07')

        with self.assertRaises(TypeError):
            test_property.value = 20150607

    def test_value_str(self):
        test_property = BaseProperty(
            'test string',
            'random string',
            '',
            'gco:CharacterString'
        )

        with self.assertRaises(TypeError):
            test_property.value = 20150607

    def test_value_url(self):
        test_property = BaseProperty(
            'test url',
            QUrl('http://inasafe.org'),
            '',
            'gmd:URL'
        )

        with self.assertRaises(TypeError):
            test_property.value = 20150607

        with self.assertRaises(TypeError):
            test_property.value = 'http://inasafe.org'

    def test_xml_path(self):
        valid_path = ''
        invalid_path = 2345

        test_property = BaseProperty(
            'test url',
            QUrl('http://inasafe.org'),
            valid_path,
            'gmd:URL'
        )
        # xml_path should be read-only
        with self.assertRaises(AttributeError):
            test_property.xml_path = 'random string'

        with self.assertRaises(MetadataInvalidPathError):
            BaseProperty(
                'test url',
                QUrl('http://inasafe.org'),
                invalid_path,
                'gmd:URL'
            )

    def test_xml_type(self):
        test_property = BaseProperty(
            'test url',
            QUrl('http://inasafe.org'),
            '',
            'gmd:URL'
        )

        # type should be read-only
        with self.assertRaises(AttributeError):
            test_property.xml_type = 'random string'

        # type should be read-only
        with self.assertRaises(AttributeError):
            test_property.python_type = 'random string'
