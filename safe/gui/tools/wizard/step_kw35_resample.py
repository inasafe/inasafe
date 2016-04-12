from safe.definitions import layer_purpose_exposure

from safe.utilities.gis import is_raster_layer

from safe.gui.tools.wizard.wizard_strings import allow_resampling_question
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_step import WizardStep


FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwResample(WizardStep, FORM_CLASS):
    """A docstring."""

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
        new_step = self.parent.step_kw_unit
        return new_step

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_kw_extrakeywords
        return new_step

    def selected_allowresampling(self):
        """Obtain the allow_resampling state selected by user.

        .. note:: Returns none if not set or not relevant

        :returns: Value of the allow_resampling or None for not-set.
        :rtype: boolean or None
        """
        if not is_raster_layer(self.parent.layer):
            return None

        if self.parent.step_kw_purpose.selected_purpose() != layer_purpose_exposure:
            return None

        # Only return false if checked, otherwise None for not-set.
        if self.chkAllowResample.isChecked():
            return False
        else:
            return None

    def set_widgets(self):
        """Set widgets on the Resample tab."""
        purpose = self.parent.step_kw_purpose.selected_purpose()
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        layer_mode = self.parent.step_kw_layermode.selected_layermode()
        self.lblSelectAllowResample.setText(
            allow_resampling_question % (
                subcategory['name'], purpose['name'], layer_mode['name']))

        # Set value based on existing keyword (if already assigned)
        if self.parent.get_existing_keyword('allow_resampling') is False:
            self.chkAllowResample.setChecked(True)
