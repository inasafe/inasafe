# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Import Dialog Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'bungcip@gmail.com'
__date__ = '05/02/2013'
__copyright__ = ('Copyright 2013, Australia Indonesia Facility for '
                 'Disaster Reduction')

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import

import logging
import unittest
import tempfile
import shutil
import os

from PyQt4.QtCore import QObject, pyqtSignal, QVariant, QByteArray, QUrl
from PyQt4.QtNetwork import QNetworkReply

from safe.definitions.constants import INASAFE_TEST
from safe.utilities.osm_downloader import fetch_zip, extract_zip
from safe.test.utilities import standard_data_path, get_qgis_app
from safe.common.version import get_version
from safe.utilities.gis import qgis_version

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)
LOGGER = logging.getLogger('InaSAFE')


class MockQNetworkReply(QObject):
    """A mock network reply for testing.

    .. versionadded:: 3.2

    :param parent:
    :type parent:
    """
    readyRead = pyqtSignal()
    finished = pyqtSignal()
    downloadProgress = pyqtSignal('qint64', 'qint64')

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.progress = 0
        self.content = ""
        self._url = ""

    # noinspection PyDocstring,PyPep8Naming
    def isFinished(self):
        """simulate download progress."""
        self.progress += 1
        # noinspection PyUnresolvedReferences
        self.readyRead.emit()
        # noinspection PyUnresolvedReferences
        self.downloadProgress.emit(self.progress, 4)
        if self.progress >= 4:
            # noinspection PyUnresolvedReferences
            self.finished.emit()
            return True
        else:
            return False

    # noinspection PyDocstring,PyPep8Naming
    def readAll(self):
        content = self.content
        self.content = ""
        return content

    # noinspection PyDocstring,PyPep8Naming
    def read(self, size):
        content = self.content
        self.content = ""
        # content = string while the input parameter size in QByteArray
        data = QByteArray(content)
        data.chop(data.size() - size)
        return str(data)

    # noinspection PyDocstring,PyPep8Naming
    def url(self):
        return QUrl(self._url)

    # noinspection PyDocstring,PyPep8Naming,PyMethodMayBeStatic
    def error(self):
        return QNetworkReply.NoError

    # noinspection PyDocstring,PyPep8Naming,PyMethodMayBeStatic
    def size(self):
        data = QByteArray(self.content)
        return data.size()

    # noinspection PyDocstring,PyPep8Naming,PyMethodMayBeStatic
    # pylint: disable=W0613
    def attribute(self):
        return QVariant()
        # pylint: enable=W0613


# noinspection PyClassHasNoInit
class FakeQNetworkAccessManager:
    """Mock network manager for testing.

    .. versionadded:: 3.2
    """
    # noinspection PyDocstring,PyPep8Naming,PyMethodMayBeStatic
    # pylint: disable=W0613
    def post(self, request_url, data=None):
        """Mock handler for post requests.
        :param request_url: Requested url.
        :param data: Payload data (ignored).
        """
        _ = data  # ignored
        return self.request(request_url)

    # pylint: enable=W0613

    # noinspection PyDocstring,PyPep8Naming,PyMethodMayBeStatic
    def get(self, request_url):
        """Mock handler for a get request.
        :param request_url: Url being requested.
        """
        return self.request(request_url)

    # noinspection PyDocstring,PyPep8Naming,PyMethodMayBeStatic
    def request(self, request_url):
        """Mock handler for an http request.
        :param request_url: Url being requested.
        """
        url = str(request_url.url().toString())
        reply = MockQNetworkReply()

        if url == 'http://hot-export.geofabrik.de/newjob':
            reply.content = read_all('test-importdlg-newjob.html')
        elif url == 'http://hot-export.geofabrik.de/wizard_area':
            reply.content = read_all('test-importdlg-wizardarea.html')
        elif url == 'http://hot-export.geofabrik.de/tagupload':
            reply.content = read_all('test-importdlg-job.html')
            reply._url = 'http://hot-export.geofabrik.de/jobs/1990'
        elif url == 'http://hot-export.geofabrik.de/jobs/1990':
            reply.content = read_all('test-importdlg-job.html')
        elif url == ('http://osm.inasafe.org/buildings-shp?'
                     'bbox=20.389938354492188,-34.10782492987083'
                     ',20.712661743164062,'
                     '-34.008273470938335&qgis_version=%s'
                     '&inasafe_version=%s'
                     '&lang=en' % (qgis_version(), get_version())):
            reply.content = read_all("test-importdlg-extractzip.zip")

        return reply


def read_all(path):
    """ Helper function to load all content of path in
        safe/test/data/control/files folder.

    :param path: File name to read in.
    :type path: str

    :returns: The file contents.
    :rtype: str
    """
    control_files_dir = standard_data_path('control', 'files')
    path = os.path.join(control_files_dir, path)
    handle = open(path, 'r')
    content = handle.read()
    handle.close()
    return content


class OsmDownloaderTest(unittest.TestCase):
    """Test the OSM Downloader.

    .. versionadded:: 3.2
    """
    # noinspection PyPep8Naming
    def setUp(self):
        """Runs before each test."""
        # provide Fake QNetworkAccessManager
        self.network_manager = FakeQNetworkAccessManager()

    def test_fetch_zip(self):
        """Test fetch zip method.

        .. versionadded:: 3.2
        """
        feature = 'buildings'
        url = (
            'http://osm.inasafe.org/buildings-shp?'
            'bbox=20.389938354492188,-34.10782492987083'
            ',20.712661743164062,-34.008273470938335')
        path = tempfile.mktemp('shapefiles')
        fetch_zip(url, path, feature)

        message = "file %s not exist" % path
        assert os.path.exists(path), message

        # cleanup
        os.remove(path)

    def test_extract_zip(self):
        """Test extract_zip method.
        This function will only take care of one file for each extensions.
        If many files has the same extension, only the last one will be copied.

        .. versionadded:: 3.2
        """
        base_path = tempfile.mkdtemp()
        base_file_path = os.path.join(base_path, 'test')
        zip_file_path = standard_data_path(
            'control',
            'files',
            'test-importdlg-extractzip.zip')
        extract_zip(zip_file_path, base_file_path)

        message = "file {0} not exist"

        path = '%s.shp' % base_file_path
        assert os.path.exists(path), message.format(path)

        # remove temporary folder and all of its content
        shutil.rmtree(base_path)

    def test_load_shapefile(self):
        """Test loading shape file to QGIS Main Window.

        .. versionadded:: 3.2
        """
        zip_file_path = standard_data_path(
            'control', 'files', 'test-importdlg-extractzip.zip')
        output_path = tempfile.mkdtemp()

        extract_zip(zip_file_path, output_path)

        shutil.rmtree(output_path)


if __name__ == '__main__':
    suite = unittest.makeSuite(OsmDownloaderTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
