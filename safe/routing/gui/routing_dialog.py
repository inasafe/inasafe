# coding=utf-8

import os
import logging

from qgis.gui import QgsMapToolPan
from PyQt4.QtGui import QDialog
from PyQt4 import uic

from safe.utilities.qgis_utilities import display_information_message_box


LOGGER = logging.getLogger('InaSAFE')

ui_file = os.path.join(os.path.dirname(__file__), 'routing_dialog_base.ui')
FORM_CLASS, BASE_CLASS = uic.loadUiType(ui_file)


class RoutingDialog(QDialog, FORM_CLASS):
    """Routing analysis."""

    def __init__(self, parent=None, iface=None):
        """Constructor for import dialog.

        :param parent: Optional widget to use as parent
        :type parent: QWidget

        :param iface: An instance of QGisInterface
        :type iface: QGisInterface
        """
        QDialog.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)

        self.setWindowTitle(self.tr('InaSAFE Routing Analysis'))

        self.iface = iface
