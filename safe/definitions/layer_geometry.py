# coding=utf-8

"""Definitions relating to layer geometry (point/line/poly/raster).
"""

from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

layer_geometry_point = {
    'key': 'point',
    'name': tr('Point'),
    'description': tr(
        'A layer composed of points which each represent a feature on the '
        'earth. Currently the only point data supported by InaSAFE are '
        '<b>volcano hazard</b> layers and building points.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_geometry_line = {
    'key': 'line',
    'name': tr('Line'),
    'description': tr(
        'A layer composed of linear features. Currently only <b>road exposure'
        '</b> line layers are supported by InaSAFE.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_geometry_polygon = {
    'key': 'polygon',
    'name': tr('Polygon'),
    'description': tr(
        'A layer composed of polygon features that represent areas of hazard '
        'or exposure. For example areas of flood represented as polygons '
        '(for a hazard) or building footprints represented as polygons '
        '(for an exposure). The polygon layer will often need the presence '
        'of specific layer attributes too - these will vary depending on '
        'whether the layer represents a hazard, exposure or aggregation layer '
        '. Polygon layers can also be used for aggregation - where impact '
        'analysis results per boundary such as village or district '
        'boundaries.'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
layer_geometry_raster = {
    'key': 'raster',
    'name': tr('Raster'),
    'description': tr(
        'A raster data layer consists of a matrix of cells organised into '
        'rows and columns. The value in the cells represents information such '
        'as a flood depth value or a hazard class. '),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
layer_geometry = {
    'key': 'layer_geometry',
    'name': tr('Geometry'),
    'description': tr(
        'Layer geometry can be either raster or vector. There are three '
        'possible vector geometries: point, line, and polygon. '),
    'types': [
        layer_geometry_raster,
        layer_geometry_point,
        layer_geometry_line,
        layer_geometry_polygon
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
