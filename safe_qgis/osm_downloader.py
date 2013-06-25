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

import os
import tempfile

from PyQt4.QtCore import QSettings, pyqtSignature
from PyQt4.QtGui import (QDialog, QProgressDialog, QMessageBox, QFileDialog)
from PyQt4.QtNetwork import QNetworkAccessManager
from osm_downloader_base import Ui_OsmDownloaderBase

from safe_qgis.exceptions import (CanceledImportDialogError, ImportDialogError)
from safe_interface import messaging as m
from utilities import downloadWebUrl
from safe_interface import styles
INFO_STYLE = styles.INFO_STYLE


class OsmDownloader(QDialog, Ui_OsmDownloaderBase):

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

        # creating progress dialog for download
        self.progressDialog = QProgressDialog(self)
        self.progressDialog.setAutoClose(False)
        myTitle = self.tr("InaSAFE OpenStreetMap Downloader")
        self.progressDialog.setWindowTitle(myTitle)

        self.showInfo()

        self.nam = QNetworkAccessManager(self)
        self.restoreState()
        self.updateExtent()

    def showInfo(self):
        # Read the header and footer html snippets
        base_dir = os.path.dirname(__file__)
        header_path = os.path.join(base_dir, 'resources', 'header.html')
        footer_path = os.path.join(base_dir, 'resources', 'footer.html')
        header_file = file(header_path, 'rt')
        footer_file = file(footer_path, 'rt')
        header = header_file.read()
        footer = footer_file.read()
        header_file.close()
        footer_file.close()
        header = header.replace('PATH', base_dir)

        string = header

        heading = m.Heading(self.tr('OSM Downloader'), **INFO_STYLE)
        body = self.tr(
            'This tool will fetch building (\'structure\') data from the '
            'OpenStreetMap project for you. The downloaded data will have '
            'InaSAFE keywords defined and a default QGIS style applied. To '
            'use this tool effectively:'
        )
        tips = m.BulletedList()
        tips.add(self.tr(
            'Use QGIS to zoom in to the area for which you want building data '
            'to be retrieved.'))
        tips.add(self.tr(
            'Check the output directory is correct. Note that the saved '
            'dataset will be called buildings.shp (and its associated files).'
        ))
        tips.add(self.tr(
            'If a dataset already exists in the output directory it will be '
            'overwritten.'
        ))
        tips.add(self.tr(
            'This tool requires a working internet connection and fetching '
            'buildings will consume your bandwidth.'))
        tips.add(m.Link(
            'http://www.openstreetmap.org/copyright',
            text=self.tr(
                'Downloaded data is copyright OpenStreetMap contributors'
                ' (click for more info).')
        ))
        message = m.Message()
        message.add(heading)
        message.add(body)
        message.add(tips)
        string += message.to_html()
        string += footer

        self.webView.setHtml(string)

    def restoreState(self):
        """ Read last state of GUI from configuration file."""
        mySetting = QSettings()
        self.outDir.setText(mySetting.value('directory').toString())

    def saveState(self):
        """ Store current state of GUI to configuration file """
        mySetting = QSettings()
        mySetting.setValue('directory', self.outDir.text())

    def updateExtent(self):
        """ Update extent value in GUI based from value in map."""
        myExtent = self.iface.mapCanvas().extent()
        self.minLongitude.setText(str(myExtent.xMinimum()))
        self.minLatitude.setText(str(myExtent.yMinimum()))
        self.maxLongitude.setText(str(myExtent.xMaximum()))
        self.maxLatitude.setText(str(myExtent.yMaximum()))

    @pyqtSignature('')  # prevents actions being handled twice
    def on_pBtnDir_clicked(self):
        """ Show a dialog to choose directory """
        self.outDir.setText(QFileDialog.getExistingDirectory(
            self, self.tr("Select download directory")))

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
                self.tr("InaSAFE OpenStreetMap downloader error"),
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

        myCoordinate = "{myMinLng},{myMinLat},{myMaxLng},{myMaxLat}".format(
            myMinLng=myMinLng,
            myMinLat=myMinLat,
            myMaxLng=myMaxLng,
            myMaxLat=myMaxLat
        )

        myShapeUrl = "{url}?bbox={myCoordinate}".format(
            url=self.url,
            myCoordinate=myCoordinate
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
        myLabelText = self.tr("Downloading shapefile")
        self.progressDialog.setLabelText(myLabelText)

        myResult = downloadWebUrl(self.nam, theUrl, theOutput,
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
