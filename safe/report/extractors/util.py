# coding=utf-8
import os

import math
from jinja2.exceptions import TemplateError

from safe.definitions.utilities import definition
from safe.utilities.rounding import population_rounding

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def layer_definition_type(layer):
    """Returned relevant layer definition based on layer purpose.

    Returned the the correct definition of layer based on its purpose.
    For example, if a layer have layer_purpose: exposure, and exposure: roads
    then it will return definition for exposure_roads.

    That's why it only supports hazard layer or exposure layer

    :param layer: hazard layer or exposure layer
    :type layer: qgis.core.QgsVectorLayer

    :return: Layer definitions.
    :rtype: dict
    """
    layer_purposes = ['exposure', 'hazard']

    layer_purpose = [p for p in layer_purposes if p in layer.keywords]

    if not layer_purpose:
        return None

    layer_purpose = layer_purpose[0]

    return definition(layer.keywords[layer_purpose])


def jinja2_output_as_string(impact_report, component_key):
    """
    Get a given jinja2 component output as string

    Useful for composing complex document

    :param impact_report: Impact Report that contains the component key
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component_key: The key of the component to get the output from
    :type component_key: str

    :return: output as string
    :rtype: str
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
                    with open(filename) as f:
                        return f.read()
                except IOError:
                    pass

    raise TemplateError(
        "Can't find component with key '%s' and have an output" %
        component_key)


def value_from_field_name(field_name, analysis_layer):
    """Get the value of analysis layer based on field name.
    Can also be used for any layer with one feature.

    :param field_name: Field name of analysis layer that we want to get
    :type field_name: str

    :param analysis_layer: Analysis layer
    :type analysis_layer: qgis.core.QgsVectorLayer

    :return: return the valeu of a given field name of the analysis.
    """
    field_index = analysis_layer.fieldNameIndex(field_name)
    return analysis_layer.getFeatures().next()[field_index]
