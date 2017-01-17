# coding=utf-8
import datetime

from safe.definitions.fields import analysis_name_field
from safe.report.extractors.util import value_from_field_name
from safe.utilities.i18n import tr
from safe.common.version import get_version

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


class QGISComposerContext(object):
    """Default context class for QGIS Composition

    The reason we made it a class is because things needed for composition
    were much more obvious and solid than Jinja2 template context.
    """

    def __init__(self):
        self._substitution_map = {}
        self._infographic_elements = []
        self._image_elements = []
        self._html_frame_elements = []
        self._map_elements = []
        self._map_legends = []

    @property
    def substitution_map(self):
        """

        :return: Substitution map containing dict mapping used in QGIS
            Composition template
        :rtype: dict
        """
        return self._substitution_map

    @substitution_map.setter
    def substitution_map(self, value):
        """

        :param value: Substitution map containing dict mapping used in QGIS
            Composition template
        :type value: dict
        """
        self._substitution_map = value

    @property
    def infographic_elements(self):
        """

        :return: Embedded infographics elements that needed to be generated
            for QGIS Composition
        :rtype: list(dict)
        """
        return self._infographic_elements

    @infographic_elements.setter
    def infographic_elements(self, value):
        """

        :param value: Embedded infographics elements that needed to be
            generated for QGIS Composition
        :type value: list(dict)
        """
        self._infographic_elements = value

    @property
    def image_elements(self):
        """

        :return: Scanned all the image elements in the composition that
            needed to be replaced
        :rtype: list(dict)
        """
        return self._image_elements

    @image_elements.setter
    def image_elements(self, value):
        """

        :param value: Scanned all the image elements in the composition that
            needed to be replaced
        :type value: list(dict)
        """
        self._image_elements = value

    @property
    def html_frame_elements(self):
        """

        :return: Scanned all html frame elements
        :rtype: list(dict)
        """
        return self._html_frame_elements

    @html_frame_elements.setter
    def html_frame_elements(self, value):
        """

        :param value: Scanned all html frame elements
        :type value: list(dict)
        """
        self._html_frame_elements = value

    @property
    def map_elements(self):
        """

        :return: Scanned all map elements
        :rtype: list(dict)
        """
        return self._map_elements

    @map_elements.setter
    def map_elements(self, value):
        """

        :param value: Scanned all map elements
        :type value: list(dict)
        """
        self._map_elements = value

    @property
    def map_legends(self):
        """

        :return: Scanned all map legends element
        :rtype: list(dict)
        """
        return self._map_legends

    @map_legends.setter
    def map_legends(self, value):
        """

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
    """
    # QGIS Composer needed certain context to generate the output
    # - Map Settings
    # - Substitution maps
    # - Element settings, such as icon for picture file or image source

    # Generate map settings
    qgis_context = impact_report.qgis_composition_context
    inasafe_context = impact_report.inasafe_context
    provenance = impact_report.impact_function.provenance

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

    # Set default map to resize

    map_elements = [
        {
            'id': 'impact-map',
            'extent': qgis_context.extent,
            'grid_split_count': 5,
        }
    ]
    context.map_elements = map_elements

    # calculate map_legends
    layers = [impact_report.impact] + impact_report.extra_layers
    symbol_count = 0
    for l in layers:
        layer = l
        """:type: qgis.core.QgsMapLayer"""
        try:
            symbol_count += len(layer.legendSymbologyItems())
            continue
        except:
            pass
        try:
            symbol_count += len(layer.rendererV2().legendSymbolItemsV2())
            continue
        except:
            pass
        symbol_count += 1

    legend_title = provenance['map_legend_title'] or ''

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
    date_time = provenance['datetime']
    """:type: datetime.datetime"""
    if isinstance(date_time, datetime.datetime):
        date = date_time.strftime('%Y-%m-%d')
        time = date_time.strftime('%H:%M')
    else:
        date = ''
        time = ''
    long_version = get_version()
    tokens = long_version.split('.')
    version = '%s.%s.%s' % (tokens[0], tokens[1], tokens[2])
    # Get title of the layer
    title = provenance['map_title']

    # Set source
    hazard_source = (
        provenance['hazard_keywords'].get('source') or tr('Unknown'))
    exposure_source = (
        provenance['exposure_keywords'].get('source') or tr('Unknown'))
    if provenance['aggregation_layer']:
        aggregation_source = (
            provenance['aggregation_keywords'].get('source') or tr('Unknown'))
    else:
        aggregation_source = tr('Not used')

    reference_name = tr('Geographic Coordinates - {crs}').format(
        crs=impact_report.impact_function.impact.crs().authid())

    analysis_layer = impact_report.analysis
    analysis_name = value_from_field_name(
        analysis_name_field['field_name'], analysis_layer)

    # Prepare the substitution map
    substitution_map = {
        'impact-title': title,
        'date': date,
        'time': time,
        'safe-version': version,  # deprecated
        'disclaimer': inasafe_context.disclaimer,
        # These added in 3.2
        'version-title': tr('Software Version'),
        'inasafe-version': version,
        'disclaimer-title': tr('Disclaimer'),
        'date-title': tr('Date'),
        'time-title': tr('Time'),
        'caution-title': tr('Note'),
        'caution-text': tr(
            'This assessment is a guide - we strongly recommend that you '
            'ground truth the results shown here before deploying '
            'resources and / or personnel.'),
        'version-text': tr(
            'InaSAFE %s' % version),
        'legend-title': tr('Legend'),
        'information-title': tr('Analysis information'),
        'supporters-title': tr('Report produced by'),
        'source-title': tr('Data Source'),
        'analysis-title': tr('Analysis Name'),
        'analysis-name': analysis_name,
        'reference-title': tr('Spatial Reference'),
        'reference-name': reference_name,
        'hazard-source': hazard_source,
        'exposure-source': exposure_source,
        'aggregation-source': aggregation_source,
    }
    context.substitution_map = substitution_map
    return context
