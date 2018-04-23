# coding=utf-8
"""Module used to generate context for impact table report.

This is useful to do layouting.
"""
from __future__ import absolute_import

from safe.report.extractors.composer import QGISComposerContext
from safe.report.extractors.util import (
    jinja2_output_as_string,
    resolve_from_dictionary)
from safe.utilities.resources import (
    resource_url,
    resources_path)

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def impact_table_extractor(impact_report, component_metadata):
    """Extracting impact summary of the impact layer.

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.report.report_metadata.
        ReportComponentsMetadata

    :return: context for rendering phase
    :rtype: dict

    .. versionadded:: 4.0
    """
    context = {}
    extra_args = component_metadata.extra_args

    components_list = resolve_from_dictionary(
        extra_args, 'components_list')

    # TODO: Decide either to use it or not
    if not impact_report.impact_function.debug_mode:
        # only show experimental MMI Detail when in debug mode
        components_list.pop('mmi_detail', None)

    context['brand_logo'] = resource_url(
        resources_path('img', 'logos', 'inasafe-logo-white.png'))
    for key, component in components_list.items():
        context[key] = jinja2_output_as_string(
            impact_report, component['key'])

    context['inasafe_resources_base_dir'] = resources_path()

    return context


def impact_table_pdf_extractor(impact_report, component_metadata):
    """Extracting impact summary of the impact layer.

    For PDF generations

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.report.report_metadata.
        ReportComponentsMetadata

    :return: context for rendering phase
    :rtype: dict

    .. versionadded:: 4.0
    """
    # QGIS Composer needed certain context to generate the output
    # - Map Settings
    # - Substitution maps
    # - Element settings, such as icon for picture file or image source

    context = QGISComposerContext()
    extra_args = component_metadata.extra_args

    html_report_component_key = resolve_from_dictionary(
        extra_args, ['html_report_component_key'])

    # we only have html elements for this
    html_frame_elements = [
        {
            'id': 'impact-report',
            'mode': 'text',
            'text': jinja2_output_as_string(
                impact_report, html_report_component_key),
            'margin_left': 10,
            'margin_top': 10,
        }
    ]
    context.html_frame_elements = html_frame_elements
    return context
