"""
Disaster risk assessment tool developed by AusAid -
  **RiabClipper implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '20/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

from qgis.core import (QgsCoordinateTransform, QgsCoordinateReferenceSystem,
                       QgsRectangle, QgsMapLayer, QgsFeature,
                       QgsVectorFileWriter)
from PyQt4 import QtCore
from riabexceptions import InvalidParameterException


def clipLayer(layer, extent):
    """Clip a Hazard or Exposure layer to the
    extents of the current view frame.

    Args:

        * theLayer - a valid QGIS vector or raster layer
        * theExtent - a valid QgsRectangle defining the
                      clip extent in EPSG:4326

    Returns:
        Path to the output clipped layer (placed in the
        system temp dir).

    Raises:
       None

    """

    myFilename = '/tmp/test.shp'  # Tempory file to write to
    if not layer or not extent:
        msg = 'Layer or Extent passed to clip is None.'
        raise InvalidParameterException(msg)
    myDestinationCrs = QgsCoordinateReferenceSystem()
    myDestinationCrs.createFromEpsg(4326)
    myXForm = QgsCoordinateTransform(
        layer.crs(), myDestinationCrs)

    # Get the clip area in the layers crs
    myProjectedExtent = myXForm.transformBoundingBox(extent)
    if layer.type() == QgsMapLayer.RasterLayer:
        msg = 'Clipping not implemented for rasters yet'
        raise Exception(msg)
    else:
        # Vector layer
        myProvider = layer.dataProvider()
        if myProvider is None:
            msg = ('Could not obtain data provider from '
                   'layer "%s"' % layer.source())
            raise Exception(msg)

        myAttributes = myProvider.attributeIndexes()
        myProvider.select(myAttributes,
                          myProjectedExtent, True, True)
        myFieldList = myProvider.fields()
        myWriter = QgsVectorFileWriter(
                myFilename,
                'UTF-8',
                myFieldList,
                layer.wkbType(),
                myDestinationCrs,
                'ESRI Shapefile')
        if myWriter.hasError() != QgsVectorFileWriter.NoError:
            msg = 'Error when creating shapefile: ', myWriter.hasError()
            raise Exception(msg)

        # Retreive every feature with its geometry and attributes
        myFeature = QgsFeature()
        while myProvider.nextFeature(myFeature):
            myWriter.addFeature(myFeature)
        del myWriter  # Flush to disk
    return myFilename  # Filename of created file
