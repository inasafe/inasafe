#!/usr/bin/python

"""A helper to open the help documentation as a standalone dialog.

Tim Sutton, 2016
"""
from safe.test.qgis_app import qgis_app
from safe.gui.tools.help_dialog import HelpDialog
from safe.gui.tools.help import definitions_help

APP, IFACE = qgis_app()

dialog = HelpDialog(
    IFACE.mainWindow(),
    definitions_help.definitions_help())
dialog.show()  # non modal
APP.exec_()
