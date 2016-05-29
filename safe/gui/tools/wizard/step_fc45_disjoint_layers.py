# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Function Centric Wizard Step: Disjoint Layers

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
from PyQt4.QtGui import QPixmap
from safe.utilities.resources import resources_path

from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_step import WizardStep


FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcDisjointLayers(WizardStep, FORM_CLASS):
    """Function Centric Wizard Step: Disjoint Layers"""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        # Never go further if layers disjoint!
        return False

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        # pylint: disable=unreachable
        if self.parent.step_fc_explayer_origin.rbExpLayerFromCanvas.\
                isChecked():
            new_step = self.parent.step_fc_explayer_from_canvas
        # pylint: enable=unreachable
        else:
            new_step = self.parent.step_fc_explayer_from_browser
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        return None

    def set_widgets(self):
        """Set widgets on the Disjoint Layers tab"""
        self.lblIconDisjoint_1.setPixmap(
            QPixmap(resources_path('img', 'wizard', 'icon-stop.svg')))
