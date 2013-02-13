"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Import Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'bungcip@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '4/12/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from PyQt4.QtCore import (QRect, QCoreApplication, QUrl, QFile)
from PyQt4.QtGui import (QDialog, QProgressDialog, QMessageBox, QFileDialog)
from PyQt4.QtNetwork import (QNetworkAccessManager, QNetworkRequest,
                             QNetworkReply)
from import_dialog_base import Ui_ImportDialogBase

from third_party.bs4 import BeautifulSoup
#from bs4 import BeautifulSoup

import time
import os

from inasafe_lightmaps import InasafeLightMaps
from safe_qgis.exceptions import (CanceledImportDialogError, ImportDialogError)


class Response:
    """ Class that contains the response of httpRequest function. """
    pass


def httpRequest(theManager, theMethod, theUrl, theData=None, theHook=None):
    """
    Request the content of url through HTTP protocol.
    This function use QNetworkAccessManager for doing the request
    and deals with its asynchronous nature.

    Params:
        * theManager - instance of QNetworkAccessManager
        * theMethod - 'POST' or 'GET', other http method is not supported.
        * theUrl - url of content
        * theData : dict - dictionary that contains data for POST request.
                           ignored in GET request.
        * theHook - callback function to check progress of download
    Raises:
        * ImportDialogError - when network connection error.
        * NotImplementedError - when theMethod value is not 'POST' or 'GET'.
    Returns:
        A Response object.
    """
    myRequest = QNetworkRequest(QUrl(theUrl))

    if callable(theData) and theHook is None:
        theHook = theData
        theData = None

    if theMethod == 'GET':
        myReply = theManager.get(myRequest)
    elif theMethod == 'POST':
        # prepare POST data
        myPostData = QUrl()
        for myKey, myValue in theData.items():
            myPostData.addEncodedQueryItem(myKey, str(myValue))
        myPostData = myPostData.encodedQuery()

        # NOTE(gigih): this content type header don't support
        #              file upload.
        myRequest.setHeader(QNetworkRequest.ContentTypeHeader,
                            "application/x-www-form-urlencoded")

        myReply = theManager.post(myRequest, myPostData)
    else:
        raise NotImplementedError('%s not implemented' % theMethod)

    if theHook:
        myReply.downloadProgress.connect(theHook)

    # wait until finished
    while not myReply.isFinished():
        QCoreApplication.processEvents()
        time.sleep(0.1)

    if myReply.error() != QNetworkReply.NoError:
        raise ImportDialogError(myReply.errorString())

    # prepare Response object
    myResult = Response()
    myResult.content = str(myReply.readAll())
    myResult.url = str(myReply.url().toString())

    return myResult


def httpDownload(theManager, theUrl, theOutPath, theHook=None):
    """ Download file from theUrl.
    Params:
        * theManager - a QNetworkManager instance
        * theUrl - url of file
        * theOutPath - output path
        * theHook - callback function to check progress of download
    Raises:
        * IOError - when cannot create theOutPath
    """

    # prepare output path
    myFile = QFile(theOutPath)
    if not myFile.open(QFile.WriteOnly):
        raise IOError(myFile.errorString())

    # slot to write data to file
    def writeData():
        myFile.write(myReply.readAll())

    myRequest = QNetworkRequest(QUrl(theUrl))
    myReply = theManager.get(myRequest)
    myReply.readyRead.connect(writeData)

    if theHook:
        myReply.downloadProgress.connect(theHook)

    # wait until finished
    while not myReply.isFinished():
        QCoreApplication.processEvents()

    myFile.close()


class ImportDialog(QDialog, Ui_ImportDialogBase):

    def __init__(self, theParent=None, theIface=None):
        '''Constructor for the dialog.

        Args:
           * theParent - Optional widget to use as parent
        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        '''
        QDialog.__init__(self, theParent)
        self.parent = theParent
        self.setupUi(self)

        self.setWindowTitle(self.tr('Import Hot-Export'))

        self.iface = theIface
        self.url = 'http://hot-export.geofabrik.de'

        # creating progress dialog for download
        self.progressDialog = QProgressDialog(self)
        self.progressDialog.setAutoClose(False)
        self.progressDialog.setWindowTitle(self.tr("Hot-Export Download"))

        ## example location: depok
        self.minLongitude.setText('106.7685')
        self.minLatitude.setText('-6.4338')
        self.maxLongitude.setText('106.8629')
        self.maxLatitude.setText('-6.3656')

        self.map = InasafeLightMaps(self)
        self.map.setGeometry(QRect(10, 10, 300, 240))

        self.map.m_normalMap.zoomTo(9)
        self.map.setCenter(-6.4338, 106.7685)

        self.map.m_normalMap.updated.connect(self.updateExtent)

        self.nam = QNetworkAccessManager(self)

    def updateExtent(self):
        """ Update extent value in GUI based from value in map widget"""
        myExtent = self.map.getExtent()
        self.minLongitude.setText(str(myExtent[1]))
        self.minLatitude.setText(str(myExtent[0]))
        self.maxLongitude.setText(str(myExtent[3]))
        self.maxLatitude.setText(str(myExtent[2]))

    def on_pBtnDir_clicked(self):
        """ Show a dialog to choose directory """
        self.outDir.setText(QFileDialog.getExistingDirectory(
            self, self.tr("Select Directory")))

    def accept(self):
        """ Do import process """

        try:
            self.ensureDirExist()
            self.doImport()
            self.loadShapeFile()
            self.done(QDialog.Accepted)
        except CanceledImportDialogError:
            pass
        except Exception as myEx:
            QMessageBox.warning(self,
                                self.tr("Hot-Export Import Error"),
                                str(myEx))

            self.progressDialog.cancel()

    def progressEvent(self, theReceived, theTotal):
        """
        Hook function that called when doing http request.
        This function will update the value of progress bar and
        check if user press cancel button.

        Params:
            * theReceived : int - number of bytes received
            * theTotal : int - total bytes of download
        Raises:
            CanceledImportDialogError - when user press cancel button
        """

        QCoreApplication.processEvents()

        self.progressDialog.setMaximum(theTotal)
        self.progressDialog.setValue(theReceived)

        if self.progressDialog.wasCanceled():
            raise CanceledImportDialogError()

    def ensureDirExist(self):
        """
        Ensure directory path entered in dialog exist.
        When the path is not exist, this function will
        ask the user if he want to create it or not.

        Raises:
            CanceledImportDialogError - when user choose 'No'
                        in question dialog for creating directory.
        """

        myDir = str(self.outDir.text())

        if os.path.exists(myDir):
            return

        myTitle = self.tr("Directory %1 not exist").arg(myDir)
        myQuestion = self.tr(
            "Directory %1 not exist. Are you want to create it?"
        ).arg(myDir)
        myAnswer = QMessageBox.question(
            self, myTitle,
            myQuestion, QMessageBox.Yes | QMessageBox.No)

        if myAnswer == QMessageBox.Yes:
            os.makedirs(myDir)
        else:
            raise CanceledImportDialogError()

    def doImport(self):
        """
        Import shape files from Hot-Export.
        """

        self.progressDialog.show()
        self.progressDialog.setMaximum(100)
        self.progressDialog.setValue(0)

        ## setup necessary data to create new job in Hot-Export
        myPayload = {
            'job[region_id]': '1',  # 1 is indonesia
            'job[name]': 'InaSAFE job',
            'job[description]': 'Created from import feature in InaSAFE',
            'job[lonmin]': str(self.minLongitude.text()),
            'job[latmin]': str(self.minLatitude.text()),
            'job[lonmax]': str(self.maxLongitude.text()),
            'job[latmax]': str(self.maxLatitude .text()),
        }

        ## create a new job in Hot-Export
        self.progressDialog.setLabelText(
            self.tr("Create A New Job on Hot-Exports..."))
        myNewJobToken = self.createNewJob(myPayload)

        ## prepare tag
        self.progressDialog.setLabelText(
            self.tr("Set Preset to ... 'mapping from jakarta'"))
        myJobId = self.uploadTag(myPayload, myNewJobToken)

        myLabelText = "Waiting For Result Available on Server..." \
                      + " (http://hot-export.geofabrik.de/jobs/%1)"
        self.progressDialog.setLabelText(self.tr(myLabelText).arg(myJobId))
        myShapeUrl = self.getDownloadUrl(myJobId)

        ## download shape file from Hot-Export
        self.progressDialog.setLabelText(
            self.tr("Download Shape File..."))
        myFilePath = '/tmp/' + myJobId + '.shp.zip'
        self.downloadShapeFile(myShapeUrl, myFilePath)

        ## extract downloaded file to output directory
        myLabelText = "Extract Shape File... from %1 to %2"
        myLabelText = self.tr(myLabelText)
        myLabelText = myLabelText.arg(myFilePath).arg(self.outDir.text())
        self.progressDialog.setLabelText(myLabelText)

        self.extractZip(myFilePath, str(self.outDir.text()))

        self.progressDialog.done(QDialog.Accepted)

    def getAuthToken(self, theContent):
        '''Get authenticity_token value

        Args:
           * theContent - string containing html page from hot-exports
        Returns:
           authenticity_token value
        Raises:
           no exceptions explicitly raised
        '''

        ## FIXME(gigih): need fail-proof method to get authenticity_token
        myToken = theContent.split(
            'authenticity_token" type="hidden" value="')[1]
        myToken = myToken.split('"')[0]

        return myToken

    def createNewJob(self, thePayload):
        """ Fill form to create new hot-exports job.
        Args:
           * thePayload - dictionary
        Returns:
           authenticity_token value
        Raises:
           no exceptions explicitly raised
        """

        myJobResponse = httpRequest(self.nam, 'GET',
                                    self.url + '/newjob',
                                    self.progressEvent)
        myJobToken = self.getAuthToken(myJobResponse.content)

        thePayload['authenticity_token'] = myJobToken

        myWizardResponse = httpRequest(self.nam, 'POST',
                                       self.url + '/wizard_area',
                                       thePayload,
                                       self.progressEvent)
        myWizardToken = self.getAuthToken(myWizardResponse.content)
        return myWizardToken

    def uploadTag(self, thePayload, theToken):
        """
        Go to page http://hot-export.geofabrik.de and fill the needed data.
        Currently the preset file is set to "preset mapping from jakarta"
        in HotExport.

        Params:
            * thePayload - dictionary containing needed data in form
            * theToken   - authentication value from previous page
        Returns:
            Job Id
        """
        ## FIXME(gigih): upload buildings preset to hot-export
        thePayload['authenticity_token'] = theToken
        thePayload['presetfile'] = 4  # preset mapping from jakarta
        thePayload['default_tags'] = 'true'
        myTagResponse = httpRequest(
            self.nam, 'POST',
            self.url + '/tagupload',
            thePayload,
            self.progressEvent)
        myId = myTagResponse.url.split('/')[-1]

        return myId

    def getDownloadUrl(self, theJobId):
        """
        Get the url of shape files from Hot-Export
        Params:
            * theJobId - the id of job in Hot-Export
        Returns:
            url of shape files
        """

        myResultUrl = self.url + '/jobs/' + theJobId
        myIsReady = False
        myCountDown = 5     # in seconds
        mySleepTime = 0.05  # in seconds

        while myIsReady is False:
            ## we need to call QCoreApplication.processEvents() because
            ## for some reason, the signal not triggered inside this loop.
            QCoreApplication.processEvents()

            if self.progressDialog.wasCanceled():
                raise CanceledImportDialogError()

            ## check Hot-Export if shape file is ready.
            ## we only check Hot-Export each 5 seconds because we don't
            ## want to accidentally DDOS-ing it.
            if myCountDown <= 0:
                myResultResponse = httpRequest(self.nam, 'GET', myResultUrl,
                                               self.progressEvent)
                mySoup = BeautifulSoup(myResultResponse.content)
                myLinks = mySoup.find_all('a', text='ESRI Shapefile (zipped)')

                if len(myLinks) > 0:
                    myIsReady = True
                else:
                    myCountDown = 5

            ## delay
            time.sleep(mySleepTime)
            myCountDown -= mySleepTime

        ## return the first URL
        return self.url + myLinks[0].get('href')

    def downloadShapeFile(self, theUrl, theOutput):
        """
        Download shape file from theUrl and write to theOutput.
        Params:
            * theUrl - URL of shape file in Hot-Export
            * theOutput - path of output file
        """

        httpDownload(self.nam, theUrl, theOutput, self.progressEvent)

    def extractZip(self, thePath, theOutDir):
        """
        Extract all content of zip file from thePath to theOutDir.
        Args:
           * thePath - the path of zip file
           * theOutDir - output directory
        Raises:
            IOError - when cannot open thePath or theOutDir is not exist.
        """

        import zipfile

        ## extract all files...
        myHandle = open(thePath, 'rb')
        myZip = zipfile.ZipFile(myHandle)
        for myName in myZip.namelist():
            myOutPath = os.path.join(theOutDir, myName)
            myOutFile = open(myOutPath, 'wb')
            myOutFile.write(myZip.read(myName))
            myOutFile.close()

        myHandle.close()

    def loadShapeFile(self):
        """
        Load downloaded shape file to QGIS Main Window.
        """

        myDir = str(self.outDir.text())

        myLinePath = os.path.join(myDir, 'planet_osm_line.shp')
        myPolygonPath = os.path.join(myDir, 'planet_osm_polygon.shp')
        myPointPath = os.path.join(myDir, 'planet_osm_point.shp')

        self.iface.addVectorLayer(myLinePath, 'line', 'ogr')
        self.iface.addVectorLayer(myPolygonPath, 'polygon', 'ogr')
        self.iface.addVectorLayer(myPointPath, 'point', 'ogr')


if __name__ == '__main__':
    import sys
    from PyQt4.QtGui import (QApplication)

    app = QApplication(sys.argv)

    a = ImportDialog()
    a.show()
    app.exec_()
    #a.doImport()
