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

from PyQt4.QtCore import (QRect, SIGNAL)
from PyQt4.QtGui import (QDialog, QProgressDialog)
from import_dialog_base import Ui_ImportDialogBase

from bs4 import BeautifulSoup
import requests
import time

from third_party.lightmaps import LightMaps


class ImportDialog(QDialog, Ui_ImportDialogBase):

    def __init__(self, theParent=None):
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

        ## base url
        self.url = 'http://hot-export.geofabrik.de'

        ## example location: depok
        self.minLongitude.setText('106.7685')
        self.minLatitude.setText('-6.4338')
        self.maxLongitude.setText('106.8629')
        self.maxLatitude.setText('-6.3656')

        self.map = LightMaps(self)
        self.map.setGeometry(QRect(10, 10, 300, 240))
        self.map.setCenter(-6.4338, 106.7685 )


    def accept(self):

        self.doImport()
        self.done(QDialog.Accepted)

    def progressDlgCanceled(self):
        pass

    def doImport(self):
        # creating progress dialog for download
        self.progressDialog=QProgressDialog(self)
        self.progressDialog.setAutoClose(False)
        self.progressDialog.setWindowTitle(self.tr("Hot-Export Download"))
        self.connect(self.progressDialog,SIGNAL("canceled()"), self.progressDlgCanceled)

        self.progressDialog.show()
        self.progressDialog.setMaximum(100)
        self.progressDialog.setValue(0)

        myPayload = {
            'job[region_id]': '1', # 1 is indonesia
            'job[name]': 'depok test',
            'job[description]': 'just some test',

            'job[lonmin]': str(self.minLongitude.text()),
            'job[latmin]': str(self.minLatitude.text()),
            'job[lonmax]': str(self.maxLongitude.text()),
            'job[latmax]': str(self.maxLatitude .text()),
        }

        self.progressDialog.setLabelText(
            self.tr("Create A New Job on Hot-Exports..."))
        myNewJobToken = self.createNewJob(myPayload)
        self.progressDialog.setValue(10)

        self.progressDialog.setLabelText(
            self.tr("Upload Default Preset File..."))
        myJobId = self.uploadTag(myPayload, myNewJobToken)
        self.progressDialog.setValue(20)

        self.progressDialog.setLabelText(
            self.tr("Waiting For Result Available on Server... (http://hot-export.geofabrik.de/jobs/%s)" % myJobId))
        myShapeUrl = self.getDownloadUrl(myJobId)
        self.progressDialog.setValue(30)

        self.progressDialog.setLabelText(
            self.tr("Waiting For Result Available on Server..."))
        myOutputPath = '/tmp/' + myJobId + '.shp.zip'
        self.progressDialog.setValue(50)

        self.progressDialog.setLabelText(
            self.tr("Download Shape File..."))
        self.downloadShapeFile(myShapeUrl, myOutputPath)
        self.progressDialog.setValue(90)

        self.progressDialog.setLabelText(
            self.tr("Extract Shape File..."))
        self.extractZip(myOutputPath)
        self.progressDialog.setValue(100)


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
        myToken = theContent.split('authenticity_token" type="hidden" value="')[1]
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

        myJobResponse = requests.get(self.url + '/newjob')
        myJobToken = self.getAuthToken(myJobResponse.content)

        print "job token : " + myJobToken
        thePayload['authenticity_token'] = myJobToken

        myWizardResponse = requests.post(self.url + '/wizard_area', thePayload)
        myWizardToken = self.getAuthToken(myWizardResponse.content)

        return myWizardToken

    def uploadTag(self, thePayload, theToken):
        ## tag upload
        ## FIXME(gigih): upload buildings preset to hot-export
        thePayload['authenticity_token'] = theToken
        thePayload['presetfile'] = 4 ## preset mapping from jakarta
        thePayload['default_tags'] = 'true'
        myTagResponse = requests.post(self.url + '/tagupload', thePayload)
        myId = myTagResponse.url.split('/')[-1]

        return myId

    def getDownloadUrl(self, theJobId):
        myResultUrl = self.url + '/jobs/' + theJobId
        myIsReady = False

        while myIsReady is False:
            myResultResponse = requests.get(myResultUrl)
            mySoup = BeautifulSoup(myResultResponse.content)
            myLinks = mySoup.find_all('a', text='ESRI Shapefile (zipped)')
            if len(myLinks) > 0:
                myIsReady = True
            else:
                print "\tstill not ready. wait 5 seconds..."
                time.sleep(5)

        return self.url + myLinks[0].get('href')

    def downloadShapeFile(self, theUrl, theOutput):
        myShapeResponse = requests.get(theUrl)

        myShapeFile = open(theOutput, 'wb')
        myShapeFile.write(myShapeResponse.content)
        myShapeFile.close()


    def extractZip(self, thePath):
        import zipfile, os

        myHandle = open(thePath, 'rb')
        myZip = zipfile.ZipFile(myHandle)
        for myName in myZip.namelist():
            #FIXME(gigih): don't put the file in temporary folder
            myOutPath = os.path.join(os.path.dirname(thePath), myName)
            myOutFile = open(myOutPath, 'wb')
            myOutFile.write(myZip.read(myName))
            myOutFile.close()
        myHandle.close()


if __name__ == '__main__':
    import sys
    from PyQt4.QtGui import (QApplication)

    app = QApplication(sys.argv)

    a = ImportDialog()
    a.show()
    app.exec_()
    #a.doImport()
