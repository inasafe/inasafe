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

from safe_qgis import import_dialog
from safe_qgis.utilities_test import getQgisTestApp

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
LOGGER = logging.getLogger('InaSAFE')

TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data/test_files')


class Mock:
    pass


def readAll(thePath):
    """ Helper function to load all content of thePath
    in TEST_DATA_DIR folder """
    myPath = os.path.join(TEST_DATA_DIR, thePath)
    myHandle = open(myPath, 'r')
    myContent = myHandle.read()
    myHandle.close()
    return myContent


def fakeResponse(theUrl, theData=None, hooks=None):
    """ replacement function for requests.get and requests.post """
    myMock = Mock()

    if theUrl == 'http://hot-export.geofabrik.de/newjob':
        myMock.content = readAll('test-importdlg-newjob.html')
    elif theUrl == 'http://hot-export.geofabrik.de/wizard_area':
        myMock.content = readAll('test-importdlg-wizardarea.html')
    elif theUrl == 'http://hot-export.geofabrik.de/tagupload':
        myMock.content = readAll('test-importdlg-job.html')
        myMock.url = 'http://hot-export.geofabrik.de/jobs/1990'
    elif theUrl == 'http://hot-export.geofabrik.de/jobs/1990':
        myMock.content = readAll('test-importdlg-job.html')
    elif theUrl == \
            'http://hot-export.geofabrik.de/download/006113/extract.shp.zip':
        myMock.content = "HELLO WORLD!! THIS IS DUMMY CONTENT"

    return myMock

import_dialog.requests.get = fakeResponse
import_dialog.requests.post = fakeResponse


class ImportDialogTest(unittest.TestCase):
    """Test Import Dialog widget"""

    def setUp(self):
        self.importDlg = import_dialog.ImportDialog(PARENT)
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

        assert myToken == 'cX0+IuzRZn1UjFBI94kqR4JpaZoBRM+SOhFlUSPerBE='

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

     # NOTE(gigih): this function fail because qgis.util.iface
     # don't exist outside of QGIS Application
#    def test_loadShapeFile(self):
#        """ test loading shape file to QGIS Main Window """
#
#        myInput = os.path.join(TEST_DATA_DIR, 'test-importdlg-extractzip.zip')
#        myOutDir = tempfile.mkdtemp()
#
#        self.importDlg.extractZip(myInput, myOutDir)
#
#        # outDir must be set to myOutDir because loadShapeFile() use
#        # that variable to determine the location of shape files.
#        self.importDlg.outDir.setText(myOutDir)
#
#        self.importDlg.loadShapeFile()
#
#        #FIXME(gigih): need to check if layer is loaded to QGIS
#
#        # remove temporary folder and all of its content
#        shutil.rmtree(myOutDir)


if __name__ == '__main__':
    suite = unittest.makeSuite(ImportDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
