# coding=utf-8

"""Test for uploading a layer to Geonode."""

__copyright__ = "Copyright 2018, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

import os
import unittest

from safe.definitions.constants import INASAFE_TEST
from safe.test.utilities import load_test_vector_layer, load_test_raster_layer
from safe.utilities.geonode.upload_layer_requests import upload, login_user
from safe.common.exceptions import GeoNodeLoginError, GeoNodeInstanceError

from safe.test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

LOGIN = 'test_geonode_user'
PASSWORD = 'test_geonode_password'
GEONODE_URL = 'http://138.201.158.66'

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
    def test_login(self):
        """Test login to geonode."""
        dummy_user = 'NotValidUser'
        dummy_password = 'NotValidPassword'
        not_geonode_instance = 'http://google.com'
        # Failed login (invalid geonode)
        self.assertRaises(
            GeoNodeInstanceError,
            login_user,
            not_geonode_instance,
            LOGIN,
            PASSWORD)
        # Failed login (wrong credential)
        self.assertRaises(
            GeoNodeLoginError,
            login_user,
            GEONODE_URL,
            dummy_user,
            dummy_password)

    @unittest.skipUnless(LOGIN, 'You need to fill LOGIN and PASSWORD above.')
    def test_upload_raster_layer(self):
        """Test upload raster layer."""
        # Connection
        session = login_user(GEONODE_URL, LOGIN, PASSWORD)

        # Upload a single raster layer
        result = upload(GEONODE_URL, session, self.raster.source())
        self.assertTrue(result['success'])

    @unittest.skipUnless(LOGIN, 'You need to fill LOGIN and PASSWORD above.')
    def test_upload_shapefile_layers(self):
        """Test upload shapefile layer."""
        # Connection
        session = login_user(GEONODE_URL, LOGIN, PASSWORD)

        # Upload a vector layer (with many files)
        result = upload(GEONODE_URL, session, self.vector.source())
        self.assertTrue(result['success'])
