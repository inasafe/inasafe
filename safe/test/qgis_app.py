# coding=utf-8
"""Fake QGIS App provided by QGIS Core."""

import mock

from qgis.testing import start_app
from qgis.gui import QgisInterface, QgsMapCanvas
from qgis.PyQt.QtWidgets import QMainWindow
from qgis.PyQt.QtCore import QSize


def qgis_app():
    """Start a QGIS application and get the iface.

    Mostly inspired by
    https://github.com/qgis/QGIS/blob/release-2_18/python/testing/mocked.py

    The application is returned as first argument. The QgisInterface is
    returned as second argument.

    The parent can be accessed by iface.mainWindow()
    The canvas can be access by iface.mapCanvas()

    You can further control its behavior
    by using the mock infrastructure.
    Refer to https://docs.python.org/3/library/unittest.mock.html
    for more details.

    :return: The QGIS interface.
    :rtype: QgisInterface
    """
    from qgis.utils import iface
    if iface:
        # We are already in QGIS.
        # I don't know if I can get the current QApplication.
        # But I guess we shouldn't use it too much.
        return None, iface

    # We are not in QGIS, we need to start an app.
    application = start_app()

    my_iface = mock.Mock(spec=QgisInterface)
    my_iface.mainWindow.return_value = QMainWindow()

    canvas = QgsMapCanvas(my_iface.mainWindow())
    canvas.resize(QSize(400, 400))

    my_iface.mapCanvas.return_value = canvas

    return application, my_iface
