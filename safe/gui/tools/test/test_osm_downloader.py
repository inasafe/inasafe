# coding=utf-8
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

# this import required to enable PyQt API v2 - DO NOT REMOVE!
# noinspection PyUnresolvedReferences
import unittest
import logging
import os
import tempfile
import shutil

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
# noinspection PyPackageRequirements
from PyQt4.QtCore import QUrl, QObject, pyqtSignal, QVariant, QByteArray
# noinspection PyPackageRequirements
from PyQt4.QtGui import QDialog
# noinspection PyPackageRequirements
from PyQt4.QtNetwork import QNetworkReply

from safe.gui.tools.osm_downloader_dialog import OsmDownloaderDialog
from safe.test.utilities import test_data_path, get_qgis_app
from safe.common.version import get_version

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
LOGGER = logging.getLogger('InaSAFE')


class MockQNetworkReply(QObject):
    """A mock network reply for testing.

    :param parent:
    :type parent:
    """
    readyRead = pyqtSignal()
    finished = pyqtSignal()
    downloadProgress = pyqtSignal('qint64', 'qint64')

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.progress = 0
        self.content = ""
        self._url = ""

    # noinspection PyDocstring,PyPep8Naming
    def isFinished(self):
        """ simulate download progress """
        self.progress += 1
        # noinspection PyUnresolvedReferences
        self.readyRead.emit()
        # noinspection PyUnresolvedReferences
        self.downloadProgress.emit(self.progress, 4)
        if self.progress >= 4:
            # noinspection PyUnresolvedReferences
            self.finished.emit()
            return True
        else:
            return False

    # noinspection PyDocstring,PyPep8Naming
    def readAll(self):
        content = self.content
        self.content = ""
        return content

    # noinspection PyDocstring,PyPep8Naming
    def read(self, size):
        content = self.content
        self.content = ""
        # content = string while the input parameter size in QByteArray
        data = QByteArray(content)
        data.chop(data.size() - size)
        return str(data)

    # noinspection PyDocstring,PyPep8Naming
    def url(self):
        return QUrl(self._url)

    # noinspection PyDocstring,PyPep8Naming,PyMethodMayBeStatic
    def error(self):
        return QNetworkReply.NoError

    # noinspection PyDocstring,PyPep8Naming,PyMethodMayBeStatic
    def size(self):
        data = QByteArray(self.content)
        return data.size()

    # noinspection PyDocstring,PyPep8Naming,PyMethodMayBeStatic
    # pylint: disable=W0613
    def attribute(self):
        return QVariant()
        # pylint: enable=W0613


# noinspection PyClassHasNoInit
class FakeQNetworkAccessManager:
    """Mock network manager for testing."""
    # noinspection PyDocstring,PyPep8Naming,PyMethodMayBeStatic
    # pylint: disable=W0613
    def post(self, request_url, data=None):
        """Mock handler for post requests.
        :param request_url: Requested url.
        :param data: Payload data (ignored).
        """
        _ = data  # ignored
        return self.request(request_url)

    # pylint: enable=W0613

    # noinspection PyDocstring,PyPep8Naming,PyMethodMayBeStatic
    def get(self, request_url):
        """Mock handler for a get request.
        :param request_url: Url being requested.
        """
        return self.request(request_url)

    # noinspection PyDocstring,PyPep8Naming,PyMethodMayBeStatic
    def request(self, request_url):
        """Mock handler for an http request.
        :param request_url: Url being requested.
        """
        url = str(request_url.url().toString())
        reply = MockQNetworkReply()

        version = get_version()
        
        if url == 'http://hot-export.geofabrik.de/newjob':
            reply.content = read_all('test-importdlg-newjob.html')
        elif url == 'http://hot-export.geofabrik.de/wizard_area':
            reply.content = read_all('test-importdlg-wizardarea.html')
        elif url == 'http://hot-export.geofabrik.de/tagupload':
            reply.content = read_all('test-importdlg-job.html')
            reply._url = 'http://hot-export.geofabrik.de/jobs/1990'
        elif url == 'http://hot-export.geofabrik.de/jobs/1990':
            reply.content = read_all('test-importdlg-job.html')
        elif url == ('http://osm.linfiniti.com/buildings-shp?'
                     'bbox=20.389938354492188,-34.10782492987083'
                     ',20.712661743164062,'
                     '-34.008273470938335&qgis_version=2'
                     '&inasafe_version=%s'
                     '&lang=en' % version):
            reply.content = read_all("test-importdlg-extractzip.zip")

        return reply


def read_all(path):
    """ Helper function to load all content of path in
        safe/test/data/control/files folder.

    :param path: File name to read in.
    :type path: str

    :returns: The file contents.
    :rtype: str
    """
    control_files_dir = test_data_path('control', 'files')
    path = os.path.join(control_files_dir, path)
    handle = open(path, 'r')
    content = handle.read()
    handle.close()
    return content


class ImportDialogTest(unittest.TestCase):
    """Test Import Dialog widget
    """
    # noinspection PyPep8Naming
    def setUp(self):
        """Runs before each test."""
        self.dialog = OsmDownloaderDialog(PARENT, IFACE)

        # provide Fake QNetworkAccessManager for self.network_manager
        self.dialog.network_manager = FakeQNetworkAccessManager()

    def test_checked_features(self):
        """Test checked features"""
        self.dialog.roads_checkBox.setChecked(False)
        self.dialog.buildings_checkBox.setChecked(False)
        self.dialog.building_points_checkBox.setChecked(False)
        self.dialog.potential_idp_checkBox.setChecked(False)
        self.dialog.boundary_checkBox.setChecked(False)
        expected = []
        get = self.dialog.get_checked_features()
        self.assertItemsEqual(expected, get)

        self.dialog.roads_checkBox.setChecked(True)
        self.dialog.buildings_checkBox.setChecked(True)
        self.dialog.building_points_checkBox.setChecked(True)
        self.dialog.potential_idp_checkBox.setChecked(True)
        self.dialog.boundary_checkBox.setChecked(False)
        expected = ['roads', 'buildings', 'building-points', 'potential-idp']
        get = self.dialog.get_checked_features()
        self.assertItemsEqual(expected, get)

        admin_level = 6
        self.dialog.admin_level_comboBox.setCurrentIndex(admin_level - 1)
        self.dialog.roads_checkBox.setChecked(False)
        self.dialog.buildings_checkBox.setChecked(True)
        self.dialog.building_points_checkBox.setChecked(True)
        self.dialog.potential_idp_checkBox.setChecked(True)
        self.dialog.boundary_checkBox.setChecked(True)
        expected = [
            'buildings', 'building-points', 'potential-idp', 'boundary-6']
        get = self.dialog.get_checked_features()
        self.assertItemsEqual(expected, get)

    def test_detect_country(self):
        """Test if the country is well detected according to the extent."""
        # Extent in Zimbabwe.
        self.dialog.update_extent([29.4239, -18.2391, 29.4676, -18.2068])
        index = self.dialog.country_comboBox.currentIndex()
        country = self.dialog.country_comboBox.itemText(index)
        self.assertTrue(country == 'Zimbabwe')

        # Extent in Indonesia.
        self.dialog.update_extent([106.7741, -6.2609, 106.8874, -6.1859])
        index = self.dialog.country_comboBox.currentIndex()
        country = self.dialog.country_comboBox.itemText(index)
        self.assertTrue(country == 'Indonesia')

        # Extent in the middle of nowhere in the Indian Ocean, default value.
        self.dialog.update_extent([75.0586, -31.7477, 75.8867, -30.9022])
        index = self.dialog.country_comboBox.currentIndex()
        country = self.dialog.country_comboBox.itemText(index)
        self.assertTrue(country == 'Afghanistan')

    def test_populate_countries(self):
        """Test if items are in the combobox.
        For instance every admin_level from 1 to 11 and
        the first and last country (alphabetical order)."""
        self.assertTrue(self.dialog.admin_level_comboBox.count() == 11)
        self.assertTrue(
            self.dialog.country_comboBox.itemText(0) == 'Afghanistan')
        nb_items = self.dialog.country_comboBox.count()
        self.assertTrue(
            self.dialog.country_comboBox.itemText(nb_items - 1) == 'Zimbabwe')

    def test_admin_level_helper(self):
        """Test the helper by setting a country and an admin level."""
        admin_level = 8
        country = 'Indonesia'
        expected = \
            '<span style=" font-size:12pt; font-style:italic;">' \
            'level 8 is : Community Group (Rukun Warga)</span>'

        self.dialog.admin_level_comboBox.setCurrentIndex(admin_level - 1)
        index = self.dialog.country_comboBox.findText(country)
        self.dialog.country_comboBox.setCurrentIndex(index)
        self.assertEquals(expected, self.dialog.boundary_helper.text())

        admin_level = 6
        country = 'Madagascar'
        expected = \
            '<span style=" font-size:12pt; font-style:italic;">' \
            'level 6 is : Distrika (districts)</span>'

        self.dialog.admin_level_comboBox.setCurrentIndex(admin_level - 1)
        index = self.dialog.country_comboBox.findText(country)
        self.dialog.country_comboBox.setCurrentIndex(index)
        self.assertEquals(expected, self.dialog.boundary_helper.text())

    def test_validate_extent(self):
        """Test validate extent method."""
        # Normal case
        self.dialog.min_longitude.setText('20.389938354492188')
        self.dialog.min_latitude.setText('-34.10782492987083')
        self.dialog.max_longitude.setText('20.712661743164062')
        self.dialog.max_latitude.setText('-34.008273470938335')
        self.assertTrue(self.dialog.validate_extent())

        # min_latitude >= max_latitude
        self.dialog.min_latitude.setText('34.10782492987083')
        self.dialog.max_latitude.setText('-34.008273470938335')
        self.dialog.min_longitude.setText('20.389938354492188')
        self.dialog.max_longitude.setText('20.712661743164062')
        self.assertFalse(self.dialog.validate_extent())

        # min_longitude >= max_longitude
        self.dialog.min_latitude.setText('-34.10782492987083')
        self.dialog.max_latitude.setText('-34.008273470938335')
        self.dialog.min_longitude.setText('34.10782492987083')
        self.dialog.max_longitude.setText('-34.008273470938335')
        self.assertFalse(self.dialog.validate_extent())

        # min_latitude < -90 or > 90
        self.dialog.min_latitude.setText('-134.10782492987083')
        self.dialog.max_latitude.setText('-34.008273470938335')
        self.dialog.min_longitude.setText('20.389938354492188')
        self.dialog.max_longitude.setText('20.712661743164062')
        self.assertFalse(self.dialog.validate_extent())

        # max_latitude < -90 or > 90
        self.dialog.min_latitude.setText('-9.10782492987083')
        self.dialog.max_latitude.setText('91.10782492987083')
        self.dialog.min_longitude.setText('20.389938354492188')
        self.dialog.max_longitude.setText('20.712661743164062')
        self.assertFalse(self.dialog.validate_extent())

        # min_longitude < -180 or > 180
        self.dialog.min_latitude.setText('-34.10782492987083')
        self.dialog.max_latitude.setText('-34.008273470938335')
        self.dialog.min_longitude.setText('-184.10782492987083')
        self.dialog.max_longitude.setText('20.712661743164062')
        self.assertFalse(self.dialog.validate_extent())

        # max_longitude < -180 or > 180
        self.dialog.min_latitude.setText('-34.10782492987083')
        self.dialog.max_latitude.setText('-34.008273470938335')
        self.dialog.min_longitude.setText('20.389938354492188')
        self.dialog.max_longitude.setText('180.712661743164062')
        self.assertFalse(self.dialog.validate_extent())

    def test_fetch_zip(self):
        """Test fetch zip method."""
        feature = 'buildings'
        url = (
            'http://osm.linfiniti.com/buildings-shp?'
            'bbox=20.389938354492188,-34.10782492987083'
            ',20.712661743164062,-34.008273470938335')
        path = tempfile.mktemp('shapefiles')
        self.dialog.fetch_zip(url, path, feature)

        message = "file %s not exist" % path
        assert os.path.exists(path), message

        # cleanup
        os.remove(path)

    def test_suffix_extracting_shapefile(self):
        """Test existing files method."""

        path = tempfile.mkdtemp('existing-files')

        # Create some files
        one_file = os.path.join(path, 'a.txt')
        open(one_file, 'a').close()

        other_file = os.path.join(path, 'a-1.txt')
        open(other_file, 'a').close()

        message = "Index for existing files is wrong."

        result = self.dialog.get_unique_file_path_suffix(one_file)
        assert result == 2, message

        os.remove(other_file)
        result = self.dialog.get_unique_file_path_suffix(one_file)
        assert result == 1, message

        os.remove(one_file)
        result = self.dialog.get_unique_file_path_suffix(one_file)
        assert result == 0, message

        # cleanup
        shutil.rmtree(path)

    def test_extract_zip(self):
        """Test extract_zip method which will only take care of one file for
        each extensions. If many files has the same extension, only the last
        one will be copied.
        """
        base_path = tempfile.mkdtemp()
        base_file_path = os.path.join(base_path, 'test')
        zip_file_path = test_data_path(
            'control',
            'files',
            'test-importdlg-extractzip.zip')
        self.dialog.extract_zip(zip_file_path, base_file_path)

        message = "file {0} not exist"

        path = '%s.shp' % base_file_path
        assert os.path.exists(path), message.format(path)

        # remove temporary folder and all of its content
        shutil.rmtree(base_path)

    def test_download(self):
        """Test download method."""
        output_directory = tempfile.mkdtemp()
        self.dialog.output_directory.setText(output_directory)
        self.dialog.min_longitude.setText('20.389938354492188')
        self.dialog.min_latitude.setText('-34.10782492987083')
        self.dialog.max_longitude.setText('20.712661743164062')
        self.dialog.max_latitude.setText('-34.008273470938335')
        self.dialog.download('buildings', output_directory)

        result = self.dialog.progress_dialog.result()
        message = "result do not match. current result is %s " % result
        assert result == QDialog.Accepted, message

    def test_load_shapefile(self):
        """Test loading shape file to QGIS Main Window """
        zip_file_path = test_data_path(
            'control', 'files', 'test-importdlg-extractzip.zip')
        output_path = tempfile.mkdtemp()

        self.dialog.extract_zip(zip_file_path, output_path)

        self.dialog.load_shapefile('buildings', output_path)

        shutil.rmtree(output_path)


if __name__ == '__main__':
    suite = unittest.makeSuite(ImportDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
