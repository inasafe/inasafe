# coding=utf-8

"""Postprocessors about population and demographics."""

from collections import OrderedDict

from safe.definitions.concepts import concepts
from safe.definitions.exposure import exposure_population
from safe.definitions.hazard import hazard_earthquake
# Displaced field
from safe.definitions.fields import (
    child_bearing_age_displaced_count_field,
    pregnant_displaced_count_field,
    lactating_displaced_count_field,
    infant_displaced_count_field,
    child_displaced_count_field,
    youth_displaced_count_field,
    adult_displaced_count_field,
    elderly_displaced_count_field,
    under_5_displaced_count_field,
    over_60_displaced_count_field,
    disabled_displaced_count_field)
# Count fields
from safe.definitions.fields import (
    displaced_field,
    fatalities_field,
    female_displaced_count_field,
    population_count_field,
    exposure_count_field,
    male_displaced_count_field,
    hygiene_packs_count_field,
)
# Other fields
from safe.definitions.fields import hazard_class_field
# Ratio fields
from safe.definitions.fields import (
    population_displacement_ratio_field,
    population_fatality_ratio_field,
    child_bearing_age_ratio_field,
    lactating_ratio_field,
    pregnant_ratio_field,
    female_ratio_field,
    male_ratio_field,
    infant_ratio_field,
    child_ratio_field,
    youth_ratio_field,
    adult_ratio_field,
    elderly_ratio_field,
    under_5_ratio_field,
    over_60_ratio_field,
    disabled_ratio_field,
)
from safe.definitions.hazard_classifications import earthquake_mmi_scale
from safe.processors import (
    function_process,
    formula_process,
)
from safe.processors.post_processor_functions import (
    multiply,
    post_processor_population_displacement_function,
    post_processor_population_fatality_function,
)
from safe.processors.post_processor_inputs import (
    constant_input_type,
    field_input_type,
    keyword_input_type,
    dynamic_field_input_type,
    keyword_value_expected,
)
from safe.utilities.i18n import tr

# A postprocessor can be defined with a formula or with a python function.

post_processor_displaced_ratio = {
    'key': 'post_processor_displacement_ratio',
    'name': tr('Population Displacement Ratio Post Processor'),
    'description': tr(
        'A post processor to add the population displacement ratio according '
        'to the hazard class'),
    'run_filter': {
        'exposure': [exposure_population['key']]
    },
    'input': {
        'hazard': {
            'type': keyword_input_type,
            'value': ['hazard_keywords', 'hazard']
        },
        # Taking hazard classification
        'classification': {
            'type': keyword_input_type,
            'value': ['hazard_keywords', 'classification']
        },
        'hazard_class': {
            'type': field_input_type,
            'value': hazard_class_field,
        },
        'population': [
            # No one of these fields are used in this postprocessor.
            # But we put them as a condition for the postprocessor to run.
            {
                'value': population_count_field,
                'type': field_input_type,
            },
            {
                'value': exposure_count_field,
                'field_param': exposure_population['key'],
                'type': dynamic_field_input_type,
            }],
    },
    'output': {
        'population_displacement_ratio': {
            'value': population_displacement_ratio_field,
            'type': function_process,
            'function': post_processor_population_displacement_function
        }
    }
}

post_processor_displaced = {
    'key': 'post_processor_displacement',
    'name': tr('Displaced Post Processor'),
    'description': tr(
        'A post processor to calculate the number of displaced people. '
        '"Displaced" is defined as: {displaced_concept}').format(
        displaced_concept=concepts['displaced_people']['description']),
    'run_filter': {
        'exposure': [exposure_population['key']]
    },
    'input': {
        # input as a list means, try to get the input from the
        # listed source. Pick the first available
        'population': [
            {
                'value': population_count_field,
                'type': field_input_type,
            },
            {
                'value': exposure_count_field,
                'field_param': exposure_population['key'],
                'type': dynamic_field_input_type,
            }],
        'fatalities': [
            {
                'type': field_input_type,
                'value': fatalities_field,
            },
            {
                'type': constant_input_type,
                'value': 0,  # If no fatality field, we take 0 for the formula.
            }
        ],
        'displacement_ratio': {
            'type': field_input_type,
            'value': population_displacement_ratio_field
        }
    },
    'output': {
        'displaced': {
            'value': displaced_field,
            'type': formula_process,
            'formula': '(population - fatalities) * displacement_ratio'
        }
    }
}


post_processor_fatality_ratio = {
    'key': 'post_processor_fatality_ratio',
    'name': tr('Population Fatality Ratio Post Processor'),
    'description': tr(
        'A post processor to add the population fatality ratio according '
        'to the hazard class. Only the MMI classification has a fatality '
        'model.'),
    'run_filter': {
        'exposure': [exposure_population['key']],
        'hazard': [hazard_earthquake['key']]
    },
    'input': {
        # Taking hazard classification
        'classification': {
            'type': keyword_input_type,
            'value': ['hazard_keywords', 'classification']
        },
        'hazard_class': {
            'type': field_input_type,
            'value': hazard_class_field,
        },
        'population': [
            # No one of these fields are used in this postprocessor.
            # But we put them as a condition for the postprocessor to run.
            {
                'value': population_count_field,
                'type': field_input_type,
            },
            {
                'value': exposure_count_field,
                'field_param': exposure_population['key'],
                'type': dynamic_field_input_type,
            }],
        'earthquake_hazard': {
            'type': keyword_value_expected,
            'value': ['hazard_keywords', 'classification'],
            'expected_value': earthquake_mmi_scale['key']
        },
    },
    'output': {
        'fatality_ratio': {
            'value': population_fatality_ratio_field,
            'type': function_process,
            'function': post_processor_population_fatality_function
        }
    }
}

post_processor_fatalities = {
    'key': 'post_processor_fatalities',
    'name': tr('Fatalities Post Processor'),
    'description': tr(
        'A post processor to calculate the number of fatalities. '),
    'run_filter': {
        'exposure': [exposure_population['key']]
    },
    'input': {
        # input as a list means, try to get the input from the
        # listed source. Pick the first available
        'population': [
            {
                'value': population_count_field,
                'type': field_input_type,
            },
            {
                'value': exposure_count_field,
                'field_param': exposure_population['key'],
                'type': dynamic_field_input_type,
            }],
        'fatality_ratio': {
            'type': field_input_type,
            'value': population_fatality_ratio_field
        },
    },
    'output': {
        'fatalities': {
            'value': fatalities_field,
            'type': formula_process,
            'formula': 'population * fatality_ratio'
        }
    }
}

#
# Demographics post processors
#

post_processor_child_bearing_age = {
    'key': 'post_processor_child_bearing_age',
    'name': tr('Child Bearing Age Post Processor'),
    'description': tr(
        'A post processor to calculate the number of displaced child bearing '
        'age. "Child Bearing Age" is defined as: {child_bearing_age_concept} '
        '"Displaced" is defined as: '
        '{displaced_concept}').format(
        child_bearing_age_concept=concepts[
            'child_bearing_age']['description'],
        displaced_concept=concepts['displaced_people']['description']),
    'run_filter': {
        'exposure': [exposure_population['key']]
    },
    'input': {
        'population_displaced': {
            'value': displaced_field,
            'type': field_input_type,
        },
        # input as a list means, try to get the input from the
        # listed source. Pick the first available
        'child_bearing_age_ratio': [
            {
                'value': child_bearing_age_ratio_field,
                'type': field_input_type
            },
            {
                'type': keyword_input_type,
                'value': [
                    'inasafe_default_values',
                    child_bearing_age_ratio_field['key'],
                ],
            }
        ]
    },
    'output': {
        'child_bearing_age_displaced': {
            'value': child_bearing_age_displaced_count_field,
            'type': function_process,
            'function': multiply
        }
    }
}

post_processor_pregnant = {
    'key': 'post_processor_pregnant',
    'name': tr('Pregnant Post Processor'),
    'description': tr(
        'A post processor to calculate the number of displaced pregnant '
        'women. "Pregnant" is defined as: {pregnant_concept} "Displaced" is '
        'defined as: {displaced_concept}').format(
        pregnant_concept=concepts[
            'pregnant']['description'],
        displaced_concept=concepts['displaced_people']['description']),
    'run_filter': {
        'exposure': [exposure_population['key']]
    },
    'input': {
        'population_displaced': {
            'value': displaced_field,
            'type': field_input_type,
        },
        # input as a list means, try to get the input from the
        # listed source. Pick the first available
        'pregnant_ratio': [
            {
                'value': pregnant_ratio_field,
                'type': field_input_type
            },
            {
                'type': keyword_input_type,
                'value': [
                    'inasafe_default_values',
                    pregnant_ratio_field['key'],
                ],
            }
        ]
    },
    'output': {
        'pregnant_displaced': {
            'value': pregnant_displaced_count_field,
            'type': function_process,
            'function': multiply
        }
    }
}
post_processor_lactating = {
    'key': 'post_processor_lactating',
    'name': tr('Lactating Women Post Processor'),
    'description': tr(
        'A post processor to calculate the number of displaced lactating '
        'women. "Lactating" is defined as: {lactating_concept} "Displaced" is '
        'defined as: {displaced_concept}').format(
        lactating_concept=concepts[
            'lactating']['description'],
        displaced_concept=concepts['displaced_people']['description']),
    'run_filter': {
        'exposure': [exposure_population['key']]
    },
    'input': {
        'population_displaced': {
            'value': displaced_field,
            'type': field_input_type,
        },
        # input as a list means, try to get the input from the
        # listed source. Pick the first available
        'lactating_lactating_ratio': [
            {
                'value': lactating_ratio_field,
                'type': field_input_type
            },
            {
                'type': keyword_input_type,
                'value': [
                    'inasafe_default_values',
                    lactating_ratio_field['key'],
                ],
            }
        ]
    },
    'output': {
        'lactating_displaced': {
            'value': lactating_displaced_count_field,
            'type': function_process,
            'function': multiply
        }
    }
}

post_processor_male = {
    'key': 'post_processor_male',
    'name': tr('Male Post Processor'),
    'description': tr(
        'A post processor to calculate the number of displaced males.'
        '"Male" is defined as: {male_concept}. "Displaced" is defined as: '
        '{displaced_concept}').format(
        male_concept=concepts['male']['description'],
        displaced_concept=concepts['displaced_people']['description']),
    'run_filter': {
        'exposure': [exposure_population['key']]
    },
    'input': {
        'population_displaced': {
            'value': displaced_field,
            'type': field_input_type,
        },
        # input as a list means, try to get the input from the
        # listed source. Pick the first available
        'male_ratio': [
            {
                'value': male_ratio_field,
                'type': field_input_type
            },
            {
                'type': keyword_input_type,
                'value': [
                    'inasafe_default_values',
                    male_ratio_field['key'],
                ],
            }]
    },
    # output is described as ordered dict because the order is important
    # and the postprocessor produce two fields.
    'output': OrderedDict([
        ('males_displaced', {
            'value': male_displaced_count_field,
            'type': formula_process,
            'formula': 'population_displaced * male_ratio'
        })
    ])
}
post_processor_female = {
    'key': 'post_processor_female',
    'name': tr('Female Post Processor'),
    'description': tr(
        'A post processor to calculate the number of displaced females.'
        '"Female" is defined as: {female_concept}. "Displaced" is defined as: '
        '{displaced_concept}').format(
        female_concept=concepts['female']['description'],
        displaced_concept=concepts['displaced_people']['description']),
    'run_filter': {
        'exposure': [exposure_population['key']]
    },
    'input': {
        'population_displaced': {
            'value': displaced_field,
            'type': field_input_type,
        },
        # input as a list means, try to get the input from the
        # listed source. Pick the first available
        'female_ratio': [
            {
                'value': female_ratio_field,
                'type': field_input_type
            },
            {
                'type': keyword_input_type,
                'value': [
                    'inasafe_default_values',
                    female_ratio_field['key'],
                ],
            }]
    },
    # output is described as ordered dict because the order is important
    # and the postprocessor produce two fields.
    'output': OrderedDict([
        ('female_displaced', {
            'value': female_displaced_count_field,
            'type': formula_process,
            'formula': 'population_displaced * female_ratio'
        })
    ])
}
post_processor_hygiene_packs = {
    'key': 'post_processor_hygiene_packs',
    'name': tr('Weekly Hygiene Packs Post Processor'),
    'description': tr(
        'A post processor to calculate needed hygiene packs weekly for women '
        'who are displaced. "Displaced" is defined as: '
        '{displaced_concept}').format(
            displaced_concept=concepts['displaced_people']['description']),
    'run_filter': {
        'exposure': [exposure_population['key']]
    },
    'input': {
        'female_displaced':
            {
                'value': female_displaced_count_field,
                'type': field_input_type,
            },
        'hygiene_packs_ratio':
            {
                'type': constant_input_type,
                'value': 0.7937,
            }
    },
    'output': {
        # The formula:
        # displaced_female * 0.7937 * (week/intended_day_use)
        'hygiene_packs': {
            'value': hygiene_packs_count_field,
            'type': function_process,
            'function': multiply
        },
    }
}
post_processor_infant = {
    'key': 'post_processor_infant',
    'name': tr('Infant Post Processor'),
    'description': tr(
        'A post processor to calculate the number of displaced infant. '
        '"Infant" is defined as: {infant_concept} "Displaced" is defined as: '
        '{displaced_concept}').format(
            infant_concept=concepts['infant']['description'],
            displaced_concept=concepts['displaced_people']['description']),
    'run_filter': {
        'exposure': [exposure_population['key']]
    },
    'input': {
        'population_displaced': {
            'value': displaced_field,
            'type': field_input_type,
        },
        # input as a list means, try to get the input from the
        # listed source. Pick the first available
        'infant_ratio': [
            {
                'value': infant_ratio_field,
                'type': field_input_type
            },
            {
                'type': keyword_input_type,
                'value': [
                    'inasafe_default_values',
                    infant_ratio_field['key'],
                ],
            }
        ]
    },
    'output': {
        'infant_displaced': {
            'value': infant_displaced_count_field,
            'type': function_process,
            'function': multiply
        }
    }
}
post_processor_child = {
    'key': 'post_processor_child',
    'name': tr('Child Post Processor'),
    'description': tr(
        'A post processor to calculate the number of displaced child. '
        '"Child" is defined as: {child_concept} "Displaced" is defined as: '
        '{displaced_concept}').format(
            child_concept=concepts['child']['description'],
            displaced_concept=concepts['displaced_people']['description']),
    'run_filter': {
        'exposure': [exposure_population['key']]
    },
    'input': {
        'population_displaced': {
            'value': displaced_field,
            'type': field_input_type,
        },
        # input as a list means, try to get the input from the
        # listed source. Pick the first available
        'child_ratio': [
            {
                'value': child_ratio_field,
                'type': field_input_type
            },
            {
                'type': keyword_input_type,
                'value': [
                    'inasafe_default_values',
                    child_ratio_field['key'],
                ],
            }
        ]
    },
    'output': {
        'child_displaced': {
            'value': child_displaced_count_field,
            'type': function_process,
            'function': multiply
        }
    }
}
post_processor_youth = {
    'key': 'post_processor_youth',
    'name': tr('Youth Post Processor'),
    'description': tr(
        'A post processor to calculate the number of displaced youth. '
        '"Youth" is defined as: {youth_concept} "Displaced" is defined as: '
        '{displaced_concept}').format(
            youth_concept=concepts['youth']['description'],
            displaced_concept=concepts['displaced_people']['description']),
    'run_filter': {
        'exposure': [exposure_population['key']]
    },
    'input': {
        'population_displaced': {
            'value': displaced_field,
            'type': field_input_type,
        },
        # input as a list means, try to get the input from the
        # listed source. Pick the first available
        'youth_ratio': [
            {
                'value': youth_ratio_field,
                'type': field_input_type
            },
            {
                'type': keyword_input_type,
                'value': [
                    'inasafe_default_values',
                    youth_ratio_field['key'],
                ],
            }
        ]
    },
    'output': {
        'youth_displaced': {
            'value': youth_displaced_count_field,
            'type': function_process,
            'function': multiply
        }
    }
}
post_processor_adult = {
    'key': 'post_processor_adult',
    'name': tr('Adult Post Processor'),
    'description': tr(
        'A post processor to calculate the number of displaced adults. '
        '"Adult" is defined as: {adult_concept}. "Displaced" is defined as: '
        '{displaced_concept}').format(
            adult_concept=concepts['adult']['description'],
            displaced_concept=concepts['displaced_people']['description']),
    'run_filter': {
        'exposure': [exposure_population['key']]
    },
    'input': {
        'population_displaced': {
            'value': displaced_field,
            'type': field_input_type,
        },
        # input as a list means, try to get the input from the
        # listed source. Pick the first available
        'adult_ratio': [
            {
                'value': adult_ratio_field,
                'type': field_input_type
            },
            {
                'type': keyword_input_type,
                'value': [
                    'inasafe_default_values',
                    adult_ratio_field['key'],
                ],
            }
        ]
    },
    'output': {
        'adult_displaced': {
            'value': adult_displaced_count_field,
            'type': function_process,
            'function': multiply
        }
    }
}
post_processor_elderly = {
    'key': 'post_processor_elderly',
    'name': tr('Elderly Post Processor'),
    'description': tr(
        'A post processor to calculate the number of displaced elderly '
        'people. "Elderly" is defined as: {elderly_concept}. "Displaced" is '
        'defined as: {displaced_concept}').format(
            elderly_concept=concepts['elderly']['description'],
            displaced_concept=concepts['displaced_people']['description']),
    'run_filter': {
        'exposure': [exposure_population['key']]
    },
    'input': {
        'population_displaced': {
            'value': displaced_field,
            'type': field_input_type,
        },
        # input as a list means, try to get the input from the
        # listed source. Pick the first available
        'elderly_ratio': [
            {
                'value': elderly_ratio_field,
                'type': field_input_type
            },
            {
                'type': keyword_input_type,
                'value': [
                    'inasafe_default_values',
                    elderly_ratio_field['key'],
                ],
            }
        ]
    },
    'output': {
        'elderly_displaced': {
            'value': elderly_displaced_count_field,
            'type': function_process,
            'function': multiply
        }
    }
}
post_processor_under_5 = {
    'key': 'post_processor_under_5',
    'name': tr('Under 5 Years Old Post Processor'),
    'description': tr(
        'A post processor to calculate the number of displaced under 5 '
        'years old. "Under 5 Years Old" is defined as: {under_5_concept}. '
        '"Displaced" is defined as: {displaced_concept}').format(
        under_5_concept=concepts['under_5']['description'],
        displaced_concept=concepts['displaced_people']['description']),
    'run_filter': {
        'exposure': [exposure_population['key']]
    },
    'input': {
        'population_displaced': {
            'value': displaced_field,
            'type': field_input_type,
        },
        # input as a list means, try to get the input from the
        # listed source. Pick the first available
        'under_5_ratio': [
            {
                'value': under_5_ratio_field,
                'type': field_input_type
            },
            {
                'type': keyword_input_type,
                'value': [
                    'inasafe_default_values',
                    under_5_ratio_field['key'],
                ],
            }
        ]
    },
    'output': {
        'under_5_displaced': {
            'value': under_5_displaced_count_field,
            'type': function_process,
            'function': multiply
        }
    }
}
post_processor_over_60 = {
    'key': 'post_processor_over_60',
    'name': tr('Over 60 Years Old Post Processor'),
    'description': tr(
        'A post processor to calculate the number of displaced over 60 '
        'years old. "Over 60 Years Old" is defined as: {over_60_concept}. '
        '"Displaced" is defined as: {displaced_concept}').format(
        over_60_concept=concepts['over_60']['description'],
        displaced_concept=concepts['displaced_people']['description']),
    'run_filter': {
        'exposure': [exposure_population['key']]
    },
    'input': {
        'population_displaced': {
            'value': displaced_field,
            'type': field_input_type,
        },
        # input as a list means, try to get the input from the
        # listed source. Pick the first available
        'over_60_ratio': [
            {
                'value': over_60_ratio_field,
                'type': field_input_type
            },
            {
                'type': keyword_input_type,
                'value': [
                    'inasafe_default_values',
                    over_60_ratio_field['key'],
                ],
            }
        ]
    },
    'output': {
        'over_60_displaced': {
            'value': over_60_displaced_count_field,
            'type': function_process,
            'function': multiply
        }
    }
}
post_processor_disability_vulnerability = {
    'key': 'post_processor_disability_vulnerability',
    'name': tr('Disability Vulnerability Post Processor'),
    'description': tr(
        'A post processor to calculate the number of displaced people '
        'who are especially vulnerable because they have disabilities. '
        '"Disabled" is defined as: {disabled_concept}. '
        '"Displaced" is defined as: {displaced_concept}').format(
        disabled_concept=concepts['disabled']['description'],
        displaced_concept=concepts['displaced_people']['description']),
    'run_filter': {
        'exposure': [exposure_population['key']]
    },
    'input': {
        'population_displaced': {
            'value': displaced_field,
            'type': field_input_type,
        },
        # input as a list means, try to get the input from the
        # listed source. Pick the first available
        'over_60_ratio': [
            {
                'value': disabled_ratio_field,
                'type': field_input_type
            },
            {
                'type': keyword_input_type,
                'value': [
                    'inasafe_default_values',
                    disabled_ratio_field['key'],
                ],
            }
        ]
    },
    'output': {
        'over_60_displaced': {
            'value': disabled_displaced_count_field,
            'type': function_process,
            'function': multiply
        }
    }
}

female_postprocessors = [
    post_processor_hygiene_packs
]
age_postprocessors = [
    post_processor_infant,
    post_processor_child,
    post_processor_youth,
    post_processor_adult,
    post_processor_elderly,
]
gender_postprocessors = [
    post_processor_male,
    post_processor_female
]
age_vulnerability_postprocessors = [
    post_processor_under_5,
    post_processor_over_60,
]
gender_vulnerability_postprocessors = [
    post_processor_child_bearing_age,
    post_processor_pregnant,
    post_processor_lactating
]
disabled_vulnerability_postprocessors = [
    post_processor_disability_vulnerability
]

all_population_post_processors = (
    female_postprocessors
    + age_postprocessors
    + gender_postprocessors
    + age_vulnerability_postprocessors
    + gender_vulnerability_postprocessors
    + disabled_vulnerability_postprocessors
) + [
    post_processor_displaced_ratio,
    post_processor_displaced,
    post_processor_fatality_ratio,
    post_processor_fatalities,
]

# Adding requirement for exposure = population, beside exposed population
# post processor
population_exposure_filter = {
    'exposure': [exposure_population['key']]
}
for pp in all_population_post_processors:
    try:
        pp['run_filter'].update(population_exposure_filter)
    except KeyError:
        pp['run_filter'] = population_exposure_filter
