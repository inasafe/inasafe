# coding=utf-8

"""Buffer a vector layer using many buffers (for volcanoes or rivers)."""

from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsGeometry,
    QgsFeature,
    QgsWkbTypes,
)

from safe.common.utilities import get_utm_epsg
from safe.definitions.fields import hazard_class_field, buffer_distance_field
from safe.definitions.layer_purposes import layer_purpose_hazard
from safe.definitions.processing_steps import buffer_steps
from safe.gis.sanity_check import check_layer
from safe.gis.vector.tools import (
    create_memory_layer,
    create_field_from_definition)
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def multi_buffering(layer, radii, callback=None):
    """Buffer a vector layer using many buffers (for volcanoes or rivers).

    This processing algorithm will keep the original attribute table and
    will add a new one for the hazard class name according to
    safe.definitions.fields.hazard_value_field.

    radii = OrderedDict()
    radii[500] = 'high'
    radii[1000] = 'medium'
    radii[2000] = 'low'

    Issue https://github.com/inasafe/inasafe/issues/3185

    :param layer: The layer to polygonize.
    :type layer: QgsVectorLayer

    :param radii: A dictionary of radius.
    :type radii: OrderedDict

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The buffered vector layer.
    :rtype: QgsVectorLayer
    """
    # Layer output
    output_layer_name = buffer_steps['output_layer_name']
    processing_step = buffer_steps['step_name']

    input_crs = layer.crs()
    feature_count = layer.featureCount()

    fields = layer.fields()
    # Set the new hazard class field.
    new_field = create_field_from_definition(hazard_class_field)
    fields.append(new_field)
    # Set the new buffer distances field.
    new_field = create_field_from_definition(buffer_distance_field)
    fields.append(new_field)

    buffered = create_memory_layer(
        output_layer_name, QgsWkbTypes.PolygonGeometry, input_crs, fields)
    buffered.startEditing()

    # Reproject features if needed into UTM if the layer is in 4326.
    if layer.crs().authid() == 'EPSG:4326':
        center = layer.extent().center()
        utm = QgsCoordinateReferenceSystem(
            get_utm_epsg(center.x(), center.y(), input_crs))
        transform = QgsCoordinateTransform(layer.crs(), utm)
        reverse_transform = QgsCoordinateTransform(utm, layer.crs())
    else:
        transform = None
        reverse_transform = None

    for i, feature in enumerate(layer.getFeatures()):
        geom = QgsGeometry(feature.geometry())

        if transform:
            geom.transform(transform)

        inner_ring = None

        for radius in radii:
            attributes = feature.attributes()

            # We add the hazard value name to the attribute table.
            attributes.append(radii[radius])
            # We add the value of buffer distance to the attribute table.
            attributes.append(radius)

            circle = geom.buffer(radius, 30)

            if inner_ring:
                circle.addRing(inner_ring)

            inner_ring = circle.asPolygon()[0]

            new_feature = QgsFeature()
            if reverse_transform:
                circle.transform(reverse_transform)

            new_feature.setGeometry(circle)
            new_feature.setAttributes(attributes)

            buffered.addFeature(new_feature)

        if callback:
            callback(current=i, maximum=feature_count, step=processing_step)

    buffered.commitChanges()

    # We transfer keywords to the output.
    buffered.keywords = layer.keywords
    buffered.keywords['layer_geometry'] = 'polygon'
    buffered.keywords['layer_purpose'] = layer_purpose_hazard['key']
    buffered.keywords['inasafe_fields'][hazard_class_field['key']] = (
        hazard_class_field['field_name'])

    check_layer(buffered)
    return buffered
