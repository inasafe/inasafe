# coding=utf-8
"""InaSAFE Profile Widget."""

from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem, QCheckBox, QDoubleSpinBox
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class ProfileWidget(QTreeWidget, object):

    """Profile Widget"""

    def __init__(self, parent, data):
        """Constructor"""
        super(ProfileWidget, self).__init__(parent)

        # Attributes
        self.data = data
        self.header = QTreeWidgetItem(
            [tr('Classification'), tr('Affected'), tr('Displacement Rate')])
        self.setHeaderItem(self.header)
        widget_items = self.generate_tree_model()
        self.addTopLevelItems(widget_items)
        self.expandAll()

    def generate_tree_model(self):
        """Generate tree model for the data."""
        widget_items = []
        for hazard, classifications in self.data.items():
            hazard_widget_item = QTreeWidgetItem()
            hazard_widget_item.setText(0, hazard)
            for classification, classes in classifications.items():
                classification_widget_item = QTreeWidgetItem()
                classification_widget_item.setText(0, classification)
                hazard_widget_item.addChild(classification_widget_item)
                for the_class, the_value in classes.items():
                    the_class_widget_item = QTreeWidgetItem()
                    the_class_widget_item.setText(0, the_class)
                    classification_widget_item.addChild(the_class_widget_item)
                    # Adding widget must be happened after addChild
                    affected_check_box = QCheckBox(self)
                    affected_check_box.setChecked(the_value['affected'])
                    self.setItemWidget(
                        the_class_widget_item, 1, affected_check_box)
                    displacement_rate_spinbox = QDoubleSpinBox(self)
                    displacement_rate_spinbox.setMinimum(0.0)
                    displacement_rate_spinbox.setMinimum(1.0)
                    displacement_rate_spinbox.setValue(
                        the_value['displacement_rate'])
                    self.setItemWidget(
                        the_class_widget_item, 2, displacement_rate_spinbox)
                    # Behaviour when the check box is checked
                    # noinspection PyUnresolvedReferences
                    affected_check_box.stateChanged.connect(
                        displacement_rate_spinbox.setEnabled)

            widget_items.append(hazard_widget_item)

        return widget_items

#
# class CustomTreeWidgetItem(QTreeWidgetItem):
#
#     """Custom Tree Widget Item with Checkbox and Double Spinbox."""
#
#     def __init__(self, parent):
