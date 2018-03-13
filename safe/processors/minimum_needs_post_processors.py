# coding=utf-8

"""Postprocessors about additional items in minimum needs."""

from safe.definitions import minimum_needs_fields, displaced_field
from safe.definitions.concepts import concepts
from safe.definitions.fields import additional_rice_count_field
from safe.definitions.fields import (
    pregnant_displaced_count_field, lactating_displaced_count_field)
from safe.processors.post_processor_inputs import (
    constant_input_type,
    field_input_type,
    needs_profile_input_type)
from safe.processors.post_processors import (
    formula_process,
    multiply,
    function_process)
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

EXTRA_CALORIES_NEEDED_PER_DAY = 500  # in KKal / day
DAY_IN_A_WEEK = 7  # in day / week
KG_RICE_PER_CALORIES = 0.1 / 129  # in KKal (100 gram gives 129 KKal calories)

post_processor_additional_rice = {
    'key': 'post_processor_additional_rice',
    'name': tr(
        'Additional Weekly Rice kg for Pregnant and Lactating Women Post '
        'Processor'
    ),
    'description': tr(
        'A post processor to calculate additional rice for pregnant and '
        'lactating women who are displaced. '
        '"Displaced" is defined as: {displaced_concept}').format(
        displaced_concept=concepts['displaced_people']['description']),
    'input': {
        'pregnant_displaced': [
            {
                'value': pregnant_displaced_count_field,
                'type': field_input_type,
            }
        ],
        'lactating_displaced': [
            {
                'value': lactating_displaced_count_field,
                'type': field_input_type,
            }
        ],
        'additional_rice_ratio': {
            'type': constant_input_type,
            'value': (
                EXTRA_CALORIES_NEEDED_PER_DAY *
                DAY_IN_A_WEEK *
                KG_RICE_PER_CALORIES),
        }
    },
    'output': {
        # The formula:
        # See: https://github.com/inasafe/inasafe/issues/3607
        # for reference
        #
        # displaced_population * (pregnant_rate + breastfeeding_rate) *
        #   extra_calories_needed_per_day * day_in_week * kg_rice_per_calories
        #
        # The number:
        # displaced_population * (0.024 + 0.026) * 550 Kkal/day * 7 day/week *
        #   0.1 kg rice / 129 Kkal
        #
        # displaced_population * (0.024 + 0.026) * 550 * 7 * 0.1 / 129

        # Update, 19 May 2017, Ismail Sunni
        # Since we have pregnant and lactating displace field, we will use it
        # to replace the hard coded value.
        'additional_rice': {
            'value': additional_rice_count_field,
            'type': formula_process,
            'formula': (
                '(pregnant_displaced + lactating_displaced) * '
                'additional_rice_ratio')
        },
    }
}


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


minimum_needs_post_processors = \
    initialize_minimum_needs_post_processors()
