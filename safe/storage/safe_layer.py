# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Impact Function Base Class**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

__author__ = 'imajimatika@gmail.com'
__revision__ = '$Format:%H$'
__filename = 'safe_layer'
__date__ = '7/14/15'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

from qgis.core import QgsVectorLayer, QgsMapLayer
from safe.storage.layer import Layer
from safe.storage.vector import Vector
from safe.common.exceptions import KeywordNotFoundError, InvalidLayerError
from safe.utilities.keyword_io import KeywordIO


class SafeLayer(object):
    """Wrapper for QgsMapLayer and safe.storage.layer.
    """

    def __init__(self, layer, name=None):
        """Init function.
        :param layer: A layer. Can be QgsMapLayer or safe.storage.layer.
        :type layer: QgsMapLayer, Layer

        :param name: A layer's name
        :type name: Basestring or None
        """
        # Merely initialization
        self._layer = None
        self._keywords = {}
        self.layer = layer

        if name:
            self._name = name
        else:
            try:
                # RM: convert title to string. Makes sure it is str
                self._name = unicode(self.keyword('title'))
            except KeywordNotFoundError:
                self._name = ''

    @property
    def layer(self):
        """Property for the actual layer.
        :returns: A map layer.
        :rtype: QgsMapLayer, Layer
        """
        return self._layer

    @layer.setter
    def layer(self, layer):
        """Setter for layer property.

        :param layer: The actual layer.
        :type layer: QgsMapLayer, Layer
        """
        if isinstance(layer, QgsMapLayer) or isinstance(layer, Layer):
            self._layer = layer
        else:
            message = (
                'SafeLayer only accept QgsMapLayer or '
                'safe.storage.layer.Layer.')
            raise InvalidLayerError(message)
        if isinstance(layer, Layer):
            self.keywords = layer.keywords
        elif isinstance(layer, QgsMapLayer):
            keyword_io = KeywordIO()
            self.keywords = keyword_io.read_keywords(layer)
        else:
            self.keywords = {}

    @property
    def keywords(self):
        """Property for the layer's keywords.
        :returns: A keywords.
        :rtype: dict
        """
        return self._keywords

    @keywords.setter
    def keywords(self, keywords):
        """Setter for keywords property.

        :param keywords: The actual layer.
        :type keywords: QgsMapLayer, Layer
        """
        self._keywords = keywords

    def keyword(self, key):
        """Return value of key from keywords.

        It will raise KeywordNotFoundError if the key is not found.

        :param key: The key of a keyword.
        :type key: str

        :returns: The value of the key in keywords dictionary.
        :rtype: str, dict, int, float
        """
        try:
            return self.keywords[key]
        except KeyError as e:
            raise KeywordNotFoundError(e)

    @property
    def name(self):
        """Property for the actual layer.

        :returns: A layer's name.
        :rtype: basestring
        """
        return self._name

    @name.setter
    def name(self, layer_name):
        """Setter for name property.

        :param layer_name: The actual layer.
        :type layer_name: str
        """
        self._name = layer_name

    def is_qgsvectorlayer(self):
        """Return true if self.layer is a QgsVectorLayer.

        :returns: Boolean.
        :rtype: bool
        """
        return isinstance(self.layer, QgsVectorLayer)

    def qgis_vector_layer(self):
        """Get QgsVectorLayer representation of self.layer.

        :returns: A QgsVectorLayer if it's vector.
        :rtype: QgsVectorLayer, None
        """
        if isinstance(self.layer, Vector):
            return self.layer.as_qgis_native()
        elif isinstance(self.layer, QgsVectorLayer):
            return self.layer
        else:
            return None
