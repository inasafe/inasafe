# coding=utf-8
"""InaSAFE Wizard Step Aggregation Layer Origin."""

from PyQt4.QtGui import QPixmap

from safe import messaging as m
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcAggLayerOrigin(WizardStep, FORM_CLASS):
    """InaSAFE Wizard Step Aggregation Layer Origin."""

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return (bool(self.rbAggLayerFromCanvas.isChecked() or
                     self.rbAggLayerFromBrowser.isChecked() or
                     self.rbAggLayerNoAggregation.isChecked()))

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
            new_step = self.parent.step_fc_summary
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
           Also, clear any previously set aggregation layer

        .. note:: This is an automatic Qt slot
           executed when the radiobutton is activated.
        """
        self.parent.aggregation_layer = None
        self.parent.pbnNext.setEnabled(True)

    def set_widgets(self):
        """Set widgets on the Aggregation Layer Origin Type tab."""
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

        # Set icon
        self.lblIconIFCWAggregationOrigin.setPixmap(QPixmap(None))

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return tr('Aggregation Layer Origin')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you can choose where your '
            'aggregation layer come from. The option for choosing aggregation '
            'layer from QGIS can not be chosen if there is no aggregation '
            'layer in QGIS.').format(step_name=self.step_name)))
        return message
