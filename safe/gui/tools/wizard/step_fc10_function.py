# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Function Centric Wizard Step: Impact Function Selector

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

# noinspection PyPackageRequirements
from PyQt4 import QtCore, QtGui
# noinspection PyPackageRequirements
from PyQt4.QtGui import QPixmap

from safe.utilities.resources import resources_path
from safe.gui.tools.wizard.wizard_strings import (
    select_function_question)
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_step import WizardStep

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcFunction(WizardStep, FORM_CLASS):
    """Function Centric Wizard Step: Impact Function Selector"""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.selected_function())

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_fc_hazlayer_origin
        return new_step

    # noinspection PyPep8Naming
    def on_lstFunctions_itemSelectionChanged(self):
        """Update function description label

        .. note:: This is an automatic Qt slot
           executed when the category selection changes.
        """
        imfunc = self.selected_function()
        # Exit if no selection
        if not imfunc:
            return

        # Set description label
        description = '<table border="0">'
        if "name" in imfunc.keys():
            description += '<tr><td><b>%s</b>: </td><td>%s</td></tr>' % (
                self.tr('Function'), imfunc['name'])
        if "overview" in imfunc.keys():
            description += '<tr><td><b>%s</b>: </td><td>%s</td></tr>' % (
                self.tr('Overview'), imfunc['overview'])
        description += '</table>'
        self.lblDescribeFunction.setText(description)

        # Enable the next button if anything selected
        self.parent.pbnNext.setEnabled(bool(self.selected_function()))

    def selected_function(self):
        """Obtain the impact function selected by user.

        :returns: metadata of the selected function.
        :rtype: dict, None
        """
        item = self.lstFunctions.currentItem()
        if not item:
            return None

        data = item.data(QtCore.Qt.UserRole)
        if data:
            return data
        else:
            return None

    def set_widgets(self):
        """Set widgets on the Impact Functions tab."""
        self.lstFunctions.clear()
        self.lblDescribeFunction.setText('')

        h, e, hc, ec = self.parent.selected_impact_function_constraints()
        # Set empty IF
        functions = []
        self.lblSelectFunction.setText(
            select_function_question % (
                hc['name'], h['name'], ec['name'], e['name']))
        for f in functions:
            item = QtGui.QListWidgetItem(self.lstFunctions)
            item.setText(f['name'])
            item.setData(QtCore.Qt.UserRole, f)
        self.auto_select_one_item(self.lstFunctions)

        # Set hazard and exposure icons on next steps
        icon_path = resources_path(
            'img', 'wizard', 'keyword-subcategory-%s.svg'
            % (h['key'] or 'notset'))
        self.lblIconFunctionHazard.setPixmap(QPixmap(icon_path))

        icon_path = resources_path(
            'img', 'wizard', 'keyword-subcategory-%s.svg'
            % (e['key'] or 'notset'))
        self.lblIconFunctionExposure.setPixmap(QPixmap(icon_path))

        # icon_path = resources_path(
        #     'img', 'wizard', 'keyword-category-aggregation.svg')
        # Temporarily hide aggregation icon until we have one suitable
        # (as requested in a comment to PR #2060)
        icon_path = None
        self.parent.step_fc_agglayer_origin.\
            lblIconIFCWAggregationOrigin.setPixmap(QPixmap(icon_path))
        self.parent.step_fc_agglayer_from_canvas.\
            lblIconIFCWAggregationFromCanvas.setPixmap(QPixmap(icon_path))
        self.parent.step_fc_agglayer_from_browser.\
            lblIconIFCWAggregationFromBrowser.setPixmap(QPixmap(icon_path))
