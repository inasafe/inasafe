# coding=utf-8

"""Postprocessors."""


# noinspection PyUnresolvedReferences
from qgis.core import QgsFeatureRequest

from safe.definitions.minimum_needs import minimum_needs_parameter
from safe.gis.vector.tools import (
    create_field_from_definition, SizeCalculator)
from safe.processors import (
    field_input_type,
    keyword_input_type,
    keyword_value_expected,
    dynamic_field_input_type,
    needs_profile_input_type,
    layer_crs_input_value,
    constant_input_type,
    geometry_property_input_type,
    layer_property_input_type,
    size_calculator_input_value
)
from safe.utilities.i18n import tr
from safe.utilities.profiling import profile
from functools import reduce

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def evaluate_formula(formula, variables):
    """Very simple formula evaluator. Beware the security.

    :param formula: A simple formula.
    :type formula: str

    :param variables: A collection of variable (key and value).
    :type variables: dict

    :returns: The result of the formula execution.
    :rtype: float, int
    """
    for key, value in list(variables.items()):
        if value is None or (hasattr(value, 'isNull') and value.isNull()):
            # If one value is null, we return null.
            return value
        formula = formula.replace(key, str(value))
    result = eval(formula)
    return result


@profile
def run_single_post_processor(layer, post_processor):
    """Run single post processor.

    If the layer has the output field, it will pass the post
    processor calculation.

    :param layer: The vector layer to use for post processing.
    :type layer: QgsVectorLayer

    :param post_processor: A post processor definition.
    :type post_processor: dict

    :returns: Tuple with True if success, else False with an error message.
    :rtype: (bool, str)
    """
    if not layer.editBuffer():

        # Turn on the editing mode.
        if not layer.startEditing():
            msg = tr('The impact layer could not start the editing mode.')
            return False, msg

    # Calculate based on formula
    # Iterate all possible output and create the correct field.
    for output_key, output_value in list(post_processor['output'].items()):

        # Get output attribute name
        key = output_value['value']['key']
        output_field_name = output_value['value']['field_name']
        layer.keywords['inasafe_fields'][key] = output_field_name

        # If there is already the output field, don't proceed
        if layer.fields().lookupField(output_field_name) > -1:
            msg = tr(
                'The field name %s already exists.'
                % output_field_name)
            layer.rollBack()
            return False, msg

        # Add output attribute name to the layer
        field = create_field_from_definition(output_value['value'])
        result = layer.addAttribute(field)
        if not result:
            msg = tr(
                'Error while creating the field %s.'
                % output_field_name)
            layer.rollBack()
            return False, msg

        # Get the index of output attribute
        output_field_index = layer.fields().lookupField(output_field_name)

        if layer.fields().lookupField(output_field_name) == -1:
            msg = tr(
                'The field name %s has not been created.'
                % output_field_name)
            layer.rollBack()
            return False, msg

        # Get the input field's indexes for input
        input_indexes = {}

        input_properties = {}

        # Default parameters
        default_parameters = {}

        msg = None

        # Iterate over every inputs.
        for key, values in list(post_processor['input'].items()):
            values = values if isinstance(values, list) else [values]
            for value in values:
                is_constant_input = (
                    value['type'] == constant_input_type)
                is_field_input = (
                    value['type'] == field_input_type
                    or value['type'] == dynamic_field_input_type)
                is_geometry_input = (
                    value['type'] == geometry_property_input_type)
                is_keyword_input = (
                    value['type'] == keyword_input_type)
                is_needs_input = (
                    value['type'] == needs_profile_input_type)
                is_layer_property_input = (
                    value['type'] == layer_property_input_type)
                if value['type'] == keyword_value_expected:
                    break
                if is_constant_input:
                    default_parameters[key] = value['value']
                    break
                elif is_field_input:
                    if value['type'] == dynamic_field_input_type:
                        key_template = value['value']['key']
                        field_param = value['field_param']
                        field_key = key_template % field_param
                    else:
                        field_key = value['value']['key']

                    inasafe_fields = layer.keywords['inasafe_fields']
                    name_field = inasafe_fields.get(field_key)

                    if not name_field:
                        msg = tr(
                            '%s has not been found in inasafe fields.'
                            % value['value']['key'])
                        continue

                    index = layer.fields().lookupField(name_field)

                    if index == -1:
                        fields = layer.fields().toList()
                        msg = tr(
                            'The field name %s has not been found in %s'
                            % (
                                name_field,
                                [f.name() for f in fields]
                            ))
                        continue

                    input_indexes[key] = index
                    break

                # For geometry, create new field that contain the value
                elif is_geometry_input:
                    input_properties[key] = geometry_property_input_type['key']
                    break

                # for keyword
                elif is_keyword_input:
                    # See http://stackoverflow.com/questions/14692690/
                    # access-python-nested-dictionary-items-via-a-list-of-keys
                    value = reduce(
                        lambda d, k: d[k], value['value'], layer.keywords)

                    default_parameters[key] = value
                    break

                # for needs profile
                elif is_needs_input:
                    need_parameter = minimum_needs_parameter(
                        parameter_name=value['value'])
                    value = need_parameter.value

                    default_parameters[key] = value
                    break

                # for layer property
                elif is_layer_property_input:
                    if value['value'] == layer_crs_input_value:
                        default_parameters[key] = layer.crs()

                    if value['value'] == size_calculator_input_value:
                        exposure = layer.keywords.get('exposure')
                        if not exposure:
                            keywords = layer.keywords.get('exposure_keywords')
                            exposure = keywords.get('exposure')

                        default_parameters[key] = SizeCalculator(
                            layer.crs(), layer.geometryType(), exposure)
                    break

            else:
                # executed when we can't find all the inputs
                layer.rollBack()
                return False, msg

        # Create iterator for feature
        request = QgsFeatureRequest().setSubsetOfAttributes(
            list(input_indexes.values()))
        iterator = layer.getFeatures(request)

        inputs = input_indexes.copy()
        inputs.update(input_properties)

        # Iterate all feature
        for feature in iterator:
            attributes = feature.attributes()

            # Create dictionary to store the input
            parameters = {}
            parameters.update(default_parameters)

            # Fill up the input from fields
            for key, value in list(inputs.items()):
                if value == geometry_property_input_type['key']:
                    parameters[key] = feature.geometry()
                else:
                    parameters[key] = attributes[value]
            # Fill up the input from geometry property

            # Evaluate the function
            python_function = output_value.get('function')
            if python_function:
                # Launch the python function
                post_processor_result = python_function(**parameters)
            else:
                # Evaluate the function
                formula = output_value['formula']
                post_processor_result = evaluate_formula(
                    formula, parameters)

            # The affected postprocessor returns a boolean.
            if isinstance(post_processor_result, bool):
                post_processor_result = tr(str(post_processor_result))

            layer.changeAttributeValue(
                feature.id(),
                output_field_index,
                post_processor_result
            )

    layer.commitChanges()
    return True, None


def enough_input(layer, post_processor_input):
    """Check if the input from impact_fields in enough.

    :param layer: The vector layer to use for post processing.
    :type layer: QgsVectorLayer

    :param post_processor_input: Collection of post processor input
        requirements.
    :type post_processor_input: dict

    :returns: Tuple with True if success, else False with an error message.
    :rtype: (bool, str)
    """
    impact_fields = list(layer.keywords['inasafe_fields'].keys())
    for input_key, input_values in list(post_processor_input.items()):
        input_values = (
            input_values if isinstance(input_values, list) else [input_values])
        msg = None
        for input_value in input_values:
            is_constant_input = input_value['type'] == constant_input_type
            is_field_input = input_value['type'] == field_input_type
            is_dynamic_input = input_value['type'] == dynamic_field_input_type
            is_needs_input = input_value['type'] == needs_profile_input_type
            is_keyword_input = input_value['type'] == keyword_input_type
            is_layer_input = input_value['type'] == layer_property_input_type
            is_keyword_value = input_value['type'] == keyword_value_expected
            is_geometry_input = (
                input_value['type'] == geometry_property_input_type)
            if is_constant_input:
                # constant input doesn't need any check
                break
            elif is_field_input:
                key = input_value['value']['key']
                if key in impact_fields:
                    break
                else:
                    msg = 'Key %s is missing in fields %s' % (
                        key, impact_fields)
            elif is_dynamic_input:
                key_template = input_value['value']['key']
                field_param = input_value['field_param']
                key = key_template % field_param
                if key in impact_fields:
                    break
                else:
                    msg = 'Key %s is missing in dynamic fields %s' % (
                        key, impact_fields)
            elif is_needs_input:
                parameter_name = input_value['value']
                if minimum_needs_parameter(parameter_name=parameter_name):
                    break
                else:
                    msg = (
                        'Minimum needs %s is missing from current '
                        'profile') % (
                            parameter_name, )
            elif is_keyword_input:
                try:
                    reduce(
                        lambda d, k:
                        d[k], input_value['value'], layer.keywords)
                    break
                except KeyError:
                    msg = 'Value %s is missing in keyword: %s' % (
                        input_key, input_value['value'])
            elif is_layer_input or is_geometry_input:
                # will be taken from the layer itself, so always true
                break
            elif is_keyword_value:
                try:
                    value = reduce(
                        lambda d, k:
                        d[k], input_value[
                            'value'], layer.keywords)
                    if value == input_value['expected_value']:
                        break
                    else:
                        msg = 'Value %s is not expected in keyword: %s' % (
                            input_value['expected_value'],
                            input_value['value'])
                except KeyError:
                    msg = 'Value %s is missing in keyword: %s' % (
                        input_key, input_value['value'])

        else:
            return False, msg
    return True, None
