from safe.utilities.i18n import tr

unit_feet = {
    'key': 'feet',
    'name': tr('Feet'),
    'plural_name': tr('feet'),
    'abbreviation': tr('feet'),
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
