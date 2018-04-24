# coding=utf-8
"""Qt related helpers."""
# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # NOQA pylint: disable=unused-import
from qgis.PyQt import Qt, QtGui, QtCore

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def qt_at_least(needed_version, test_version=None):
    """Check if the installed Qt version is greater than the requested

    :param needed_version: minimally needed Qt version in format like 4.8.4
    :type needed_version: str

    :param test_version: Qt version as returned from Qt.QT_VERSION. As in
     0x040100 This is used only for tests
    :type test_version: int

    :returns: True if the installed Qt version is greater than the requested
    :rtype: bool
    """
    major, minor, patch = needed_version.split('.')
    needed_version = '0x0%s0%s0%s' % (major, minor, patch)
    needed_version = int(needed_version, 0)

    installed_version = Qt.QT_VERSION
    if test_version is not None:
        installed_version = test_version

    if needed_version <= installed_version:
        return True
    else:
        return False


def enable_busy_cursor():
    """Set the hourglass enabled and stop listening for layer changes."""
    QtGui.qApp.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))


def disable_busy_cursor():
    """Disable the hourglass cursor and listen for layer changes."""
    while QtGui.qApp.overrideCursor() is not None and \
            QtGui.qApp.overrideCursor().shape() == QtCore.Qt.WaitCursor:
        QtGui.qApp.restoreOverrideCursor()
