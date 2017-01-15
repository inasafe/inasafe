# coding=utf-8
"""
Definitions relating to layer modes (continuous or classified data).
"""

from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


layer_mode_continuous = {
    'key': 'continuous',
    'name': tr('Continuous'),
    'description': tr(
        '<b>Continuous</b> data can be used in raster hazard or exposure data '
        'where the values in the data are either integers or decimal values '
        'representing a continuously varying phenomenon. For example flood '
        'depth is a continuous value from 0 to the maximum reported depth '
        'during a flood. <p>Raster exposure data such as population data are '
        'also continuous. In this example the cell values represent the '
        'number of people in cell.</p>'
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
        '<p>Classified values in a vector (polygon) volcano data set might '
        'represent discrete classes where a value of I might represent low '
        'volcanic hazard, a value of II might represent medium volcanic '
        'hazard and a value of III  might represent a high volcanic hazard.'
        '</p>'
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
        'The data type describes the values in the layer. Values can be '
        'continuous or classified'),
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

layer_mode_all = [
    layer_mode_classified,
    layer_mode_continuous
]
