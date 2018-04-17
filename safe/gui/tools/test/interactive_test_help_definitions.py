# coding=utf-8

"""Interactive test for definitions help."""


from safe.test.utilities import get_qgis_app
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app(qsetting='InaSAFETest')
from safe.gui.tools.help_dialog import HelpDialog  # NOQA
from safe.gui.tools.help import definitions_help  # NOQA

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

dialog = HelpDialog(None, definitions_help.definitions_help())
