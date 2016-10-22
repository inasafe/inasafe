# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Keyword Wizard Step: Unit

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
from safe.definitionsv4.units import exposure_unit
from safe.definitionsv4.hazard import (
    continuous_hazard_unit)
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_strings import unit_question
from safe.utilities.gis import is_raster_layer
from safe.utilities.keyword_io import definition

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwUnit(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Unit"""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.selected_unit())

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
            if self.parent.step_kw_purpose.\
                    selected_purpose() == layer_purpose_exposure:
                # Only go to resample for continuous raster exposures
                new_step = self.parent.step_kw_resample
            else:
                new_step = self.parent.step_kw_extrakeywords
        else:
            # Currently not used, as we don't have continuous vectors
            new_step = self.parent.step_kw_field
        return new_step

    # noinspection PyPep8Naming
    def on_lstUnits_itemSelectionChanged(self):
        """Update unit description label and field widgets.

        .. note:: This is an automatic Qt slot
           executed when the unit selection changes.
        """
        self.clear_further_steps()
        # Set widgets
        unit = self.selected_unit()
        # Exit if no selection
        if not unit:
            return
        self.lblDescribeUnit.setText(unit['description'])
        # Enable the next button
        self.parent.pbnNext.setEnabled(True)

    def selected_unit(self):
        """Obtain the unit selected by user.

        :returns: Metadata of the selected unit.
        :rtype: dict, None
        """
        item = self.lstUnits.currentItem()
        try:
            return definition(item.data(QtCore.Qt.UserRole))
        except (AttributeError, NameError):
            return None

    def clear_further_steps(self):
        """ Clear all further steps
            in order to properly calculate the prev step
        """
        self.parent.step_kw_field.lstFields.clear()
        self.parent.step_kw_classification.lstClassifications.clear()

    def set_widgets(self):
        """Set widgets on the Unit tab."""
        self.clear_further_steps()
        # Set widgets
        purpose = self.parent.step_kw_purpose.selected_purpose()
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        self.lblSelectUnit.setText(
            unit_question % (subcategory['name'], purpose['name']))
        self.lblDescribeUnit.setText('')
        self.lstUnits.clear()
        subcat = self.parent.step_kw_subcategory.selected_subcategory()['key']
        laygeo = self.parent.get_layer_geometry_id()
        laymod = self.parent.step_kw_layermode.selected_layermode()['key']
        if purpose == layer_purpose_hazard:
            hazcat = self.parent.step_kw_hazard_category.\
                selected_hazard_category()['key']
            units_for_layer = self.impact_function_manager.\
                continuous_hazards_units_for_layer(
                    subcat, laygeo, laymod, hazcat)
        else:
            units_for_layer = self.impact_function_manager\
                .exposure_units_for_layer(
                    subcat, laygeo, laymod)
        for unit_for_layer in units_for_layer:
            # if (self.parent.get_layer_geometry_id() == 'raster' and
            #         'constraint' in unit_for_layer and
            #         unit_for_layer['constraint'] == 'categorical'):
            #     continue
            # else:
            item = QListWidgetItem(unit_for_layer['name'], self.lstUnits)
            item.setData(QtCore.Qt.UserRole, unit_for_layer['key'])
            self.lstUnits.addItem(item)

        # Set values based on existing keywords (if already assigned)
        if self.parent.step_kw_purpose.\
                selected_purpose() == layer_purpose_hazard:
            key = continuous_hazard_unit['key']
        else:
            key = exposure_unit['key']
        unit_id = self.parent.get_existing_keyword(key)
        # unit_id = definitions.old_to_new_unit_id(unit_id)
        if unit_id:
            units = []
            for index in xrange(self.lstUnits.count()):
                item = self.lstUnits.item(index)
                units.append(item.data(QtCore.Qt.UserRole))
            if unit_id in units:
                self.lstUnits.setCurrentRow(units.index(unit_id))

        self.auto_select_one_item(self.lstUnits)
