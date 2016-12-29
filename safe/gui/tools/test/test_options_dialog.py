# coding=utf-8
"""Test InaSAFE Options Dialog"""

import unittest
import logging

from safe.definitionsv4.default_settings import inasafe_default_settings
from safe.gui.tools.options_dialog import OptionsDialog
from safe.test.utilities import get_qgis_app
from safe.common.utilities import temp_dir
from safe.defaults import (
    default_north_arrow_path,
    supporters_logo_path,
    disclaimer)
from PyQt4.QtCore import QSettings

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

LOGGER = logging.getLogger('InaSAFE')

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class TestOptionsDialog(unittest.TestCase):
    """Test Options Dialog"""

    def setUp(self):
        """Fixture run before all tests"""
        self.qsetting = QSettings('InaSAFETest')
        self.qsetting.clear()

    def tearDown(self):
        """Fixture run after each test."""
        # Make sure it's empty
        self.qsetting.clear()

    def test_setup_dialog(self):
        """Test Setup Options Dialog."""
        dialog = OptionsDialog(
            parent=PARENT, iface=IFACE, qsetting='InaSAFETest')
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
            dialog.leOrganisationLogoPath.text(), supporters_logo_path())
        self.assertEqual(dialog.leReportTemplatePath.text(), '')
        self.assertEqual(dialog.txtDisclaimer.toPlainText(), disclaimer())
        self.assertEqual(
            dialog.leUserDirectoryPath.text(), temp_dir('impacts'))

        self.assertEqual(
            dialog.iso19115_organization_le.text(),
            inasafe_default_settings['ISO19115_ORGANIZATION'])
        self.assertEqual(
            dialog.iso19115_url_le.text(),
            inasafe_default_settings['ISO19115_URL'])
        self.assertEqual(
            dialog.iso19115_email_le.text(),
            inasafe_default_settings['ISO19115_EMAIL'])
        self.assertEqual(
            dialog.iso19115_title_le.text(),
            inasafe_default_settings['ISO19115_TITLE'])
        self.assertEqual(
            dialog.iso19115_license_le.text(),
            inasafe_default_settings['ISO19115_LICENSE'])

    def test_update_settings(self):
        """Test update InaSAFE Option works."""
        # Create new option dialog
        dialog = OptionsDialog(
            parent=PARENT, iface=IFACE, qsetting='InaSAFETest')

        # Update some state
        new_state = not inasafe_default_settings['visibleLayersOnlyFlag']
        dialog.cbxVisibleLayersOnly.setChecked(new_state)

        new_organization = 'Super Organization'
        dialog.iso19115_organization_le.setText(new_organization)

        # Accept the dialog
        dialog.accept()

        # Check the value in QSettings
        self.assertEqual(
            new_state, self.qsetting.value('inasafe/visibleLayersOnlyFlag'))
        self.assertEqual(
            new_organization,
            self.qsetting.value('inasafe/ISO19115_ORGANIZATION'))

        # Open the options dialog
        dialog = OptionsDialog(PARENT, IFACE, qsetting='InaSAFETest')

        # Check the state of the dialog after save the settings
        self.assertEqual(new_state, dialog.cbxVisibleLayersOnly.isChecked())
        self.assertEqual(
            new_organization, dialog.iso19115_organization_le.text())

if __name__ == '__main__':
    suite = unittest.makeSuite(TestOptionsDialog, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
