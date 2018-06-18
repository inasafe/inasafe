# coding=utf-8
"""Help Dialog."""

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # NOQA pylint: disable=unused-import
from qgis.PyQt import QtGui, QtWidgets
from qgis.PyQt.QtCore import Qt

from safe.utilities.resources import resources_path, get_ui_class
from safe.utilities.help import get_help_html


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

        self.help_web_view.setHtml(get_help_html(message))
