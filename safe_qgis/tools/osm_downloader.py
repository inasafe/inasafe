# coding=utf-8
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

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QSettings, pyqtSignature
from PyQt4.QtGui import QDialog, QProgressDialog, QMessageBox, QFileDialog
from PyQt4.QtNetwork import QNetworkAccessManager
from safe_qgis.ui.osm_downloader_base import Ui_OsmDownloaderBase

from safe_qgis.exceptions import CanceledImportDialogError, ImportDialogError
from safe_qgis.safe_interface import messaging as m
from safe_qgis.utilities.utilities import (
    download_url, html_footer, html_header)
from safe_qgis.utilities.help import show_context_help
from safe_qgis.safe_interface import styles

INFO_STYLE = styles.INFO_STYLE


class OsmDownloader(QDialog, Ui_OsmDownloaderBase):
    """Downloader for OSM data."""

    def __init__(self, parent=None, iface=None):
        """Constructor for import dialog.

        :param parent: Optional widget to use as parent
        :type parent: QWidget

        :param iface: An instance of QGisInterface
        :type iface: QGisInterface
        """
        QDialog.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)

        self.setWindowTitle(self.tr('InaSAFE OpenStreetMap Downloader'))

        self.iface = iface
        self.url = "http://osm.linfiniti.com/buildings-shp"

        # creating progress dialog for download
        self.progressDialog = QProgressDialog(self)
        self.progressDialog.setAutoClose(False)
        myTitle = self.tr("InaSAFE OpenStreetMap Downloader")
        self.progressDialog.setWindowTitle(myTitle)
        # Set up context help
        helpButton = self.buttonBox.button(QtGui.QDialogButtonBox.Help)
        QtCore.QObject.connect(helpButton, QtCore.SIGNAL('clicked()'),
                               self.show_help)

        self.show_info()

        self.network_manager = QNetworkAccessManager(self)
        self.restore_state()
        self.update_extent()

    def show_info(self):
        """Show usage info to the user."""
        # Read the header and footer html snippets
        header = html_header()
        footer = html_footer()

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

    def restore_state(self):
        """ Read last state of GUI from configuration file."""
        mySetting = QSettings()
        self.outDir.setText(mySetting.value('directory'))

    def save_state(self):
        """ Store current state of GUI to configuration file """
        mySetting = QSettings()
        mySetting.setValue('directory', self.outDir.text())

    def show_help(self):
        """Load the help text for the dialog."""
        show_context_help('openstreetmap_downloader')

    def update_extent(self):
        """ Update extent value in GUI based from value in map."""
        myExtent = self.iface.mapCanvas().extent()
        self.minLongitude.setText(str(myExtent.xMinimum()))
        self.minLatitude.setText(str(myExtent.yMinimum()))
        self.maxLongitude.setText(str(myExtent.xMaximum()))
        self.maxLatitude.setText(str(myExtent.yMaximum()))

    @pyqtSignature('')  # prevents actions being handled twice
    def on_pBtnDir_clicked(self):
        """ Show a dialog to choose directory """
        # noinspection PyCallByClass,PyTypeChecker
        self.outDir.setText(QFileDialog.getExistingDirectory(
            self, self.tr("Select download directory")))

    def accept(self):
        """Do osm download and display it in QGIS."""

        try:
            self.save_state()

            self.require_directory()
            self.download()
            self.load_shapefile()
            self.done(QDialog.Accepted)
        except CanceledImportDialogError:
            # don't show anything because this exception raised
            # when user canceling the import process directly
            pass
        except Exception as myEx:
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QMessageBox.warning(
                self,
                self.tr("InaSAFE OpenStreetMap downloader error"),
                str(myEx))

            self.progressDialog.cancel()

    def require_directory(self):
        """Ensure directory path entered in dialog exist.

        When the path does not exist, this function will ask the user if he
        want to create it or not.

        :raises: CanceledImportDialogError - when user choose 'No' in
            the question dialog for creating directory.
        """

        myDir = str(self.outDir.text())

        if os.path.exists(myDir):
            return

        myTitle = self.tr("Directory %s not exist") % myDir
        myQuestion = self.tr(
            "Directory %s not exist. Do you want to create it?"
        ) % myDir
        # noinspection PyCallByClass,PyTypeChecker
        myAnswer = QMessageBox.question(
            self, myTitle,
            myQuestion, QMessageBox.Yes | QMessageBox.No)

        if myAnswer == QMessageBox.Yes:
            os.makedirs(myDir)
        else:
            raise CanceledImportDialogError()

    def download(self):
        """Download shapefiles from Linfinti server.

        :raises: ImportDialogError, CanceledImportDialogError
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
        self.fetch_zip(myShapeUrl, myFilePath)
        print myFilePath
        print str(self.outDir.text())
        self.extract_zip(myFilePath, str(self.outDir.text()))

        self.progressDialog.done(QDialog.Accepted)

    def fetch_zip(self, url, output_path):
        """Download zip containing shp file and write to output_path.

        :param url: URL of the zip bundle.
        :type url: str

        :param output_path: Path of output file,
        :type output_path: str

        :raises: ImportDialogError - when network error occurred
        """

        self.progressDialog.show()
        self.progressDialog.setMaximum(100)
        self.progressDialog.setValue(0)

        # myLabelText = "Begin downloading shapefile from " \
        #               + "%s ..."
        # self.progressDialog.setLabelText(self.tr(myLabelText) % (url))
        myLabelText = self.tr("Downloading shapefile")
        self.progressDialog.setLabelText(myLabelText)

        myResult = download_url(
            self.network_manager, url, output_path,
            self.progressDialog)

        if myResult is not True:
            _, myErrorMessage = myResult
            raise ImportDialogError(myErrorMessage)

    def extract_zip(self, path, output_dir):
        """Extract all content of a .zip file from path to output_dir.

        :param path: The path of the .zip file
        :type path: str

        :param output_dir: Output directory where the shp will be written to.
        :type output_dir: str

        :raises: IOError - when not able to open path or output_dir does not
            exist.
        """

        import zipfile

        # extract all files...
        myHandle = open(path, 'rb')
        myZip = zipfile.ZipFile(myHandle)
        for myName in myZip.namelist():
            myOutPath = os.path.join(output_dir, myName)
            myOutFile = open(myOutPath, 'wb')
            myOutFile.write(myZip.read(myName))
            myOutFile.close()

        myHandle.close()

    def load_shapefile(self):
        """
        Load downloaded shape file to QGIS Main Window.

        :raises: ImportDialogError - when buildings.shp not exist
        """

        myDir = str(self.outDir.text())
        myPath = os.path.join(myDir, 'buildings.shp')

        if not os.path.exists(myPath):
            myMessage = self.tr(
                "%s don't exist. The server don't have buildings data."
            )
            raise ImportDialogError(myMessage)

        self.iface.addVectorLayer(myPath, 'buildings', 'ogr')
