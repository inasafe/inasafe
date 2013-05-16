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

from PyQt4.QtCore import (QCoreApplication, QUrl, QFile,
                          QSettings, pyqtSignature)
from PyQt4.QtGui import (QDialog, QProgressDialog,
                         QMessageBox, QFileDialog)
from PyQt4.QtNetwork import (QNetworkAccessManager, QNetworkRequest,
                             QNetworkReply)
from import_dialog_base import Ui_ImportDialogBase

import os
import tempfile

from inasafe_lightmaps import InasafeLightMaps
from safe_qgis.exceptions import (CanceledImportDialogError, ImportDialogError)


def httpDownload(theManager, theUrl, theOutPath, theProgressDlg=None):
    """ Download file from theUrl.
    Params:
        * theManager - a QNetworkManager instance
        * theUrl - url of file
        * theOutPath - output path
        * theProgressDlg - progress dialog widget
    Returns:
        True if success, otherwise return a tuple with format like this
        (QNetworkReply.NetworkError, error_message)
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

    if theProgressDlg:
        # progress bar
        def progressEvent(theReceived, theTotal):

            QCoreApplication.processEvents()

            theProgressDlg.setLabelText("%s / %s" % (theReceived, theTotal))
            theProgressDlg.setMaximum(theTotal)
            theProgressDlg.setValue(theReceived)

        # cancel
        def cancelAction():
            myReply.abort()

        myReply.downloadProgress.connect(progressEvent)
        theProgressDlg.canceled.connect(cancelAction)

    # wait until finished
    while not myReply.isFinished():
        QCoreApplication.processEvents()

    myFile.close()

    myResult = myReply.error()
    if myResult == QNetworkReply.NoError:
        return True
    else:
        return (myResult, str(myReply.errorString()))


class ImportDialog(QDialog, Ui_ImportDialogBase):

    def __init__(self, theParent=None, theIface=None):
        """Constructor for import dialog.

        Args:
           * theParent - Optional widget to use as parent
           * theIface - an instance of QGisInterface
        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """
        QDialog.__init__(self, theParent)
        self.parent = theParent
        self.setupUi(self)

        self.setWindowTitle(self.tr('InaSAFE OpenStreetMap Downloader'))

        self.iface = theIface
        self.url = "http://osm.linfiniti.com/buildings-shp"

        ## region coordinate: (latitude, longtitude, zoom_level)
        self.regionExtent = {
            '0': [18.87685, -71.493, 6],     # haiti
            '1': [-2.5436300, 116.8887, 3],  # indonesia
            '2': [1.22449, 15.40999, 2],     # africa
            '3': [34.05, 56.55, 3],          # middle east
            '4': [12.98855, 121.7166, 4],    # philipine
        }

        # creating progress dialog for download
        self.progressDialog = QProgressDialog(self)
        self.progressDialog.setAutoClose(False)
        myTitle = self.tr("InaSAFE OpenStreetMap Downloader")
        self.progressDialog.setWindowTitle(myTitle)

        ## set map parameter based on placeholder self.map widget
        theMap = InasafeLightMaps(self.gbxMap)
        theMap.setGeometry(self.map.geometry())
        theMap.setSizePolicy(self.map.sizePolicy())
        self.map = theMap

        self.nam = QNetworkAccessManager(self)

        self.setupOptions()

        self.restoreState()

        self.cbxRegion.currentIndexChanged.connect(self.regionChanged)
        self.map.m_normalMap.updated.connect(self.updateExtent)

    def regionChanged(self, theIndex):
        """ Slot that called when region combo box changed.
        Params:
            theIndex - index of combo box
        """
        myRegionIndex = str(self.cbxRegion.itemData(theIndex).toString())
        myCenter = self.regionExtent[myRegionIndex]
        self.map.setCenter(myCenter[0], myCenter[1], myCenter[2])

    # pylint: disable=W0613
    def resizeEvent(self, theEvent):
        """ Function that called when resize event occurred.
        Params:
            theEvent - QEvent instance. Not used.
        """
        self.map.resize(self.gbxMap.width() - 30, self.gbxMap.height() - 30)
    # pylint: disable=W0613

    def setupOptions(self):
        """ Set the content of combo box for region and preset """
        self.cbxRegion.insertItem(0, 'Indonesia', 1)
        self.cbxRegion.insertItem(1, 'Africa', 2)
        self.cbxRegion.insertItem(2, 'Philippines', 4)
        self.cbxRegion.insertItem(3, 'Central Asia/Middle East', 3)
        self.cbxRegion.insertItem(4, 'Haiti', 0)

        self.cbxPreset.insertItem(0, self.tr('Buildings'), 'building')
        self.cbxPreset.insertItem(0, self.tr('Highway'), 'highway')

    def restoreState(self):
        """ Read last state of GUI from configuration file """
        mySetting = QSettings()

        myRegion = mySetting.value('region').toInt()
        if myRegion[1] is True:
            self.cbxRegion.setCurrentIndex(myRegion[0])

        myPreset = mySetting.value('preset').toInt()
        if myPreset[1] is True:
            self.cbxPreset.setCurrentIndex(myPreset[0])

        self.outDir.setText(mySetting.value('directory').toString())

        myZoomLevel = mySetting.value('zoom_level').toInt()
        myLatitude = mySetting.value('latitude').toDouble()
        myLongitude = mySetting.value('longitude').toDouble()

        if myZoomLevel[1] is True:
            self.map.setCenter(myLatitude[0], myLongitude[0], myZoomLevel[0])
        else:
            # just set to indonesia extent
            myCenter = self.regionExtent['1']
            self.map.setCenter(myCenter[0], myCenter[1], myCenter[2])

    def saveState(self):
        """ Store current state of GUI to configuration file """
        mySetting = QSettings()
        mySetting.setValue('region', self.cbxRegion.currentIndex())
        mySetting.setValue('preset', self.cbxPreset.currentIndex())
        mySetting.setValue('directory', self.outDir.text())

        mySetting.setValue('zoom_level', self.map.getZoomLevel())
        myCenter = self.map.getCenter()
        mySetting.setValue('latitude', myCenter[0])
        mySetting.setValue('longitude', myCenter[1])

    def updateExtent(self):
        """ Update extent value in GUI based from value in map widget"""
        myExtent = self.map.getExtent()
        self.minLongitude.setText(str(myExtent[1]))
        self.minLatitude.setText(str(myExtent[0]))
        self.maxLongitude.setText(str(myExtent[3]))
        self.maxLatitude.setText(str(myExtent[2]))

    @pyqtSignature('')  # prevents actions being handled twice
    def on_pBtnDir_clicked(self):
        """ Show a dialog to choose directory """
        self.outDir.setText(QFileDialog.getExistingDirectory(
            self, self.tr("Select Directory")))

    def accept(self):
        """ Do import process """

        try:
            self.saveState()

            self.ensureDirExist()
            self.doImport()
            self.loadShapeFile()
            self.done(QDialog.Accepted)
        except CanceledImportDialogError:
            # don't show anything because this exception raised
            # when user canceling the import process directly
            pass
        except Exception as myEx:
            QMessageBox.warning(
                self,
                self.tr("InaSAFE OpenStreetMap Downloader Error"),
                str(myEx))

            self.progressDialog.cancel()

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
        Import shape files from Linfinti.
        Raises:
            * ImportDialogError - when network error occurred
            * CanceledImportDialogError - when user press cancel button
        """

        ## preparing necessary data
        myMinLng = str(self.minLongitude.text())
        myMinLat = str(self.minLatitude.text())
        myMaxLng = str(self.maxLongitude.text())
        myMaxLat = str(self.maxLatitude.text())

        myCurrentIndex = self.cbxPreset.currentIndex()
        myType = str(self.cbxPreset.itemData(myCurrentIndex).toString())

        myCoordinate = "{myMinLng},{myMinLat},{myMaxLng},{myMaxLat}".format(
            myMinLng=myMinLng,
            myMinLat=myMinLat,
            myMaxLng=myMaxLng,
            myMaxLat=myMaxLat
        )

        myShapeUrl = "{url}?bbox={myCoordinate}&obj={type}".format(
            url=self.url,
            myCoordinate=myCoordinate,
            type=myType
        )

        myFilePath = tempfile.mktemp('.shp.zip')

        # download and extract it
        self.downloadShapeFile(myShapeUrl, myFilePath)
        self.extractZip(myFilePath, str(self.outDir.text()))

        self.progressDialog.done(QDialog.Accepted)

    def downloadShapeFile(self, theUrl, theOutput):
        """
        Download shape file from theUrl and write to theOutput.
        Params:
            * theUrl - URL of shape file
            * theOutput - path of output file
        Raises:
            * ImportDialogError - when network error occurred
        """

        self.progressDialog.show()
        self.progressDialog.setMaximum(100)
        self.progressDialog.setValue(0)

        # myLabelText = "Begin downloading shapefile from " \
        #               + "%1 ..."
        # self.progressDialog.setLabelText(self.tr(myLabelText).arg(theUrl))
        myLabelText = self.tr("Begin downloading shapefile")
        self.progressDialog.setLabelText(myLabelText)

        myResult = httpDownload(self.nam, theUrl, theOutput,
                                self.progressDialog)

        if myResult is not True:
            _, myErrorMessage = myResult
            raise ImportDialogError(myErrorMessage)

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

        Raises:
            ImportDialogError - when buildings.shp not exist
        """

        myDir = str(self.outDir.text())
        myPath = os.path.join(myDir, 'buildings.shp')

        if not os.path.exists(myPath):
            myMessage = self.tr(
                "%s don't exist. The server don't have buildings data."
            )
            raise ImportDialogError(myMessage)

        self.iface.addVectorLayer(myPath, 'buildings', 'ogr')


if __name__ == '__main__':
    import sys
    from PyQt4.QtGui import (QApplication)

    app = QApplication(sys.argv)

    a = ImportDialog()
    a.show()
    app.exec_()
    #a.doImport()
