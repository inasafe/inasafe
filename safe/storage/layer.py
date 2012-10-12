"""**Class Layer**
"""

from safe.common.utilities import verify
from projection import Projection


class Layer:
    """Common class for geospatial layers
    """

    def __init__(self, name=None, projection=None,
                 keywords=None, style_info=None,
                 sublayer=None):
        """Common constructor for all types of layers

        See docstrings for class Raster and class Vector for details.
        """

        # Name
        msg = ('Specified name  must be a string or None. '
               'I got %s with type %s' % (name, str(type(name))[1:-1]))
        verify(isinstance(name, basestring) or name is None, msg)
        self.name = name

        # Projection
        self.projection = Projection(projection)

        # Keywords
        if keywords is None:
            self.keywords = {}
        else:
            msg = ('Specified keywords must be either None or a '
                   'dictionary. I got %s' % keywords)
            verify(isinstance(keywords, dict), msg)
            self.keywords = keywords

        # Style info
        if style_info is None:
            self.style_info = {}
        else:
            msg = ('Specified style_info must be either None or a '
                   'dictionary. I got %s' % style_info)
            verify(isinstance(style_info, dict), msg)
            self.style_info = style_info

        # Defaults
        self.sublayer = sublayer
        self.filename = None
        self.data = None

    def __ne__(self, other):
        """Override '!=' to allow comparison with other projection objecs
        """
        return not self == other

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_filename(self):
        return self.filename

    def get_projection(self, proj4=False):
        """Return projection of this layer as a string
        """
        return self.projection.get_projection(proj4)

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
                raise Exception(msg)

    def get_style_info(self):
        """Return style_info dictionary
        """
        return self.style_info

    def get_impact_summary(self):
        """Return 'impact_summary' keyword if present. Otherwise ''.
        """
        if 'impact_summary' in self.keywords:
            return self.keywords['impact_summary']
        else:
            return ''

    # Layer properties used to identify their types
    @property
    def is_inasafe_spatial_object(self):
        return True

    @property
    def is_raster(self):
        if 'Raster' in str(self.__class__):
            return True
        else:
            return False

    @property
    def is_vector(self):
        if 'Vector' in str(self.__class__):
            return True
        else:
            return False
