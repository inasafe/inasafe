# coding=utf-8
import os

from jinja2.exceptions import TemplateError

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


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
