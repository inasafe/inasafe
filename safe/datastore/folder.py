# coding=utf-8

"""Folder datastore implementation."""

from itertools import product

from qgis.PyQt.QtCore import QFileInfo, QDir, QFile
from qgis.core import (
    QgsVectorFileWriter,
    QgsRasterPipe,
    QgsRasterFileWriter
)

from safe.common.exceptions import ErrorDataStore
from safe.datastore.datastore import DataStore
from safe.utilities.utilities import human_sorting

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

VECTOR_EXTENSIONS = ('shp', 'kml', 'geojson')
RASTER_EXTENSIONS = ('asc', 'tiff', 'tif')
TABULAR_EXTENSIONS = ('csv',)
EXTENSIONS = RASTER_EXTENSIONS + VECTOR_EXTENSIONS + TABULAR_EXTENSIONS


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
        self._default_vector_format = 'shp'

        if isinstance(uri, QDir):
            self._uri = uri
        elif isinstance(uri, str):
            self._uri = QDir(uri)
        else:
            raise ErrorDataStore('Unknown type')

    @property
    def default_vector_format(self):
        """Default vector format for the folder datastore.

        :return: The default vector format.
        :rtype: str.
        """
        return self._default_vector_format

    @default_vector_format.setter
    def default_vector_format(self, default_format):
        """Set the default vector format for the folder datastore.

        :param default_format: The default output format.
            It can be 'shp', 'geojson' or 'kml'.
        :param default_format: str
        """
        if default_format in VECTOR_EXTENSIONS:
            self._default_vector_format = default_format

    @property
    def uri_path(self):
        """Return the URI of the datastore as a path. It's not a layer URI.

        :return: The URI.
        :rtype: str

        .. versionadded:: 4.0
        """
        return self.uri.absolutePath()

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
        files = human_sorting([QFileInfo(f).baseName() for f in files])
        return files

    def layer_uri(self, layer_name):
        """Get layer URI.

        :param layer_name: The name of the layer to fetch.
        :type layer_name: str

        :return: The URI to the layer.
        :rtype: str

        .. versionadded:: 4.0
        """
        layers = self.layers()
        for layer, extension in product(layers, EXTENSIONS):
            one_file = QFileInfo(
                self.uri.filePath(layer + '.' + extension))
            if one_file.exists():
                if one_file.baseName() == layer_name:
                    return one_file.absoluteFilePath()
        else:
            return None

    def _add_tabular_layer(self, tabular_layer, layer_name):
        """Add a tabular layer to the folder.

        :param tabular_layer: The layer to add.
        :type tabular_layer: QgsVectorLayer

        :param layer_name: The name of the layer in the datastore.
        :type layer_name: str

        :returns: A two-tuple. The first element will be True if we could add
            the layer to the datastore. The second element will be the layer
            name which has been used or the error message.
        :rtype: (bool, str)

        .. versionadded:: 4.0
        """
        output = QFileInfo(
            self.uri.filePath(layer_name + '.csv'))

        QgsVectorFileWriter.writeAsVectorFormat(
            tabular_layer,
            output.absoluteFilePath(),
            'utf-8',
            None,
            'CSV')

        assert output.exists()
        return True, output.baseName()

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

        output = QFileInfo(
            self.uri.filePath(layer_name + '.' + self._default_vector_format))

        driver_mapping = {
            'shp': 'ESRI Shapefile',
            'kml': 'KML',
            'geojson': 'GeoJSON',
        }

        QgsVectorFileWriter.writeAsVectorFormat(
            vector_layer,
            output.absoluteFilePath(),
            'utf-8',
            vector_layer.crs(),
            driver_mapping[self._default_vector_format])

        assert output.exists()
        return True, output.baseName()

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

        source = QFileInfo(raster_layer.source())
        if source.exists() and source.suffix() in ['tiff', 'tif']:
            # If it's tiff file based.
            QFile.copy(source.absoluteFilePath(), output.absoluteFilePath())

        else:
            # If it's not file based.
            renderer = raster_layer.renderer()
            provider = raster_layer.dataProvider()
            crs = raster_layer.crs()

            pipe = QgsRasterPipe()
            pipe.set(provider.clone())
            pipe.set(renderer.clone())

            file_writer = QgsRasterFileWriter(output.absoluteFilePath())
            file_writer.Mode(1)

            file_writer.writeRaster(
                pipe,
                provider.xSize(),
                provider.ySize(),
                provider.extent(),
                crs)

            del file_writer

        assert output.exists()
        return True, output.baseName()
