# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Function Centric Wizard Step: IF Constraint Selector 1

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
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignature

from safe.definitionsv4.hazard_category import hazard_category_single_event
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_utils import (
    RoleFunctions,
    RoleHazard,
    RoleExposure)
from safe.utilities.resources import resources_path

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcFunctions1(WizardStep, FORM_CLASS):
    """Function Centric Wizard Step: IF Constraint Selector 1"""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.tblFunctions1.selectedItems())

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        return None

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        return self.parent.step_fc_functions2

    def selected_functions_1(self):
        """Obtain functions available for hazard an exposure selected by user.

        :returns: List of the available functions metadata.
        :rtype: list, None
        """
        selection = self.tblFunctions1.selectedItems()
        if len(selection) != 1:
            return []
        try:
            return selection[0].data(RoleFunctions)
        except (AttributeError, NameError):
            return None

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_tblFunctions1_itemSelectionChanged(self):
        """Choose selected hazard x exposure combination.

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        functions = self.selected_functions_1()
        if not functions:
            self.lblAvailableFunctions1.clear()
        else:
            txt = self.tr('Available functions:') + ' ' + ', '.join(
                [f['name'] for f in functions])
            self.lblAvailableFunctions1.setText(txt)

        # Clear the selection on the 2nd matrix
        self.parent.step_fc_functions2.tblFunctions2.clearContents()
        self.parent.step_fc_functions2.lblAvailableFunctions2.clear()
        self.parent.pbnNext.setEnabled(True)

        # Put a dot to the selected cell - note there is no way
        # to center an icon without using a custom ItemDelegate
        selection = self.tblFunctions1.selectedItems()
        selItem = (len(selection) == 1) and selection[0] or None
        for row in range(self.tblFunctions1.rowCount()):
            for col in range(self.tblFunctions1.columnCount()):
                item = self.tblFunctions1.item(row, col)
                item.setText((item == selItem) and u'\u2022' or '')

    # pylint: disable=W0613
    # noinspection PyPep8Naming
    def on_tblFunctions1_cellDoubleClicked(self, row, column):
        """Choose selected hazard x exposure combination and go ahead.

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        self.parent.pbnNext.click()
    # pylint: enable=W0613

    def populate_function_table_1(self):
        """Populate the tblFunctions1 table with available functions."""
        # The hazard category radio buttons are now removed -
        # make this parameter of IFM.available_hazards() optional
        hazard_category = hazard_category_single_event
        hazards = self.impact_function_manager\
            .available_hazards(hazard_category['key'])
        # Remove 'generic' from hazards
        for h in hazards:
            if h['key'] == 'generic':
                hazards.remove(h)
        exposures = self.impact_function_manager.available_exposures()

        self.lblAvailableFunctions1.clear()
        self.tblFunctions1.clear()
        self.tblFunctions1.setColumnCount(len(hazards))
        self.tblFunctions1.setRowCount(len(exposures))
        for i in range(len(hazards)):
            h = hazards[i]
            item = QtGui.QTableWidgetItem()
            item.setIcon(QtGui.QIcon(
                resources_path('img', 'wizard', 'keyword-subcategory-%s.svg'
                               % (h['key'] or 'notset'))))
            item.setText(h['name'].capitalize())
            self.tblFunctions1.setHorizontalHeaderItem(i, item)
        for i in range(len(exposures)):
            e = exposures[i]
            item = QtGui.QTableWidgetItem()

            item.setIcon(QtGui.QIcon(resources_path(
                'img', 'wizard', 'keyword-subcategory-%s.svg'
                % (e['key'] or 'notset'))))
            item.setText(e['name'].capitalize())
            self.tblFunctions1.setVerticalHeaderItem(i, item)

        big_font = QtGui.QFont()
        big_font.setPointSize(80)

        for h in hazards:
            for e in exposures:
                item = QtGui.QTableWidgetItem()
                functions = \
                    self.impact_function_manager.functions_for_constraint(
                        h['key'], e['key'])
                if len(functions):
                    background_colour = QtGui.QColor(120, 255, 120)
                else:
                    background_colour = QtGui.QColor(220, 220, 220)
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
                item.setBackground(QtGui.QBrush(background_colour))
                item.setFont(big_font)
                item.setTextAlignment(
                    QtCore.Qt.AlignCenter | QtCore.Qt.AlignHCenter)
                item.setData(RoleFunctions, functions)
                item.setData(RoleHazard, h)
                item.setData(RoleExposure, e)
                self.tblFunctions1.setItem(
                    exposures.index(e), hazards.index(h), item)
        self.parent.pbnNext.setEnabled(False)

    def set_widgets(self):
        """Set widgets on the Impact Functions Table 1 tab."""

        self.tblFunctions1.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)
        self.tblFunctions1.verticalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)

        self.populate_function_table_1()
