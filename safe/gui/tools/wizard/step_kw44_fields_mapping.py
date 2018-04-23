# coding=utf-8
"""InaSAFE Wizard Step Multi Fields."""

import logging

from parameters.parameter_exceptions import InvalidValidationException
from safe import messaging as m
from safe.definitions.layer_purposes import (
    layer_purpose_aggregation, layer_purpose_hazard, layer_purpose_exposure)
from safe.definitions.utilities import get_fields, get_non_compulsory_fields
from safe.gui.tools.help.field_mapping_help import field_mapping_help_content
from safe.gui.tools.wizard.utilities import skip_inasafe_field
from safe.gui.tools.wizard.wizard_step import (
    WizardStep, get_wizard_step_ui_class)
from safe.gui.widgets.field_mapping_widget import FieldMappingWidget
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)
LOGGER = logging.getLogger('InaSAFE')


class StepKwFieldsMapping(WizardStep, FORM_CLASS):

    """InaSAFE Wizard Step Multi Fields."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: widget to use as parent (Wizard Dialog).
        :type parent: QWidget
        """
        WizardStep.__init__(self, parent)
        self.field_mapping_widget = FieldMappingWidget(self, self.parent.iface)

    def is_ready_to_next_step(self):
        """Check if the step is complete.

        If so, there is no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        try:
            self.get_field_mapping()
        except InvalidValidationException:
            return False
        return True

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep
        """
        layer_purpose = self.parent.step_kw_purpose.selected_purpose()
        if layer_purpose != layer_purpose_aggregation:
            subcategory = self.parent.step_kw_subcategory.\
                selected_subcategory()
        else:
            subcategory = {'key': None}

        # Has classifications, go to multi classifications
        if subcategory.get('classifications'):
            if layer_purpose == layer_purpose_hazard:
                return self.parent.step_kw_multi_classifications

        # Check if it can go to inasafe field step
        non_compulsory_fields = get_non_compulsory_fields(
            layer_purpose['key'], subcategory['key'])
        if not skip_inasafe_field(self.parent.layer, non_compulsory_fields):
            # Do not go to InaSAFE Field step if we already visited it.
            # For example in place exposure.
            if (self.parent.step_kw_inasafe_fields not in
                    self.parent.keyword_steps):
                return self.parent.step_kw_inasafe_fields

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

    def set_widgets(self):
        """Set widgets on the Field Mapping step."""
        on_the_fly_metadata = {}
        layer_purpose = self.parent.step_kw_purpose.selected_purpose()
        on_the_fly_metadata['layer_purpose'] = layer_purpose['key']
        if layer_purpose != layer_purpose_aggregation:
            subcategory = self.parent.step_kw_subcategory.\
                selected_subcategory()
            if layer_purpose == layer_purpose_exposure:
                on_the_fly_metadata['exposure'] = subcategory['key']
            if layer_purpose == layer_purpose_hazard:
                on_the_fly_metadata['hazard'] = subcategory['key']
        inasafe_fields = self.parent.get_existing_keyword(
            'inasafe_fields')
        inasafe_default_values = self.parent.get_existing_keyword(
            'inasafe_default_values')
        on_the_fly_metadata['inasafe_fields'] = inasafe_fields
        on_the_fly_metadata['inasafe_default_values'] = inasafe_default_values
        self.field_mapping_widget.set_layer(
            self.parent.layer, on_the_fly_metadata)
        self.field_mapping_widget.show()
        self.main_layout.addWidget(self.field_mapping_widget)

    def get_field_mapping(self):
        """Obtain metadata from current state of the widget.

        Null or empty list will be removed.

        :returns: Dictionary of values by type in this format:
            {'fields': {}, 'values': {}}.
        :rtype: dict
        """
        field_mapping = self.field_mapping_widget.get_field_mapping()
        for k, v in list(field_mapping['values'].items()):
            if not v:
                field_mapping['values'].pop(k)
        for k, v in list(field_mapping['fields'].items()):
            if not v:
                field_mapping['fields'].pop(k)
        return field_mapping

    def clear(self):
        """Helper to clear the state of the step."""
        self.field_mapping_widget.delete_tabs()

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return tr('Field Mapping Step')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you will be able to define '
            'field mappings to use for demographic breakdowns of your '
            'analysis results.').format(step_name=self.step_name)))
        message.add(field_mapping_help_content())
        return message
