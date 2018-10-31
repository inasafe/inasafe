# coding=utf-8
"""InaSAFE Wizard Step Hazard Layer Origin."""

# noinspection PyPackageRequirements
from qgis.PyQt.QtGui import QPixmap

from safe import messaging as m
from safe.gui.tools.wizard.utilities import get_image_path
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_strings import (
    select_hazard_origin_question,
    select_hazlayer_from_canvas_question,
    select_hazlayer_from_browser_question)
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcHazLayerOrigin(WizardStep, FORM_CLASS):
    """InaSAFE Wizard Step Hazard Layer Origin."""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return (bool(self.rbHazLayerFromCanvas.isChecked()
                     or self.rbHazLayerFromBrowser.isChecked()))

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        if self.rbHazLayerFromCanvas.isChecked():
            new_step = self.parent.step_fc_hazlayer_from_canvas
        else:
            new_step = self.parent.step_fc_hazlayer_from_browser
        return new_step

    # noinspection PyPep8Naming
    def on_rbHazLayerFromCanvas_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.parent.pbnNext.setEnabled(True)

    # noinspection PyPep8Naming
    def on_rbHazLayerFromBrowser_toggled(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.parent.pbnNext.setEnabled(True)

    def set_widgets(self):
        """Set widgets on the Hazard Layer Origin Type tab."""
        # First, list available layers in order to check if there are
        # any available layers. Note This will be repeated in
        # set_widgets_step_fc_hazlayer_from_canvas because we need
        # to list them again after coming back from the Keyword Wizard.
        self.parent.step_fc_hazlayer_from_canvas.\
            list_compatible_canvas_layers()
        lst_wdg = self.parent.step_fc_hazlayer_from_canvas.lstCanvasHazLayers
        if lst_wdg.count():
            wizard_name = self.parent.keyword_creation_wizard_name
            self.rbHazLayerFromCanvas.setText(tr(
                'I would like to use a hazard layer already loaded in QGIS\n'
                '(launches the {wizard_name} for hazard if needed)'
            ).format(wizard_name=wizard_name))
            self.rbHazLayerFromCanvas.setEnabled(True)
            self.rbHazLayerFromCanvas.click()
        else:
            self.rbHazLayerFromCanvas.setText(tr(
                'I would like to use a hazard layer already loaded in QGIS\n'
                '(no suitable layers found)'))
            self.rbHazLayerFromCanvas.setEnabled(False)
            self.rbHazLayerFromBrowser.click()

        # Set the memo labels on this and next (hazard) steps
        (hazard, _, hazard_constraints, _) = self.\
            parent.selected_impact_function_constraints()

        layer_geometry = hazard_constraints['name']

        text = (select_hazard_origin_question % (
            layer_geometry, hazard['name']))
        self.lblSelectHazLayerOriginType.setText(text)

        text = (select_hazlayer_from_canvas_question % (
            layer_geometry, hazard['name']))
        self.parent.step_fc_hazlayer_from_canvas.\
            lblSelectHazardLayer.setText(text)

        text = (select_hazlayer_from_browser_question % (
            layer_geometry, hazard['name']))
        self.parent.step_fc_hazlayer_from_browser.\
            lblSelectBrowserHazLayer.setText(text)

        # Set icon
        icon_path = get_image_path(hazard)
        self.lblIconIFCWHazardOrigin.setPixmap(QPixmap(icon_path))

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return tr('Hazard Layer Origin')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you can choose where your '
            'hazard layer come from. The option for choosing hazard layer '
            'from QGIS can not be chosen if there is no hazard layer in QGIS.'
        ).format(step_name=self.step_name)))
        return message
