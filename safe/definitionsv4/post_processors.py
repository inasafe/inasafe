# coding=utf-8

"""Definitions relating to post-processing."""

from PyQt4.QtCore import QPyNullVariant

from qgis.core import QgsDistanceArea

from safe.definitionsv4.exposure import exposure_population
from safe.definitionsv4.minimum_needs import minimum_needs_fields
from safe.utilities.i18n import tr
from safe.definitionsv4.fields import (
    female_ratio_field,
    population_count_field,
    female_count_field,
    youth_ratio_field,
    youth_count_field,
    adult_ratio_field,
    adult_count_field,
    elderly_ratio_field,
    elderly_count_field,
    feature_rate_field,
    feature_value_field,
    size_field,
    hazard_class_field,
    affected_field,
    exposure_count_field)
from safe.definitionsv4.hazard_classifications import all_hazard_classes

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

"""
Functions
"""


def multiply(**kwargs):
    """Simple postprocessor where we multiply values.

    :param kwargs: Dictionary of values to multiply
    :type kwargs: dict

    :return: The result.
    :rtype: float
    """
    result = 1
    for i in kwargs.values():
        if isinstance(i, QPyNullVariant) or not i:
            # If one value is null, we return null.
            return i
        result *= i
    return result


def size(**kwargs):
    """Simple postprocessor where we compute the size of a feature.

    :param geometry: The geometry.
    :type geometry: QgsGeometry

    :param size_calculator: The size calculator.
    :type size_calculator: QgsDistanceArea

    :return: The size.
    """
    feature_size = kwargs['size_calculator'].measure(kwargs['geometry'])
    return feature_size


# This postprocessor function is also used in the aggregation_summary
def post_processor_affected_function(**kwargs):
    """Private function used in the affected postprocessor.

    :param classification: The hazard classification to use.

    :param hazard_class: The hazard class to check.

    :return: If this hazard class is affected or not.
    :rtype: bool
    """
    for hazard in all_hazard_classes:
        if hazard['key'] == kwargs['classification']:
            classification = hazard['classes']

    for level in classification:
        if level['key'] == kwargs['hazard_class']:
            affected = level['affected']
            break
    else:
        affected = False

    return affected


"""
Post processors related definitions
"""

"""Input"""
field_input_type = {
    'key': 'field',
    'description': tr('This type of input take value from field')
}

dynamic_field_input_type = {
    'key': 'dynamic_field',
    'description': tr(
        'This type of input take value from a dynamic field. '
        'Thus, it required some additional parameter.')
}

keyword_input_type = {
    'key': 'keyword',
    'description': tr(
        'This type of input take value from layer keyword being handled.')
}

needs_profile_input_type = {
    'key': 'needs_profile',
    'description': tr(
        'This type of input take value from current InaSAFE needs profile.')
}

"""Process"""
formula_process = {
    'key': 'formula',
    'description': tr(
        'This type of process takes inputs as arguments and process it '
        'according to python expressions described.')
}

function_process = {
    'key': 'function',
    'description': tr(
        'This type of process takes inputs as arguments and process it '
        'using python function referenced.')
}

"""
Post processors
"""

# A postprocessor can be defined with a formula or with a python function.

post_processor_gender = {
    'key': 'post_processor_gender',
    'name': tr('Gender Post Processor'),
    'description': tr(
        'Post processor to calculate the number of affected females'),
    'input': {
        'population': {
            'value': population_count_field,
            'type': 'field'
        },
        'gender_ratio': {
            'value': female_ratio_field,
            'type': 'field'
        }
    },
    'output': {
        'female': {
            'value': female_count_field,
            'formula': 'population * gender_ratio'
        }
    }
}

post_processor_youth = {
    'key': 'post_processor_youth',
    'name': tr('Youth Post Processor'),
    'description': tr(
        'Post processor to calculate the number of affected youth'),
    'input': {
        'population': {
            'value': population_count_field,
            'type': 'field'
        },
        'youth_ratio': {
            'value': youth_ratio_field,
            'type': 'field'
        }
    },
    'output': {
        'youth': {
            'value': youth_count_field,
            'function': multiply
        }
    }
}

post_processor_adult = {
    'key': 'post_processor_adult',
    'name': tr('Adult Post Processor'),
    'description': tr(
        'Post processor to calculate the number of affected adults'),
    'input': {
        'population': {
            'value': population_count_field,
            'type': 'field'
        },
        'adult_ratio': {
            'value': adult_ratio_field,
            'type': 'field'
        }
    },
    'output': {
        'adult': {
            'value': adult_count_field,
            'function': multiply
        }
    }
}

post_processor_elderly = {
    'key': 'post_processor_elderly',
    'name': tr('Elderly Post Processor'),
    'description': tr(
        'Post processor to calculate the number of affected elderly'),
    'input': {
        'population': {
            'value': population_count_field,
            'type': 'field'
        },
        'elderly_ratio': {
            'value': elderly_ratio_field,
            'type': 'field'
        }
    },
    'output': {
        'elderly': {
            'value': elderly_count_field,
            'function': multiply
        }
    }
}

post_processor_size = {
    'key': 'post_processor_size',
    'name': tr('Size Value Post Processor'),
    'description': tr(
        'Post processor to calculate the size of the feature. If the feature '
        'is a polygon we use m^2. If the feature is a line we use metres.'),
    'input': {
        'size_calculator': {
            'type': 'layer_property',
            'value': 'size_calculator'
        },
        'geometry': {
            'type': 'geometry_property'
        }
    },
    'output': {
        'size': {
            'value': size_field,
            'function': size
        }
    }
}

post_processor_size_rate = {
    'key': 'post_processor_size_rate',
    'name': tr('Size Rate Post Processor'),
    'description': tr(
        'Post processor to calculate the value of a feature based on the size '
        'of the feature. If feature is a polygon the size is calculated as '
        'the area in m^2. If the feature is a line we use length in metres.'),
    'input': {
        'size': {
            'type': 'field',
            'value': size_field,
        },
        'rate': {
            'value': feature_rate_field,
            'type': 'field'
        }
    },
    'output': {
        'elderly': {
            'value': feature_value_field,
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
        'Post processor to determine of the feature is affected or not '
        'according to the hazard classification.'),
    'input': {
        'hazard_class': {
            'value': hazard_class_field,
            'type': 'field'
        },
        'classification': {
            'type': 'keyword',
            'value': ['hazard_keywords', 'classification'],
        },
    },
    'output': {
        'affected': {
            'value': affected_field,
            'function': post_processor_affected_function
        }
    }
}

"""
Minimum Needs.

Minimum needs is a kind of post processor which can be defined by user.
"""


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
            'name': field_name,
            'description': field_description,
            'input': {
                # input as a list means, try to get the input from the
                # listed source. Pick the first available
                'population': [
                    {
                        'value': population_count_field,
                        'type': 'field'
                    },
                    {
                        'value': exposure_count_field,
                        'field_param': exposure_population['key'],
                        'type': 'dynamic_field',
                    }],
                'amount': {
                    'type': 'needs_profile',
                    'value': need_parameter.name,
                }
            },
            'output': {
                'needs': {
                    'value': field,
                    'function': multiply
                }
            }
        }
        processors.append(processor)
    return processors


minimum_needs_post_processors = initialize_minimum_needs_post_processors()


# This is the order of execution, so the order is important.
# For instance, the size post processor must run before size_rate.
post_processors = [
    post_processor_size,
    post_processor_gender,
    post_processor_youth,
    post_processor_adult,
    post_processor_elderly,
    post_processor_size_rate,
    post_processor_affected,
] + minimum_needs_post_processors
