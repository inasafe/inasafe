# coding=utf-8

"""Definitions relating to layer keywords."""
from safe.definitions.extra_keywords import all_extra_keywords_name
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


# Base Metadata Property
property_organisation = {
    'key': 'property_organisation',
    'name': tr('Organisation'),
    'description': tr('An organized body of people who own the layer.')
}

property_email = {
    'key': 'property_email',
    'name': tr('Organisation'),
    'description': tr('The email address of the author of the layer.')
}

property_date = {
    'key': 'property_date',
    'name': tr('Date'),
    'description': tr('The date when the layer is created.')
}

property_abstract = {
    'key': 'property_abstract',
    'name': tr('Abstract'),
    'description': tr(
        'A brief narrative summary of the content of the layer.')
}

property_title = {
    'key': 'property_title',
    'name': tr('Title'),
    'description': tr('A name of the layer.')
}

property_license = {
    'key': 'property_license',
    'name': tr('License'),
    'description': tr('A permit from an authority to use the layer.')
}

property_url = {
    'key': 'property_url',
    'name': tr('URL'),
    'description': tr(
        'The address of World Web Page where we can find the layer or its '
        'description.')
}

property_layer_purpose = {
    'key': 'property_layer_purpose',
    'name': tr('Layer Purpose'),
    'description': tr(
        'The purpose of the layer, it can be hazard layer, exposure layer, or '
        'aggregation layer.')
}

property_layer_mode = {
    'key': 'property_layer_mode',
    'name': tr('Layer Mode'),
    'description': tr(
        'The mode of the layer, it can be continuous or classified layer.')
}

property_layer_geometry = {
    'key': 'property_layer_geometry',
    'name': tr('Layer Geometry'),
    'description': tr(
        'The geometry type of the layer, it can be point, line, polygon, '
        'or raster.')
}

property_keyword_version = {
    'key': 'property_keyword_version',
    'name': tr('Keyword Version'),
    'description': tr(
        'The version of the keywords for example 3.5 or 4.0. It depends on '
        'the InaSAFE version and has backward compatibility for some version.')
}

property_scale = {
    'key': 'property_scale',
    'name': tr('Scale'),
    'description': tr('The default scale of the layer.')
}

property_source = {
    'key': 'property_source',
    'name': tr('Source'),
    'description': tr('The location of where does the layer comes from.')
}

property_inasafe_fields = {
    'key': 'property_inasafe_fields',
    'name': tr('InaSAFE Fields'),
    'description': tr(
        'The mapping of field to a field concept in InaSAFE. More than one '
        'field can be mapped to the same field concept. It is stored as a '
        'dictionary format where field concept key is the key of the '
        'dictionary. And the value will be the list of fields that mapped '
        'into the field concept.')
}

property_inasafe_default_values = {
    'key': 'property_inasafe_default_values',
    'name': tr('InaSAFE Default Values'),
    'description': tr(
        'If a field concept in InaSAFE does not have field to be mapped, '
        'InaSAFE default values can be used to set a default value for a '
        'field concept in InaSAFE. One field concept can only have one '
        'default value. It is stored as dictionary where field concept key is '
        'the key of the dictionary and the default value will be the value of '
        'that key.')
}

# Exposure Layer Metadata Properties
property_exposure = {
    'key': 'property_exposure',
    'name': tr('Exposure'),
    'description': tr('The type of exposure that the layer represents.')
}

property_exposure_unit = {
    'key': 'property_exposure_unit',
    'name': tr('Exposure Unit'),
    'description': tr('The unit of the exposure that the layer represents.')
}

property_classification = {
    'key': 'property_classification',
    'name': tr('Exposure Classification'),
    'description': tr(
        'The classification of the exposure type. Some of the available '
        'values are generic_structure_classes, generic_road_classes, or '
        'data_driven_classes.')
}

property_value_map = {
    'key': 'property_value_map',
    'name': tr('Exposure Value Map'),
    'description': tr(
        'The mapping of class\'s key of the classification to some '
        'unique values.')
}

property_active_band = {
    'key': 'property_active_band',
    'name': tr('Active Band'),
    'description': tr(
        'Active band indicate which band of the layer that contains the data '
        'that the user want to use. The default value is the first band. It '
        'is only applied for multi band dataset.')
}

# Hazard Layer Metadata Properties
property_hazard = {
    'key': 'property_hazard',
    'name': tr('Hazard'),
    'description': tr('The type of hazard that the layer represents.')
}

property_hazard_category = {
    'key': 'property_hazard_category',
    'name': tr('Hazard Category'),
    'description': tr(
        'The category of the hazard that the layer represents. It can be '
        'single event or multiple event.')
}

property_continuous_hazard_unit = {
    'key': 'property_continuous_hazard_unit',
    'name': tr('Continuous Hazard Unit'),
    'description': tr('A unit for continuous hazard.')
}

property_value_maps = {
    'key': 'property_value_maps',
    'name': tr('Hazard Value Maps'),
    'description': tr(
        'A collection of value mapping for each exposure type. Where exposure '
        'type key is the key. For each exposure type, there is one or more '
        'classifications and its value mapping (to indicate which class a '
        'value mapped into). There is a flag `active` to indicate which '
        'classification is the active one.')
    # Sample
    # value_maps = {
    #     'land_cover': {
    #         'flood_hazard_classes': {
    #             'active': False,
    #             'classes': {
    #                 'dry': ['No', 'NO', 'dry'],
    #                 'wet': ['Yes', 'YES', 'Very wet', 'wet'],
    #             }
    #         },
    #         'flood_petabencana_hazard_classes': {
    #             'active': True,
    #             'classes': {
    #                 'low': ['No', 'NO', 'dry'],
    #                 'high': ['Yes', 'YES', 'wet'],
    #                 'very_high': ['Very wet', ]
    #             },
    #         }
    #     },
    #     'road': {
    #         'flood_hazard_classes': {
    #             'active': True,
    #             'classes': {
    #                 'dry': ['No', 'NO', 'dry'],
    #                 'wet': ['Yes', 'YES', 'Very wet', 'wet'],
    #             }
    #         },
    #         'flood_petabencana_hazard_classes': {
    #             'active': False,
    #             'classes': {
    #                 'low': ['No', 'NO', 'dry'],
    #                 'high': ['Yes', 'YES', 'wet'],
    #                 'very_high': ['Very wet', ]
    #             },
    #         }
    #     }
    # }
}

property_thresholds = {
    'key': 'property_thresholds',
    'name': tr('Hazard Thresholds'),
    'description': tr(
        'A collection of thresholds for each exposure type. Where exposure '
        'type key is the key. For each exposure type, there is one or more '
        'classifications and its thresholds (to indicate which class a '
        'range of value mapped into). The range consists of minimum value and '
        'maximum value in list. Minimum value is excluded while maximum '
        'value is included in the range. There is a flag `active` to '
        'indicate which classification is the active one.')
    # Sample
    # value_maps = {
    #     'land_cover': {
    #         'flood_hazard_classes': {
    #             'active': False,
    #             'classes': {
    #                 'dry': [0, 1],
    #                 'wet': [1, 999],
    #             }
    #         },
    #         'flood_petabencana_hazard_classes': {
    #             'active': True,
    #             'classes': {
    #                 'low': [0, 1],
    #                 'high': [1, 5],
    #                 'very_high': [5, 999]
    #             },
    #         }
    #     },
    #     'road': {
    #         'flood_hazard_classes': {
    #             'active': True,
    #             'classes': {
    #                 'dry': [0, 1],
    #                 'wet': [1, 999],
    #             }
    #         },
    #         'flood_petabencana_hazard_classes': {
    #             'active': False,
    #             'classes': {
    #                 'low': [0, 1],
    #                 'high': [1, 4],
    #                 'very_high': [4, 999]
    #             },
    #         }
    #     }
    # }
}

# Output Layer Metadata Property
property_exposure_keywords = {
    'key': 'property_exposure_keywords',
    'name': tr('Exposure Keywords'),
    'description': tr(
        'A copy of original exposure keywords in the output\'s analysis.'
    )
}

property_hazard_keywords = {
    'key': 'property_hazard_keywords',
    'name': tr('Hazard Keywords'),
    'description': tr(
        'A copy of original hazard keywords in the output\'s analysis.'
    )
}

property_aggregation_keywords = {
    'key': 'property_aggregation_keywords',
    'name': tr('Aggregation Keywords'),
    'description': tr(
        'A copy of original aggregation keywords in the output\'s analysis.'
    )
}

property_provenance_data = {
    'key': 'property_provenance_data',
    'name': tr('Provenance Data'),
    'description': tr(
        'A collection of provenance of the analysis as dictionary.'
    )
}

property_extra_keywords = {
    'key': 'extra_keywords',
    'name': tr('Extra Keywords'),
    'description': tr(
        'A collection of extra keyword for creating richer report.'
    ),
    # For translation
    'member_names': all_extra_keywords_name
}
