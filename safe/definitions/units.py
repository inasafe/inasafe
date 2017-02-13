# coding=utf-8

"""Definitions relating to units."""

from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

unit_feet = {
    'key': 'feet',
    'name': tr('Feet'),
    'plural_name': tr('feet'),
    'abbreviation': tr('ft'),
    'description': tr(
        '<b>Feet</b> are an imperial unit of measure. There are 12 '
        'inches in 1 foot and 3 feet in 1 yard.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
unit_generic = {
    'key': 'generic',
    'name': tr('Generic'),
    'plural_name': tr('generic'),
    'abbreviation': tr('generic'),
    'description': tr(
        'A generic unit for value that does not have unit or we do not know '
        'about the unit. It also can be used for normalised values.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
}
unit_kilogram_per_meter_square = {
    'key': 'kilogram_per_meter_square',
    'name': tr('kg/m2'),
    'plural_name': tr('kg/m2'),
    'abbreviation': tr('kg/m2'),
    'description': tr(
        '<b>Kilograms per square metre</b> is a metric unit of measure where '
        'the weight is specified according to area.  This unit is relevant '
        'for hazards such as volcanic ash.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
unit_kilometres_per_hour = {
    'key': 'kilometres_per_hour',
    'name': tr('km/h'),
    'plural_name': tr('km/h'),
    'abbreviation': tr('km/h'),
    'description': tr(
        '<b>The kilometre per hour</b> is a unit of speed, expressing the '
        'number of kilometres covered in one hour.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
unit_miles_per_hour = {
    'key': 'miles_per_hour',
    'name': tr('mph'),
    'plural_name': tr('mph'),
    'abbreviation': tr('mph'),
    'description': tr(
        '<b>The mile per hour</b> is a unit of speed, expressing the '
        'number of statute miles covered in one hour.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
unit_metres_per_second = {
    'key': 'metres_per_second',
    'name': tr('m/s'),
    'plural_name': tr('m/s'),
    'abbreviation': tr('m/s'),
    'description': tr(
        '<b>The Metres per second</b> is a unit of speed, expressing the '
        'number of metres covered in one second.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
unit_knots = {
    'key': 'knots',
    'name': tr('kn'),
    'plural_name': tr('kn'),
    'abbreviation': tr('kn'),
    'description': tr(
        '<b>The knot</b> is a unit of speed, expressing the '
        'number of nautical miles covered in one hour.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
unit_kilometres = {
    'key': 'kilometres',
    'name': tr('Kilometres'),
    'plural_name': tr('kilometres'),
    'abbreviation': tr('km'),
    'description': tr(
        '<b>Kilometres</b> are a metric unit of measure. There are 1000 '
        'metres in 1 kilometre (km).'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
}
unit_metres = {
    'key': 'metres',
    'name': tr('Metres'),
    'plural_name': tr('metres'),
    'abbreviation': tr('m'),
    'description': tr(
        '<b>Metres</b> are a metric unit of measure. There are 100 '
        'centimetres in 1 metre.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
}
unit_square_metres = {
    'key': 'square_metres',
    'name': tr('Square Metres'),
    'plural_name': tr('square metres'),
    'abbreviation': tr(u'm²'),
    'description': tr(
        '<b>Square Metres</b> are a metric unit of measure.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
}
unit_millimetres = {
    'key': 'millimetres',
    'name': tr('Millimetres'),
    'plural_name': tr('millimetres'),
    'abbreviation': tr('mm'),
    'description': tr(
        '<b>Millimetres</b> are a metric unit of measure. There are 1000 '
        'millimetres in 1 metre.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
}
unit_centimetres = {
    'key': 'centimetres',
    'name': tr('Centimetres'),
    'plural_name': tr('centimetres'),
    'abbreviation': tr('cm'),
    'description': tr(
        '<b>Centimetres</b> are a metric unit of measure. There are 100 '
        'centimetres in 1 metre.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
}
unit_mmi = {
    'key': 'mmi',
    'name': tr('MMI'),
    'plural_name': tr('MMI'),
    'abbreviation': tr('MMI'),
    'description': tr(
        'The <b>Modified Mercalli Intensity (MMI)</b> scale describes '
        'the intensity of ground shaking from a earthquake based on the '
        'effects observed by people at the surface.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
}
unit_percentage = {
    'key': 'percentage',
    'name': tr('Percentage'),
    'plural_name': tr('percentages'),
    'abbreviation': tr('%%'),
    'description': tr(
        'Percentage values ranges from 0 to 100. It represents a ratio of '
        'hundred.'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
}
count_exposure_unit = {
    'key': 'count',
    'name': tr('Count'),
    'plural_name': tr('Count'),
    'abbreviation': '',
    'description': tr(
        'Number of people (or any other exposure element) per pixel, building '
        'or area. '
        '<p>In a raster file, a pixel would have a value assigned to it '
        'representing the number (or count) of people in that pixel.</p> '
        '<p>In a vector file, a value would be assigned to an object (e.g. a '
        'building or area) representing the number of people in that '
        'object.</p> '),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
density_exposure_unit = {
    'key': 'density',
    'name': tr('Density'),
    'plural_name': tr('Density'),
    'abbreviation': tr('#'),
    'description': tr(
        'Number of people (or any other exposure element) per unit of area. '
        '<p> e.g. 35 people per km<sup>2</sup> </p>'),
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
exposure_unit = {
    'key': 'exposure_unit',
    'name': tr('Units'),
    'plural_name': tr('Units'),
    'abbreviation': tr('#'),
    'description': tr(
        'Exposure unit defines the unit for the exposure, for example '
        'people can either be measured as count or density (count per area.'),
    'types': [
        count_exposure_unit,
        density_exposure_unit
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

units_all = [
    unit_feet,
    unit_generic,
    unit_kilogram_per_meter_square,
    unit_kilometres_per_hour,
    unit_miles_per_hour,
    unit_knots,
    unit_metres_per_second,
    unit_kilometres,
    unit_metres,
    unit_millimetres,
    unit_centimetres,
    unit_mmi,
    unit_percentage,
    count_exposure_unit,
    density_exposure_unit,
    exposure_unit
]
