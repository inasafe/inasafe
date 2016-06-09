# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides:
  Function Centric Wizard Step: Aggregation Layer From Browser

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


from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_step_browser import WizardStepBrowser
from safe.gui.tools.wizard.wizard_utils import layers_intersect


FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcAggLayerFromBrowser(WizardStepBrowser, FORM_CLASS):
    """Function Centric Wizard Step: Aggregation Layer From Browser"""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizad Dialog).
        :type parent: QWidget

        """
        WizardStepBrowser.__init__(self, parent)
        self.tvBrowserAggregation.setModel(self.proxy_model)
        self.tvBrowserAggregation.selectionModel().selectionChanged.connect(
            self.tvBrowserAggregation_selection_changed)

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return self.get_layer_description_from_browser('aggregation')[0]

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_fc_agglayer_origin
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
            if layers_intersect(self.parent.exposure_layer,
                                self.parent.aggregation_layer):
                new_step = self.parent.step_fc_extent
            else:
                new_step = self.parent.step_fc_agglayer_disjoint
        return new_step

    # noinspection PyPep8Naming
    def tvBrowserAggregation_selection_changed(self):
        """Update layer description label"""
        (is_compatible, desc) = self.get_layer_description_from_browser(
            'aggregation')
        self.lblDescribeBrowserAggLayer.setText(desc)
        self.parent.pbnNext.setEnabled(is_compatible)

    def set_widgets(self):
        """Set widgets on the Aggregation Layer From Browser tab"""
        self.tvBrowserAggregation_selection_changed()
