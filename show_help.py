#!/usr/bin/python

"""A helper to open the help documentation as a standalone dialog.

Tim Sutton, 2016
"""
from safe.test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
# from PyQt4.QtGui import QApplication
from safe.gui.tools.help_dialog import HelpDialog  # NOQA
from safe.gui.tools.help import definitions_help  # NOQA
dialog = HelpDialog(
    None,
    definitions_help.definitions_help())
dialog.show()  # non modal
QGIS_APP.exec_()
