from safe.gui.tools.function_options_dialog import (
    FunctionOptionsDialog)

from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_step import WizardStep


FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcParams(WizardStep, FORM_CLASS):
    """A docstring."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizad Dialog).
        :type parent: QWidget

        """
        WizardStep.__init__(self, parent)
        self.parameter_dialog = None
        self.twParams = None

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return True

    def get_previous_step(self):
        """Find the proper step when user clicks the Previous button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_fc_extent
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_fc_summary
        return new_step

    def set_widgets(self):
        """Set widgets on the Params tab"""

        # TODO Put the params to metadata! Now we need to import the IF class.
        # Notes: Why don't we store impact_function to class attribute?
        impact_function_id = self.parent.\
            step_fc_function.selected_function()['id']
        impact_function = self.impact_function_manager.get(
            impact_function_id)
        if not impact_function:
            return
        self.if_params = None
        if hasattr(impact_function, 'parameters'):
            self.if_params = impact_function.parameters

        text = self.tr(
            'Please set impact functions parameters.<br/>Parameters for '
            'impact function "%s" that can be modified are:' %
            impact_function_id)
        self.lblSelectIFParameters.setText(text)

        self.parameter_dialog = FunctionOptionsDialog(self)
        self.parameter_dialog.set_dialog_info(impact_function_id)
        self.parameter_dialog.build_form(self.if_params)

        if self.twParams:
            self.twParams.hide()

        self.twParams = self.parameter_dialog.tabWidget
        self.layoutIFParams.addWidget(self.twParams)
