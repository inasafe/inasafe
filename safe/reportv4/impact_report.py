# coding=utf-8
"""
Module to generate impact report using QgsComposition and Jinja2 Template
engine.
"""

import os
import logging
import imp
from qgis.core import (
    QgsComposition,
    QgsRectangle,
    QgsMapSettings,
    QgsComposerHtml,
    QgsComposerFrame)

from PyQt4.QtCore import QUrl
from safe.defaults import disclaimer
from safe.common.utilities import temp_dir, unique_filename
from safe.common.version import get_version
from safe.common.exceptions import (
    KeywordNotFoundError, TemplateLoadingError)
from safe import messaging as m
from safe.messaging import styles
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.gis import qgis_version
from safe.utilities.utilities import impact_attribution, html_to_file
from safe.utilities.resources import (
    html_footer, html_header, resource_url, resources_path)
from safe.utilities.i18n import tr
from safe.defaults import (
    white_inasafe_logo_path,
    black_inasafe_logo_path,
    supporters_logo_path,
    default_north_arrow_path)
from safe.impact_template.utilities import get_report_template

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

LOGGER = logging.getLogger('InaSAFE')


class InaSAFEReportContext(object):
    """A class to compile all InaSAFE related context for reporting uses"""
    def __init__(self):
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
        if isinstance(north_arrow_path, basestring) and os.path.exists(
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
        """Getter to black inasafe logo path

        :rtype: str
        """
        return self._black_inasafe_logo

    @property
    def white_inasafe_logo(self):
        """Getter for white inasafe logo path

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
        if isinstance(logo, basestring) and os.path.exists(logo):
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
        if not isinstance(text, basestring):
            self._disclaimer = disclaimer()
        else:
            self._disclaimer = text


class QGISCompositionContext(object):
    """A class to hold the value for QGISComposition object"""
    def __init__(self, extent, map_settings, page_dpi):
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
        """

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
        """

        :param value: Extent of map element to display
        :type value: QgsRectangle
        """
        self._extent = value

    @property
    def map_settings(self):
        """QgsMapSettings instance that will be used.

        Used for QgsComposition

        :rtype: QgsMapSettings
        """
        return self._map_settings

    @map_settings.setter
    def map_settings(self, value):
        """

        :param value: QgsMapSettings for QgsComposition
        :type value: QgsMapSettings
        """
        self._map_settings = value

    @property
    def plot_style(self):
        """Constant options for composition rendering style

        Possible values:
        - QgsComposition.PlotStyle.Preview
        - QgsComposition.PlotStyle.Render
        - QgsComposition.PlotStyle.Postscript

        :rtype: QgsComposition.PlotStyle
        """
        return self._plot_style

    @property
    def save_as_raster(self):
        """Boolean that indicates the composition will be saved as Raster

        :rtype: bool
        """
        return self._save_as_raster


class ImpactReport(object):

    # constant for default PAGE_DPI settings
    DEFAULT_PAGE_DPI = 300

    """A class for creating report using QgsComposition."""
    def __init__(
            self,
            iface,
            template_metadata,
            impact_layer,
            analysis_layer,
            extra_layers=[],
            minimum_needs_profile=None):
        """Constructor for the Composition Report class.

        :param iface: Reference to the QGIS iface object.
        :type iface: QgsAppInterface

        :param template_metadata: InaSAFE template metadata.
        :type template_metadata: ReportMetadata
        """
        LOGGER.debug('InaSAFE Impact Report class initialised')
        self._iface = iface
        self._metadata = template_metadata
        self._output_folder = None
        self._impact_layer = impact_layer
        self._analysis_layer = analysis_layer
        self._extra_layers = extra_layers
        self._minimum_needs = minimum_needs_profile
        self._extent = self._iface.mapCanvas().extent()
        self._inasafe_context = InaSAFEReportContext()

        # QgsMapSettings is added in 2.4
        map_settings = self._iface.mapCanvas().mapSettings()

        self._qgis_composition_context = QGISCompositionContext(
            self._iface.mapCanvas().extent(),
            map_settings,
            ImpactReport.DEFAULT_PAGE_DPI)
        self._keyword_io = KeywordIO()

    @property
    def inasafe_context(self):
        """Reference to default InaSAFE Context

        :rtype: InaSAFEReportContext
        """
        return self._inasafe_context

    @property
    def qgis_composition_context(self):
        """Reference to default QGIS Composition Context

        :rtype: QGISCompositionContext
        """
        return self._qgis_composition_context

    @property
    def metadata(self):
        """Getter to the template

        :return: ReportMetadata
        :rtype: safe.reportv4.report_metadata.ReportMetadata
        """
        return self._metadata

    @property
    def output_folder(self):
        """Output folder path for the rendering

        :rtype: str
        """
        return self._output_folder

    @output_folder.setter
    def output_folder(self, value):
        """

        :param value: output folder path
        :type value: str
        """
        self._output_folder = value
        if not os.path.exists(self._output_folder):
            os.makedirs(self._output_folder)

    @property
    def impact_layer(self):
        """Getter to layer that will be used for stats, legend, reporting.

        :rtype: qgis.core.QgsVectorLayer
        """
        return self._impact_layer

    @impact_layer.setter
    def impact_layer(self, layer):
        """Set the layer that will be used for stats, legend and reporting.

        :param layer: Layer that will be used for stats, legend and reporting.
        :type layer: qgis.core.QgsVectorLayer
        """
        self._impact_layer = layer

    @property
    def analysis_layer(self):
        """
        :return:
        :rtype: qgis.core.QgsVectorLayer
        """
        return self._analysis_layer

    @analysis_layer.setter
    def analysis_layer(self, layer):
        """

        :param layer: Analysis layer
        :type layer: qgis.core.QgsVectorLayer
        """
        self._analysis_layer = layer

    @property
    def extra_layers(self):
        """Getter to extra layers

        extra layers will be rendered alongside impact layer
        """
        return self._extra_layers

    @extra_layers.setter
    def extra_layers(self, extra_layers):
        """Set extra layers

        extra layers will be rendered alongside impact layer
        :param extra_layers: List of QgsMapLayer
        :type extra_layers: list(QgsMapLayer)
        """
        self._extra_layers = extra_layers

    @property
    def minimum_needs(self):
        """

        :return: minimum needs used in impact report
        :rtype: safe.gui.tools.minimum_needs.needs_profile.NeedsProfile
        """
        return self._minimum_needs

    @minimum_needs.setter
    def minimum_needs(self, value):
        """
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
                self.impact_layer, 'map_title')
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
                        self.impact_layer, legend_attribute)
            except KeywordNotFoundError:
                pass
            except Exception:  # pylint: disable=broad-except
                pass
        return legend_attribute_dict

    def process_component(self):
        """Process context for each component and a given template"""
        for component in self.metadata.components:
            # load extractors
            if callable(component.extractor):
                _extractor_method = component.extractor
            else:
                _package_name = '%s.extractors.%s' % (
                    self.metadata.key,
                    component.key
                )
                # replace dash with underscores
                _package_name = _package_name.replace('-', '_')
                _extractor_path = os.path.join(
                    self.metadata.template_folder,
                    component.extractor
                )
                _module = imp.load_source(_package_name, _extractor_path)
                _extractor_method = getattr(_module, 'extractor')
            try:
                # method signature:
                #  - this ImpactReport
                #  - this component
                context = _extractor_method(self, component)
                component.context = context
            except Exception as exc:
                LOGGER.exception(exc)

            # load processor
            if callable(component.processor):
                _renderer = component.processor
            else:
                _package_name = '%s.renderer.%s' % (
                    self.metadata.key,
                    component.key
                )
                # replace dash with underscores
                _package_name = _package_name.replace('-', '_')
                _renderer_path = os.path.join(
                    self.metadata.template_folder,
                    component.processor
                )
                _module = imp.load_source(_package_name, _renderer_path)
                _renderer = getattr(_module, 'renderer')
            try:
                # method signature:
                output = _renderer(self, component)
                component.output = output
            except Exception as exc:
                LOGGER.exception(exc)
