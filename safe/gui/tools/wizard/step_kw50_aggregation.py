# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Keyword Wizard Step: Aggregation Parameters

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

from safe.definitionsv4.aggregation import (
    global_default_attribute, do_not_use_attribute)
from safe.defaults import get_defaults
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.utilities.gis import layer_attribute_names


# Aggregations' keywords
DEFAULTS = get_defaults()
female_ratio_attribute_key = DEFAULTS['FEMALE_RATIO_ATTR_KEY']
female_ratio_default_key = DEFAULTS['FEMALE_RATIO_KEY']
youth_ratio_attribute_key = DEFAULTS['YOUTH_RATIO_ATTR_KEY']
youth_ratio_default_key = DEFAULTS['YOUTH_RATIO_KEY']
adult_ratio_attribute_key = DEFAULTS['ADULT_RATIO_ATTR_KEY']
adult_ratio_default_key = DEFAULTS['ADULT_RATIO_KEY']
elderly_ratio_attribute_key = DEFAULTS['ELDERLY_RATIO_ATTR_KEY']
elderly_ratio_default_key = DEFAULTS['ELDERLY_RATIO_KEY']


FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwAggregation(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Aggregation Parameters"""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizad Dialog).
        :type parent: QWidget

        """
        WizardStep.__init__(self, parent)
        # string constants
        self.global_default_string = global_default_attribute['name']
        self.global_default_data = global_default_attribute['id']
        self.do_not_use_string = do_not_use_attribute['name']
        self.do_not_use_data = do_not_use_attribute['id']

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
        new_step = self.parent.step_kw_field
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_kw_source
        return new_step

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def on_cboFemaleRatioAttribute_currentIndexChanged(self):
        """Automatic slot executed when the female ratio attribute is changed.

        When the user changes the female ratio attribute
        (cboFemaleRatioAttribute), it will change the enabled value of
        dsbFemaleRatioDefault. If value is 'Use default', enable
        dsbFemaleRatioDefault. Otherwise, disabled it.
        """
        value = self.cboFemaleRatioAttribute.currentText()
        if value == self.global_default_string:
            self.dsbFemaleRatioDefault.setEnabled(True)
        else:
            self.dsbFemaleRatioDefault.setEnabled(False)

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def on_cboYouthRatioAttribute_currentIndexChanged(self):
        """Automatic slot executed when the youth ratio attribute is changed.

        When the user changes the youth ratio attribute
        (cboYouthRatioAttribute), it will change the enabled value of
        dsbYouthRatioDefault. If value is 'Use default', enable
        dsbYouthRatioDefault. Otherwise, disabled it.
        """
        value = self.cboYouthRatioAttribute.currentText()
        if value == self.global_default_string:
            self.dsbYouthRatioDefault.setEnabled(True)
        else:
            self.dsbYouthRatioDefault.setEnabled(False)

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def on_cboAdultRatioAttribute_currentIndexChanged(self):
        """Automatic slot executed when the adult ratio attribute is changed.

        When the user changes the adult ratio attribute
        (cboAdultRatioAttribute), it will change the enabled value of
        dsbAdultRatioDefault. If value is 'Use default', enable
        dsbAdultRatioDefault. Otherwise, disabled it.
        """
        value = self.cboAdultRatioAttribute.currentText()
        if value == self.global_default_string:
            self.dsbAdultRatioDefault.setEnabled(True)
        else:
            self.dsbAdultRatioDefault.setEnabled(False)

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def on_cboElderlyRatioAttribute_currentIndexChanged(self):
        """Automatic slot executed when the adult ratio attribute is changed.

        When the user changes the elderly ratio attribute
        (cboElderlyRatioAttribute), it will change the enabled value of
        dsbElderlyRatioDefault. If value is 'Use default', enable
        dsbElderlyRatioDefault. Otherwise, disabled it.
        """
        value = self.cboElderlyRatioAttribute.currentText()
        if value == self.global_default_string:
            self.dsbElderlyRatioDefault.setEnabled(True)
        else:
            self.dsbElderlyRatioDefault.setEnabled(False)

    def get_aggregation_attributes(self):
        """Obtain the value of aggregation attributes set by user.

        :returns: The key and value of aggregation attributes.
        :rtype: dict
        """
        aggregation_attributes = dict()

        current_index = self.cboFemaleRatioAttribute.currentIndex()
        data = self.cboFemaleRatioAttribute.itemData(current_index)
        aggregation_attributes[female_ratio_attribute_key] = data

        value = self.dsbFemaleRatioDefault.value()
        aggregation_attributes[female_ratio_default_key] = value

        current_index = self.cboYouthRatioAttribute.currentIndex()
        data = self.cboYouthRatioAttribute.itemData(current_index)
        aggregation_attributes[youth_ratio_attribute_key] = data

        value = self.dsbYouthRatioDefault.value()
        aggregation_attributes[youth_ratio_default_key] = value

        current_index = self.cboAdultRatioAttribute.currentIndex()
        data = self.cboAdultRatioAttribute.itemData(current_index)
        aggregation_attributes[adult_ratio_attribute_key] = data

        value = self.dsbAdultRatioDefault.value()
        aggregation_attributes[adult_ratio_default_key] = value

        current_index = self.cboElderlyRatioAttribute.currentIndex()
        data = self.cboElderlyRatioAttribute.itemData(current_index)
        aggregation_attributes[elderly_ratio_attribute_key] = data

        value = self.dsbElderlyRatioDefault.value()
        aggregation_attributes[elderly_ratio_default_key] = value

        return aggregation_attributes

    def age_ratios_are_valid(self):
        """Return true if the sum of age ratios is good, otherwise False.

        Good means their sum does not exceed 1.

        :returns: Tuple of boolean and float. Boolean represent good or not
            good, while float represent the summation of age ratio. If some
            ratio do not use global default, the summation is set to 0.
        :rtype: tuple

        """
        youth_ratio_index = self.cboYouthRatioAttribute.currentIndex()
        adult_ratio_index = self.cboAdultRatioAttribute.currentIndex()
        elderly_ratio_index = self.cboElderlyRatioAttribute.currentIndex()

        ratio_indexes = [
            youth_ratio_index, adult_ratio_index, elderly_ratio_index]

        if ratio_indexes.count(0) == len(ratio_indexes):
            youth_ratio_default = self.dsbYouthRatioDefault.value()
            adult_ratio_default = self.dsbAdultRatioDefault.value()
            elderly_ratio_default = self.dsbElderlyRatioDefault.value()

            sum_ratio_default = youth_ratio_default + adult_ratio_default
            sum_ratio_default += elderly_ratio_default
            if sum_ratio_default > 1:
                return False, sum_ratio_default
            else:
                return True, sum_ratio_default
        return True, 0

    # noinspection PyUnresolvedReferences,PyStatementEffect
    def populate_cbo_aggregation_attribute(
            self, ratio_attribute_key, cbo_ratio_attribute):
        """Populate the combo box cbo_ratio_attribute for ratio_attribute_key.

        :param ratio_attribute_key: A ratio attribute key that saved in
               keywords.
        :type ratio_attribute_key: str

        :param cbo_ratio_attribute: A combo box that wants to be populated.
        :type cbo_ratio_attribute: QComboBox
        """
        cbo_ratio_attribute.clear()
        ratio_attribute = self.parent.get_existing_keyword(ratio_attribute_key)
        fields, attribute_position = layer_attribute_names(
            self.parent.layer, [QtCore.QVariant.Double], ratio_attribute)

        cbo_ratio_attribute.addItem(
            self.global_default_string, self.global_default_data)
        cbo_ratio_attribute.addItem(
            self.do_not_use_string, self.do_not_use_data)
        for field in fields:
            cbo_ratio_attribute.addItem(field, field)
        # For backward compatibility, still use Use default
        if (ratio_attribute == self.global_default_data or
                ratio_attribute == self.tr('Use default')):
            cbo_ratio_attribute.setCurrentIndex(0)
        elif ratio_attribute == self.do_not_use_data:
            cbo_ratio_attribute.setCurrentIndex(1)
        elif ratio_attribute is None or attribute_position is None:
            # current_keyword was not found in the attribute table.
            # Use default
            cbo_ratio_attribute.setCurrentIndex(0)
        else:
            # + 2 is because we add use defaults and don't use
            cbo_ratio_attribute.setCurrentIndex(attribute_position + 2)

    def set_widgets(self):
        """Set widgets on the aggregation tab."""
        # Set values based on existing keywords (if already assigned)
        defaults = get_defaults()

        female_ratio_default = self.parent.get_existing_keyword(
            female_ratio_default_key)
        if female_ratio_default:
            self.dsbFemaleRatioDefault.setValue(
                float(female_ratio_default))
        else:
            self.dsbFemaleRatioDefault.setValue(defaults['FEMALE_RATIO'])

        youth_ratio_default = self.parent.get_existing_keyword(
            youth_ratio_default_key)
        if youth_ratio_default:
            self.dsbYouthRatioDefault.setValue(float(youth_ratio_default))
        else:
            self.dsbYouthRatioDefault.setValue(defaults['YOUTH_RATIO'])

        adult_ratio_default = self.parent.get_existing_keyword(
            adult_ratio_default_key)
        if adult_ratio_default:
            self.dsbAdultRatioDefault.setValue(float(adult_ratio_default))
        else:
            self.dsbAdultRatioDefault.setValue(defaults['ADULT_RATIO'])

        elderly_ratio_default = self.parent.get_existing_keyword(
            elderly_ratio_default_key)
        if elderly_ratio_default:
            self.dsbElderlyRatioDefault.setValue(float(elderly_ratio_default))
        else:
            self.dsbElderlyRatioDefault.setValue(
                defaults['ELDERLY_RATIO'])

        ratio_attribute_keys = [
            female_ratio_attribute_key,
            youth_ratio_attribute_key,
            adult_ratio_attribute_key,
            elderly_ratio_attribute_key]

        cbo_ratio_attributes = [
            self.cboFemaleRatioAttribute,
            self.cboYouthRatioAttribute,
            self.cboAdultRatioAttribute,
            self.cboElderlyRatioAttribute]

        for i in range(len(cbo_ratio_attributes)):
            self.populate_cbo_aggregation_attribute(
                ratio_attribute_keys[i], cbo_ratio_attributes[i])
