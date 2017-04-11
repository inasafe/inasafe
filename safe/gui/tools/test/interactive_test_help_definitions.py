# coding=utf-8

"""Interactive test for definitions help."""


from safe.test.utilities import get_qgis_app, get_dock
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
from PyQt4.QtGui import QApplication
from safe.gui.tools.help_dialog import HelpDialog
from safe.gui.tools.help import definitions_help

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

dialog = HelpDialog(None, definitions_help.definitions_help())
