# coding=utf-8
"""
QGIS utilities for InaSAFE
"""

__author__ = 'etienne'

from qgis.gui import QgsMessageBar
from qgis.utils import iface


def display_information_message_bar(title=None, message=None, duration=8):
    """
    Display a information message bar.

    :param title The title of the message bar.
    :type title str

    :param message The message inside the message bar.
    :type message str

    :param duration The duration for the display, default is 8 seconds.
    :type duration int
    """

    iface.messageBar().pushMessage(title, message, QgsMessageBar.INFO, duration)


def display_critical_message_bar(title=None, message=None, duration=8):
    """
    Display a critical message bar.

    :param title The title of the message bar.
    :type title str

    :param message The message inside the message bar.
    :type message str

    :param duration The duration for the display, default is 8 seconds.
    :type duration int
    """

    iface.messageBar().pushMessage(title, message, QgsMessageBar.CRITICAL, duration)


def display_warning_message_bar(title=None, message=None, duration=8):
    """
    Display a warning message bar.

    :param title The title of the message bar.
    :type title str

    :param message The message inside the message bar.
    :type message str

    :param duration The duration for the display, default is 8 seconds.
    :type duration int
    """

    iface.messageBar().pushMessage(title, message, QgsMessageBar.WARNING, duration)


def display_success_message_bar(title=None, message=None, duration=8):
    """
    Display a success message bar.

    :param title The title of the message bar.
    :type title str

    :param message The message inside the message bar.
    :type message str

    :param duration The duration for the display, default is 8 seconds.
    :type duration int
    """

    iface.messageBar().pushMessage(title, message, QgsMessageBar.SUCCESS, duration)