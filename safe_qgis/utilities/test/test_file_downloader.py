# coding=utf-8
"""
Test for Save Scenario Dialog.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'akbargumbira@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '16/03/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import tempfile

#noinspection PyPackageRequirements
from PyQt4.QtNetwork import QNetworkAccessManager

from safe.common.testing import get_qgis_app
# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe_qgis.utilities.file_downloader import FileDownloader
from safe_qgis.utilities.utilities_for_testing import assert_hash_for_file
from safe_qgis.exceptions import DownloadError


class FileDownloaderTest(unittest.TestCase):
    """Test FileDownloader class."""
    #noinspection PyMethodMayBeStatic
    def test_download(self):
        """Test download."""
        manager = QNetworkAccessManager(PARENT)

        # NOTE(gigih):
        # this is the hash of google front page.
        # I think we can safely assume that the content
        # of google.com never changes (probably).
        # ...or not...changed on 5 Dec 2013 ...
        # ...and changed on 28 Apr 2014 by Tim to hash and url  below
        unique_hash = '32230a09ffe7b0011095e8cd627097a5'
        url = 'http://inasafe.org/en/_static/img/logo.png'
        path = tempfile.mktemp()

        file_downloader = FileDownloader(
            manager, url, path)
        try:
            result = file_downloader.download()
        except IOError as ex:
            raise IOError(ex)

        if result[0] is not True:
            _, error_message = result
            raise DownloadError(error_message)

        assert_hash_for_file(unique_hash, path)
