# coding=utf-8
"""Wizard Help Widget."""

# noinspection PyPackageRequirements
from qgis.PyQt.QtWidgets import QWidget

from safe.utilities.resources import get_ui_class, html_header, html_footer

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

HELP_WIDGET = get_ui_class('wizard/wizard_help.ui')


class WizardHelp(QWidget, HELP_WIDGET):

    """An abstract step.

    Each step is a tab meant to be placed in the wizard.
    Each derived class must implement mandatory methods.
    """

    def __init__(self, parent=None):
        """Constructor

        :param parent: parent - widget to use as parent.
        :type parent: QWidget
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)

        self.wizard_step = None
        self.next_button_state = False
        self.back_button_state = False

    def show_help(self, wizard_step):
        """Set wizard step and show the help text."""
        self.wizard_step = wizard_step

        header = html_header()
        footer = html_footer()

        content = header

        message = self.wizard_step.help()

        content += message.to_html()
        content += footer

        self.help_web_view.setHtml(content)

        # Store buttons' state
        self.next_button_state = self.parent.pbnNext.isEnabled()
        self.back_button_state = self.parent.pbnBack.isEnabled()

        # Disable those buttons
        self.parent.pbnNext.setEnabled(False)
        self.parent.pbnBack.setEnabled(False)

    def restore_button_state(self):
        """Helper to restore button state."""
        self.parent.pbnNext.setEnabled(self.next_button_state)
        self.parent.pbnBack.setEnabled(self.back_button_state)
