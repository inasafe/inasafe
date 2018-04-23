# coding=utf-8
"""InaSAFE Wizard Step Hazard Layer Browser."""

# noinspection PyPackageRequirements
from qgis.PyQt.QtGui import QPixmap

from safe import messaging as m
from safe.definitions.layer_purposes import layer_purpose_hazard
from safe.gui.tools.wizard.utilities import get_image_path
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_step_browser import WizardStepBrowser
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcHazLayerFromBrowser(WizardStepBrowser, FORM_CLASS):
    """InaSAFE Wizard Step Hazard Layer Browser."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizard Dialog).
        :type parent: QWidget

        """
        WizardStepBrowser.__init__(self, parent)
        self.tvBrowserHazard.setModel(self.proxy_model)
        self.tvBrowserHazard.selectionModel().selectionChanged.connect(
            self.tvBrowserHazard_selection_changed)

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return self.get_layer_description_from_browser('hazard')[0]

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        if self.parent.is_selected_layer_keywordless:
            # insert keyword creation thread here
            self.parent.parent_step = self
            self.parent.existing_keywords = None
            self.parent.set_mode_label_to_keywords_creation()
            new_step = self.parent.step_kw_purpose
        else:
            new_step = self.parent.step_fc_explayer_origin
        return new_step

    # noinspection PyPep8Naming
    def tvBrowserHazard_selection_changed(self):
        """Update layer description label."""
        (is_compatible, desc) = self.get_layer_description_from_browser(
            'hazard')
        self.lblDescribeBrowserHazLayer.setText(desc)
        self.lblDescribeBrowserHazLayer.setEnabled(is_compatible)
        self.parent.pbnNext.setEnabled(is_compatible)

    def set_widgets(self):
        """Set widgets on the Hazard Layer From Browser tab."""
        self.tvBrowserHazard_selection_changed()

        # Set icon
        hazard = self.parent.step_fc_functions1.selected_value(
            layer_purpose_hazard['key'])
        icon_path = get_image_path(hazard)
        self.lblIconIFCWHazardFromBrowser.setPixmap(QPixmap(icon_path))

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        # noinspection SqlDialectInspection,SqlNoDataSourceInspection
        return tr('Select Hazard from Browser Step')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, You can choose a hazard layer '
            'from the list of layers from local disk or postgres database '
            'that matches with the geometry and hazard type you set in the '
            'previous step').format(step_name=self.step_name)))
        return message
