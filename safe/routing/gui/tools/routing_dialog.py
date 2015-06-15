# coding=utf-8

import logging

from qgis.gui import QgsMapToolPan
from PyQt4.QtGui import QDialog

from safe.utilities.resources import get_ui_class
from safe.utilities.qgis_utilities import display_information_message_box


LOGGER = logging.getLogger('InaSAFE')

    ui_file_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.pardir,
            'gui',
            'ui',
            ui_file
        )
    )
    return uic.loadUiType(ui_file_path)[0]
FORM_CLASS = get_ui_class('routing_dialog_base.ui')


class RoutingAnalysisDialog(QDialog, FORM_CLASS):
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
