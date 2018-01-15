# coding=utf-8
"""InaSAFE Wizard Step Extra Keywords."""

from collections import OrderedDict
from datetime import datetime

import pytz
from PyQt4.QtCore import Qt
from PyQt4.QtGui import (
    QLineEdit, QDateTimeEdit, QDoubleSpinBox, QComboBox, QCheckBox
)

from safe import messaging as m
from safe.common.custom_logging import LOGGER
from safe.definitions.extra_keywords import (
    extra_keyword_volcano_name,
    extra_keyword_region,
    extra_keyword_volcano_alert_level,
    extra_keyword_eruption_height,
    extra_keyword_volcano_eruption_event_time,
    extra_keyword_time_zone,
    extra_keyword_volcano_longitude,
    extra_keyword_volcano_latitude,
    extra_keyword_volcano_height,
    extra_keyword_volcano_event_id,
)
from safe.definitions.hazard import hazard_volcanic_ash
from safe.gui.tools.wizard.wizard_step import WizardStep
from safe.gui.tools.wizard.wizard_step import get_wizard_step_ui_class
from safe.utilities.i18n import tr

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
            volcano_name_checkbox = QCheckBox()
            volcano_name_line_edit = QLineEdit()

            # Volcano longitude
            volcano_longitude_checkbox = QCheckBox()
            volcano_longitude_spin_box = QDoubleSpinBox()
            volcano_longitude_spin_box.setMinimum(-180)
            volcano_longitude_spin_box.setMaximum(180)
            volcano_longitude_spin_box.setSuffix(u'°')  # degree symbol

            # Volcano latitude
            volcano_latitude_checkbox = QCheckBox()
            volcano_latitude_spin_box = QDoubleSpinBox()
            volcano_latitude_spin_box.setMinimum(-90)
            volcano_latitude_spin_box.setMaximum(90)
            volcano_latitude_spin_box.setSuffix(u'°')  # degree symbol

            # Volcano height
            volcano_height_checkbox = QCheckBox()
            volcano_height_spin_box = QDoubleSpinBox()
            volcano_height_spin_box.setMinimum(0)
            volcano_height_spin_box.setMaximum(9999999)
            volcano_height_spin_box.setSuffix(tr(' metres'))

            # Volcano region
            volcano_region_checkbox = QCheckBox()
            volcano_region_line_edit = QLineEdit()

            # Alert level
            alert_level_checkbox = QCheckBox()
            alert_level_combo_box = QComboBox()
            volcano_alert_level_options = extra_keyword_volcano_alert_level[
                'options']
            for volcano_alert_level in volcano_alert_level_options:
                alert_level_combo_box.addItem(
                    volcano_alert_level['name'],
                    volcano_alert_level['key'],
                )
            default_option_index = alert_level_combo_box.findData(
                extra_keyword_volcano_alert_level['key'])
            alert_level_combo_box.setCurrentIndex(default_option_index)

            # Eruption height in metres
            eruption_height_checkbox = QCheckBox()
            eruption_height_spin_box = QDoubleSpinBox()
            eruption_height_spin_box.setMinimum(0)
            eruption_height_spin_box.setMaximum(9999999)
            eruption_height_spin_box.setSuffix(tr(' metres'))

            # Event time
            event_time_checkbox = QCheckBox()
            event_time_picker = QDateTimeEdit()
            event_time_picker.setCalendarPopup(True)
            event_time_picker.setDisplayFormat('hh:mm:ss, d MMM yyyy')
            event_time_picker.setDateTime(datetime.now())

            # Timezone
            timezone_checkbox = QCheckBox()
            timezone_combo_box = QComboBox()
            for timezone in extra_keyword_time_zone['options']:
                timezone_combo_box.addItem(
                    timezone['key'], timezone['name']
                )
            index = timezone_combo_box.findData(
                extra_keyword_time_zone['default_option'])
            timezone_combo_box.setCurrentIndex(index)

            self.widgets_dict[extra_keyword_volcano_name['key']] = [
                volcano_name_checkbox,
                volcano_name_line_edit,
                extra_keyword_volcano_name
            ]
            self.widgets_dict[extra_keyword_region['key']] = [
                volcano_region_checkbox,
                volcano_region_line_edit,
                extra_keyword_region
            ]
            self.widgets_dict[extra_keyword_volcano_longitude['key']] = [
                volcano_longitude_checkbox,
                volcano_longitude_spin_box,
                extra_keyword_volcano_longitude
            ]
            self.widgets_dict[extra_keyword_volcano_latitude['key']] = [
                volcano_latitude_checkbox,
                volcano_latitude_spin_box,
                extra_keyword_volcano_latitude
            ]
            self.widgets_dict[extra_keyword_volcano_height['key']] = [
                volcano_height_checkbox,
                volcano_height_spin_box,
                extra_keyword_volcano_height
            ]
            self.widgets_dict[extra_keyword_volcano_alert_level['key']] = [
                alert_level_checkbox,
                alert_level_combo_box,
                extra_keyword_volcano_alert_level
            ]
            self.widgets_dict[extra_keyword_eruption_height['key']] = [
                eruption_height_checkbox,
                eruption_height_spin_box,
                extra_keyword_eruption_height
            ]
            self.widgets_dict[
                extra_keyword_volcano_eruption_event_time['key']] = [
                event_time_checkbox,
                event_time_picker,
                extra_keyword_volcano_eruption_event_time
            ]
            self.widgets_dict[extra_keyword_time_zone['key']] = [
                timezone_checkbox,
                timezone_combo_box,
                extra_keyword_time_zone
            ]

            index = 0
            for key, widgets in self.widgets_dict.items():
                self.extra_keywords_layout.addWidget(widgets[0], index, 0)
                self.extra_keywords_layout.addWidget(widgets[1], index, 1)
                widgets[0].setText(widgets[2]['name'])
                widgets[0].stateChanged.connect(widgets[1].setEnabled)
                widgets[0].setChecked(True)
                widgets[0].setToolTip(widgets[2]['description'])
                widgets[1].setToolTip(widgets[2]['description'])
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
                    current_index = widgets[1].currentIndex()
                    extra_keywords[key] = widgets[1].itemData(current_index)
                elif isinstance(widgets[1], QDoubleSpinBox):
                    extra_keywords[key] = widgets[1].value()
                elif isinstance(widgets[1], QDateTimeEdit):
                    extra_keywords[key] = widgets[1].dateTime().toString(
                        Qt.ISODate)

        # Set volcano ash event ID
        required_keywords = (
            extra_keyword_volcano_eruption_event_time['key'],
            extra_keyword_time_zone['key'],
            extra_keyword_volcano_name['key']
        )
        LOGGER.debug(required_keywords)
        LOGGER.debug(extra_keywords.keys())
        LOGGER.debug(set(extra_keywords.keys()).issubset(required_keywords))
        if set(required_keywords).issubset(extra_keywords.keys()):
            event_time = extra_keywords[
                extra_keyword_volcano_eruption_event_time['key']]
            time_zone = extra_keywords[extra_keyword_time_zone['key']]
            volcano_name = extra_keywords[extra_keyword_volcano_name['key']]

            real_event_time = datetime.strptime(
                event_time, '%Y-%m-%dT%H:%M:%S')
            event_time_str = real_event_time.strftime('%Y%m%d%H%M%S')

            zone_offset = datetime.now(pytz.timezone(time_zone)).strftime('%z')

            event_id = event_time_str + zone_offset + '_' + volcano_name

            extra_keywords[extra_keyword_volcano_event_id['key']] = event_id

        return extra_keywords

    def set_existing_extra_keywords(self):
        """Set extra keywords from the value from metadata."""
        extra_keywords = self.parent.get_existing_keyword('extra_keywords')
        for key, widgets in self.widgets_dict.items():
            value = extra_keywords.get(key)
            if value is None:
                widgets[0].setChecked(False)
            else:
                widgets[0].setChecked(True)
                if isinstance(widgets[1], QLineEdit):
                    widgets[1].setText(value)
                elif isinstance(widgets[1], QComboBox):
                    value_index = widgets[1].findData(value)
                    widgets[1].setCurrentIndex(value_index)
                elif isinstance(widgets[1], QDoubleSpinBox):
                    try:
                        value = float(value)
                        widgets[1].setValue(value)
                    except ValueError:
                        LOGGER.warning('Failed to convert %s to float' % value)
                elif isinstance(widgets[1], QDateTimeEdit):
                    try:
                        value_datetime = datetime.strptime(
                            value, "%Y-%m-%dT%H:%M:%S.%f")
                        widgets[1].setDateTime(value_datetime)
                    except ValueError:
                        try:
                            value_datetime = datetime.strptime(
                                value, "%Y-%m-%dT%H:%M:%S")
                            widgets[1].setDateTime(value_datetime)
                        except ValueError:
                            LOGGER.info(
                                'Failed to convert %s to datetime' % value)
