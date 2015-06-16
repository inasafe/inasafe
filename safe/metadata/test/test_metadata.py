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

from datetime import datetime, date
from unittest import TestCase
from PyQt4.QtCore import QDate, QUrl
from safe.metadata.metadata import Metadata


class TestMetadata(TestCase):
    
    def test_metadata(self):
        metadata = Metadata('random_layer_id')
        path = 'gmd:MD_Metadata/gmd:dateStamp/'

        # using unsupported xml types
        test_value = 'Random string'
        with self.assertRaises(KeyError):
            metadata.set('ISO19115_TEST', test_value, path, 'gco:RandomString')

    def test_metadata_provenance(self):
        metadata = Metadata('random_layer_id')
        metadata.append_provenance_step('Title 1', 'Description of step 1')
        metadata.append_provenance_step('Title 2', 'Description of step 2')
        metadata.append_provenance_step('Title 3', 'Description of step 3')
        self.assertEqual(metadata.provenance.count, 3)
        self.assertEqual(metadata.provenance.last.title, 'Title 3')

    def test_metadata_date(self):
        metadata = Metadata('random_layer_id')
        path = 'gmd:MD_Metadata/gmd:dateStamp/'

        # using QDate
        test_value = QDate(2015, 6, 7)
        metadata.set('ISO19115_TEST', test_value, path, 'gco:Date')
        self.assertEqual(metadata.get('ISO19115_TEST'), '2015-06-07')

        # using datetime
        test_value = datetime(2015, 6, 7)
        metadata.update('ISO19115_TEST', test_value)
        self.assertEqual(metadata.get('ISO19115_TEST'), '2015-06-07')

        # using date
        test_value = date(2015, 6, 7)
        metadata.set('ISO19115_TEST', test_value, path, 'gco:Date')
        self.assertEqual(metadata.get('ISO19115_TEST'), '2015-06-07')

        # using str should fail
        test_value = '2015-06-07'
        with self.assertRaises(TypeError):
            metadata.update('ISO19115_TEST', test_value)

    def test_metadata_url(self):
        metadata = Metadata('random_layer_id')
        path = 'gmd:MD_Metadata/gmd:dateStamp/'

        # using QUrl
        test_value = QUrl('http://inasafe.org')
        metadata.set('ISO19115_TEST', test_value, path, 'gmd:URL')
        self.assertEqual(
            metadata.get('ISO19115_TEST'), 'http://inasafe.org')

        # using str should fail
        test_value = 'http://inasafe.org'
        with self.assertRaises(TypeError):
            metadata.update('ISO19115_TEST', test_value)

        # using invalid QUrl (has a space)
        test_value = QUrl('http://inasafe.org ')
        with self.assertRaises(ValueError):
            metadata.set('ISO19115_TEST', test_value, path, 'gmd:URL')

    def test_metadata_str(self):
        metadata = Metadata('random_layer_id')
        path = 'gmd:MD_Metadata/gmd:dateStamp/'

        # using str
        test_value = 'Random string'
        metadata.set(
            'ISO19115_TEST', test_value, path, 'gco:CharacterString')
        self.assertEqual(
            metadata.get('ISO19115_TEST'), 'Random string')

        # using int
        test_value = 1234
        metadata.update('ISO19115_TEST', test_value)
        self.assertEqual(metadata.get('ISO19115_TEST'), '1234')

        # using float
        test_value = 1234.5678
        metadata.update('ISO19115_TEST', test_value)
        self.assertEqual(metadata.get('ISO19115_TEST'), '1234.5678')

        # using invalid QUrl
        test_value = QUrl()
        with self.assertRaises(ValueError):
            metadata.update('ISO19115_TEST', test_value)
