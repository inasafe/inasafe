# coding=utf-8
"""InaSAFE Wizard Step Extent Selection."""

import logging

from safe import messaging as m
from safe.gui.tools.extent_selector_dialog import ExtentSelectorDialog
from safe.gui.tools.help.extent_selector_help import extent_mode_content
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)

LOGGER = logging.getLogger('InaSAFE')


class StepFcExtent(WizardStep, FORM_CLASS):

    """InaSAFE Wizard Step Extent Selection."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizard Dialog).
        :type parent: QWidget
        """
        WizardStep.__init__(self, parent)
        self.swExtent = None
        self.extent_dialog = None

    def is_ready_to_next_step(self):
        """Check if the step is complete.

        If so, there is no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return True

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to.
        :rtype: WizardStep instance or None
        """
        if self.validate_extent():
            new_step = self.parent.step_fc_summary
        else:
            new_step = self.parent.step_fc_extent_disjoint
        return new_step

    def validate_extent(self):
        """Check if the selected extent intersects source data.

        :returns: true if extent intersects both layers, false if is disjoint.
        :rtype: boolean
        """
        # TODO: Until we define have good extent behavior, always return True
        return True

    def start_capture_coordinates(self):
        """Enter the coordinate capture mode."""
        self.parent.hide()

    def stop_capture_coordinates(self):
        """Exit the coordinate capture mode."""
        self.extent_dialog._populate_coordinates()
        self.extent_dialog.canvas.setMapTool(
            self.extent_dialog.previous_map_tool)
        self.parent.show()

    def write_extent(self):
        """After the extent selection, save the extent and disconnect signals.
        """
        self.extent_dialog.accept()
        self.extent_dialog.clear_extent.disconnect(
            self.parent.dock.extent.clear_user_analysis_extent)
        self.extent_dialog.extent_defined.disconnect(
            self.parent.dock.define_user_analysis_extent)
        self.extent_dialog.capture_button.clicked.disconnect(
            self.start_capture_coordinates)
        self.extent_dialog.tool.rectangle_created.disconnect(
            self.stop_capture_coordinates)

    def set_widgets(self):
        """Set widgets on the Extent tab."""
        self.extent_dialog = ExtentSelectorDialog(
            self.parent.iface,
            self.parent.iface.mainWindow(),
            extent=self.parent.dock.extent.user_extent,
            crs=self.parent.dock.extent.crs)
        self.extent_dialog.tool.rectangle_created.disconnect(
            self.extent_dialog.stop_capture)
        self.extent_dialog.clear_extent.connect(
            self.parent.dock.extent.clear_user_analysis_extent)
        self.extent_dialog.extent_defined.connect(
            self.parent.dock.define_user_analysis_extent)
        self.extent_dialog.capture_button.clicked.connect(
            self.start_capture_coordinates)
        self.extent_dialog.tool.rectangle_created.connect(
            self.stop_capture_coordinates)

        self.extent_dialog.label.setText(tr(
            'Please specify extent of your analysis:'))

        if self.swExtent:
            self.swExtent.hide()

        self.swExtent = self.extent_dialog.main_stacked_widget
        self.layoutAnalysisExtent.addWidget(self.swExtent)

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        # noinspection SqlDialectInspection,SqlNoDataSourceInspection
        return tr('Extent Selection')

    def help_content(self):
        """Return the content of help for this step wizard.

        We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name} you will be allowed to specify '
            'which geographical region should be used for your analysis. '
            'There are a number of different modes that can be used which are '
            'described below:'
        ).format(step_name=self.step_name)))
        message.add(extent_mode_content())
        return message
