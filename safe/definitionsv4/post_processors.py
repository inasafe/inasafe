# coding=utf-8

"""Definitions relating to post-processing."""

from PyQt4.QtCore import QPyNullVariant

from safe.utilities.i18n import tr
from safe.definitionsv4.fields import (
    female_ratio_field,
    population_count_field,
    women_count_field,
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
)
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


def assign(**kwargs):
    """Simple postprocessor where we assign a value.

    :param kwargs: Dictionary of only one value to return.
    :type kwargs: dict

    :return: The result.
    """
    if len(kwargs) != 1:
        raise Exception('The dictionary should have only one item.')

    value = kwargs.values()[0]
    return value


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
        'women': {
            'value': women_count_field,
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
    'name': tr('Size Rate Post Processor'),
    'description': tr(
        'Post processor to calculate the size of the feature. If the feature '
        'is a polygon we use m^2. If the feature is a line we use metres.'),
    'input': {
        'size': {
            'value': 'size',
            'type': 'geometry_property'
        }
    },
    'output': {
        'elderly': {
            'value': size_field,
            'function': assign
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
            'value': 'size',
            'type': 'geometry_property'
            # We can add something later, like mandatory requirement, another
            #  source of input (e.g. parameter)
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

post_processors = [
    post_processor_size,
    post_processor_gender,
    post_processor_youth,
    post_processor_adult,
    post_processor_elderly,
    post_processor_size_rate,
    post_processor_affected,
]
