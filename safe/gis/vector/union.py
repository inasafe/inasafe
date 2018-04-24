# coding=utf-8

"""Clip and mask a hazard layer."""

import logging

from qgis.core import (
    QgsGeometry,
    QgsFeatureRequest,
    QgsWkbTypes,
    QgsFeature,
)

from safe.definitions.fields import hazard_class_field, aggregation_id_field
from safe.definitions.hazard_classifications import not_exposed_class
from safe.definitions.processing_steps import union_steps
from safe.gis.sanity_check import check_layer
from safe.gis.vector.clean_geometry import geometry_checker
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
def union(union_a, union_b):
    """Union of two vector layers.

    Issue https://github.com/inasafe/inasafe/issues/3186

    Note : This algorithm is copied from :
    https://github.com/qgis/QGIS/blob/master/python/plugins/processing/algs/
    qgis/Union.py

    :param union_a: The vector layer for the union.
    :type union_a: QgsVectorLayer

    :param union_b: The vector layer for the union.
    :type union_b: QgsVectorLayer

    :return: The clip vector layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    output_layer_name = union_steps['output_layer_name']
    output_layer_name = output_layer_name % (
        union_a.keywords['layer_purpose'],
        union_b.keywords['layer_purpose']
    )

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

    # use to avoid modifying original source
    writer.keywords = dict(union_a.keywords)
    writer.keywords['inasafe_fields'] = inasafe_fields
    writer.keywords['title'] = output_layer_name
    writer.keywords['layer_purpose'] = 'aggregate_hazard'
    writer.keywords['hazard_keywords'] = keywords_union_1.copy()
    writer.keywords['aggregation_keywords'] = keywords_union_2.copy()
    skip_field = inasafe_fields_union_2[aggregation_id_field['key']]
    not_null_field_index = writer.fieldNameIndex(skip_field)

    writer.startEditing()

    # Begin copy/paste from Processing plugin.
    # Please follow their code as their code is optimized.
    # The code below is not following our coding standards because we want to
    # be able to track any diffs from QGIS easily.

    index_a = create_spatial_index(union_b)
    index_b = create_spatial_index(union_a)

    count = 0
    n_element = 0
    # Todo fix callback
    # nFeat = len(union_a.getFeatures())
    for in_feat_a in union_a.getFeatures():
        # progress.setPercentage(nElement / float(nFeat) * 50)
        n_element += 1
        list_intersecting_b = []
        geom = geometry_checker(in_feat_a.geometry())
        at_map_a = in_feat_a.attributes()
        intersects = index_a.intersects(geom.boundingBox())
        if len(intersects) < 1:
            try:
                _write_feature(at_map_a, geom, writer, not_null_field_index)
            except BaseException:
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
                tmp_geom = geometry_checker(in_feat_b.geometry())

                if engine.intersects(tmp_geom.geometry()):
                    int_geom = geometry_checker(geom.intersection(tmp_geom))
                    list_intersecting_b.append(QgsGeometry(tmp_geom))

                    if not int_geom:
                        # There was a problem creating the intersection
                        # LOGGER.debug(
                        #     tr('GEOS geoprocessing error: One or more input '
                        #        'features have invalid geometry.'))
                        pass
                        int_geom = QgsGeometry()
                    else:
                        int_geom = QgsGeometry(int_geom)

                    if int_geom.wkbType() == QgsWkbTypes.Unknown\
                            or QgsWkbTypes.flatType(
                            int_geom.geometry().wkbType()) == \
                            QgsWkbTypes.GeometryCollection:
                        # Intersection produced different geometry types
                        temp_list = int_geom.asGeometryCollection()
                        for i in temp_list:
                            if i.type() == geom.type():
                                int_geom = QgsGeometry(geometry_checker(i))
                                try:
                                    _write_feature(
                                        at_map_a + at_map_b,
                                        int_geom,
                                        writer,
                                        not_null_field_index,
                                    )
                                except BaseException:
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
                                    at_map_a + at_map_b,
                                    int_geom,
                                    writer,
                                    not_null_field_index)
                            except BaseException:
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
                diff_geom = geometry_checker(diff_geom.difference(int_b))
                if diff_geom is None or \
                        diff_geom.isGeosEmpty() or not diff_geom.isGeosValid():
                    # LOGGER.debug(
                    #     tr('GEOS geoprocessing error: One or more input '
                    #        'features have invalid geometry.'))
                    pass

            if diff_geom is not None and (
                diff_geom.wkbType() == 0 or QgsWkbTypes.flatType(
                    diff_geom.geometry().wkbType()) ==
                    QgsWkbTypes.GeometryCollection):
                temp_list = diff_geom.asGeometryCollection()
                for i in temp_list:
                    if i.type() == geom.type():
                        diff_geom = QgsGeometry(geometry_checker(i))
            try:
                _write_feature(
                    at_map_a,
                    diff_geom,
                    writer,
                    not_null_field_index)
            except BaseException:
                LOGGER.debug(
                    tr('Feature geometry error: One or more output features '
                       'ignored due to invalid geometry.'))

    length = len(union_a.fields())

    # nFeat = len(union_b.getFeatures())
    for in_feat_a in union_b.getFeatures():
        # progress.setPercentage(nElement / float(nFeat) * 100)
        geom = geometry_checker(in_feat_a.geometry())
        atMap = [None] * length
        atMap.extend(in_feat_a.attributes())
        intersects = index_b.intersects(geom.boundingBox())
        lstIntersectingA = []

        for id in intersects:
            request = QgsFeatureRequest().setFilterFid(id)
            inFeatB = next(union_a.getFeatures(request))
            tmpGeom = QgsGeometry(geometry_checker(inFeatB.geometry()))

            if geom.intersects(tmpGeom):
                lstIntersectingA.append(tmpGeom)

        if len(lstIntersectingA) == 0:
            res_geom = geom
        else:
            intA = QgsGeometry.unaryUnion(lstIntersectingA)
            res_geom = geom.difference(intA)
            if res_geom is None:
                # LOGGER.debug(
                #    tr('GEOS geoprocessing error: One or more input features '
                #        'have null geometry.'))
                pass
                continue  # maybe it is better to fail like @gustry
                # does below ....
            if res_geom.isGeosEmpty() or not res_geom.isGeosValid():
                # LOGGER.debug(
                #    tr('GEOS geoprocessing error: One or more input features '
                #        'have invalid geometry.'))
                pass

        try:
            _write_feature(atMap, res_geom, writer, not_null_field_index)
        except BaseException:
            # LOGGER.debug(
            #     tr('Feature geometry error: One or more output features '
            #        'ignored due to invalid geometry.'))
            pass

        n_element += 1

    # End of copy/paste from processing

    writer.commitChanges()

    fill_hazard_class(writer)

    check_layer(writer)
    return writer


def _write_feature(attributes, geometry, writer, not_null_field_index):
    """
    Internal function to write the feature to the output.

    :param attributes: Attributes of the feature.
    :type attributes: list

    :param geometry: The geometry to write to the output.
    :type geometry: QgsGeometry

    :param writer: A vector layer in editing mode.
    :type: QgsVectorLayer

    :param not_null_field_index: The index in the attribute table which should
        not be null.
    :type not_null_field_index: int
    """
    if writer.geometryType() != geometry.type():
        # We don't write the feature if it's not the same geometry type.
        return

    compulsary_field = attributes[not_null_field_index]
    if not compulsary_field:
        # We don't want feature without a compulsary field.
        # I think this a bug from the union algorithm.
        return

    out_feature = QgsFeature()
    out_feature.setGeometry(geometry)
    out_feature.setAttributes(attributes)
    writer.addFeature(out_feature)


@profile
def fill_hazard_class(layer):
    """We need to fill hazard class when it's empty.

    :param layer: The vector layer.
    :type layer: QgsVectorLayer

    :return: The updated vector layer.
    :rtype: QgsVectorLayer

    .. versionadded:: 4.0
    """
    hazard_field = layer.keywords['inasafe_fields'][hazard_class_field['key']]

    expression = '"%s" is NULL OR  "%s" = \'\'' % (hazard_field, hazard_field)
    index = layer.fieldNameIndex(hazard_field)
    request = QgsFeatureRequest().setFilterExpression(expression)
    layer.startEditing()

    for feature in layer.getFeatures(request):
        layer.changeAttributeValue(
            feature.id(),
            index,
            not_exposed_class['key'])
    layer.commitChanges()

    return layer
