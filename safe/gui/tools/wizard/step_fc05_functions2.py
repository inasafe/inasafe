# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Function Centric Wizard Step: IF Constraint Selector 2

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

from definitionsv4.definitions_v3 import (
    layer_geometry_point,
    layer_geometry_line,
    layer_geometry_polygon,
    layer_geometry_raster)
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_strings import (
    select_function_constraints2_question)
from safe.gui.tools.wizard.wizard_utils import (
    RoleFunctions,
    RoleHazard,
    RoleExposure,
    RoleHazardConstraint,
    RoleExposureConstraint)

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcFunctions2(WizardStep, FORM_CLASS):
    """Function Centric Wizard Step: IF Constraint Selector 2"""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.tblFunctions2.selectedItems())

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_fc_functions1
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_fc_function
        return new_step

    def selected_functions_2(self):
        """Obtain functions available for hazard and exposure selected by user.

        :returns: List of the available functions metadata.
        :rtype: list, None
        """
        selection = self.tblFunctions2.selectedItems()
        if len(selection) != 1:
            return []
        return selection[0].data(RoleFunctions)

    # prevents actions being handled twice
    # noinspection PyPep8Naming
    @pyqtSignature('')
    def on_tblFunctions2_itemSelectionChanged(self):
        """Choose selected hazard x exposure constraints combination.

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        functions = self.selected_functions_2()
        if not functions:
            self.lblAvailableFunctions2.clear()
        else:
            text = self.tr('Available functions:') + ' ' + ', '.join(
                [f['name'] for f in functions])
            self.lblAvailableFunctions2.setText(text)
        self.parent.pbnNext.setEnabled(True)

        # Put a dot to the selected cell - note there is no way
        # to center an icon without using a custom ItemDelegate
        selection = self.tblFunctions2.selectedItems()
        selItem = (len(selection) == 1) and selection[0] or None
        for row in range(self.tblFunctions2.rowCount()):
            for col in range(self.tblFunctions2.columnCount()):
                item = self.tblFunctions2.item(row, col)
                item.setText((item == selItem) and u'\u2022' or '')

    # pylint: disable=W0613
    # noinspection PyPep8Naming,PyUnusedLocal
    def on_tblFunctions2_cellDoubleClicked(self, row, column):
        """Click handler for selecting hazard and exposure constraints.

        :param row: The row that the user clicked on.
        :type row: int

        :param column: The column that the user clicked on.
        :type column: int

        .. note:: This is an automatic Qt slot executed when the category
            selection changes.
        """
        self.parent.pbnNext.click()
    # pylint: enable=W0613

    def set_widgets(self):
        """Set widgets on the Impact Functions Table 2 tab."""
        self.tblFunctions2.clear()
        h, e, _hc, _ec = self.parent.selected_impact_function_constraints()
        hazard_layer_geometries = [
            layer_geometry_raster,
            layer_geometry_point,
            layer_geometry_line,
            layer_geometry_polygon]
        exposure_layer_geometries = [
            layer_geometry_raster,
            layer_geometry_point,
            layer_geometry_line,
            layer_geometry_polygon]
        self.lblSelectFunction2.setText(
            select_function_constraints2_question % (h['name'], e['name']))
        self.tblFunctions2.setColumnCount(len(hazard_layer_geometries))
        self.tblFunctions2.setRowCount(len(exposure_layer_geometries))
        self.tblFunctions2.setHorizontalHeaderLabels(
            [i['name'].capitalize() for i in hazard_layer_geometries])
        for i in range(len(exposure_layer_geometries)):
            item = QtGui.QTableWidgetItem()
            item.setText(exposure_layer_geometries[i]['name'].capitalize())
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.tblFunctions2.setVerticalHeaderItem(i, item)

        self.tblFunctions2.horizontalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)
        self.tblFunctions2.verticalHeader().setResizeMode(
            QtGui.QHeaderView.Stretch)

        big_font = QtGui.QFont()
        big_font.setPointSize(80)

        active_items = []
        for col in range(len(hazard_layer_geometries)):
            for row in range(len(exposure_layer_geometries)):
                hc = hazard_layer_geometries[col]
                ec = exposure_layer_geometries[row]
                functions = self.impact_function_manager\
                    .functions_for_constraint(
                        h['key'], e['key'], hc['key'], ec['key'])
                item = QtGui.QTableWidgetItem()
                if len(functions):
                    bgcolor = QtGui.QColor(120, 255, 120)
                    active_items += [item]
                else:
                    bgcolor = QtGui.QColor(220, 220, 220)
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
                    item.setFlags(item.flags() & ~QtCore.Qt.ItemIsSelectable)
                item.setBackground(QtGui.QBrush(bgcolor))
                item.setFont(big_font)
                item.setTextAlignment(
                    QtCore.Qt.AlignCenter | QtCore.Qt.AlignHCenter)
                item.setData(RoleFunctions, functions)
                item.setData(RoleHazard, h)
                item.setData(RoleExposure, e)
                item.setData(RoleHazardConstraint, hc)
                item.setData(RoleExposureConstraint, ec)
                self.tblFunctions2.setItem(row, col, item)
        # Automatically select one item...
        if len(active_items) == 1:
            active_items[0].setSelected(True)
            # set focus, as the inactive selection style is gray
            self.tblFunctions2.setFocus()
