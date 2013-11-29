"""Package safe_qgis."""

import os
import sys

# Import the PyQt and QGIS libraries
# this import required to enable PyQt API v2
import qgis  # pylint: disable=W0611

# Add parent directory to path to make test aware of other modules
myDir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if myDir not in sys.path:
    sys.path.append(myDir)

# MONKEYPATCHING safe.defaults.get_defaults to use breakdown_defaults
# see safe_qgis.utilities.defaults for more details
import safe.defaults
from safe_qgis.utilities.defaults import breakdown_defaults
safe.defaults.get_defaults = lambda the_default = None: breakdown_defaults(
    the_default)

try:
    # When upgrading, using the plugin manager, you may get an error when
    # doing the following import, so we wrap it in a try except
    # block and then display a friendly message to restart QGIS
    from safe_qgis.utilities.custom_logging import setup_logger
    setup_logger()
except ImportError:
    # Note we use translate directly but the string may still not translate
    # at this early stage since the i18n setup routines have not been called
    # yet.
    import traceback

    trace = ''.join(traceback.format_tb(sys.exc_info()[2]))
    # Note that we do a late import here to avoid QPaintDevice before
    # QApplication errors when running tests of safe package. TS
    from PyQt4.QtCore import QCoreApplication
    from PyQt4.QtGui import QMessageBox
    myWarning = QCoreApplication.translate(
        'Plugin', 'Please restart QGIS to use this plugin. If you experience '
                  'further problems after restarting please report the issue '
                  'to the InaSAFE team.')
    QMessageBox.warning(
        None, 'InaSAFE', myWarning)
        #None, 'InaSAFE', myWarning + ' ' + e.message + ' ' + trace)
    raise
