# coding=utf-8
"""
InaSAFE Disaster risk assessment tool by AusAid - **Clipper test suite.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from abc import ABCMeta, abstractmethod
from qgis.core import QgsMapLayer, QgsRasterLayer


class DataStore(object):
    """
    DataStore

    .. versionadded:: 4.0
    """

    __metaclass__ = ABCMeta

    def __init__(self, uri):
        """
        Constructor for the DataStore.

        The datastore can be used in three different ways :
        - a PostGIS connection
        - a folder to store a shapefile
        - a geopackage file.

        In a datastore, we should be able to save many layers.

        :param uri: The URI using a QFileInfo, QgsDataSourceURI or the path.
        :type uri: QDir, QFileInfo, QgsDataSourceURI, str

        .. versionadded:: 4.0
        """
        self._uri = uri

    @property
    def uri(self):
        """Return the URI of the datastore. It's not a layer URI.

        :return: The URI.
        :rtype: QgsDataSourceURI, str

        .. versionadded:: 4.0
        """
        return self._uri

    def add_layer(self, layer, layer_name):
        """Add a layer to the datastore.

        :param layer: The layer to add.
        :type layer: QgsMapLayer

        :param layer_name: The name of the layer in the datastore.
        :type layer_name: str

        :returns: A two-tuple. The first element will be True if we could add
            the layer to the datastore. The second element will be the layer
            name which has been used or the error message.
        :rtype: (bool, str)

        .. versionadded:: 4.0
        """
        if isinstance(layer, QgsRasterLayer):
            return self._add_raster_layer(layer, layer_name)
        else:
            return self._add_vector_layer(layer, layer_name)

    @abstractmethod
    def is_writable(self):
        """Check if the URI is writable.

        :return: If it's writable or not.
        :rtype: bool

        .. versionadded:: 4.0
        """
        raise NotImplementedError

    @abstractmethod
    def layers(self):
        """Return a list of layers available.

        :return: List of layers available in the datastore.
        :rtype: list

        .. versionadded:: 4.0
        """
        raise NotImplementedError

    @abstractmethod
    def layer_uri(self, layer_name):
        """Get layer URI.

        :param layer_name: The name of the layer to fetch.
        :type layer_name: str

        :return: The URI of the layer.
        :rtype: QgsDataSourceURI, str

        .. versionadded:: 4.0
        """
        raise NotImplementedError

    @abstractmethod
    def _add_raster_layer(self, raster_layer, layer_name):
        """Add a raster layer to the database.

        :param raster_layer: The layer to add.
        :type raster_layer: QgsVectorLayer

        :param layer_name: The name of the layer in the datastore.
        :type layer_name: str

        :returns: A two-tuple. The first element will be True if we could add
            the layer to the datastore. The second element will be the layer
            name which has been used or the error message.
        :rtype: (bool, str)

        .. versionadded:: 4.0
        """
        raise NotImplementedError

    @abstractmethod
    def _add_vector_layer(self, vector_layer, layer_name):
        """Add a vector layer to the database.

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
        raise NotImplementedError
