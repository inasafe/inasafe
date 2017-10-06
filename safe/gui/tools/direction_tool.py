from PyQt4 import QtGui
from PyQt4.QtCore import QVariant
from safe.utilities.resources import get_ui_class
from qgis.gui import QgsMapLayerProxyModel
from qgis.core import (
    QgsDistanceArea,
    QgsFeature,
    QgsGeometry,
    QgsField,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform)
import math

FORM_CLASS = get_ui_class('direction_tool_base.ui')

class DirectionTool(QtGui.QDialog, FORM_CLASS):
    """Direction Tool"""

    def __init__(self, parent=None, iface=None):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.parent = parent
        self.iface = iface

        self.hazard.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.exposure.setFilters(QgsMapLayerProxyModel.PointLayer)

        ok_button = self.buttonBox.button(QtGui.QDialogButtonBox.Ok)
        ok_button.clicked.connect(self.accept)
        cancel_button = self.buttonBox.button(QtGui.QDialogButtonBox.Cancel)
        cancel_button.clicked.connect(self.reject)

    def bearing_to_cardinal(self, bearing_angle):
        """

        :param bearing_angle:
        :return:
        """
        direction_list = [
            'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE',
            'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WW',
            'NW', 'NNW'
        ]

        try:
            bearing = float(bearing_angle)
        except ValueError:
            print 'Error casting bearing to a float'

        direction_count = len(direction_list)
        direction_interval = 360. / direction_count
        index = int(round(bearing / direction_interval))
        index %= direction_count
        return direction_list[index]


    def distance_and_bearing(self, hazard_layer, exposure_layer, update_layer=True):
        '''Calculate bearing angle.

        :param point_a: Hazard Layer
        :type point_a: QgsPointLayer
        :param point_b: ExposureLayer
        :type point_b: QgsPointLayer
        '''
        index = 0
        distance = QgsDistanceArea()
        distance.setEllipsoidalMode(True)
        distance.setEllipsoid('WGS84')
        exposure_provider = exposure_layer.dataProvider()
        for field in exposure_provider.fields():
            index += 1
        exposure_provider.addAttributes([
            QgsField('distance', QVariant.Double),
            QgsField('bearing', QVariant.Double),
            QgsField('direction', QVariant.String)
        ])
        distance_index = index
        bearing_index = index + 1
        direction_index = index + 2

        hazard_feature_list = []
        for feature in hazard_layer.getFeatures():
            hazard_feature_list.append(feature)
        if len(hazard_feature_list) <= 1:
            hazard_feature = hazard_feature_list[0]
        else:
            print 'hazard layer contain more than one feature'  # implement logging later
            print 'using the first feature as default'          # implement logging later
            hazard_feature = hazard_feature_list[0]
        hazard_point = hazard_feature.geometry().asPoint()
        exposure_layer.startEditing()
        for feature in exposure_layer.getFeatures():
            fid = feature.id()
            exposure_point = feature.geometry().asPoint()
            # calculate cardinality
            bearing_angle = hazard_point.azimuth(exposure_point)
            cardinality = self.bearing_to_cardinal(bearing_angle)
            # calculate distance
            measure_distance = distance.measureLine(hazard_point, exposure_point)

            exposure_layer.changeAttributeValue(fid, distance_index, measure_distance)
            exposure_layer.changeAttributeValue(fid, bearing_index, bearing_angle)
            exposure_layer.changeAttributeValue(fid, direction_index, cardinality)

        exposure_layer.commitChanges()

    def accept(self):
        print 'run'
        self.hazard_layer = self.hazard.currentLayer()
        self.exposure_layer = self.exposure.currentLayer()
        self.distance_and_bearing(self.hazard_layer, self.exposure_layer)
        print 'finished'
