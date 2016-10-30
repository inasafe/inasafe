# coding=utf-8
"""Definitions relating to exposure in InaSAFE."""

from safe.definitionsv4.concepts import concepts
from safe.definitionsv4.units import (
    count_exposure_unit, density_exposure_unit)
from safe.definitionsv4.fields import (
    adult_count_field,
    adult_ratio_field,
    elderly_count_field,
    elderly_ratio_field,
    exposure_fields,
    exposure_name_field,
    female_ratio_field,
    women_count_field,
    youth_count_field,
    youth_ratio_field,
    population_count_field
)
from safe.definitionsv4.layer_modes import (
    layer_mode_classified, layer_mode_continuous)
from safe.definitionsv4.exposure_classifications import (
    generic_place_classes,
    generic_road_classes,
    generic_structure_classes,
    generic_landcover_classes,
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
    'notes': [  # these are additional generic notes for people - IF has more
        tr('Numbers for population counts have been rounded to the '
           'nearest 10 people if the total is less than 1,000; nearest 100 '
           'people if more than 1,000 and less than 100,000; and nearest '
           '1000 if more than 100,000.'),
        tr('Rounding is applied to all population values, which may cause '
           'discrepancies between subtotals and totals.'),

    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'actions': [  # these are additional generic actions
        tr('Which group or population is most affected?'),
        tr('Who are the vulnerable people in the population and why?'),
        tr('How will we distribute relief items?'),
        tr('Where can we obtain additional relief items?'),
        tr('How will we distribute relief items?'),
        tr('Who are the key people responsible for coordination?'),
        tr('What are the security factors for relief responders?'),
        tr('Are there enough victim identification units?'),
        # these are shelter actions
        tr('What are people\'s likely movements?'),
        tr('How will we reach displaced people?'),
        tr('Are there enough covered floor areas available for the displaced '
           'people?'),
        tr('What are the land-use rights for the settlement location?'),
        tr('What is the ownership of the shelter or settlement location'),
        tr('What is the appropriate construction for temporary or '
           'transitional household shelter?'),
        tr('What are the existing environmental risks or vulnerabilities at '
           'the shelter location?'),
        tr('Are there enough clothing, bedding and household items available '
           'for the displaced people?'),
        tr('What are the critical non-food items required by the affected '
           'population?'),
        tr('Are the non-food items available at an active local market?'),
        # these are food security and nutrition actions
        tr('What kind of food does the population normally consume?'),
        tr('Are there any alternative source of food?'),
        tr('Is there enough food for the displaced people?'),
        tr('Are there any crops that can be used for consumption?'),
        tr('Are there large numbers of separated children?'),
        # these are WASH actions
        tr('What water and sanitation practices were the population '
           'accustomed to before the emergency?'),
        tr('What type of outreach system would work for hygiene promotion for '
           'this situation?'),
        tr('What is the current water supply source and who are the present '
           'users?'),
        tr('Are there enough water supply, sanitation and hygiene, items '
           'available for displaced people?'),
        tr('Are water collection points close enough to where people live?'),
        tr('Are water collection points safe?'),
        tr('Is the water source contaminated or at risk of contamination?'),
        tr('Are there alternative sources of water nearby?'),
        tr('Is there a drainage problem?'),
        # these are health actions
        tr('What are the existing health problems?'),
        tr('What are the potential epidemic diseases?'),
        tr('Are there any potential disease outbreaks?'),
        tr('Are there any healthcare sources that are accessible and '
           'functioning?')

    ],
    'citations': [
        {
                'text': tr(
                    'The Sphere Handbook: Humanitarian Charter and Minimum '
                    'Standards in Humanitarian Response'),
                'link': 'http://www.spherehandbook.org/'
        }
    ],
    'allowed_geometries': [
        'polygon',
        'raster'
    ],
    'units': [
        count_exposure_unit,
        density_exposure_unit],
    'classifications': [],
    'fields': exposure_fields,
    'extra_fields': [
        population_count_field,
        exposure_name_field,
        women_count_field,
        youth_count_field,
        adult_count_field,
        elderly_count_field,
        female_ratio_field,
        youth_ratio_field,
        adult_ratio_field,
        elderly_ratio_field
    ],
    'layer_modes': [layer_mode_continuous]
}

exposure_road = {
    'key': 'road',
    'name': tr('Roads'),
    'description': tr(
        'A <b>road</b> is a defined route used by a vehicle or people to '
        'travel between two or more points.'),
    'notes': [  # these are additional generic notes for roads - IF has more
        tr('Numbers for road lengths have been rounded to the nearest metre.'),
        tr('Roads marked as not affected may still be unusable due to network '
           'isolation. Roads marked as affected may still be usable if they '
           'are elevated above the local landscape.'),
        # only flood and tsunami are used with road
        # currently to it is safe to use inundated here ...
        tr('Roads are closed if they are affected.'),
        tr('Roads are open if they are not affected.')
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'actions': [  # these are additional generic actions - IF has more
        tr('Which roads can be used to evacuate people or to distribute '
           'logistics?'),
        tr('What type of vehicles can use the unaffected roads?'),
        tr('What sort of equipment will be needed to reopen roads?'),
        tr('Where will we get the equipment needed to open roads?'),
        tr('Which government department is responsible for supplying '
           'equipment?')

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
    'units': [],
    'classifications': [generic_road_classes],
    'fields': exposure_fields,
    'extra_fields': [],
    'layer_modes': [layer_mode_classified]
}
exposure_structure = {
    'key': 'structure',
    'name': tr('Structures'),
    'description': tr(
        'A <b>structure</b> can be any relatively permanent man '
        'made feature such as a building (an enclosed structure '
        'with walls and a roof), telecommunications facility or '
        'bridge.'),
    'notes': [  # additional generic notes for structures - IF has more
        tr('Numbers reported for structures have not been rounded.')
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'actions': [  # these are additional generic actions - IF has more
        tr('Which structures have warning capacity (eg. sirens or speakers)?'),
        tr('Are the water and electricity services still operating?'),
        tr('Are the schools and hospitals still active?'),
        tr('Are the health centres still open?'),
        tr('Are the other public services accessible?'),
        tr('Which buildings will be evacuation centres?'),
        tr('Where will we locate the operations centre?'),
        tr('Where will we locate warehouse and/or distribution centres?')

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
    'units': [],
    'classifications': [generic_structure_classes],
    'fields': exposure_fields,
    'extra_fields': [
        population_count_field,
        women_count_field,
        youth_count_field,
        adult_count_field,
        elderly_count_field,
        female_ratio_field,
        youth_ratio_field,
        adult_ratio_field,
        elderly_ratio_field
    ],
    'layer_modes': [layer_mode_classified]
}
exposure_place = {
    'key': 'place',
    'name': tr('Places'),
    'description': tr(
        'A <b>place</b> is used to indicate that a particular location is '
        'known by a particular name.'),
    'notes': [  # additional generic notes for places - IF has more
        tr('Where places are represented as a single point, the effect of the '
           'hazard over the entire place may differ from the point at which '
           'the place is represented on the map.'),
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'actions': [  # these are additional generic actions - IF has more
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
    'units': [],
    'classifications': [generic_place_classes],
    'fields': exposure_fields,
    'extra_fields': [
        population_count_field,
        exposure_name_field,
        women_count_field,
        youth_count_field,
        adult_count_field,
        elderly_count_field,
        female_ratio_field,
        youth_ratio_field,
        adult_ratio_field,
        elderly_ratio_field
    ],
    'layer_modes': [layer_mode_classified]
}
exposure_land_cover = {
    'key': 'land_cover',
    'name': tr('Land cover'),
    'description': tr(
        'The <b>land cover</b> exposure data describes features on '
        'the surface of the earth that might be exposed to a particular '
        ' hazard. This might include crops, forest and urban areas. '),
    'notes': [
        # these are additional generic notes for landcover - IF has more
        tr('Areas reported for land cover have not been rounded.'),
    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'actions': [  # these are additional generic actions - IF has more
        tr('What type of crops are planted in the affected fields?'),
        tr('How long will the activity or function of the land cover be '
           'disturbed?'),
        tr('What proportion of the land cover is damaged?'),
        tr('What potential losses will result from the land cover '
           'damage?'),
        tr('How much productivity will be lost during this event?'),
        tr('Which crops were ready for harvest during this event?'),
        tr('What is the ownership system of the land/crops/field?'),
        tr('Are the land/crops/field accessible after the event?'),
        tr('What urgent actions can be taken to normalize the land/crops/'
           'field?'),
        tr('What tools or equipment are needed for early recovery of the '
           'land/crops/field?')
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'allowed_geometries': [
        'polygon',
        'raster'
    ],
    'units': [],
    'classifications': [generic_landcover_classes],
    'fields': exposure_fields,
    'extra_fields': [],
    'layer_modes': [layer_mode_classified]
}
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
