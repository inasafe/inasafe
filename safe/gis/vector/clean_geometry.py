# coding=utf-8

"""Try to make a layer valid."""

from safe.common.custom_logging import LOGGER
from safe.definitions.processing_steps import clean_geometry_steps
from safe.gis.sanity_check import check_layer
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def clean_layer(layer):
    """Clean a vector layer.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :return: The buffered vector layer.
    :rtype: QgsVectorLayer
    """
    output_layer_name = clean_geometry_steps['output_layer_name']
    output_layer_name = output_layer_name % layer.keywords['layer_purpose']

    # start editing
    layer.startEditing()
    count = 0

    # iterate through all features
    for feature in layer.getFeatures():
        geom = feature.geometry()
        geometry_cleaned = geometry_checker(geom)
        if geometry_cleaned:
            feature.setGeometry(geometry_cleaned)
        else:
            count += 1
            layer.deleteFeature(feature.id())

    if count:
        LOGGER.critical(
            '%s features have been removed from %s because of invalid '
            'geometries.' % (count, layer.name()))
    else:
        LOGGER.info(
            '0 feature has been removed from the layer: %s' % layer.name())

    # save changes
    layer.commitChanges()

    layer.keywords['title'] = output_layer_name

    check_layer(layer)
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
        if new_geom.isGeosValid():
            return new_geom
        else:
            # Buffer 0 is not enough, the feature will be deleted.
            return None
