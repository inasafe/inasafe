# coding=utf-8

"""Definitions relating to productivity post processor.."""

from safe.definitions.fields import (
    size_field,
    productivity_rate_field,
    productivity_cost_rate_field,
    productivity_value_rate_field,
    productivity_field,
    productivity_cost_field,
    productivity_value_field
)
from safe.definitions.post_processors.post_processor_inputs import (
    field_input_type)
from safe.definitions.post_processors.post_processors import formula_process
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

post_processor_productivity = {
    'key': 'post_processor_productivity',
    'name': tr('Productivity Post Processor'),
    'description': tr(
        'A post processor to calculate the productivity for each feature'
    ),
    'input': {
        'productivity_rate': {
            'value': productivity_rate_field,
            'type': field_input_type,
        },
        # In meter square
        'size': {
            'value': size_field,
            'type': field_input_type,
        },
    },
    'output': {
        'productivity': {
            'value': productivity_field,
            'type': formula_process,
            'formula': 'productivity_rate * size / 10000'
        }
    }
}
post_processor_productivity_cost = {
    'key': 'post_processor_productivity_cost',
    'name': tr('Productivity Cost Post Processor'),
    'description': tr(
        'A post processor to calculate the productivity cost for each feature'
    ),
    'input': {
        'productivity_cost_rate': {
            'value': productivity_cost_rate_field,
            'type': field_input_type,
        },
        # In meter square
        'size': {
            'value': size_field,
            'type': field_input_type,
        },
    },
    'output': {
        'productivity_cost': {
            'value': productivity_cost_field,
            'type': formula_process,
            'formula': 'productivity_cost_rate * size / 10000'
        }
    }
}
post_processor_productivity_value = {
    'key': 'post_processor_productivity_value',
    'name': tr('Productivity Value Post Processor'),
    'description': tr(
        'A post processor to calculate the productivity value for each feature'
    ),
    'input': {
        'productivity_value_rate': {
            'value': productivity_value_rate_field,
            'type': field_input_type,
        },
        # In meter square
        'size': {
            'value': size_field,
            'type': field_input_type,
        },
    },
    'output': {
        'productivity_value': {
            'value': productivity_value_field,
            'type': formula_process,
            'formula': 'productivity_value_rate * size / 10000'
        }
    }
}

productivity_post_processors = [
    post_processor_productivity,
    post_processor_productivity_cost,
    post_processor_productivity_value
]
