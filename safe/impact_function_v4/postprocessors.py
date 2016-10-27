# coding=utf-8

"""
Postprocessors.
"""

from qgis.core import QgsDistanceArea, QgsField, QgsFeatureRequest

from safe.definitionsv4.fields import size_field
from safe.utilities.profiling import profile
from safe.utilities.i18n import tr

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
    for key, value in variables.items():
        formula = formula.replace(key, str(value))
    return eval(formula)


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
    valid, message = enough_input(layer, post_processor['input'])
    if valid:

        if not layer.editBuffer():

            # Turn on the editing mode.
            if not layer.startEditing():
                msg = tr(
                    'The impact layer could not start the editing mode.')
                return False, msg

        # Calculate based on formula
        # Iterate all possible output
        for output_key, output_value in post_processor['output'].items():

            # Get output attribute name
            key = output_value['value']['key']
            output_field_name = output_value['value']['field_name']
            layer.keywords['inasafe_fields'][key] = output_field_name

            # If there is already the output field, don't proceed
            if layer.fieldNameIndex(output_field_name) > -1:
                msg = tr(
                    'The field name %s already exists.'
                    % output_field_name)
                layer.rollBack()
                return False, msg

            # Add output attribute name to the layer
            result = layer.addAttribute(
                QgsField(
                    output_field_name,
                    output_value['value']['type'])
            )
            if not result:
                msg = tr(
                    'Error while creating the field %s.'
                    % output_field_name)
                layer.rollBack()
                return False, msg

            # Get the index of output attribute
            output_field_index = layer.fieldNameIndex(
                output_field_name)

            if layer.fieldNameIndex(output_field_name) == -1:
                msg = tr(
                    'The field name %s has not been created.'
                    % output_field_name)
                layer.rollBack()
                return False, msg

            # Get the input field's indexes for input
            input_indexes = {}
            # Store the indexes that will be deleted.
            temporary_indexes = []
            for key, value in post_processor['input'].items():

                if value['type'] == 'field':
                    inasafe_fields = layer.keywords['inasafe_fields']
                    name_field = inasafe_fields.get(value['value']['key'])

                    if not name_field:
                        msg = tr(
                            '%s has not been found in inasafe fields.'
                            % value['value']['key'])
                        layer.rollBack()
                        return False, msg

                    index = layer.fieldNameIndex(name_field)

                    if index == -1:
                        fields = layer.fields().toList()
                        msg = tr(
                            'The field name %s has not been found in %s'
                            % (
                                name_field,
                                [f.name() for f in fields]
                            ))
                        layer.rollBack()
                        return False, msg

                    input_indexes[key] = index

                # For geometry, create new field that contain the value
                elif value['type'] == 'geometry_property':
                    if value['value'] == 'size':
                        flag = False
                        # Check if size field is already exist
                        if layer.fieldNameIndex(
                                size_field['field_name']) != -1:
                            flag = True
                            # temporary_indexes.append(input_indexes[key])
                        input_indexes[key] = add_size_field(layer)
                        if not flag:
                            temporary_indexes.append(input_indexes[key])

            # Create iterator for feature
            request = QgsFeatureRequest().setSubsetOfAttributes(
                input_indexes.values())
            iterator = layer.getFeatures(request)
            # Iterate all feature
            for feature in iterator:
                attributes = feature.attributes()

                # Create dictionary to store the input
                parameters = {}

                # Fill up the input from fields
                for key, value in input_indexes.items():
                    parameters[key] = attributes[value]
                # Fill up the input from geometry property

                # Evaluate the formula
                post_processor_result = evaluate_formula(
                    output_value['formula'], parameters)

                layer.changeAttributeValue(
                    feature.id(),
                    output_field_index,
                    post_processor_result
                )

            # Delete temporary indexes
            layer.deleteAttributes(temporary_indexes)

        layer.commitChanges()
        return True, None
    else:
        layer.rollBack()
        return False, message


@profile
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
    impact_fields = layer.keywords['inasafe_fields'].keys()
    for input_key, input_value in post_processor_input.items():
        if input_value['type'] == 'field':
            key = input_value['value']['key']
            if key in impact_fields:
                continue
            else:
                msg = 'Key %s is missing in fields %s' % (
                    key, impact_fields)
                return False, msg
    return True, None


@profile
def add_size_field(layer):
    """Add size field in to impact layer.

    If polygon, size will be area in square metre.
    If line, size will be length in metre.

    :param layer: The vector layer to use for post processing.
    :type layer: QgsVectorLayer

    :returns: Index of the size field.
    :rtype: int
    """
    # Create QgsDistanceArea object
    size_calculator = QgsDistanceArea()
    size_calculator.setSourceCrs(layer.crs())
    size_calculator.setEllipsoid('WGS84')
    size_calculator.setEllipsoidalMode(True)

    size_field_index = layer.fieldNameIndex('size')
    # Check if size field already exist
    if size_field_index == -1:
        # Add new field, size
        layer.addAttribute(QgsField(
            size_field['field_name'], size_field['type']))
        # Get index
        size_field_index = layer.fieldNameIndex('size')

    # Iterate through all features
    request = QgsFeatureRequest().setSubsetOfAttributes([])
    features = layer.getFeatures(request)
    for feature in features:
        layer.changeAttributeValue(
            feature.id(),
            size_field_index,
            size_calculator.measure(feature.geometry())
        )
    return size_field_index
