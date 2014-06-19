# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **GUI Test Cases for Wizard in Local mode.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'ismail@linfiniti.com'
__date__ = '24/02/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
import os
import sys

skipped_reason = (
    'These tests are skipped because it will make a segmentation fault. Just '
    'run in separately.')


@unittest.skip(skipped_reason)
class TestWizardDialogLocale(unittest.TestCase):
    """Test for Wizard Dialog in Locale mode."""
    def setUp(self):
        if 'safe.metadata' in sys.modules.keys():
            del sys.modules['safe.metadata']
        self.assertFalse('safe.metadata' in sys.modules.keys())
        os.environ['LANG'] = 'id'

    def tearDown(self):
        if 'LANG' in os.environ:
            del os.environ['LANG']

    def check_list(self, expected_list, list_widget):
        """Helper function to check that list_widget is equal to expected_list.

        :param expected_list: List of expected values to be found.
        :type expected_list: list

        :param list_widget: List widget that wants to be checked.
        :type expected_list: QListWidget
        """
        real_list = []
        for i in range(list_widget.count()):
            real_list.append(list_widget.item(i).text())
        message = ('Expected %s but I got %s' % (expected_list, real_list))
        self.assertItemsEqual(expected_list, real_list, message)

    def check_current_step(self, expected_step, dialog):
        """Helper function to check the current step is expected_step

        :param expected_step: The expected current step.
        :type expected_step: int

        :param dialog: The dialog that contains a wizard.
        :type dialog: WizardDialog
        """
        current_step = dialog.get_current_step()
        message = ('Expected %s but I got %s' % (expected_step, current_step))
        self.assertEqual(expected_step, current_step, message)

    # noinspection PyUnresolvedReferences
    def check_current_text(self, expected_text, list_widget):
        """Check the current text in list widget is expected_text

        :param expected_text: The expected current step.
        :type expected_text: str

        :param list_widget: List widget that wants to be checked.
        :type list_widget: QListWidget
        """
        # noinspection PyUnresolvedReferences
        message = 'No selected option in the list'
        self.assertNotEqual(-1, list_widget.currentRow(), message)
        current_text = list_widget.currentItem().text()
        message = ('Expected %s but I got %s' % (expected_text, current_text))
        self.assertEqual(expected_text, current_text, message)

    # noinspection PyUnresolvedReferences
    def select_from_list_widget(self, option, list_widget):
        """Helper function to select option from list_widget

        :param option: Option to be chosen
        :type option: str

        :param list_widget: List widget that wants to be checked.
        :type list_widget: QListWidget
        """
        items = []
        for i in range(list_widget.count()):
            items.append(list_widget.item(i).text())
            if list_widget.item(i).text() == option:
                list_widget.setCurrentRow(i)
                return
        message = 'There is no %s in the list widget' % option
        message += '\n The options are %s' % items
        self.assertTrue(False, message)

    def test_translation(self):
        """Test for metadata translation."""
        from safe_qgis.tools.wizard_dialog import WizardDialog
        from safe_qgis.utilities.utilities_for_testing import (
            clone_shp_layer, remove_vector_temp_file)
        from safe_qgis.safe_interface import BOUNDDATA

        from safe.common.testing import get_qgis_app
        # Get QGis app handle
        # noinspection PyPep8Naming
        _, _, IFACE, PARENT = get_qgis_app()

        layer = clone_shp_layer(
            name='kabupaten_jakarta',
            include_keywords=True,
            source_directory=BOUNDDATA)
        # noinspection PyTypeChecker
        dialog = WizardDialog(PARENT, IFACE, None, layer)
        expected_categories = ['keterpaparan', 'ancaman', 'agregasi']
        # noinspection PyTypeChecker
        self.check_list(expected_categories, dialog.lstCategories)

        self.check_current_text('agregasi', dialog.lstCategories)

        dialog.pbnNext.click()

        remove_vector_temp_file(layer.source())

    def test_existing_complex_keywords(self):
        """Test for existing complex keywords in wizard in locale mode."""
        from safe_qgis.tools.wizard_dialog import WizardDialog
        from safe_qgis.utilities.utilities_for_testing import (
            clone_shp_layer, remove_vector_temp_file)
        layer = clone_shp_layer(include_keywords=True)

        from safe.common.testing import get_qgis_app
        # Get QGis app handle
        # noinspection PyPep8Naming
        _, _, IFACE, PARENT = get_qgis_app()
        # noinspection PyTypeChecker
        dialog = WizardDialog(PARENT, IFACE, None, layer)

        # select hazard
        self.select_from_list_widget('ancaman', dialog.lstCategories)
        dialog.pbnNext.click()

        # select volcano
        self.select_from_list_widget('gunung berapi', dialog.lstSubcategories)
        dialog.pbnNext.click()

        # select volcano categorical unit
        self.select_from_list_widget('Kategori gunung berapi', dialog.lstUnits)
        dialog.pbnNext.click()

        # select GRIDCODE
        self.select_from_list_widget('GRIDCODE', dialog.lstFields)
        dialog.pbnNext.click()

        unit = dialog.selected_unit()
        default_classes = unit['classes']
        unassigned_values = []  # no need to check actually, not save in file
        assigned_values = {
            'low': ['5.0'],
            'medium': ['3.0', '4.0'],
            'high': ['2.0']
        }
        dialog.populate_classified_values(
            unassigned_values, assigned_values, default_classes)
        dialog.pbnNext.click()

        source = 'Source'
        source_scale = 'Source Scale'
        source_url = 'Source Url'
        source_date = 'Source Date'

        dialog.leSource.setText(source)
        dialog.leSource_scale.setText(source_scale)
        dialog.leSource_url.setText(source_url)
        dialog.leSource_date.setText(source_date)
        dialog.pbnNext.click()  # next
        dialog.pbnNext.click()  # finish

        # noinspection PyTypeChecker
        dialog = WizardDialog(PARENT, IFACE, None, layer)

        # step 1 of 7 - select category
        self.check_current_text('ancaman', dialog.lstCategories)

        # Click Next
        dialog.pbnNext.click()

        # step 2 of 7 - select subcategory
        # noinspection PyTypeChecker
        self.check_current_text('gunung berapi', dialog.lstSubcategories)

        # Click Next
        dialog.pbnNext.click()

        # step 3 of 7 - select volcano units
        self.check_current_text('Kategori gunung berapi', dialog.lstUnits)

        # Click Next
        dialog.pbnNext.click()

        # step 4 of 7 - select field
        self.check_current_text('GRIDCODE', dialog.lstFields)

        # Click Next
        dialog.pbnNext.click()

        for index in range(dialog.lstUniqueValues.count()):
            message = ('%s Should be in unassigned values' %
                       dialog.lstUniqueValues.item(index).text())
            self.assertIn(
                dialog.lstUniqueValues.item(index).text(),
                unassigned_values,
                message)
        real_assigned_values = dialog.selected_mapping()
        self.assertDictEqual(real_assigned_values, assigned_values)

        # Click Next
        dialog.pbnNext.click()

        # step 6 of 7 - enter source
        message = ('Invalid Next button state in step 6! Disabled while '
                   'source is optional')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)

        message = 'Source should be %s' % source
        self.assertEqual(dialog.leSource.text(), source, message)
        message = 'Source Url should be %s' % source_url
        self.assertEqual(dialog.leSource_url.text(), source_url, message)
        message = 'Source Date should be %s' % source_date
        self.assertEqual(dialog.leSource_date.text(), source_date, message)
        message = 'Source Scale should be %s' % source_scale
        self.assertEqual(dialog.leSource_scale.text(), source_scale, message)
        dialog.pbnNext.click()

        dialog.pbnCancel.click()

        remove_vector_temp_file(layer.source())


if __name__ == '__main__':
    unittest.main()
