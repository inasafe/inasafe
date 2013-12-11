"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Import Dialog Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.common.testing import get_qgis_app

__author__ = 'bungcip@gmail.com'
__date__ = '05/02/2013'
__copyright__ = ('Copyright 2013, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import logging

import os
import tempfile
import shutil

from PyQt4.QtCore import QUrl, QObject, pyqtSignal, QVariant
from PyQt4.QtGui import (QDialog)
from PyQt4.QtNetwork import (QNetworkAccessManager, QNetworkReply)
from safe_qgis.tools.osm_downloader import OsmDownloader
from safe_qgis.utilities.utilities import download_url
from safe_qgis.utilities.utilities_for_testing import (
    assert_hash_for_file)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
LOGGER = logging.getLogger('InaSAFE')

TEST_DATA_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), '../../test/test_data/test_files'))


class MockQNetworkReply(QObject):
    """A mock network reply for testing.

    :param parent:
    :type parent:
    """
    readyRead = pyqtSignal()
    downloadProgress = pyqtSignal('qint64', 'qint64')

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.progress = 0
        self.content = ""
        self._url = ""

    #noinspection PyDocstring,PyPep8Naming
    def isFinished(self):
        """ simulate download progress """
        self.progress += 1
        # noinspection PyUnresolvedReferences
        self.readyRead.emit()
        # noinspection PyUnresolvedReferences
        self.downloadProgress.emit(self.progress, 4)
        return self.progress >= 4

    #noinspection PyDocstring,PyPep8Naming
    def readAll(self):
        myContent = self.content
        self.content = ""
        return myContent

    #noinspection PyDocstring,PyPep8Naming
    def url(self):
        return QUrl(self._url)

    #noinspection PyDocstring,PyPep8Naming,PyMethodMayBeStatic
    def error(self):
        return QNetworkReply.NoError

    #noinspection PyDocstring,PyPep8Naming,PyMethodMayBeStatic
    # pylint: disable=W0613
    def attribute(self, theAttribute):
        return QVariant()
        # pylint: enable=W0613


#noinspection PyClassHasNoInit
class FakeQNetworkAccessManager:
    """Mock network manager for testing."""
    #noinspection PyDocstring,PyPep8Naming,PyMethodMayBeStatic
    # pylint: disable=W0613
    def post(self, theRequest, theData=None):
        """Mock handler for post requests.
        :param theRequest: Requested url.
        :param theData: Payload data (ignored).
        """
        _ = theData  # ignored
        return self.request(theRequest)

    # pylint: enable=W0613

    #noinspection PyDocstring,PyPep8Naming,PyMethodMayBeStatic
    def get(self, theRequest):
        """Mock handler for a get request.
        :param theRequest: Url being requested.
        """
        return self.request(theRequest)

    #noinspection PyDocstring,PyPep8Naming,PyMethodMayBeStatic
    def request(self, theRequest):
        """Mock handler for an http request.
        :param theRequest: Url being requested.
        """
        myUrl = str(theRequest.url().toString())
        myReply = MockQNetworkReply()

        print myUrl

        if myUrl == 'http://hot-export.geofabrik.de/newjob':
            myReply.content = read_all('test-importdlg-newjob.html')
        elif myUrl == 'http://hot-export.geofabrik.de/wizard_area':
            myReply.content = read_all('test-importdlg-wizardarea.html')
        elif myUrl == 'http://hot-export.geofabrik.de/tagupload':
            myReply.content = read_all('test-importdlg-job.html')
            myReply._url = 'http://hot-export.geofabrik.de/jobs/1990'
        elif myUrl == 'http://hot-export.geofabrik.de/jobs/1990':
            myReply.content = read_all('test-importdlg-job.html')
        elif myUrl == ('http://osm.linfiniti.com/buildings-shp?'
                       'bbox=20.389938354492188,-34.10782492987083'
                       ',20.712661743164062,'
                       '-34.008273470938335&qgis_version=2'):
            myReply.content = read_all("test-importdlg-extractzip.zip")

        return myReply


def read_all(path):
    """ Helper function to load all content of path in TEST_DATA_DIR folder.
    :param path: File name to read in.
    :type path: str

    :returns: The file contents.
    :rtype: str
    """
    path = os.path.join(TEST_DATA_DIR, path)
    handle = open(path, 'r')
    content = handle.read()
    handle.close()
    return content


class ImportDialogTest(unittest.TestCase):
    """Test Import Dialog widget
    """
    def setUp(self):
        """Runs before each test."""
        self.dialog = OsmDownloader(PARENT, IFACE)

        ## provide Fake QNetworkAccessManager for self.network_manager
        self.dialog.network_manager = FakeQNetworkAccessManager()

    #noinspection PyMethodMayBeStatic
    def test_download_url(self):
        """Test we can download a zip. Uses a mock network stack."""
        manager = QNetworkAccessManager(PARENT)

        # NOTE(gigih):
        # this is the hash of google front page.
        # I think we can safely assume that the content
        # of google.com never changes (probably).
        # ...or not...changed on 5 Dec 2013 by Tim to hash below...
        unique_hash = 'd4b691cd9d99117b2ea34586d3e7eeb8'
        url = 'http://google.com'
        path = tempfile.mktemp()

        download_url(manager, url, path)

        assert_hash_for_file(unique_hash, path)

    def test_fetch_zip(self):
        """Test fetch zip method."""
        url = (
            'http://osm.linfiniti.com/buildings-shp?'
            'bbox=20.389938354492188,-34.10782492987083'
            ',20.712661743164062,'
            '-34.008273470938335&obj=building')
        path = tempfile.mktemp('shapefiles')
        self.dialog.fetch_zip(url, path)

        message = "file %s not exist" % path
        assert os.path.exists(path), message

        # cleanup
        os.remove(path)

    def test_extract_zip(self):
        """Test extract_zip method."""
        base_path = tempfile.mkdtemp()
        zipfile = os.path.abspath(os.path.join(
            TEST_DATA_DIR, 'test-importdlg-extractzip.zip'))
        self.dialog.extract_zip(zipfile, base_path)

        message = "file {0} not exist"

        file_name = 'planet_osm_line.shp'
        path = os.path.join(base_path, file_name)
        assert os.path.exists(path), message.format(file_name)

        file_name = 'planet_osm_point.shp'
        path = os.path.join(base_path, file_name)
        assert os.path.exists(path), message.format(file_name)

        file_name = 'planet_osm_polygon.shp'
        path = os.path.join(base_path, file_name)
        assert os.path.exists(path), message.format(file_name)

        # remove temporary folder and all of its content
        shutil.rmtree(base_path)

    def test_download(self):
        """Test download method."""
        output_directory = tempfile.mkdtemp()
        self.dialog.output_directory.setText(output_directory)
        self.dialog.min_longitude.setText('20.389938354492188')
        self.dialog.min_latitude.setText('-34.10782492987083')
        self.dialog.max_longitude.setText('20.712661743164062')
        self.dialog.max_latitude.setText('-34.008273470938335')
        self.dialog.download('buildings')

        result = self.dialog.progress_dialog.result()
        message = "result do not match. current result is %s " % result
        assert result == QDialog.Accepted, message

    def test_load_shapefile(self):
        """Test loading shape file to QGIS Main Window """

        zip_path = os.path.abspath(os.path.join(
            TEST_DATA_DIR, 'test-importdlg-extractzip.zip'))
        output_path = tempfile.mkdtemp()

        self.dialog.extract_zip(zip_path, output_path)

        # outDir must be set to output_path because loadShapeFile() use
        # that variable to determine the location of shape files.
        self.dialog.output_directory.setText(output_path)

        self.dialog.load_shapefile('buildings')

        shutil.rmtree(output_path)


if __name__ == '__main__':
    suite = unittest.makeSuite(ImportDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
