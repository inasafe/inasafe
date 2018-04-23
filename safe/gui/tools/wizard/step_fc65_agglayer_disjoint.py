# coding=utf-8
"""InaSAFE Wizard Step Aggregation Layer Disjoint."""

# noinspection PyPackageRequirements
from qgis.PyQt.QtGui import QPixmap

from safe import messaging as m
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.utilities.i18n import tr
from safe.utilities.resources import resources_path

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcAggLayerDisjoint(WizardStep, FORM_CLASS):

    """InaSAFE Wizard Step Aggregation Layer Disjoint."""

    def is_ready_to_next_step(self):
        """Check if the step is complete.

        If so, there is no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        # Never go further if layers disjoint!
        return False

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        return None

    def set_widgets(self):
        """Set widgets on the Aggregation Layer Disjoint tab."""
        self.lblIconDisjoint_2.setPixmap(
            QPixmap(resources_path('img', 'wizard', 'icon-stop.svg')))

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        # noinspection SqlDialectInspection,SqlNoDataSourceInspection
        return tr('Disjoint Layers')

    def help_content(self):
        """Return the content of help for this step wizard.

        We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you will know that your '
            'exposure and hazard layer do not intersect with your aggregation '
            'layer. You can not go forward and you need to change the layer '
            'to run an analysis.'
        ).format(step_name=self.step_name)))
        return message
