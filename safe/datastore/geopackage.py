# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from osgeo import ogr, osr
from PyQt4.QtCore import QFileInfo
from qgis.core import (
    QgsVectorLayer,
    QgsRasterLayer,
)

from safe.gis.gdal_ogr_tools import QGIS_OGR_GEOMETRY_MAP
from safe.datastore.datastore import DataStore
from safe.common.exceptions import ErrorDataStore


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
        self.driver = ogr.GetDriverByName('GPKG')

        if isinstance(uri, QFileInfo):
            self._uri = uri
        elif isinstance(uri, basestring):
            self._uri = QFileInfo(uri)
        else:
            raise ErrorDataStore('Unknown type')

        if self.uri.exists():
            raise ErrorDataStore('A file exists already')
        else:
            path = self.uri.absoluteFilePath()
            self.datasource = self.driver.CreateDataSource(path)

    def is_writable(self):
        """Check if the folder is writable.

        :return: If it's writable or not.
        :rtype: bool

        .. versionadded:: 4.0
        """
        # Fixme, need to check DB permissions ?
        return self._uri.absolutePath().isWritable()

    def is_raster_supported(self):
        """Check if we can support raster in the datastore.

        :return: If it's writable or not.
        :rtype: bool

        .. versionadded:: 4.0
        """
        # Fixme need to check GDAL version
        return False

    def layers(self):
        """Return a list of layers available.

        :return: List of layers available in the datastore.
        :rtype: list

        .. versionadded:: 4.0
        """
        layers = []
        for i in range(self.datasource.GetLayerCount()):
            layers.append(self.datasource.GetLayer(i).GetName())
        return layers

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
                uri = u'{}|layername={}'.format(
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

        geom = QGIS_OGR_GEOMETRY_MAP[vector_layer.wkbType()]

        srs = osr.SpatialReference()
        qgis_crs = vector_layer.crs().authid()
        srs.ImportFromEPSG(int(qgis_crs.split(':')[1]))

        self.datasource.CreateLayer(layer_name, srs, geom)
        uri = u'{}|layerid=0'.format(self.uri.absoluteFilePath())
        vl = QgsVectorLayer(uri, layer_name, u'ogr')

        data_provider = vl.dataProvider()
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
        # fixme
        # if not self.is_writable():
        #    return False, 'The destination is not writable.'

        raise NotImplementedError
