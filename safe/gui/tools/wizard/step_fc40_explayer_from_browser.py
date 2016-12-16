# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Function Centric Wizard Step: Exposure Layer From Browser

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

# noinspection PyPackageRequirements
from PyQt4.QtGui import QPixmap

from safe.definitionsv4.layer_purposes import layer_purpose_exposure
from safe.utilities.resources import resources_path
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_step_browser import WizardStepBrowser
from safe.gui.tools.wizard.wizard_utils import layers_intersect

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcExpLayerFromBrowser(WizardStepBrowser, FORM_CLASS):
    """Function Centric Wizard Step: Exposure Layer From Browser"""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizad Dialog).
        :type parent: QWidget

        """
        WizardStepBrowser.__init__(self, parent)
        self.tvBrowserExposure.setModel(self.proxy_model)
        self.tvBrowserExposure.selectionModel().selectionChanged.connect(
            self.tvBrowserExposure_selection_changed)

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return self.get_layer_description_from_browser('exposure')[0]

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_fc_explayer_origin
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        if self.parent.is_selected_layer_keywordless:
            # insert keyword creation thread here
            self.parent.parent_step = self
            self.parent.existing_keywords = None
            self.parent.set_mode_label_to_keywords_creation()
            new_step = self.parent.step_kw_purpose
        else:
            if layers_intersect(self.parent.hazard_layer,
                                self.parent.exposure_layer):
                new_step = self.parent.step_fc_agglayer_origin
            else:
                new_step = self.parent.step_fc_disjoint_layers
        return new_step

    def tvBrowserExposure_selection_changed(self):
        """Update layer description label"""
        (is_compatible, desc) = self.get_layer_description_from_browser(
            'exposure')
        self.lblDescribeBrowserExpLayer.setText(desc)
        self.parent.pbnNext.setEnabled(is_compatible)

    def set_widgets(self):
        """Set widgets on the Exposure Layer From Browser tab"""
        self.tvBrowserExposure_selection_changed()

        # Set icon
        exposure = self.parent.step_fc_functions1.selected_value(
            layer_purpose_exposure['key'])
        icon_path = resources_path(
            'img', 'wizard', 'keyword-subcategory-%s.svg' % (
                exposure['key'] or 'notset'))
        self.lblIconIFCWExposureFromBrowser.setPixmap(QPixmap(icon_path))
