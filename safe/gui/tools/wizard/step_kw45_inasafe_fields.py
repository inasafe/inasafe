# coding=utf-8
"""InaSAFE Wizard Step InaSAFE Fields."""


# noinspection PyPackageRequirements
import logging

from parameters.qt_widgets.parameter_container import ParameterContainer
from parameters.select_parameter import SelectParameter
from safe import messaging as m
from safe.definitions.constants import no_field
from safe.definitions.layer_geometry import layer_geometry_raster
from safe.definitions.layer_purposes import (layer_purpose_aggregation)
from safe.definitions.utilities import get_fields, get_compulsory_fields
from safe.gui.tools.wizard.wizard_step import (
    WizardStep, get_wizard_step_ui_class)
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)
LOGGER = logging.getLogger('InaSAFE')


class StepKwInaSAFEFields(WizardStep, FORM_CLASS):

    """InaSAFE Wizard Step InaSAFE Fields."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizard Dialog).
        :type parent: QWidget

        """
        WizardStep.__init__(self, parent)

        self.parameters = []
        self.parameter_container = ParameterContainer()
        self.kwExtraKeywordsGridLayout.addWidget(self.parameter_container)

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return True

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        layer_purpose = self.parent.step_kw_purpose.selected_purpose()
        if layer_purpose['key'] != layer_purpose_aggregation['key']:
            subcategory = self.parent.step_kw_subcategory. \
                selected_subcategory()
        else:
            subcategory = {'key': None}

        # We don't use field mapping for populated place exposure. Use the
        # population point instead.

        # inasafe_fields = self.get_inasafe_fields()
        # If population field is set, must go to field mapping step first.
        # if population_count_field['key'] in inasafe_fields.keys():
        #     return self.parent.step_kw_fields_mapping

        # Check if it can go to inasafe default field step
        default_inasafe_fields = get_fields(
            layer_purpose['key'],
            subcategory['key'],
            replace_null=True,
            in_group=False)
        if default_inasafe_fields:
            return self.parent.step_kw_default_inasafe_fields

        # Any other case
        return self.parent.step_kw_source

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
        # Get all fields with replace_null = False
        inasafe_fields = get_fields(
            layer_purpose_key,
            subcategory_key,
            replace_null=False,
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
        existing_inasafe_field = self.parent.get_existing_keyword(
            'inasafe_fields')
        # Remove old container and parameter
        if self.parameter_container:
            self.kwExtraKeywordsGridLayout.removeWidget(
                self.parameter_container)
        if self.parameters:
            self.parameters = []

        # Iterate through all inasafe fields
        for inasafe_field in self.inasafe_fields_for_the_layer():
            # Option for Not Available
            option_list = [no_field]
            for field in self.parent.layer.fields():
                # Check the field type
                if isinstance(inasafe_field['type'], list):
                    if field.type() in inasafe_field['type']:
                        field_name = field.name()
                        option_list.append('%s' % field_name)
                else:
                    if field.type() == inasafe_field['type']:
                        field_name = field.name()
                        option_list.append('%s' % field_name)

            # If there is no option, pass
            if option_list == [no_field]:
                continue

            # Create SelectParameter
            select_parameter = SelectParameter()
            select_parameter.guid = inasafe_field['key']
            select_parameter.name = inasafe_field['name']
            select_parameter.is_required = False
            select_parameter.description = inasafe_field['description']
            select_parameter.help_text = inasafe_field['help_text']
            select_parameter.element_type = str
            select_parameter.options_list = option_list
            select_parameter.value = no_field
            # Check if there is already value in the metadata.
            if existing_inasafe_field:
                existing_value = existing_inasafe_field.get(
                    inasafe_field['key'])
                if existing_value:
                    if existing_value in select_parameter.options_list:
                        select_parameter.value = existing_value

            self.parameters.append(select_parameter)

        # Create the parameter container and add to the wizard.
        self.parameter_container = ParameterContainer(self.parameters)
        self.parameter_container.setup_ui()
        self.kwExtraKeywordsGridLayout.addWidget(self.parameter_container)

        if not self.parameters:
            no_field_message = tr(
                'There is no available field that has match type for the '
                'InaSAFE fields. You can click next.')
            self.lblInaSAFEFields.setText(no_field_message)

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

    def clear(self):
        """Clear current state."""
        # Adapted from http://stackoverflow.com/a/13103617/1198772
        for i in reversed(list(range(self.kwExtraKeywordsGridLayout.count()))):
            self.kwExtraKeywordsGridLayout.itemAt(i).widget().setParent(None)
        self.parameters = []
        self.parameter_container = ParameterContainer()

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return tr('InaSAFE Field Step')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you will be able to '
            'set a field that corresponded with a InaSAFE field '
            'concept.').format(step_name=self.step_name)))
        return message
