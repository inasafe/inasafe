
from PyQt4.QtCore import QCoreApplication


__author__ = 'timlinux'


def tr(text):
    """Convenience QObject.tr wrapper for use by non QObject derived classes.

    .. note:: see http://tinyurl.com/pyqt-differences

    :param text: String to be translated
    :type text: str

    :returns: Translated version of the given string if available, otherwise
        the original string.
    :rtype: str
    """
    # Ensure that the text is a string
    text = str(text)
    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    return QCoreApplication.translate('@default', text)
