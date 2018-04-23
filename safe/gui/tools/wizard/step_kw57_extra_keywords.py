# coding=utf-8
"""InaSAFE Wizard Step Extra Keywords."""
from builtins import range

from collections import OrderedDict
from datetime import datetime

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QLineEdit, QDateTimeEdit, QDoubleSpinBox, QComboBox, QCheckBox, QSpinBox

from safe import messaging as m
from safe.common.custom_logging import LOGGER
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
        self.clear()
        self.description_label.setText(
            'In this step you can set some extra keywords for the layer. This '
            'keywords can be used for creating richer reporting or map.')
        subcategory = self.parent.step_kw_subcategory.selected_subcategory()
        extra_keywords = subcategory.get('extra_keywords')
        for extra_keyword in extra_keywords:
            check_box, input_widget = extra_keywords_to_widgets(extra_keyword)
            self.widgets_dict[extra_keyword['key']] = [
                check_box,
                input_widget,
                extra_keyword
            ]

        # Add to layout
        index = 0
        for key, widgets in list(self.widgets_dict.items()):
            self.extra_keywords_layout.addWidget(widgets[0], index, 0)
            self.extra_keywords_layout.addWidget(widgets[1], index, 1)
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
        for key, widgets in list(self.widgets_dict.items()):
            if widgets[0].isChecked():
                if isinstance(widgets[1], QLineEdit):
                    extra_keywords[key] = widgets[1].text()
                elif isinstance(widgets[1], QComboBox):
                    current_index = widgets[1].currentIndex()
                    extra_keywords[key] = widgets[1].itemData(current_index)
                elif isinstance(widgets[1], (QDoubleSpinBox, QSpinBox)):
                    extra_keywords[key] = widgets[1].value()
                elif isinstance(widgets[1], QDateTimeEdit):
                    extra_keywords[key] = widgets[1].dateTime().toString(
                        Qt.ISODate)

        return extra_keywords

    def set_existing_extra_keywords(self):
        """Set extra keywords from the value from metadata."""
        extra_keywords = self.parent.get_existing_keyword('extra_keywords')
        for key, widgets in list(self.widgets_dict.items()):
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

    def clear(self):
        """Clear current state."""
        # Adapted from http://stackoverflow.com/a/13103617/1198772
        for i in reversed(list(range(self.extra_keywords_layout.count()))):
            self.extra_keywords_layout.itemAt(i).widget().setParent(None)
        self.widgets_dict = OrderedDict()


def extra_keywords_to_widgets(extra_keyword_definition):
    """Create widgets for extra keyword.

    :param extra_keyword_definition: An extra keyword definition.
    :type extra_keyword_definition: dict

    :return: QCheckBox and The input widget
    :rtype: (QCheckBox, QWidget)
    """
    # Check box
    check_box = QCheckBox(extra_keyword_definition['name'])
    check_box.setToolTip(extra_keyword_definition['description'])
    check_box.setChecked(True)

    # Input widget
    if extra_keyword_definition['type'] == float:
        input_widget = QDoubleSpinBox()
        input_widget.setMinimum(extra_keyword_definition['minimum'])
        input_widget.setMaximum(extra_keyword_definition['maximum'])
        input_widget.setSuffix(extra_keyword_definition['unit_string'])
    elif extra_keyword_definition['type'] == int:
        input_widget = QSpinBox()
        input_widget.setMinimum(extra_keyword_definition['minimum'])
        input_widget.setMaximum(extra_keyword_definition['maximum'])
        input_widget.setSuffix(extra_keyword_definition['unit_string'])
    elif extra_keyword_definition['type'] == str:
        if extra_keyword_definition.get('options'):
            input_widget = QComboBox()
            options = extra_keyword_definition['options']
            for option in options:
                input_widget.addItem(
                    option['name'],
                    option['key'],
                )
            default_option_index = input_widget.findData(
                extra_keyword_definition['default_option'])
            input_widget.setCurrentIndex(default_option_index)
        else:
            input_widget = QLineEdit()
    elif extra_keyword_definition['type'] == datetime:
        input_widget = QDateTimeEdit()
        input_widget.setCalendarPopup(True)
        input_widget.setDisplayFormat('hh:mm:ss, d MMM yyyy')
        input_widget.setDateTime(datetime.now())
    else:
        raise Exception
    input_widget.setToolTip(extra_keyword_definition['description'])

    # Signal
    # noinspection PyUnresolvedReferences
    check_box.stateChanged.connect(input_widget.setEnabled)

    return check_box, input_widget
