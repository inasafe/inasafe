"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Functions Dialog.**

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




from PyQt4.QtGui import (QDialog)
from import_dialog_base import Ui_ImportDialogBase

from bs4 import BeautifulSoup
import requests
import time


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

        ## example location: depok
        self.minLongitude.setText('106.7685')
        self.minLatitude.setText('-6.4338')
        self.maxLongitude.setText('106.8629')
        self.maxLatitude.setText('-6.3656')

    def accept(self):
        print "hore"
        self.done(QDialog.Accepted)


    def getToken(self, theContent):
        ## we need to get authenticity_token value
        ## FIXME(gigih): need fail-proof method to get authenticity_token
        myToken = theContent.split('authenticity_token" type="hidden" value="')[1]
        myToken = myToken.split('"')[0]

        return myToken


    def createNewJob(self):

        myUrl = 'http://hot-export.geofabrik.de'

        ## Job
        myJobResponse = requests.get(myUrl + '/newjob')
        myJobToken = self.getToken(myJobResponse.content)

        print "job token : " + myJobToken


        ## wizard area
        myPayload = {
            'authenticity_token': myJobToken,

            'job[region_id]': '1', # 1 is indonesia
            'job[name]': 'depok test',
            'job[description]': 'just some test',

            'job[lonmin]': str(self.minLongitude.text()),
            'job[latmin]': str(self.minLatitude.text()),
            'job[lonmax]': str(self.maxLongitude.text()),
            'job[latmax]': str(self.maxLatitude .text()),
        }
        myWizardResponse = requests.post(myUrl + '/wizard_area', myPayload)
        myWizardToken = self.getToken(myWizardResponse.content)

        print "wizard token : " + myWizardToken

        ## tag upload
        myPayload['authenticity_token'] = myWizardToken
        myTagResponse = requests.post(myUrl + '/tagupload', myPayload)
        myId = myTagResponse.url.split('/')[-1]

        ## wait until download page is ready
        print "wait until download page is ready...."
        myResultUrl = myUrl + '/jobs/' + myId
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

        print "download shape file...."

        ## only need first link
        myShapeUrl = myUrl + myLinks[0].get('href')
        myShapeResponse = requests.get(myShapeUrl)

        ## FIXME(gigih): don't put in temporary folder
        myShapePath = '/tmp/' + myId + '.shp.zip'
        myShapeFile = open(myShapePath, 'wb')
        myShapeFile.write(myShapeResponse.content)
        myShapeFile.close()

        print "extract file...."
        self.extractZip(myShapePath)

        ## FIXME(gigih): add shape file layer to qgis

        print "file already extracted in /tmp...."



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
#    a.show()
#    app.exec_()
    a.createNewJob()
