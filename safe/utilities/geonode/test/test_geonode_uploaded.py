# coding=utf-8

"""Test for uploading a layer to Geonode."""

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

import os
import unittest

from safe.test.utilities import load_test_vector_layer, load_test_raster_layer
from safe.utilities.geonode.upload_layer_requests import upload, login_user

from safe.test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting='InaSAFETest')

LOGIN = ''
PASSWORD = ''
GEONODE_URL = ''


class GeonodeUploadTest(unittest.TestCase):

    """Test Geonode upload.

    WARNINGS:

    Most of tests here are fragile as they rely on an external website.
    Their HTML might change and break the test. These tests are disabled
    because we use our own credentials.
    """

    def setUp(self):
        self.vector = load_test_vector_layer('exposure', 'airports.shp')
        self.raster = load_test_raster_layer(
            'gisv4', 'hazard', 'earthquake.asc')

    def test_credentials_are_not_public(self):
        """Test if we did not publish credentials on github/travis."""
        if os.environ.get('ON_TRAVIS', False):
            self.assertEqual(LOGIN, '', 'Login must be empty.')
            self.assertEqual(PASSWORD, '', 'Password must be empty.')
            self.assertEqual(GEONODE_URL, '', 'URL must be empty.')

    @unittest.skipUnless(LOGIN, 'You need to fill LOGIN and PASSWORD above.')
    def test_login_and_upload_layers(self):
        """Test login page."""
        # Connection
        session = login_user(GEONODE_URL, LOGIN, PASSWORD)

        # Upload a single raster layer
        result = upload(GEONODE_URL, session, self.raster.source())
        self.assertTrue(result['success'])

        # Upload a vector layer (with many files)
        result = upload(GEONODE_URL, session, self.vector.source())
        self.assertTrue(result['success'])
