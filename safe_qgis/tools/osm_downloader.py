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
import logging

#noinspection PyPackageRequirements
from PyQt4 import QtGui
#noinspection PyPackageRequirements
from PyQt4.QtCore import QSettings, pyqtSignature, QRegExp
#noinspection PyPackageRequirements
from PyQt4.QtGui import (
    QDialog, QProgressDialog, QMessageBox, QFileDialog, QRegExpValidator)
#noinspection PyPackageRequirements
from PyQt4.QtNetwork import QNetworkAccessManager

#noinspection PyUnresolvedReferences
#pylint: disable=W0611
from qgis.core import QGis  # force sip2 api
#pylint: enable=W0611
from safe_qgis.ui.osm_downloader_base import Ui_OsmDownloaderBase

from safe_qgis.exceptions import (
    CanceledImportDialogError, ImportDialogError, DownloadError)
from safe_qgis.safe_interface import messaging as m
from safe_qgis.utilities.file_downloader import FileDownloader
from safe_qgis.utilities.utilities import (
    html_footer, html_header, viewport_geo_array)
from safe_qgis.utilities.help import show_context_help
from safe_qgis.safe_interface import styles
from safe_qgis.utilities.proxy import get_proxy

INFO_STYLE = styles.INFO_STYLE
LOGGER = logging.getLogger('InaSAFE')


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
        self.buildings_url = "http://osm.linfiniti.com/buildings-shp"
        self.roads_url = "http://osm.linfiniti.com/roads-shp"

        self.help_context = 'openstreetmap_downloader'
        # creating progress dialog for download
        self.progress_dialog = QProgressDialog(self)
        self.progress_dialog.setAutoClose(False)
        title = self.tr("InaSAFE OpenStreetMap Downloader")
        self.progress_dialog.setWindowTitle(title)
        # Set up context help
        help_button = self.button_box.button(QtGui.QDialogButtonBox.Help)
        help_button.clicked.connect(self.show_help)

        self.show_info()

        # set up the validator for the file name prefix
        expression = QRegExp('^[A-Za-z0-9-_]*$')
        validator = QRegExpValidator(expression, self.filename_prefix)
        self.filename_prefix.setValidator(validator)

        # Set Proxy in webpage
        proxy = get_proxy()
        self.network_manager = QNetworkAccessManager(self)
        if not proxy is None:
            self.network_manager.setProxy(proxy)
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
            'This tool will fetch building (\'structure\') or road ('
            '\'highway\') data from the OpenStreetMap project for you. '
            'The downloaded data will have InaSAFE keywords defined and a '
            'default QGIS style applied. To use this tool effectively:'
        )
        tips = m.BulletedList()
        tips.add(self.tr(
            'Your current extent will be used to determine the area for which '
            'you want data to be retrieved. You can adjust it manually using '
            'the bounding box options below.'))
        tips.add(self.tr(
            'Check the output directory is correct. Note that the saved '
            'dataset will be called either roads.shp or buildings.shp (and '
            'associated files).'
        ))
        tips.add(self.tr(
            'By default simple file names will be used (e.g. roads.shp, '
            'buildings.shp). If you wish you can specify a prefix to '
            'add in front of this default name. For example using a prefix '
            'of \'padang-\' will cause the downloaded files to be saved as '
            '\'padang-roads.shp\' and \'padang-buildings.shp\'. Note that '
            'the only allowed prefix characters are A-Z, a-z, 0-9 and the '
            'characters \'-\' and \'_\'. You can leave this blank if you '
            'prefer.'
        ))
        tips.add(self.tr(
            'If a dataset already exists in the output directory it will be '
            'overwritten.'
        ))
        tips.add(self.tr(
            'This tool requires a working internet connection and fetching '
            'buildings or roads will consume your bandwidth.'))
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

        self.web_view.setHtml(string)

    def restore_state(self):
        """ Read last state of GUI from configuration file."""
        settings = QSettings()
        try:
            last_path = settings.value('directory', type=str)
        except TypeError:
            last_path = ''
        self.output_directory.setText(last_path)

    def save_state(self):
        """ Store current state of GUI to configuration file """
        settings = QSettings()
        settings.setValue('directory', self.output_directory.text())

    def show_help(self):
        """Load the help text for the dialog."""
        show_context_help(self.help_context)

    def update_extent(self):
        """ Update extent value in GUI based from value in map."""
        # Get the extent as [xmin, ymin, xmax, ymax]
        extent = viewport_geo_array(self.iface.mapCanvas())
        self.min_longitude.setText(str(extent[0]))
        self.min_latitude.setText(str(extent[1]))
        self.max_longitude.setText(str(extent[2]))
        self.max_latitude.setText(str(extent[3]))

    def validate_extent(self):
        """Validate the bounding box before user click OK to download.

        :return: True if the bounding box is valid, otherwise False
        :rtype: bool
        """
        min_latitude = float(str(self.min_latitude.text()))
        max_latitude = float(str(self.max_latitude.text()))
        min_longitude = float(str(self.min_longitude.text()))
        max_longitude = float(str(self.max_longitude.text()))

        # min_latitude < max_latitude
        if min_latitude >= max_latitude:
            return False

        # min_longitude < max_longitude
        if min_longitude >= max_longitude:
            return False

        # -90 <= latitude <= 90
        if min_latitude < -90 or min_latitude > 90:
            return False
        if max_latitude < -90 or max_latitude > 90:
            return False

        # -180 <= longitude <= 180
        if min_longitude < -180 or min_longitude > 180:
            return False
        if max_longitude < -180 or max_longitude > 180:
            return False

        return True

    @pyqtSignature('')  # prevents actions being handled twice
    def on_directory_button_clicked(self):
        """ Show a dialog to choose directory """
        # noinspection PyCallByClass,PyTypeChecker
        self.output_directory.setText(QFileDialog.getExistingDirectory(
            self, self.tr("Select download directory")))

    def accept(self):
        """Do osm download and display it in QGIS."""
        error_dialog_title = self.tr('InaSAFE OpenStreetMap Downloader Error')

        # Validate extent
        valid_flag = self.validate_extent()
        if not valid_flag:
            message = self.tr(
                'The bounding box is not valid. Please make sure it is '
                'valid or check your projection!')
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QMessageBox.warning(self, error_dialog_title, message)
            return

        # Get all the feature types
        index = self.feature_type.currentIndex()
        if index == 0:
            feature_types = ['buildings', 'roads']
        elif index == 1:
            feature_types = ['buildings']
        else:
            feature_types = ['roads']

        try:
            self.save_state()
            self.require_directory()
            for feature_type in feature_types:
                self.download(feature_type)
                self.load_shapefile(feature_type)
            self.done(QDialog.Accepted)
        except CanceledImportDialogError:
            # don't show anything because this exception raised
            # when user canceling the import process directly
            pass
        except Exception as exception:
            # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
            QMessageBox.warning(self, error_dialog_title, str(exception))

            self.progress_dialog.cancel()

    def require_directory(self):
        """Ensure directory path entered in dialog exist.

        When the path does not exist, this function will ask the user if he
        want to create it or not.

        :raises: CanceledImportDialogError - when user choose 'No' in
            the question dialog for creating directory.
        """
        path = str(self.output_directory.text())

        if os.path.exists(path):
            return

        title = self.tr("Directory %s not exist") % path
        question = self.tr(
            "Directory %s not exist. Do you want to create it?") % path
        # noinspection PyCallByClass,PyTypeChecker
        answer = QMessageBox.question(
            self, title, question, QMessageBox.Yes | QMessageBox.No)

        if answer == QMessageBox.Yes:
            if len(path) != 0:
                os.makedirs(path)
            else:
            # noinspection PyCallByClass,PyTypeChecker, PyArgumentList
                QMessageBox.warning(
                    self,
                    self.tr('InaSAFE error'),
                    self.tr('Output directory can not be empty.'))
                raise CanceledImportDialogError()
        else:
            raise CanceledImportDialogError()

    def download(self, feature_type):
        """Download shapefiles from Linfiniti server.

        :param feature_type: What kind of features should be downloaded.
            Currently 'buildings' or 'roads' are supported.
        :type feature_type: str

        :raises: ImportDialogError, CanceledImportDialogError
        """

        ## preparing necessary data
        min_longitude = str(self.min_longitude.text())
        min_latitude = str(self.min_latitude.text())
        max_longitude = str(self.max_longitude.text())
        max_latitude = str(self.max_latitude.text())

        box = (
            '{min_longitude},{min_latitude},{max_longitude},'
            '{max_latitude}').format(
                min_longitude=min_longitude,
                min_latitude=min_latitude,
                max_longitude=max_longitude,
                max_latitude=max_latitude
            )
        output_prefix = self.filename_prefix.text()
        if feature_type == 'buildings':
            url = "{url}?bbox={box}&qgis_version=2".format(
                url=self.buildings_url, box=box)
        else:
            url = "{url}?bbox={box}&qgis_version=2".format(
                url=self.roads_url, box=box)

        if output_prefix is not None:
            url += '&output_prefix=%s' % output_prefix

        path = tempfile.mktemp('.shp.zip')

        # download and extract it
        self.fetch_zip(url, path)
        self.extract_zip(path, str(self.output_directory.text()))

        self.progress_dialog.done(QDialog.Accepted)

    def fetch_zip(self, url, output_path):
        """Download zip containing shp file and write to output_path.

        :param url: URL of the zip bundle.
        :type url: str

        :param output_path: Path of output file,
        :type output_path: str

        :raises: ImportDialogError - when network error occurred
        """
        LOGGER.debug('Downloading file from URL: %s' % url)
        LOGGER.debug('Downloading to: %s' % output_path)

        self.progress_dialog.show()
        self.progress_dialog.setMaximum(100)
        self.progress_dialog.setValue(0)

        label_text = self.tr("Downloading shapefile")
        self.progress_dialog.setLabelText(label_text)

        # Download Process
        downloader = FileDownloader(
            self.network_manager, url, output_path, self.progress_dialog)
        try:
            result = downloader.download()
        except IOError as ex:
            raise IOError(ex)

        if result[0] is not True:
            _, error_message = result
            raise DownloadError(error_message)

    @staticmethod
    def extract_zip(path, output_dir):
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
        handle = open(path, 'rb')
        zip_file = zipfile.ZipFile(handle)
        for name in zip_file.namelist():
            output_path = os.path.join(output_dir, name)
            output_file = open(output_path, 'wb')
            output_file.write(zip_file.read(name))
            output_file.close()

        handle.close()

    def load_shapefile(self, feature_type):
        """Load downloaded shape file to QGIS Main Window.

        :param feature_type: What kind of features should be downloaded.
            Currently 'buildings' or 'roads' are supported.
        :type feature_type: str

        :raises: ImportDialogError - when buildings.shp not exist
        """
        output_prefix = self.filename_prefix.text()
        path = str(self.output_directory.text())
        path = os.path.join(path, '%s%s.shp' % (output_prefix, feature_type))

        if not os.path.exists(path):
            message = self.tr(
                "%s don't exist. The server doesn't have any data.")
            raise ImportDialogError(message)

        self.iface.addVectorLayer(path, feature_type, 'ogr')
