"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

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

from PyQt4.QtCore import QUrl, QObject, pyqtSignal
from PyQt4.QtGui import (QDialog)
from PyQt4.QtNetwork import (QNetworkAccessManager, QNetworkReply)
from safe_qgis.import_dialog import (httpDownload, httpRequest, ImportDialog)

from safe_qgis.utilities_test import (getQgisTestApp, assertHashForFile)

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
LOGGER = logging.getLogger('InaSAFE')

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data/test_files')


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
        self.readyRead.emit()
        self.downloadProgress.emit(self.progress, 4)
        return self.progress >= 4

    def readAll(self):
        myContent = self.content
        self.content = ""
        return myContent

    def url(self):
        return QUrl(self._url)

    def error(self):
        return  QNetworkReply.NoError


class FakeQNetworkAccessManager:
    def post(self, theRequest, theData=None):
        return self.request(theRequest)

    def get(self, theRequest):
        return self.request(theRequest)

    def request(self, theRequest):
        myUrl = str(theRequest.url().toString())
        myReply = FakeQNetworkReply()

        if myUrl == 'http://hot-export.geofabrik.de/newjob':
            myReply.content = readAll('test-importdlg-newjob.html')
        elif myUrl == 'http://hot-export.geofabrik.de/wizard_area':
            myReply.content = readAll('test-importdlg-wizardarea.html')
        elif myUrl == 'http://hot-export.geofabrik.de/tagupload':
            myReply.content = readAll('test-importdlg-job.html')
            myReply._url = 'http://hot-export.geofabrik.de/jobs/1990'
        elif myUrl == 'http://hot-export.geofabrik.de/jobs/1990':
            myReply.content = readAll('test-importdlg-job.html')
        elif myUrl == \
                'http://hot-export.geofabrik.de/download/' + \
                '006113/extract.shp.zip':
            myReply.content = readAll("test-importdlg-extractzip.zip")

        return myReply


def readAll(thePath):
    """ Helper function to load all content of thePath
    in TEST_DATA_DIR folder """
    myPath = os.path.join(TEST_DATA_DIR, thePath)
    myHandle = open(myPath, 'r')
    myContent = myHandle.read()
    myHandle.close()
    return myContent


class ImportDialogTest(unittest.TestCase):
    """Test Import Dialog widget"""

    def test_httpRequest(self):
        myManager = QNetworkAccessManager(PARENT)

        # we use httpbin service to test HTTP Request
        myUrl = 'http://httpbin.org/html'
        myResponse = httpRequest(myManager, 'GET', myUrl)

        myMessage = "Url don't match. Expected {0} but got {1} instead."
        assert myResponse.url == myUrl, myMessage.format(myUrl, myResponse.url)

        myExpectedContent = readAll('test-importdlg-httprequest.html')
        assert myResponse.content == myExpectedContent, "Content don't match."

        myUrl = 'http://httpbin.org/post'
        myData = {'name': 'simple POST test', 'value': 'Hello World'}
        myResponse = httpRequest(myManager, 'POST', myUrl, myData)

        myPos = myResponse.content.find('"name": "simple POST test"')
        myMessage = "POST Request failed. The response is %s".format(
            myResponse.content)
        assert myPos != -1, myMessage

    def test_httpDownload(self):
        myManager = QNetworkAccessManager(PARENT)

        # NOTE(gigih):
        # this is the hash of google front page.
        # I think we can safely assume that the content
        # of google.com never changes (probably).
        #
        myHash = 'd4b691cd9d99117b2ea34586d3e7eeb8'
        myUrl = 'http://google.com'
        myTempFilePath = tempfile.mktemp()

        httpDownload(myManager, myUrl, myTempFilePath)

        assertHashForFile(myHash, myTempFilePath)

    def setUp(self):
        self.importDlg = ImportDialog(PARENT, IFACE)

        ## provide Fake QNetworkAccessManager for self.nam
        self.importDlg.nam = FakeQNetworkAccessManager()

        self.payload = {
            'job[region_id]': '1',  # 1 is indonesia
            'job[name]': 'InaSAFE job',
            'job[description]': 'Test',

            'job[lonmin]': '92.7188',
            'job[latmin]': '-19.7515',
            'job[lonmax]': '141.0586',
            'job[latmax]': '14.8329',
        }
        self.token = "cX0+IuzRZn1UjFBI94kqR4JpaZoBRM+SOhFlUSPerBE="

    def test_getAuthToken(self):
        myContent = readAll('test-importdlg-newjob.html')
        myResult = self.importDlg.getAuthToken(myContent)
        myMessage = "Auth Token don't match. expected %s but got %s" % \
                    (self.token, myResult)
        assert myResult == self.token, myMessage

    def test_createNewJob(self):
        myToken = self.importDlg.createNewJob(self.payload)
        myMessage = "Token don't match. Expected %s but got %s." % (
            self.token, myToken)

        assert myToken == self.token, myMessage

    def test_uploadTag(self):
        myJobId = self.importDlg.uploadTag(self.payload, self.token)
        assert myJobId == '1990'

    def test_getDownloadUrl(self):
        myUrl = self.importDlg.getDownloadUrl('1990')
        myExpected = \
            'http://hot-export.geofabrik.de/download/006113/extract.shp.zip'
        myMessage = "URL don't match. Expected %s but got %s" % (
            myUrl, myExpected)
        assert myUrl == myExpected

    def test_downloadShapeFile(self):
        myUrl = 'http://hot-export.geofabrik.de/' + \
                'download/006113/extract.shp.zip'
        myTempFilePath = tempfile.mktemp('shapefiles')
        self.importDlg.downloadShapeFile(myUrl, myTempFilePath)

        myMessage = "file %s not exist" % myTempFilePath
        assert os.path.exists(myTempFilePath), myMessage

        # cleanup
        os.remove(myTempFilePath)

    def test_extractZip(self):
        myInput = os.path.join(TEST_DATA_DIR, 'test-importdlg-extractzip.zip')
        myOutDir = tempfile.mkdtemp()

        self.importDlg.extractZip(myInput, myOutDir)

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

    def test_doImport(self):
        myOutDir = tempfile.mkdtemp()
        self.importDlg.outDir.setText(myOutDir)
        self.importDlg.doImport()

        myResult = self.importDlg.progressDialog.result()
        myMessage = "result dont match. current result is %s " % myResult
        assert myResult == QDialog.Accepted

    def test_loadShapeFile(self):
        """ test loading shape file to QGIS Main Window """

        myInput = os.path.join(TEST_DATA_DIR, 'test-importdlg-extractzip.zip')
        myOutDir = tempfile.mkdtemp()

        self.importDlg.extractZip(myInput, myOutDir)

        # outDir must be set to myOutDir because loadShapeFile() use
        # that variable to determine the location of shape files.
        self.importDlg.outDir.setText(myOutDir)

        self.importDlg.loadShapeFile()

        #FIXME(gigih): need to check if layer is loaded to QGIS

        # remove temporary folder and all of its content
        shutil.rmtree(myOutDir)


if __name__ == '__main__':
    suite = unittest.makeSuite(ImportDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
