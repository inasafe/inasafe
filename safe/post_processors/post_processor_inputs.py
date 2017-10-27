# coding=utf-8
"""Post processor input type and value definitions."""
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2017, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

# Input types

constant_input_type = {
    'key': 'constant',
    'description': tr('This type of input takes a constant value.')
}
field_input_type = {
    'key': 'field',
    'description': tr('This type of input takes a value from a field.')
}
dynamic_field_input_type = {
    'key': 'dynamic_field',
    'description': tr(
        'This type of input takes value from a dynamic field. '
        'It will require some additional parameter details.')
}
keyword_input_type = {
    'key': 'keyword',
    'description': tr(
        'This type of input takes value from a keyword for the layer '
        'being handled.')
}
keyword_value_expected = {
    'key': 'keyword_value',
    'description': tr(
        'This type of parameter checks the value of a specific keyword in '
        'order to run for the layer being handled.')
}
needs_profile_input_type = {
    'key': 'needs_profile',
    'description': tr(
        'This type of input takes a value from current InaSAFE minimum needs '
        'profile.')
}
geometry_property_input_type = {
    'key': 'geometry_property',
    'description': tr(
        'This type of input takes a value from the geometry property.')
}
layer_property_input_type = {
    'key': 'layer_property',
    'description': tr(
        'This type of input takes it\'s value from a layer property. For '
        'example the layer Coordinate Reference System of the layer.')
}
post_processor_input_types = [
    constant_input_type,
    field_input_type,
    dynamic_field_input_type,
    keyword_input_type,
    needs_profile_input_type,
    geometry_property_input_type,
    layer_property_input_type
]

# Input values

size_calculator_input_value = {
    'key': 'size_calculator',
    'description': tr(
        'This is a value for the layer_property input type. It retrieves Size '
        'Calculator of the layer CRS')
}
layer_crs_input_value = {
    'key': 'layer_crs',
    'description': tr(
        'This is a value for layer_property input type. It retrieves the '
        'layer Coordinate Reference System (CRS).')
}
layer_property_input_values = [
    size_calculator_input_value,
    layer_crs_input_value
]
post_processor_input_values = [
    size_calculator_input_value,
    layer_crs_input_value,
    layer_property_input_type]
