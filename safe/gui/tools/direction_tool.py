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

        ok_button = self.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        ok_button.clicked.connect(self.accept)
        cancel_button = self.buttonBox.button(QtGui.QDialogButtonBox.Cancel)
        cancel_button.clicked.connect(self.reject)

    # def on_hazard_layer_currentIndexChanged(self):
    #     hazard_layer = self.hazard_layer.currentLayer()
    #     print hazard_layer.name()

    def bearing_to_cardinal(self, bearing_angle):

        direction_list = [
            'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE',
            'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WW',
            'NW', 'NNW'
        ]

        try:
            bearing = float(bearing_angle)
        except ValueError:
            LOGGER.exception('Error casting bearing to a float')

        direction_count = len(direction_list)
        direction_interval = 360. / direction_count
        index = int(round(bearing / direction_interval))
        index %= direction_count
        return direction_list[index]

    def calculate_bearing(self, hazard_layer, exposure_layer):
        '''Calculate bearing angle.

        :param point_a: Hazard Layer
        :type point_a: QgsPointLayer
        :param point_b: ExposureLayer
        :type point_b: QgsPointLayer
        '''

        # point_a.azimuth(point_b)



    def accept(self):

        bearing = self.new_field_name.text()
        bearing = float(bearing)

        cardinal = self.bearing_to_cardinal(bearing)
        print cardinal