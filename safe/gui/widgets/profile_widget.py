# coding=utf-8
"""InaSAFE Profile Widget."""

from collections import OrderedDict
from functools import partial

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (
    QTreeWidget,
    QTreeWidgetItem,
    QCheckBox,
    QFont,
    QHeaderView,
    QPalette,
    QPushButton,
)

from safe.common.parameters.percentage_parameter_widget import (
    PercentageSpinBox)
from safe.definitions.utilities import get_name, get_class_name, definition
from safe.definitions.exposure import exposure_population
from safe.utilities.i18n import tr
from safe.definitions.utilities import generate_default_profile
from safe.common.custom_logging import LOGGER

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

black_text_palette = QPalette()
black_text_palette.setColor(QPalette.Text, Qt.black)

red_text_palette = QPalette()
red_text_palette.setColor(QPalette.Text, Qt.red)

green_text_palette = QPalette()
green_text_palette.setColor(QPalette.Text, Qt.green)


class ProfileWidget(QTreeWidget, object):

    """Profile Widget."""

    def __init__(self, data=None):
        """Constructor."""
        super(ProfileWidget, self).__init__()

        # Attributes
        self.widget_items = []
        # Set data
        if data:
            self.data = data
        # Set header
        self.header_tree_widget = QTreeWidgetItem([
            tr('Classification'),
            tr('Affected'),
            tr('Displacement Rate'),
            tr('Restore Default'),
        ])
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(14)
        self.header_tree_widget.setFont(0, header_font)
        self.header_tree_widget.setFont(1, header_font)
        self.header_tree_widget.setFont(2, header_font)
        self.header_tree_widget.setFont(3, header_font)
        self.setHeaderItem(self.header_tree_widget)
        self.header().setResizeMode(0, QHeaderView.Stretch)
        self.header().setResizeMode(1, QHeaderView.Fixed)
        self.header().setResizeMode(2, QHeaderView.ResizeToContents)
        self.header().setResizeMode(3, QHeaderView.ResizeToContents)
        self.header().setMovable(False)

    @property
    def data(self):
        """Get the data from the current state of widgets.

        :returns: Profile data in dictionary.
        :rtype: dict
        """
        if len(self.widget_items) == 0:
            return
        data = {}
        for hazard_item in self.widget_items:
            hazard = hazard_item.data(0, Qt.UserRole)
            data[hazard] = {}
            classification_items = [
                hazard_item.child(i) for i in range(hazard_item.childCount())
            ]
            for classification_item in classification_items:
                classification = classification_item.data(0, Qt.UserRole)
                data[hazard][classification] = OrderedDict()
                class_items = [
                    classification_item.child(i) for i in range(
                        classification_item.childCount()
                    )
                ]
                for the_class_item in class_items:
                    the_class = the_class_item.data(0, Qt.UserRole)
                    affected_check_box = self.itemWidget(the_class_item, 1)
                    displacement_rate_spin_box = self.itemWidget(
                        the_class_item, 2)
                    data[hazard][classification][the_class] = {
                        'affected': affected_check_box.isChecked(),
                        'displacement_rate': displacement_rate_spin_box.value()
                    }
        return data

    @data.setter
    def data(self, profile_data):
        """Set data for the widget.

        :param profile_data: profile data.
        :type profile_data: dict

        It will replace the previous data.
        """
        default_profile = generate_default_profile()
        self.clear()
        for hazard in sorted(default_profile.keys()):
            classifications = default_profile[hazard]
            hazard_widget_item = QTreeWidgetItem()
            hazard_widget_item.setData(0, Qt.UserRole, hazard)
            hazard_widget_item.setText(0, get_name(hazard))
            for classification in sorted(classifications.keys()):
                # Filter out classification that doesn't support population.
                # TODO(IS): This is not the best place to put the filtering.
                # It's more suitable in the generate_default_profile method
                # in safe/definitions/utilities.
                classification_definition = definition(classification)
                supported_exposures = classification_definition.get(
                    'exposures', [])
                # Empty list means support all exposure
                if supported_exposures != []:
                    if exposure_population not in supported_exposures:
                        continue
                classes = classifications[classification]
                classification_widget_item = QTreeWidgetItem()
                classification_widget_item.setData(
                    0, Qt.UserRole, classification)
                classification_widget_item.setText(0, get_name(classification))
                hazard_widget_item.addChild(classification_widget_item)
                for the_class, the_value in classes.items():
                    the_class_widget_item = QTreeWidgetItem()
                    the_class_widget_item.setData(0, Qt.UserRole, the_class)
                    the_class_widget_item.setText(
                        0, get_class_name(the_class, classification))
                    classification_widget_item.addChild(the_class_widget_item)
                    # Set from profile_data if exist, else get default
                    profile_value = profile_data.get(
                        hazard, {}).get(classification, {}).get(
                        the_class, the_value)
                    # Adding widget must be happened after addChild
                    # Affected checkbox
                    affected_check_box = QCheckBox(self)
                    affected_check_box.setChecked(profile_value['affected'])
                    # Set default value
                    affected_check_box.default_value = the_value['affected']
                    self.setItemWidget(
                        the_class_widget_item, 1, affected_check_box)

                    # Displacement rate spinbox
                    displacement_rate_spinbox = PercentageSpinBox(self)
                    displacement_rate_spinbox.setValue(
                        profile_value['displacement_rate'])
                    displacement_rate_spinbox.setEnabled(
                        profile_value['affected'])
                    # Set default value
                    displacement_rate_spinbox.default_value = the_value[
                        'displacement_rate']
                    displacement_rate_spinbox.user_value = profile_value[
                        'displacement_rate']
                    self.setItemWidget(
                        the_class_widget_item, 2, displacement_rate_spinbox)

                    # Restore Button
                    restore_button = QPushButton(tr('Restore'))
                    self.setItemWidget(
                        the_class_widget_item, 3, restore_button)
                    restore_button.setEnabled(profile_value['affected'])

                    update_spin_box_button_state(
                        displacement_rate_spinbox, restore_button)

                    # Behaviour when the check box is checked
                    # noinspection PyUnresolvedReferences
                    affected_check_box.stateChanged.connect(
                        displacement_rate_spinbox.setEnabled)
                    # noinspection PyUnresolvedReferences
                    affected_check_box.stateChanged.connect(
                        restore_button.setEnabled)

                    # For debugging purpose, delete later
                    def is_affected_default(check_box):
                        if check_box.isChecked() == check_box.default_value:
                            print ('affected is default')
                        else:
                            print ('affected is NOT default')

                    def is_displacement_rate_default(spin_box):
                        if spin_box.value() == spin_box.default_value:
                            print ('spin box is default')
                        else:
                            print ('spin box is NOT default')

                    # noinspection PyUnresolvedReferences
                    affected_check_box.stateChanged.connect(partial(
                        is_affected_default, check_box=affected_check_box))
                    # noinspection PyUnresolvedReferences
                    displacement_rate_spinbox.valueChanged.connect(partial(
                        is_displacement_rate_default,
                        spin_box=displacement_rate_spinbox))
                    # noinspection PyUnresolvedReferences
                    displacement_rate_spinbox.valueChanged.connect(partial(
                        update_spin_box_button_state,
                        spin_box=displacement_rate_spinbox,
                        button=restore_button
                    ))
                    # noinspection PyUnresolvedReferences
                    restore_button.clicked.connect(partial(
                        set_to_default_value,
                        spin_box=displacement_rate_spinbox))

            if hazard_widget_item.childCount() > 0:
                self.widget_items.append(hazard_widget_item)

        self.addTopLevelItems(self.widget_items)

        self.expandAll()

    def clear(self):
        """Clear method to clear the widget items and the tree widget."""
        super(ProfileWidget, self).clear()
        self.widget_items = []


def update_spin_box_button_state(spin_box, button):
    """Update spin box and restore button state based on current value.

    :param spin_box: The spin box which has default_value and user_value
        attribute.
    :type spin_box: PercentageSpinBox

    :param button: The restore button.
    :type button: QPushButton
    """
    LOGGER.debug('%s %s %s' % (
        spin_box.value(), spin_box.default_value, spin_box.user_value))
    if spin_box.value() == spin_box.default_value:
        LOGGER.debug('Black, default value == value')
        spin_box.setPalette(black_text_palette)
        button.setEnabled(False)
    elif spin_box.value() == spin_box.user_value:
        LOGGER.debug('Green, user value == value')
        spin_box.setPalette(green_text_palette)
        button.setEnabled(True)
    else:
        LOGGER.debug('Red, Edited')
        spin_box.setPalette(red_text_palette)
        button.setEnabled(True)
    LOGGER.debug('Result')
    LOGGER.debug('%s' % spin_box.palette().color(QPalette.Text).name())


def set_to_default_value(spin_box):
    """Set spin box value to default value.

    :param spin_box: The spin box which has default_value and user_value
        attribute.
    :type spin_box: PercentageSpinBox
    """
    if spin_box.isEnabled():
        spin_box.setValue(spin_box.default_value)
