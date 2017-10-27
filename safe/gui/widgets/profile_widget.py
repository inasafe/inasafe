# coding=utf-8
"""InaSAFE Profile Widget."""

from PyQt4.QtGui import (
    QTreeWidget, QTreeWidgetItem, QCheckBox, QDoubleSpinBox, QFont)
from PyQt4.QtCore import Qt
from safe.definitions.utilities import get_name, get_class_name
from safe.utilities.i18n import tr
from collections import OrderedDict

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class ProfileWidget(QTreeWidget, object):

    """Profile Widget."""

    def __init__(self, parent, data):
        """Constructor."""
        super(ProfileWidget, self).__init__(parent)

        # Attributes
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

        self.widget_items = self.generate_tree_model()
        self.addTopLevelItems(self.widget_items)
        self.expandAll()
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.resizeColumnToContents(2)

    def generate_tree_model(self):
        """Generate tree model for the data."""
        widget_items = []
        for hazard, classifications in self.data.items():
            hazard_widget_item = QTreeWidgetItem()
            hazard_widget_item.setData(0, Qt.UserRole, hazard)
            hazard_widget_item.setText(0, get_name(hazard))
            for classification, classes in classifications.items():
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

            widget_items.append(hazard_widget_item)

        return widget_items

    def get_data(self):
        """Get the data from the current state of widgets.

        :returns: Profile data in dictionary.
        :rtype: dict
        """
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


class PercentageSpinBox(QDoubleSpinBox):

    """Custom Spinbox for percentage 0 % - 100 %."""

    def __init__(self, parent):
        """Constructor."""
        super(PercentageSpinBox, self).__init__(parent)
        self.setRange(0.0, 1.0)
        self.setSingleStep(0.01)
        # noinspection PyUnresolvedReferences

    def textFromValue(self, value):
        """Modify text representation to get percentage representation.

        :param value: The real value.
        :type value: float

        :returns: The percentage representation.
        :rtype: str
        """
        return '%d %%' % (value * 100)
