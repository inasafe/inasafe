# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Keyword Wizard Step: Field

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'qgis@borysjurgiel.pl'
__revision__ = '$Format:%H$'
__date__ = '16/03/2016'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import re

from PyQt4 import QtCore
from PyQt4.QtGui import QListWidgetItem

from safe.definitionsv4.layer_purposes import layer_purpose_aggregation
from safe.definitionsv4.layer_modes import (
    layer_mode_continuous, layer_mode_classified)
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_strings import (
    field_question_subcategory_unit,
    field_question_subcategory_classified,
    field_question_aggregation)
from safe.gui.tools.wizard.wizard_utils import get_question_text
from safe.utilities.gis import is_raster_layer
from safe.definitionsv4.utilities import get_fields

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwField(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Field"""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.selected_field() or not self.lstFields.count())

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        if self.parent.step_kw_layermode.\
                selected_layermode() == layer_mode_classified:
            if self.parent.step_kw_classification.\
                    classifications_for_layer():
                # Classified data
                return self.parent.step_kw_classify

        if self.parent.step_kw_layermode. \
                selected_layermode() == layer_mode_continuous:
            if self.parent.step_kw_classification. \
                    classifications_for_layer():
                return self.parent.step_kw_threshold

        layer_purpose = self.parent.step_kw_purpose.selected_purpose()
        if layer_purpose['key'] != layer_purpose_aggregation['key']:
            subcategory = self.parent.step_kw_subcategory.\
                selected_subcategory()
        else:
            subcategory = {'key': None}

        # Check if it can go to inasafe field step
        inasafe_fields = get_fields(
            layer_purpose['key'], subcategory['key'], replace_null=False)
        if inasafe_fields:
            return self.parent.step_kw_inasafe_fields

        # Check if it can go to inasafe default field step
        default_inasafe_fields = get_fields(
            layer_purpose['key'], subcategory['key'], replace_null=True)
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
        """ Clear all further steps
            in order to properly calculate the prev step
        """
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
            # unique values, continuous or categorical data
            subcategory_unit_relation = get_question_text(
                '%s_%s_question' % (subcategory['key'], unit['key']))
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
