from safe.utilities.i18n import tr

from safe.gui.tools.wizard.wizard_strings import (
    select_exposure_origin_question,
    select_explayer_from_canvas_question,
    select_explayer_from_browser_question)
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_step import WizardStep


FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcExpLayerOrigin(WizardStep, FORM_CLASS):
    """A docstring."""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return (bool(self.rbExpLayerFromCanvas.isChecked() or
                     self.rbExpLayerFromBrowser.isChecked()))

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        if self.parent.step_fc_hazlayer_origin.rbHazLayerFromCanvas.isChecked():
            new_step = self.parent.step_fc_hazlayer_from_canvas
        else:
            new_step = self.parent.step_fc_hazlayer_from_browser
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        if self.rbExpLayerFromCanvas.isChecked():
            new_step = self.parent.step_fc_explayer_from_canvas
        else:
            new_step = self.parent.step_fc_explayer_from_browser
        return new_step



    # noinspection PyPep8Naming
    def on_rbExpLayerFromCanvas_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.parent.pbnNext.setEnabled(True)

    # noinspection PyPep8Naming
    def on_rbExpLayerFromBrowser_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.parent.pbnNext.setEnabled(True)

    def set_widgets(self):
        """Set widgets on the Exposure Layer Origin Type tab"""
        # First, list available layers in order to check if there are
        # any available layers. Note This will be repeated in
        # set_widgets_step_fc_explayer_from_canvas because we need
        # to list them again after coming back from the Keyword Wizard.
        lst_wdg = self.parent.step_fc_explayer_from_canvas.lstCanvasExpLayers
        self.list_compatible_layers_from_canvas('exposure', lst_wdg)
        if lst_wdg.count():
            self.rbExpLayerFromCanvas.setText(tr(

                'I would like to use an exposure layer already loaded in QGIS'
                '\n'
                '(launches the %s for exposure if needed)'
            ) % self.parent.keyword_creation_wizard_name)
            self.rbExpLayerFromCanvas.setEnabled(True)
            self.rbExpLayerFromCanvas.click()
        else:
            self.rbExpLayerFromCanvas.setText(tr(

                'I would like to use an exposure layer already loaded in QGIS'
                '\n'
                '(no suitable layers found)'))
            self.rbExpLayerFromCanvas.setEnabled(False)
            self.rbExpLayerFromBrowser.click()

        # Set the memo labels on this and next (exposure) steps
        (_, exposure, _, exposure_constraints) = self.parent.\
            step_fc_functions1.selected_impact_function_constraints()

        layer_geometry = exposure_constraints['name']

        text = (select_exposure_origin_question % (
            layer_geometry,
            exposure['name'],
            self.parent.step_fc_function.selected_function()['name']))
        self.lblSelectExpLayerOriginType.setText(text)

        text = (select_explayer_from_canvas_question % (
            layer_geometry,
            exposure['name'],
            self.parent.step_fc_function.selected_function()['name']))
        self.parent.step_fc_explayer_from_canvas.lblSelectExposureLayer.setText(text)

        text = (select_explayer_from_browser_question % (
            layer_geometry,
            exposure['name'],
            self.parent.step_fc_function.selected_function()['name']))
        self.parent.step_fc_explayer_from_browser.lblSelectBrowserExpLayer.setText(text)
