# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid -**InaSAFE Wizard**

This module provides: Keyword Wizard Step: Layer Title

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.gui.tools.wizard.wizard_step import WizardStep

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwTitle(WizardStep, FORM_CLASS):
    """Keyword Wizard Step: Layer Title"""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizad Dialog).
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
