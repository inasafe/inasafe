# coding=utf-8
from safe.common.parameters.resource_parameter import ResourceParameter
from safe.definitionsv4.minimum_needs import (
    minimum_needs_fields,
    minimum_needs_namespace)
from safe.reportv4.extractors.util import round_affecter_number
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def minimum_needs_extractor(impact_report, component_metadata):
    """
    Extracting minimum needs of the impact layer

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.reportv4.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.reportv4.report_metadata.ReportMetadata

    :return: context for rendering phase
    :rtype: dict
    """
    context = {}

    analysis_layer = impact_report.analysis
    analysis_keywords = analysis_layer.keywords['inasafe_fields']

    # minimum needs calculation only affect population type exposure
    # check if analysis keyword have minimum_needs keywords
    have_minimum_needs_field = False
    for field_key in analysis_keywords:
        if field_key.startswith(minimum_needs_namespace):
            have_minimum_needs_field = True
            break

    if not have_minimum_needs_field:
        return context

    frequencies = {}
    # map each needs to its frequency groups
    for field in minimum_needs_fields:
        need_parameter = field['need_parameter']
        if isinstance(need_parameter, ResourceParameter):
            if need_parameter.frequency not in frequencies:
                frequencies[need_parameter.frequency] = [field]
            else:
                frequencies[need_parameter.frequency].append(field)

    needs = []
    analysis_feature = analysis_layer.getFeatures().next()
    # group the needs by frequency
    for key, frequency in frequencies.iteritems():
        group = {
            'header': tr('Relief items to be provided %s') % tr(key),
            'total_header': tr('Total'),
            'needs': []
        }
        for field in frequency:
            # check value exists in the field
            field_idx = analysis_layer.fieldNameIndex(field['field_name'])
            if field_idx == -1:
                # skip if field doesn't exists
                continue
            value = round_affecter_number(analysis_feature[field_idx], False)
            if value == 0:
                # skip if no needs needed
                continue

            need_parameter = field['need_parameter']
            """:type: ResourceParameter"""
            header = need_parameter.name
            if need_parameter.unit.abbreviation:
                header = '%s [%s]' % (
                    header, need_parameter.unit.abbreviation)
            item = {
                'header': header,
                'value': value
            }
            group['needs'].append(item)
        needs.append(group)

    # TODO: perhaps title needs to be specific to exposure type
    context['header'] = tr('Minimum needs')
    context['needs'] = needs

    return context
