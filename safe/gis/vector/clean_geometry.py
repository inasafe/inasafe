# coding=utf-8

"""Try to make a layer valid."""
from qgis.core import QgsFeatureRequest

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
    request = QgsFeatureRequest().setSubsetOfAttributes([])
    for feature in layer.getFeatures(request):
        geom = feature.geometry()
        was_valid, geometry_cleaned = geometry_checker(geom)

        if was_valid:
            # Do nothing if it was valid
            pass
        elif not was_valid and geometry_cleaned:
            # Update the geometry if it was not valid, and clean now
            layer.changeGeometry(feature.id(), geometry_cleaned, True)
        else:
            # Delete if it was not valid and not able to be cleaned
            count += 1
            layer.deleteFeature(feature.id())

    if count:
        LOGGER.critical(
            '%s features have been removed from %s because of invalid '
            'geometries.' % (count, layer.name()))
    else:
        LOGGER.info(
            'No feature has been removed from the layer: %s' % layer.name())

    # save changes
    layer.commitChanges()
    layer.keywords['title'] = output_layer_name

    check_layer(layer)
    return layer


def geometry_checker(geometry):
    """Perform a cleaning if the geometry is not valid.

    :param geometry: The geometry to check and clean.
    :type geometry: QgsGeometry

    :return: Tuple of bool and cleaned geometry. True if the geometry is
        already valid, False if the geometry was not valid.
        A cleaned geometry, or None if the geometry could not be repaired
    :rtype: (bool, QgsGeometry)
    """
    if geometry is None:
        # The geometry can be None.
        return False, None

    if geometry.isGeosValid():
        return True, geometry
    else:
        new_geom = geometry.makeValid()
        if new_geom.isGeosValid():
            return False, new_geom
        else:
            # Make valid was not enough, the feature will be deleted.
            return False, None
