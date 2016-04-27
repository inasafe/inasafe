# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Function Centric Wizard Step: Aggregation Layer Origin

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

from safe.utilities.i18n import tr

from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_step import WizardStep


FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcAggLayerOrigin(WizardStep, FORM_CLASS):
    """Function Centric Wizard Step: Aggregation Layer Origin"""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return (bool(self.rbAggLayerFromCanvas.isChecked() or
                     self.rbAggLayerFromBrowser.isChecked() or
                     self.rbAggLayerNoAggregation.isChecked()))

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        if self.parent.step_fc_explayer_origin.rbExpLayerFromCanvas.isChecked():
            new_step = self.parent.step_fc_explayer_from_canvas
        else:
            new_step = self.parent.step_fc_explayer_from_browser
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        if self.rbAggLayerFromCanvas.isChecked():
            new_step = self.parent.step_fc_agglayer_from_canvas
        elif self.rbAggLayerFromBrowser.isChecked():
            new_step = self.parent.step_fc_agglayer_from_browser
        else:
            new_step = self.parent.step_fc_extent
        return new_step

    # noinspection PyPep8Naming
    def on_rbAggLayerFromCanvas_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.parent.pbnNext.setEnabled(True)

    # noinspection PyPep8Naming
    def on_rbAggLayerFromBrowser_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.parent.pbnNext.setEnabled(True)

    # noinspection PyPep8Naming
    def on_rbAggLayerNoAggregation_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.parent.pbnNext.setEnabled(True)

    def set_widgets(self):
        """Set widgets on the Aggregation Layer Origin Type tab"""
        # First, list available layers in order to check if there are
        # any available layers. Note This will be repeated in
        # set_widgets_step_fc_agglayer_from_canvas because we need
        # to list them again after coming back from the Keyword Wizard.
        self.parent.step_fc_agglayer_from_canvas.\
            list_compatible_canvas_layers()
        lst_wdg = self.parent.step_fc_agglayer_from_canvas.lstCanvasAggLayers
        if lst_wdg.count():
            self.rbAggLayerFromCanvas.setText(tr(
                'I would like to use an aggregation layer already loaded in '
                'QGIS\n'
                '(launches the %s for aggregation if needed)'
            ) % self.parent.keyword_creation_wizard_name)
            self.rbAggLayerFromCanvas.setEnabled(True)
            self.rbAggLayerFromCanvas.click()
        else:
            self.rbAggLayerFromCanvas.setText(tr(
                'I would like to use an aggregation layer already loaded in '
                'QGIS\n'
                '(no suitable layers found)'))
            self.rbAggLayerFromCanvas.setEnabled(False)
            self.rbAggLayerFromBrowser.click()
