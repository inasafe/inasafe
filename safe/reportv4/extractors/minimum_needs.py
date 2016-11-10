# coding=utf-8
from safe.common.parameters.resource_parameter import ResourceParameter
from safe.definitionsv4.exposure import exposure_population
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

    needs_profile = impact_report.minimum_needs
    exposure_layer = impact_report.exposure
    analysis_layer = impact_report.analysis

    # minimum needs calculation only affect population type exposure
    if not exposure_layer.keywords['exposure'] == exposure_population['key']:
        return context

    frequencies = {}
    # map each needs to its frequency groups
    for n in needs_profile.get_needs_parameters():
        need_parameter = n
        if isinstance(need_parameter, ResourceParameter):
            if need_parameter.frequency not in frequencies:
                frequencies[need_parameter.frequency] = [need_parameter]
            else:
                frequencies[need_parameter.frequency].append(need_parameter)

    needs = []
    # group the needs by frequency
    for key, freq in frequencies.iteritems():
        group = {
            'header': tr('Relief items to be provided %s') % tr(key),
            'total_header': tr('Total'),
            'needs': []
        }
        for n in freq:
            need_parameter = n
            """:type: ResourceParameter"""
            header = need_parameter.name
            if need_parameter.unit.abbreviation:
                header = '%s [%s]' % (
                    header, need_parameter.unit.abbreviation)
            need_index = analysis_layer.fieldNameIndex(
                need_parameter.name)
            feat = analysis_layer.getFeatures().next()
            item = {
                'header': header,
                'value': feat[need_index]
            }
            group['needs'].append(item)
        needs.append(group)

    # TODO: perhaps title needs to be specific to exposure type
    context['header'] = tr('Minimum needs')
    context['needs'] = needs

    return context
