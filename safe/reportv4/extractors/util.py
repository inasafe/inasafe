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


def round_affecter_number(
        number,
        enable_rounding=False,
        use_population_rounding=False):
    """Tries to convert and round the number.

    Rounded using population rounding rule.

    :param number: number represented as string or float
    :type number: str, float

    :param enable_rounding: flag to enable rounding
    :type enable_rounding: bool

    :param use_population_rounding: flag to enable population rounding scheme
    :type use_population_rounding: bool

    :return: rounded number
    """
    decimal_number = float(number)
    rounded_number = int(math.ceil(decimal_number))
    if enable_rounding and use_population_rounding:
        # if uses population rounding
        return population_rounding(rounded_number)
    elif enable_rounding:
        return rounded_number

    return decimal_number


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
    :type impact_report: safe.reportv4.impact_report.ImpactReport

    :param component_key: The key of the component to get the output from
    :type component_key: str

    :return: output as string
    :rtype: str
    """
    metadata = impact_report.metadata
    for c in metadata.components:
        if c.key == component_key:
            if c.output_format == 'string':
                return c.output
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
