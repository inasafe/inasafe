# coding=utf-8
"""InaSAFE Keyword Wizard Band Selector."""

import logging

# noinspection PyPackageRequirements
from PyQt4 import QtCore
from PyQt4.QtGui import QListWidgetItem
from qgis.core import QgsRasterBandStats

from safe.gui.tools.wizard.wizard_step import (
    get_wizard_step_ui_class, WizardStep)
from safe.utilities.i18n import tr

LOGGER = logging.getLogger('InaSAFE')

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwBandSelector(WizardStep, FORM_CLASS):

    """InaSAFE Keyword Wizard Band Selector."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: widget to use as parent (Wizard Dialog).
        :type parent: QWidget
        """
        WizardStep.__init__(self, parent)
        self.lstBands.itemSelectionChanged.connect(
            self.update_band_description)

    def is_ready_to_next_step(self):
        """Check if the step is complete.

        If so, there is no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return True

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to.
        :rtype: WizardStep instance or None
        """
        return self.parent.step_kw_layermode

    def update_band_description(self):
        """Helper to update band description."""
        self.clear_further_steps()
        # Set widgets
        selected_band = self.selected_band()
        statistics = self.parent.layer.dataProvider().bandStatistics(
            selected_band,
            QgsRasterBandStats.All,
            self.parent.layer.extent(),
            0)
        band_description = tr(
            'This band contains data from {min_value} to {max_value}').format(
            min_value=statistics.minimumValue,
            max_value=statistics.maximumValue
        )
        self.lblDescribeBandSelector.setText(band_description)

    def selected_band(self):
        """Obtain the layer mode selected by user.

        :returns: selected layer mode.
        :rtype: string, None
        """
        item = self.lstBands.currentItem()
        return item.data(QtCore.Qt.UserRole)

    def clear_further_steps(self):
        """Clear all further steps in order to properly calculate the prev step
        """
        self.parent.step_kw_unit.lstUnits.clear()
        self.parent.step_kw_field.lstFields.clear()
        self.parent.step_kw_classification.lstClassifications.clear()

    def set_widgets(self):
        """Set widgets on the LayerMode tab."""
        self.clear_further_steps()
        # Set widgets
        self.lblBandSelector.setText(tr(
            'Please select which band that contains the data that you want to '
            'use for this layer.'))
        self.lstBands.clear()
        band_num = self.parent.layer.bandCount()
        for i in range(band_num):
            item = QListWidgetItem(
                self.parent.layer.bandName(i + 1),
                self.lstBands)
            item.setData(QtCore.Qt.UserRole, i + 1)
            self.lstBands.addItem(item)
        existing_band = self.parent.get_existing_keyword('active_band')
        if existing_band:
            self.lstBands.setCurrentRow(existing_band - 1)
        else:
            # Set to Band 1 / index 0
            self.lstBands.setCurrentRow(0)
