# coding=utf-8

"""Definitions relating to units."""

from collections import OrderedDict

from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

unit_feet = {
    'key': 'feet',
    'name': tr('Feet'),
    'plural_name': tr('feet'),
    'measure': tr('Length'),
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
    'measure': tr('Count'),
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
    'measure': tr('Weight/area'),
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
    'measure': tr('Speed'),
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
    'measure': tr('Speed'),
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
    'measure': tr('Speed'),
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
    'measure': tr('Speed'),
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
    'measure': tr('Length'),
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
    'measure': tr('Length'),
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
unit_hectares = {
    'key': 'hectare',
    'name': tr('Hectare'),
    'base_unit': False,
    'plural_name': tr('hectares'),
    'measure': tr('Area'),
    'abbreviation': 'ha',
    'description': tr(
        '<b>Hectare</b> is an SI accepted metric system unit of area equal '
        'to 100 ares (10,000 m²) and primarily used in the measurement of '
        'land'),
    'citations': [
        {
            'text': 'Wikipedia',
            'link': 'https://en.wikipedia.org/wiki/Hectare'
        }
    ],
}
unit_hundred_kilograms = {
    'key': 'hundred_kilograms',
    'name': tr('Hundreds Kilogram'),
    'base_unit': False,
    'plural_name': tr('hundreds kilograms'),
    'measure': tr('Weight'),
    'abbreviation': 'hundreds kg',
    'description': tr(
        '<b>A hundred kilograms</b> is a unit of weight equal to 100 '
        'kilograms.'),
    'citations': [],
}
unit_square_metres = {
    'key': 'square_metres',
    'name': tr('Square Metres'),
    'plural_name': tr('square metres'),
    'measure': tr('Area'),
    'abbreviation': tr('m²'),
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
    'measure': tr('Length'),
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
    'measure': tr('Length'),
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
    'measure': tr('MMI'),
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
    'measure': tr('Percentage'),
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
    'measure': tr('Count'),
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
    'measure': tr('Density'),
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
    'name': tr('Unit'),
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


unit_ones = {
    'key': 'unit_ones',
    'name': tr('One'),
    'plural_name': tr('Ones'),
    'abbreviation': tr('#'),
    'description': None,
    'types': [
        count_exposure_unit
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

unit_tens = {
    'key': 'unit_tens',
    'name': tr('Ten'),
    'plural_name': tr('Tens'),
    'abbreviation': tr('#'),
    'description': None,
    'types': [
        count_exposure_unit
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

unit_hundreds = {
    'key': 'unit_hundreds',
    'name': tr('Hundred'),
    'plural_name': tr('Hundreds'),
    'abbreviation': tr('#'),
    'description': None,
    'types': [
        count_exposure_unit
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}


unit_thousand = {
    'key': 'unit_thousand',
    'name': tr('Thousand'),
    'plural_name': tr('Thousands'),
    'abbreviation': tr('#'),
    'description': None,
    'types': [
        count_exposure_unit
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
unit_million = {
    'key': 'unit_million',
    'name': tr('Million'),
    'plural_name': tr('Millions'),
    'abbreviation': tr('#'),
    'description': None,
    'types': [
        count_exposure_unit
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
unit_billion = {
    'key': 'unit_billion',
    'name': tr('Billion'),
    'plural_name': tr('Billions'),
    'abbreviation': tr('#'),
    'description': None,
    'types': [
        count_exposure_unit
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
unit_trillion = {
    'key': 'unit_trillion',
    'name': tr('Trillion'),
    'plural_name': tr('Trillions'),
    'abbreviation': tr('#'),
    'description': None,
    'types': [
        count_exposure_unit
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

nominal_mapping = OrderedDict()
nominal_mapping[1] = unit_ones
nominal_mapping[10] = unit_tens
nominal_mapping[100] = unit_hundreds
nominal_mapping[1000] = unit_thousand
nominal_mapping[1000000] = unit_million
nominal_mapping[1000000000] = unit_billion
nominal_mapping[1000000000000] = unit_trillion

unit_mapping = (
    (unit_metres, unit_millimetres, 1000),
    (unit_metres, unit_centimetres, 100),
    (unit_metres, unit_kilometres, 0.001),
    (unit_square_metres, unit_hectares, 0.0001),
    (unit_metres_per_second, unit_knots, 1.94384),
    (unit_metres_per_second, unit_miles_per_hour, 2.23694),
    (unit_metres_per_second, unit_kilometres_per_hour, 3.6),

    # Unfortunately, we need to add every permutations.
    # We need to improve convert_unit in safe.utilities.rounding.
    (unit_millimetres, unit_centimetres, 0.1),
    (unit_millimetres, unit_kilometres, 0.000001),
    (unit_centimetres, unit_kilometres, 0.00001),
    (unit_knots, unit_miles_per_hour, 1.15078),
    (unit_knots, unit_kilometres_per_hour, 1.852),
    (unit_miles_per_hour, unit_kilometres_per_hour, 1.60934),
)

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
    unit_square_metres,
    unit_hectares,
    unit_mmi,
    unit_percentage,
    count_exposure_unit,
    density_exposure_unit,
    exposure_unit,
    unit_thousand,
    unit_million,
    unit_billion,
    unit_trillion,
]
