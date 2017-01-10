# coding=utf-8
"""InaSAFE Wizard Analysis Summary step."""

from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

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
