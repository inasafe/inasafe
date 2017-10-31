# coding=utf-8
"""Test Profile Widget."""

import unittest
from safe.test.utilities import get_qgis_app
from PyQt4.QtCore import Qt

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.definitions.utilities import generate_default_profile
from safe.gui.widgets.profile_widget import ProfileWidget


class TestProfileWidget(unittest.TestCase):
    """Test Profile Widget."""

    maxDiff = None

    def test_setup_profile_widget(self):
        """Test setup profile widget."""
        data = generate_default_profile()
        profile_widget = ProfileWidget(parent=PARENT, data=data)

        self.assertDictEqual(data, profile_widget.data)

        hazard_item = profile_widget.widget_items[0]
        hazard_key = hazard_item.data(0, Qt.UserRole)
        classification_item = hazard_item.child(0)
        classification_key = classification_item.data(0, Qt.UserRole)
        class_item = classification_item.child(0)
        class_key = class_item.data(0, Qt.UserRole)

        affected_check_box = profile_widget.itemWidget(class_item, 1)
        displacement_spin_box = profile_widget.itemWidget(class_item, 2)
        # Test changing value
        displacement_spin_box.setValue(0.5)
        self.assertEqual(
            profile_widget.data[hazard_key][classification_key][
                class_key]['displacement_rate'],
            0.5
        )
        # Test behaviour
        affected_check_box.setChecked(False)
        self.assertFalse(displacement_spin_box.isEnabled())


if __name__ == '__main__':
    unittest.main()
