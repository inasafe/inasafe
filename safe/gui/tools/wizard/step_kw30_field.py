# coding=utf-8
"""InaSAFE Keyword Wizard Field Step."""

import re
import logging

from PyQt4 import QtCore
from PyQt4.QtGui import QListWidgetItem

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
from safe.utilities.gis import is_raster_layer
from safe.definitions.utilities import get_fields, get_non_compulsory_fields

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)
LOGGER = logging.getLogger('InaSAFE')


class StepKwField(WizardStep, FORM_CLASS):
    """InaSAFE Keyword Wizard Field Step."""

    def is_ready_to_next_step(self):
        """Check if the step is complete.

        If so, there is no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        # Choose hazard / exposure / aggregation field is mandatory
        return bool(self.selected_field())

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

    # noinspection PyPep8Naming
    def on_lstFields_itemSelectionChanged(self):
        """Update field description label and unlock the Next button.

        .. note:: This is an automatic Qt slot
           executed when the field selection changes.
        """
        self.clear_further_steps()
        field = self.selected_field()
        # Exit if no selection
        if not field:
            return
        # Exit if the selected field comes from a previous wizard run (vector)
        if is_raster_layer(self.parent.layer):
            return
        fields = self.parent.layer.dataProvider().fields()
        field_index = fields.indexFromName(field)
        # Exit if the selected field comes from a previous wizard run
        if field_index < 0:
            return
        field_type = fields.field(field).typeName()
        field_index = fields.indexFromName(self.selected_field())
        unique_values = self.parent.layer.uniqueValues(field_index)[0:48]
        unique_values_str = [
            i is not None and unicode(i) or 'NULL'
            for i in unique_values]
        if unique_values != self.parent.layer.uniqueValues(field_index):
            unique_values_str += ['...']
        desc = '<br/>%s: %s<br/><br/>' % (self.tr('Field type'), field_type)
        desc += self.tr('Unique values: %s') % ', '.join(unique_values_str)
        self.lblDescribeField.setText(desc)
        # Enable the next buttonlayer_purpose_aggregation
        self.parent.pbnNext.setEnabled(True)

    def selected_field(self):
        """Obtain the field selected by user.

        :returns: Keyword of the selected field.
        :rtype: string, None
        """
        item = self.lstFields.currentItem()
        if item:
            return item.text()
        else:
            return None

    def clear_further_steps(self):
        """Clear all further steps to re-init widget."""
        self.parent.step_kw_classify.treeClasses.clear()

    def set_widgets(self):
        """Set widgets on the Field tab."""
        self.clear_further_steps()
        purpose = self.parent.step_kw_purpose.selected_purpose()
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        unit = self.parent.step_kw_unit.selected_unit()
        if purpose == layer_purpose_aggregation:
            question_text = field_question_aggregation
        elif self.parent.step_kw_layermode.\
                selected_layermode() == layer_mode_continuous and unit:
            subcategory_unit_relation = get_question_text(
                '%s_%s_question' % (subcategory['key'], unit['key']))
            if 'MISSING' in subcategory_unit_relation:
                subcategory_unit_relation = self.tr(
                    '{subcategory} in {unit} unit').format(
                    subcategory=subcategory['name'].lower(),
                    unit=unit['plural_name'])
            question_text = field_question_subcategory_unit % (
                purpose['name'],
                subcategory['name'],
                unit['name'],
                subcategory_unit_relation)
        else:
            question_text = field_question_subcategory_classified % (
                subcategory['name'])
        self.lblSelectField.setText(question_text)
        self.lstFields.clear()
        default_item = None
        for field in self.parent.layer.dataProvider().fields():
            field_name = field.name()
            item = QListWidgetItem(field_name, self.lstFields)
            item.setData(QtCore.Qt.UserRole, field_name)
            # Select the item if it match the unit's default_attribute
            if unit and 'default_attribute' in unit \
                    and field_name == unit['default_attribute']:
                default_item = item
            # For continuous data, gray out id, gid, fid and text fields
            if self.parent.step_kw_layermode.\
                    selected_layermode() == layer_mode_continuous and unit:
                field_type = field.type()
                if field_type > 9 or re.match(
                        '.{0,2}id$', field_name, re.I):
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
        if default_item:
            self.lstFields.setCurrentItem(default_item)
        self.lblDescribeField.clear()

        # Set values based on existing keywords (if already assigned)
        field_keyword = self.parent.field_keyword_for_the_layer()
        inasafe_field = self.parent.get_existing_keyword('inasafe_fields')
        if inasafe_field:
            field = inasafe_field.get(field_keyword)
            if field:
                fields = []
                for index in xrange(self.lstFields.count()):
                    fields.append(str(self.lstFields.item(index).text()))
                if field in fields:
                    self.lstFields.setCurrentRow(fields.index(field))
            self.auto_select_one_item(self.lstFields)
