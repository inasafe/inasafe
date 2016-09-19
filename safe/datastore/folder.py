# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from os.path import splitext
from os import remove
from PyQt4.QtCore import QFileInfo, QDir
from qgis.core import (
    QgsVectorFileWriter,
    QgsRasterLayer,
    QgsRasterPipe,
    QgsRasterFileWriter
)

from safe.datastore.datastore import DataStore
from safe.common.exceptions import ErrorDataStore, ShapefileCreationError

EXTENSIONS = ('shp', 'asc', 'tiff', 'tif')


class Folder(DataStore):
    """
    Folder DataStore

    A folder based data store is a collection of shape files and tiff images
    stored in a common folder.

    .. versionadded:: 4.0
    """

    def __init__(self, uri):
        """
        Constructor for the folder DataStore.

        :param uri: A directory object or the path to the folder
        :type uri: QDir, str

        .. versionadded:: 4.0
        """
        super(Folder, self).__init__(uri)

        if isinstance(uri, QDir):
            self._uri = uri
        elif isinstance(uri, basestring):
            self._uri = QDir(uri)
        else:
            raise ErrorDataStore('Unknown type')

    def is_writable(self):
        """Check if the folder is writable.

        :return: If it's writable or not.
        :rtype: bool

        .. versionadded:: 4.0
        """
        return QFileInfo(self._uri.absolutePath()).isWritable()

    def supports_rasters(self):
        """Check if we can support raster in the datastore.

        :return: If it's writable or not.
        :rtype: bool

        .. versionadded:: 4.0
        """
        return True

    def layers(self):
        """Return a list of layers available.

        :return: List of layers available in the datastore.
        :rtype: list

        .. versionadded:: 4.0
        """
        extensions = ['*.%s' % f for f in EXTENSIONS]
        self.uri.setNameFilters(extensions)
        files = self.uri.entryList()
        self.uri.setNameFilters('')
        return files

    def layer_uri(self, layer_name):
        """Get layer URI.

        :param layer_name: The name of the layer to fetch.
        :type layer_name: str

        :return: The URI to the layer.
        :rtype: str

        .. versionadded:: 4.0
        """
        for layer in self.layers():
            if layer == layer_name:
                return self.uri.filePath(layer)
        else:
            return None

    def _add_vector_layer(self, vector_layer, layer_name):
        """Add a vector layer to the folder.

        :param vector_layer: The layer to add.
        :type vector_layer: QgsVectorLayer

        :param layer_name: The name of the layer in the datastore.
        :type layer_name: str

        :returns: A two-tuple. The first element will be True if we could add
            the layer to the datastore. The second element will be the layer
            name which has been used or the error message.
        :rtype: (bool, str)

        .. versionadded:: 4.0
        """

        if not self.is_writable():
            return False, 'The destination is not writable.'

        output = QFileInfo(self.uri.filePath(layer_name + '.shp'))
        if output.exists():
            msg = 'The file was already existing : %s' % output.fileName()
            return False, msg

        file_writer = QgsVectorFileWriter(
            output.absoluteFilePath(),
            'utf-8',
            vector_layer.fields(),
            vector_layer.wkbType(),
            vector_layer.crs(),
            'ESRI Shapefile')

        if file_writer.hasError() != QgsVectorFileWriter.NoError:
            raise ShapefileCreationError(file_writer.hasError())

        for feature in vector_layer.getFeatures():
            file_writer.addFeature(feature)

        del file_writer
        return True, output.fileName()

    def _add_raster_layer(self, raster_layer, layer_name):
        """Add a raster layer to the folder.

        :param raster_layer: The layer to add.
        :type raster_layer: QgsRasterLayer

        :param layer_name: The name of the layer in the datastore.
        :type layer_name: str

        :returns: A two-tuple. The first element will be True if we could add
            the layer to the datastore. The second element will be the layer
            name which has been used or the error message.
        :rtype: (bool, str)

        .. versionadded:: 4.0
        """
        if not self.is_writable():
            return False, 'The destination is not writable.'

        output = QFileInfo(self.uri.filePath(layer_name + '.tif'))

        if output.exists():
            msg = 'The file was already existing : %s' % output.fileName()
            return False, msg

        renderer = raster_layer.renderer()
        provider = raster_layer.dataProvider()
        crs = raster_layer.crs()

        pipe = QgsRasterPipe()
        pipe.set(provider.clone())
        pipe.set(renderer.clone())

        file_writer = QgsRasterFileWriter(output.absoluteFilePath())
        file_writer.Mode(1)

        file_writer.writeRaster(
            pipe, provider.xSize(), provider.ySize(), provider.extent(), crs)

        del file_writer
        return True, output.fileName()
