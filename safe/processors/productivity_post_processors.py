# coding=utf-8

"""Definitions relating to productivity post processor.."""

from safe.definitions.fields import (
    affected_field,
    size_field,
    productivity_rate_field,
    production_cost_rate_field,
    production_value_rate_field,
    productivity_field,
    production_cost_field,
    production_value_field,
    affected_productivity_field,
    affected_production_cost_field,
    affected_production_value_field,
)
from safe.processors import (
    field_input_type)
from safe.processors import (
    formula_process, function_process, post_processor_affected_value_function)
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

post_processor_productivity = {
    'key': 'post_processor_productivity',
    'name': tr('Productivity Post Processor'),
    'description': tr(
        'A post processor to calculate the productivity for each feature.'
    ),
    'input': {
        'productivity_rate': {
            'value': productivity_rate_field,
            'type': field_input_type,
        },
        # Size is in hectare for land cover
        'size': {
            'value': size_field,
            'type': field_input_type,
        },
    },
    'output': {
        'productivity': {
            'value': productivity_field,
            'type': formula_process,
            'formula': 'productivity_rate * size'
        }
    }
}
post_processor_production_cost = {
    'key': 'post_processor_production_cost',
    'name': tr('Production Cost Post Processor'),
    'description': tr(
        'A post processor to calculate the production cost for each feature'),
    'input': {
        'production_cost_rate': {
            'value': production_cost_rate_field,
            'type': field_input_type,
        },
        # Size is in hectare for land cover
        'size': {
            'value': size_field,
            'type': field_input_type,
        },
    },
    'output': {
        'production_cost': {
            'value': production_cost_field,
            'type': formula_process,
            'formula': 'production_cost_rate * size'
        }
    }
}
post_processor_production_value = {
    'key': 'post_processor_production_value',
    'name': tr('Production Value Post Processor'),
    'description': tr(
        'A post processor to calculate the production value for each feature'),
    'input': {
        'production_value_rate': {
            'value': production_value_rate_field,
            'type': field_input_type,
        },
        # Size is in hectare for land cover
        'size': {
            'value': size_field,
            'type': field_input_type,
        },
    },
    'output': {
        'production_value': {
            'value': production_value_field,
            'type': formula_process,
            'formula': 'production_value_rate * size'
        }
    }
}

# Affected productivities
post_processor_affected_productivity = {
    'key': 'post_processor_affected_productivity',
    'name': tr('Affected Productivity Post Processor'),
    'description': tr(
        'A post processor to calculate the affected productivity for each '
        'feature.'
    ),
    'input': {
        'value': {
            'value': productivity_field,
            'type': field_input_type,
        },
        'affected': {
            'value': affected_field,
            'type': field_input_type,
        },
    },
    'output': {
        'affected_productivity': {
            'value': affected_productivity_field,
            'type': function_process,
            'function': post_processor_affected_value_function
        }
    }
}

post_processor_affected_production_cost = {
    'key': 'post_processor_affected_production_cost',
    'name': tr('Affected Production Cost Post Processor'),
    'description': tr(
        'A post processor to calculate the affected production cost for each '
        'feature.'
    ),
    'input': {
        'value': {
            'value': production_cost_field,
            'type': field_input_type,
        },
        'affected': {
            'value': affected_field,
            'type': field_input_type,
        },
    },
    'output': {
        'affected_production_cost': {
            'value': affected_production_cost_field,
            'type': function_process,
            'function': post_processor_affected_value_function
        }
    }
}

post_processor_affected_production_value = {
    'key': 'post_processor_affected_production_value',
    'name': tr('Affected Production Value Post Processor'),
    'description': tr(
        'A post processor to calculate the affected production value for each '
        'feature.'
    ),
    'input': {
        'value': {
            'value': production_value_field,
            'type': field_input_type,
        },
        'affected': {
            'value': affected_field,
            'type': field_input_type,
        },
    },
    'output': {
        'affected_production_value': {
            'value': affected_production_value_field,
            'type': function_process,
            'function': post_processor_affected_value_function
        }
    }
}

productivity_post_processors = [
    post_processor_productivity,
    post_processor_production_cost,
    post_processor_production_value,
    post_processor_affected_productivity,
    post_processor_affected_production_cost,
    post_processor_affected_production_value,
]
