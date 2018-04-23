# coding=utf-8
"""InaSAFE Wizard Step Exposure Layer Origin."""

# noinspection PyPackageRequirements
from qgis.PyQt.QtGui import QPixmap

from safe import messaging as m
from safe.gui.tools.wizard.utilities import get_image_path
from safe.gui.tools.wizard.wizard_step import (
    WizardStep, get_wizard_step_ui_class)
from safe.gui.tools.wizard.wizard_strings import (
    select_exposure_origin_question,
    select_explayer_from_canvas_question,
    select_explayer_from_browser_question)
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcExpLayerOrigin(WizardStep, FORM_CLASS):
    """InaSAFE Wizard Step Exposure Layer Origin."""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return (bool(self.rbExpLayerFromCanvas.isChecked() or
                     self.rbExpLayerFromBrowser.isChecked()))

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
        """Set widgets on the Exposure Layer Origin Type tab."""
        # First, list available layers in order to check if there are
        # any available layers. Note This will be repeated in
        # set_widgets_step_fc_explayer_from_canvas because we need
        # to list them again after coming back from the Keyword Wizard.
        self.parent.step_fc_explayer_from_canvas.\
            list_compatible_canvas_layers()
        lst_wdg = self.parent.step_fc_explayer_from_canvas.lstCanvasExpLayers
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
        (_, exposure, _, exposure_constraints) = self.\
            parent.selected_impact_function_constraints()

        layer_geometry = exposure_constraints['name']

        text = (select_exposure_origin_question % (
            layer_geometry, exposure['name']))
        self.lblSelectExpLayerOriginType.setText(text)

        text = (select_explayer_from_canvas_question % (
            layer_geometry, exposure['name']))
        self.parent.step_fc_explayer_from_canvas.lblSelectExposureLayer.\
            setText(text)

        text = (select_explayer_from_browser_question % (
            layer_geometry, exposure['name']))
        self.parent.step_fc_explayer_from_browser.lblSelectBrowserExpLayer.\
            setText(text)

        # Set icon
        icon_path = get_image_path(exposure)
        self.lblIconIFCWExposureOrigin.setPixmap(QPixmap(icon_path))

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return tr('Exposure Layer Origin')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you can choose where your '
            'exposure layer come from. The option for choosing exposure layer '
            'from QGIS can not be chosen if there is no exposure layer in '
            'QGIS.').format(step_name=self.step_name)))
        return message
