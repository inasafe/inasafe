#!/usr/bin/python

"""A helper to open the help documentation as a standalone dialog.

Tim Sutton, 2016
"""
from safe.test.utilities import get_qgis_app, get_dock
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
# from PyQt4.QtGui import QApplication
from safe.gui.tools.help_dialog import HelpDialog
from safe.gui.tools.help import definitions_help
dialog = HelpDialog(
    None,
    definitions_help.definitions_help())
dialog.show()  # non modal
QGIS_APP.exec_()
