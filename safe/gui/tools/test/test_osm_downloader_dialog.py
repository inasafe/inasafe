# coding=utf-8

"""Tests for OSM downloader dialog."""

# noinspection PyUnresolvedReferences
import unittest
import logging
import os
import tempfile
import shutil

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import

from safe.gui.tools.osm_downloader_dialog import OsmDownloaderDialog
from safe.test.utilities import get_qgis_app

__copyright__ = "Copyright 2013, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
LOGGER = logging.getLogger('InaSAFE')


class OsmDownloaderDialogTest(unittest.TestCase):

    """Test Osm Downloader Dialog widget.

    .. versionchanged:: 3.2
    """

    # noinspection PyPep8Naming
    def setUp(self):
        """Runs before each test."""
        self.dialog = OsmDownloaderDialog(PARENT, IFACE)

    def test_checked_features(self):
        """Test checked features."""
        self.dialog.roads_flag.setChecked(False)
        self.dialog.buildings_flag.setChecked(False)
        self.dialog.building_points_flag.setChecked(False)
        self.dialog.flood_prone_flag.setChecked(False)
        self.dialog.evacuation_centers_flag.setChecked(False)
        self.dialog.boundary_flag.setChecked(False)
        expected = []
        get = self.dialog.get_checked_features()
        self.assertEqual(expected, get)

        self.dialog.roads_flag.setChecked(True)
        self.dialog.buildings_flag.setChecked(True)
        self.dialog.building_points_flag.setChecked(True)
        self.dialog.flood_prone_flag.setChecked(False)
        self.dialog.evacuation_centers_flag.setChecked(True)
        self.dialog.boundary_flag.setChecked(False)
        expected = [
            'roads',
            'buildings',
            'building-points',
            'evacuation-centers']
        get = self.dialog.get_checked_features()
        self.assertEqual(expected, get)

        admin_level = 6
        self.dialog.admin_level_comboBox.setCurrentIndex(admin_level - 1)
        self.dialog.roads_flag.setChecked(False)
        self.dialog.buildings_flag.setChecked(True)
        self.dialog.building_points_flag.setChecked(True)
        self.dialog.flood_prone_flag.setChecked(True)
        self.dialog.evacuation_centers_flag.setChecked(True)
        self.dialog.boundary_flag.setChecked(True)
        expected = [
            'buildings',
            'building-points',
            'flood-prone',
            'evacuation-centers',
            'boundary-6']
        get = self.dialog.get_checked_features()
        self.assertEqual(expected, get)

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

        For instance every admin_level from 1 to 11 and the first and last
        country (alphabetical order).
        """
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
        expected = 'which represents Community Group (Rukun Warga) in'

        self.dialog.admin_level_comboBox.setCurrentIndex(admin_level - 1)
        index = self.dialog.country_comboBox.findText(country)
        self.dialog.country_comboBox.setCurrentIndex(index)
        self.assertEqual(expected, self.dialog.boundary_helper.text())

        admin_level = 6
        country = 'Madagascar'
        expected = 'which represents Distrika (districts) in'

        self.dialog.admin_level_comboBox.setCurrentIndex(admin_level - 1)
        index = self.dialog.country_comboBox.findText(country)
        self.dialog.country_comboBox.setCurrentIndex(index)
        self.assertEqual(expected, self.dialog.boundary_helper.text())

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
        self.assertEqual(result, 2, message)

        os.remove(other_file)
        result = self.dialog.get_unique_file_path_suffix(one_file)
        self.assertEqual(result, 1, message)

        os.remove(one_file)
        result = self.dialog.get_unique_file_path_suffix(one_file)
        self.assertEqual(result, 0, message)

        # cleanup
        shutil.rmtree(path)


if __name__ == '__main__':
    suite = unittest.makeSuite(OsmDownloaderDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
