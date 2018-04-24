# coding=utf-8
"""InaSAFE Wizard Step for Choosing Exposure and Hazard."""


from copy import deepcopy

from qgis.PyQt.QtCore import Qt, pyqtSlot
from qgis.PyQt.QtGui import QIcon, QBrush
from qgis.PyQt.QtWidgets import QTableWidgetItem, QHeaderView

from safe import messaging as m
from safe.definitions.exposure import exposure_all
from safe.definitions.font import big_font
from safe.definitions.hazard import hazard_all
from safe.definitions.layer_purposes import (
    layer_purpose_exposure, layer_purpose_hazard)
from safe.definitions.styles import (
    available_option_color, unavailable_option_color)
from safe.gui.tools.wizard.utilities import (
    RoleHazard, RoleExposure, get_image_path)
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.utilities.i18n import tr
from safe.utilities.settings import setting

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
    @pyqtSlot()
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
            for column in range(self.tblFunctions1.columnCount()):
                item = self.tblFunctions1.item(row, column)
                item.setText((item == selItem) and '\\u2022' or '')

    # pylint: disable=W0613
    # noinspection PyPep8Naming
    def on_tblFunctions1_cellDoubleClicked(self):
        """Choose selected hazard x exposure combination and go ahead.

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        self.parent.pbnNext.click()
    # pylint: enable=W0613

    def populate_function_table_1(self):
        """Populate the tblFunctions1 table with available functions."""
        hazards = deepcopy(hazard_all)
        exposures = exposure_all

        self.lblAvailableFunctions1.clear()
        self.tblFunctions1.clear()
        self.tblFunctions1.setColumnCount(len(hazards))
        self.tblFunctions1.setRowCount(len(exposures))
        for i in range(len(hazards)):
            hazard = hazards[i]
            item = QTableWidgetItem()
            item.setIcon(QIcon(get_image_path(hazard)))
            item.setText(hazard['name'].capitalize())
            item.setTextAlignment(Qt.AlignLeft)
            self.tblFunctions1.setHorizontalHeaderItem(i, item)
        for i in range(len(exposures)):
            exposure = exposures[i]
            item = QTableWidgetItem()
            item.setIcon(QIcon(get_image_path(exposure)))
            item.setText(exposure['name'].capitalize())
            self.tblFunctions1.setVerticalHeaderItem(i, item)
        developer_mode = setting('developer_mode', False, bool)
        for hazard in hazards:
            for exposure in exposures:
                item = QTableWidgetItem()
                if (exposure in hazard['disabled_exposures'] and not
                        developer_mode):
                    background_colour = unavailable_option_color
                    # Set it disable and un-selectable
                    item.setFlags(
                        item.flags() & ~
                        Qt.ItemIsEnabled & ~
                        Qt.ItemIsSelectable
                    )
                else:
                    background_colour = available_option_color
                item.setBackground(QBrush(background_colour))
                item.setFont(big_font)
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignHCenter)
                item.setData(RoleHazard, hazard)
                item.setData(RoleExposure, exposure)
                self.tblFunctions1.setItem(
                    exposures.index(exposure), hazards.index(hazard), item)
        self.parent.pbnNext.setEnabled(False)

    def set_widgets(self):
        """Set widgets on the Impact Functions Table 1 tab."""
        self.tblFunctions1.horizontalHeader().setResizeMode(
            QHeaderView.Stretch)
        self.tblFunctions1.verticalHeader().setResizeMode(
            QHeaderView.Stretch)

        self.populate_function_table_1()

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return tr('Impact Function Filter by Layer Purpose Step')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, there is a grid that shows all '
            'possible combination for hazard and exposure that can be run in '
            'InaSAFE. You can select a grid cell where your intended exposure '
            'and hazard intersect. This will help you to choose the '
            'layer that is suitable for the analysis. You can only '
            'select the green grid cell. The grey color indicates that the '
            'combination is not supported by InaSAFE.'
            '').format(step_name=self.step_name)))
        return message
