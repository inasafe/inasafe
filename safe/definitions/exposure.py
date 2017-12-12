# coding=utf-8
"""Definitions relating to exposure in InaSAFE."""

from safe.definitions.caveats import caveat_incomplete_data
from safe.definitions.concepts import concepts
from safe.definitions.exposure_classifications import (
    generic_place_classes,
    generic_road_classes,
    generic_structure_classes,
    generic_landcover_classes,
    badan_geologi_landcover_classes,
    data_driven_classes)
from safe.definitions.field_groups import population_field_groups
from safe.definitions.fields import (
    exposure_fields,
    exposure_name_field,
    population_count_field,
    exposure_type_field,
    productivity_rate_field,
    production_cost_rate_field,
    production_value_rate_field)
from safe.definitions.layer_modes import (
    layer_mode_continuous, layer_mode_classified)
from safe.definitions.units import (
    count_exposure_unit,
    unit_metres,
    unit_square_metres,
    unit_hectares,
    unit_kilometres,
)
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

exposure_population = {
    'key': 'population',
    'name': tr('Population'),
    'description': tr(
        'The <b>population</b> describes the people that might be '
        'exposed to a particular hazard.'),
    'notes': [
        {
            'item_category': 'population_general',
            'item_header': tr('population exposure general notes'),
            'item_list': [
                # these are additional generic notes for people
                caveat_incomplete_data,
                tr('Exposed population varies by the time (day or night, '
                   'weekends, holidays etc.). Such variations are not '
                   'included in the analysis.'),
                tr('Numbers reported for population counts have been rounded '
                   'to the nearest 10 people if the total is less than 1,000; '
                   'nearest 100 people if more than 1,000 and less than '
                   '100,000; and nearest 1,000 if more than 100,000.'),
                tr('Rounding is applied to all population values, which may '
                   'cause discrepancies between subtotals and totals.'),
                concepts['rounding_methodology']['description'],
                tr('If displacement counts are 0, no minimum needs and '
                   'displaced related postprocessors will be shown.')
            ]
        }
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'actions': [
        {
            'item_category': 'general',
            'item_header': tr('general checklist'),
            'item_list': [
                tr('How will warnings be disseminated?'),
                tr('What are people\'s likely movements?'),
                tr('Which group or population is most affected?'),
                tr('Who are the vulnerable people in the population and why?'),
                tr('How will we distribute relief items?'),
                tr('Where can we obtain additional relief items?'),
                tr('How will we distribute relief items?'),
                tr('Who are the key people responsible for coordination?'),
                tr('What are the security factors for relief responders?'),
                tr('Are there enough victim identification units?')
            ]
        },
        {
            'item_category': 'shelter',
            'item_header': tr('shelter, settlement, and non-food item'),
            'item_list': [
                tr('What are people\'s likely movements?'),
                tr('How will we reach displaced people?'),
                tr('Are there enough covered floor areas available for '
                   'the displaced people?'),
                tr('What are the land-use rights for '
                   'the settlement location?'),
                tr('What is the ownership of the shelter or '
                   'settlement location?'),
                tr('What is the appropriate construction for temporary or '
                   'transitional household shelter?'),
                tr('What are the existing environmental risks or '
                   'vulnerabilities at the shelter location?'),
                tr('Are there enough clothing, bedding and household items '
                   'available for the displaced people?'),
                tr('What are the critical non-food items required by '
                   'the affected population?'),
                tr('Are the non-food items available at an active '
                   'local market?')
            ]
        },
        {
            'item_category': 'food',
            'item_header': tr('food security and nutrition'),
            'item_list': [
                tr('What kind of food does the population normally consume?'),
                tr('Are there any alternative source of food?'),
                tr('Is there enough food for the displaced people?'),
                tr('Are there any crops that can be used for consumption?'),
                tr('Are there large numbers of separated children?')
            ]
        },
        {
            'item_category': 'wash',
            'item_header': tr('sanitation and clean water'),
            'item_list': [
                tr('What water and sanitation practices were '
                   'the population accustomed to before the emergency?'),
                tr('What type of outreach system would work for '
                   'hygiene promotion for this situation?'),
                tr('What is the current water supply source and '
                   'who are the present users?'),
                tr('Are there enough water supply, sanitation and '
                   'hygiene, items available for displaced people?'),
                tr('Are water collection points close enough to '
                   'where people live?'),
                tr('Are water collection points safe?'),
                tr('Is the water source contaminated or at risk of '
                   'contamination?'),
                tr('Are there alternative sources of water nearby?'),
                tr('Is there a drainage problem?')
            ]
        },
        {
            'item_category': 'health',
            'item_header': tr('health facilities'),
            'item_list': [
                tr('What are the existing health problems?'),
                tr('What are the potential epidemic diseases?'),
                tr('Are there any potential disease outbreaks?'),
                tr('Are there any healthcare sources that are accessible and '
                   'functioning?')
            ]
        }
    ],
    'citations': [
        {
            'text': tr(
                'The Sphere Handbook: Humanitarian Charter and Minimum '
                'Standards in Humanitarian Response'),
            'link': u'http://www.spherehandbook.org/'
        }
    ],
    'allowed_geometries': [
        'point',  # See feature request #4592
        'polygon',
        'raster'
    ],
    'size_unit': unit_hectares,
    'units': [count_exposure_unit],
    'classifications': [],
    'compulsory_fields': [population_count_field],
    'fields': exposure_fields,
    'extra_fields': [exposure_name_field],
    'field_groups': population_field_groups,
    'layer_modes': [layer_mode_continuous],
    'display_not_exposed': False,
    'use_population_rounding': True,
    'layer_legend_title': tr('Number of people'),
    'measure_question': tr('how many')
}

exposure_road = {
    'key': 'road',
    'name': tr('Roads'),
    'description': tr(
        'A <b>road</b> is defined as a route used by a vehicle or people to '
        'travel between two or more points.'),
    'notes': [
        {
            'item_category': 'road_general',
            'item_header': tr('road exposure general notes'),
            'item_list': [
                # these are additional generic notes for roads
                caveat_incomplete_data,
                tr('Numbers for road lengths have been rounded to the '
                   'nearest 10 metres if the total is less than 1,000; '
                   'nearest 100 metres if more than 1,000 and less than '
                   '100,000; and nearest 1000 metres if more than 100,000.'),
                tr('Rounding is applied to all road lengths, which may cause '
                   'discrepancies between subtotals and totals.'),
                concepts['rounding_methodology']['description'],
                tr('Roads marked as not affected may still be unusable due '
                   'to network isolation. Roads marked as affected may '
                   'still be usable if they are elevated above '
                   'the local landscape.'),
                # only flood and tsunami are used with road
                # currently to it is safe to use inundated here ...
                tr('Roads are closed if they are affected.'),
                tr('Roads are open if they are not affected.')
            ]
        }
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'actions': [
        {
            'item_category': 'general',
            'item_header': tr('general checklist'),
            'item_list': [
                tr('Which roads can be used to evacuate people or '
                   'to distribute logistics?'),
                tr('What type of vehicles can use the not affected roads?'),
                tr('What sort of equipment will be needed to reopen roads?'),
                tr('Where will we get the equipment needed to open roads?'),
                tr('Which government department is responsible for supplying '
                   'equipment?')
            ]
        }
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'allowed_geometries': [
        'line'
    ],
    'size_unit': unit_metres,
    'units': [unit_metres, unit_kilometres],
    'classifications': [generic_road_classes, data_driven_classes],
    'compulsory_fields': [exposure_type_field],
    'fields': exposure_fields,
    'extra_fields': [
        # feature_value_field, disabled in V4.0, ET 13/02/17
        # feature_rate_field disabled in V4.0, ET 13/02/17
    ],
    'field_groups': [],
    'layer_modes': [layer_mode_classified],
    'display_not_exposed': True,
    'use_population_rounding': False,
    'layer_legend_title': tr('Length of roads'),
    'measure_question': tr('what length of')
}
exposure_structure = {
    'key': 'structure',
    'name': tr('Structures'),
    'description': tr(
        'A <b>structure</b> can be any relatively permanent man '
        'made feature such as a building (an enclosed structure '
        'with walls and a roof), telecommunications facility or '
        'bridge.'),
    'notes': [
        {
            'item_category': 'structure_general',
            'item_header': tr('structure exposure general notes'),
            'item_list': [
                # additional generic notes for structures
                caveat_incomplete_data,
                tr('Structures overlapping the analysis extent may be '
                   'assigned a hazard status lower than that to which they '
                   'are exposed outside the analysis area.'),
                tr('Numbers reported for structures have been rounded '
                   'to the nearest 100 if more than 1,000 and less than '
                   '100,000; and nearest 1000 if more than 100,000.'),
                tr('Rounding is applied to all structure counts greater than '
                   '1,000 which may cause discrepancies between subtotals '
                   'and totals.'),
                concepts['rounding_methodology']['description'],
            ]
        }
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'actions': [
        {
            'item_category': 'general',
            'item_header': tr('general checklist'),
            'item_list': [
                tr('Which structures have warning capacity '
                   '(e.g. sirens or speakers)?'),
                tr('Are the water and electricity services still operating?'),
                tr('Are the schools and hospitals still active?'),
                tr('Are the health centres still open?'),
                tr('Are the other public services accessible?'),
                tr('Which buildings will be evacuation centres?'),
                tr('Where will we locate the operations centre?'),
                tr('Where will we locate warehouse and/or '
                   'distribution centres?')
            ]
        }
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'allowed_geometries': [
        'polygon',
        'point'
    ],
    'size_unit': unit_square_metres,
    'units': [count_exposure_unit],
    'classifications': [generic_structure_classes, data_driven_classes],
    'compulsory_fields': [exposure_type_field],
    'fields': exposure_fields,
    'extra_fields': [
        # feature_value_field, disabled in V4.0, ET 13/02/17
        # feature_rate_field disabled in V4.0, ET 13/02/17
    ],
    'field_groups': [],
    'layer_modes': [layer_mode_classified],
    'display_not_exposed': True,
    'use_population_rounding': False,
    'layer_legend_title': tr('Number of structures'),
    'measure_question': tr('how many')
}
exposure_place = {
    'key': 'place',
    'name': tr('Places'),
    'description': tr(
        'A <b>place</b> is used to indicate that a particular location is '
        'known by a particular name.'),
    'notes': [
        {
            'item_category': 'place_general',
            'item_header': tr('place exposure general notes'),
            'item_list': [
                # additional generic notes for places
                caveat_incomplete_data,
                tr('Where places are represented as a single point, '
                   'the effect of the hazard over the entire place may '
                   'differ from the point at which the place is represented '
                   'on the map.'),
            ]
        }
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'actions': [  # these are additional generic actions
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'allowed_geometries': [
        'point'
    ],
    'size_unit': None,  # It's a point layer.
    'units': [count_exposure_unit],
    'classifications': [generic_place_classes, data_driven_classes],
    'compulsory_fields': [exposure_type_field],
    'fields': exposure_fields,
    'extra_fields': [exposure_name_field, population_count_field],
    'field_groups': [],
    'layer_modes': [layer_mode_classified],
    'display_not_exposed': True,
    'use_population_rounding': False,
    'layer_legend_title': tr('Number of places'),
    'measure_question': tr('how many')
}
exposure_land_cover = {
    'key': 'land_cover',
    'name': tr('Land cover'),
    'description': tr(
        'The <b>land cover</b> exposure data describes features on '
        'the surface of the earth that might be exposed to a particular '
        'hazard. This might include crops, forest and urban areas.'),
    'notes': [
        {
            'item_category': 'land_cover_general',
            'item_header': tr('land cover exposure general notes'),
            'item_list': [
                # these are additional generic notes for landcover
                caveat_incomplete_data,
                tr('Areas reported for land cover have been rounded to '
                   'the nearest 10 hectares if the total is less than 1,000; '
                   'nearest 100 hectares if more than 1,000 and less than '
                   '100,000; and nearest 1000 hectares if more than 100,000.'),
                tr('Rounding is applied to all land cover areas, which may '
                   'cause discrepancies between subtotals and totals.'),
                concepts['rounding_methodology']['description']
            ]
        }
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'actions': [
        {
            'item_category': 'general',
            'item_header': tr('general checklist'),
            'item_list': [
                tr('What type of crops are planted in the affected fields?'),
                tr('How long will the activity or function of '
                   'the land cover be disturbed?'),
                tr('What proportion of the land cover is damaged?'),
                tr('What potential losses will result from the land cover '
                   'damage?'),
                tr('How much productivity will be lost during this event?'),
                tr('Which crops were ready for harvest during this event?'),
                tr('What is the ownership system of the land/crops/field?'),
                tr('Are the land/crops/field accessible after the event?'),
                tr('What urgent actions can be taken to normalize '
                   'the land/crops/field?'),
                tr('What tools or equipment are needed for early recovery of '
                   'the land/crops/field?')
            ]
        }
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'allowed_geometries': [
        'polygon',
        # 'raster'  # Disable per #3600
    ],
    'size_unit': unit_hectares,
    'units': [unit_hectares],
    'classifications': [
        generic_landcover_classes,
        badan_geologi_landcover_classes,
        data_driven_classes
    ],
    'compulsory_fields': [exposure_type_field],
    'fields': exposure_fields,
    'extra_fields': [
        # feature_value_field, disabled in V4.0, ET 13/02/17
        # feature_rate_field disabled in V4.0, ET 13/02/17
        productivity_rate_field,
        production_cost_rate_field,
        production_value_rate_field
    ],
    'field_groups': [],
    'layer_modes': [layer_mode_classified],
    'display_not_exposed': False,
    'use_population_rounding': False,
    'layer_legend_title': tr('Area of landcover'),
    'measure_question': tr('what area of')
}

indivisible_exposure = [
    exposure_structure,
]

exposure_all = [
    exposure_land_cover,
    exposure_population,
    exposure_road,
    exposure_place,
    exposure_structure
]
exposures = {
    'key': 'exposures',
    'name': tr('Exposure'),
    'description': concepts['exposure']['description'],
    'citations': concepts['exposure']['citations'],
    'types': exposure_all,
}
