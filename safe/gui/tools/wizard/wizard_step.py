# coding=utf-8
"""Wizard Step Abstract Class."""

import os
import re

# noinspection PyPackageRequirements
from qgis.PyQt.QtWidgets import QWidget

from safe import messaging as m
from safe.gui.tools.wizard import STEP_KW, STEP_FC
from safe.messaging import styles
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.resources import get_ui_class

SUBSECTION_STYLE = styles.SUBSECTION_LEVEL_3_STYLE

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def get_wizard_step_ui_class(py_file_name):
    return get_ui_class(os.path.join(
        'wizard', re.sub(r"pyc?$", "ui", os.path.basename(py_file_name))))


class WizardStep(QWidget):

    """An abstract step.

    Each step is a tab meant to be placed in the wizard.
    Each derived class must implement mandatory methods.
    """

    def __init__(self, parent=None):
        """Constructor.

        :param parent: parent - widget to use as parent.
        :type parent: safe.gui.tools.wizard.wizard_dialog.WizardDialog
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)

        self.keyword_io = KeywordIO()

    # noinspection PyUnresolvedReferences,PyMethodMayBeStatic
    def auto_select_one_item(self, list_widget):
        """Select item in the list in list_widget if it's the only item.

        :param list_widget: The list widget that want to be checked.
        :type list_widget: QListWidget
        """
        if list_widget.count() == 1 and list_widget.currentRow() == -1:
            list_widget.setCurrentRow(0)

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
           no reason to block the Next button.

           This method must be implemented in derived classes.
           Otherwise no exception is raised but the return value is False.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return False

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

           This method must be implemented in derived classes.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        raise NotImplementedError("The current step class doesn't implement \
            the get_next_step method")

    def set_widgets(self):
        """Set all widgets on the tab.

        This method must be implemented in derived classes.
        """
        raise NotImplementedError("The current step class doesn't implement \
            the set_widgets method")

    @property
    def step_type(self):
        """Whether it's a IFCW step or Keyword Wizard Step."""
        if 'stepfc' in self.__class__.__name__.lower():
            return STEP_FC
        if 'stepkw' in self.__class__.__name__.lower():
            return STEP_KW

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return self.__class__.__name__

    def help(self):
        """Return full help message for the step wizard.

        :returns: A message object contains help text.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Brand())
        message.add(self.help_heading())
        message.add(self.help_content())
        return message

    def help_heading(self):
        """Helper method that returns just the header.

        :returns: A heading object.
        :rtype: safe.messaging.heading.Heading
        """
        message = m.Heading(
            tr('Help for {step_name}').format(step_name=self.step_name),
            **SUBSECTION_STYLE)
        return message

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        help_message = m.Message()
        help_message.add(m.Text(tr('No help text for this wizard step, yet.')))
        return help_message
