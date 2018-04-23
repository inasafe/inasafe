# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from qgis.PyQt.QtCore import QFileInfo
from osgeo import ogr, osr, gdal
from qgis.core import (
    QgsVectorLayer,
)

from safe.common.exceptions import ErrorDataStore
from safe.datastore.datastore import DataStore
from safe.definitions.gis import QGIS_OGR_GEOMETRY_MAP


class GeoPackage(DataStore):
    """
    GeoPackage DataStore

    .. versionadded:: 4.0
    """

    def __init__(self, uri):
        """
        Constructor for the GeoPackage DataStore.

        :param uri: A filepath which doesn't exist
        :type uri: QFileInfo, str

        .. versionadded:: 4.0
        """
        super(GeoPackage, self).__init__(uri)
        self.vector_driver = ogr.GetDriverByName('GPKG')
        self.raster_driver = gdal.GetDriverByName('GPKG')

        if isinstance(uri, QFileInfo):
            self._uri = uri
        elif isinstance(uri, str):
            self._uri = QFileInfo(uri)
        else:
            raise ErrorDataStore('Unknown type')

        if self.uri.exists():
            raster_datasource = gdal.Open(self.uri.absoluteFilePath())
            if raster_datasource is None:
                # Let's try if it's a vector one.
                vector_datasource = self.vector_driver.Open(
                    self.uri.absoluteFilePath())
                if vector_datasource is None:
                    msg = 'The file is not a geopackage or it doesn\'t ' \
                          'contain any layers.'
                    raise ErrorDataStore(msg)
        else:
            path = self.uri.absoluteFilePath()
            # We need this variable to be created. The delete will create it.
            datasource = self.vector_driver.CreateDataSource(path)  # NOQA
            del datasource

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
        # Fixme, need to check DB permissions ?
        return self._uri.absolutePath().isWritable()

    def supports_rasters(self):
        """Check if we can support raster in the geopackage.

        :return: If it's writable or not.
        :rtype: bool

        .. versionadded:: 4.0
        """
        if int(gdal.VersionInfo('VERSION_NUM')) < 2000000:
            return False
        else:
            return True

    def _vector_layers(self):
        """Return a list of vector layers available.

        :return: List of vector layers available in the geopackage.
        :rtype: list

        .. versionadded:: 4.0
        """
        layers = []
        vector_datasource = self.vector_driver.Open(
            self.uri.absoluteFilePath())
        if vector_datasource:
            for i in range(vector_datasource.GetLayerCount()):
                layers.append(vector_datasource.GetLayer(i).GetName())
        return layers

    def _raster_layers(self):
        """Return a list of raster layers available.

        :return: List of raster layers available in the geopackage.
        :rtype: list

        .. versionadded:: 4.0
        """
        layers = []

        raster_datasource = gdal.Open(self.uri.absoluteFilePath())
        if raster_datasource:
            subdatasets = raster_datasource.GetSubDatasets()
            if len(subdatasets) == 0:
                metadata = raster_datasource.GetMetadata()
                layers.append(metadata['IDENTIFIER'])
            else:
                for subdataset in subdatasets:
                    layers.append(subdataset[0].split(':')[2])

        return layers

    def layers(self):
        """Return a list of layers available.

        :return: List of layers available in the datastore.
        :rtype: list

        .. versionadded:: 4.0
        """
        return self._vector_layers() + self._raster_layers()

    def layer_uri(self, layer_name):
        """Get layer URI.

        For a vector layer :
        /path/to/the/geopackage.gpkg|layername=my_vector_layer

        For a raster :
        GPKG:/path/to/the/geopackage.gpkg:my_raster_layer

        :param layer_name: The name of the layer to fetch.
        :type layer_name: str

        :return: The URI to the layer.
        :rtype: str

        .. versionadded:: 4.0
        """
        for layer in self._vector_layers():
            if layer == layer_name:
                uri = '{}|layername={}'.format(
                    self.uri.absoluteFilePath(), layer_name)
                return uri
        else:
            for layer in self._raster_layers():
                if layer == layer_name:
                    uri = 'GPKG:{}:{}'.format(
                        self.uri.absoluteFilePath(), layer_name)
                    return uri
            else:
                return None

    def _add_vector_layer(self, vector_layer, layer_name):
        """Add a vector layer to the geopackage.

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

        # Fixme
        # if not self.is_writable():
        #    return False, 'The destination is not writable.'

        geometry = QGIS_OGR_GEOMETRY_MAP[vector_layer.wkbType()]

        spatial_reference = osr.SpatialReference()
        qgis_spatial_reference = vector_layer.crs().authid()
        spatial_reference.ImportFromEPSG(
            int(qgis_spatial_reference.split(':')[1]))

        vector_datasource = self.vector_driver.Open(
            self.uri.absoluteFilePath(), True)
        vector_datasource.CreateLayer(layer_name, spatial_reference, geometry)
        uri = '{}|layerid=0'.format(self.uri.absoluteFilePath())
        vector_layer = QgsVectorLayer(uri, layer_name, 'ogr')

        data_provider = vector_layer.dataProvider()
        for feature in vector_layer.getFeatures():
            data_provider.addFeatures([feature])

        return True, layer_name

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

        source = gdal.Open(raster_layer.source())
        array = source.GetRasterBand(1).ReadAsArray()

        x_size = source.RasterXSize
        y_size = source.RasterYSize

        output = self.raster_driver.Create(
            self.uri.absoluteFilePath(),
            x_size,
            y_size,
            1,
            gdal.GDT_Byte,
            ['APPEND_SUBDATASET=YES', 'RASTER_TABLE=%s' % layer_name]
        )

        output.SetGeoTransform(source.GetGeoTransform())
        output.SetProjection(source.GetProjection())
        output.GetRasterBand(1).WriteArray(array)

        # Once we're done, close properly the dataset
        output = None
        source = None
        return True, layer_name

    def _add_tabular_layer(self, tabular_layer, layer_name):
        """Add a tabular layer to the geopackage.

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
        return self._add_vector_layer(tabular_layer, layer_name)
