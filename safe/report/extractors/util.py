# coding=utf-8
"""Module that contains helper function for report context extraction."""
import codecs
import os

from jinja2.exceptions import TemplateError

from safe.definitions.hazard_classifications import hazard_classes_all
from safe.definitions.utilities import definition

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def layer_definition_type(layer):
    """Returned relevant layer definition based on layer purpose.

    Returned the the correct definition of layer based on its purpose.
    For example, if a layer have layer_purpose: exposure, and exposure: roads
    then it will return definition for exposure_roads.

    That's why it only supports hazard layer or exposure layer.

    :param layer: hazard layer or exposure layer
    :type layer: qgis.core.QgsVectorLayer

    :return: Layer definitions.
    :rtype: dict

    .. versionadded:: 4.0
    """
    layer_purposes = ['exposure', 'hazard']

    layer_purpose = [p for p in layer_purposes if p in layer.keywords]

    if not layer_purpose:
        return None

    layer_purpose = layer_purpose[0]

    return definition(layer.keywords[layer_purpose])


def layer_hazard_classification(layer):
    """Returned this particular hazard classification.

    :param layer: hazard layer or exposure layer
    :type layer: qgis.core.QgsVectorLayer

    :return: Hazard classification.
    :rtype: dict

    .. versionadded:: 4.0
    """
    if not layer.keywords.get('hazard'):
        # return nothing if not hazard layer
        return None

    hazard_classification = None
    # retrieve hazard classification from hazard layer
    for classification in hazard_classes_all:
        classification_name = layer.keywords['classification']
        if classification_name == classification['key']:
            hazard_classification = classification
            break
    return hazard_classification


def jinja2_output_as_string(impact_report, component_key):
    """Get a given jinja2 component output as string.

    Useful for composing complex document.

    :param impact_report: Impact Report that contains the component key.
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component_key: The key of the component to get the output from.
    :type component_key: str

    :return: output as string.
    :rtype: str

    .. versionadded:: 4.0
    """
    metadata = impact_report.metadata
    for c in metadata.components:
        if c.key == component_key:
            if c.output_format == 'string':
                return c.output or ''
            elif c.output_format == 'file':
                try:
                    filename = os.path.join(
                        impact_report.output_folder, c.output_path)
                    filename = os.path.abspath(filename)
                    # We need to open the file in UTF-8, the HTML may have
                    # some accents for instance.
                    with codecs.open(filename, 'r', 'utf-8') as f:
                        return f.read()
                except IOError:
                    pass

    raise TemplateError(
        "Can't find component with key '%s' and have an output" %
        component_key)


def value_from_field_name(field_name, analysis_layer):
    """Get the value of analysis layer based on field name.

    Can also be used for any layer with one feature.

    :param field_name: Field name of analysis layer that we want to get.
    :type field_name: str

    :param analysis_layer: Analysis layer.
    :type analysis_layer: qgis.core.QgsVectorLayer

    :return: return the valeu of a given field name of the analysis.

    .. versionadded:: 4.0
    """
    field_index = analysis_layer.fields().lookupField(field_name)
    if field_index < 0:
        return None
    else:
        return analysis_layer.getFeatures().next()[field_index]


def resolve_from_dictionary(dictionary, key_list, default_value=None):
    """Take value from a given key list from dictionary.

    Example: given dictionary d, key_list = ['foo', 'bar'],
    it will try to resolve d['foo']['bar']. If not possible,
    return default_value.

    :param dictionary: A dictionary to resolve.
    :type dictionary: dict

    :param key_list: A list of key to resolve.
    :type key_list: list[str], str

    :param default_value: Any arbitrary default value to return.

    :return: intended value, if fails, return default_value.

    .. versionadded:: 4.0
    """
    try:
        current_value = dictionary
        key_list = key_list if isinstance(key_list, list) else [key_list]
        for key in key_list:
            current_value = current_value[key]

        return current_value
    except KeyError:
        return default_value


def retrieve_exposure_classes_lists(exposure_keywords):
    """Retrieve exposures classes.

    Only if the exposure has some classifications.

    :param exposure_keywords: exposure keywords
    :type exposure_keywords: dict

    :return: lists of classes used in the classifications.
    :rtype: list(dict)
    """
    # return None in case exposure doesn't have classifications
    classification = exposure_keywords.get('classification')
    if not classification:
        return None
    # retrieve classes definitions
    exposure_classifications = definition(classification)
    return exposure_classifications['classes']
