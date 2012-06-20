"""Class Layer
"""

from common.utilities import verify
from projection import Projection

class Layer:
    """Common class for geospatial layers
    """

    def __init__(self, name='', projection=None, keywords=None, style_info=None):
        """Common constructor for all types of layers

        See docstrings for class Raster and class Vector for details.
        """

        # Name
        msg = ('Specified name  must be a string. '
               'I got %s with type %s' % (name, str(type(name))[1:-1]))
        verify(isinstance(name, basestring), msg)
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
        self.filename = None
