# coding=utf-8

"""
Clip and mask a hazard layer.

Issue https://github.com/inasafe/inasafe/issues/3186
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
from safe.common.exceptions import InvalidKeywordsForProcessingAlgorithm
# from safe.definitionsv4.processing import intersection_vector
from safe.gisv4.vector.tools import create_memory_layer, wkb_type_groups
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


LOGGER = logging.getLogger('InaSAFE')


@profile
def intersection(layer_to_clip, mask_layer, callback=None):
    """Clip and mask a vector layer.

    Note : This algorithm is copied from :
    https://github.com/qgis/QGIS/blob/master/python/plugins/processing/algs/
    qgis/Intersection.py

    :param layer_to_clip: The vector layer to clip.
    :type layer_to_clip: QgsVectorLayer

    :param mask_layer: The vector layer to use for clipping.
    :type mask_layer: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The clip vector layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    # To fix
    # output_layer_name = intersection_vector['output_layer_name']
    # processing_step = intersection_vector['step_name']
    output_layer_name = 'clip'
    processing_step = 'Clipping and masking'

    fields = layer_to_clip.fields()
    fields.extend(mask_layer.fields())

    writer = create_memory_layer(
        output_layer_name,
        layer_to_clip.geometryType(),
        layer_to_clip.crs(),
        fields
    )

    # Specific to InaSAFE
    clip_purpose = layer_to_clip.keywords['layer_purpose']
    mask_purpose = mask_layer.keywords['layer_purpose']
    inasafe_fields = layer_to_clip.keywords['inasafe_fields'].copy()
    inasafe_fields.update(mask_layer.keywords['inasafe_fields'])

    writer.keywords = layer_to_clip.keywords.copy()
    writer.keywords['inasafe_fields'] = inasafe_fields

    not_transfer_attributes = False
    if clip_purpose == 'hazard' and mask_purpose == 'aggregation':
        writer.keywords['layer_purpose'] = 'aggregate_hazard'
    elif clip_purpose == 'exposure' and mask_purpose == 'aggregation':
        writer.keywords['layer_purpose'] = 'exposure'
    elif clip_purpose == 'exposure' and mask_purpose == 'aggregate_hazard':
        writer.keywords['layer_purpose'] = 'impact'
        not_transfer_attributes = True
    else:
        msg = 'I got clip purpose = %s and mask purpose = %s'\
              % (clip_purpose, mask_purpose)
        raise InvalidKeywordsForProcessingAlgorithm(msg)

    writer.startEditing()

    # Begin copy/paste from Processing plugin.
    # Please follow their code as their code is optimized.

    out_feature = QgsFeature()
    index = QgsSpatialIndex(mask_layer.getFeatures())

    # Todo callback
    # total = 100.0 / len(selectionA)

    for current, in_feature in enumerate(layer_to_clip.getFeatures()):
        # progress.setPercentage(int(current * total))
        geom = in_feature.geometry()
        attributes = in_feature.attributes()
        intersects = index.intersects(geom.boundingBox())
        for i in intersects:
            request = QgsFeatureRequest().setFilterFid(i)
            feature_mask = next(mask_layer.getFeatures(request))
            tmp_geom = feature_mask.geometry()
            if geom.intersects(tmp_geom):
                mask_attributes = feature_mask.attributes()
                int_geom = QgsGeometry(geom.intersection(tmp_geom))
                if int_geom.wkbType() == QgsWKBTypes.Unknown\
                        or QgsWKBTypes.flatType(
                        int_geom.geometry().wkbType()) ==\
                                QgsWKBTypes.GeometryCollection:
                    int_com = geom.combine(tmp_geom)
                    int_geom = QgsGeometry()
                    if int_com:
                        int_sym = geom.symDifference(tmp_geom)
                        int_geom = QgsGeometry(int_com.difference(int_sym))
                if int_geom.isGeosEmpty() or not int_geom.isGeosValid():
                    LOGGER.debug(
                        tr('GEOS geoprocessing error: One or more input '
                           'features have invalid geometry.'))
                try:
                    geom_types = wkb_type_groups[
                        wkb_type_groups[int_geom.wkbType()]]
                    if int_geom.wkbType() in geom_types:
                        out_feature.setGeometry(int_geom)
                        attrs = []
                        attrs.extend(attributes)
                        attrs.extend(mask_attributes)
                        out_feature.setAttributes(attrs)
                        writer.addFeature(out_feature)
                except:
                    LOGGER.debug(
                        tr('Feature geometry error: One or more output '
                           'features ignored due to invalid geometry.'))
                    continue

    # End copy/paste from Processing plugin.
    writer.commitChanges()

    return writer
