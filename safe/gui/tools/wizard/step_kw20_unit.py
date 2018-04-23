# coding=utf-8
"""InaSAFE Wizard Step Layer Unit."""
from builtins import range

# noinspection PyPackageRequirements
from qgis.PyQt import QtCore
from qgis.PyQt.QtWidgets import QListWidgetItem

from safe import messaging as m
from safe.definitions.hazard import continuous_hazard_unit
from safe.definitions.layer_purposes import layer_purpose_hazard
from safe.definitions.units import exposure_unit
from safe.definitions.utilities import (
    definition, hazard_units, exposure_units, get_classifications)
from safe.gui.tools.wizard.wizard_step import (
    get_wizard_step_ui_class, WizardStep)
from safe.gui.tools.wizard.wizard_strings import unit_question
from safe.utilities.gis import is_raster_layer
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwUnit(WizardStep, FORM_CLASS):

    """InaSAFE Wizard Step Layer Unit."""

    def is_ready_to_next_step(self):
        """Check if the step is complete.

        If so, there is no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.selected_unit())

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to.
        :rtype: WizardStep instance or None
        """
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        is_raster = is_raster_layer(self.parent.layer)
        has_classifications = get_classifications(subcategory['key'])

        # Vector
        if not is_raster:
            return self.parent.step_kw_field
        # Raster and has classifications
        elif has_classifications:
            return self.parent.step_kw_multi_classifications
        # else go to source
        return self.parent.step_kw_source

    # noinspection PyPep8Naming
    def on_lstUnits_itemSelectionChanged(self):
        """Update unit description label and field widgets.

        .. note:: This is an automatic Qt slot
           executed when the unit selection changes.
        """
        self.clear_further_steps()
        # Set widgets
        unit = self.selected_unit()
        # Exit if no selection
        if not unit:
            return
        self.lblDescribeUnit.setText(unit['description'])
        # Enable the next button
        self.parent.pbnNext.setEnabled(True)

    def selected_unit(self):
        """Obtain the unit selected by user.

        :returns: Metadata of the selected unit.
        :rtype: dict, None
        """
        item = self.lstUnits.currentItem()
        try:
            return definition(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def clear_further_steps(self):
        """Clear all further steps in order to properly compute the prev step.
        """
        self.parent.step_kw_field.lstFields.clear()
        self.parent.step_kw_classification.lstClassifications.clear()

    def set_widgets(self):
        """Set widgets on the Unit tab."""
        self.clear_further_steps()
        # Set widgets
        purpose = self.parent.step_kw_purpose.selected_purpose()
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        self.lblSelectUnit.setText(
            unit_question % (subcategory['name'], purpose['name']))
        self.lblDescribeUnit.setText('')
        self.lstUnits.clear()
        subcat = self.parent.step_kw_subcategory.selected_subcategory()['key']
        if purpose == layer_purpose_hazard:
            units_for_layer = hazard_units(subcat)
        else:
            units_for_layer = exposure_units(subcat)
        for unit_for_layer in units_for_layer:
            item = QListWidgetItem(unit_for_layer['name'], self.lstUnits)
            item.setData(QtCore.Qt.UserRole, unit_for_layer['key'])
            self.lstUnits.addItem(item)

        # Set values based on existing keywords (if already assigned)
        if self.parent.step_kw_purpose.\
                selected_purpose() == layer_purpose_hazard:
            key = continuous_hazard_unit['key']
        else:
            key = exposure_unit['key']
        unit_id = self.parent.get_existing_keyword(key)
        if unit_id:
            units = []
            for index in range(self.lstUnits.count()):
                item = self.lstUnits.item(index)
                units.append(item.data(QtCore.Qt.UserRole))
            if unit_id in units:
                self.lstUnits.setCurrentRow(units.index(unit_id))

        self.auto_select_one_item(self.lstUnits)

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return tr('Layer Unit Step')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you will be able to set the '
            'unit of the layer that is being assigned in this wizard. This '
            'only applies for continuous layer.'
        ).format(step_name=self.step_name)))
        return message
