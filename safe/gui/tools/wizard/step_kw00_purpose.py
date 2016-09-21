# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Keyword Wizard Step: Layer Purpose

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
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtGui import (
    QListWidgetItem,
    QPixmap)

from definitionsv4.definitions_v3 import layer_purpose_aggregation
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_strings import category_question
from safe.utilities.keyword_io import definition
from safe.utilities.resources import resources_path

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwPurpose(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Layer Purpose"""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.selected_purpose())

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        if self.parent.parent_step:
            # Come back to the parent thread
            self.parent.set_mode_label_to_ifcw()
            new_step = self.parent.parent_step
            self.parent.parent_step = None
        else:
            new_step = None
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        if self.selected_purpose() == layer_purpose_aggregation:
            new_step = self.parent.step_kw_field
        else:
            new_step = self.parent.step_kw_subcategory
        return new_step

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_lstCategories_itemSelectionChanged(self):
        """Update purpose description label.

        .. note:: This is an automatic Qt slot
           executed when the purpose selection changes.
        """
        self.clear_further_steps()
        # Set widgets
        purpose = self.selected_purpose()
        # Exit if no selection
        if not purpose:
            return
        # Set description label
        self.lblDescribeCategory.setText(purpose["description"])
        self.lblIconCategory.setPixmap(QPixmap(
            resources_path('img', 'wizard', 'keyword-category-%s.svg'
                           % (purpose['key'] or 'notset'))))
        # Enable the next button
        self.parent.pbnNext.setEnabled(True)

    def selected_purpose(self):
        """Obtain the layer purpose selected by user.

        :returns: Metadata of the selected layer purpose.
        :rtype: dict, None
        """
        item = self.lstCategories.currentItem()
        try:
            return definition(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def purposes_for_layer(self):
        """Return a list of valid purposes for the current layer.

        :returns: A list where each value represents a valid purpose.
        :rtype: list
        """
        layer_geometry_id = self.parent.get_layer_geometry_id()
        return self.impact_function_manager.purposes_for_layer(
            layer_geometry_id)

    def clear_further_steps(self):
        """ Clear all further steps
            in order to properly calculate the prev step
        """
        self.parent.step_kw_hazard_category.lstHazardCategories.clear()
        self.parent.step_kw_subcategory.lstSubcategories.clear()
        self.parent.step_kw_layermode.lstLayerModes.clear()
        self.parent.step_kw_unit.lstUnits.clear()
        self.parent.step_kw_field.lstFields.clear()
        self.parent.step_kw_classification.lstClassifications.clear()

    def set_widgets(self):
        """Set widgets on the layer purpose tab."""
        self.clear_further_steps()
        # Set widgets
        self.lstCategories.clear()
        self.lblDescribeCategory.setText('')
        self.lblIconCategory.setPixmap(QPixmap())
        self.lblSelectCategory.setText(
            category_question % self.parent.layer.name())
        purposes = self.purposes_for_layer()
        if self.parent.get_layer_geometry_id() == 'polygon':
            purposes += ['aggregation']
        for purpose in purposes:
            if not isinstance(purpose, dict):
                purpose = definition(purpose)
            item = QListWidgetItem(purpose['name'], self.lstCategories)
            item.setData(QtCore.Qt.UserRole, purpose['key'])
            self.lstCategories.addItem(item)

        # Check if layer keywords are already assigned
        purpose_keyword = self.parent.get_existing_keyword('layer_purpose')

        # Overwrite the purpose_keyword if it's KW mode embedded in IFCW mode
        if self.parent.parent_step:
            purpose_keyword = self.parent.\
                get_parent_mode_constraints()[0]['key']

        # Set values based on existing keywords or parent mode
        if purpose_keyword:
            purposes = []
            for index in xrange(self.lstCategories.count()):
                item = self.lstCategories.item(index)
                purposes.append(item.data(QtCore.Qt.UserRole))
            if purpose_keyword in purposes:
                self.lstCategories.setCurrentRow(
                    purposes.index(purpose_keyword))

        self.auto_select_one_item(self.lstCategories)
