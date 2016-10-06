# coding=utf-8
"""
Polygonize a raster layer into a vector layer.

Issue https://github.com/inasafe/inasafe/issues/3183
"""


from osgeo import gdal, osr, ogr

from qgis.core import (
    QgsRasterLayer,
    QgsVectorLayer,
)

from safe.common.utilities import unique_filename, temp_dir
from safe.definitionsv4.fields import hazard_class_field
from safe.definitionsv4.layer_geometry import (
    layer_geometry, layer_geometry_polygon)
from safe.definitionsv4.processing import polygonize_raster

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def polygonize(layer, callback=None):
    """
    Polygonize a raster layer into a vector layer using GDAL.

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
    output_layer_name = polygonize_raster['output_layer_name']
    processing_step = polygonize_raster['step_name']

    input_raster = gdal.Open(layer.source(), gdal.GA_ReadOnly)

    srs = osr.SpatialReference()
    srs.ImportFromWkt(input_raster.GetProjectionRef())

    temporary_dir = temp_dir(sub_dir='pre-process')
    out_shapefile = unique_filename(
        suffix='-%s.shp' % output_layer_name, dir=temporary_dir)

    driver = ogr.GetDriverByName("ESRI Shapefile")
    destination = driver.CreateDataSource(out_shapefile)

    output_layer = destination.CreateLayer(output_layer_name, srs)

    fd = ogr.FieldDefn(hazard_class_field['field_name'], ogr.OFTInteger)
    output_layer.CreateField(fd)

    input_band = input_raster.GetRasterBand(1)
    # Fixme : add our own callback to Polygonize
    gdal.Polygonize(input_band, None, output_layer, 0, [], callback=None)
    destination.Destroy()

    vector_layer = QgsVectorLayer(out_shapefile, output_layer_name, 'ogr')

    # We transfer keywords to the output.
    vector_layer.keywords = layer.keywords
    vector_layer.keywords[
        layer_geometry['key']] = layer_geometry_polygon['key']

    inasafe_field = hazard_class_field['key']
    field_name = hazard_class_field['field_name']
    vector_layer.keywords['inasafe_fields'][inasafe_field] = field_name

    return vector_layer
