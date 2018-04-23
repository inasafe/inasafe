# coding=utf-8
"""Concepts used in various places in InaSAFE.

Where possible please supply citations. Concepts are used in reporting display
and in other places like the wizard to ensure that the user will have adequate
contextual information to accompany the data shown to them.
"""

from collections import OrderedDict

from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

concepts = OrderedDict()
concepts['analysis'] = {
    'group': tr('Basic concepts'),
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
            'link': ''
        }
    ],
}
concepts['hazard'] = {
    'group': tr('Basic concepts'),
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
            'link': 'https://www.unisdr.org/we/inform/terminology'
        }
    ],
}
concepts['generic_hazard'] = {
    'group': tr('Basic concepts'),
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
            'link': ''
        }
    ],
}
concepts['exposure'] = {
    'group': tr('Basic concepts'),
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
            'link': 'https://www.unisdr.org/we/inform/terminology'
        }
    ],
}
concepts['affected'] = {
    'group': tr('Basic concepts'),
    'key': 'affected',
    'name': tr('Affected'),
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
}
concepts['exposed_people'] = {
    'group': tr('Basic concepts'),
    'key': 'exposed_people',
    'name': tr('Exposed People'),
    'description': tr(
        'People who are present in hazard zones and are thereby subject '
        'to potential losses. In InaSAFE, people who are exposed are '
        'those people who are within the extent of the hazard.'),
    'citations': [
        {
            'text': tr(
                'UNISDR (2009)Terminology on Disaster'),
            'link': 'https://www.unisdr.org/we/inform/terminology'
        }
    ],
}
concepts['affected_people'] = {
    'group': tr('Basic concepts'),
    'key': 'affected_people',
    'name': tr('Affected People'),
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
            'link': 'http://www.preventionweb.net/files/'
                    '45462_backgoundpaperonterminologyaugust20.pdf'
        }
    ],
}
concepts['directly_affected_people'] = {
    'group': tr('Basic concepts'),
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
            'link': 'http://www.preventionweb.net/files/'
                    '45462_backgoundpaperonterminologyaugust20.pdf'
        }
    ],
}
concepts['indirectly_affected_people'] = {
    'group': tr('Basic concepts'),
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
            'link': 'http://www.preventionweb.net/files/'
                    '45462_backgoundpaperonterminologyaugust20.pdf'
        }
    ],
}
concepts['displaced_people'] = {
    'group': tr('Basic concepts'),
    'key': 'displaced_people',
    'name': tr('Displaced People'),
    'description': tr(
        'Displaced people are people who, for different reasons and '
        'circumstances because of risk or disaster, have to leave their '
        'place of residence. In InaSAFE, demographic and minimum '
        'needs reports are based on displaced / evacuated people.'),
    'citations': [
        {
            'text': tr(
                'UNISDR (2015)Proposed Updated Terminology on Disaster '
                'Risk Reduction: A Technical Review'),
            'link': 'http://www.preventionweb.net/files/'
                    '45462_backgoundpaperonterminologyaugust20.pdf'
        }
    ],
}
concepts['displacement_rate'] = {
    'group': tr('Basic concepts'),
    'key': 'displacement_rate',
    'name': tr('Displacement rate'),
    'description': tr(
        'The population displacement ratio for a given hazard class.'),
    'citations': [
        {
            'text': '',
            'link': ''
        }
    ],
}
concepts['evacuated_people'] = {
    'group': tr('Basic concepts'),
    'key': 'evacuated_people',
    'description': tr(
        'Evacuated people are people who, for different reasons and '
        'circumstances because of risk conditions or disaster, move '
        'temporarily to safer places before, during or after the '
        'occurrence of a hazardous event. Evacuation can occur from '
        'places of residence, workplaces, schools and hospitals to other '
        'places. Evacuation is usually a planned and organised '
        'mobilisation of persons, animals and goods for eventual return. '
        'In InaSAFE, demographic and minimum needs reports are based on '
        'displaced / evacuated people.'),
    'citations': [
        {
            'text': tr(
                'UNISDR (2015)Proposed Updated Terminology on Disaster '
                'Risk Reduction: A Technical Review'),
            'link': 'http://www.preventionweb.net/files/'
                    '45462_backgoundpaperonterminologyaugust20.pdf'
        }
    ],
}
concepts['relocated_people'] = {
    'group': tr('Basic concepts'),
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
            'link': 'http://www.preventionweb.net/files/'
                    '45462_backgoundpaperonterminologyaugust20.pdf'
        }
    ],
}
concepts['injured_people'] = {
    'group': tr('Basic concepts'),
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
            'link': 'http://www.preventionweb.net/files/'
                    '45462_backgoundpaperonterminologyaugust20.pdf'
        }
    ],
}
concepts['killed_people'] = {
    'group': tr('Basic concepts'),
    'key': 'killed_people',
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
}

concepts['female'] = {
    'group': tr('Gender'),
    'key': 'female',
    'description': tr(
        'Relating to the characteristics of women.'),
    'citations': [
        {
            'text': tr(
                'Oxford Dictionary.'),
            'link': 'https://en.oxforddictionaries.com/definition/female'
        }
    ],
}
concepts['male'] = {
    'group': tr('Gender'),
    'key': 'male',
    'description': tr(
        'Relating to the characteristics of men.'),
    'citations': [
        {
            'text': tr(
                'Oxford Dictionary.'),
            'link': 'https://en.oxforddictionaries.com/definition/male'
        }
    ],
}
concepts['people'] = {
    'group': tr('Demographics'),
    'key': 'people',
    'description': tr(
        'Human beings in general or considered collectively.'),
    'citations': [
        {
            'text': tr(
                'Oxford Dictionary.'),
            'link': 'https://en.oxforddictionaries.com/definition/people'
        }
    ],
}
concepts['infant'] = {
    'group': tr('Demographics'),
    'key': 'infant',
    'description': tr(
        'A very young child or baby aged between 0 and 4 years.'),
    'citations': [
        {
            'text': tr(
                'Oxford Dictionary.'),
            'link': 'https://en.oxforddictionaries.com/definition/infant'
        },
        {
            'text': tr(
                'World Population Dashboard. '
                'ICPD Goals and Demographic Indicators 2016.'),
            'link': 'http://www.unfpa.org/world-population-dashboard'
        }
    ],
}
concepts['child'] = {
    'group': tr('Demographics'),
    'key': 'child',
    'description': tr(
        'A young person aged between 5 and 14 years, usually below the '
        'age of puberty.'),
    'citations': [
        {
            'text': tr(
                'Oxford Dictionary.'),
            'link': 'https://en.oxforddictionaries.com/definition/child'
        },
        {
            'text': tr(
                'World Population Dashboard. '
                'ICPD Goals and Demographic Indicators 2016.'),
            'link': 'http://www.unfpa.org/world-population-dashboard'
        }
    ],
}
concepts['youth'] = {
    'group': tr('Demographics'),
    'key': 'youth',
    'description': tr(
        'A person aged between 0 and 14 years.'),
    'citations': [
        {
            'text': tr(
                'World Population Dashboard. '
                'ICPD Goals and Demographic Indicators 2016.'),
            'link': 'http://www.unfpa.org/world-population-dashboard'
        }
    ],
}
concepts['adult'] = {
    'group': tr('Demographics'),
    'key': 'adult',
    'description': tr(
        'Person aged between 15 and 64 years, usually of working age.'),
    'citations': [
        {
            'text': tr(
                'World Population Dashboard. '
                'ICPD Goals and Demographic Indicators 2016.'),
            'link': 'http://www.unfpa.org/world-population-dashboard'
        }
    ],
}
concepts['elderly'] = {
    'group': tr('Demographics'),
    'key': 'elderly',
    'description': tr(
        'Persons aged 65 years and over.'),
    'citations': [
        {
            'text': tr(
                'World Population Dashboard. '
                'ICPD Goals and Demographic Indicators 2016.'),
            'link': 'http://www.unfpa.org/world-population-dashboard'
        }
    ],
}
concepts['disabled'] = {
    'group': tr('Vulnerability'),
    'key': 'disabled',
    'description': tr(
        'A person having a physical or mental condition that limits their '
        'movements, senses, or activities.'),
    'citations': [
        {
            'text': tr(
                'Oxford Dictionary.'),
            'link': 'https://en.oxforddictionaries.com/definition/'
                    'disabled'
        },
        {
            'text': tr(
                'World Report on Disability.'),
            'link': 'http://www.who.int/disabilities/world_report/2011/'
                    'report.pdf'
        }
    ],
}
concepts['under_5'] = {
    'group': tr('Vulnerability'),
    'key': 'under_5',
    'description': tr(
        'Persons aged under 5 years'),
    'citations': [
        {
            'text': tr(
                'World Population Dashboard. '
                'ICPD Goals and Demographic Indicators 2016.'),
            'link': 'http://www.unfpa.org/world-population-dashboard'
        }
    ],
}
concepts['over_60'] = {
    'group': tr('Vulnerability'),
    'key': 'over_60',
    'description': tr(
        'Persons aged 60 years and over'),
    'citations': [
        {
            'text': tr('World Population Aging 2013'),
            'link': 'http://www.un.org/en/development/desa/population/'
                    'publications/pdf/ageing/WorldPopulationAgeing2013.pdf'
        }
    ],
}
concepts['child_bearing_age'] = {
    'group': tr('Vulnerability'),
    'key': 'child_bearing_age',
    'description': tr(
        'The span of ages (usually 15-49) at which individuals are capable '
        'of becoming parents. The phrase can be applied to men and women '
        'but most frequently refers to women.'),
    'citations': [
        {
            'text': tr('UNFPA One Voice'),
            'link': 'https://onevoice.unfpa.org/'
                    'index.unfpa?method=article&id=66'
        }
    ],
}
concepts['pregnant'] = {
    'group': tr('Vulnerability'),
    'key': 'pregnant',
    'description': tr(
        'A female having a child developing in the uterus.'),
    'citations': [
        {
            'text': tr(
                'Oxford Dictionary.'),
            'link': 'https://en.oxforddictionaries.com/definition/'
                    'pregnant'
        }
    ],
}
concepts['lactating'] = {
    'group': tr('Vulnerability'),
    'key': 'lactating',
    'description': tr(
        'A female producing milk to feed a baby.'),
    'citations': [
        {
            'text': tr(
                'Oxford Dictionary.'),
            'link': 'https://en.oxforddictionaries.com/definition/'
                    'lactate'
        }
    ],
}

concepts['rice'] = {
    'group': tr('Minimum needs'),
    'key': 'rice',
    'description': tr(
        'Grains of rice used as food.'),
    'citations': [
        {
            'text': tr(
                'Oxford Dictionary.'),
            'link': 'https://en.oxforddictionaries.com/definition/rice'
        }
    ],
}
concepts['drinking_water'] = {
    'group': tr('Minimum needs'),
    'key': 'drinking_water',
    'description': tr(
        'Water pure enough for drinking.'),
    'citations': [
        {
            'text': tr(
                'Oxford Dictionary.'),
            'link': 'https://en.oxforddictionaries.com/definition/'
                    'drinking_water'
        }
    ],
}
concepts['clean_water'] = {
    'group': tr('Minimum needs'),
    'key': 'clean_water',
    'description': tr(
        'Water suitable for washing and other purposes but not suitable '
        'for drinking.'),
    'citations': [
        {
            'text': tr(
                ''),
            'link': ''
        }
    ],
}
concepts['family_kit'] = {
    'group': tr('Minimum needs'),
    'key': 'family_kit',
    'description': tr(
        'Relief supplies such as clothing to support families.'),
    'citations': [
        {
            'text': tr(
                'BNPB Perka 7/2008'),
            'link': 'http://tinyurl.com/BNPB-Perka-7-2008'
        }
    ],
}
concepts['hygiene_pack'] = {
    'group': tr('Minimum needs'),
    'key': 'hygiene_pack',
    'description': tr(
        'Relief supplies to promote practices conducive to maintaining '
        'health and preventing disease.'),
    'citations': [
        {
            'text': tr(
                'Oxford Dictionary.'),
            'link': 'https://en.oxforddictionaries.com/definition/hygiene'
        }
    ],
}
concepts['toilet'] = {
    'group': tr('Minimum needs'),
    'key': 'toilet',
    'description': tr(
        'A room, building or cubicle with facilities to collect and '
        'dispose of human waste.'),
    'citations': [
        {
            'text': tr(
                'Oxford Dictionary.'),
            'link': 'https://en.oxforddictionaries.com/definition/'
                    'toilet'
        }
    ],
}
concepts['thresholds'] = {
    'group': tr('Data representation'),
    'key': 'thresholds',
    'description': tr(
        'A range defined with a minimum and maximum value. In InaSAFE '
        'we exclude the minimum value but include the maximum value. In '
        'mathematical expression: minimum value < x <= maximum value. It '
        'is used for doing classification of continuous data.'),
    'citations': [
        {
            'text': '',
            'link': ''
        }
    ],
}
concepts['value_maps'] = {
    'group': tr('Data representation'),
    'key': 'value_maps',
    'description': tr(
        'A conceptual mapping between one set of unique values and '
        'another set of unique values. Each unique value represents a '
        'particular class. It is used to express terms or concepts from '
        'one classification system in another classification system and '
        'only applies to non-continuous data. For example a value map can '
        'be used to express local names for entities (e.g.street type: '
        '"alley") into generic concepts (e.g.street type: "residential").'
    ),
    'citations': [
        {
            'text': '',
            'link': ''
        }
    ],
}
concepts['rounding_methodology'] = {
    'group': tr('Data representation'),
    'key': 'rounding_methodology',
    'description': tr(
        'Note that report rows containing totals are calculated from the '
        'entire analysis area totals and then rounded, whereas the '
        'subtotal rows are calculated from the aggregation areas and '
        'then rounded. Using this approach we avoid adding already '
        'rounded numbers and in so doing compounding the rounding.'),
    'citations': [
        {
            'text': '',
            'link': ''
        }
    ],
}
concepts['productivity_rate'] = {
    'group': tr('Productivity'),
    'key': 'productivity_rate',
    'name': tr('Productivity Rate'),
    'description': tr(
        'The weight of a crop from land cover can produce per area unit. The '
        'unit is in hundred kilograms /hectare.'),
    'citations': [
        {
            'text': '',
            'link': ''
        }
    ],
}
concepts['productivity'] = {
    'group': tr('Productivity'),
    'key': 'productivity',
    'name': tr('Productivity'),
    'description': tr(
        'The number of crop in hundred kilograms unit that can be produced in '
        'a land cover area.'),
    'citations': [
        {
            'text': '',
            'link': ''
        }
    ],
}
concepts['production_cost_rate'] = {
    'group': tr('Productivity'),
    'key': 'production_cost_rate',
    'name': tr('Production Cost Rate'),
    'description': tr(
        'The amount of money that is needed to build a crop land cover per '
        'area unit. The default unit is currency per area unit (e.g. '
        'IDR/hectare, USD/hectare).'),
    'citations': [
        {
            'text': '',
            'link': ''
        }
    ],
}
concepts['production_cost'] = {
    'group': tr('Productivity'),
    'key': 'production_cost',
    'name': tr('Production Cost'),
    'description': tr(
        'The amount of money that is needed to build a crop land cover area. '
        'The unit is a currency unit (e.g. IDR, USD, Euro).'),
    'citations': [
        {
            'text': '',
            'link': ''
        }
    ],
}
concepts['production_value_rate'] = {
    'group': tr('Productivity'),
    'key': 'production_value_rate',
    'name': tr('Production Value Rate'),
    'description': tr(
        'The price of a crop per area unit. The default unit is currency per '
        'area unit. (e.g. IDR/hectare, USD/hectare).'),
    'citations': [
        {
            'text': '',
            'link': ''
        }
    ],
}
concepts['production_value'] = {
    'group': tr('Productivity'),
    'key': 'production_value',
    'name': tr('Production Value'),
    'description': tr(
        'The price of a crop in a land cover area. The unit is a currency '
        'unit (e.g. IDR, USD, Euro).'),
    'citations': [
        {
            'text': '',
            'link': ''
        }
    ],
}
# Boilerplate for adding a new concept...
#  concepts[''] = {
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
