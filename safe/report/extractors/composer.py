# coding=utf-8
"""Module used to generate context for composer related rendering.

Particular example are:
- Map rendering
- PDF rendering
- PNG rendering

"""

import datetime
from copy import deepcopy

from qgis.core import QgsMapLayerRegistry

from safe.common.version import get_version
from safe.definitions.fields import analysis_name_field
from safe.definitions.provenance import (
    provenance_exposure_layer_id,
    provenance_multi_exposure_layers_id)
from safe.definitions.reports.infographic import (
    html_frame_elements,
    population_chart,
    inasafe_logo_white,
    image_item_elements, map_overview)
from safe.report.extractors.util import (
    value_from_field_name,
    resolve_from_dictionary,
    jinja2_output_as_string)
from safe.utilities.settings import setting

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class QGISComposerContext():

    """Default context class for QGIS Composition.

    The reason we made it a class is because things needed for composition
    were much more obvious and solid than Jinja2 template context.

    .. versionadded:: 4.0
    """

    def __init__(self):
        """Create QGIS Composer context."""
        self._substitution_map = {}
        self._infographic_elements = []
        self._image_elements = []
        self._html_frame_elements = []
        self._map_elements = []
        self._map_legends = []

    @property
    def substitution_map(self):
        """Substitution map.

        :return: Substitution map containing dict mapping used in QGIS
            Composition template
        :rtype: dict
        """
        return self._substitution_map

    @substitution_map.setter
    def substitution_map(self, value):
        """Substitution map.

        :param value: Substitution map containing dict mapping used in QGIS
            Composition template
        :type value: dict
        """
        self._substitution_map = value

    @property
    def infographic_elements(self):
        """Infographic elements.

        :return: Embedded infographics elements that needed to be generated
            for QGIS Composition
        :rtype: list(dict)
        """
        return self._infographic_elements

    @infographic_elements.setter
    def infographic_elements(self, value):
        """Infographic elements.

        :param value: Embedded infographics elements that needed to be
            generated for QGIS Composition
        :type value: list(dict)
        """
        self._infographic_elements = value

    @property
    def image_elements(self):
        """Image elements.

        :return: Scanned all the image elements in the composition that
            needed to be replaced
        :rtype: list(dict)
        """
        return self._image_elements

    @image_elements.setter
    def image_elements(self, value):
        """Image elements.

        :param value: Scanned all the image elements in the composition that
            needed to be replaced
        :type value: list(dict)
        """
        self._image_elements = value

    @property
    def html_frame_elements(self):
        """HTML frame elements.

        :return: Scanned all html frame elements
        :rtype: list(dict)
        """
        return self._html_frame_elements

    @html_frame_elements.setter
    def html_frame_elements(self, value):
        """HTML frame elements.

        :param value: Scanned all html frame elements
        :type value: list(dict)
        """
        self._html_frame_elements = value

    @property
    def map_elements(self):
        """Map elements.

        :return: Scanned all map elements
        :rtype: list(dict)
        """
        return self._map_elements

    @map_elements.setter
    def map_elements(self, value):
        """Map elements.

        :param value: Scanned all map elements
        :type value: list(dict)
        """
        self._map_elements = value

    @property
    def map_legends(self):
        """Map legends.

        :return: Scanned all map legends element
        :rtype: list(dict)
        """
        return self._map_legends

    @map_legends.setter
    def map_legends(self, value):
        """Map legends.

        :param value: Scanned all map legends
        :type value: list(dict)
        """
        self._map_legends = value


def qgis_composer_extractor(impact_report, component_metadata):
    """Extract composer context.

    This method extract necessary context for a given impact report and
    component metadata and save the context so it can be used in composer
    rendering phase

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

    # Generate map settings
    qgis_context = impact_report.qgis_composition_context
    inasafe_context = impact_report.inasafe_context
    provenance = impact_report.impact_function.provenance
    extra_args = component_metadata.extra_args

    context = QGISComposerContext()

    # Set default image elements to replace
    image_elements = [
        {
            'id': 'safe-logo',
            'path': inasafe_context.inasafe_logo
        },
        {
            'id': 'black-inasafe-logo',
            'path': inasafe_context.black_inasafe_logo
        },
        {
            'id': 'white-inasafe-logo',
            'path': inasafe_context.white_inasafe_logo
        },
        {
            'id': 'north-arrow',
            'path': inasafe_context.north_arrow
        },
        {
            'id': 'organisation-logo',
            'path': inasafe_context.organisation_logo
        },
        {
            'id': 'supporters_logo',
            'path': inasafe_context.supporters_logo
        }
    ]
    context.image_elements = image_elements

    # Set default HTML Frame elements to replace
    html_frame_elements = [
        {
            'id': 'impact-report',
            'mode': 'text',  # another mode is url
            'text': '',  # TODO: get impact summary table
        }
    ]
    context.html_frame_elements = html_frame_elements

    """Define the layers for the impact map."""

    project = QgsProject.instance()
    layers = []

    exposure_summary_layers = []
    if impact_report.multi_exposure_impact_function:
        for impact_function in (
                impact_report.multi_exposure_impact_function.impact_functions):
            impact_layer = impact_function.exposure_summary or (
                impact_function.aggregate_hazard_impacted)
            exposure_summary_layers.append(impact_layer)

    # use custom ordered layer if any
    if impact_report.ordered_layers:
        for layer in impact_report.ordered_layers:
            layers.append(layer)

        # We are keeping this if we want to enable below behaviour again.
        # Currently realtime might have layer order without impact layer in it.

        # # make sure at least there is an impact layer
        # if impact_report.multi_exposure_impact_function:
        #     additional_layers = []  # for exposure summary layers
        #     impact_layer_found = False
        #     impact_functions = (
        #        impact_report.multi_exposure_impact_function.impact_functions)
        #     # check for impact layer occurrences
        #     for analysis in impact_functions:
        #         impact_layer = analysis.exposure_summary or (
        #             analysis.aggregate_hazard_impacted)
        #         for index, layer in enumerate(layers):
        #             if impact_layer.source() == layer.source():
        #                 add_impact_layers_to_canvas(analysis)
        #                 layers[index] = impact_layer
        #                 impact_layer_found = True
        #     if not impact_layer_found:
        #         for analysis in impact_functions:
        #             add_impact_layers_to_canvas(analysis)
        #             impact_layer = analysis.exposure_summary or (
        #                 analysis.aggregate_hazard_impacted)
        #             layer_uri = full_layer_uri(impact_layer)
        #             layer = load_layer_from_registry(layer_uri)
        #             additional_layers.append(layer)
        #     layers = additional_layers + layers
        # else:
        #     impact_layer = (
        #         impact_report.impact_function.exposure_summary or (
        #             impact_report.impact_function.aggregate_hazard_impacted))
        #     if impact_layer not in layers:
        #         layers.insert(0, impact_layer)

    # use default layer order if no custom ordered layer found
    else:
        if not impact_report.multi_exposure_impact_function:  # single IF
            layers = [impact_report.impact] + impact_report.extra_layers
        else:  # multi-exposure IF
            layers = [] + impact_report.extra_layers

        add_supplementary_layers = (
            not impact_report.multi_exposure_impact_function or not (
                impact_report.multi_exposure_impact_function.
                output_layers_ordered)
        )
        if add_supplementary_layers:
            # Check show only impact.
            show_only_impact = setting(
                'set_show_only_impact_on_report', expected_type=bool)
            if not show_only_impact:
                hazard_layer = project.mapLayers().get(
                    provenance['hazard_layer_id'], None)

                aggregation_layer_id = provenance['aggregation_layer_id']
                if aggregation_layer_id:
                    aggregation_layer = project.mapLayers().get(
                        aggregation_layer_id, None)
                    layers.append(aggregation_layer)

                layers.append(hazard_layer)

            # check hide exposure settings
            hide_exposure_flag = setting(
                'setHideExposureFlag', expected_type=bool)
            if not hide_exposure_flag:
                exposure_layers_id = []
                if provenance.get(
                        provenance_exposure_layer_id['provenance_key']):
                    exposure_layers_id.append(
                        provenance.get(
                            provenance_exposure_layer_id['provenance_key']))
                elif provenance.get(
                        provenance_multi_exposure_layers_id['provenance_key']):
                    exposure_layers_id = provenance.get(
                        provenance_multi_exposure_layers_id['provenance_key'])

                # place exposure at the bottom
                for layer_id in exposure_layers_id:
                    exposure_layer = project.mapLayers().get(layer_id)
                    layers.append(exposure_layer)

    # default extent is analysis extent
    if not qgis_context.extent:
        qgis_context.extent = impact_report.impact_function.analysis_extent

    map_elements = [
        {
            'id': 'impact-map',
            'extent': qgis_context.extent,
            'grid_split_count': 5,
            'layers': layers,
        }
    ]
    context.map_elements = map_elements

    # calculate map_legends, only show the legend for impact layer
    if impact_report.legend_layers:  # use requested legend if any
        layers = impact_report.legend_layers
    elif impact_report.multi_exposure_impact_function:  # multi-exposure IF
        layers = exposure_summary_layers
    else:  # single IF
        layers = [impact_report.impact]
    symbol_count = 0
    for l in layers:
        layer = l
        """:type: qgis.core.QgsMapLayer"""
        try:
            symbol_count += len(layer.legendSymbologyItems())
            continue
        except Exception:  # pylint: disable=broad-except
            pass
        try:
            symbol_count += len(layer.rendererV2().legendSymbolItemsV2())
            continue
        except Exception:  # pylint: disable=broad-except
            pass
        symbol_count += 1

    legend_title = provenance.get('map_legend_title') or ''

    map_legends = [
        {
            'id': 'impact-legend',
            'title': legend_title,
            'layers': layers,
            'symbol_count': symbol_count,
            # 'column_count': 2,  # the number of column in legend display
        }
    ]
    context.map_legends = map_legends

    # process substitution map
    start_datetime = provenance['start_datetime']
    """:type: datetime.datetime"""
    date_format = resolve_from_dictionary(extra_args, 'date-format')
    time_format = resolve_from_dictionary(extra_args, 'time-format')
    if isinstance(start_datetime, datetime.datetime):
        date = start_datetime.strftime(date_format)
        time = start_datetime.strftime(time_format)
    else:
        date = ''
        time = ''
    long_version = get_version()
    tokens = long_version.split('.')
    version = '%s.%s.%s' % (tokens[0], tokens[1], tokens[2])
    # Get title of the layer
    title = provenance.get('map_title') or ''

    # Set source
    unknown_source_text = resolve_from_dictionary(
        extra_args, ['defaults', 'unknown_source'])
    aggregation_not_used = resolve_from_dictionary(
        extra_args, ['defaults', 'aggregation_not_used'])

    hazard_source = (
        provenance.get(
            'hazard_keywords', {}).get('source') or unknown_source_text)
    exposure_source = (
        provenance.get(
            'exposure_keywords', {}).get('source') or unknown_source_text)
    if provenance['aggregation_layer']:
        aggregation_source = (
            provenance['aggregation_keywords'].get('source') or
            unknown_source_text)
    else:
        aggregation_source = aggregation_not_used

    spatial_reference_format = resolve_from_dictionary(
        extra_args, 'spatial-reference-format')
    reference_name = spatial_reference_format.format(
        crs=impact_report.impact_function.crs.authid())

    analysis_layer = impact_report.analysis
    analysis_name = value_from_field_name(
        analysis_name_field['field_name'], analysis_layer)

    # Prepare the substitution map
    version_title = resolve_from_dictionary(extra_args, 'version-title')
    disclaimer_title = resolve_from_dictionary(extra_args, 'disclaimer-title')
    date_title = resolve_from_dictionary(extra_args, 'date-title')
    time_title = resolve_from_dictionary(extra_args, 'time-title')
    caution_title = resolve_from_dictionary(extra_args, 'caution-title')
    caution_text = resolve_from_dictionary(extra_args, 'caution-text')
    version_text = resolve_from_dictionary(extra_args, 'version-text')
    legend_section_title = resolve_from_dictionary(
        extra_args, 'legend-title')
    information_title = resolve_from_dictionary(
        extra_args, 'information-title')
    supporters_title = resolve_from_dictionary(
        extra_args, 'supporters-title')
    source_title = resolve_from_dictionary(extra_args, 'source-title')
    analysis_title = resolve_from_dictionary(extra_args, 'analysis-title')
    reference_title = resolve_from_dictionary(
        extra_args, 'spatial-reference-title')
    substitution_map = {
        'impact-title': title,
        'date': date,
        'time': time,
        'safe-version': version,  # deprecated
        'disclaimer': inasafe_context.disclaimer,
        # These added in 3.2
        'version-title': version_title,
        'inasafe-version': version,
        'disclaimer-title': disclaimer_title,
        'date-title': date_title,
        'time-title': time_title,
        'caution-title': caution_title,
        'caution-text': caution_text,
        'version-text': version_text.format(version=version),
        'legend-title': legend_section_title,
        'information-title': information_title,
        'supporters-title': supporters_title,
        'source-title': source_title,
        'analysis-title': analysis_title,
        'analysis-name': analysis_name,
        'reference-title': reference_title,
        'reference-name': reference_name,
        'hazard-source': hazard_source,
        'exposure-source': exposure_source,
        'aggregation-source': aggregation_source,
    }
    context.substitution_map = substitution_map
    return context


def qgis_composer_infographic_extractor(impact_report, component_metadata):
    """Extract composer context specific for infographic template.

    This method extract necessary context for a given impact report and
    component metadata and save the context so it can be used in composer
    rendering phase

    :param impact_report: the impact report that acts as a proxy to fetch
        all the data that extractor needed
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component_metadata: the component metadata. Used to obtain
        information about the component we want to render
    :type component_metadata: safe.report.report_metadata.
        ReportComponentsMetadata

    :return: context for rendering phase
    :rtype: dict

    .. versionadded:: 4.2
    """
    qgis_context = impact_report.qgis_composition_context
    extra_args = component_metadata.extra_args

    context = QGISComposerContext()

    """Image Elements."""

    # get all image elements with their respective source path
    image_elements = deepcopy(image_item_elements)

    # remove inasafe_logo_white because we use expression for the image source
    image_elements.remove(inasafe_logo_white)
    # remove population_chart because we still don't have the source path
    image_elements.remove(population_chart)
    context.image_elements = image_elements

    # get the source path of population_chart
    population_donut_path = impact_report.component_absolute_output_path(
        'population-chart-png')
    population_chart['path'] = population_donut_path

    context.image_elements.append(population_chart)

    """HTML Elements."""

    components = resolve_from_dictionary(extra_args, 'components')
    html_elements = deepcopy(html_frame_elements)

    # get the html content from component that has been proceed
    for element in html_elements:
        component = components.get(element['component'])
        if component:
            element['text'] = jinja2_output_as_string(
                impact_report, component['key'])

    context.html_frame_elements = html_elements

    """Map Elements."""

    map_overview_layer = None
    project = QgsProject.instance()
    for layer in list(project.mapLayers().values()):
        if layer.name() == map_overview['id']:
            map_overview_layer = layer

    layers = [impact_report.impact_function.analysis_impacted]

    if map_overview_layer:
        layers.append(map_overview_layer)

    # default extent is analysis extent
    if not qgis_context.extent:
        qgis_context.extent = impact_report.impact_function.analysis_extent

    map_elements = [
        {
            'id': 'map-overview',
            'extent': qgis_context.extent,
            'grid_split_count': 5,
            'layers': layers,
        }
    ]

    context.map_elements = map_elements

    return context
