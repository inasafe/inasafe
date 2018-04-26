# coding=utf-8
"""Help Dialog."""

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # NOQA pylint: disable=unused-import
from qgis.PyQt import QtGui, QtWidgets
from qgis.PyQt.QtCore import Qt

from safe.gui.tools.help.dock_help import dock_help
from safe.utilities.resources import (
    get_ui_class, html_footer, html_help_header, resources_path)

FORM_CLASS = get_ui_class('help_dialog_base.ui')

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class HelpDialog(QtWidgets.QDialog, FORM_CLASS):
    """About dialog for the InaSAFE plugin."""

    def __init__(self, parent=None, message=None):
        """Constructor for the dialog.

        :param message: An optional message object to display in the dialog.
        :type message: Message.Message

        :param parent: Parent widget of this dialog
        :type parent: QWidget
        """

        QtWidgets.QDialog.__init__(
            self, parent,
            flags=Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setupUi(self)
        self.parent = parent
        icon = resources_path('img', 'icons', 'show-inasafe-help.svg')
        self.setWindowIcon(QtGui.QIcon(icon))

        header = html_help_header()
        footer = html_footer()

        string = header

        if message is None:
            message = dock_help()

        string += message.to_html()
        string += footer

        self.help_web_view.setHtml(string)
