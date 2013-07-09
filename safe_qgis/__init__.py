"""Package safe_qgis."""
import os
import sys
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import QMessageBox

# Add parent directory to path to make test aware of other modules
myDir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if myDir not in sys.path:
    sys.path.append(myDir)

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
    myTraceback = ''.join(traceback.format_tb(sys.exc_info()[2]))
    myWarning = QCoreApplication.translate(
        'Plugin', 'Please restart QGIS to use this plugin. If you experience '
                  'further problems after restarting please report the issue '
                  'to the InaSAFE team.')
    QMessageBox.warning(
        None, 'InaSAFE', myWarning)
        #None, 'InaSAFE', myWarning + ' ' + e.message + ' ' + myTraceback)
    raise
