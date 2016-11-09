# coding=utf-8
import os

from jinja2.exceptions import TemplateError

from safe.definitionsv4.exposure import exposure_all
from safe.definitionsv4.hazard import hazard_all
from safe.definitionsv4.layer_purposes import layer_purpose_exposure, \
    layer_purpose_hazard

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def layer_definition_type(layer):
    """Returned relevant layer definition based on layer purpose.

    Returned the the correct definition of layer based on its purpose.
    For example, if a layer have layer_porpose: exposure, and exposure: roads
    then it will return definition for exposure_roads.

    That's why it only supports hazard layer or exposure layer

    :param layer: hazard layer or exposure layer
    :type layer: qgis.core.QgsVectorLayer

    :return: Layer definitions.
    :rtype: dict
    """
    layer_purpose = layer.keywords['layer_purpose']
    definition_list = []
    if layer_purpose == layer_purpose_exposure['key']:
        definition_list = exposure_all
    elif layer_purpose == layer_purpose_hazard['key']:
        definition_list = hazard_all

    def_type = [
        definition for definition in definition_list
        if definition['key'] == layer.keywords[layer_purpose]
    ]
    if def_type:
        return def_type[0]

    return None


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
        if c.key == component_key and c.output:
            if c.output_format == 'string':
                return c.output
            elif c.output_format == 'file':
                filename = os.path.join(
                    impact_report.output_folder, c.output_path)
                filename = os.path.abspath(filename)
                with open(filename) as f:
                    return f.read()

    raise TemplateError("Can't find component with key '%s'" % component_key)
