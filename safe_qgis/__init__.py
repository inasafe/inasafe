import os
import sys
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import QCoreApplication
from PyQt4.QtGui import QMessageBox

# Add parent directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

try:
    # When upgrading, using the plugin manager, you may get an error when
    # doing the following import, so we wrap it in a try except
    # block and then display a friendly message to restart QGIS
    from .custom_logging import setupLogger
    setupLogger()
except ImportError:
    # Note we use translate directly but the string may still not translate
    # at this early stage since the i18n setup routines have not been called
    # yet.
    myWarning = QCoreApplication.translate(
        'Plugin', 'Please restart QGIS to use this plugin.')
    QMessageBox.warning(
        None, 'InaSAFE', myWarning)
    raise

