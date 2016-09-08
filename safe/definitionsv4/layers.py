# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid / DFAT -
**New Metadata for SAFE.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""
from safe.utilities.i18n import tr
from safe.definitionsv4.concepts import concepts

# Layer Purpose
layer_purpose_hazard = {
    'key': 'hazard',
    'name': tr('Hazard'),
    'description': concepts['hazard']['description'],
    'citations': concepts['hazard']['citations']
}

layer_purpose_exposure = {
    'key': 'exposure',
    'name': tr('Exposure'),
    'description': concepts['exposure']['description'],
    'citations': concepts['exposure']['citations'],
}

layer_purpose_aggregation = {
    'key': 'aggregation',
    'name': tr('Aggregation'),
    'description': tr(
        'An <b>aggregation</b> layer represents regions that can be used to '
        'summarise impact analysis results. For example, we might summarise '
        'the affected people after a flood according to administration '
        'boundaries.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_purpose = {
    'key': 'layer_purpose',
    'name': tr('Purpose'),
    'description': tr(
        'The purpose of the layer can be hazard layer, exposure layer, or '
        'aggregation layer'),
    'types': [
        layer_purpose_hazard,
        layer_purpose_exposure,
        layer_purpose_aggregation
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

# Layer mode
layer_mode_continuous = {
    'key': 'continuous',
    'name': tr('Continuous'),
    'description': tr(
        '<b>Continuous</b> data can be used in raster hazard or exposure data '
        'where the values in the data are either integers or decimal '
        'values representing a continuously varying phenomenon. '
        'For example flood depth is a continuous value from 0 to the maximum '
        'reported depth during a flood. '
        '<p>Raster exposure data such as population data are also continuous. '
        'In this example the cell values represent the number of people in '
        'cell.</p>'
        '<p>Raster data is considered to be continuous by default and you '
        'should explicitly indicate that it is classified if each cell in the '
        'raster represents a discrete class (e.g. low depth = 1, medium depth '
        '= 2, high depth = 3).</p>'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
}

layer_mode_classified = {
    'key': 'classified',
    'name': tr('Classified'),
    'description': tr(
        '<b>Classified</b> data can be used for either hazard or exposure '
        'data and can be used for both raster and vector layer types where '
        'the attribute values represent a classified or coded value.'
        '<p>For example, classified values in a flood raster data set might '
        'represent discrete classes where a value of 1 might represent the '
        'low inundation class, a value of 2 might represent the medium '
        'inundation class and a value of 3 might represent the '
        'high inundation class.</p>'
        '<p>Classified values in a vector (polygon) Volcano data set might '
        'represent discrete classes where a value of I might represent low '
        'volcanic hazard, a value of II might represent medium volcanic '
        'hazard and a value of III  might represent a high volcanic hazard.'
        '</p>'
        '<p>In a vector (point) Volcano data the user specified buffer '
        'distances will be used to classify the data.</p>'
        '<p>Classified values in a vector exposure data set might include '
        'building type or road type.</p>'
    ),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
}

layer_mode = {
    'key': 'layer_mode',
    'name': tr('Data type'),
    'description': tr(
        'The data type describes the values in the layer. '
        'Values can be continuous or classified'),
    'types': [
        layer_mode_continuous,
        layer_mode_classified
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

# Layer Geometry
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
        '</b>line layers are supported by InaSAFE.'),
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
        'A layer composed on polygon features that represent areas of hazard '
        'or exposure. For example areas of flood represented as polygons '
        '(for a hazard) or building footprints represented as polygons '
        '(for an exposure). The polygon layer will often need the presence '
        'of specific layer attributes too - these will vary from impact '
        'function to impact function and whether the layer represents '
        'a hazard or an exposure layer. Polygon layers can also be used '
        'for aggregation - where impact analysis results per boundary '
        'such as village or district boundaries.'),
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
        'Layer geometry can be either raster or vector. There '
        'are three possible vector geometries: point, line, and polygon. '),
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