# coding=utf-8
"""Reporting 101."""

import os
import unittest

from safe.common.utilities import safe_dir
from safe.definitions.reports import (
    jinja2_component_type,
    final_product_tag,
    table_product_tag,
    html_product_tag)
from safe.impact_function.impact_function import ImpactFunction
from safe.report.impact_report import ImpactReport
from safe.report.processors.default import jinja2_renderer
from safe.report.report_metadata import (
    Jinja2ComponentsMetadata,
    ReportMetadata)
from safe.test.utilities import get_qgis_app
from safe.utilities.i18n import tr


# first step
def hello_world_extractor(impact_report, component):
    print 'Component key: {component_key}'.format(component_key=component.key)
    context = dict()
    context['hello_world'] = "Hello World!"
    return context


# second step
hello_world_component = {
    'key': 'hello-world',
    'type': jinja2_component_type,
    'processor': jinja2_renderer,
    'extractor': hello_world_extractor,
    'output_format': Jinja2ComponentsMetadata.OutputFormat.File,
    'output_path': 'hello-world-output.html',
    'template': 'hello-world.html',
    'tags': [
        final_product_tag,
        table_product_tag,
        html_product_tag
    ],
    'extra_args': {
        'header': tr('Hello World!')
    }
}

# third step (specifying what components to use)
hello_world_metadata_html = {
    'key': 'hello-world-result-html',
    'name': 'hello-world-result-html',
    'template_folder': safe_dir('report/test/fixtures'),
    'components': [hello_world_component]
}


class TestHelloWorldReport(unittest.TestCase):

    """Test about report generation, from scratch."""

    @classmethod
    def fixtures_dir(cls, path):
        """Helper to return fixture path."""
        directory_name = os.path.dirname(__file__)
        return os.path.join(directory_name, 'fixtures', path)

    def test_hello_world_report(self):
        """Test for creating hello world report.

        .. versionadded:: 4.1
        """
        QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()
        output_folder = self.fixtures_dir('../output/hello_world_report')

        # sneaky monkey patch
        ImpactFunction.outputs = ['Not implemented']
        impact_function = ImpactFunction()

        template_metadata = ReportMetadata(
            metadata_dict=hello_world_metadata_html)

        impact_report = ImpactReport(
            iface=IFACE,
            template_metadata=template_metadata,
            impact_function=impact_function)

        impact_report.output_folder = output_folder

        impact_report.process_components()
