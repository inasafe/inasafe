# coding=utf-8

"""Definitions that will be used when describing the different analysis steps.
"""

from collections import OrderedDict

from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

# Note that we use an ordered dict for these definitions as we want them
# to show in a particular order in the definitions help. TS.
analysis_steps = OrderedDict()

analysis_steps['initialisation'] = {
    'key': 'initialisation',
    'name': tr('Analysis initialisation'),
    'description': tr(
        'In this phase we clear the impact function state and work logs.'),
    'icon': '.svg',
    'icon_credits': 'Not specified',
    'citations': [
        {
            'text': tr(''),
            'link': u''
        }
    ]
}
analysis_steps['data_store'] = {
    'key': 'data_store',
    'name': tr('Data store creation'),
    'description': tr(
        'In this phase we create a data store. The data store is a '
        'folder or GeoPackage containing all of the working data '
        'used for and produced by this analysis.'),
    'citations': [
        {
            'text': tr(''),
            'link': u''
        }
    ]
}
analysis_steps['pre_processing'] = {
    'key': 'pre_processing',
    'name': tr('Pre processing'),
    'description': tr(
        'During this step we check if we can create some side products based '
        'on your inputs.'),
    'citations': [
        {
            'text': tr(''),
            'link': u''
        }
    ]
}
analysis_steps['hazard_preparation'] = {
    'key': 'hazard_preparation',
    'name': tr('Hazard preparation'),
    'description': tr(
        'During the hazard preparation phase of the analysis, we convert '
        'the hazard data to a classified vector layer if it is not '
        'already in this format.'),
    'citations': [
        {
            'text': tr(''),
            'link': u''
        }
    ]
}
analysis_steps['exposure_preparation'] = {
    'key': 'exposure_preparation',
    'name': tr('Exposure preparation'),
    'description': tr(
        'During the exposure preparation phase of the analysis, we '
        'convert the exposure data to a usable format for the analysis.'),
    'citations': [
        {
            'text': tr(''),
            'link': u''
        }
    ]
}
analysis_steps['aggregation_preparation'] = {
    'key': 'aggregation_preparation',
    'name': tr('Aggregation preparation'),
    'description': tr(
        'During this step we prepare the aggregation data, extracting '
        'only the selected polygons from the aggregation layer, and '
        'reprojecting to aggregation data to the exposure layer\'s '
        'coordinate reference system.'),
    'citations': [
        {
            'text': tr(''),
            'link': u''
        }
    ]
}
analysis_steps['aggregate_hazard_preparation'] = {
    'key': 'aggregate_hazard_preparation',
    'name': tr('Aggregate hazard preparation'),
    'description': tr(
        'In this step we union the hazard data and the aggregation data '
        'then remove any of the resulting polygons that do not intersect '
        'the aggregation areas. Each resulting polygon stores the id and '
        'class of the hazard and the id and name from the aggregation '
        'area.'),
    'citations': [
        {
            'text': tr(''),
            'link': u''
        }
    ]
}

analysis_steps['combine_hazard_exposure'] = {
    'key': 'combine_hazard_exposure',
    'name': tr('Combine aggregate hazard and exposure'),
    'description': tr(
        'In this step we combine the aggregate hazard and exposure layers '
        'to produce an intermediate impact layer where each exposure '
        'feature has been assigned an aggregation id and name, hazard id '
        'and class and a column indicating whether the exposed feature '
        'is affected or not.'),
    'citations': [
        {
            'text': tr(''),
            'link': u''
        }
    ]
}
analysis_steps['post_processing'] = {
    'key': 'post_processing',
    'name': tr('Post processing'),
    'description': tr(
        'During this step we analyse each exposure feature to determine '
        'additional vulnerability attributes such as gender breakdown '
        'age breakdown, minimum needs and so on. This additional '
        'information is written into the impact layers.'),
    'citations': [
        {
            'text': tr(''),
            'link': u''
        }
    ]
}
analysis_steps['summary_calculation'] = {
    'key': 'summary',
    'name': tr('Summary calculation'),
    'description': tr(
        'At the end of the analysis we summarise the analysis results '
        'by aggregate hazard areas, aggregation areas and the total '
        'analysis area.'),
    'citations': [
        {
            'text': tr(''),
            'link': u''
        }
    ]
}
analysis_steps['profiling'] = {
    'key': 'profiling',
    'name': tr('Profiling'),
    'description': tr(
        'At the end of the analysis we extract profiling data so that '
        'we can provide a detailed work log and also help you to '
        'identify any bottlenecks in the processing flow.'),
    'citations': [
        {
            'text': tr(''),
            'link': u''
        }
    ]
}
