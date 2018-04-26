# coding=utf-8
"""InaSAFE Wizard Step for Choosing Layer Geometry."""


import logging

# noinspection PyPackageRequirements
from qgis.PyQt import QtCore, QtGui, QtWidgets
from qgis.PyQt.QtCore import pyqtSlot

from safe import messaging as m
from safe.definitions.font import big_font
from safe.definitions.layer_purposes import (
    layer_purpose_exposure, layer_purpose_hazard)
from safe.definitions.styles import (
    available_option_color, unavailable_option_color)
from safe.definitions.utilities import get_allowed_geometries
from safe.gui.tools.wizard.utilities import (
    RoleFunctions,
    RoleHazard,
    RoleExposure,
    RoleHazardConstraint,
    RoleExposureConstraint)
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_strings import (
    select_function_constraints2_question)
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcFunctions2(WizardStep, FORM_CLASS):
    """Function Centric Wizard Step: IF Constraint Selector 2"""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.tblFunctions2.selectedItems())

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_fc_hazlayer_origin
        return new_step

    def selected_value(self, layer_purpose_key):
        """Obtain selected hazard or exposure.

        :param layer_purpose_key: A layer purpose key, can be hazard or
            exposure.
        :type layer_purpose_key: str

        :returns: A selected hazard or exposure definition.
        :rtype: dict
        """
        if layer_purpose_key == layer_purpose_exposure['key']:
            role = RoleExposureConstraint
        elif layer_purpose_key == layer_purpose_hazard['key']:
            role = RoleHazardConstraint
        else:
            return None

        selected = self.tblFunctions2.selectedItems()
        if len(selected) != 1:
            return None
        try:
            return selected[0].data(role)
        except (AttributeError, NameError):
            return None

    def selected_functions_2(self):
        """Obtain functions available for hazard and exposure selected by user.

        :returns: List of the available functions metadata.
        :rtype: list, None
        """
        selection = self.tblFunctions2.selectedItems()
        if len(selection) != 1:
            return []
        return selection[0].data(RoleFunctions)

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSlot()
    def on_tblFunctions2_itemSelectionChanged(self):
        """Choose selected hazard x exposure constraints combination.

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        functions = self.selected_functions_2()
        if not functions:
            self.lblAvailableFunctions2.clear()
        else:
            text = self.tr('Available functions:') + ' ' + ', '.join(
                [f['name'] for f in functions])
            self.lblAvailableFunctions2.setText(text)
        self.parent.pbnNext.setEnabled(True)

        # Put a dot to the selected cell - note there is no way
        # to center an icon without using a custom ItemDelegate
        selection = self.tblFunctions2.selectedItems()
        selItem = (len(selection) == 1) and selection[0] or None
        for row in range(self.tblFunctions2.rowCount()):
            for column in range(self.tblFunctions2.columnCount()):
                item = self.tblFunctions2.item(row, column)
                item.setText((item == selItem) and '\\u2022' or '')

    # pylint: disable=W0613
    # noinspection PyPep8Naming,PyUnusedLocal
    def on_tblFunctions2_cellDoubleClicked(self, row, column):
        """Click handler for selecting hazard and exposure constraints.

        :param row: The row that the user clicked on.
        :type row: int

        :param column: The column that the user clicked on.
        :type column: int

        .. note:: This is an automatic Qt slot executed when the category
            selection changes.
        """
        self.parent.pbnNext.click()
    # pylint: enable=W0613

    def set_widgets(self):
        """Set widgets on the Impact Functions Table 2 tab."""
        self.tblFunctions2.clear()
        hazard, exposure, _, _ = self.parent.\
            selected_impact_function_constraints()
        hazard_layer_geometries = get_allowed_geometries(
            layer_purpose_hazard['key'])
        exposure_layer_geometries = get_allowed_geometries(
            layer_purpose_exposure['key'])
        self.lblSelectFunction2.setText(
            select_function_constraints2_question % (
                hazard['name'], exposure['name']))
        self.tblFunctions2.setColumnCount(len(hazard_layer_geometries))
        self.tblFunctions2.setRowCount(len(exposure_layer_geometries))
        self.tblFunctions2.setHorizontalHeaderLabels(
            [i['name'].capitalize() for i in hazard_layer_geometries])
        for i in range(len(exposure_layer_geometries)):
            item = QtWidgets.QTableWidgetItem()
            item.setText(exposure_layer_geometries[i]['name'].capitalize())
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tblFunctions2.setVerticalHeaderItem(i, item)

        self.tblFunctions2.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
        self.tblFunctions2.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)

        active_items = []
        for column in range(len(hazard_layer_geometries)):
            for row in range(len(exposure_layer_geometries)):
                hazard_geometry = hazard_layer_geometries[column]
                exposure_geometry = exposure_layer_geometries[row]
                item = QtWidgets.QTableWidgetItem()

                hazard_geometry_allowed = hazard_geometry['key'] in hazard[
                    'allowed_geometries']
                exposure_geometry_allowed = (
                    exposure_geometry['key'] in exposure[
                        'allowed_geometries'])

                if hazard_geometry_allowed and exposure_geometry_allowed:
                    background_color = available_option_color
                    active_items += [item]
                else:
                    background_color = unavailable_option_color
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)

                item.setBackground(QtGui.QBrush(background_color))
                item.setFont(big_font)
                item.setTextAlignment(
                    QtCore.Qt.AlignCenter | QtCore.Qt.AlignHCenter)
                item.setData(RoleHazard, hazard)
                item.setData(RoleExposure, exposure)
                item.setData(RoleHazardConstraint, hazard_geometry)
                item.setData(RoleExposureConstraint, exposure_geometry)
                self.tblFunctions2.setItem(row, column, item)
        # Automatically select one item...
        if len(active_items) == 1:
            active_items[0].setSelected(True)
            # set focus, as the inactive selection style is gray
            self.tblFunctions2.setFocus()

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return tr('Impact Function Filter by Layer Geometry Step')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, there is a grid that shows all '
            'possible combination for hazard and exposure based on the layer '
            'geometry that can be run in InaSAFE. You can select a grid cell '
            'where your intended exposure and hazard intersect. This will '
            'help you to choose the layer that is suitable for the analysis. '
            'You can only select the green grid cell. The grey color '
            'indicates that the combination is not supported by InaSAFE.'
        ).format(step_name=self.step_name)))
        return message
