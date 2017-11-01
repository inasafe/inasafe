# coding=utf-8

# pylint: disable=pointless-string-statement
# This is disabled for typehinting docstring.

"""Definitions relating to post-processing."""

import logging

from safe.definitions.fields import (
    feature_rate_field,
    feature_value_field,
    size_field,
    hazard_class_field,
    affected_field
)
from safe.definitions.hazard_classifications import not_exposed_class
from safe.processors.post_processor_functions import (
    multiply,
    size,
    post_processor_affected_function)
from safe.processors.post_processor_inputs import (
    geometry_property_input_type,
    layer_property_input_type,
    size_calculator_input_value,
    keyword_input_type,
    field_input_type)
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
