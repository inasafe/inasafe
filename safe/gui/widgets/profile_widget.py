# coding=utf-8
"""InaSAFE Profile Widget."""

from collections import OrderedDict

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (
    QTreeWidget, QTreeWidgetItem, QCheckBox, QDoubleSpinBox, QFont)

from safe.definitions.utilities import get_name, get_class_name
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class ProfileWidget(QTreeWidget, object):

    """Profile Widget."""

    def __init__(self, parent, data=None):
        """Constructor."""
        super(ProfileWidget, self).__init__(parent)

        # Attributes
        self.widget_items = []
        # Set data
        if data:
            self.data = data
        # Set header
        self.header = QTreeWidgetItem(
            [tr('Classification'), tr('Affected'), tr('Displacement Rate')])
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(14)
        self.header.setFont(0, header_font)
        self.header.setFont(1, header_font)
        self.header.setFont(2, header_font)
        self.setHeaderItem(self.header)

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
        self.clear()
        for hazard in sorted(profile_data.keys()):
            classifications = profile_data[hazard]
            hazard_widget_item = QTreeWidgetItem()
            hazard_widget_item.setData(0, Qt.UserRole, hazard)
            hazard_widget_item.setText(0, get_name(hazard))
            for classification in sorted(classifications.keys()):
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
                    # Adding widget must be happened after addChild
                    affected_check_box = QCheckBox(self)
                    affected_check_box.setChecked(the_value['affected'])
                    self.setItemWidget(
                        the_class_widget_item, 1, affected_check_box)
                    displacement_rate_spinbox = PercentageSpinBox(self)
                    displacement_rate_spinbox.setValue(
                        the_value['displacement_rate'])
                    displacement_rate_spinbox.setEnabled(the_value['affected'])
                    self.setItemWidget(
                        the_class_widget_item, 2, displacement_rate_spinbox)
                    # Behaviour when the check box is checked
                    # noinspection PyUnresolvedReferences
                    affected_check_box.stateChanged.connect(
                        displacement_rate_spinbox.setEnabled)

            self.widget_items.append(hazard_widget_item)

        self.addTopLevelItems(self.widget_items)

        self.expandAll()
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.resizeColumnToContents(2)

    def clear(self):
        """Clear method to clear the widget items and the tree widget."""
        super(ProfileWidget, self).clear()
        self.widget_items = []


class PercentageSpinBox(QDoubleSpinBox):

    """Custom Spinbox for percentage 0 % - 100 %."""

    def __init__(self, parent):
        """Constructor."""
        super(PercentageSpinBox, self).__init__(parent)
        self.setRange(0.0, 100.0)
        self.setSingleStep(0.1)
        self.setDecimals(1)
        self.setSuffix(' %')

    def setValue(self, p_float):
        """Override method to set a value to show it as 0 to 100.

        :param p_float: The float number that want to be set.
        :type p_float: float
        """
        p_float = p_float * 100

        super(PercentageSpinBox, self).setValue(p_float)

    def value(self):
        """Override method to get a value to to 0.0 to 1.0

        :returns: The float number that want to be set.
        :rtype: float
        """
        return super(PercentageSpinBox, self).value() / 100
