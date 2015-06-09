# coding=utf-8
from safe.utilities.i18n import tr
from safe_extras.parameters.input_list_parameter import InputListParameter

__author__ = 'lucernae'
__date__ = '13/04/15'


def categorical_thresholds():
    field = InputListParameter()
    field.name = 'Categorical Thresholds'
    field.element_type = float
    field.minimum_item_count = 3
    field.maximum_item_count = 3
    field.ordering = InputListParameter.AscendingOrder
    field.value = [0.34, 0.67, 1.0]
    field.help_text = tr('Thresholds to categorize hazards values.')
    field.description = tr(
        'It needs 3 values to categorize hazard as low, medium, and high '
        'hazard.')
    return field
