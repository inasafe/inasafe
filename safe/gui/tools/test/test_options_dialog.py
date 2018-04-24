# coding=utf-8
"""Test InaSAFE Options Dialog."""

import unittest
import logging

from safe.definitions.constants import INASAFE_TEST
from safe.definitions.default_settings import inasafe_default_settings
from safe.definitions.messages import disclaimer
from safe.gui.tools.options_dialog import OptionsDialog
from safe.test.utilities import get_qgis_app
from safe.common.utilities import temp_dir
from safe.defaults import default_north_arrow_path, supporters_logo_path
from PyQt4.QtCore import QSettings

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting=INASAFE_TEST)

LOGGER = logging.getLogger('InaSAFE')

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestOptionsDialog(unittest.TestCase):

    """Test Options Dialog."""

    def setUp(self):
        """Fixture run before all tests."""
        self.qsetting = QSettings(INASAFE_TEST)
        self.qsetting.clear()

    def tearDown(self):
        """Fixture run after each test."""
        # Make sure it's empty
        self.qsetting.clear()

    def test_setup_dialog(self):
        """Test Setup Options Dialog."""
        dialog = OptionsDialog(
            parent=PARENT, iface=IFACE, qsetting=INASAFE_TEST)
        self.assertIsNotNone(dialog)

        # Check default values
        self.assertEqual(
            dialog.cbxVisibleLayersOnly.isChecked(),
            inasafe_default_settings['visibleLayersOnlyFlag'])
        self.assertEqual(
            dialog.cbxSetLayerNameFromTitle.isChecked(),
            inasafe_default_settings['set_layer_from_title_flag'])
        self.assertEqual(
            dialog.cbxZoomToImpact.isChecked(),
            inasafe_default_settings['setZoomToImpactFlag'])
        self.assertEqual(
            dialog.cbxHideExposure.isChecked(),
            inasafe_default_settings['setHideExposureFlag'])
        self.assertEqual(
            dialog.cbxUseSelectedFeaturesOnly.isChecked(),
            inasafe_default_settings['useSelectedFeaturesOnly'])
        self.assertEqual(
            dialog.leKeywordCachePath.text(),
            inasafe_default_settings['keywordCachePath'])
        self.assertEqual(
            dialog.template_warning_checkbox.isChecked(),
            inasafe_default_settings['template_warning_verbose'])
        self.assertEqual(
            dialog.organisation_on_dock_checkbox.isChecked(),
            inasafe_default_settings['showOrganisationLogoInDockFlag'])
        self.assertEqual(
            dialog.cbxDevMode.isChecked(),
            inasafe_default_settings['developer_mode'])

        self.assertEqual(
            dialog.leNorthArrowPath.text(), default_north_arrow_path())
        self.assertEqual(
            dialog.organisation_logo_path_line_edit.text(),
            supporters_logo_path())
        self.assertEqual(dialog.leReportTemplatePath.text(), '')
        self.assertEqual(dialog.txtDisclaimer.toPlainText(), disclaimer())
        self.assertEqual(
            dialog.leUserDirectoryPath.text(), temp_dir('impacts'))

        self.assertEqual(
            dialog.organisation_line_edit.text(),
            inasafe_default_settings['ISO19115_ORGANIZATION'])
        self.assertEqual(
            dialog.website_line_edit.text(),
            inasafe_default_settings['ISO19115_URL'])
        self.assertEqual(
            dialog.email_line_edit.text(),
            inasafe_default_settings['ISO19115_EMAIL'])
        self.assertEqual(
            dialog.license_line_edit.text(),
            inasafe_default_settings['ISO19115_LICENSE'])

    def test_update_settings(self):
        """Test update InaSAFE Option works."""
        # Create new option dialog
        dialog = OptionsDialog(
            parent=PARENT, iface=IFACE, qsetting=INASAFE_TEST)

        # Update some state
        new_state = not inasafe_default_settings['visibleLayersOnlyFlag']
        dialog.cbxVisibleLayersOnly.setChecked(new_state)

        new_organization = 'Super Organization'
        dialog.organisation_line_edit.setText(new_organization)

        # Accept the dialog
        dialog.accept()

        # Check the value in QSettings
        # Next two lines a hack because windows qsettings returns a string
        # rather than a bool...TS
        value = self.qsetting.value('inasafe/visibleLayersOnlyFlag')
        if value == u'false':
            value = False
        if value == u'true':
            value = True
        self.assertEquals(
            new_state, value)
        self.assertEqual(
            new_organization,
            self.qsetting.value('inasafe/ISO19115_ORGANIZATION'))

        # Open the options dialog
        dialog = OptionsDialog(
            iface=IFACE, parent=PARENT, qsetting=INASAFE_TEST)

        # Check the state of the dialog after save the settings
        self.assertEqual(new_state, dialog.cbxVisibleLayersOnly.isChecked())
        self.assertEqual(
            new_organization, dialog.organisation_line_edit.text())

    def test_mode(self):
        """Test for checking that the state is correct for the mode.

        If your test is failed, perhaps one the following is the cause:
        1. You add / remove tab in the options.
        2. You rename the tab's name.
        3. The function show_welcome_dialog or show_option_dialog is changed
        """
        # Welcome mode
        dialog = OptionsDialog(parent=PARENT, iface=IFACE)
        dialog.show_welcome_dialog()

        expected_tabs = [
            dialog.welcome_tab,
            dialog.organisation_profile_tab,
            dialog.preference_tab
        ]

        message = 'Tab count should be %d in welcome dialog.' % len(
            expected_tabs)
        self.assertEqual(dialog.tabWidget.count(), len(expected_tabs), message)

        message = 'Current tab index should be 0.'
        self.assertEqual(dialog.tabWidget.currentIndex(), 0, message)

        for index, expected_tab in enumerate(expected_tabs):
            dialog.tabWidget.setCurrentIndex(index)
            message = 'Current tab should be %s.' % expected_tab.objectName()
            current_tab = dialog.tabWidget.currentWidget()
            self.assertEqual(current_tab, expected_tab, message)

        # Usual option mode
        dialog = OptionsDialog(parent=PARENT, iface=IFACE)
        dialog.show_option_dialog()

        expected_tabs = [
            dialog.organisation_profile_tab,
            dialog.preference_tab,
            dialog.gis_environment_tab,
            dialog.earthquake_tab,
            dialog.template_option_tab,
            dialog.demographic_defaults_tab,
            dialog.advanced_tab
        ]

        message = 'Tab count should be %d in welcome dialog.' % len(
            expected_tabs)
        self.assertEqual(dialog.tabWidget.count(), len(expected_tabs), message)

        message = 'Current tab index should be 0.'
        self.assertEqual(dialog.tabWidget.currentIndex(), 0, message)

        for index, expected_tab in enumerate(expected_tabs):
            dialog.tabWidget.setCurrentIndex(index)
            message = 'Current tab should be %s.' % expected_tab.objectName()
            current_tab = dialog.tabWidget.currentWidget()
            self.assertEqual(current_tab, expected_tab, message)


if __name__ == '__main__':
    suite = unittest.makeSuite(TestOptionsDialog, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
