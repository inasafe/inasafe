from PyQt4 import QtGui
from safe.utilities.resources import get_ui_class
from qgis.gui import QgsMapLayerProxyModel

FORM_CLASS = get_ui_class('direction_tool_base.ui')

class DirectionTool(QtGui.QDialog, FORM_CLASS):
    """Direction Tool"""

    def __init__(self, parent=None, iface=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.parent = parent
        self.iface = iface

        self.hazard_layer.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.exposure_layer.setFilters(QgsMapLayerProxyModel.PointLayer)

    def accept(self):
        pass

    def on_hazard_layer_currentIndexChanged(self):
        print "Hazard Changed"
