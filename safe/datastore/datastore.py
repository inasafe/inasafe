# coding=utf-8

"""Datastore implementation."""
from builtins import object

import logging
from abc import ABCMeta, abstractmethod

from qgis.core import QgsRasterLayer, QgsVectorLayer, QGis

from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.utilities import monkey_patch_keywords
from future.utils import with_metaclass

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


class DataStore(with_metaclass(ABCMeta, object)):

    """DataStore.

    .. versionadded:: 4.0
    """

    def __init__(self, uri):
        """Constructor for the DataStore.

        The datastore can be used in three different ways :
        - a PostGIS connection
        - a folder to store a shapefile
        - a geopackage file.

        We may add more datastores in the future.

        In a datastore, we should be able to save many layers.

        :param uri: The URI using a QFileInfo, QgsDataSourceURI or the path.
        :type uri: QDir, QFileInfo, QgsDataSourceURI, str

        .. versionadded:: 4.0
        """
        self._uri = uri
        self._index = 1
        self._use_index = False

    @property
    def use_index(self):
        """Return if we use an index to add the layer name.

        :return: If we use an index.
        :rtype: bool
        """
        return self._use_index

    @use_index.setter
    def use_index(self, index):
        """Setter if we use an index when we add a layer to the datastore.

        :param index: A boolean if we use an index.
        :type index: bool
        """
        self._use_index = index

    @property
    def uri(self):
        """Return the URI of the datastore. It's not a layer URI.

        :return: The URI.
        :rtype: QgsDataSourceURI, str

        .. versionadded:: 4.0
        """
        return self._uri

    @property
    def uri_path(self):
        """Return the URI of the datastore as a path. It's not a layer URI.

        :return: The URI.
        :rtype: str

        .. versionadded:: 4.0
        """
        raise NotImplementedError

    def add_layer(self, layer, layer_name, save_style=False):
        """Add a layer to the datastore.

        :param layer: The layer to add.
        :type layer: QgsMapLayer

        :param layer_name: The name of the layer in the datastore.
        :type layer_name: str

        :param save_style: If we have to save a QML too. Default to False.
        :type save_style: bool

        :returns: A two-tuple. The first element will be True if we could add
            the layer to the datastore. The second element will be the layer
            name which has been used or the error message.
        :rtype: (bool, str)

        .. versionadded:: 4.0
        """
        if self._use_index:
            layer_name = '%s-%s' % (self._index, layer_name)
            self._index += 1

        if self.layer_uri(layer_name):
            return False, tr('The layer already exists in the datastore.')

        if isinstance(layer, QgsRasterLayer):
            result = self._add_raster_layer(layer, layer_name, save_style)
        else:
            if layer.wkbType() == QGis.WKBNoGeometry:
                result = self._add_tabular_layer(layer, layer_name, save_style)
            else:
                result = self._add_vector_layer(layer, layer_name, save_style)

        if result[0]:
            LOGGER.info(
                u'Layer saved {layer_name}'.format(layer_name=result[1]))

        try:
            layer.keywords
            real_layer = self.layer(result[1])
            if isinstance(real_layer, bool):
                message = ('{name} was not found in the datastore or the '
                           'layer was not valid.'.format(name=result[1]))
                LOGGER.debug(message)
                return False, message
            KeywordIO().write_keywords(real_layer, layer.keywords)
        except AttributeError:
            pass

        return result

    def layer(self, layer_name):
        """Get QGIS layer.

        :param layer_name: The name of the layer to fetch.
        :type layer_name: str

        :return: The QGIS layer.
        :rtype: QgsMapLayer

        .. versionadded:: 4.0
        """
        uri = self.layer_uri(layer_name)
        layer = QgsVectorLayer(uri, layer_name, 'ogr')
        if not layer.isValid():
            layer = QgsRasterLayer(uri, layer_name)
            if not layer.isValid():
                return False

        monkey_patch_keywords(layer)

        return layer

    @abstractmethod
    def is_writable(self):
        """Check if the URI is writable.

        :return: If it's writable or not.
        :rtype: bool

        .. versionadded:: 4.0
        """
        raise NotImplementedError

    @abstractmethod
    def supports_rasters(self):
        """Check if we can support raster in the datastore.

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

    def layer_keyword(self, keyword, value):
        """Get a layer according to a keyword and its value.

        :param keyword: The keyword to check.
        :type keyword: basestring

        :param value: The value to check for the specific keyword.
        :type value: basestring

        :return: The QGIS layer.
        :rtype: QgsMapLayer

        .. versionadded:: 4.0
        """
        for layer in sorted(self.layers(), reverse=True):
            qgis_layer = self.layer(layer)
            if qgis_layer.keywords.get(keyword) == value:
                return qgis_layer
        return None

    @abstractmethod
    def _add_raster_layer(self, raster_layer, layer_name, save_style=False):
        """Add a raster layer to the database.

        :param raster_layer: The layer to add.
        :type raster_layer: QgsRasterLayer

        :param layer_name: The name of the layer in the datastore.
        :type layer_name: str

        :param save_style: If we have to save a QML too. Default to False.
        :type save_style: bool

        :returns: A two-tuple. The first element will be True if we could add
            the layer to the datastore. The second element will be the layer
            name which has been used or the error message.
        :rtype: (bool, str)

        .. versionadded:: 4.0
        """
        raise NotImplementedError

    @abstractmethod
    def _add_vector_layer(self, vector_layer, layer_name, save_style=False):
        """Add a vector layer to the database.

        :param vector_layer: The layer to add.
        :type vector_layer: QgsVectorLayer

        :param layer_name: The name of the layer in the datastore.
        :type layer_name: str

        :param save_style: If we have to save a QML too. Default to False.
        :type save_style: bool

        :returns: A two-tuple. The first element will be True if we could add
            the layer to the datastore. The second element will be the layer
            name which has been used or the error message.
        :rtype: (bool, str)

        .. versionadded:: 4.0
        """
        raise NotImplementedError

    @abstractmethod
    def _add_tabular_layer(self, tabular_layer, layer_name, save_style=False):
        """Add a vector layer to the database.

        :param tabular_layer: The layer to add.
        :type tabular_layer: QgsVectorLayer

        :param layer_name: The name of the layer in the datastore.
        :type layer_name: str

        :param save_style: If we have to save a QML too. Default to False.
        :type save_style: bool

        :returns: A two-tuple. The first element will be True if we could add
            the layer to the datastore. The second element will be the layer
            name which has been used or the error message.
        :rtype: (bool, str)

        .. versionadded:: 4.0
        """
        raise NotImplementedError
