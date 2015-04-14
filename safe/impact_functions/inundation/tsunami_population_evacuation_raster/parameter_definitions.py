# coding=utf-8
__author__ = 'lucernae'
__date__ = '11/04/15'

from safe_extras.parameters.input_list_parameter import InputListParameter


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
    field.maximum_item_count = 3
    field.value = [0.7]  # default value
    return field
