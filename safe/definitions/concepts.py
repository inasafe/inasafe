# coding=utf-8
"""Concepts used in various places in InaSAFE.

Where possible please supply citations. Concepts are used in reporting display
and in other places like the wizard to ensure that the user will have adequate
contextual information to accompany the data shown to them.
"""

from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

concepts = {
    'analysis': {
        'key': 'analysis',
        'description': tr(
            '<p>An <b>analysis</b> from the point of view of using InaSAFE is '
            'the process whereby a hazard layer, an exposure layer and '
            'an optional aggregation layer are used to determine the '
            'potential impact of the hazard data on the exposure. The '
            'analysis results are grouped by region (as defined in the '
            'aggregation layer).</p> '
            '<p>In InaSAFE the analysis process commences with a preparation '
            'phase where each input layer is pre-processed to ensure that it '
            'is in a consistent state. The hazard and aggregation are '
            'reprojected to the same coordinate reference system of the '
            'exposure dataset. Any data that is not within the selected '
            'aggregation areas is removed. Note that any modifications made '
            'are done on copies of the original data - the original data are '
            'not modified in any way.</p>'
            '<p>Any continuous datasets are reclassified into classfied (also '
            'sometimes referred to as categorical) datasets.</p>'
            '<p>The aggregation layer and the hazard are combined using a GIS '
            'union operation and then each exposure within these areas is '
            'counted to arrive at a total number, length or area of '
            'exposure features per aggregation area. These processes are '
            'defined in more detail below. After the primary GIS processing '
            'has been carried out, one or more post-processors are applied '
            'to the resulting datasets in order to compute statistics like '
            'the breakdown of buildings or the area of each land use type '
            'in the affected areas.</p>'
            '<p>The final part of the analysis process is report generation '
            'whereby InaSAFE generates various tables and cartographic '
            'products to represent the result summaries. InaSAFE will '
            'also create a number of spatial and non-spatial products which '
            'you can use to generate your own reports - for example by '
            'importing the data into a spreadsheet and further analysing it '
            'there.</p>'),
        'citations': [
            {
                'text': tr(
                    ''),
                'link': u''
            }
        ],
    },
    'hazard': {
        'key': 'hazard',
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
                'link': u'https://www.unisdr.org/we/inform/terminology'
            }
        ],
    },
    'exposure': {
        'key': 'exposure',
        'description': tr(
            '<b>Exposure</b> represents people, property, systems, or '
            'other elements present in hazard zones that are subject to '
            'potential losses in the event of a flood, earthquake, volcano '
            'etc.'),
        'citations': [
            {
                'text': tr(
                    'UNISDR (2009) Terminology on disaster risk reduction.'),
                'link': u'https://www.unisdr.org/we/inform/terminology'
            }
        ],
    },
    'generic_hazard': {
        'key': 'generic_hazard',
        'description': tr(
            'A generic hazard is any dataset where the areas within the '
            'data set have been classified as either <b>low</b>, '
            '<b>medium</b>, or <b>high</b> hazard level. Use generic hazard '
            'in cases where InaSAFE does not have an existing hazard concept '
            'for the data you are using.'),
        'citations': [
            {
                'text': tr(
                    ''),
                'link': u''
            }
        ],
    },
    'affected': {
        'key': 'affected',
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
                'link': u'http://www.preventionweb.net/files/'
                        u'45462_backgoundpaperonterminologyaugust20.pdf'
            }
        ],
    },
    'exposed_people': {
        'key': 'exposed_people',
        'description': tr(
            'People who are present in hazard zones and are thereby subject '
            'to potential losses. In InaSAFE, people who are exposed are '
            'those people who are within the extent of the hazard.'),
        'citations': [
            {
                'text': tr(
                    'UNISDR (2009)Terminology on Disaster'),
                'link': u'https://www.unisdr.org/we/inform/terminology'
            }
        ],
    },
    'affected_people': {
        'key': 'affected_people',
        'description': tr(
            'People who are affected by a hazardous event. People can be '
            'affected directly or indirectly. Affected people may experience '
            'short-term or long-term consequences to their lives, livelihoods '
            'or health and in the economic, physical, social, cultural and '
            'environmental assets. In InaSAFE, people who are killed during '
            'the event are also considered affected.'),
        'citations': [
            {
                'text': tr(
                    'UNISDR (2015)Proposed Updated Terminology on Disaster '
                    'Risk Reduction: A Technical Review'),
                'link': u'http://www.preventionweb.net/files/'
                        u'45462_backgoundpaperonterminologyaugust20.pdf'
            }
        ],
    },
    'directly_affected_people': {
        'key': 'directly_affected_people',
        'description': tr(
            'People who have suffered injury, illness or other health effects '
            'who were evacuated, displaced,relocated; or have suffered direct '
            'damage to their livelihoods, economic, physical, social,cultural '
            'and environmental assets. In InaSAFE, people who are missing or '
            'dead may be considered as directly affected.'),
        'citations': [
            {
                'text': tr(
                    'UNISDR (2015)Proposed Updated Terminology on Disaster '
                    'Risk Reduction: A Technical Review'),
                'link': u'http://www.preventionweb.net/files/'
                        u'45462_backgoundpaperonterminologyaugust20.pdf'
            }
        ],
    },
    'indirectly_affected_people': {
        'key': 'indirectly_affected_people',
        'description': tr(
            'People who have suffered consequences, other than or in addition '
            'to direct effects, over time due to disruption or changes in '
            'economy, critical infrastructures, basic services, commerce,work '
            'or social, health and psychological consequences. In InaSAFE, '
            'people who are indirectly affected are not included in minimum '
            'needs reports.'),
        'citations': [
            {
                'text': tr(
                    'UNISDR (2015)Proposed Updated Terminology on Disaster '
                    'Risk Reduction: A Technical Review'),
                'link': u'http://www.preventionweb.net/files/'
                        u'45462_backgoundpaperonterminologyaugust20.pdf'
            }
        ],
    },
    'displaced_people': {
        'key': 'displaced_people',
        'description': tr(
            'Displaced people are people who, for different reasons and '
            'circumstances because of risk or disaster, have to leave their '
            'place of residence. In InaSAFE, demographic and minimum'
            'needs reports are based on displaced / evacuated people.'),
        'citations': [
            {
                'text': tr(
                    'UNISDR (2015)Proposed Updated Terminology on Disaster '
                    'Risk Reduction: A Technical Review'),
                'link': u'http://www.preventionweb.net/files/'
                        u'45462_backgoundpaperonterminologyaugust20.pdf'
            }
        ],
    },
    'evacuated_people': {
        'key': 'evacuated_people',
        'description': tr(
            'Evacuated people are people who, for different reasons and '
            'circumstances because of risk conditions or disaster, move '
            'temporarily to safer places before, during or after the '
            'occurrence of a hazardous event. Evacuation can occur from '
            'places of residence, workplaces, schools and hospitals to other '
            'places. Evacuation is usually a planned and organised '
            'mobilisation of persons, animals and goods for eventual return.'
            'In InaSAFE, demographic and minimum needs reports are based on '
            'displaced / evacuated people.'),
        'citations': [
            {
                'text': tr(
                    'UNISDR (2015)Proposed Updated Terminology on Disaster '
                    'Risk Reduction: A Technical Review'),
                'link': u'http://www.preventionweb.net/files/'
                        u'45462_backgoundpaperonterminologyaugust20.pdf'
            }
        ],
    },
    'relocated_people': {
        'key': 'relocated_people',
        'description': tr(
            'Relocated people are people who, for different reasons or '
            'circumstances because of risk or disaster, have moved '
            'permanently from their places of residence to new sites.'),
        'citations': [
            {
                'text': tr(
                    'UNISDR (2015)Proposed Updated Terminology on Disaster '
                    'Risk Reduction: A Technical Review'),
                'link': u'http://www.preventionweb.net/files/'
                        u'45462_backgoundpaperonterminologyaugust20.pdf'
            }
        ],
    },
    'injured_people': {
        'key': 'injured_people',
        'description': tr(
            'People suffering from a new or exacerbated physical or '
            'psychological harm, trauma or an illness as a result of a '
            'hazardous event.'),
        'citations': [
            {
                'text': tr(
                    'UNISDR (2015)Proposed Updated Terminology on Disaster '
                    'Risk Reduction: A Technical Review'),
                'link': u'http://www.preventionweb.net/files/'
                        u'45462_backgoundpaperonterminologyaugust20.pdf'
            }
        ],
    },
    'killed_people': {
        'key': 'killed_people',
        'description': tr(
            'People who lost their lives as a consequence of a hazardous '
            'event.'),
        'citations': [
            {
                'text': tr(
                    'UNISDR (2015)Proposed Updated Terminology on Disaster '
                    'Risk Reduction: A Technical Review'),
                'link': u'http://www.preventionweb.net/files/'
                        u'45462_backgoundpaperonterminologyaugust20.pdf'
            }
        ],
    },
    'youth': {
        'key': 'youth',
        'description': tr(
            'A person aged between 0 and 14 years.'),
        'citations': [
            {
                'text': tr(
                    'CIA (2016)The World Factbook.'),
                'link': u'https://www.cia.gov/library/publications/'
                        u'resources/the-world-factbook/'
            }
        ],
    },
    'adult': {
        'key': 'adult',
        'description': tr(
            'Person aged between 15 and 64 years, usually of working age.'),
        'citations': [
            {
                'text': tr(
                    'CIA (2016)The World Factbook.'),
                'link': u'https://www.cia.gov/library/publications/'
                        u'resources/the-world-factbook/'
            }
        ],
    },
    'elderly': {
        'key': 'elderly',
        'description': tr(
            'Person aged 64 years and over.'),
        'citations': [
            {
                'text': tr(
                    'CIA (2016)The World Factbook.'),
                'link': u'https://www.cia.gov/library/publications/'
                        u'resources/the-world-factbook/'
            }
        ],
    },
    'people': {
        'key': 'people',
        'description': tr(
            'Human beings in general or considered collectively.'),
        'citations': [
            {
                'text': tr(
                    'Oxford Dictionary.'),
                'link': u'https://en.oxforddictionaries.com/definition/people'
            }
        ],
    },
    'female': {
        'key': 'female',
        'description': tr(
            'Relating to the characteristics of women.'),
        'citations': [
            {
                'text': tr(
                    'Oxford Dictionary.'),
                'link': u'https://en.oxforddictionaries.com/definition/female'
            }
        ],
    },
    'male': {
        'key': 'male',
        'description': tr(
            'Relating to the characteristics of men.'),
        'citations': [
            {
                'text': tr(
                    'Oxford Dictionary.'),
                'link': u'https://en.oxforddictionaries.com/definition/male'
            }
        ],
    },
    'infant': {
        'key': 'infant',
        'description': tr(
            'A very young child or baby.'),
        'citations': [
            {
                'text': tr(
                    'Oxford Dictionary.'),
                'link': u'https://en.oxforddictionaries.com/definition/infant'
            }
        ],
    },
    'disabled': {
        'key': 'disabled',
        'description': tr(
            'A person having a physical or mental condition that limits their '
            'movements, senses, or activities.'),
        'citations': [
            {
                'text': tr(
                    'Oxford Dictionary.'),
                'link': u'https://en.oxforddictionaries.com/definition/'
                        u'disabled'
            }
        ],
    },
    'pregnant': {
        'key': 'pregnant',
        'description': tr(
            'A female having a child developing in the uterus.'),
        'citations': [
            {
                'text': tr(
                    'Oxford Dictionary.'),
                'link': u'https://en.oxforddictionaries.com/definition/'
                        u'pregnant'
            }
        ],
    },
    'rice': {
        'key': 'rice',
        'description': tr(
            'Grains of rice used as food.'),
        'citations': [
            {
                'text': tr(
                    'Oxford Dictionary.'),
                'link': u'https://en.oxforddictionaries.com/definition/rice'
            }
        ],
    },
    'drinking_water': {
        'key': 'drinking_water',
        'description': tr(
            'Water pure enough for drinking.'),
        'citations': [
            {
                'text': tr(
                    'Oxford Dictionary.'),
                'link': u'https://en.oxforddictionaries.com/definition/'
                        u'drinking_water'
            }
        ],
    },
    'clean_water': {
        'key': 'clean_water',
        'description': tr(
            'Water suitable for washing and other purposes but not suitable '
            'for drinking.'),
        'citations': [
            {
                'text': tr(
                    ''),
                'link': u''
            }
        ],
    },
    'family_kit': {
        'key': 'family_kit',
        'description': tr(
            'Relief supplies such as clothing to support families.'),
        'citations': [
            {
                'text': tr(
                    'BNPB Perka 7/2008'),
                'link': u'http://tinyurl.com/BNPB-Perka-7-2008'
            }
        ],
    },
    'hygiene_pack': {
        'key': 'hygiene_pack',
        'description': tr(
            'Relief supplies to promote practices conducive to maintaining '
            'health and preventing disease.'),
        'citations': [
            {
                'text': tr(
                    'Oxford Dictionary.'),
                'link': u'https://en.oxforddictionaries.com/definition/hygiene'
            }
        ],
    },
    'toilet': {
        'key': 'toilet',
        'description': tr(
            'A room, building or cubicle with facilities to collect and '
            'dispose of human waste.'),
        'citations': [
            {
                'text': tr(
                    'Oxford Dictionary.'),
                'link': u'https://en.oxforddictionaries.com/definition/'
                        u'toilet'
            }
        ],
    },
    'thresholds': {
        'key': 'thresholds',
        'description': tr(
            'A range that defined with minimum and maximum value. In InaSAFE '
            'we exclude the minimum value but include the maximum value. In '
            'mathematical expression: minimum value < x <= maximum value. It '
            'is used for doing classification for continuous data.'),
        'citations': [
            {
                'text': '',
                'link': u''
            }
        ],
    },
    'value_maps': {
        'key': 'value_maps',
        'description': tr(
            'A conceptual mapping between one set of unique values and '
            'another set of unique values. Each unique value represents a '
            'particular class. It is used to express terms or concepts from '
            'one classification system in another classification system and '
            'only applies to non-continuous data. For example a value map can '
            'be used to express local names for entities (e.g.street type: '
            '"jalan") into generic concepts (e.g.street type: "residential").'
        ),
        'citations': [
            {
                'text': '',
                'link': u''
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
