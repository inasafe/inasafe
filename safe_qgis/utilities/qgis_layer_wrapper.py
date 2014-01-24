# coding=utf-8
"""**Layer module**

.. tip:: Provides keywords functionality for QgisMapLayers.
"""

__author__ = 'Dmitry Kolesov <kolesov.dm@gmail.com>'
__revision__ = '$Format:%H$'
__date__ = '01/21/2014'
__license__ = "GPL"
__copyright__ = 'Copyright 2014, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

from safe_qgis.utilities.keyword_io import KeywordIO
from safe_qgis.exceptions import KeywordNotFoundError


class QgisWrapper():
    """Wrapper class to add keywords functionality to Qgis layers
    """
    def __init__(self, layer, name=None):
        """Create the wrapper

        :param layer:       Qgis layer
        :type layer:        QgsMapLayer

        :param name:        A layer's name
        :type name:         Basestring or None
        """

        self.data = layer
        self.keyword_io = KeywordIO()
        self.keywords = self.keyword_io.read_keywords(layer)
        if name is None:
            try:
                self.name = self.get_keywords(key='title')
            except KeywordNotFoundError:
                pass

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_keywords(self, key=None):
        """Return a copy of the keywords dictionary

        Args:
            * key (optional): If specified value will be returned for key only
        """
        if key is None:
            return self.keywords.copy()
        else:
            if key in self.keywords:
                return self.keywords[key]
            else:
                msg = ('Keyword %s does not exist in %s: Options are '
                       '%s' % (key, self.get_name(), self.keywords.keys()))
                raise KeywordNotFoundError(msg)

    def get_layer(self):
        return self.data
