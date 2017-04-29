# coding=utf-8
"""InaSAFE Keyword Wizard Multi Fields Step."""

import re
import logging

from PyQt4 import QtCore
from PyQt4.QtGui import QListWidgetItem, QAbstractItemView

from safe.utilities.i18n import tr
from safe.definitions.layer_purposes import (
    layer_purpose_aggregation, layer_purpose_hazard, layer_purpose_exposure)
from safe.definitions.layer_modes import layer_mode_continuous
from safe.gui.tools.wizard.wizard_step import (
    WizardStep, get_wizard_step_ui_class)
from safe.gui.tools.wizard.wizard_strings import (
    field_question_subcategory_unit,
    field_question_subcategory_classified,
    field_question_aggregation)
from safe.gui.tools.wizard.wizard_utils import (
    get_question_text, skip_inasafe_field)
from safe.definitions.utilities import get_fields, get_non_compulsory_fields
from safe.definitions.fields import population_count_field
from safe.gui.widgets.field_mapping_widget import FieldMappingWidget
from safe.definitions.utilities import get_field_groups

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)
LOGGER = logging.getLogger('InaSAFE')


SINGLE_MODE = 'single'
MULTI_MODE = 'multi'


class StepKwFieldsMapping(WizardStep, FORM_CLASS):

    """InaSAFE Keyword Wizard Field Mapping Step."""

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
            elif layer_purpose == layer_purpose_exposure:
                return self.parent.step_kw_classification

        # Check if it can go to inasafe field step
        non_compulsory_fields = get_non_compulsory_fields(
            layer_purpose['key'], subcategory['key'])
        if not skip_inasafe_field(self.parent.layer, non_compulsory_fields):
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

    def clear_further_steps(self):
        """Clear all further steps to re-init widget."""
        # self.parent.step_kw_classify.treeClasses.clear()
        pass

    def set_widgets(self):
        """Set widgets on the Field Mapping step."""
        self.clear_further_steps()

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
        """Obtain field mapping from the current state."""
        field_mapping = self.field_mapping_widget.get_field_mapping()
        for k, v in field_mapping['values'].items():
            if not v:
                field_mapping['values'].pop(k)
        return field_mapping
