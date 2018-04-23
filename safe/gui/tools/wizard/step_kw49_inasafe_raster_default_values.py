# coding=utf-8
"""InaSAFE Wizard Step InaSAFE Raster Default Fields."""


# noinspection PyPackageRequirements
import logging

from parameters.qt_widgets.parameter_container import ParameterContainer
from safe import messaging as m
from safe.common.parameters.default_value_parameter import (
    DefaultValueParameter)
from safe.common.parameters.default_value_parameter_widget import (
    DefaultValueParameterWidget)
from safe.definitions.layer_purposes import (layer_purpose_aggregation)
from safe.definitions.utilities import get_fields, get_compulsory_fields
from safe.gui.tools.wizard.utilities import get_inasafe_default_value_fields
from safe.gui.tools.wizard.wizard_step import (
    WizardStep, get_wizard_step_ui_class)
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)
LOGGER = logging.getLogger('InaSAFE')


class StepKwInaSAFERasterDefaultValues(WizardStep, FORM_CLASS):

    """InaSAFE Wizard Step InaSAFE Raster Default Fields."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizard Dialog).
        :type parent: QWidget
        """
        WizardStep.__init__(self, parent)

        self.extra_parameters = [
            (DefaultValueParameter, DefaultValueParameterWidget)
        ]
        self.parameters = []
        self.parameter_container = ParameterContainer(
            extra_parameters=self.extra_parameters)
        self.default_values_grid.addWidget(self.parameter_container)

    def is_ready_to_next_step(self):
        """Check if the step is complete.

        If so, there is no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return True

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
            layer_purpose_key,
            subcategory_key,
            replace_null=True,
            in_group=False)
        # remove compulsory field since it has been set in previous step
        try:
            inasafe_fields.remove(get_compulsory_fields(
                layer_purpose_key, subcategory_key))
        except ValueError:
            pass
        return inasafe_fields

    # noinspection PyTypeChecker
    def set_widgets(self):
        """Set widgets on the Extra Keywords tab."""
        existing_inasafe_default_values = self.parent.get_existing_keyword(
            'inasafe_default_values')
        # Remove old container and parameter
        if self.parameter_container:
            self.default_values_grid.removeWidget(
                self.parameter_container)
        if self.parameters:
            self.parameters = []

        # Iterate through all inasafe fields
        # existing_inasafe_default_values

        for inasafe_field in self.inasafe_fields_for_the_layer():
            # Create DefaultSelectParameter
            parameter = DefaultValueParameter()
            parameter.guid = inasafe_field['key']
            parameter.name = inasafe_field['name']
            parameter.is_required = False
            parameter.help_text = inasafe_field['default_value']['description']
            # parameter.description = inasafe_field['default_value']
            parameter.element_type = str
            parameter.labels = get_inasafe_default_value_fields(
                self.parent.setting, inasafe_field['key'])[0]
            parameter.options = get_inasafe_default_value_fields(
                self.parent.setting, inasafe_field['key'])[1]

            if existing_inasafe_default_values:
                existing_default_value = existing_inasafe_default_values.get(
                    inasafe_field['key'])
                if existing_default_value:
                    parameter.default = existing_default_value

            self.parameters.append(parameter)

        # Create the parameter container and add to the wizard.
        self.parameter_container = ParameterContainer(
            self.parameters, extra_parameters=self.extra_parameters)
        self.parameter_container.setup_ui()
        self.default_values_grid.addWidget(self.parameter_container)

        # Set default value to None
        for parameter_widget in self.parameter_container.\
                get_parameter_widgets():
            parameter_widget.widget().set_value(None)
        # Set default value from existing keywords
        if existing_inasafe_default_values:
            for guid, default in list(existing_inasafe_default_values.items()):
                parameter_widget = self.parameter_container.\
                    get_parameter_widget_by_guid(guid)
                if isinstance(parameter_widget, DefaultValueParameterWidget):
                    parameter_widget.set_value(default)

    def get_inasafe_default_values(self):
        """Return inasafe default from the current wizard state.

        :returns: Dictionary of key and value from InaSAFE Default Values.
        :rtype: dict
        """
        inasafe_default_values = {}
        parameters = self.parameter_container.get_parameters(True)
        for parameter in parameters:
            if parameter.value is not None:
                inasafe_default_values[parameter.guid] = parameter.value

        return inasafe_default_values

    def clear(self):
        """Clear current state."""
        # Adapted from http://stackoverflow.com/a/13103617/1198772
        for i in reversed(list(range(self.default_values_grid.count()))):
            self.default_values_grid.itemAt(i).widget().setParent(None)
        self.parameters = []
        self.parameter_container = ParameterContainer()

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you will be able to '
            'set a value that corresponded with a InaSAFE field '
            'concept as default value.').format(step_name=self.step_name)))
        return message
