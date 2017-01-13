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
def buffering(layer, radius, callback=None):
    """Buffer a vector layer using a single radius.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :param radius: The radius.
    :type radius: int

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The buffered vector layer.
    :rtype: QgsVectorLayer
    """
    pass
