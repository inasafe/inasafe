# coding=utf-8
"""
Align rasters :
- reproject to the same CRS
- resample to the same cell size and offset in the grid
- clip to a region of interest
"""

from qgis.core import (
    QgsRasterLayer,
    QgsRectangle,
)
from qgis.analysis import QgsAlignRaster


from safe.common.utilities import unique_filename
from safe.common.exceptions import AlignRastersError
from safe.definitions.processing_steps import align_steps
from safe.utilities.profiling import profile
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


@profile
def align_rasters(hazard_layer, exposure_layer, extent):
    """Align hazard and exposure raster layers.

    Align hazard and exposure raster layers so they fit perfectly and so they
    can be used for raster algebra. The method uses QGIS raster alignment tool
    to do the work (which in turn uses GDAL).

    Alignment of layers means that the layers have the same CRS, cell size,
    grid origin and size. That involves clipping and resampling of rasters.
    From the two layers, the layer with finer resolution (smaller cell size)
    will be used as the reference for the alignment (i.e. parameters will
    be set to its CRS, cell size and grid offset).

    :param hazard_layer: Hazard layer to be aligned.
    :type hazard_layer: QgsRasterLayer

    :param exposure_layer: Exposure layer to be aligned.
    :type exposure_layer: QgsRasterLayer

    :param extent: Extent in exposure CRS to which raster should be clipped.
    :type extent: QgsRectangle

    :return: Clipped hazard and exposure layers.
    :rtype: QgsRasterLayer, QgsRasterLayer
    """
    output_layer_name = align_steps['output_layer_name']
    processing_step = align_steps['step_name']

    hazard_output = unique_filename(suffix='.tif')
    exposure_output = unique_filename(suffix='.tif')

    # Setup the two raster layers for alignment
    align = QgsAlignRaster()

    inputs = [
        QgsAlignRaster.Item(hazard_layer.source(), hazard_output),
        QgsAlignRaster.Item(exposure_layer.source(), exposure_output)
    ]

    if exposure_layer.keywords.get('exposure_unit') == 'count':
        inputs[1].rescaleValues = True

    align.setRasters(inputs)

    # Find out which layer has finer grid and use it as the reference.
    # This will setup destination CRS, cell size and grid origin
    if exposure_layer.keywords.get('allow_resampling', True):
        index = align.suggestedReferenceLayer()
    else:
        index = 1  # have to use exposure layer as the reference

    if index < 0:
        raise AlignRastersError(tr('Unable to select reference layer'))

    if not align.setParametersFromRaster(
            inputs[index].inputFilename, exposure_layer.crs().toWkt()):
        raise AlignRastersError(align.errorMessage())

    # Setup clip extent
    align.setClipExtent(extent)

    # Everything configured - do the alignment now!
    # For each raster, it will create output file and write resampled values
    if not align.run():
        raise AlignRastersError(align.errorMessage())

    # Load resulting layers
    aligned_hazard_layer = QgsRasterLayer(
        hazard_output, output_layer_name % 'hazard')
    aligned_exposure_layer = QgsRasterLayer(
        exposure_output, output_layer_name % 'exposure')

    aligned_hazard_layer.keywords = dict(hazard_layer.keywords)
    aligned_hazard_layer.keywords['title'] = output_layer_name % 'hazard'
    aligned_exposure_layer.keywords = dict(exposure_layer.keywords)
    aligned_exposure_layer.keywords['title'] = output_layer_name % 'exposure'

    # avoid any possible further rescaling of exposure data by correctly
    # setting original resolution to be the same as current resolution
    aligned_exposure_layer.keywords['resolution'] = (
        align.cellSize().width(), align.cellSize().height())

    return aligned_hazard_layer, aligned_exposure_layer
