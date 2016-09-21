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

# noinspection PyPackageRequirements
from PyQt4 import QtCore
from PyQt4.QtGui import QListWidgetItem

from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_strings import field_question_name_field
from safe.utilities.gis import is_raster_layer

__author__ = 'etienne@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '16/03/2016'
__copyright__ = (
    'Copyright 2012, Australia Indonesia Facility for Disaster Reduction')


FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwNameField(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Population Field for populated places."""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return True if self.selected_field() else False

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        return self.parent.step_kw_classify

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_kw_population_field
        return new_step

    # noinspection PyPep8Naming
    def on_lstFields_itemSelectionChanged(self):
        """Update field description label and unlock the Next button.

        .. note:: This is an automatic Qt slot
           executed when the field selection changes.
        """
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

    def set_widgets(self):
        """Set widgets on the Field tab."""
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        unit = self.parent.step_kw_unit.selected_unit()
        question_text = field_question_name_field % (subcategory['name'])
        self.lblSelectField.setText(question_text)
        self.lstFields.clear()
        default_item = None
        type_field = self.parent.step_kw_field.selected_field()
        for field in self.parent.layer.dataProvider().fields():
            field_name = field.name()
            if type_field != field_name:
                # We do not use a field already used in the wizard before.
                item = QListWidgetItem(field_name, self.lstFields)
                item.setData(QtCore.Qt.UserRole, field_name)
                # Select the item if it match the unit's default_attribute
                if unit and 'default_attribute' in unit \
                        and field_name == unit['default_attribute']:
                    default_item = item
        if default_item:
            self.lstFields.setCurrentItem(default_item)
        self.lblDescribeField.clear()

        # Set values based on existing keywords (if already assigned)
        field_keyword = self.parent.field_keyword_for_the_layer()
        field = self.parent.get_existing_keyword(field_keyword)
        if field:
            fields = []
            for index in xrange(self.lstFields.count()):
                fields.append(str(self.lstFields.item(index).text()))
            if field in fields:
                self.lstFields.setCurrentRow(fields.index(field))
        self.auto_select_one_item(self.lstFields)
