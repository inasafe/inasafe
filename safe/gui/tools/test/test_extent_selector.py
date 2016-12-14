# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Import Dialog Test Cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@kartoza.com'
__date__ = '13/11/2014'
__copyright__ = ('Copyright 2013, Australia Indonesia Facility for '
                 'Disaster Reduction')

# noinspection PyUnresolvedReferences
import unittest
import logging

from qgis.core import QgsRectangle, QgsCoordinateReferenceSystem
from qgis.PyQt import QtGui
from qgis.PyQt.QtTest import QTest
from qgis.PyQt.QtCore import Qt, QPoint

from safe.test.utilities import get_qgis_app

# In our tests, we need to have this line below before importing any other
# safe_qgis.__init__ to load all the configurations that we make for testing
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.gui.tools.extent_selector_dialog import ExtentSelectorDialog

LOGGER = logging.getLogger('InaSAFE')


class ExtentSelectorTest(unittest.TestCase):
    """Test Import Dialog widget
    """
    # noinspection PyPep8Naming
    def setUp(self):
        """Runs before each test."""
        self.extent = QgsRectangle(10.0, 10.0, 20.0, 20.0)
        self.crs = QgsCoordinateReferenceSystem('EPSG:4326')
        CANVAS.setExtent(self.extent)
        self.dialog = ExtentSelectorDialog(
            IFACE,
            PARENT,
            self.extent,
            self.crs)
        self.signal_received = False

        self.dialog.extent_defined.connect(self.extent_defined)

        self.widget = QtGui.QWidget()
        self.widget.setGeometry(0, 0, 500, 500)
        layout = QtGui.QVBoxLayout(self.widget)
        layout.addWidget(CANVAS)
        self.widget.show()
        QTest.qWaitForWindowShown(self.widget)

        self.dialog.show()
        QTest.qWaitForWindowShown(self.dialog)

    def tearDown(self):
        """Runs after each test."""
        self.dialog.reject()
        self.dialog = None
        self.extent = None
        self.crs = None

    def extent_defined(self, extent, crs):
        """Slot for when extents are changed in dialog.

        :param extent: Rectangle that was created.
        :type extent: QgsRectangle

        :param crs: Coordiate reference system.
        :type crs: QgsCoordinateReferenceSystem
        """
        self.extent = extent
        self.crs = crs
        self.signal_received = True

    def canvas_mouse_moved(self, point):
        """Slot for when the mouse moves on the canvas."""
        # print point.toString()

    def test_spinboxes(self):
        """Test validate extent method."""
        self.dialog.x_maximum.clear()
        self.dialog.extent_defined.connect(self.extent_defined)
        QTest.mouseClick(self.dialog.x_maximum, Qt.LeftButton)
        QTest.keyClick(self.dialog.x_maximum, '3')
        QTest.keyClick(self.dialog.x_maximum, '0')
        ok = self.dialog.button_box.button(QtGui.QDialogButtonBox.Ok)
        QTest.mouseClick(ok, Qt.LeftButton)

        expected_extent = QgsRectangle(10.0, 10.0, 30.0, 20.0)
        self.assertEqual(self.extent.toString(), expected_extent.toString())

    @unittest.expectedFailure
    @unittest.skip
    def test_mouse_drag(self):
        """Test setting extents by dragging works.

        This currently fails as QTest does not properly do the mouse
        interactions with the canvas.

        """
        # Imported here because it is not available in OSX QGIS bundle
        # pylint: disable=redefined-outer-name
        from qgis.PyQt.QtTest import QTest

        # Click the capture button
        QTest.mouseClick(self.dialog.capture_button, Qt.LeftButton)

        # drag a rect on the canvas
        QTest.mousePress(CANVAS, Qt.LeftButton, pos=QPoint(0, 0), delay=500)
        QTest.mouseRelease(
            CANVAS, Qt.LeftButton,
            pos=QPoint(300, 300),
            delay=-1)

        # on drag the extents selector windows should appear again
        QTest.qWaitForWindowShown(self.dialog)
        # Click ok to dispose of the window again
        ok = self.dialog.button_box.button(QtGui.QDialogButtonBox.Ok)
        QTest.mouseClick(ok, Qt.LeftButton)

        # Check the extent emitted on closing teh dialog is correct
        expected_extent = QgsRectangle(10.0, 10.0, 30.0, 20.0)
        self.assertEqual(self.extent.toString(), expected_extent.toString())

if __name__ == '__main__':
    suite = unittest.makeSuite(ExtentSelectorTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
