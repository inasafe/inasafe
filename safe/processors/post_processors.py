# coding=utf-8

# pylint: disable=pointless-string-statement
# This is disabled for typehinting docstring.

"""Definitions relating to post-processing."""

import logging

from safe.definitions.exposure import (
    exposure_place,
    exposure_structure
)
from safe.definitions.extra_keywords import (
    extra_keyword_earthquake_longitude,
    extra_keyword_earthquake_latitude
)
from safe.definitions.fields import (
    bearing_field,
    direction_field,
    distance_field,
    feature_rate_field,
    feature_value_field,
    size_field,
    hazard_class_field,
    affected_field,
    pcrafi_construction_class_id_field,
    pcrafi_minimum_floor_height_id_field,
    pcrafi_damage_ratio_output,
    pcrafi_damage_state_output,
    pcrafi_damage_state_0_count_field,
    pcrafi_damage_state_1_count_field,
    pcrafi_damage_state_2_count_field,
    pcrafi_damage_state_3_count_field,
    pcrafi_damage_state_4_count_field,
    pcrafi_damage_state_5_count_field,
)
from safe.definitions.hazard import (
    hazard_earthquake,
    hazard_flood,
)
from safe.definitions.hazard_classifications import not_exposed_class
from safe.processors.post_processor_functions import (
    calculate_bearing,
    calculate_cardinality,
    calculate_distance,
    multiply,
    size,
    post_processor_affected_function,
    post_processor_pcrafi_damage_ratio_function,
    post_processor_pcrafi_damage_state_function,
    post_processor_pcrafi_damage_state_function_factory,
    )
from safe.processors.post_processor_inputs import (
    geometry_property_input_type,
    layer_property_input_type,
    size_calculator_input_value,
    keyword_input_type,
    field_input_type,
    keyword_value_expected)
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


formula_process = {
    'key': 'formula',
    'description': tr(
        'This type of process is a formula which is interpreted and executed '
        'by the post processor.')
}

function_process = {
    'key': 'function',
    'description': tr(
        'This type of process takes inputs as arguments and processes them '
        'by passing them to a Python function.')
}


post_processor_process_types = [
    formula_process, function_process
]


post_processor_size = {
    'key': 'post_processor_size',
    'name': tr('Size Value Post Processor'),
    'description': tr(
        'A post processor to calculate the size of the feature. The unit is '
        'defined in the exposure definition.'),
    'input': {
        'size_calculator': {
            'type': layer_property_input_type,
            'value': size_calculator_input_value,
        },
        'geometry': {
            'type': geometry_property_input_type
        }
    },
    'output': {
        'size': {
            'value': size_field,
            'type': function_process,
            'function': size
        }
    }
}

post_processor_distance = {
    'key': 'post_processor_distance',
    'name': tr('Distance Post Processor'),
    'description': tr(
        'A post processor to calculate the distance between two points.'),
    'input': {
        'distance_calculator': {
            'type': layer_property_input_type,
            'value': size_calculator_input_value,
        },
        'place_geometry': {
            'type': geometry_property_input_type
        },
        'latitude': {
            'type': keyword_input_type,
            'value': [
                'hazard_keywords',
                'extra_keywords',
                extra_keyword_earthquake_latitude['key']
            ]
        },
        'longitude': {
            'type': keyword_input_type,
            'value': [
                'hazard_keywords',
                'extra_keywords',
                extra_keyword_earthquake_longitude['key']
            ]
        },
        'earthquake_hazard': {
            'type': keyword_value_expected,
            'value': ['hazard_keywords', 'hazard'],
            'expected_value': hazard_earthquake['key']
        },
        'place_exposure': {
            'type': keyword_value_expected,
            'value': ['exposure_keywords', 'exposure'],
            'expected_value': exposure_place['key']
        }
    },
    'output': {
        'size': {
            'value': distance_field,
            'type': function_process,
            'function': calculate_distance
        }
    }
}

post_processor_bearing = {
    'key': 'post_processor_bearing',
    'name': tr('Bearing Angle Post Processor'),
    'description': tr(
        'A post processor to calculate the bearing angle between two points.'
    ),
    'input': {
        'place_geometry': {
            'type': geometry_property_input_type
        },
        'latitude': {
            'type': keyword_input_type,
            'value': [
                'hazard_keywords',
                'extra_keywords',
                extra_keyword_earthquake_latitude['key']
            ]
        },
        'longitude': {
            'type': keyword_input_type,
            'value': [
                'hazard_keywords',
                'extra_keywords',
                extra_keyword_earthquake_longitude['key']
            ]
        },
        'earthquake_hazard': {
            'type': keyword_value_expected,
            'value': ['hazard_keywords', 'hazard'],
            'expected_value': hazard_earthquake['key']
        },
        'place_exposure': {
            'type': keyword_value_expected,
            'value': ['exposure_keywords', 'exposure'],
            'expected_value': exposure_place['key']
        }
    },
    'output': {
        'size': {
            'value': bearing_field,
            'type': function_process,
            'function': calculate_bearing
        }
    }
}

post_processor_cardinality = {
    'key': 'post_processor_cardinality',
    'name': tr('Cardinality Post Processor'),
    'description': tr(
        'A post processor to calculate the cardinality of an angle.'
    ),
    'input': {
        'angle': {
            'type': field_input_type,
            'value': bearing_field
        },
        'earthquake_hazard': {
            'type': keyword_value_expected,
            'value': ['hazard_keywords', 'hazard'],
            'expected_value': hazard_earthquake['key']
        },
        'place_exposure': {
            'type': keyword_value_expected,
            'value': ['exposure_keywords', 'exposure'],
            'expected_value': exposure_place['key']
        }
    },
    'output': {
        'size': {
            'value': direction_field,
            'type': function_process,
            'function': calculate_cardinality
        }
    }
}

post_processor_size_rate = {
    'key': 'post_processor_size_rate',
    'name': tr('Size Rate Post Processor'),
    'description': tr(
        'A post processor to calculate the value of a feature based on its '
        'size. If a feature is a polygon the size is calculated as '
        'the area in m². If the feature is a line we use length in metres.'),
    'input': {
        'size': {
            'type': field_input_type,
            'value': size_field,
        },
        'rate': {
            'value': feature_rate_field,
            'type': field_input_type
        }
    },
    'output': {
        'elderly': {
            'value': feature_value_field,
            'type': function_process,
            'function': multiply
        }
    }
}

# We can access a specific keyword by specifying a list of keys to reach the
# keyword.
# For instance ['hazard_keywords', 'classification'].

post_processor_affected = {
    'key': 'post_processor_affected',
    'name': tr('Affected Post Processor'),
    'description': tr(
        'A post processor to determine if a feature is affected or not '
        '(according to the hazard classification). It can be '
        '"{not_exposed_value}".').format(
            not_exposed_value=not_exposed_class['key']
    ),
    'input': {
        'hazard_class': {
            'value': hazard_class_field,
            'type': field_input_type,
        },
        'exposure': {
            'type': keyword_input_type,
            'value': ['exposure_keywords', 'exposure'],
        },
        'classification': {
            'type': keyword_input_type,
            'value': ['hazard_keywords', 'classification'],
        },
        'hazard': {
            'type': keyword_input_type,
            'value': ['hazard_keywords', 'hazard'],
        },
    },
    'output': {
        'affected': {
            'value': affected_field,
            'type': function_process,
            'function': post_processor_affected_function
        }
    }
}

post_processor_pcrafi_damage_ratio = {
    'key': 'post_processor_pcrafi_damage_ratio',
    'name': tr('PCRAFI Post-processor for structures damage ratio'),
    'description': tr(
        'A post processor that calculates building damage ratio for the PCRAFI buildings dataset.'
    ),
    'run_filter': {
        'hazard': hazard_flood['key'],
        'exposure': exposure_structure['key'],
    },
    'input': {
        'hazard_class': {
            'value': hazard_class_field,
            'type': field_input_type,
        },
        'exposure': {
            'type': keyword_input_type,
            'value': ['exposure_keywords', 'exposure'],
        },
        'classification': {
            'type': keyword_input_type,
            'value': ['hazard_keywords', 'classification'],
        },
        'hazard': {
            'type': keyword_input_type,
            'value': ['hazard_keywords', 'hazard'],
        },
        'pcrafi_construction_class': {
            'type': field_input_type,
            'value': pcrafi_construction_class_id_field,
        },
        'pcrafi_minimum_floor_height_class': {
            'type': field_input_type,
            'value': pcrafi_minimum_floor_height_id_field,
        },
    },
    'output': {
        'damage_ratio': {
            'value': pcrafi_damage_ratio_output,
            'type': function_process,
            'function': post_processor_pcrafi_damage_ratio_function
        }
    }
}

post_processor_pcrafi_damage_states = {
    'key': 'post_processor_pcrafi_damage_states',
    'name': tr('PCRAFI Post-processor for structures damage state'),
    'description': tr(
        'A post processor that assigns damage state according to damage ratio for the PCRAFI buildings dataset.'
    ),
    'run_filter': {
        'exposure': exposure_structure['key'],
    },
    'input': {
        'pcrafi_damage_ratio': {
            'type': field_input_type,
            'value': pcrafi_damage_ratio_output,
        },
    },
    'output': {
        'damage_state': {
            'value': pcrafi_damage_state_output,
            'type': function_process,
            'function': post_processor_pcrafi_damage_state_function
        },
        'ds0': {
            'value': pcrafi_damage_state_0_count_field,
            'type': function_process,
            'function': post_processor_pcrafi_damage_state_function_factory('DS0')
        },
        'ds1': {
            'value': pcrafi_damage_state_1_count_field,
            'type': function_process,
            'function': post_processor_pcrafi_damage_state_function_factory('DS1')
        },
        'ds2': {
            'value': pcrafi_damage_state_2_count_field,
            'type': function_process,
            'function': post_processor_pcrafi_damage_state_function_factory('DS2')
        },
        'ds3': {
            'value': pcrafi_damage_state_3_count_field,
            'type': function_process,
            'function': post_processor_pcrafi_damage_state_function_factory('DS3')
        },
        'ds4': {
            'value': pcrafi_damage_state_4_count_field,
            'type': function_process,
            'function': post_processor_pcrafi_damage_state_function_factory('DS4')
        },
        'ds5': {
            'value': pcrafi_damage_state_5_count_field,
            'type': function_process,
            'function': post_processor_pcrafi_damage_state_function_factory('DS5')
        }
    }
}

# EXEMPLE Usage of a postprocessor with filters
# from safe.definitions.hazard import (
#     hazard_flood,
#     hazard_cyclone,
#     )
# from safe.definitions.exposure import exposure_population
# post_processor_filter_example = {
#     'key': 'post_processor_filter_test',
#     'name': tr('Should run filter Processor for tests'),
#     'description': tr(
#         'A post processor to demo how to use the should run filter. this '
#         'postrocessor would run only for flood or cyclone on structure. The '
#         'run_filter can be completely omitted to allow the postprocessor to '
#         'always run. Also only one of the two filters can be defined to put'
#         'limitation only the specific field.'
#     ),
#     'run_filter': {
#         'hazard': [hazard_flood['key']', hazard_cyclone['key']],
#         'exposure': [exposure_structure['key']]
#         },
#     'input': {},
#     'output': {}
# }
