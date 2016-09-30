# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Keyword Wizard Step: Layer Mode

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

from safe.definitionsv4.layer_purposes import (
    layer_purpose_exposure, layer_purpose_hazard)
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_strings import (
    layer_mode_raster_question,
    layer_mode_vector_question,
    layer_mode_vector_classified_confirm,
    layer_mode_vector_continuous_confirm)
from safe.utilities.gis import (
    is_raster_layer,
    is_point_layer)
from safe.utilities.keyword_io import definition

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwLayerMode(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Layer Mode"""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.selected_layermode())

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        if self.parent.step_kw_purpose.\
                selected_purpose() == layer_purpose_hazard:
            new_step = self.parent.step_kw_hazard_category
        else:
            new_step = self.parent.step_kw_subcategory
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        if self.parent.step_kw_layermode.\
                selected_layermode() == layer_mode_classified:
            if is_point_layer(self.parent.layer) \
                    and self.parent.step_kw_purpose.\
                    selected_purpose() == layer_purpose_hazard:
                # Skip FIELD and CLASSIFICATION for point volcanos
                new_step = self.parent.step_kw_extrakeywords
            elif self.parent.step_kw_classification.\
                    classifications_for_layer():
                new_step = self.parent.step_kw_classification
            elif is_raster_layer(self.parent.layer):
                new_step = self.parent.step_kw_extrakeywords
            else:
                new_step = self.parent.step_kw_field
        else:
            # CONTINUOUS DATA, ALL GEOMETRIES
            new_step = self.parent.step_kw_unit
        return new_step

    def layermodes_for_layer(self):
        """Return a list of valid layer modes for a layer.

        :returns: A list where each value represents a valid layer mode.
        :rtype: list
        """
        purpose = self.parent.step_kw_purpose.selected_purpose()
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        layer_geometry_id = self.parent.get_layer_geometry_id()
        if purpose == layer_purpose_hazard:
            hazard_category = self.parent.step_kw_hazard_category.\
                selected_hazard_category()
            return self.impact_function_manager.available_hazard_layer_modes(
                subcategory['key'], layer_geometry_id, hazard_category['key'])
        elif purpose == layer_purpose_exposure:
            return self.impact_function_manager.available_exposure_layer_modes(
                subcategory['key'], layer_geometry_id)

    # noinspection PyPep8Naming
    def on_lstLayerModes_itemSelectionChanged(self):
        """Update layer mode description label and unit widgets.

        .. note:: This is an automatic Qt slot
           executed when the subcategory selection changes.
        """
        self.clear_further_steps()
        # Set widgets
        layer_mode = self.selected_layermode()
        # Exit if no selection
        if not layer_mode:
            self.lblDescribeLayerMode.setText('')
            return
        # Set description label
        self.lblDescribeLayerMode.setText(layer_mode['description'])
        # Enable the next button
        self.parent.pbnNext.setEnabled(True)

    def selected_layermode(self):
        """Obtain the layer mode selected by user.
        :returns: selected layer mode.
        :rtype: string, None
        """
        item = self.lstLayerModes.currentItem()
        try:
            return definition(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def clear_further_steps(self):
        """ Clear all further steps
            in order to properly calculate the prev step
        """
        self.parent.step_kw_unit.lstUnits.clear()
        self.parent.step_kw_field.lstFields.clear()
        self.parent.step_kw_classification.lstClassifications.clear()

    def set_widgets(self):
        """Set widgets on the LayerMode tab."""
        self.clear_further_steps()
        # Set widgets
        purpose = self.parent.step_kw_purpose.selected_purpose()
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        layer_mode_question = (
            layer_mode_raster_question
            if is_raster_layer(self.parent.layer)
            else layer_mode_vector_question)

        self.lblDescribeLayerMode.setText('')
        self.lstLayerModes.clear()
        layer_modes = self.parent.step_kw_layermode.layermodes_for_layer()
        if is_raster_layer(self.parent.layer):
            layer_mode_question = layer_mode_raster_question
        else:
            if len(layer_modes) == 2:
                layer_mode_question = layer_mode_vector_question
            elif len(layer_modes) == 1:
                if layer_modes[0]['key'] == 'classified':
                    layer_mode_question = layer_mode_vector_classified_confirm
                elif layer_modes[0]['key'] == 'continuous':
                    layer_mode_question = layer_mode_vector_continuous_confirm
                else:
                    layer_mode_question = layer_mode_vector_question
        self.lblSelectLayerMode.setText(
            layer_mode_question % (subcategory['name'], purpose['name']))
        for layer_mode in layer_modes:
            item = QListWidgetItem(layer_mode['name'], self.lstLayerModes)
            item.setData(QtCore.Qt.UserRole, layer_mode['key'])
            self.lstLayerModes.addItem(item)

        # Set value to existing keyword or default value
        layermode_keys = [m['key'] for m in layer_modes]
        layermode_keyword = self.parent.get_existing_keyword('layer_mode')
        if layermode_keyword in layermode_keys:
            indx = layermode_keys.index(layermode_keyword)
        elif layer_mode_continuous['key'] in layermode_keys:
            # Set default value
            indx = layermode_keys.index(layer_mode_continuous['key'])
        else:
            indx = -1
        self.lstLayerModes.setCurrentRow(indx)

        self.auto_select_one_item(self.lstLayerModes)
