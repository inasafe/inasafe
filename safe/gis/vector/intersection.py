# coding=utf-8

"""Intersect two layers."""

import logging

from qgis.core import (
    QgsGeometry,
    QgsFeatureRequest,
    QgsWKBTypes,
    QgsFeature,
)

from safe.definitions.layer_purposes import layer_purpose_exposure_summary
from safe.definitions.processing_steps import intersection_steps
from safe.gis.sanity_check import check_layer
from safe.gis.vector.tools import (
    create_memory_layer, wkb_type_groups, create_spatial_index)
from safe.utilities.i18n import tr
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


LOGGER = logging.getLogger('InaSAFE')


@profile
def intersection(source, mask, callback=None):
    """Intersect two layers.

    Issue https://github.com/inasafe/inasafe/issues/3186

    Note : This algorithm is copied from :
    https://github.com/qgis/QGIS/blob/master/python/plugins/processing/algs/
    qgis/Intersection.py

    :param source: The vector layer to clip.
    :type source: QgsVectorLayer

    :param mask: The vector layer to use for clipping.
    :type mask: QgsVectorLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int), 'maximum' (int) and 'step' (str).
        Defaults to None.
    :type callback: function

    :return: The clip vector layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = intersection_steps['output_layer_name']
    output_layer_name = output_layer_name % (
        source.keywords['layer_purpose'])
    processing_step = intersection_steps['step_name']  # NOQA

    fields = source.fields()
    fields.extend(mask.fields())

    writer = create_memory_layer(
        output_layer_name,
        source.geometryType(),
        source.crs(),
        fields
    )

    writer.startEditing()

    # Begin copy/paste from Processing plugin.
    # Please follow their code as their code is optimized.
    # The code below is not following our coding standards because we want to
    # be able to track any diffs from QGIS easily.

    out_feature = QgsFeature()
    index = create_spatial_index(mask)

    # Todo callback
    # total = 100.0 / len(selectionA)

    for current, in_feature in enumerate(source.getFeatures()):
        # progress.setPercentage(int(current * total))
        geom = in_feature.geometry()
        attributes = in_feature.attributes()
        intersects = index.intersects(geom.boundingBox())
        for i in intersects:
            request = QgsFeatureRequest().setFilterFid(i)
            feature_mask = next(mask.getFeatures(request))
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
                    # LOGGER.debug(
                    #     tr('GEOS geoprocessing error: One or more input '
                    #        'features have invalid geometry.'))
                    pass
                try:
                    geom_types = wkb_type_groups[
                        wkb_type_groups[int_geom.wkbType()]]
                    if int_geom.wkbType() in geom_types:
                        if int_geom.type() == source.geometryType():
                            # We got some features which have not the same
                            # kind of geometry. We want to skip them.
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

    writer.keywords = dict(source.keywords)
    writer.keywords['title'] = output_layer_name
    writer.keywords['layer_purpose'] = layer_purpose_exposure_summary['key']
    writer.keywords['inasafe_fields'] = dict(source.keywords['inasafe_fields'])
    writer.keywords['inasafe_fields'].update(mask.keywords['inasafe_fields'])
    writer.keywords['hazard_keywords'] = dict(mask.keywords['hazard_keywords'])
    writer.keywords['exposure_keywords'] = dict(source.keywords)
    writer.keywords['aggregation_keywords'] = dict(
        mask.keywords['aggregation_keywords'])

    check_layer(writer)
    return writer
