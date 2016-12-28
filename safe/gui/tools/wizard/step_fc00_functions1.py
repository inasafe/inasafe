# coding=utf-8
"""InaSAFE Wizard Step for Choosing Exposure and Hazard"""

# noinspection PyPackageRequirements
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignature

from safe.definitionsv4.hazard import hazard_all
from safe.definitionsv4.exposure import exposure_all
from safe.definitionsv4.colors import available_option_color
from safe.definitionsv4.font import big_font
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_utils import RoleHazard, RoleExposure
from safe.definitionsv4.layer_purposes import (
    layer_purpose_exposure, layer_purpose_hazard)
from safe.utilities.resources import resources_path

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcFunctions1(WizardStep, FORM_CLASS):
    """Function Centric Wizard Step: IF Constraint Selector 1"""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.tblFunctions1.selectedItems())

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        return self.parent.step_fc_functions2

    def selected_value(self, layer_purpose_key):
        """Obtain selected hazard or exposure.

        :param layer_purpose_key: A layer purpose key, can be hazard or
            exposure.
        :type layer_purpose_key: str

        :returns: A selected hazard or exposure definition.
        :rtype: dict
        """
        if layer_purpose_key == layer_purpose_exposure['key']:
            role = RoleExposure
        elif layer_purpose_key == layer_purpose_hazard['key']:
            role = RoleHazard
        else:
            return None

        selected = self.tblFunctions1.selectedItems()
        if len(selected) != 1:
            return None
        try:
            return selected[0].data(role)
        except (AttributeError, NameError):
            return None

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_tblFunctions1_itemSelectionChanged(self):
        """Choose selected hazard x exposure combination.

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        # Clear the selection on the 2nd matrix
        self.parent.step_fc_functions2.tblFunctions2.clearContents()
        self.parent.step_fc_functions2.lblAvailableFunctions2.clear()
        self.parent.pbnNext.setEnabled(True)

        # Put a dot to the selected cell - note there is no way
        # to center an icon without using a custom ItemDelegate
        selection = self.tblFunctions1.selectedItems()
        selItem = (len(selection) == 1) and selection[0] or None
        for row in range(self.tblFunctions1.rowCount()):
            for col in range(self.tblFunctions1.columnCount()):
                item = self.tblFunctions1.item(row, col)
                item.setText((item == selItem) and u'\u2022' or '')

    # pylint: disable=W0613
    # noinspection PyPep8Naming
    def on_tblFunctions1_cellDoubleClicked(self, row, column):
        """Choose selected hazard x exposure combination and go ahead.

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        self.parent.pbnNext.click()
    # pylint: enable=W0613

    def populate_function_table_1(self):
        """Populate the tblFunctions1 table with available functions."""
        # The hazard category radio buttons are now removed -
        # make this parameter of IFM.available_hazards() optional
        hazards = hazard_all
        # Remove 'generic' from hazards
        for hazard in hazards:
            if hazard['key'] == 'generic':
                hazards.remove(hazard)
        exposures = exposure_all

        self.lblAvailableFunctions1.clear()
        self.tblFunctions1.clear()
        self.tblFunctions1.setColumnCount(len(hazards))
        self.tblFunctions1.setRowCount(len(exposures))
        for i in range(len(hazards)):
            hazard = hazards[i]
            item = QtGui.QTableWidgetItem()
            item.setIcon(QtGui.QIcon(
                resources_path('img', 'wizard', 'keyword-subcategory-%s.svg'
                               % (hazard['key'] or 'notset'))))
            item.setText(hazard['name'].capitalize())
            self.tblFunctions1.setHorizontalHeaderItem(i, item)
        for i in range(len(exposures)):
            exposure = exposures[i]
            item = QtGui.QTableWidgetItem()

            item.setIcon(QtGui.QIcon(resources_path(
                'img', 'wizard', 'keyword-subcategory-%s.svg'
                % (exposure['key'] or 'notset'))))
            item.setText(exposure['name'].capitalize())
            self.tblFunctions1.setVerticalHeaderItem(i, item)

        for hazard in hazards:
            for exposure in exposures:
                item = QtGui.QTableWidgetItem()
                background_colour = available_option_color
                item.setBackground(QtGui.QBrush(background_colour))
                item.setFont(big_font)
                item.setTextAlignment(
                    QtCore.Qt.AlignCenter | QtCore.Qt.AlignHCenter)
                item.setData(RoleHazard, hazard)
                item.setData(RoleExposure, exposure)
                self.tblFunctions1.setItem(
                    exposures.index(exposure), hazards.index(hazard), item)
        self.parent.pbnNext.setEnabled(False)

    def set_widgets(self):
        """Set widgets on the Impact Functions Table 1 tab."""
        self.tblFunctions1.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)
        self.tblFunctions1.verticalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)

        self.populate_function_table_1()
