# coding=utf-8

"""Polygonize a raster layer into a vector layer."""


from osgeo import gdal, osr, ogr
from qgis.core import (
    QgsVectorLayer,
    QgsFeatureRequest,
)

from safe.common.utilities import unique_filename, temp_dir
from safe.definitions.constants import no_data_value
from safe.definitions.fields import hazard_value_field, exposure_type_field
from safe.definitions.layer_geometry import (
    layer_geometry, layer_geometry_polygon)
from safe.definitions.processing_steps import polygonize_steps
from safe.gis.sanity_check import check_layer
from safe.utilities.profiling import profile

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def polygonize(layer, callback=None):
    """Polygonize a raster layer into a vector layer using GDAL.

    Issue https://github.com/inasafe/inasafe/issues/3183

    :param layer: The layer to reproject.
    :type layer: QgsRasterLayer

    :param callback: A function to all to indicate progress. The function
        should accept params 'current' (int) and 'maximum' (int). Defaults to
        None.
    :type callback: function

    :return: Reprojected memory layer.
    :rtype: QgsRasterLayer

    .. versionadded:: 4.0
    """
    output_layer_name = polygonize_steps['output_layer_name']
    processing_step = polygonize_steps['step_name']  # NOQA
    output_layer_name = output_layer_name % layer.keywords['layer_purpose']
    gdal_layer_name = polygonize_steps['gdal_layer_name']

    if layer.keywords.get('layer_purpose') == 'exposure':
        output_field = exposure_type_field
    else:
        output_field = hazard_value_field

    input_raster = gdal.Open(layer.source(), gdal.GA_ReadOnly)

    srs = osr.SpatialReference()
    srs.ImportFromWkt(input_raster.GetProjectionRef())

    temporary_dir = temp_dir(sub_dir='pre-process')
    out_shapefile = unique_filename(
        suffix='-%s.shp' % output_layer_name, dir=temporary_dir)

    driver = ogr.GetDriverByName("ESRI Shapefile")
    destination = driver.CreateDataSource(out_shapefile)

    output_layer = destination.CreateLayer(gdal_layer_name, srs)

    # We have no other way to use a shapefile. We need only the first 10 chars.
    field_name = output_field['field_name'][0:10]
    fd = ogr.FieldDefn(field_name, ogr.OFTInteger)
    output_layer.CreateField(fd)

    active_band = layer.keywords.get('active_band', 1)
    input_band = input_raster.GetRasterBand(active_band)
    # Fixme : add our own callback to Polygonize
    gdal.Polygonize(input_band, None, output_layer, 0, [], callback=None)
    destination.Destroy()

    vector_layer = QgsVectorLayer(out_shapefile, output_layer_name, 'ogr')

    # Let's remove polygons which were no data
    request = QgsFeatureRequest()
    expression = '"%s" = %s' % (field_name, no_data_value)
    request.setFilterExpression(expression)
    vector_layer.startEditing()
    for feature in vector_layer.getFeatures(request):
        vector_layer.deleteFeature(feature.id())
    vector_layer.commitChanges()

    # We transfer keywords to the output.
    vector_layer.keywords = layer.keywords.copy()
    vector_layer.keywords[
        layer_geometry['key']] = layer_geometry_polygon['key']

    vector_layer.keywords['title'] = output_layer_name
    # We just polygonized the raster layer. inasafe_fields do not exist.
    vector_layer.keywords['inasafe_fields'] = {
        output_field['key']: field_name
    }

    check_layer(vector_layer)
    return vector_layer
