# coding=utf-8

"""
Assign the highest value to an exposure according to a hazard layer.

Issue https://github.com/inasafe/inasafe/issues/3192
"""

from builtins import next
from builtins import zip
import logging
from qgis.core import (
    QGis,
    QgsFeatureRequest,
    QgsWKBTypes,
)

from safe.common.exceptions import InvalidKeywordsForProcessingAlgorithm
from safe.definitionsv4.layer_purposes import layer_purpose_exposure_impacted
from safe.definitionsv4.fields import hazard_class_field
from safe.definitionsv4.hazard_classifications import (
    hazard_classification, null_hazard_value)
from safe.definitionsv4.processing_steps import assign_highest_value_steps
from safe.gisv4.vector.tools import create_spatial_index
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


LOGGER = logging.getLogger('InaSAFE')


@profile
def assign_highest_value(exposure, hazard, callback=None):
    """For indivisible polygon exposure layers such as buildings, we need to
    assigned the greatest hazard that each polygon touches and use that as the
     effective hazard class.

    We follow the concept here that any part of the exposure dataset that
    touches the hazard is affected, and the greatest hazard is the effective
    hazard.

    :param exposure: The building vector layer.
    :type exposure: QgsVectorLayer

    :param hazard: The vector layer to use for hazard.
    :type hazard: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The new impact layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = assign_highest_value_steps['output_layer_name']
    processing_step = assign_highest_value_steps['step_name']

    hazard_inasafe_fields = hazard.keywords['inasafe_fields']

    if not hazard.keywords.get('classification'):
        raise InvalidKeywordsForProcessingAlgorithm
    if not hazard_inasafe_fields.get(hazard_class_field['key']):
        raise InvalidKeywordsForProcessingAlgorithm

    indices = []
    exposure.startEditing()
    for field in hazard.fields():
        exposure.addAttribute(field)
        indices.append(exposure.fieldNameIndex(field.name()))
    exposure.commitChanges()
    provider = exposure.dataProvider()

    spatial_index = create_spatial_index(exposure)

    # Todo callback
    # total = 100.0 / len(selectionA)

    hazard_field = hazard_inasafe_fields[hazard_class_field['key']]

    layer_classification = None
    for classification in hazard_classification['types']:
        if classification['key'] == hazard.keywords['classification']:
            layer_classification = classification
            break

    # Get a ordered list of classes like ['high', 'medium', 'low']
    levels = [key['key'] for key in layer_classification['classes']]
    levels.append(null_hazard_value)

    # Let's loop over the hazard layer, from high to low hazard zone.
    for hazard_value in levels:
        expression = '"%s" = \'%s\'' % (hazard_field, hazard_value)
        hazard_request = QgsFeatureRequest().setFilterExpression(expression)
        update_map = {}
        for area in hazard.getFeatures(hazard_request):
            geometry = area.geometry()
            intersects = spatial_index.intersects(geometry.boundingBox())

            # We need to loop over each intersections exposure / hazard.
            for i in intersects:
                request = QgsFeatureRequest().setFilterFid(i)
                building = next(exposure.getFeatures(request))
                building_geometry = building.geometry()

                if geometry.intersects(building_geometry):
                    update_map[building.id()] = {}
                    for index, value in zip(indices, area.attributes()):
                        update_map[building.id()][index] = value

                    # We don't want this building again, let's remove it from
                    # the index.
                    spatial_index.deleteFeature(building)

        provider.changeAttributeValues(update_map)

    exposure.updateExtents()
    exposure.updateFields()

    exposure.keywords['inasafe_fields'].update(
        hazard.keywords['inasafe_fields'])
    exposure.keywords['layer_purpose'] = layer_purpose_exposure_impacted['key']

    exposure.keywords['exposure_keywords'] = exposure.keywords.copy()
    exposure.keywords['aggregation_keywords'] = (
        hazard.keywords['aggregation_keywords'].copy())
    exposure.keywords['hazard_keywords'] = (
        hazard.keywords['hazard_keywords'].copy())

    exposure.keywords['title'] = output_layer_name

    return exposure
