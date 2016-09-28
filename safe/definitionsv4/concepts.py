from safe.utilities.i18n import tr

concepts = {
    'hazard': {
        'description': tr(
             'A <b>hazard</b> represents a natural process or phenomenon '
             'that may cause loss of life, injury or other health impacts, '
             'property damage, loss of livelihoods and services, social and '
             'economic disruption, or environmental damage. For example; '
             'flood, earthquake, tsunami and volcano are all examples of '
             'hazards.'),
        'citations': [
            {
                'text': tr(
                    'UNISDR (2009) Terminology on disaster risk reduction.'),
                'link': 'https://www.unisdr.org/we/inform/terminology'
            }
        ],
    },
    'exposure': {
        'description': tr(
            '<b>Exposure</b> represents people, property, systems, or '
            'other elements present in hazard zones that are subject to '
            'potential losses in the event of a flood, earthquake, volcano '
            'etc.'),
        'citations': [
            {
                'text': tr(
                    'UNISDR (2009) Terminology on disaster risk reduction.'),
                'link': 'https://www.unisdr.org/we/inform/terminology'
            }
        ],
    },
    'generic_hazard': {
        'description': tr(
            'This is a ternary description for an area used with generic '
            'impact functions. The area may have either <b>low</b>, '
            '<b>medium</b>, or <b>high</b> classification for the hazard.'),
        'citations': [
            {
                'text': tr(
                    ''),
                'link': ''
            }
        ],
    },
    'affected': {
        'description': tr(
            'An exposure element (e.g. people, roads, buildings, land '
            'cover) that experiences a hazard (e.g. tsunami, flood, '
            'earthquake) and endures consequences (e.g. damage, evacuation, '
            'displacement, death) due to that hazard.'),
        'citations': [
            {
                'text': tr(
                    'UNISDR (2015)Proposed Updated Terminology on Disaster '
                    'Risk Reduction: A Technical Review'),
                'link': 'http://www.preventionweb.net/files/'
                        '45462_backgoundpaperonterminologyaugust20.pdf'
             }
        ],
    },
    'affected_people': {
        'description': tr(
            'People who are affected by a hazardous event. People can be '
            'affected directly or indirectly. Affected people may experience '
            'short-term or long-term consequences to their lives, livelihoods '
            'or health and in the economic, physical, social, cultural and '
            'environmental assets.'),
        'citations': [
            {
                'text': tr(
                    'UNISDR (2015)Proposed Updated Terminology on Disaster '
                    'Risk Reduction: A Technical Review'),
                'link': 'http://www.preventionweb.net/files/'
                        '45462_backgoundpaperonterminologyaugust20.pdf'
             }
        ],
    },
    'displaced_people': {
        'description': tr(
            'Displaced people are people who, for different reasons and '
            'circumstances because of risk or disaster, have to leave their '
            'place of residence.'),
        'citations': [
            {
                'text': tr(
                    'UNISDR (2015)Proposed Updated Terminology on Disaster '
                    'Risk Reduction: A Technical Review'),
                'link': 'http://www.preventionweb.net/files/'
                        '45462_backgoundpaperonterminologyaugust20.pdf'
            }
        ],
    },
    'evacuated_people': {
        'description': tr(
            'Evacuated people are people who, for different reasons and '
            'circumstances because of risk conditions or disaster, move '
            'temporarily to safer places before, during or after the '
            'occurrence of a hazardous event. Evacuation can occur from '
            'places of residence, workplaces, schools and hospitals to other '
            'places. Evacuation is usually a planned and organised '
            'mobilisation of persons, animals and goods.'),
        'citations': [
            {
                'text': tr(
                    'UNISDR (2015)Proposed Updated Terminology on Disaster '
                    'Risk Reduction: A Technical Review'),
                'link': 'http://www.preventionweb.net/files/'
                        '45462_backgoundpaperonterminologyaugust20.pdf'
            }
        ],
    },
    'injured_people': {
        'description': tr(
            'People suffering from a new or exacerbated physical or '
            'psychological harm, trauma or an illness as a result of a '
            'hazardous event.'),
        'citations': [
            {
                'text': tr(
                    'UNISDR (2015)Proposed Updated Terminology on Disaster '
                    'Risk Reduction: A Technical Review'),
                'link': 'http://www.preventionweb.net/files/'
                        '45462_backgoundpaperonterminologyaugust20.pdf'
            }
        ],
      },
    'killed_people': {
        'description': tr(
            'People who lost their lives as a consequence of a hazardous '
            'event.'),
        'citations': [
            {
                'text': tr(
                    'UNISDR (2015)Proposed Updated Terminology on Disaster '
                    'Risk Reduction: A Technical Review'),
                'link': 'http://www.preventionweb.net/files/'
                        '45462_backgoundpaperonterminologyaugust20.pdf'
            }
        ],
      },
    # Boilerplate for adding a new concept...
    #  '': {
    #    'description': tr(
    #    ),
    #    'citations': [
    #        {
    #            'text': tr(
    #                ''),
    #            'link': ''
    #        }
    #    ],
    #  },
}
