# coding=utf-8
__author__ = 'lucernae'
__date__ = '11/04/15'

from safe_extras.parameters.input_list_parameter import InputListParameter
from safe.utilities.i18n import tr


def threshold():
    """Generator for the default threshold parameter.

    :return: List of InputListParameter
    :rtype: list[InputListParameter]
    """
    field = InputListParameter()
    field.name = 'Thresholds [m]'
    field.is_required = True
    field.element_type = float
    field.expected_type = list
    field.ordering = InputListParameter.AscendingOrder
    field.minimum_item_count = 1
    # Rizky: no reason for the number below. It can be any values to describe
    # maximum item count. Feel free to change it when necessary.
    # PS: it was my birthdate
    field.maximum_item_count = 19
    field.value = [0.7]  # default value
    field.help_text = tr(
        'Thresholds to categorize people in the inundated area.')
    field.description = tr(
        'Up to three thresholds (in meters) can be set in an increasing '
        'order. The impact function will report the number of people per '
        'threshold you define here. Specify the upper bound for each '
        'threshold. The lower bound of the first threshold shall be zero. '
        'People in water depths above the maximum threshold will be '
        'classified as needing evacuation.'
    )
    return field
