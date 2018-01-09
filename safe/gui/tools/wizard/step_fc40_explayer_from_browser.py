# coding=utf-8
"""InaSAFE Wizard Step Exposure Layer Browser."""

# noinspection PyPackageRequirements
from PyQt4.QtGui import QPixmap

from safe import messaging as m
from safe.definitions.layer_purposes import layer_purpose_exposure
from safe.gui.tools.wizard.utilities import layers_intersect, get_image_path
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_step_browser import WizardStepBrowser
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepFcExpLayerFromBrowser(WizardStepBrowser, FORM_CLASS):

    """InaSAFE Wizard Step Exposure Layer Browser."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizard Dialog).
        :type parent: QWidget
        """
        WizardStepBrowser.__init__(self, parent)
        self.tvBrowserExposure.setModel(self.proxy_model)
        self.tvBrowserExposure.selectionModel().selectionChanged.connect(
            self.tvBrowserExposure_selection_changed)

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
        no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return self.get_layer_description_from_browser('exposure')[0]

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
            if layers_intersect(self.parent.hazard_layer,
                                self.parent.exposure_layer):
                new_step = self.parent.step_fc_agglayer_origin
            else:
                new_step = self.parent.step_fc_disjoint_layers
        return new_step

    def tvBrowserExposure_selection_changed(self):
        """Update layer description label."""
        (is_compatible, desc) = self.get_layer_description_from_browser(
            'exposure')
        self.lblDescribeBrowserExpLayer.setText(desc)
        self.parent.pbnNext.setEnabled(is_compatible)

    def set_widgets(self):
        """Set widgets on the Exposure Layer From Browser tab."""
        self.tvBrowserExposure_selection_changed()

        # Set icon
        exposure = self.parent.step_fc_functions1.selected_value(
            layer_purpose_exposure['key'])
        icon_path = get_image_path(exposure)
        self.lblIconIFCWExposureFromBrowser.setPixmap(QPixmap(icon_path))

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        # noinspection SqlDialectInspection,SqlNoDataSourceInspection
        return tr('Select Exposure from Browser Step')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, You can choose a exposure '
            'layer from the list of layers from local disk or postgres '
            'database that matches with the geometry and exposure type you '
            'set in the previous step').format(step_name=self.step_name)))
        return message
