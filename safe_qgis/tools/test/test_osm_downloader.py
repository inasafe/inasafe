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

import unittest
import logging

import os
import tempfile
import shutil

# this import required to enable PyQt API v2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611

from PyQt4.QtCore import QUrl, QObject, pyqtSignal, QVariant
from PyQt4.QtGui import (QDialog)
from PyQt4.QtNetwork import (QNetworkAccessManager, QNetworkReply)
from safe_qgis.tools.osm_downloader import OsmDownloader
from safe_qgis.utilities.utilities import download_url
from safe_qgis.utilities.utilities_for_testing import (
    get_qgis_app,
    assert_hash_for_file)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
LOGGER = logging.getLogger('InaSAFE')

TEST_DATA_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), '../../test/test_data/test_files'))


class FakeQNetworkReply(QObject):
    readyRead = pyqtSignal()
    downloadProgress = pyqtSignal('qint64', 'qint64')

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.progress = 0
        self.content = ""
        self._url = ""

    def isFinished(self):
        """ simulate download progress """
        self.progress += 1
        # noinspection PyUnresolvedReferences
        self.readyRead.emit()
        # noinspection PyUnresolvedReferences
        self.downloadProgress.emit(self.progress, 4)
        return self.progress >= 4

    def readAll(self):
        myContent = self.content
        self.content = ""
        return myContent

    def url(self):
        return QUrl(self._url)

    def error(self):
        return QNetworkReply.NoError

    # pylint: disable=W0613
    def attribute(self, theAttribute):
        return QVariant()
        # pylint: enable=W0613


class FakeQNetworkAccessManager:
    """Mock network manager for testing."""
    # pylint: disable=W0613
    def post(self, theRequest, theData=None):
        """Mock handler for post requests.
        :param theRequest: Requested url.
        :param theData: Payload data (ignored).
        """
        _ = theData  # ignored
        return self.request(theRequest)

    # pylint: enable=W0613

    def get(self, theRequest):
        """Mock handler for a get request.
        :param theRequest: Url being requested.
        """
        return self.request(theRequest)

    def request(self, theRequest):
        """Mock handler for an http request.
        :param theRequest: Url being requested.
        """
        myUrl = str(theRequest.url().toString())
        myReply = FakeQNetworkReply()

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
                       '-34.008273470938335'):
            myReply.content = read_all("test-importdlg-extractzip.zip")

        return myReply


def read_all(path):
    """ Helper function to load all content of path in TEST_DATA_DIR folder.
    :param path: File name to read in.
    :type path: str

    :returns: The file contents.
    :rtype: str
    """
    myPath = os.path.join(TEST_DATA_DIR, path)
    myHandle = open(myPath, 'r')
    myContent = myHandle.read()
    myHandle.close()
    return myContent


class ImportDialogTest(unittest.TestCase):
    """Test Import Dialog widget
    """
    def setUp(self):
        """Runs before each test."""
        self.importDlg = OsmDownloader(PARENT, IFACE)

        ## provide Fake QNetworkAccessManager for self.network_manager
        self.importDlg.network_manager = FakeQNetworkAccessManager()

    def test_download_url(self):
        """Test we can download a zip. Uses a mock network stack."""
        myManager = QNetworkAccessManager(PARENT)

        # NOTE(gigih):
        # this is the hash of google front page.
        # I think we can safely assume that the content
        # of google.com never changes (probably).
        #
        myHash = 'd4b691cd9d99117b2ea34586d3e7eeb8'
        myUrl = 'http://google.com'
        myTempFilePath = tempfile.mktemp()

        download_url(myManager, myUrl, myTempFilePath)

        assert_hash_for_file(myHash, myTempFilePath)

    def test_fetch_zip(self):
        """Test fetch zip method."""
        myUrl = 'http://osm.linfiniti.com/buildings-shp?' + \
                'bbox=20.389938354492188,-34.10782492987083' \
                ',20.712661743164062,' + \
                '-34.008273470938335&obj=building'
        myTempFilePath = tempfile.mktemp('shapefiles')
        self.importDlg.fetch_zip(myUrl, myTempFilePath)

        myMessage = "file %s not exist" % myTempFilePath
        assert os.path.exists(myTempFilePath), myMessage

        # cleanup
        os.remove(myTempFilePath)

    def test_extract_zip(self):
        """Test extract_zip method."""
        myOutDir = tempfile.mkdtemp()
        myInput = os.path.abspath(os.path.join(
            TEST_DATA_DIR, 'test-importdlg-extractzip.zip'))
        self.importDlg.extract_zip(myInput, myOutDir)

        myMessage = "file {0} not exist"

        myFile = 'planet_osm_line.shp'
        myPath = os.path.join(myOutDir, myFile)
        assert os.path.exists(myPath), myMessage.format(myFile)

        myFile = 'planet_osm_point.shp'
        myPath = os.path.join(myOutDir, myFile)
        assert os.path.exists(myPath), myMessage.format(myFile)

        myFile = 'planet_osm_polygon.shp'
        myPath = os.path.join(myOutDir, myFile)
        assert os.path.exists(myPath), myMessage.format(myFile)

        # remove temporary folder and all of its content
        shutil.rmtree(myOutDir)

    def test_download(self):
        """Test download method."""
        myOutDir = tempfile.mkdtemp()
        self.importDlg.outDir.setText(myOutDir)
        self.importDlg.minLongitude.setText('20.389938354492188')
        self.importDlg.minLatitude.setText('-34.10782492987083')
        self.importDlg.maxLongitude.setText('20.712661743164062')
        self.importDlg.maxLatitude.setText('-34.008273470938335')
        self.importDlg.download()

        myResult = self.importDlg.progressDialog.result()
        myMessage = "result do not match. current result is %s " % myResult
        assert myResult == QDialog.Accepted, myMessage

    def test_load_shapefile(self):
        """Test loading shape file to QGIS Main Window """

        myInput = os.path.abspath(os.path.join(
            TEST_DATA_DIR, 'test-importdlg-extractzip.zip'))
        myOutDir = tempfile.mkdtemp()

        self.importDlg.extract_zip(myInput, myOutDir)

        # outDir must be set to myOutDir because loadShapeFile() use
        # that variable to determine the location of shape files.
        self.importDlg.outDir.setText(myOutDir)

        self.importDlg.load_shapefile()

        #FIXME(gigih): need to check if layer is loaded to QGIS

        # remove temporary folder and all of its content
        shutil.rmtree(myOutDir)


if __name__ == '__main__':
    suite = unittest.makeSuite(ImportDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
