# coding=utf-8

"""Try to make a layer valid."""
import processing

from safe.common.custom_logging import LOGGER
from safe.common.exceptions import ProcessingInstallationError
from safe.definitions.processing_steps import clean_geometry_steps
from safe.gis.processing_tools import (
    initialize_processing,
    create_processing_feedback,
    create_processing_context)
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
    :type layer: qgis.core.QgsVectorLayer

    :return: The buffered vector layer.
    :rtype: qgis.core.QgsVectorLayer
    """
    output_layer_name = clean_geometry_steps['output_layer_name']
    output_layer_name = output_layer_name % layer.keywords['layer_purpose']

    count = layer.featureCount()

    parameters = {
        'INPUT': layer,
        'OUTPUT': 'memory:'
    }

    initialize_processing()

    feedback = create_processing_feedback()
    context = create_processing_context(feedback=feedback)
    result = processing.run('qgis:fixgeometries', parameters, context=context)
    if result is None:
        raise ProcessingInstallationError

    cleaned = result['OUTPUT']
    cleaned.setName(output_layer_name)

    removed_count = count - cleaned.featureCount()

    if removed_count:
        LOGGER.critical(
            '{removed_count} features have been removed from {layer_name} '
            'because of invalid geometries.'.format(
                removed_count=removed_count,
                layer_name=layer.name()))
    else:
        LOGGER.info(
            'No feature has been removed from the layer: '
            '{layer_name}'.format(layer_name=layer.name()))

    cleaned.keywords = layer.keywords.copy()
    cleaned.keywords['title'] = output_layer_name
    check_layer(cleaned)

    return cleaned


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
