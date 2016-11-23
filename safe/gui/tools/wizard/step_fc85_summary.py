# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Function Centric Wizard Step: Summary

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

from collections import OrderedDict

from safe.common.parameters.resource_parameter import ResourceParameter
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe_extras.parameters.group_parameter import GroupParameter


FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcSummary(WizardStep, FORM_CLASS):
    """Function Centric Wizard Step: Summary"""

    if_params = None

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
        new_step = self.parent.step_fc_params
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_fc_analysis
        return new_step

    def set_widgets(self):
        """Set widgets on the Summary tab"""
        if self.parent.aggregation_layer:
            aggr = self.parent.aggregation_layer.name()
        else:
            aggr = self.tr('no aggregation')

        html = self.tr('Please ensure the following information '
                       'is correct and press Run.')

        # TODO: update this to use InaSAFE message API rather...
        html += '<br/><table cellspacing="4">'
        html += ('<tr>'
                 '  <td><b>%s</b></td><td></td><td>%s</td>'
                 '</tr><tr>'
                 '  <td><b>%s</b></td><td></td><td>%s</td>'
                 '</tr><tr>'
                 '  <td><b>%s</b></td><td></td><td>%s</td>'
                 '</tr><tr>'
                 '  <td colspan="3"></td>'
                 '</tr>' % (
                     self.tr('hazard layer').capitalize().replace(
                         ' ', '&nbsp;'),
                     self.parent.hazard_layer.name(),
                     self.tr('exposure layer').capitalize().replace(
                         ' ', '&nbsp;'),
                     self.parent.exposure_layer.name(),
                     self.tr('aggregation layer').capitalize().replace(
                         ' ', '&nbsp;'), aggr))

        self.lblSummary.setText(html)
