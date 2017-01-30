# coding=utf-8
"""Buffer a vector layer using a single radius."""

from qgis.core import (
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsGeometry,
    QgsFeature,
    QGis,
    QgsField,
)

from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def clean_layer(layer, callback=None):
    """Clean a vector layer.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        editing should accept params 'current' (int), 'maximum' (int) and
        'step' (str). Defaults to None.
    :type callback: function

    :return: The buffered vector layer.
    :rtype: QgsVectorLayer
    """
    # start editing
    layer.startEditing()

    # iterate through all features
    for feature in layer.getFeatures():
        geom = feature.geometry()
        feature.setGeometry(geometry_checker(geom))

    # save changes
    layer.commitChanges()

    return layer


def geometry_checker(geometry):
    """Perform a cleaning if the geometry is not valid.

    :param geometry: The geometry to check and clean.
    :type geometry: QgsGeometry

    :return: A cleaned geometry
    :rtype: QgsGeometry
    """
    if geometry is None:
        # The geometry can be None.
        return None

    if geometry.isGeosValid():
        return geometry
    else:
        new_geom = geometry.buffer(0, 5)
        return new_geom
