# coding=utf-8
from safe.definitions import unit_metres_depth
from safe_extras.parameters.float_parameter import FloatParameter
from safe_extras.parameters.input_list_parameter import InputListParameter
from safe_extras.parameters.unit import Unit

__author__ = 'lucernae'
__project_name__ = 'inasafe'
__filename__ = 'default_parameters'
__date__ = '07/04/15'
__copyright__ = 'lana.pcfre@gmail.com'


def default_threshold():
    """Generator for the default threshold parameter."""
    field = InputListParameter()
    field.name = 'Thresholds [m]'
    field.is_required = True
    field.element_type = float
    field.expected_type = list
    field.ordering = InputListParameter.AscendingOrder
    field.minimum_item_count = 1
    field.maximum_item_count = 3
    field.value = [1.0]  # default value
    field.help_text = 'The depth of flood.'
    field.description = (
        'Lorem ipsum text for threshold')
    return [field]