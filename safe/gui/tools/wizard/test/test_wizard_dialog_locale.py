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
from builtins import range
__author__ = 'ismail@kartoza.com'
__date__ = '24/02/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

# pylint: disable=no-member
import unittest
import os
import sys
# Import qgis in order to set SIP API.
# pylint: disable=unused-import
import qgis
# pylint: enable=unused-import
from qgis.PyQt.QtCore import QDateTime

from safe.definitions.constants import INASAFE_TEST

skipped_reason = (
    'These tests are skipped because it will make a segmentation fault. Just '
    'run it separately.')


@unittest.skip(skipped_reason)
class TestWizardDialogLocale(unittest.TestCase):
    """Test for Wizard Dialog in Locale mode."""
    def setUp(self):
        if 'safe.metadata' in list(sys.modules.keys()):
            del sys.modules['safe.metadata']
        self.assertFalse('safe.metadata' in list(sys.modules.keys()))
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
        raise Exception(message)

    def test_translation(self):
        """Test for metadata translation."""
        from safe.test.utilities import (
            clone_shp_layer, remove_vector_temp_file)
        from safe.test.utilities import BOUNDDATA

        from safe.test.utilities import get_qgis_app
        # Get QGis app handle
        # noinspection PyPep8Naming
        _, _, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

        from safe.gui.tools.wizard.wizard_dialog import WizardDialog

        layer = clone_shp_layer(
            name='kabupaten_jakarta',
            include_keywords=True,
            source_directory=BOUNDDATA)
        # noinspection PyTypeChecker
        dialog = WizardDialog(PARENT, IFACE)
        dialog.set_keywords_creation_mode(layer)
        expected_categories = ['ancaman']
        # noinspection PyTypeChecker
        self.check_list(expected_categories,
                        dialog.step_kw_purpose.lstCategories)

        self.check_current_text(
            'ancaman', dialog.step_kw_purpose.lstCategories)

        dialog.pbnNext.click()

        remove_vector_temp_file(layer.source())

    def test_existing_complex_keywords(self):
        """Test for existing complex keywords in wizard in locale mode."""
        from safe.test.utilities import (
            clone_shp_layer, remove_vector_temp_file)
        layer = clone_shp_layer(
            name='tsunami_polygon', include_keywords=True, source_directory='')

        from safe.test.utilities import get_qgis_app
        # Get QGis app handle
        # noinspection PyPep8Naming
        _, _, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

        from safe.gui.tools.wizard.wizard_dialog import WizardDialog

        # noinspection PyTypeChecker
        dialog = WizardDialog(PARENT, IFACE)
        dialog.set_keywords_creation_mode(layer)

        # select hazard
        self.select_from_list_widget('ancaman',
                                     dialog.step_kw_purpose.lstCategories)
        dialog.pbnNext.click()

        # select volcano
        self.select_from_list_widget('gunung berapi', dialog.
                                     step_kw_subcategory.lstSubcategories)
        dialog.pbnNext.click()

        # select volcano categorical unit
        self.select_from_list_widget('Kategori gunung berapi',
                                     dialog.step_kw_unit.lstUnits)
        dialog.pbnNext.click()

        # select GRIDCODE
        self.select_from_list_widget(
            'GRIDCODE', dialog.step_kw_field.lstFields)
        dialog.pbnNext.click()

        unit = dialog.step_kw_unit.selected_unit()
        default_classes = unit['classes']
        unassigned_values = []  # no need to check actually, not save in file
        assigned_values = {
            'low': ['5.0'],
            'medium': ['3.0', '4.0'],
            'high': ['2.0']
        }
        dialog.step_kw_classify.populate_classified_values(
            unassigned_values, assigned_values, default_classes)
        dialog.pbnNext.click()

        source = 'Source'
        source_scale = 'Source Scale'
        source_url = 'Source Url'
        source_date = QDateTime.fromString(
            '06-12-2015 12:30',
            'dd-MM-yyyy HH:mm')

        dialog.step_kw_source.leSource.setText(source)
        dialog.step_kw_source.leSource_scale.setText(source_scale)
        dialog.step_kw_source.leSource_url.setText(source_url)
        dialog.step_kw_source.leSource_date.seDateTime(source_date)
        dialog.pbnNext.click()  # next
        dialog.pbnNext.click()  # finish

        # noinspection PyTypeChecker
        dialog = WizardDialog(PARENT, IFACE)
        dialog.set_keywords_creation_mode(layer)

        # step 1 of 7 - select category
        self.check_current_text(
            'ancaman', dialog.step_kw_purpose.lstCategories)

        # Click Next
        dialog.pbnNext.click()

        # step 2 of 7 - select subcategory
        # noinspection PyTypeChecker
        self.check_current_text('gunung berapi',
                                dialog.step_kw_subcategory.lstSubcategories)

        # Click Next
        dialog.pbnNext.click()

        # step 3 of 7 - select volcano units
        self.check_current_text('Kategori gunung berapi',
                                dialog.step_kw_unit.lstUnits)

        # Click Next
        dialog.pbnNext.click()

        # step 4 of 7 - select field
        self.check_current_text('GRIDCODE', dialog.step_kw_field.lstFields)

        # Click Next
        dialog.pbnNext.click()

        for index in range(dialog.step_classify.lstUniqueValues.count()):
            message = ('%s Should be in unassigned values' %
                       dialog.step_classify.lstUniqueValues.item(index).text())
            self.assertIn(
                dialog.step_classify.lstUniqueValues.item(index).text(),
                unassigned_values,
                message)
        real_assigned_values = dialog.step_classify.selected_mapping()
        self.assertDictEqual(real_assigned_values, assigned_values)

        # Click Next
        dialog.pbnNext.click()

        # step 6 of 7 - enter source
        message = ('Invalid Next button state in step 6! Disabled while '
                   'source is optional')
        self.assertTrue(dialog.pbnNext.isEnabled(), message)

        message = 'Source should be %s' % source
        self.assertEqual(
            dialog.step_kw_source.leSource.text(), source, message)
        message = 'Source Url should be %s' % source_url
        self.assertEqual(dialog.step_kw_source.leSource_url.text(),
                         source_url, message)
        message = 'Source Date should be %s' % source_date.toString(
            'dd-MM-yyyy HH:mm')
        self.assertEqual(dialog.step_kw_source.leSource_date.dateTime(),
                         source_date, message)
        message = 'Source Scale should be %s' % source_scale
        self.assertEqual(dialog.step_kw_source.leSource_scale.text(),
                         source_scale, message)
        dialog.pbnNext.click()

        dialog.pbnCancel.click()

        remove_vector_temp_file(layer.source())


if __name__ == '__main__':
    unittest.main()
