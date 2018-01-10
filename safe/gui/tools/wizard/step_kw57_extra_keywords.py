# coding=utf-8
"""InaSAFE Wizard Step Extra Keywords."""

import pytz

from collections import OrderedDict
from datetime import datetime

from PyQt4.QtGui import (
    QLineEdit, QDateTimeEdit, QDoubleSpinBox, QComboBox, QCheckBox
)
from PyQt4.QtCore import Qt

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
from safe.common.custom_logging import LOGGER

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
        self.widgets_dict = OrderedDict()

    def is_ready_to_next_step(self):
        """Check if the step is complete.

        If so, there is no reason to block the Next button.

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
        self.description_label.setText(
            'In this step you can set some extra keywords for the layer. This '
            'keywords can be used for creating richer reporting or map.')
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        if subcategory == hazard_volcanic_ash:
            # Volcano name
            volcano_name_checkbox = QCheckBox(tr('Volcano Name'))
            volcano_name_line_edit = QLineEdit()

            # Alert level
            alert_level_checkbox = QCheckBox(tr('Alert Level'))
            alert_level_combo_box = QComboBox()
            alert_level_combo_box.addItem(tr('Normal'))
            alert_level_combo_box.addItem(tr('Advisory'))
            alert_level_combo_box.addItem(tr('Watch'))
            alert_level_combo_box.addItem(tr('Warning'))
            alert_level_combo_box.setCurrentIndex(0)

            # Eruption height in metres
            eruption_height_checkbox = QCheckBox(
                tr('Eruption height (metres)'))
            eruption_height_spin_box = QDoubleSpinBox()
            eruption_height_spin_box.setMinimum(0)
            eruption_height_spin_box.setMaximum(9999999)
            eruption_height_spin_box.setSuffix(tr(' metres'))

            # Event time
            event_time_checkbox = QCheckBox(tr('Event time'))
            event_time_picker = QDateTimeEdit()
            event_time_picker.setCalendarPopup(True)
            event_time_picker.setDisplayFormat('hh:mm:ss, d MMM yyyy')
            event_time_picker.setDateTime(datetime.now())

            # Timezone
            timezone_checkbox = QCheckBox(tr('Timezone'))
            timezone_combo_box = QComboBox()
            for timezone in pytz.common_timezones:
                timezone_combo_box.addItem(timezone)
            index = timezone_combo_box.findText('Asia/Jakarta')
            timezone_combo_box.setCurrentIndex(index)

            self.widgets_dict[extra_keyword_volcano_name['key']] = [
                volcano_name_checkbox,
                volcano_name_line_edit
            ]
            self.widgets_dict[extra_keyword_volcano_alert_level['key']] = [
                alert_level_checkbox,
                alert_level_combo_box
            ]
            self.widgets_dict[extra_keyword_eruption_height['key']] = [
                eruption_height_checkbox,
                eruption_height_spin_box
            ]
            self.widgets_dict[
                extra_keyword_volcano_eruption_event_time['key']] = [
                event_time_checkbox,
                event_time_picker
            ]
            self.widgets_dict[extra_keyword_time_zone['key']] = [
                timezone_checkbox,
                timezone_combo_box
            ]

            index = 0
            for key, widgets in self.widgets_dict.items():
                self.extra_keywords_layout.addWidget(widgets[0], index, 0)
                self.extra_keywords_layout.addWidget(widgets[1], index, 1)
                widgets[0].stateChanged.connect(widgets[1].setEnabled)
                widgets[0].setChecked(True)
                index += 1

        self.set_existing_extra_keywords()

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

    def get_extra_keywords(self):
        """Obtain extra keywords from the current state."""
        extra_keywords = {}
        for key, widgets in self.widgets_dict.items():
            if widgets[0].isChecked():
                if isinstance(widgets[1], QLineEdit):
                    extra_keywords[key] = widgets[1].text()
                elif isinstance(widgets[1], QComboBox):
                    extra_keywords[key] = widgets[1].currentText()
                elif isinstance(widgets[1], QDoubleSpinBox):
                    extra_keywords[key] = widgets[1].value()
                elif isinstance(widgets[1], QDateTimeEdit):
                    extra_keywords[key] = widgets[1].dateTime().toString(
                        Qt.ISODate)
        return extra_keywords

    def set_existing_extra_keywords(self):
        """Set extra keywords from the value from metadata."""
        extra_keywords = self.parent.get_existing_keyword('extra_keywords')
        for key, widgets in self.widgets_dict.items():
            value = extra_keywords.get(key)
            LOGGER.debug('%s : %s' % (key, value))
            if value is None:
                widgets[0].setChecked(False)
            else:
                widgets[0].setChecked(True)
                if isinstance(widgets[1], QLineEdit):
                    widgets[1].setText(value)
                elif isinstance(widgets[1], QComboBox):
                    value_index = widgets[1].findText(value)
                    widgets[1].setCurrentIndex(value_index)
                elif isinstance(widgets[1], QDoubleSpinBox):
                    widgets[1].setValue(value)
                elif isinstance(widgets[1], QDateTimeEdit):
                    try:
                        value_datetime = datetime.strptime(
                            value, "%Y-%m-%dT%H:%M:%S")
                        widgets[1].setDateTime(value_datetime)
                    except ValueError:
                        LOGGER.info('Failed to convert %s to datetime' % value)
