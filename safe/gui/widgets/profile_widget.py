# coding=utf-8
"""InaSAFE Profile Widget."""


from collections import OrderedDict

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem,
    QCheckBox,
    QHeaderView
)
from qgis.PyQt.QtGui import QFont

from safe.common.parameters.percentage_parameter_widget import (
    PercentageSpinBox)
from safe.definitions.exposure import exposure_population
from safe.definitions.utilities import generate_default_profile
from safe.definitions.utilities import get_name, get_class_name, definition
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


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
        self.header_tree_widget = QTreeWidgetItem(
            [tr('Classification'), tr('Affected'), tr('Displacement Rate')])
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(14)
        self.header_tree_widget.setFont(0, header_font)
        self.header_tree_widget.setFont(1, header_font)
        self.header_tree_widget.setFont(2, header_font)
        self.setHeaderItem(self.header_tree_widget)
        self.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.header().setSectionResizeMode(1, QHeaderView.Fixed)
        self.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.header().setSectionsMovable(False)

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
                for the_class, the_value in list(classes.items()):
                    the_class_widget_item = QTreeWidgetItem()
                    the_class_widget_item.setData(0, Qt.UserRole, the_class)
                    the_class_widget_item.setText(
                        0, get_class_name(the_class, classification))
                    classification_widget_item.addChild(the_class_widget_item)
                    # Adding widget must be happened after addChild
                    affected_check_box = QCheckBox(self)
                    # Set from profile_data if exist, else get default
                    profile_value = profile_data.get(
                        hazard, {}).get(classification, {}).get(
                        the_class, the_value)

                    affected_check_box.setChecked(profile_value['affected'])
                    self.setItemWidget(
                        the_class_widget_item, 1, affected_check_box)
                    displacement_rate_spinbox = PercentageSpinBox(self)
                    displacement_rate_spinbox.setValue(
                        profile_value['displacement_rate'])
                    displacement_rate_spinbox.setEnabled(
                        profile_value['affected'])
                    self.setItemWidget(
                        the_class_widget_item, 2, displacement_rate_spinbox)
                    # Behaviour when the check box is checked
                    # noinspection PyUnresolvedReferences
                    affected_check_box.stateChanged.connect(
                        displacement_rate_spinbox.setEnabled)
            if hazard_widget_item.childCount() > 0:
                self.widget_items.append(hazard_widget_item)

        self.addTopLevelItems(self.widget_items)

        self.expandAll()

    def clear(self):
        """Clear method to clear the widget items and the tree widget."""
        super(ProfileWidget, self).clear()
        self.widget_items = []
