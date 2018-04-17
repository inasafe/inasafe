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

# AG: Although we don't use qgis here, qgis should be imported before PyQt to
#  force this test to use SIP API V.2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import

from safe.utilities.file_downloader import FileDownloader
from safe.common.exceptions import DownloadError
from safe.test.utilities import assert_hash_for_file, get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting='InaSAFETest')


class FileDownloaderTest(unittest.TestCase):
    """Test FileDownloader class."""
    # noinspection PyMethodMayBeStatic
    def test_download(self):
        """Test download."""

        # NOTE(gigih):
        # this is the hash of google front page.
        # I think we can safely assume that the content
        # of google.com never changes (probably).
        # ...or not...changed on 5 Dec 2013 ...
        # ...and changed on 28 Apr 2014 by Tim to hash and url below
        # ...and changed on 9 Dec 2014 by Akbar to hash and url below
        # ...and changed on 16 Dec 2016 by Etienne to hash and url below
        unique_hash = '1fbe0165bd686a0aff8ab647ae255da6'
        url = 'http://www.google.com/images/srpr/logo11w.png'
        path = tempfile.mktemp()

        file_downloader = FileDownloader(url, path)
        try:
            result = file_downloader.download()
        except IOError as ex:
            raise IOError(ex)

        if result[0] is not True:
            _, error_message = result
            raise DownloadError(error_message)

        assert_hash_for_file(unique_hash, path)
