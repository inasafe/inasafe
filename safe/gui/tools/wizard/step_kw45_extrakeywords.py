# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Keyword Wizard Step: Extra Keywords

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

# noinspection PyPackageRequirements
from PyQt4 import QtCore

from safe.definitionsv4.definitions_v3 import \
    layer_mode_classified, layer_purpose_hazard, exposure_place
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class


FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwExtraKeywords(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Extra Keywords"""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizad Dialog).
        :type parent: QWidget

        """
        WizardStep.__init__(self, parent)
        # Collect some serial widgets
        self.extra_keywords_widgets = [
            {'cbo': self.cboExtraKeyword1, 'lbl': self.lblExtraKeyword1},
            {'cbo': self.cboExtraKeyword2, 'lbl': self.lblExtraKeyword2},
            {'cbo': self.cboExtraKeyword3, 'lbl': self.lblExtraKeyword3},
            {'cbo': self.cboExtraKeyword4, 'lbl': self.lblExtraKeyword4},
            {'cbo': self.cboExtraKeyword5, 'lbl': self.lblExtraKeyword5},
            {'cbo': self.cboExtraKeyword6, 'lbl': self.lblExtraKeyword6},
            {'cbo': self.cboExtraKeyword7, 'lbl': self.lblExtraKeyword7},
            {'cbo': self.cboExtraKeyword8, 'lbl': self.lblExtraKeyword8}
        ]
        for ekw in self.extra_keywords_widgets:
            ekw['key'] = None
            ekw['slave_key'] = None

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return self.are_all_extra_keywords_selected()

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
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

    def additional_keywords_for_the_layer(self):
        """Return a list of valid additional keywords for the current layer.

        :returns: A list where each value represents a valid additional kw.
        :rtype: list
        """
        layer_geometry_key = self.parent.get_layer_geometry_id()
        layer_mode_key = self.parent.step_kw_layermode.\
            selected_layermode()['key']
        if self.parent.step_kw_purpose.\
                selected_purpose() == layer_purpose_hazard:
            hazard_category_key = self.parent.step_kw_hazard_category.\
                selected_hazard_category()['key']
            hazard_key = self.parent.step_kw_subcategory.\
                selected_subcategory()['key']
            return self.impact_function_manager.hazard_additional_keywords(
                layer_mode_key, layer_geometry_key,
                hazard_category_key, hazard_key)
        else:
            exposure_key = self.parent.step_kw_subcategory.\
                selected_subcategory()['key']
            return self.impact_function_manager.exposure_additional_keywords(
                layer_mode_key, layer_geometry_key, exposure_key)

    # noinspection PyPep8Naming
    def on_cboExtraKeyword1_currentIndexChanged(self, indx):
        """This is an automatic Qt slot executed when the
           1st extra keyword combobox selection changes.

        :param indx: The new index.
        :type indx: int or str
        """
        if isinstance(indx, int) and indx > -1:
            self.extra_keyword_changed(self.extra_keywords_widgets[0])

    # noinspection PyPep8Naming
    def on_cboExtraKeyword2_currentIndexChanged(self, indx):
        """This is an automatic Qt slot executed when the
           2nd extra keyword combobox selection changes.

        :param indx: The new index.
        :type indx: int or str
        """
        if isinstance(indx, int) and indx > -1:
            self.extra_keyword_changed(self.extra_keywords_widgets[1])

    # noinspection PyPep8Naming
    def on_cboExtraKeyword3_currentIndexChanged(self, indx):
        """This is an automatic Qt slot executed when the
           3rd extra keyword combobox selection changes.

        :param indx: The new index.
        :type indx: int or str
        """
        if isinstance(indx, int) and indx > -1:
            self.extra_keyword_changed(self.extra_keywords_widgets[2])

    # noinspection PyPep8Naming
    def on_cboExtraKeyword4_currentIndexChanged(self, indx):
        """This is an automatic Qt slot executed when the
           4th extra keyword combobox selection changes.

        :param indx: The new index.
        :type indx: int or str
        """
        if isinstance(indx, int) and indx > -1:
            self.extra_keyword_changed(self.extra_keywords_widgets[3])

    # noinspection PyPep8Naming
    def on_cboExtraKeyword5_currentIndexChanged(self, indx):
        """This is an automatic Qt slot executed when the
           5th extra keyword combobox selection changes.

        :param indx: The new index.
        :type indx: int or str
        """
        if isinstance(indx, int) and indx > -1:
            self.extra_keyword_changed(self.extra_keywords_widgets[4])

    # noinspection PyPep8Naming
    def on_cboExtraKeyword6_currentIndexChanged(self, indx):
        """This is an automatic Qt slot executed when the
           6th extra keyword combobox selection changes.

        :param indx: The new index.
        :type indx: int or str
        """
        if isinstance(indx, int) and indx > -1:
            self.extra_keyword_changed(self.extra_keywords_widgets[5])

    # noinspection PyPep8Naming
    def on_cboExtraKeyword7_currentIndexChanged(self, indx):
        """This is an automatic Qt slot executed when the
           7th extra keyword combobox selection changes.

        :param indx: The new index.
        :type indx: int or str
        """
        if isinstance(indx, int) and indx > -1:
            self.extra_keyword_changed(self.extra_keywords_widgets[6])

    # noinspection PyPep8Naming
    def on_cboExtraKeyword8_currentIndexChanged(self, indx):
        """This is an automatic Qt slot executed when the
           8th extra keyword combobox selection changes.

        :param indx: The new index.
        :type indx: int or str
        """
        if isinstance(indx, int) and indx > -1:
            self.extra_keyword_changed(self.extra_keywords_widgets[7])

    def extra_keyword_changed(self, widget):
        """Populate slave widget if exists and enable the Next button
           if all extra keywords are set.

        :param widget: Metadata of the widget where the event happened.
        :type widget: dict
        """
        if 'slave_key' in widget and widget['slave_key']:
            for w in self.extra_keywords_widgets:
                if w['key'] == widget['slave_key']:
                    field_name = widget['cbo'].itemData(
                        widget['cbo'].currentIndex(), QtCore.Qt.UserRole)
                    self.populate_value_widget_from_field(w['cbo'], field_name)

        self.parent.pbnNext.setEnabled(self.are_all_extra_keywords_selected())

    def selected_extra_keywords(self):
        """Obtain the extra keywords selected by user.

        :returns: Metadata of the extra keywords.
        :rtype: dict, None
        """
        extra_keywords = {}
        for ekw in self.extra_keywords_widgets:
            if ekw['key'] is not None and ekw['cbo'].currentIndex() != -1:
                key = ekw['key']
                val = ekw['cbo'].itemData(ekw['cbo'].currentIndex(),
                                          QtCore.Qt.UserRole)
                extra_keywords[key] = val
        return extra_keywords

    def are_all_extra_keywords_selected(self):
        """Ensure all all additional keyword are set by user

        :returns: True if all additional keyword widgets are set
        :rtype: boolean
        """
        for ekw in self.extra_keywords_widgets:
            if ekw['key'] is not None and ekw['cbo'].currentIndex() == -1:
                return False
        return True

    def populate_value_widget_from_field(self, widget, field_name):
        """Populate the slave widget with unique values of the field
           selected in the master widget.

        :param widget: The widget to be populated
        :type widget: QComboBox

        :param field_name: Name of the field to take the values from
        :type field_name: str
        """
        fields = self.parent.layer.dataProvider().fields()
        field_index = fields.indexFromName(field_name)
        widget.clear()
        for v in self.parent.layer.uniqueValues(field_index):
            widget.addItem(unicode(v), unicode(v))
        widget.setCurrentIndex(-1)

    def set_widgets(self):
        """Set widgets on the Extra Keywords tab."""
        # Hide all widgets

        for ekw in self.extra_keywords_widgets:
            ekw['cbo'].clear()
            ekw['cbo'].hide()
            ekw['lbl'].hide()
            ekw['key'] = None
            ekw['master_key'] = None

        # Set and show used widgets
        extra_keywords = self.additional_keywords_for_the_layer()
        for i in range(len(extra_keywords)):
            extra_keyword = extra_keywords[i]
            extra_keywords_widget = self.extra_keywords_widgets[i]
            extra_keywords_widget['key'] = extra_keyword['key']
            extra_keywords_widget['lbl'].setText(extra_keyword['description'])
            if extra_keyword['type'] == 'value':
                field_widget = self.extra_keywords_widgets[i - 1]['cbo']
                field_name = field_widget.itemData(
                    field_widget.currentIndex(), QtCore.Qt.UserRole)
                self.populate_value_widget_from_field(
                    extra_keywords_widget['cbo'], field_name)
            else:
                for field in self.parent.layer.dataProvider().fields():
                    field_name = field.name()
                    field_type = field.typeName()
                    extra_keywords_widget['cbo'].addItem('%s (%s)' % (
                        field_name, field_type), field_name)
            # If there is a master keyword, attach this widget as a slave
            # to the master widget. It's used for values of a given field.
            if ('master_keyword' in extra_keyword and
                    extra_keyword['master_keyword']):
                master_key = extra_keyword['master_keyword']['key']
                for master_candidate in self.extra_keywords_widgets:
                    if master_candidate['key'] == master_key:
                        master_candidate['slave_key'] = extra_keyword['key']
            # Show the widget
            extra_keywords_widget['cbo'].setCurrentIndex(-1)
            extra_keywords_widget['lbl'].show()
            extra_keywords_widget['cbo'].show()

        # Set values based on existing keywords (if already assigned)
        for ekw in self.extra_keywords_widgets:
            if not ekw['key']:
                continue
            value = self.parent.get_existing_keyword(ekw['key'])
            indx = ekw['cbo'].findData(value, QtCore.Qt.UserRole)
            if indx != -1:
                ekw['cbo'].setCurrentIndex(indx)
