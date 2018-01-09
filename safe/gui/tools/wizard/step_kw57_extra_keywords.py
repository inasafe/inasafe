# coding=utf-8
"""InaSAFE Wizard Step Extra Keywords."""

from PyQt4.QtGui import (
    QLabel, QLineEdit, QDateTimeEdit, QDoubleSpinBox, QComboBox, QCheckBox
)
from collections import OrderedDict

from datetime import datetime
import pytz
from safe import messaging as m
from safe.definitions.hazard import hazard_volcanic_ash
from safe.definitions.extra_keywords import (
    extra_keyword_volcano_name,
    extra_keyword_volcano_alert_level,
    extra_keyword_eruption_height,
    extra_keyword_volcano_eruption_event_time,
    extra_keyword_time_zone,
)
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.utilities.i18n import tr
from safe.utilities.unicode import get_unicode

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

FORM_CLASS = get_wizard_step_ui_class(__file__)


class StepKwExtraKeywords(WizardStep, FORM_CLASS):

    """InaSAFE Wizard Step Source."""

    def __init__(self, parent=None):
        """Constructor for the tab.

        :param parent: parent - widget to use as parent (Wizard Dialog).
        :type parent: QWidget

        """
        WizardStep.__init__(self, parent)

    def is_ready_to_next_step(self):
        """Check if the step is complete. If so, there is
            no reason to block the Next button.

        :returns: True if new step may be enabled.
        :rtype: bool
        """
        return True

    def get_next_step(self):
        """Find the proper step when user clicks the Next button.

        :returns: The step to be switched to
        :rtype: WizardStep instance or None
        """
        new_step = self.parent.step_kw_title
        return new_step

    def set_widgets(self):
        """Set widgets on the extra keywords tab."""
        self.description_label.setText('Lorem ipsum')
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        if subcategory == hazard_volcanic_ash:
            # Volcano name
            self.volcano_name_checkbox = QCheckBox(tr('Volcano Name'))
            self.volcano_name_line_edit = QLineEdit()

            # Alert level
            self.alert_level_checkbox = QCheckBox(tr('Alert Level'))
            self.alert_level_combo_box = QComboBox()
            self.alert_level_combo_box.addItem(tr('Normal'))
            self.alert_level_combo_box.addItem(tr('Advisory'))
            self.alert_level_combo_box.addItem(tr('Watch'))
            self.alert_level_combo_box.addItem(tr('Warning'))
            self.alert_level_combo_box.setCurrentIndex(0)

            # Eruption height in metres
            self.eruption_height_checkbox = QCheckBox(
                tr('Eruption height (metres)'))
            self.eruption_height_spin_box = QDoubleSpinBox()
            self.eruption_height_spin_box.setMinimum(0)
            self.eruption_height_spin_box.setMaximum(9999999)
            self.eruption_height_spin_box.setSuffix(tr(' metres'))

            # Event time
            self.event_time_checkbox = QCheckBox(tr('Event time'))
            self.event_time_picker = QDateTimeEdit()
            self.event_time_picker.setCalendarPopup(True)
            self.event_time_picker.setDisplayFormat('hh:mm:ss, d MMM yyyy')
            self.event_time_picker.setDateTime(datetime.now())

            # Timezone
            self.timezone_checkbox = QCheckBox(tr('Timezone'))
            self.timezone_combo_box = QComboBox()
            for timezone in pytz.common_timezones:
                self.timezone_combo_box.addItem(timezone)
            index = self.timezone_combo_box.findText('Asia/Jakarta')
            self.timezone_combo_box.setCurrentIndex(index)

            widgets_dict = OrderedDict()
            widgets_dict[extra_keyword_volcano_name['key']] = [
                self.volcano_name_checkbox,
                self.volcano_name_line_edit
            ]
            widgets_dict[extra_keyword_volcano_alert_level['key']] = [
                self.alert_level_checkbox,
                self.alert_level_combo_box
            ]
            widgets_dict[extra_keyword_eruption_height['key']] = [
                self.eruption_height_checkbox,
                self.eruption_height_spin_box
            ]
            widgets_dict[extra_keyword_volcano_eruption_event_time['key']] = [
                self.event_time_checkbox,
                self.event_time_picker
            ]
            widgets_dict[extra_keyword_time_zone['key']] = [
                self.timezone_checkbox,
                self.timezone_combo_box
            ]

            index = 0
            for key, widgets in widgets_dict.iteritems():
                self.extra_keywords_layout.addWidget(widgets[0], index, 0)
                self.extra_keywords_layout.addWidget(widgets[1], index, 1)
                widgets[0].stateChanged.connect(widgets[1].setEnabled)
                widgets[0].setChecked(True)
                index += 1

    @property
    def step_name(self):
        """Get the human friendly name for the wizard step.

        :returns: The name of the wizard step.
        :rtype: str
        """
        return tr('InaSAFE Extra Keywords')

    def help_content(self):
        """Return the content of help for this step wizard.

            We only needs to re-implement this method in each wizard step.

        :returns: A message object contains help.
        :rtype: m.Message
        """
        message = m.Message()
        message.add(m.Paragraph(tr(
            'In this wizard step: {step_name}, you will be able to '
            'set some extra keywords for a richer reporting.').format(
            step_name=self.step_name)))
        return message
