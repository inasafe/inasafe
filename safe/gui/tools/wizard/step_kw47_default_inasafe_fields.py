# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Keyword Wizard Step: Default InaSAFE Fields

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

# noinspection PyPackageRequirements
import logging
from PyQt4.QtGui import QWidget

from safe.common.parameters.default_select_parameter import (
    DefaultSelectParameter)
from safe.common.parameters.default_select_parameter_widget import (
    DefaultSelectParameterWidget)
from safe_extras.parameters.qt_widgets.parameter_container import (
    ParameterContainer)

from safe.definitionsv4.layer_purposes import (layer_purpose_aggregation)
from safe.definitionsv4.layer_modes import layer_mode_classified
from safe.definitionsv4.exposure import exposure_place
from safe.definitionsv4.utilities import get_fields, get_class_field
from safe.definitionsv4.layer_geometry import layer_geometry_raster
from safe.definitionsv4.constants import no_field
from safe.definitionsv4.utilities import get_defaults

from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)
LOGGER = logging.getLogger('InaSAFE')


class StepKwDefaultInaSAFEFields(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Default InaSAFE Fields"""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizard Dialog).
        :type parent: QWidget

        """
        WizardStep.__init__(self, parent)

        self.extra_parameters = [
            (DefaultSelectParameter, DefaultSelectParameterWidget)
        ]
        self.parameters = []
        self.parameter_container = ParameterContainer(
            extra_parameters=self.extra_parameters)
        self.kwExtraKeywordsGridLayout.addWidget(self.parameter_container)

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return True

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        # Get hazard or exposure value
        layer_purpose_key = self.parent.step_kw_purpose.selected_purpose()[
            'key']
        if layer_purpose_key != layer_purpose_aggregation['key']:
            subcategory_key = self.parent.step_kw_subcategory. \
                selected_subcategory()['key']
        else:
            subcategory_key = None
        # Check if InaSAFE fields with replace_null = False has element
        inasafe_fields = get_fields(
            layer_purpose_key, subcategory_key, replace_null=False)
        if inasafe_fields:
            new_step = self.parent.step_kw_inasafe_fields
            return new_step

        selected_subcategory = self.parent.step_kw_subcategory.\
            selected_subcategory()
        if selected_subcategory == exposure_place:
            new_step = self.parent.step_kw_name_field
        elif self.parent.step_kw_layermode.\
                selected_layermode() == layer_mode_classified:
            if self.parent.step_kw_classification.selected_classification() \
                    or self.parent.step_kw_classify.\
                    postprocessor_classification_for_layer():
                new_step = self.parent.step_kw_classify
            elif self.parent.step_kw_field.selected_field():
                new_step = self.parent.step_kw_field
            else:
                new_step = self.parent.step_kw_layermode
        else:
            if self.parent.step_kw_resample.\
                    selected_allowresampling() is not None:
                new_step = self.parent.step_kw_resample
            else:
                new_step = self.parent.step_kw_unit
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_kw_source
        return new_step

    def inasafe_fields_for_the_layer(self):
        """Return a list of inasafe fields the current layer.

        :returns: A list where each value represents inasafe field.
        :rtype: list
        """
        if (self.parent.get_layer_geometry_key() ==
                layer_geometry_raster['key']):
            return []
        # Get hazard or exposure value
        layer_purpose_key = self.parent.step_kw_purpose.selected_purpose()[
            'key']
        if layer_purpose_key != layer_purpose_aggregation['key']:
            subcategory_key = self.parent.step_kw_subcategory.\
                selected_subcategory()['key']
        else:
            subcategory_key = None
        # Get all fields with replace_null = True
        inasafe_fields = get_fields(
            layer_purpose_key, subcategory_key, replace_null=True)
        # Remove the field for value map since it's already selected in
        # Field step
        try:
            inasafe_fields.remove(get_class_field(layer_purpose_key))
        except ValueError:
            pass
        return inasafe_fields

    # noinspection PyTypeChecker
    def set_widgets(self):
        """Set widgets on the Extra Keywords tab."""
        existing_inasafe_field = self.parent.get_existing_keyword(
            'inasafe_fields')
        # Remove old container and parameter
        if self.parameter_container:
            self.kwExtraKeywordsGridLayout.removeWidget(
                self.parameter_container)
        if self.parameters:
            self.parameters = []

        layer_data_provider = self.parent.layer.dataProvider()

        # Iterate through all inasafe fields
        for inasafe_field in self.inasafe_fields_for_the_layer():
            # Option for Not Available
            option_list = [no_field]
            for field in layer_data_provider.fields():
                # Check the field type
                if isinstance(inasafe_field['type'], list):
                    if field.type() in inasafe_field['type']:
                        field_name = field.name()
                        option_list.append('%s' % field_name)
                else:
                    if field.type() == inasafe_field['type']:
                        field_name = field.name()
                        option_list.append('%s' % field_name)

            # Create DefaultSelectParameter
            parameter = DefaultSelectParameter()
            parameter.guid = inasafe_field['key']
            parameter.name = inasafe_field['name']
            parameter.is_required = False
            parameter.help_text = inasafe_field['description']
            parameter.description = inasafe_field['description']
            parameter.element_type = unicode
            parameter.options_list = option_list
            parameter.value = no_field
            parameter.default_labels = get_defaults(inasafe_field['key'])[0]
            parameter.default_values = get_defaults(inasafe_field['key'])[1]
            # Check if there is already value in the metadata.
            if existing_inasafe_field:
                existing_value = existing_inasafe_field.get(
                    inasafe_field['key'])
                if existing_value:
                    parameter.value = existing_value

            self.parameters.append(parameter)

        # Create the parameter container and add to the wizard.
        self.parameter_container = ParameterContainer(
            self.parameters, extra_parameters=self.extra_parameters)
        self.parameter_container.setup_ui()
        self.kwExtraKeywordsGridLayout.addWidget(self.parameter_container)

    def get_inasafe_fields(self):
        """Return inasafe fields from the current wizard state.

        :returns: Dictionary of key and value from InaSAFE Fields.
        :rtype: dict
        """
        inasafe_fields = {}
        parameters = self.parameter_container.get_parameters(True)
        for parameter in parameters:
            if not parameter.value == no_field:
                inasafe_fields[parameter.guid] = parameter.value

        return inasafe_fields
