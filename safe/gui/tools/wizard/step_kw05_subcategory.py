# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Keyword Wizard Step: Layer Subcategory
  (Hazard or Exposure)

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

import os

from PyQt4 import QtCore
from PyQt4.QtGui import (
    QListWidgetItem,
    QPixmap)

from safe.definitionsv4.layer_purposes import (
    layer_purpose_exposure, layer_purpose_hazard)
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_utils import get_question_text
from safe.utilities.keyword_io import definition
from safe.utilities.resources import resources_path


FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwSubcategory(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Layer Subcategory (Hazard or Exposure)"""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.selected_subcategory())

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_kw_purpose
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        if self.parent.step_kw_purpose.\
                selected_purpose() == layer_purpose_hazard:
            new_step = self.parent.step_kw_hazard_category
        else:
            new_step = self.parent.step_kw_layermode
        return new_step

    def subcategories_for_layer(self):
        """Return a list of valid subcategories for a layer.
           Subcategory is hazard type or exposure type.

        :returns: A list where each value represents a valid subcategory.
        :rtype: list
        """
        purpose = self.parent.step_kw_purpose.selected_purpose()
        layer_geometry_id = self.parent.get_layer_geometry_id()
        if purpose == layer_purpose_hazard:
            return self.impact_function_manager.hazards_for_layer(
                layer_geometry_id)
        elif purpose == layer_purpose_exposure:
            return self.impact_function_manager.exposures_for_layer(
                layer_geometry_id)

    # noinspection PyPep8Naming
    def on_lstSubcategories_itemSelectionChanged(self):
        """Update subcategory description label.

        .. note:: This is an automatic Qt slot
           executed when the subcategory selection changes.
        """
        self.clear_further_steps()
        # Set widgets
        subcategory = self.selected_subcategory()
        # Exit if no selection
        if not subcategory:
            return
        # Set description label
        self.lblDescribeSubcategory.setText(subcategory['description'])

        icon_path = resources_path('img', 'wizard',
                                   'keyword-subcategory-%s.svg'
                                   % (subcategory['key'] or 'notset'))
        if not os.path.exists(icon_path):
            purpose = self.parent.step_kw_purpose.selected_purpose()
            icon_path = resources_path('img', 'wizard',
                                       'keyword-category-%s.svg'
                                       % (purpose['key']))
        self.lblIconSubcategory.setPixmap(QPixmap(icon_path))
        # Enable the next button
        self.parent.pbnNext.setEnabled(True)

    def selected_subcategory(self):
        """Obtain the subcategory selected by user.

        :returns: Metadata of the selected subcategory.
        :rtype: dict, None
        """
        item = self.lstSubcategories.currentItem()
        try:
            return definition(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def clear_further_steps(self):
        """ Clear all further steps
            in order to properly calculate the prev step
        """
        self.parent.step_kw_hazard_category.lstHazardCategories.clear()
        self.parent.step_kw_layermode.lstLayerModes.clear()
        self.parent.step_kw_unit.lstUnits.clear()
        self.parent.step_kw_field.lstFields.clear()
        self.parent.step_kw_classification.lstClassifications.clear()

    def set_widgets(self):
        """Set widgets on the Subcategory tab."""
        self.clear_further_steps()
        # Set widgets
        purpose = self.parent.step_kw_purpose.selected_purpose()
        self.lstSubcategories.clear()
        self.lblDescribeSubcategory.setText('')
        self.lblIconSubcategory.setPixmap(QPixmap())
        self.lblSelectSubcategory.setText(
            get_question_text('%s_question' % purpose['key']))
        for i in self.subcategories_for_layer():
            item = QListWidgetItem(i['name'], self.lstSubcategories)
            item.setData(QtCore.Qt.UserRole, i['key'])
            self.lstSubcategories.addItem(item)

        # Check if layer keywords are already assigned
        key = self.parent.step_kw_purpose.selected_purpose()['key']
        keyword = self.parent.get_existing_keyword(key)

        # Overwrite the keyword if it's KW mode embedded in IFCW mode
        if self.parent.parent_step:
            keyword = self.parent.get_parent_mode_constraints()[1]['key']

        # Set values based on existing keywords or parent mode
        if keyword:
            subcategories = []
            for index in xrange(self.lstSubcategories.count()):
                item = self.lstSubcategories.item(index)
                subcategories.append(item.data(QtCore.Qt.UserRole))
            if keyword in subcategories:
                self.lstSubcategories.setCurrentRow(
                    subcategories.index(keyword))

        self.auto_select_one_item(self.lstSubcategories)
