# coding=utf-8
"""InaSAFE Wizard Step Layer Mode."""

# noinspection PyPackageRequirements
from qgis.PyQt import QtCore
from qgis.PyQt.QtWidgets import QListWidgetItem

from safe import messaging as m
from safe.common.exceptions import InvalidWizardStep
from safe.definitions.layer_modes import layer_mode_continuous
from safe.definitions.utilities import definition, get_layer_modes
from safe.gui.tools.wizard.wizard_step import (
    get_wizard_step_ui_class, WizardStep)
from safe.gui.tools.wizard.wizard_strings import (
    layer_mode_raster_question,
    layer_mode_vector_question,
    layer_mode_vector_classified_confirm,
    layer_mode_vector_continuous_confirm)
from safe.utilities.gis import is_raster_layer
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwLayerMode(WizardStep, FORM_CLASS):

    """InaSAFE Wizard Step Layer Mode."""

    def is_ready_to_next_step(self):
        """Check if the step is complete.

        If so, there is no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.selected_layermode())

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        is_raster = is_raster_layer(self.parent.layer)
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        has_unit = subcategory.get('units') or subcategory.get(
            'continuous_hazard_units')
        selected_layer_mode = self.selected_layermode()

        # continuous
        if selected_layer_mode == layer_mode_continuous and has_unit:
            new_step = self.parent.step_kw_unit
        # no unit and vector
        elif not is_raster:
            new_step = self.parent.step_kw_field
        # no unit and raster
        elif is_raster:
            new_step = self.parent.step_kw_multi_classifications
        else:
            raise InvalidWizardStep

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
        """Clear all further steps in order to properly calculate the prev step
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
        layer_mode_keyword = self.parent.get_existing_keyword('layer_mode')
        if layer_mode_keyword in layer_mode_keys:
            index = layer_mode_keys.index(layer_mode_keyword)
        elif layer_mode_continuous['key'] in layer_mode_keys:
            # Set default value
            index = layer_mode_keys.index(layer_mode_continuous['key'])
        else:
            index = -1
        self.lstLayerModes.setCurrentRow(index)

        self.auto_select_one_item(self.lstLayerModes)

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return tr('Layer Mode Step')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you will be able to set the '
            'mode of the layer that is being assigned in this wizard.'
        ).format(step_name=self.step_name)))
        return message
