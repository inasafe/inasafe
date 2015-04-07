# coding=utf-8
from safe.definitions import unit_metres_depth
from safe_extras.parameters.float_parameter import FloatParameter
from safe_extras.parameters.unit import Unit

__author__ = 'lucernae'
__project_name__ = 'inasafe'
__filename__ = 'default_parameters'
__date__ = '07/04/15'
__copyright__ = 'lana.pcfre@gmail.com'


def default_threshold():
    """Generator for the flooded target field parameter."""
    field = FloatParameter()
    field.name = 'Threshold'
    field.is_required = True
    field.value = 1.0  # default value
    field.precision = 3
    field.minimum_allowed_value = 0.0
    field.maximum_allowed_value = 10.0
    field.help_text = 'The depth of flood.'
    field.description = (
        'Lorem ipsum text for threshold')
    
    unit_metres = Unit()
    unit_metres.load_dictionary(unit_metres_depth)
    
    field.unit = unit_metres
    field.allowed_units = [unit_metres]
    field.value = 1.0
    return [field]