# coding=utf-8
"""InaSAFE Wizard Step Title."""

from safe import messaging as m
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwTitle(WizardStep, FORM_CLASS):

    """InaSAFE Wizard Step Title."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizard Dialog).
        :type parent: QWidget

        """
        WizardStep.__init__(self, parent)
        title_tooltip = self.tr('Title of the layer.')
        self.lblTitle.setToolTip(title_tooltip)
        self.leTitle.setToolTip(title_tooltip)

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return bool(self.leTitle.text())

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_kw_summary
        return new_step

    # noinspection PyPep8Naming
    def on_leTitle_textChanged(self):
        """Unlock the Next button

        .. note:: This is an automatic Qt slot
           executed when the title value changes.
        """
        self.parent.pbnNext.setEnabled(bool(self.leTitle.text()))

    def set_widgets(self):
        """Set widgets on the Title tab."""
        # Set title from keyword first, if not found use layer name
        if self.parent.layer:
            if self.parent.get_existing_keyword('title'):
                title = self.parent.get_existing_keyword('title')
            else:
                title = self.parent.layer.name()
            self.leTitle.setText(title)

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return tr('Title Step')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you will be able to '
            'set the title of this layer that will show up in the '
            'analysis report').format(step_name=self.step_name)))
        return message
