# noinspection PyPackageRequirements
from PyQt4.QtGui import QPixmap
from safe.utilities.resources import resources_path

from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_step import WizardStep


FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcAggLayerDisjoint(WizardStep, FORM_CLASS):
    """A docstring."""

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
        if self.parent.step_fc_agglayer_origin.rbAggLayerFromCanvas.isChecked():
            new_step = self.parent.step_fc_agglayer_from_canvas
        else:
            new_step = self.parent.step_fc_agglayer_from_browser
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_fc_extent
        return new_step

    def set_widgets(self):
        """Set widgets on the Aggregation Layer Disjoint tab"""
        self.lblIconDisjoint_2.setPixmap(
            QPixmap(resources_path('img', 'wizard', 'icon-stop.svg')))
