
from qgis.core import QgsRasterLayer

from processing.core.Processing import Processing

from safe.common.utilities import unique_filename


def rasterize_vector_layer(layer, attr_name, width, height, extent):
    """Rasterize a vector layer to the grid given by extent and
    width/height of the output raster."""

    output_filename = unique_filename(prefix='rasterized', suffix='.tif')

    extent_str = "%f,%f,%f,%f" % (extent.xMinimum(), extent.xMaximum(),
                                  extent.yMinimum(), extent.yMaximum())
    Processing.runAlgorithm("gdalogr:rasterize", None,
                            layer,
                            attr_name,
                            0,      # output size is given in pixels
                            width,
                            height,
                            extent_str,
                            False,  # force generation of ESRI TFW
                            # advanced options
                            1,      # raster type: Int16
                            '-1',   # nodata value
                            4,      # GeoTIFF compression: DEFLATE
                            75,     # JPEG compression level: 75
                            6,      # DEFLATE compression level
                            1,      # predictor for JPEG/DEFLATE
                            False,  # Tiled GeoTIFF?
                            0,      # whether to make big TIFF
                            '',     # additional creation parameters
                            # output
                            output_filename)

    layer_aligned = QgsRasterLayer(output_filename, "rasterized", "gdal")
    assert layer_aligned.isValid()
    return layer_aligned
