# coding=utf-8
"""Module to generate impact report.

Enable dynamic report generation based on report metadata.
Easily customize map report or document based report.

"""


import imp
import logging
import os
import shutil

from qgis.core import QgsComposition, QgsRasterLayer, QgsMapSettings

from safe import messaging as m
from safe.common.exceptions import (
    KeywordNotFoundError)
from safe.defaults import (
    white_inasafe_logo_path,
    black_inasafe_logo_path,
    supporters_logo_path,
    default_north_arrow_path)
from safe.definitions.messages import disclaimer
from safe.messaging import styles
from safe.utilities.i18n import tr
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.utilities import get_error_message
import collections

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

SUGGESTION_STYLE = styles.GREEN_LEVEL_4_STYLE
WARNING_STYLE = styles.RED_LEVEL_4_STYLE

LOGGER = logging.getLogger('InaSAFE')


class InaSAFEReportContext():

    """A class to compile all InaSAFE related context for reporting uses.

    .. versionadded:: 4.0
    """

    def __init__(self):
        """Create InaSAFE Report context."""
        self._black_inasafe_logo = black_inasafe_logo_path()
        self._white_inasafe_logo = white_inasafe_logo_path()
        # User can change this path in preferences
        self._organisation_logo = supporters_logo_path()
        self._supporters_logo = supporters_logo_path()
        self._north_arrow = default_north_arrow_path()
        self._disclaimer = disclaimer()

    @property
    def north_arrow(self):
        """Getter to north arrow path.

        :rtype: str
        """
        return self._north_arrow

    @north_arrow.setter
    def north_arrow(self, north_arrow_path):
        """Set image that will be used as north arrow in reports.

        :param north_arrow_path: Path to the north arrow image.
        :type north_arrow_path: str
        """
        if isinstance(north_arrow_path, str) and os.path.exists(
                north_arrow_path):
            self._north_arrow = north_arrow_path
        else:
            self._north_arrow = default_north_arrow_path()

    @property
    def inasafe_logo(self):
        """Getter to safe logo path.

        .. versionchanged:: 3.2 - this property is now read only.

        :rtype: str
        """
        return self.black_inasafe_logo

    @property
    def black_inasafe_logo(self):
        """Getter to black inasafe logo path.

        :rtype: str
        """
        return self._black_inasafe_logo

    @property
    def white_inasafe_logo(self):
        """Getter for white inasafe logo path.

        :rtype: str
        """
        return self._white_inasafe_logo

    @property
    def organisation_logo(self):
        """Getter to organisation logo path.

        :rtype: str
        """
        return self._organisation_logo

    @organisation_logo.setter
    def organisation_logo(self, logo):
        """Set image that will be used as organisation logo in reports.

        :param logo: Path to the organisation logo image.
        :type logo: str
        """
        if isinstance(logo, str) and os.path.exists(logo):
            self._organisation_logo = logo
        else:
            self._organisation_logo = supporters_logo_path()

    @property
    def supporters_logo(self):
        """Getter to supporters logo path - this is a read only property.

        It always returns the InaSAFE supporters logo unlike the organisation
        logo which is customisable.

        .. versionadded:: 3.2
        :rtype: str
        """
        return self._supporters_logo

    @property
    def disclaimer(self):
        """Getter to disclaimer.

        :rtype: str
        """
        return self._disclaimer

    @disclaimer.setter
    def disclaimer(self, text):
        """Set text that will be used as disclaimer in reports.

        :param text: Disclaimer text
        :type text: str
        """
        if not isinstance(text, str):
            self._disclaimer = disclaimer()
        else:
            self._disclaimer = text


class QGISCompositionContext():

    """A class to hold the value for QGISComposition object.

    .. versionadded:: 4.0
    """

    def __init__(self, extent, map_settings, page_dpi):
        """Create QGISComposition context."""
        self._extent = extent
        self._map_settings = map_settings
        self._page_dpi = page_dpi
        self._plot_style = QgsComposition.Print
        self._save_as_raster = True

    @property
    def page_dpi(self):
        """The Page DPI that QGISComposition uses.

        Can be overriden by report metadata

        :rtype: float
        """
        return self._page_dpi

    @page_dpi.setter
    def page_dpi(self, value):
        """Page DPI.

        :param value: DPI value for printing
        :type value: float
        """
        self._page_dpi = value

    @property
    def extent(self):
        """The extent of the map element.

        This extent is used by map element to render the extent
        of the layer

        :rtype: QgsRectangle
        """
        return self._extent

    @extent.setter
    def extent(self, value):
        """Extent of map element.

        :param value: Extent of map element to display
        :type value: QgsRectangle
        """
        self._extent = value

    @property
    def map_settings(self):
        """QgsMapSettings instance that will be used.

        Used for QgsComposition

        :rtype: qgis.core.QgsMapSettings
        """
        return self._map_settings

    @map_settings.setter
    def map_settings(self, value):
        """QgsMapSettings instance.

        :param value: QgsMapSettings for QgsComposition
        :type value: qgis.core.QgsMapSettings
        """
        self._map_settings = value

    @property
    def plot_style(self):
        """Constant options for composition rendering style.

        Possible values:
        - QgsComposition.PlotStyle.Preview
        - QgsComposition.PlotStyle.Render
        - QgsComposition.PlotStyle.Postscript

        :rtype: QgsComposition.PlotStyle
        """
        return self._plot_style

    @property
    def save_as_raster(self):
        """Boolean that indicates the composition will be saved as Raster.

        :rtype: bool
        """
        return self._save_as_raster


class ImpactReport():

    """A class for creating and generating report.

    .. versionadded:: 4.0
    """

    # constant for default PAGE_DPI settings
    DEFAULT_PAGE_DPI = 300
    REPORT_GENERATION_SUCCESS = 0
    REPORT_GENERATION_FAILED = 1

    class LayerException(Exception):

        """Class for Layer Exception.

        Raised if layer being used is not valid.
        """

        pass

    def __init__(
            self,
            iface,
            template_metadata,
            impact_function=None,
            hazard=None,
            exposure=None,
            impact=None,
            analysis=None,
            exposure_summary_table=None,
            aggregation_summary=None,
            extra_layers=None,
            ordered_layers=None,
            legend_layers=None,
            minimum_needs_profile=None,
            multi_exposure_impact_function=None,
            use_template_extent=False):
        """Constructor for the Composition Report class.

        :param iface: Reference to the QGIS iface object.
        :type iface: QgsAppInterface

        :param template_metadata: InaSAFE template metadata.
        :type template_metadata: ReportMetadata

        :param impact_function: Impact function instance for the report
        :type impact_function:
            safe.impact_function.impact_function.ImpactFunction

        .. versionadded:: 4.0
        """
        LOGGER.debug('InaSAFE Impact Report class initialised')
        self._iface = iface
        self._metadata = template_metadata
        self._output_folder = None
        self._impact_function = impact_function or (
            multi_exposure_impact_function)
        self._hazard = hazard or self._impact_function.hazard
        self._analysis = (analysis or self._impact_function.analysis_impacted)
        if impact_function:
            self._exposure = (
                exposure or self._impact_function.exposure)
            self._impact = (
                impact or self._impact_function.impact)
            self._exposure_summary_table = (
                exposure_summary_table or
                self._impact_function.exposure_summary_table)
            self._aggregation_summary = (
                aggregation_summary or
                self._impact_function.aggregation_summary)
        if extra_layers is None:
            extra_layers = []
        self._extra_layers = extra_layers
        self._ordered_layers = ordered_layers
        self._legend_layers = legend_layers
        self._minimum_needs = minimum_needs_profile
        self._multi_exposure_impact_function = multi_exposure_impact_function
        self._use_template_extent = use_template_extent
        self._inasafe_context = InaSAFEReportContext()

        # QgsMapSettings is added in 2.4
        if self._iface:
            map_settings = self._iface.mapCanvas().mapSettings()
        else:
            map_settings = QgsMapSettings()

        self._qgis_composition_context = QGISCompositionContext(
            None,
            map_settings,
            ImpactReport.DEFAULT_PAGE_DPI)
        self._keyword_io = KeywordIO()

    @property
    def inasafe_context(self):
        """Reference to default InaSAFE Context.

        :rtype: InaSAFEReportContext
        """
        return self._inasafe_context

    @property
    def qgis_composition_context(self):
        """Reference to default QGIS Composition Context.

        :rtype: QGISCompositionContext
        """
        return self._qgis_composition_context

    @property
    def metadata(self):
        """Getter to the template.

        :return: ReportMetadata
        :rtype: safe.report.report_metadata.ReportMetadata
        """
        return self._metadata

    @property
    def output_folder(self):
        """Output folder path for the rendering.

        :rtype: str
        """
        return self._output_folder

    @output_folder.setter
    def output_folder(self, value):
        """Output folder path for the rendering.

        :param value: output folder path
        :type value: str
        """
        self._output_folder = value
        if not os.path.exists(self._output_folder):
            os.makedirs(self._output_folder)

    @staticmethod
    def absolute_output_path(
            output_folder, components, component_key):
        """Return absolute output path of component.

        :param output_folder: The base output folder
        :type output_folder: str

        :param components: The list of components to look up
        :type components: list[ReportMetadata]

        :param component_key: The component key
        :type component_key: str

        :return: absolute output path
        :rtype: str

        .. versionadded:: 4.0
        """
        comp_keys = [c.key for c in components]

        if component_key in comp_keys:
            idx = comp_keys.index(component_key)
            output_path = components[idx].output_path
            if isinstance(output_path, str):
                return os.path.abspath(
                    os.path.join(output_folder, output_path))
            elif isinstance(output_path, list):
                output_list = []
                for path in output_path:
                    output_list.append(os.path.abspath(
                        os.path.join(output_folder, path)))
                return output_list
            elif isinstance(output_path, dict):
                output_dict = {}
                for key, path in list(output_path.items()):
                    output_dict[key] = os.path.abspath(
                        os.path.join(output_folder, path))
                return output_dict
        return None

    def component_absolute_output_path(self, component_key):
        """Return absolute output path of component.

        :param component_key: The component key
        :type component_key: str

        :return: absolute output path
        :rtype: str

        .. versionadded:: 4.0
        """
        return ImpactReport.absolute_output_path(
            self.output_folder,
            self.metadata.components,
            component_key)

    @property
    def impact_function(self):
        """Getter for impact function instance to use.

        :rtype: safe.impact_function.impact_function.ImpactFunction
        """
        return self._impact_function

    @property
    def multi_exposure_impact_function(self):
        """Getter for multi impact function instance to use.

        We define this property because we want to avoid the usage of
        impact_function property when there is multi exposure impact function
        being used.

        :rtype: MultiExposureImpactFunction
        """
        return self._multi_exposure_impact_function

    def _check_layer_count(self, layer):
        """Check for the validity of the layer.

        :param layer: QGIS layer
        :type layer: qgis.core.QgsVectorLayer
        :return:
        """
        if layer:
            if not layer.isValid():
                raise ImpactReport.LayerException('Layer is not valid')
            if isinstance(layer, QgsRasterLayer):
                # can't check feature count of raster layer
                return
            feature_count = len([f for f in layer.getFeatures()])
            if feature_count == 0:
                raise ImpactReport.LayerException(
                    'Layer contains no features')

    @property
    def hazard(self):
        """Getter to hazard layer.

        :rtype: qgis.core.QgsVectorLayer
        """
        self._check_layer_count(self._hazard)
        return self._hazard

    @hazard.setter
    def hazard(self, layer):
        """Hazard layer.

        :param layer: hazard layer
        :type layer: qgis.core.QgsVectorLayer
        """
        self._hazard = layer

    @property
    def exposure(self):
        """Getter to exposure layer.

        :rtype: qgis.core.QgsVectorLayer
        """
        self._check_layer_count(self._exposure)
        return self._exposure

    @exposure.setter
    def exposure(self, layer):
        """Exposure layer.

        :param layer: exposure layer
        :type layer: qgis.core.QgsVectorLayer
        """
        self._impact = layer

    @property
    def impact(self):
        """Getter to layer that will be used for stats, legend, reporting.

        :rtype: qgis.core.QgsVectorLayer
        """
        self._check_layer_count(self._impact)
        return self._impact

    @impact.setter
    def impact(self, layer):
        """Set the layer that will be used for stats, legend and reporting.

        :param layer: Layer that will be used for stats, legend and reporting.
        :type layer: qgis.core.QgsVectorLayer
        """
        self._impact = layer

    @property
    def analysis(self):
        """Analysis layer.

        :rtype: qgis.core.QgsVectorLayer
        """
        self._check_layer_count(self._analysis)
        return self._analysis

    @analysis.setter
    def analysis(self, layer):
        """Analysis layer.

        :param layer: Analysis layer
        :type layer: qgis.core.QgsVectorLayer
        """
        self._analysis = layer

    @property
    def exposure_summary_table(self):
        """Exposure summary table.

        :rtype: qgis.core.QgsVectorLayer
        """
        # self._check_layer_count(self._exposure_summary_table)
        return self._exposure_summary_table

    @exposure_summary_table.setter
    def exposure_summary_table(self, value):
        """Exposure summary table.

        :param value: Exposure Summary Table
        :type value: qgis.core.QgsVectorLayer
        :return:
        """
        self._exposure_summary_table = value

    @property
    def aggregation_summary(self):
        """Aggregation summary.

        :rtype: qgis.core.QgsVectorLayer
        """
        self._check_layer_count(self._aggregation_summary)
        return self._aggregation_summary

    @aggregation_summary.setter
    def aggregation_summary(self, value):
        """Aggregation summary.

        :param value: Aggregation Summary
        :type value: qgis.core.QgsVectorLayer
        """
        self._aggregation_summary = value

    @property
    def extra_layers(self):
        """Getter to extra layers.

        extra layers will be rendered alongside impact layer
        """
        return self._extra_layers

    @extra_layers.setter
    def extra_layers(self, extra_layers):
        """Set extra layers.

        extra layers will be rendered alongside impact layer

        :param extra_layers: List of QgsMapLayer
        :type extra_layers: list(QgsMapLayer)
        """
        self._extra_layers = extra_layers

    @property
    def ordered_layers(self):
        """Getter to ordered layers.

        Ordered layers will determine the layers order on map report.
        :return:
        """
        return self._ordered_layers

    @ordered_layers.setter
    def ordered_layers(self, ordered_layers):
        """Set ordered layers.

        Ordered layers will determine the layers order on map report.

        :param ordered_layers:
        :return:
        """
        self._ordered_layers = ordered_layers

    @property
    def legend_layers(self):
        """Getter to legend layers.

        Legend layers will determine the legend on map report.

        :return: List of legend layers.
        :rtype: list
        """
        return self._legend_layers

    @legend_layers.setter
    def legend_layers(self, legend_layers):
        """Set legend layers.

        Legend layers will determine the legend on map report.

        :param legend_layers: List of legend layers.
        :type legend_layers: list
        """
        self._legend_layers = legend_layers

    @property
    def use_template_extent(self):
        """Getter to the flag for using template extent.

        If True, map report will use extent defined in the template. If False,
        map report will use analysis extent.

        :return: The flag for using template extent or not.
        :rtype: bool
        """
        return self._use_template_extent

    @property
    def minimum_needs(self):
        """Minimum needs.

        :return: minimum needs used in impact report
        :rtype: safe.gui.tools.minimum_needs.needs_profile.NeedsProfile
        """
        return self._minimum_needs

    @minimum_needs.setter
    def minimum_needs(self, value):
        """Minimum needs.

        :param value: minimum needs used in impact report
        :type value: safe.gui.tools.minimum_needs.needs_profile.NeedsProfile
        """
        self._minimum_needs = value

    @property
    def map_title(self):
        """Get the map title from the layer keywords if possible.

        :returns: None on error, otherwise the title.
        :rtype: None, str
        """
        # noinspection PyBroadException
        try:
            title = self._keyword_io.read_keywords(
                self.impact, 'map_title')
            return title
        except KeywordNotFoundError:
            return None
        except Exception:  # pylint: disable=broad-except
            return None

    @property
    def map_legend_attributes(self):
        """Get the map legend attribute from the layer keywords if possible.

        :returns: None on error, otherwise the attributes (notes and units).
        :rtype: None, str
        """
        LOGGER.debug('InaSAFE Map getMapLegendAttributes called')
        legend_attribute_list = [
            'legend_notes',
            'legend_units',
            'legend_title']
        legend_attribute_dict = {}
        for legend_attribute in legend_attribute_list:
            # noinspection PyBroadException
            try:
                legend_attribute_dict[legend_attribute] = \
                    self._keyword_io.read_keywords(
                        self.impact, legend_attribute)
            except KeywordNotFoundError:
                pass
            except Exception:  # pylint: disable=broad-except
                pass
        return legend_attribute_dict

    def process_components(self):
        """Process context for each component and a given template.

        :returns: Tuple of error code and message
        :type: tuple

        .. versionadded:: 4.0
        """
        message = m.Message()
        warning_heading = m.Heading(
            tr('Report Generation issue'), **WARNING_STYLE)
        message.add(warning_heading)
        failed_extract_context = m.Heading(tr(
            'Failed to extract context'), **WARNING_STYLE)
        failed_render_context = m.Heading(tr(
            'Failed to render context'), **WARNING_STYLE)
        failed_find_extractor = m.Heading(tr(
            'Failed to load extractor method'), **WARNING_STYLE)
        failed_find_renderer = m.Heading(tr(
            'Failed to load renderer method'), **WARNING_STYLE)

        generation_error_code = self.REPORT_GENERATION_SUCCESS

        for component in self.metadata.components:
            # load extractors
            try:
                if not component.context:
                    if isinstance(component.extractor, collections.Callable):
                        _extractor_method = component.extractor
                    else:
                        _package_name = (
                            '%(report-key)s.extractors.%(component-key)s')
                        _package_name %= {
                            'report-key': self.metadata.key,
                            'component-key': component.key
                        }
                        # replace dash with underscores
                        _package_name = _package_name.replace('-', '_')
                        _extractor_path = os.path.join(
                            self.metadata.template_folder,
                            component.extractor
                        )
                        _module = imp.load_source(
                            _package_name, _extractor_path)
                        _extractor_method = getattr(_module, 'extractor')
                else:
                    LOGGER.info('Predefined context. Extractor not needed.')
            except Exception as e:  # pylint: disable=broad-except
                generation_error_code = self.REPORT_GENERATION_FAILED
                LOGGER.info(e)
                if not self.impact_function.use_rounding:
                    raise
                else:
                    message.add(failed_find_extractor)
                    message.add(component.info)
                    message.add(get_error_message(e))
                    continue

            # method signature:
            #  - this ImpactReport
            #  - this component
            try:
                if not component.context:
                    context = _extractor_method(self, component)
                    component.context = context
                else:
                    LOGGER.info('Using predefined context.')
            except Exception as e:  # pylint: disable=broad-except
                generation_error_code = self.REPORT_GENERATION_FAILED
                LOGGER.info(e)
                if not self.impact_function.use_rounding:
                    raise
                else:
                    message.add(failed_extract_context)
                    message.add(get_error_message(e))
                    continue

            try:
                # load processor
                if isinstance(component.processor, collections.Callable):
                    _renderer = component.processor
                else:
                    _package_name = '%(report-key)s.renderer.%(component-key)s'
                    _package_name %= {
                        'report-key': self.metadata.key,
                        'component-key': component.key
                    }
                    # replace dash with underscores
                    _package_name = _package_name.replace('-', '_')
                    _renderer_path = os.path.join(
                        self.metadata.template_folder,
                        component.processor
                    )
                    _module = imp.load_source(_package_name, _renderer_path)
                    _renderer = getattr(_module, 'renderer')
            except Exception as e:  # pylint: disable=broad-except
                generation_error_code = self.REPORT_GENERATION_FAILED
                LOGGER.info(e)
                if not self.impact_function.use_rounding:
                    raise
                else:
                    message.add(failed_find_renderer)
                    message.add(component.info)
                    message.add(get_error_message(e))
                    continue

            # method signature:
            #  - this ImpactReport
            #  - this component
            if component.context:
                try:
                    output = _renderer(self, component)
                    output_path = self.component_absolute_output_path(
                        component.key)
                    if isinstance(output_path, dict):
                        try:
                            dirname = os.path.dirname(output_path.get('doc'))
                        except:
                            dirname = os.path.dirname(output_path.get('map'))
                    else:
                        dirname = os.path.dirname(output_path)
                    if component.resources:
                        for resource in component.resources:
                            target_resource = os.path.basename(resource)
                            target_dir = os.path.join(
                                dirname, 'resources', target_resource)
                            # copy here
                            if os.path.exists(target_dir):
                                shutil.rmtree(target_dir)
                            shutil.copytree(resource, target_dir)
                    component.output = output
                except Exception as e:  # pylint: disable=broad-except
                    generation_error_code = self.REPORT_GENERATION_FAILED
                    LOGGER.info(e)
                    if not self.impact_function.use_rounding:
                        raise
                    else:
                        message.add(failed_render_context)
                        message.add(get_error_message(e))
                        continue

        return generation_error_code, message
