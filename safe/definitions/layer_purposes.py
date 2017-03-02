# coding=utf-8

"""Definitions relating to exposure."""
from safe.definitions.concepts import concepts
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
}

layer_purpose_hazard = {
    'key': 'hazard',
    'name': tr('Hazard'),
    'description': concepts['hazard']['description'],
    'allowed_geometries': [
        layer_geometry_polygon,
        layer_geometry_raster
    ],
    'citations': concepts['hazard']['citations']
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
    ]
}

layer_purpose_exposure_summary = {
    'key': 'exposure_summary',
    'name': tr('Impact Layer - Exposure Summary'),
    'description': tr(
        'This <b>impact layer - exposure summary</b> contains all the '
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
    'key': 'aggregate_hazard_impacted',
    'name': tr('Aggregate Hazard Impacted'),
    'description': tr(
        'An <b>aggregate hazard impacted</b> layer is created during an '
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

layer_purpose_aggregation_impacted = {
    'key': 'aggregation_impacted',
    'name': tr('Aggregation Impacted'),
    'description': tr(
        'An <b>aggregate impacted</b> layer is created during an InaSAFE '
        'analysis. This layer contains the geometries from the original '
        'aggregation layer that were selected at the start of the analysis ('
        'or all of the analysis layer geometries if there was no selection '
        'when the analysis was started). If no aggregation layer was used '
        'for the analysis, the extent of the analysis area based on the '
        'intersection rules defined in the "Set Analysis Area" dialog will '
        'be used to create an aggregation layer. In this case the '
        'aggregation '
        'layer will consist of a single rectangular polygon geometry. '
        'If the exposure is indivisible (e.g. building polygons) or point '
        'based (e.g. places, building points), the the aggregate hazard '
        'impacted layer will include a count of the number of features per '
        'aggregation area and, if applicable, either the length or the area '
        'of the exposure features contained within each polygon. As well as '
        'simple metrics of counts, areas or distances, additional columns '
        'will be writen to the aggregation impacted layer breaking down '
        'features by their classes and providing other similar metrics.'),
    'allowed_geometries': [layer_geometry_polygon],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_purpose_analysis_impacted = {
    'key': 'analysis_impacted',
    'name': tr('Analysis Impacted'),
    'description': tr(
        'An <b>analysis impacted</b> layer is the result from InaSAFE '
        'analysis. It contains only one geometry polygon. This geometry is '
        'created by computing the outer bounding polygon of all of the '
        'aggregation layer features that were used for the analysis. Whereas '
        'the aggregation impacted layer provides summaries by the classes of '
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
    'allowed_geometries': [],
    'citations': [
        {
            'text': None,
            'link': None
        }
    ]
}

layer_purpose_profiling = {
    'key': 'profiling',
    'name': tr('Profiling'),
    'description': tr(
        'A <b>profiling</b> layer contains auxilliary information mainly '
        'intended for developers and power users. The data in the profiling '
        'table can be sent to the developers of InaSAFE should you be '
        'encountering particularly long analysis times so that they can '
        'identify any particular bottlenecks. This layer does not have a '
        'geometry.'),
    'allowed_geometries': [],
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
    'description': tr(
        'The purpose of the layer can be hazard layer, exposure layer, or '
        'aggregation layer'),
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
