# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Keyword Wizard Step: Layer Mode

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

# noinspection PyPackageRequirements
from PyQt4 import QtCore
from PyQt4.QtGui import QListWidgetItem

from safe.common.exceptions import InvalidWizardStep
from safe.utilities.i18n import tr
from safe.definitionsv4.layer_purposes import (
    layer_purpose_exposure, layer_purpose_hazard)
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_strings import (
    layer_mode_raster_question,
    layer_mode_vector_question,
    layer_mode_vector_classified_confirm,
    layer_mode_vector_continuous_confirm)
from safe.utilities.gis import is_raster_layer
from safe.definitionsv4.utilities import definition, get_layer_modes
from safe.definitionsv4.layer_modes import (
    layer_mode_classified, layer_mode_continuous)
from safe.definitionsv4.utilities import get_classifications

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwLayerMode(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Layer Mode"""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.selected_layermode())

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        # Check if there is classifications or no
        layer_purpose = self.parent.step_kw_purpose.selected_purpose()
        layer_mode = self.selected_layermode()

        if layer_purpose in [
            layer_purpose_hazard, layer_purpose_exposure]:
            subcategory = self.parent.step_kw_subcategory.\
                selected_subcategory()
            if layer_mode == layer_mode_classified:
                if get_classifications(subcategory['key']):
                    new_step = self.parent.step_kw_classification
                else:  # No classifications
                    if is_raster_layer(self.parent.layer):
                        new_step = self.parent.step_kw_source
                    else:  # Vector
                        new_step = self.parent.step_kw_field

            elif layer_mode == layer_mode_continuous:
                if (subcategory.get('units') or
                        subcategory.get('continuous_hazard_units')):
                    new_step = self.parent.step_kw_unit
                else:  # Continuous but no unit
                    if get_classifications(subcategory['key']):
                        new_step = self.parent.step_kw_classification
                    else:  # Continuous, no unit, no classification
                        if is_raster_layer(self.parent.layer):
                            new_step = self.parent.step_kw_source
                        else:  # Vector
                            new_step = self.parent.step_kw_field
            else:
                message = tr('Layer mode should be continuous or classified')
                raise InvalidWizardStep(message)
        else:
            message = tr('Layer purpose should be hazard or exposure')
            raise InvalidWizardStep(message)

        return new_step

    # noinspection PyPep8Naming
    def on_lstLayerModes_itemSelectionChanged(self):
        """Update layer mode description label and unit widgets.

        .. note:: This is an automatic Qt slot
           executed when the subcategory selection changes.
        """
        self.clear_further_steps()
        # Set widgets
        layer_mode = self.selected_layermode()
        # Exit if no selection
        if not layer_mode:
            self.lblDescribeLayerMode.setText('')
            return
        # Set description label
        self.lblDescribeLayerMode.setText(layer_mode['description'])
        # Enable the next button
        self.parent.pbnNext.setEnabled(True)

    def selected_layermode(self):
        """Obtain the layer mode selected by user.
        :returns: selected layer mode.
        :rtype: string, None
        """
        item = self.lstLayerModes.currentItem()
        try:
            return definition(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def clear_further_steps(self):
        """ Clear all further steps
            in order to properly calculate the prev step
        """
        self.parent.step_kw_unit.lstUnits.clear()
        self.parent.step_kw_field.lstFields.clear()
        self.parent.step_kw_classification.lstClassifications.clear()

    def set_widgets(self):
        """Set widgets on the LayerMode tab."""
        self.clear_further_steps()
        # Set widgets
        purpose = self.parent.step_kw_purpose.selected_purpose()
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        layer_mode_question = (
            layer_mode_raster_question
            if is_raster_layer(self.parent.layer)
            else layer_mode_vector_question)

        self.lblDescribeLayerMode.setText('')
        self.lstLayerModes.clear()
        layer_modes = get_layer_modes(subcategory['key'])
        if is_raster_layer(self.parent.layer):
            layer_mode_question = layer_mode_raster_question
        else:
            if len(layer_modes) == 2:
                layer_mode_question = layer_mode_vector_question
            elif len(layer_modes) == 1:
                if layer_modes[0]['key'] == 'classified':
                    layer_mode_question = layer_mode_vector_classified_confirm
                elif layer_modes[0]['key'] == 'continuous':
                    layer_mode_question = layer_mode_vector_continuous_confirm
                else:
                    layer_mode_question = layer_mode_vector_question
        self.lblSelectLayerMode.setText(
            layer_mode_question % (subcategory['name'], purpose['name']))
        for layer_mode in layer_modes:
            item = QListWidgetItem(layer_mode['name'], self.lstLayerModes)
            item.setData(QtCore.Qt.UserRole, layer_mode['key'])
            self.lstLayerModes.addItem(item)

        # Set value to existing keyword or default value
        layer_mode_keys = [m['key'] for m in layer_modes]
        layermode_keyword = self.parent.get_existing_keyword('layer_mode')
        if layermode_keyword in layer_mode_keys:
            indx = layer_mode_keys.index(layermode_keyword)
        elif layer_mode_continuous['key'] in layer_mode_keys:
            # Set default value
            indx = layer_mode_keys.index(layer_mode_continuous['key'])
        else:
            indx = -1
        self.lstLayerModes.setCurrentRow(indx)

        self.auto_select_one_item(self.lstLayerModes)
