# coding=utf-8
"""
InaSAFE uDisaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'borysjurgiel.pl'
__date__ = '24/02/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
# this import required to enable PyQt API v2 - DO NOT REMOVE!
#noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611

import unittest
import sys
import os
import shutil
# noinspection PyPackageRequirements
# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..///'))
sys.path.append(pardir)

from PyQt4.QtCore import Qt

from qgis.core import QgsVectorLayer

from safe.common.testing import get_qgis_app
from safe_qgis.safe_interface import unique_filename
from safe_qgis.safe_interface import TESTDATA
from safe_qgis.tools.wizard_dialog import WizardDialog
from safe_qgis.utilities.keyword_io import KeywordIO


# Get QGis app handle
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


def clone_csv_layer():
    """Helper function that copies a test csv layer and returns it."""
    path = 'test_buildings.csv'
    temp_path = unique_filename()
    # copy to temp file
    source_path = os.path.join(TESTDATA, path)
    shutil.copy2(source_path, temp_path)
    # return a single predefined layer
    layer = QgsVectorLayer(temp_path, '', 'delimitedtext')
    return layer


def clone_shp_layer(name='tsunami_polygon'):
    """Helper function that copies a test shplayer and returns it."""
    extensions = ['.shp', '.shx', '.dbf', '.prj']
    temp_path = unique_filename()
    # copy to temp file
    for ext in extensions:
        src_path = os.path.join(TESTDATA, name + ext)
        trg_path = temp_path + ext
        shutil.copy2(src_path, trg_path)
    # return a single predefined layer
    layer = QgsVectorLayer(temp_path+'.shp', 'TestLayer', 'ogr')
    return layer


def remove_temp_file(file_path):
    """Helper function that removes temp file created during test.
       Also its keywords file will be removed

    :param file_name: File to remove.
    """
    file_path = file_path[:-4]
    extensions = ['.shp', '.shx', '.dbf', '.prj', '.keywords']
    for ext in extensions:
        if os.path.exists(file_path + ext):
            os.remove(file_path + ext)


class WizardDialogTest(unittest.TestCase):
    """Test the InaSAFE wizard GUI"""

    def test_keywords_creation_wizard(self):
        """Test how the widgets work"""

        expected_category_count = 3
        expected_second_category = "exposure"
        expected_subcategory_count = 4
        expected_second_subcategory = "tsunami"
        expected_unit_count = 3
        expected_third_unit = "feet_depth"
        expected_field_count = 5
        expected_second_field = "GRIDCODE"

        expected_keywords = {
            'category': 'hazard',
            'subcategory': 'tsunami',
            'unit': 'feet_depth',
            'field': 'GRIDCODE',
            'source': 'some source',
            'title': 'some title'
        }

        layer = clone_shp_layer()

        dialog = WizardDialog(PARENT, IFACE, None, layer)

        # step 1 of 7 - select category
        count = dialog.lstCategories.count()
        self.assertTrue(
            count == expected_category_count,
            'Invalid category count! There should be %d while there were: %d'
            % (expected_category_count, count))
        second_category = dialog.lstCategories.item(1).data(Qt.UserRole)
        second_category = eval(second_category)['id']
        self.assertTrue(
            second_category == expected_second_category,
            'Invalid second category! It should be "%s" while it was: "%s"'
            % (expected_second_category, second_category))

        self.assertTrue(
            not dialog.pbnNext.isEnabled(), 'Invalid Next button'
            ' state in step 1! Enabled while there\'s nothing selected yet')
        dialog.lstCategories.setCurrentRow(0)
        self.assertTrue(
            dialog.pbnNext.isEnabled(), 'Invalid Next button'
            'state in step 1! Still disabled after an item selected')

        dialog.pbnNext.click()

        # step 2 of 7 - select hazard
        count = dialog.lstSubcategories.count()
        self.assertTrue(
            count == expected_subcategory_count,
            'Invalid subcategory count! There should be %d and there were: %d'
            % (expected_subcategory_count, count))
        second_subcategory = dialog.lstSubcategories.item(1).data(Qt.UserRole)
        second_subcategory = eval(second_subcategory)['id']
        self.assertTrue(
            second_subcategory == expected_second_subcategory,
            'Invalid second subcategory! It should be "%s" while it was: "%s"'
            % (expected_second_subcategory, second_subcategory))

        self.assertTrue(
            not dialog.pbnNext.isEnabled(), 'Invalid Next button'
            ' state in step 2! Enabled while there\'s nothing selected yet')
        dialog.lstSubcategories.setCurrentRow(1)
        self.assertTrue(
            dialog.pbnNext.isEnabled(), 'Invalid Next button'
            ' state in step 2! Still disabled after an item selected')

        dialog.pbnNext.click()

        # step 3 of 7 - select tsunami units
        count = dialog.lstUnits.count()
        self.assertTrue(
            count == expected_unit_count,
            'Invalid unit count! There should be %d while there were: %d'
            % (expected_unit_count, count))
        third_unit = dialog.lstUnits.item(2).data(Qt.UserRole)
        third_unit = eval(third_unit)['id']
        self.assertTrue(
            third_unit == expected_third_unit,
            'Invalid fourth unit! It should be "%s" while it was: "%s"'
            % (expected_third_unit, third_unit))

        self.assertTrue(
            not dialog.pbnNext.isEnabled(), 'Invalid Next button'
            ' state in step 3! Enabled while there\'s nothing selected yet')
        dialog.lstUnits.setCurrentRow(2)
        self.assertTrue(
            dialog.pbnNext.isEnabled(), 'Invalid Next button'
            ' state in step 3! Still disabled after an item selected')

        dialog.pbnNext.click()

        # step 4 of 7 - select data field for tsunami feet
        count = dialog.lstFields.count()
        self.assertTrue(
            count == expected_field_count,
            'Invalid field count! There should be %d while there were: %d'
            % (expected_field_count, count))
        second_field = dialog.lstFields.item(1).data(Qt.UserRole)
        self.assertTrue(
            second_field == expected_second_field,
            'Invalid second field ! It should be "%s" while it was: "%s"'
            % (expected_second_field, second_field))

        self.assertTrue(
            not dialog.pbnNext.isEnabled(), 'Invalid Next button'
            ' state in step 4! Enabled while there\'s nothing selected yet')
        dialog.lstFields.setCurrentRow(1)
        self.assertTrue(
            dialog.pbnNext.isEnabled(), 'Invalid Next button'
            ' state in step 4! Still disabled after an item selected')

        dialog.pbnNext.click()

        # step 6 of 7 - enter source
        self.assertTrue(
            dialog.pbnNext.isEnabled(), 'Invalid Next button'
            ' state in step 6! Disabled while source is optional')
        dialog.leSource.setText('some source')
        dialog.pbnNext.click()

        # step 7 of 7 - enter title
        self.assertTrue(
            not dialog.pbnNext.isEnabled(), 'Invalid Next button'
            'state in step 7! Enabled while there\'s nothing entered yet')
        dialog.leTitle.setText('some title')
        self.assertTrue(
            dialog.pbnNext.isEnabled(), 'Invalid Next button state'
            'in step 7! Still disabled after a text entered')
        dialog.pbnNext.click()

        # test the resulting keywords
        keyword_io = KeywordIO()
        keywords = keyword_io.read_keywords(layer)

        self.assertTrue(
            keywords == expected_keywords,
            'Invalid metadata!\n Was: %s\n Should be: %s' %
            (unicode(keywords), unicode(expected_keywords)))

        remove_temp_file(layer.source())


if __name__ == '__main__':
    suite = unittest.makeSuite(WizardDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
