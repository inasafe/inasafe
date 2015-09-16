# coding=utf-8
"""
QGIS utilities for InaSAFE
"""

__author__ = 'etienne'
__revision__ = '$Format:%H$'
__date__ = '17/02/2015'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

from qgis.gui import QgsMessageBar
from qgis.core import QGis
from qgis.utils import iface
from PyQt4.QtGui import QMessageBox, QPushButton

from safe.utilities.i18n import tr


def display_information_message_box(
        parent=None, title=None, message=None):
    """
    Display an information message box.

    :param title: The title of the message box.
    :type title: str

    :param message: The message inside the message box.
    :type message: str
    """
    QMessageBox.information(parent, title, message)


def display_information_message_bar(
        title=None,
        message=None,
        more_details=None,
        button_text=tr('Show details ...'),
        duration=8):
    """
    Display an information message bar.

    :param iface: The QGIS IFace instance. Note that we cannot
        use qgis.utils.iface since it is not available in our
        test environment.
    :type iface: QgisInterface

    :param title: The title of the message bar.
    :type title: str

    :param message: The message inside the message bar.
    :type message: str

    :param more_details: The message inside the 'Show details' button.
    :type more_details: str

    :param button_text: The text of the button if 'more_details' is not empty.
    :type button_text: str

    :param duration: The duration for the display, default is 8 seconds.
    :type duration: int
    """
    iface.messageBar().clearWidgets()
    widget = iface.messageBar().createMessage(title, message)

    if more_details:
        button = QPushButton(widget)
        button.setText(button_text)
        button.pressed.connect(
            lambda: display_information_message_box(
                title=title, message=more_details))
        widget.layout().addWidget(button)

    iface.messageBar().pushWidget(widget, QgsMessageBar.INFO, duration)


def display_success_message_bar(
        title=None,
        message=None,
        more_details=None,
        button_text=tr('Show details ...'),
        duration=8):
    """
    Display a success message bar.

    :param iface: The QGIS IFace instance. Note that we cannot
        use qgis.utils.iface since it is not available in our
        test environment.
    :type iface: QgisInterface

    :param title: The title of the message bar.
    :type title: str

    :param message: The message inside the message bar.
    :type message: str

    :param more_details: The message inside the 'Show details' button.
    :type more_details: str

    :param button_text: The text of the button if 'more_details' is not empty.
    :type button_text: str

    :param duration: The duration for the display, default is 8 seconds.
    :type duration: int
    """

    iface.messageBar().clearWidgets()
    widget = iface.messageBar().createMessage(title, message)

    if more_details:
        button = QPushButton(widget)
        button.setText(button_text)
        button.pressed.connect(
            lambda: display_information_message_box(
                title=title, message=more_details))
        widget.layout().addWidget(button)

    if QGis.QGIS_VERSION_INT >= 20700:
        iface.messageBar().pushWidget(widget, QgsMessageBar.SUCCESS, duration)
    else:
        iface.messageBar().pushWidget(widget, QgsMessageBar.INFO, duration)


def display_warning_message_box(parent=None, title=None, message=None):
    """
    Display a warning message box.

    :param title: The title of the message box.
    :type title: str

    :param message: The message inside the message box.
    :type message: str
    """
    QMessageBox.warning(parent, title, message)


def display_warning_message_bar(
        title=None,
        message=None,
        more_details=None,
        button_text=tr('Show details ...'),
        duration=8):
    """
    Display a warning message bar.

    :param title: The title of the message bar.
    :type title: str

    :param message: The message inside the message bar.
    :type message: str

    :param more_details: The message inside the 'Show details' button.
    :type more_details: str

    :param button_text: The text of the button if 'more_details' is not empty.
    :type button_text: str

    :param duration: The duration for the display, default is 8 seconds.
    :type duration: int
    """

    iface.messageBar().clearWidgets()
    widget = iface.messageBar().createMessage(title, message)

    if more_details:
        button = QPushButton(widget)
        button.setText(button_text)
        button.pressed.connect(
            lambda: display_warning_message_box(
                title=title, message=more_details))
        widget.layout().addWidget(button)

    iface.messageBar().pushWidget(widget, QgsMessageBar.WARNING, duration)


def display_critical_message_box(parent=None, title=None, message=None):
    """
    Display a critical message box.

    :param title: The title of the message box.
    :type title: str

    :param message: The message inside the message box.
    :type message: str
    """
    QMessageBox.critical(parent, title, message)


def display_critical_message_bar(
        title=None,
        message=None,
        more_details=None,
        button_text=tr('Show details ...'),
        duration=8):
    """
    Display a critical message bar.

    :param title: The title of the message bar.
    :type title: str

    :param message: The message inside the message bar.
    :type message: str

    :param more_details: The message inside the 'Show details' button.
    :type more_details: str

    :param button_text: The text of the button if 'more_details' is not empty.
    :type button_text: str

    :param duration: The duration for the display, default is 8 seconds.
    :type duration: int
    """

    iface.messageBar().clearWidgets()
    widget = iface.messageBar().createMessage(title, message)

    if more_details:
        button = QPushButton(widget)
        button.setText(button_text)
        button.pressed.connect(
            lambda: display_critical_message_box(
                title=title, message=more_details))
        widget.layout().addWidget(button)

    iface.messageBar().pushWidget(widget, QgsMessageBar.CRITICAL, duration)
