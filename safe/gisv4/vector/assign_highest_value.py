# coding=utf-8

"""
Assign the highest value to an exposure according to a hazard layer.

Issue https://github.com/inasafe/inasafe/issues/3192
"""

import logging
from qgis.core import (
    QGis,
    QgsGeometry,
    QgsFeatureRequest,
    QgsWKBTypes,
    QgsFeature,
    QgsSpatialIndex
)

from safe.utilities.i18n import tr
from safe.definitionsv4.fields import hazard_class_field
from safe.definitionsv4.hazard_classifications import hazard_classification
# from safe.definitionsv4.processing import assign_highest_value
from safe.gisv4.vector.tools import create_memory_layer, wkb_type_groups
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


LOGGER = logging.getLogger('InaSAFE')


@profile
def assign_highest_value(exposure_layer, hazard_layer, callback=None):
    """For indivisible polygon exposure layers such as buildings, we need to
    assigned the greatest hazard that each polygon touches and use that as the
     effective hazard class.

    We follow the concept here that any part of the exposure dataset that
    touches the hazard is affected, and the greatest hazard is the effective
    hazard.

    :param exposure_layer: The building vector layer.
    :type exposure_layer: QgsVectorLayer

    :param hazard_layer: The vector layer to use for hazard.
    :type hazard_layer: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The new impact layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    # To fix
    # output_layer_name = intersection_vector['output_layer_name']
    # processing_step = intersection_vector['step_name']
    output_layer_name = 'highest_hazard_value'
    processing_step = 'Assigning the highest hazard value'

    # We add exposure and hazard fields to the out layer.
    fields = exposure_layer.fields()
    for field in hazard_layer.fields():
        fields.append(field)

    # We create the memory layer.
    writer = create_memory_layer(
        output_layer_name,
        exposure_layer.geometryType(),
        exposure_layer.crs(),
        fields
    )
    writer.startEditing()

    spatial_index = QgsSpatialIndex(hazard_layer.getFeatures())

    # Todo callback
    # total = 100.0 / len(selectionA)

    hazard_keywords = hazard_layer.keywords
    inasafe_fields = hazard_keywords['inasafe_fields']
    hazard_field = inasafe_fields[hazard_class_field['key']]
    index = hazard_layer.fieldNameIndex(hazard_field)

    for classification in hazard_classification['types']:
        if classification['key'] == hazard_keywords['hazard_classification']:
            layer_classification = classification
            break

    # Get a ordered list of classes like ['low', 'medium', 'high']
    levels = list(
        reversed([key['key'] for key in layer_classification['classes']]))

    out_feature = QgsFeature()

    # Let's loop over the exposure layer.
    for current, in_feature in enumerate(exposure_layer.getFeatures()):
        # progress.setPercentage(int(current * total))
        geom = in_feature.geometry()
        attributes = in_feature.attributes()

        intersects = spatial_index.intersects(geom.boundingBox())

        highest_hazard_value = [None, None]

        # We need to loop over each intersections exposure / aggregate hazard.
        for i in intersects:
            request = QgsFeatureRequest().setFilterFid(i)
            feature_hazard = next(hazard_layer.getFeatures(request))

            tmp_geom = feature_hazard.geometry()

            if geom.intersects(tmp_geom):

                # We get the value of the hazard.
                hazard_value = feature_hazard.attributes()[index]

                # If the hazard is null, we skip.
                if not hazard_value:
                    continue

                # If it's the first time in the loop, we assign the value.
                if not highest_hazard_value[0]:
                    highest_hazard_value = (
                        levels.index(hazard_value),
                        feature_hazard.attributes()
                    )

                # We compare to a previous feature if the hazard is higher :
                if levels.index(hazard_value) > highest_hazard_value[0]:
                    highest_hazard_value = (
                        levels.index(hazard_value),
                        feature_hazard.attributes()
                    )

                # We compare size if same hazard value :
                if levels.index(hazard_value) == highest_hazard_value[1]:
                    # TODO We should add another test to check the biggest
                    # aggregation area.
                    highest_hazard_value = (
                        levels.index(hazard_value),
                        feature_hazard.attributes()
                    )

        out_feature.setGeometry(geom)
        attrs = []
        attrs.extend(attributes)
        if highest_hazard_value[0] is not None:
            attrs.extend(highest_hazard_value[1])
        else:
            attrs.extend([])
        out_feature.setAttributes(attrs)
        writer.addFeature(out_feature)

    writer.commitChanges()

    inasafe_fields = exposure_layer.keywords['inasafe_fields'].copy()
    inasafe_fields.update(hazard_layer.keywords['inasafe_fields'])
    writer.keywords['inasafe_fields'] = inasafe_fields
    writer.keywords['layer_purpose'] = 'aggregate_hazard'

    return writer
