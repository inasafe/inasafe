# coding=utf-8
"""List of custom validations for parameter container.."""

from safe.definitions.constants import (
    DO_NOT_USE,
    CUSTOM_VALUE,
    GLOBAL_DEFAULT,
    FIELDS,
    STATIC,
    SINGLE_DYNAMIC,
    MULTIPLE_DYNAMIC,
    qvariant_numbers,
    RECENT,
    GLOBAL
)
from safe.utilities.i18n import tr
import logging
LOGGER = logging.getLogger('InaSAFE')

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def validate_sum(parameter_container):
    """Validate the sum of parameter value's.

    :param parameter_container: The container that use this validator.
    :type parameter_container: ParameterContainer

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

    if None in values:
        # If there is None, just check to not exceeding 1
        clean_value = [x for x in values if x is not None]
        values.remove(None)
        if sum(clean_value) > 1:
            return {
                'valid': False,
                'message': tr('The sum of ratio is more than 1.')
            }
    else:
        if sum(values) > 1:  # Just make sure to not have more than 1.
            return {
                'valid': False,
                'message': tr('The sum of ratio is more than 1.')
            }
    return {
        'valid': True,
        'message': ''
    }
