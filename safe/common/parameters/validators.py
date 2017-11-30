# coding=utf-8
"""List of custom validations for parameter container."""

import logging

from safe.definitions.constants import STATIC, SINGLE_DYNAMIC

LOGGER = logging.getLogger('InaSAFE')

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def validate_sum(parameter_container, validation_message, **kwargs):
    """Validate the sum of parameter value's.

    :param parameter_container: The container that use this validator.
    :type parameter_container: ParameterContainer

    :param validation_message: The message if there is validation error.
    :type validation_message: str

    :param kwargs: Keywords Argument.
    :type kwargs: dict

    :returns: Dictionary of valid and message.
    :rtype: dict

    Note: The code is not the best I wrote, since there are two alternatives.
    1. If there is no None, the sum must be equal to 1
    2. If there is no None, the sum must be less than 1
    """
    parameters = parameter_container.get_parameters(False)
    values = []
    for parameter in parameters:
        if parameter.selected_option_type() in [SINGLE_DYNAMIC, STATIC]:
            values.append(parameter.value)

    sum_threshold = kwargs.get('max', 1)

    if None in values:
        # If there is None, just check to not exceeding validation_threshold
        clean_value = [x for x in values if x is not None]
        values.remove(None)
        if sum(clean_value) > sum_threshold:
            return {
                'valid': False,
                'message': validation_message
            }
    else:
        # Just make sure to not have more than validation_threshold.
        if sum(values) > sum_threshold:
            return {
                'valid': False,
                'message': validation_message
            }
    return {
        'valid': True,
        'message': ''
    }


# Add validator here.
validators = {
    'sum': validate_sum
}
