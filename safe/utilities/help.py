# coding=utf-8
"""Help HTML utilities."""

from tempfile import mktemp

from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices
from safe.gui.tools.help.dock_help import dock_help
from safe.utilities.resources import (
    html_footer,
    html_help_header,
)


def get_help_html(message=None):
    """Create the HTML content for the help dialog  or for external browser

    :param message: An optional message object to display in the dialog.
    :type message: Message.Message
    :return: the help HTML content
    :rtype: str
    """

    html = html_help_header()

    if message is None:
        message = dock_help()

    html += message.to_html()
    html += html_footer()
    return html


def show_help(message=None):
    """Open an help message in the user's browser

    :param message: An optional message object to display in the dialog.
    :type message: Message.Message
    """

    help_path = mktemp('.html')
    with open(help_path, 'w+') as f:
        f.write(get_help_html(message))
        QDesktopServices.openUrl(QUrl(help_path))
