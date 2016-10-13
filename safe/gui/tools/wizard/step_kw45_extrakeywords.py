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

# noinspection PyPackageRequirements
import logging
from PyQt4.QtGui import QWidget

from safe_extras.parameters.select_parameter import SelectParameter
from safe_extras.parameters.qt_widgets.parameter_container import (
    ParameterContainer)

from safe.definitionsv4.layer_modes import layer_mode_classified
from safe.definitionsv4.exposure import exposure_place
from safe.definitionsv4.utilities import get_fields
from safe.definitionsv4.layer_geometry import layer_geometry_raster
from safe.definitionsv4.constants import not_available
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class


__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


FORM_CLASS = get_wizard_step_ui_class(__file__)
LOGGER = logging.getLogger('InaSAFE')


class StepKwExtraKeywords(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Extra Keywords"""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizad Dialog).
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

    def inasafe_fields_for_the_layer(self):
        """Return a list of inasafe fields the current layer.

        :returns: A list where each value represents inasafe field.
        :rtype: list
        """
        if (self.parent.get_layer_geometry_key() ==
                layer_geometry_raster['key']):
            return []
        # Get hazard or exposure value
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        inasafe_fields = get_fields(
            self.parent.step_kw_purpose.selected_purpose()['key'],
            subcategory['key'])
        return inasafe_fields

    def extra_keyword_changed(self, widget):
        """Populate slave widget if exists and enable the Next button
           if all extra keywords are set.

        :param widget: Metadata of the widget where the event happened.
        :type widget: dict
        """

        self.parent.pbnNext.setEnabled(self.are_all_extra_keywords_selected())

    def selected_extra_keywords(self):
        """Obtain the extra keywords selected by user.

        :returns: Metadata of the extra keywords.
        :rtype: dict, None
        """
        extra_keywords = {}

        return extra_keywords

    def are_all_extra_keywords_selected(self):
        """Ensure all all additional keyword are set by user

        :returns: True if all additional keyword widgets are set
        :rtype: boolean
        """
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

    # noinspection PyTypeChecker
    def set_widgets(self):
        """Set widgets on the Extra Keywords tab."""
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
            option_list = [not_available]
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

            # Create SelectParameter
            select_parameter = SelectParameter()
            select_parameter.guid = inasafe_field['key']
            select_parameter.name = inasafe_field['name']
            select_parameter.is_required = False
            select_parameter.help_text = inasafe_field['description']
            select_parameter.description = inasafe_field['description']
            select_parameter.element_type = unicode
            select_parameter.options_list = option_list
            select_parameter.value = option_list[0]
            self.parameters.append(select_parameter)

        # Create the parameter container and add to the wizard.
        self.parameter_container = ParameterContainer(self.parameters)
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
            if not parameter.value == not_available:
                inasafe_fields[parameter.guid] = parameter.value

        return inasafe_fields
