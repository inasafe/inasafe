# coding=utf-8

"""Clip and mask a hazard layer."""

import logging

from qgis.core import (
    QgsGeometry,
    QgsFeatureRequest,
    QgsWKBTypes,
    QgsFeature,
)

from safe.definitions.processing_steps import clip_steps
from safe.gis.sanity_check import check_layer
from safe.gis.vector.tools import create_memory_layer
from safe.utilities.i18n import tr
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


LOGGER = logging.getLogger('InaSAFE')


@profile
def clip(layer_to_clip, mask_layer, callback=None):
    """Clip a vector layer with another.

    Issue https://github.com/inasafe/inasafe/issues/3186

    Note : This algorithm is copied from :
    https://github.com/qgis/QGIS/blob/master/python/plugins/processing/algs/
    qgis/Clip.py

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
    output_layer_name = clip_steps['output_layer_name']
    output_layer_name = output_layer_name % (
        layer_to_clip.keywords['layer_purpose'])
    processing_step = clip_steps['step_name']  # NOQA

    writer = create_memory_layer(
        output_layer_name,
        layer_to_clip.geometryType(),
        layer_to_clip.crs(),
        layer_to_clip.fields()
    )
    writer.startEditing()

    # Begin copy/paste from Processing plugin.
    # Please follow their code as their code is optimized.
    # The code below is not following our coding standards because we want to
    # be able to track any diffs from QGIS easily.

    # first build up a list of clip geometries
    clip_geometries = []
    request = QgsFeatureRequest().setSubsetOfAttributes([])
    for mask_feature in mask_layer.getFeatures(request):
        clip_geometries.append(QgsGeometry(mask_feature.geometry()))

    # are we clipping against a single feature? if so,
    # we can show finer progress reports
    if len(clip_geometries) > 1:
        # noinspection PyTypeChecker,PyCallByClass,PyArgumentList
        combined_clip_geom = QgsGeometry.unaryUnion(clip_geometries)
        single_clip_feature = False
    else:
        combined_clip_geom = clip_geometries[0]
        single_clip_feature = True

    # use prepared geometries for faster intersection tests
    # noinspection PyArgumentList
    engine = QgsGeometry.createGeometryEngine(combined_clip_geom.geometry())
    engine.prepareGeometry()

    tested_feature_ids = set()

    for i, clip_geom in enumerate(clip_geometries):
        request = QgsFeatureRequest().setFilterRect(clip_geom.boundingBox())
        input_features = [f for f in layer_to_clip.getFeatures(request)]

        if not input_features:
            continue

        # if single_clip_feature:
        #     total = 100.0 / len(input_features)
        # else:
        #     total = 0

        for current, in_feat in enumerate(input_features):
            if not in_feat.geometry():
                continue

            if in_feat.id() in tested_feature_ids:
                # don't retest a feature we have already checked
                continue

            tested_feature_ids.add(in_feat.id())

            if not engine.intersects(in_feat.geometry().geometry()):
                continue

            if not engine.contains(in_feat.geometry().geometry()):
                cur_geom = in_feat.geometry()
                new_geom = combined_clip_geom.intersection(cur_geom)
                if new_geom.wkbType() == QgsWKBTypes.Unknown \
                        or QgsWKBTypes.flatType(
                        new_geom.geometry().wkbType()) == \
                        QgsWKBTypes.GeometryCollection:
                    int_com = in_feat.geometry().combine(new_geom)
                    int_sym = in_feat.geometry().symDifference(new_geom)
                    if not int_com or not int_sym:
                        # LOGGER.debug(
                        #     tr('GEOS geoprocessing error: One or more input '
                        #        'features have invalid geometry.'))
                        pass
                    else:
                        new_geom = int_com.difference(int_sym)
                        if new_geom.isGeosEmpty()\
                                or not new_geom.isGeosValid():
                            # LOGGER.debug(
                            #     tr('GEOS geoprocessing error: One or more '
                            #        'input features have invalid geometry.'))
                            pass
            else:
                # clip geometry totally contains feature geometry,
                # so no need to perform intersection
                new_geom = in_feat.geometry()

            try:
                out_feat = QgsFeature()
                out_feat.setGeometry(new_geom)
                out_feat.setAttributes(in_feat.attributes())
                if new_geom.type() == layer_to_clip.geometryType():
                    writer.addFeature(out_feat)
            except:
                LOGGER.debug(
                    tr('Feature geometry error: One or more output features '
                       'ignored due to invalid geometry.'))
                continue

            # TODO implement callback
            if single_clip_feature:
                # progress.setPercentage(int(current * total))
                pass

        if not single_clip_feature:
            # coarse progress report for multiple clip geometries
            # progress.setPercentage(100.0 * i / len(clip_geoms))
            pass

    # End copy/paste from Processing plugin.
    writer.commitChanges()

    writer.keywords = layer_to_clip.keywords.copy()
    writer.keywords['title'] = output_layer_name
    check_layer(writer)
    return writer
