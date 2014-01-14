
"""**Convert QgsRasterLayer to QgsVectorLayer**
"""

__author__ = 'Dmitry Kolesov <kolesov.dm@gmail.com>'
__revision__ = '$Format:%H$'
__date__ = '14/01/2014'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'



from safe.storage.raster import qgis_imported
if qgis_imported:   # Import QgsRasterLayer if qgis is available
    from PyQt4.QtCore import QVariant
    from qgis.core import (
        QgsRasterLayer,
        QgsField,
        QgsVectorLayer,
        QgsFeature,
        QgsPoint,
        QgsGeometry
    )


def _get_pixel_coords(extent, width, height, row, col):
    """Pixel to coordinates transformation

    :param extent: Geotransformation parameter: extent
    :type extent: QgsRectangle

    :param width:   Geotransformation parameter: horizontal raster size
    :type width:    Int

    :param height:  Geotransformation parameter: vertical raster size
    :type height:   Int

    :param col:  Input x pixel coordinate
    :type col:   Int

    :param row:  Input y pixel coordinate
    :type row:   Int

    :returns:   outx,outy Output coordinates
    :rtype:     (double, double)

    """
    xmin = extent.xMinimum()
    ymax = extent.yMaximum()
    x_res = (extent.xMaximum() - extent.xMinimum())/width
    y_res = (extent.yMaximum() - extent.yMinimum())/height

    outx = xmin + col*x_res
    outy = ymax - row*y_res
    return (outx, outy)

def pixes_to_points(raster,
               threshold_min=0.0,
               threshold_max=float('inf'),
               field_name='value'):
    """
    Convert raster to points. Areas (pixels) with
        threshold_min < pixel_values < threshold_max
    will be converted to point layer.

    :param raster:  Raster layer
    :type raster: QgsRasterLayer

    :param threshold_min: Value that splits raster to
                    flooded or not flooded.
    :type threshold_min: float

    :param threshold_max: Value that splits raster to
                    flooded or not flooded.
    :type threshold_max: float

    :param field_name: Field name to store pixel valued
    :type field_name:  string

    :returns:   Point layer of pixels
    :rtype:     QgsVectorLayer

    """

    if raster.bandCount() != 1:
        msg = "Current version allows using of one-band raster only"
        raise NotImplemented(msg)

    extent = raster.extent()
    width, height = raster.width(), raster.height()
    provider = raster.dataProvider()
    block = provider.block(1, extent, width, height)

    # Create points
    crs = raster.crs().toWkt()
    point_layer = QgsVectorLayer(
        'Point?crs=' + crs, 'pixels', 'memory')

    point_provider = point_layer.dataProvider()
    point_provider.addAttributes([QgsField(field_name, QVariant.Double)])
    field_index = point_provider.fieldNameIndex(field_name)
    attribute_count = 1

    point_layer.startEditing()
    for row in range(height):
        for col in range(width):
            value = block.value(row, col)
            x, y = _get_pixel_coords(extent, width, height, row, col)
            geom = QgsGeometry.fromPoint(QgsPoint(x, y))
            if threshold_min < value < threshold_max:
                feature = QgsFeature()
                feature.initAttributes(attribute_count)
                feature.setAttribute(field_index, value)
                feature.setGeometry(geom)
                _ = point_layer.dataProvider().addFeatures([feature])
    point_layer.commitChanges()

    return point_layer




def polygonize(raster,
               threshold_min=0.0,
               threshold_max=float('inf')):
    """
    Helper to polygonize raster. Areas (pixels) with
        threshold_min < pixel_values < threshold_max
    will be converted to polygons.

    :param raster:  Raster layer
    :type raster: QgsRasterLayer

    :param threshold_min: Value that splits raster to
                    flooded or not flooded.
    :type threshold_min: float

    :param threshold_max: Value that splits raster to
                    flooded or not flooded.
    :type threshold_max: float

    :returns:   Polygon layer of pixels
    :rtype:     QgsVectorLayer

    """
    pass
