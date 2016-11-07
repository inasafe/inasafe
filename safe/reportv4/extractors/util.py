# coding=utf-8
import os

from jinja2.exceptions import TemplateError

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '10/28/16'


def jinja2_output_as_string(impact_report, component_key):
    """
    Get a given jinja2 component output as string

    Useful for composing complex document

    :param impact_report:
    :type impact_report: safe.reportv4.impact_report.ImpactReport
    :param component_key:
    :return:
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
