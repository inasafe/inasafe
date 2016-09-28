# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Keyword Wizard Step: Classification Selector

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
from PyQt4.QtGui import QListWidgetItem

from safe.definitionsv4.hazard import layer_purpose_hazard
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_strings import classification_question
from safe.utilities.gis import is_raster_layer
from safe.utilities.keyword_io import definition

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwClassification(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Classification Selector"""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.selected_classification())

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_kw_layermode
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        if is_raster_layer(self.parent.layer):
            new_step = self.parent.step_kw_classify
        else:
            new_step = self.parent.step_kw_field
        return new_step

    def classifications_for_layer(self):
        """Return a list of valid classifications for a layer.

        :returns: A list where each value represents a valid classification.
        :rtype: list
        """
        layer_geometry_id = self.parent.get_layer_geometry_id()
        layer_mode_id = self.parent.step_kw_layermode.\
            selected_layermode()['key']
        subcategory_id = self.parent.step_kw_subcategory.\
            selected_subcategory()['key']
        if self.parent.step_kw_purpose.\
                selected_purpose() == layer_purpose_hazard:
            hazard_category_id = self.parent.step_kw_hazard_category.\
                selected_hazard_category()['key']
            if is_raster_layer(self.parent.layer):
                return self.impact_function_manager.\
                    raster_hazards_classifications_for_layer(
                        subcategory_id,
                        layer_geometry_id,
                        layer_mode_id,
                        hazard_category_id)
            else:
                return self.impact_function_manager\
                    .vector_hazards_classifications_for_layer(
                        subcategory_id,
                        layer_geometry_id,
                        layer_mode_id,
                        hazard_category_id)
        else:
            # There are no classifications for exposures defined yet, apart
            # from postprocessor_classification, processed paralelly
            return []

    def on_lstClassifications_itemSelectionChanged(self):
        """Update classification description label and unlock the Next button.

        .. note:: This is an automatic Qt slot
           executed when the field selection changes.
        """
        self.clear_further_steps()
        classification = self.selected_classification()
        # Exit if no selection
        if not classification:
            return
        # Set description label
        self.lblDescribeClassification.setText(classification["description"])
        # Enable the next button
        self.parent.pbnNext.setEnabled(True)

    def selected_classification(self):
        """Obtain the classification selected by user.

        :returns: Metadata of the selected classification.
        :rtype: dict, None
        """
        item = self.lstClassifications.currentItem()
        try:
            return definition(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def clear_further_steps(self):
        """ Clear all further steps
            in order to properly calculate the prev step
        """
        self.parent.step_kw_field.lstFields.clear()
        self.parent.step_kw_classify.treeClasses.clear()

    def set_widgets(self):
        """Set widgets on the Classification tab."""
        self.clear_further_steps()
        purpose = self.parent.step_kw_purpose.selected_purpose()['name']
        subcategory = self.parent.step_kw_subcategory.\
            selected_subcategory()['name']
        self.lstClassifications.clear()
        self.lblDescribeClassification.setText('')
        self.lblSelectClassification.setText(
            classification_question % (subcategory, purpose))
        classifications = self.classifications_for_layer()
        for classification in classifications:
            if not isinstance(classification, dict):
                classification = definition(classification)
            item = QListWidgetItem(
                classification['name'],
                self.lstClassifications)
            item.setData(QtCore.Qt.UserRole, classification['key'])
            self.lstClassifications.addItem(item)

        # Set values based on existing keywords (if already assigned)
        geom = 'raster' if is_raster_layer(self.parent.layer) else 'vector'
        key = '%s_%s_classification' % (
            geom, self.parent.step_kw_purpose.selected_purpose()['key'])
        classification_keyword = self.parent.get_existing_keyword(key)
        if classification_keyword:
            classifications = []
            for index in xrange(self.lstClassifications.count()):
                item = self.lstClassifications.item(index)
                classifications.append(item.data(QtCore.Qt.UserRole))
            if classification_keyword in classifications:
                self.lstClassifications.setCurrentRow(
                    classifications.index(classification_keyword))

        self.auto_select_one_item(self.lstClassifications)
