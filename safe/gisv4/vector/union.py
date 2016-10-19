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
# from safe.definitionsv4.processing import union
from safe.gisv4.vector.tools import create_memory_layer, wkb_type_groups
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


LOGGER = logging.getLogger('InaSAFE')


@profile
def union(union_a, union_b, callback=None):
    """Union of two vector layers.

    Note : This algorithm is copied from :
    https://github.com/qgis/QGIS/blob/master/python/plugins/processing/algs/
    qgis/Union.py

    :param union_a: The vector layer for the union.
    :type union_a: QgsVectorLayer

    :param union_b: The vector layer for the union.
    :type union_b: QgsVectorLayer

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

    fields = union_a.fields()
    fields.extend(union_b.fields())

    writer = create_memory_layer(
        output_layer_name,
        union_a.geometryType(),
        union_a.crs(),
        fields
    )
    keywords_union_1 = union_a.keywords
    keywords_union_2 = union_b.keywords
    inasafe_fields_union_1 = keywords_union_1['inasafe_fields']
    inasafe_fields_union_2 = keywords_union_2['inasafe_fields']
    inasafe_fields = inasafe_fields_union_1
    inasafe_fields.update(inasafe_fields_union_2)

    layer_purpose_1 = keywords_union_1['layer_purpose']
    layer_purpose_2 = keywords_union_2['layer_purpose']

    if not (layer_purpose_1 == 'exposure' and
                layer_purpose_2 == 'aggregate_hazard') or \
        not (layer_purpose_1 == 'hazard' and
                     layer_purpose_2 == 'aggregation'):
        raise InvalidKeywordsForProcessingAlgorithm

    writer.keywords = union_a.keywords
    writer.keywords['inasafe_fields'] = inasafe_fields
    writer.keywords['layer_purpose'] = 'aggregate_hazard'

    writer.startEditing()

    # Begin copy/paste from Processing plugin.
    # Please follow their code as their code is optimized.

    index_a = QgsSpatialIndex(union_b.getFeatures())
    index_b = QgsSpatialIndex(union_a.getFeatures())

    count = 0
    n_element = 0
    # Todo fix callback
    # nFeat = len(union_a.getFeatures())
    for in_feat_a in union_a.getFeatures():
        # progress.setPercentage(nElement / float(nFeat) * 50)
        n_element += 1
        list_intersecting_b = []
        geom = in_feat_a.geometry()
        at_map_a = in_feat_a.attributes()
        intersects = index_a.intersects(geom.boundingBox())
        if len(intersects) < 1:
            try:
                _write_feature(at_map_a, geom, writer)
            except:
                # This really shouldn't happen, as we haven't
                # edited the input geom at all
                LOGGER.debug(
                    tr('Feature geometry error: One or more output features '
                       'ignored due to invalid geometry.'))
        else:
            request = QgsFeatureRequest().setFilterFids(intersects)

            engine = QgsGeometry.createGeometryEngine(geom.geometry())
            engine.prepareGeometry()

            for in_feat_b in union_b.getFeatures(request):
                count += 1

                at_map_b = in_feat_b.attributes()
                tmp_geom = in_feat_b.geometry()

                if engine.intersects(tmp_geom.geometry()):
                    int_geom = geom.intersection(tmp_geom)
                    list_intersecting_b.append(QgsGeometry(tmp_geom))

                    if not int_geom:
                        # There was a problem creating the intersection
                        LOGGER.debug(
                            tr('GEOS geoprocessing error: One or more input '
                               'features have invalid geometry.'))
                        int_geom = QgsGeometry()
                    else:
                        int_geom = QgsGeometry(int_geom)

                    if int_geom.wkbType() == QgsWKBTypes.Unknown\
                            or QgsWKBTypes.flatType(
                            int_geom.geometry().wkbType()) == \
                                    QgsWKBTypes.GeometryCollection:
                        # Intersection produced different geomety types
                        temp_list = int_geom.asGeometryCollection()
                        for i in temp_list:
                            if i.type() == geom.type():
                                int_geom = QgsGeometry(i)
                                try:
                                    _write_feature(
                                        at_map_a + at_map_b,
                                        int_geom,
                                        writer)
                                except:
                                    LOGGER.debug(
                                        tr('Feature geometry error: One or '
                                           'more output features ignored due '
                                           'to invalid geometry.'))
                    else:
                        # Geometry list: prevents writing error
                        # in geometries of different types
                        # produced by the intersection
                        # fix #3549
                        if int_geom.wkbType() in wkb_type_groups[
                            wkb_type_groups[int_geom.wkbType()]]:
                            try:
                                _write_feature(
                                    at_map_a + at_map_b, int_geom, writer)
                            except:
                                LOGGER.debug(
                                    tr('Feature geometry error: One or more '
                                       'output features ignored due to '
                                       'invalid geometry.'))

            # the remaining bit of inFeatA's geometry
            # if there is nothing left, this will just silently fail and we
            # are good
            diff_geom = QgsGeometry(geom)
            if len(list_intersecting_b) != 0:
                int_b = QgsGeometry.unaryUnion(list_intersecting_b)
                diff_geom = diff_geom.difference(int_b)
                if diff_geom.isGeosEmpty() or not diff_geom.isGeosValid():
                    LOGGER.debug(
                        tr('GEOS geoprocessing error: One or more input '
                           'features have invalid geometry.'))

            if diff_geom.wkbType() == 0 or QgsWKBTypes.flatType(
                    diff_geom.geometry().wkbType()) == \
                    QgsWKBTypes.GeometryCollection:
                temp_list = diff_geom.asGeometryCollection()
                for i in temp_list:
                    if i.type() == geom.type():
                        diff_geom = QgsGeometry(i)
            try:
                _write_feature(at_map_a, diff_geom, writer)
            except:
                LOGGER.debug(
                    tr('Feature geometry error: One or more output features '
                       'ignored due to invalid geometry.'))

    length = len(union_a.fields())
    at_map_a = [None] * length

    # nFeat = len(union_b.getFeatures())
    for in_feat_a in union_b.getFeatures():
        # progress.setPercentage(nElement / float(nFeat) * 100)
        add = False
        geom = in_feat_a.geometry()
        diff_geom = QgsGeometry(geom)
        atMap = [None] * length
        atMap.extend(in_feat_a.attributes())
        intersects = index_b.intersects(geom.boundingBox())

        if len(intersects) < 1:
            try:
                _write_feature(atMap, geom, writer)
            except:
                LOGGER.debug(
                    tr('Feature geometry error: One or more output features '
                       'ignored due to invalid geometry.'))
        else:
            request = QgsFeatureRequest().setFilterFids(intersects)

            # use prepared geometries for faster intersection tests
            engine = QgsGeometry.createGeometryEngine(diff_geom.geometry())
            engine.prepareGeometry()

            for in_feat_b in union_a.getFeatures(request):
                at_map_b = in_feat_b.attributes()
                tmp_geom = in_feat_b.geometry()

                if engine.intersects(tmp_geom.geometry()):
                    add = True
                    diff_geom = QgsGeometry(diff_geom.difference(tmp_geom))
                    if diff_geom.isGeosEmpty() or not diff_geom.isGeosValid():
                        LOGGER.debug(
                            tr('GEOS geoprocessing error: One or more input '
                               'features have invalid geometry.'))
                else:
                    try:
                        # Ihis only happends if the bounding box
                        # intersects, but the geometry doesn't
                        _write_feature(
                            atMap, diff_geom, writer)
                    except:
                        LOGGER.debug(
                            tr('Feature geometry error: One or more output '
                               'features ignored due to invalid geometry.'))

        if add:
            try:
                _write_feature(atMap, diff_geom, writer)
            except:
                LOGGER.debug(
                    tr('Feature geometry error: One or more output features '
                       'ignored due to invalid geometry.'))
        n_element += 1

    # End of copy/paste from processing

    writer.commitChanges()
    return writer


def _write_feature(attributes, geometry, writer):
    """
    Internal function to write the feature to the output.

    :param attributes: Attributes of the feature.
    :type attributes: list

    :param geometry: The geometry to write to the output.
    :type geometry: QgsGeometry

    :param writer: A vector layer in editing mode.
    :type: QgsVectorLayer
    """
    if writer.geometryType() != geometry.type():
        # We don't write the feature if it's not the same geometry type.
        return

    out_feature = QgsFeature()
    out_feature.setGeometry(geometry)
    out_feature.setAttributes(attributes)
    writer.addFeature(out_feature)
