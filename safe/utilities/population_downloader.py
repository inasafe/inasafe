# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Import Dialog.**
Contact : etienne@kartoza.com
.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
__author__ = 'oscar mbita (mgwetam@gmail.com)'
__date__ = '8/02/2016'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
from qgis.core import (
    QGis,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsPoint,
    QgsGeometry,
    QgsRectangle,
    QgsVectorLayer,
    QgsMapLayerRegistry,
    QgsCoordinateReferenceSystem,
    QgsVectorFileWriter,
    QgsNetworkAccessManager
)

from qgis.utils import iface

from safe.common.utilities import (
    format_int,
    unique_filename
)

from PyQt4.QtGui import (
    QApplication,
    QCursor)

from PyQt4.QtCore import (
    QVariant,
    Qt)
from safe.utilities.request import Request

import logging
import json

LOGGER = logging.getLogger('InaSAFE')


def download(
        output_base_path,
        extent,
        rectangle,
        progress_dialog=None):
    """Download worldpop data

    :param output_base_path: The base path of the shape file.
    :type output_base_path: str

    :param extent: A list in the form [xmin, ymin, xmax, ymax] where all
    coordinates provided are in Geographic / EPSG:4326.
    :type extent: list

    :param rectangle: Bounding box rectangle
    coordinates provided are in Geographic / EPSG:4326.
    :type rectangle: QgsRectangle

    :param progress_dialog: A progress dialog.
    :type progress_dialog: QProgressDialog

    :raises: ImportDialogError, CanceledImportDialogError
    """
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

    # preparing coordinates of the dragged area
    min_longitude = extent[0]
    min_latitude = extent[1]
    max_longitude = extent[2]
    max_latitude = extent[3]

    min_long_max_lat = [min_longitude, max_latitude]
    max_long_max_lat = [max_longitude, max_latitude]
    max_long_min_lat = [max_longitude, min_latitude]
    min_long_min_lat = [min_longitude, min_latitude]

    points = [
        min_long_max_lat,
        max_long_max_lat,
        max_long_min_lat,
        min_long_min_lat]

    coordinates = '[[' + str(min_long_max_lat) + ',' + \
                  str(max_long_max_lat) + ',' + \
                  str(max_long_min_lat) + ',' + \
                  str(min_long_min_lat) + ',' + \
                  str(min_long_max_lat) + ']]'

    data = 'coordinates=' + str(coordinates)

    # python requests to fetch json data from api
    url = 'https://worldpop-api-server.herokuapp.com/api'

    request = Request(url, progress_dialog)
    response = request.post(data)

    if response[0] is not False:
        population_data = str(response[1])

        file_path = output_base_path + '.geojson'

        with open(file_path, 'w+') as outfile:
            outfile.write(population_data)

        create_layer(population_data, points)

        QApplication.restoreOverrideCursor()
    else:
        _, error_message = response

        raise Exception(error_message)


def create_layer(data, points):
    """  Create vector layer from given data with a polygon
    from the given rectangle

    :param data: number of population
    :type data: {}

    :param points: population area coordinate points
    :type points:[]

    """
    filename = unique_filename(suffix='.shp')
    layer_crs = QgsCoordinateReferenceSystem("EPSG:4326")

    fields = QgsFields()
    fields.append(QgsField("pixelCount", QVariant.String))
    fields.append(QgsField("population", QVariant.String))
    fields.append(QgsField("area", QVariant.String))

    writer = QgsVectorFileWriter(
        filename,
        "utf-8",
        fields,
        QGis.WKBPolygon,
        layer_crs)

    # Adding new feature

    data = json.loads(data)
    population = int(data["totalPopulation"])
    # Correcting population value to right density
    # as the api return value exceeds by 10000

    population /= 10000
    population = int(population)
    population = format_int(population)

    qgs_points = []
    qgs_points.append(QgsPoint(points[0][0], points[0][1]))
    qgs_points.append(QgsPoint(points[1][0], points[1][1]))
    qgs_points.append(QgsPoint(points[2][0], points[2][1]))
    qgs_points.append(QgsPoint(points[3][0], points[3][1]))

    new_feature = QgsFeature(fields)
    geom = QgsGeometry.fromPolygon([qgs_points])
    new_feature.setGeometry(geom)

    new_feature.setAttribute('pixelCount', str(data["count"]))
    new_feature.setAttribute('population', str(population))
    new_feature.setAttribute('area', str(data["totalArea"]))

    writer.addFeature(new_feature)

    # Load layer into Qgis
    del writer

    layer = QgsVectorLayer(filename, 'Population Data', 'ogr')
    QgsMapLayerRegistry.instance().addMapLayers([layer])

    active_layer = iface.activeLayer()
    active_layer.setCustomProperty("labeling", "pal")
    active_layer.setCustomProperty("labeling/enabled", "true")
    active_layer.setCustomProperty("labeling/fontFamily", "Arial")
    active_layer.setCustomProperty("labeling/fontSize", "10")
    active_layer.setCustomProperty("labeling/fieldName", "population")
    active_layer.setCustomProperty("labeling/placement", "0")

    active_layer.setCustomProperty('transparency', '50')

    iface.mapCanvas().refresh()

    iface.zoomToActiveLayer()
