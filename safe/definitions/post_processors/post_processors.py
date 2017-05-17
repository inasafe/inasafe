# coding=utf-8

# pylint: disable=pointless-string-statement
# This is disabled for typehinting docstring.

"""Definitions relating to post-processing."""

import logging


from safe.definitions import concepts
from safe.definitions.exposure import exposure_population
from safe.definitions.fields import (
    population_displacement_ratio_field,
    displaced_field,
    population_count_field,
    pregnant_lactating_displaced_count_field,
    feature_rate_field,
    feature_value_field,
    size_field,
    hazard_class_field,
    affected_field,
    exposure_count_field,
    additional_rice_count_field,
)
from safe.definitions.hazard_classifications import hazard_classes_all
from post_processor_functions import (
    multiply,
    size,
    post_processor_affected_function,
    post_processor_population_displacement_function,
)
from safe.definitions.hazard_classifications import not_exposed_class
from safe.definitions.minimum_needs import minimum_needs_fields
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


# # #
# Post processors related definitions
# # #

# # #
# Input
# # #
constant_input_type = {
    'key': 'constant',
    'description': tr('This type of input takes a constant value.')
}

field_input_type = {
    'key': 'field',
    'description': tr('This type of input takes a value from a field.')
}

dynamic_field_input_type = {
    'key': 'dynamic_field',
    'description': tr(
        'This type of input takes value from a dynamic field. '
        'It will require some additional parameter details.')
}

keyword_input_type = {
    'key': 'keyword',
    'description': tr(
        'This type of input takes value from a keyword for the layer '
        'being handled.')
}

needs_profile_input_type = {
    'key': 'needs_profile',
    'description': tr(
        'This type of input takes a value from current InaSAFE minimum needs '
        'profile.')
}

geometry_property_input_type = {
    'key': 'geometry_property',
    'description': tr(
        'This type of input takes a value from the geometry property.')
}

layer_property_input_type = {
    'key': 'layer_property',
    'description': tr(
        'This type of input takes it\'s value from a layer property. For '
        'example the layer Coordinate Reference System of the layer.')
}


post_processor_input_types = [
    constant_input_type,
    field_input_type,
    dynamic_field_input_type,
    keyword_input_type,
    needs_profile_input_type,
    geometry_property_input_type,
    layer_property_input_type
]

# Input values

size_calculator_input_value = {
    'key': 'size_calculator',
    'description': tr(
        'This is a value for the layer_property input type. It retrieves Size '
        'Calculator of the layer CRS')
}

layer_crs_input_value = {
    'key': 'layer_crs',
    'description': tr(
        'This is a value for layer_property input type. It retrieves the '
        'layer Coordinate Reference System (CRS).')
}

layer_property_input_values = [
    size_calculator_input_value,
    layer_crs_input_value
]

post_processor_input_values = [
    size_calculator_input_value,
    layer_crs_input_value,
    layer_property_input_type]

# # # Process
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
        u'A post processor to calculate the size of the feature. The unit is '
        u'defined in the exposure definition.'),
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

post_processor_size_rate = {
    'key': 'post_processor_size_rate',
    'name': tr('Size Rate Post Processor'),
    'description': tr(
        u'A post processor to calculate the value of a feature based on its '
        u'size. If a feature is a polygon the size is calculated as '
        u'the area in m². If the feature is a line we use length in metres.'),
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
        'classification': {
            'type': keyword_input_type,
            'value': ['hazard_keywords', 'classification'],
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

# # #
# Minimum Needs.
#
# Minimum needs is a kind of post processor which can be defined by user.
# # #


def initialize_minimum_needs_post_processors():
    """Generate definitions for minimum needs post processors."""
    processors = []

    for field in minimum_needs_fields:
        field_key = field['key']
        field_name = field['name']
        field_description = field['description']
        need_parameter = field['need_parameter']
        """:type: safe.common.parameters.resource_parameter.ResourceParameter
        """

        processor = {
            'key': 'post_processor_{key}'.format(key=field_key),
            'name': '{field_name} Post Processor'.format(
                field_name=field_name),
            'description': field_description,
            'input': {
                'population': {
                    'value': displaced_field,
                    'type': field_input_type,
                },
                'amount': {
                    'type': needs_profile_input_type,
                    'value': need_parameter.name,
                }
            },
            'output': {
                'needs': {
                    'value': field,
                    'type': function_process,
                    'function': multiply
                }
            }
        }
        processors.append(processor)
    return processors


minimum_needs_post_processors = initialize_minimum_needs_post_processors()

