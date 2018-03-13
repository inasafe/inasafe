# coding=utf-8

"""Definitions relating to exposure."""
from safe.definitions.concepts import concepts
from safe.definitions.field_groups import aggregation_field_groups
from safe.definitions.keyword_properties import property_layer_purpose
from safe.definitions.layer_geometry import (
    layer_geometry_raster,
    layer_geometry_line,
    layer_geometry_point,
    layer_geometry_polygon
)
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

layer_purpose_exposure = {
    'key': 'exposure',
    'name': tr('Exposure'),
    'description': concepts['exposure']['description'],
    'allowed_geometries': [
        layer_geometry_point,
        layer_geometry_line,
        layer_geometry_polygon,
        layer_geometry_raster
    ],
    'citations': concepts['exposure']['citations'],
    'field_groups': []  # Set in each exposure definition
}

layer_purpose_hazard = {
    'key': 'hazard',
    'name': tr('Hazard'),
    'description': concepts['hazard']['description'],
    'allowed_geometries': [
        layer_geometry_polygon,
        layer_geometry_raster
    ],
    'citations': concepts['hazard']['citations'],
    'field_groups': []  # Set in each exposure definition
}

layer_purpose_aggregation = {
    'key': 'aggregation',
    'name': tr('Aggregation'),
    'description': tr(
        'An <b>aggregation</b> layer represents regions that can be used to '
        'summarise impact analysis results. For example, we might summarise '
        'the affected people after a flood according to administration '
        'boundaries.'),
    'allowed_geometries': [layer_geometry_polygon],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ],
    'field_groups': aggregation_field_groups
}

layer_purpose_exposure_summary = {
    'key': 'impact_analysis',
    'name': tr('Impact Analysis'),
    'description': tr(
        'This <b>Impact Analysis</b> contains all the '
        'results for the spatial analysis of the hazard, exposure and '
        'aggregation layers (if used) within the analysis extent. This '
        'layer is not created if the input includes a continuous raster '
        'exposure layer (eg population raster).'),
    'allowed_geometries': [
        layer_geometry_point, layer_geometry_line, layer_geometry_polygon],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_purpose_aggregate_hazard_impacted = {
    'key': 'hazard_aggregation_summary',
    'name': tr('Hazard Aggregation Summary'),
    'description': tr(
        'An <b>hazard aggregation summary</b> is created during an '
        'InaSAFE analysis. This layer is a cross product between the hazard '
        'layer, the aggregate layer and the exposure summary layer. The '
        'layer geometries are firstly a union between the hazard layer and '
        'the aggregation layer. If the exposure is indivisible (e.g. '
        'building polygons) or point based (e.g. places, building points), '
        'the the aggregate hazard impacted layer will include a count of the '
        'number of features per intersected aggregate hazard polygon and, if '
        'applicable, either the length or the area of the exposure features '
        'contained within each polygon. If the exposure data is divisible ('
        'e.g'
        '. landcover polygons), those polygons will again be unioned with '
        'the '
        'output from the aggregation layer / hazard layer intersection '
        'process'
        '. As well as simple metrics of area or distance, additional columns '
        'will be writen to the aggregate hazard layer breaking down features '
        'by their classes and providing other similar metrics.'
    ),
    'allowed_geometries': [layer_geometry_polygon],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_purpose_aggregation_summary = {
    'key': 'aggregation_summary',
    'name': tr('Aggregation Summary'),
    'multi_exposure_name': tr('Combined Aggregation Summary'),
    'description': tr(
        "This <b>aggregation summary</b> contains the "
        "analysis results for each exposure type by hazard type, summarised "
        "by aggregation area. Where an aggregation layer was not used; the "
        "analysis area is defined by the extent of the input layers or the "
        "'analysis extent' set by the user."),
    'allowed_geometries': [layer_geometry_polygon],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

# multi_exposure_name is a special name for the legend if we do a multi
# exposure analysis

layer_purpose_analysis_impacted = {
    'key': 'analysis_summary',
    'name': tr('Analysis Summary'),
    'multi_exposure_name': tr('Combined Analysis Summary'),
    'description': tr(
        'An <b>analysis summary</b> layer is the result from InaSAFE '
        'analysis. It contains only one geometry polygon. This geometry is '
        'created by computing the outer bounding polygon of all of the '
        'aggregation layer features that were used for the analysis. Whereas '
        'the aggregation summary layer provides summaries by the classes of '
        'exposure feature types, the analysis impacted layer provides '
        'summaries by <b>hazard zone</b>. For example, when carrying out an '
        'impact assessment of flood on roads, the analysis impacted layer '
        'will contain columns with "wet" and "dry" counts for roads.'),
    'allowed_geometries': [layer_geometry_polygon],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_purpose_exposure_summary_table = {
    'key': 'exposure_summary_table',
    'name': tr('Exposure Summary Table'),
    'description': tr(
        'This <b>exposure summary table</b> contains the analysis results '
        'for exposure type by hazard type, summarised by exposure type. It '
        'includes totals for affected and not affected status. It is used '
        'to generate reports and can be exported to a spreadsheet for '
        'further analysis.'),
    'allowed_geometries': [],  # It's a table.
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_purpose_profiling = {
    'key': 'analysis_log',
    'name': tr('Analysis Log'),
    'description': tr(
        'The <b>analysis log</b> contains information intended for '
        'developers and power users. The data in the analysis log can be '
        'sent to the developers of InaSAFE if you encounter long processing '
        'times. They will use the information to identify processing '
        'bottlenecks.'),
    'allowed_geometries': [],  # It's a table.
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_purpose_nearby_places = {
    'key': 'nearby_places',
    'name': tr('Nearby Places'),
    'description': tr('Lorem ipsum on the nearby places layers.'),
    'allowed_geometries': [layer_geometry_point],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_purpose_earthquake_contour = {
    'key': 'earthquake_contour',
    'name': tr('Earthquake Contour'),
    'description': tr('A contour of a hazard earthquake'),
    'allowed_geometries': [layer_geometry_line],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_purpose = {
    'key': 'layer_purpose',
    'name': tr('Purpose'),
    'description': property_layer_purpose['description'],
    'types': [
        layer_purpose_hazard,
        layer_purpose_exposure,
        layer_purpose_aggregation
    ],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_purposes = [
    layer_purpose_hazard,
    layer_purpose_exposure,
    layer_purpose_aggregation
]
