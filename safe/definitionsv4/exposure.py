from safe.definitionsv4.concepts import concepts
from safe.utilities.i18n import tr

exposure_population = {
    'key': 'population',
    'name': tr('Population'),
    'description': tr(
        'The <b>population</b> describes the people that might be '
        'exposed to a particular hazard.'),
    'notes': [  # these are additional generic notes for people - IF has more
        tr('Numbers reported for population counts have been rounded to the '
           'nearest 10 people if the total is less than 1,000; nearest 100 '
           'people if more than 1,000 and less than 100,000; and nearest '
           '1000 if more than 100,000.'),
        tr('Rounding is applied to all population values, '
           'which may cause discrepancies when adding values.'),

    ],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'actions': [  # these are additional generic actions - IF has more
        tr('How will warnings be disseminated?'),
        tr('What are people\'s likely movements?'),
        tr('Which group or population is most affected?'),
        tr('Who are the vulnerable people in the population and why?'),
        tr('What are people\'s likely movements?'),
        tr('What are the security factors for the affected people?'),
        tr('What are the security factors for relief responders?'),
        tr('How will we reach displaced people?'),
        tr('What kind of food does the population normally consume?'),
        tr('What are the critical non-food items required by the affected '
           'population?'),
        tr('If yes, where are they located and how will we distribute them?'),
        tr('If no, where can we obtain additional relief items and how'
           ' will we distribute them?'),
        tr('What are the related health risks?'),
        tr('Who are the key people responsible for coordination?'),
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}
exposure_people_in_building = {
    'key': 'people_in_building',
    'name': tr('People in buildings'),
    'description': tr(
        '<b>People in buildings</b> exposure data assigns the population '
        'of a specific administrative area to the buildings with a '
        'residential function in that area. <p>The process of assigning '
        'people to buildings assumes that all people and buildings in the '
        'area are mapped.</p>'),
    'notes': exposure_population['notes'],
    'continuous_notes': [  # notes specific to continuous data
    ],
    'classified_notes': [  # notes specific to classified data
    ],
    'actions': exposure_population['actions'],
    'citations': [
        {
            'text': tr('UNISDR (2015) Background Paper: Proposed Updated '
                       'Terminology on Disaster Risk  Reduction '
                       'Reduction.'),
            'link': 'http://www.preventionweb.net/files/'
                    '45462_backgoundpaperonterminologyaugust20.pdf'
        }
    ]
}
exposure_road = {
    'key': 'road',
    'name': tr('Roads'),
    'description': tr(
        'A <b>road</b> is a defined route used by a vehicle or people to '
        'travel between two or more points.'),
    'notes': [  # these are additional generic notes for roads - IF has more
        tr('Numbers reported for road lengths have been rounded to the '
           'nearest meter.'),
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
        tr('What sort of equipment will be needed to reopen roads & where '
           'will we get it?'),
        tr('Which government department is responsible for supplying '
           'equipment?')

    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
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
        tr('Which structures have warning capacity (eg. sirens, speakers, '
           'etc.)?'),
        tr('Are the water and electricity services still operating?'),
        tr('Are the health centres still open?'),
        tr('Are the other public services accessible?'),
        tr('Which buildings will be evacuation centres?'),
        tr('Where will we locate the operations centre?'),
        tr('Where will we locate warehouse and/or distribution centres?'),
        tr('Are the schools and hospitals still active?'),
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
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
    ]
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
    ]
}
exposure_all = [
    exposure_land_cover,
    exposure_people_in_building,
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
