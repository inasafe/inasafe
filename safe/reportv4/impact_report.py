# coding=utf-8
"""
Module to generate impact report using QgsComposition and Jinja2 Template
engine.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'akbargumbira@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '21/03/2014'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import os
import logging
import imp
from importlib import import_module
from qgis.core import (
    QgsComposition,
    QgsRectangle,
    QgsMapLayer,
    QgsComposerPicture,
    QgsComposerHtml,
    QgsComposerFrame)
# Whoaa this is ugly can we get rid of it?
try:
    # noinspection PyUnresolvedReferences
    # pylint: disable=unused-import
    from qgis.core import QgsLayerTreeGroup, QgsMapSettings
    # pylint: enable=unused-import
except ImportError:
    from qgis.core import QgsMapRenderer

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

INFO_STYLE = styles.INFO_STYLE
LOGO_ELEMENT = m.Image(
    resource_url(
        resources_path('img', 'logos', 'inasafe-logo.png')),
    'InaSAFE Logo')
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
        """Getter to north arrow path."""
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
        """
        return self.black_inasafe_logo

    @property
    def black_inasafe_logo(self):
        return self._black_inasafe_logo

    @property
    def white_inasafe_logo(self):
        return self._white_inasafe_logo

    @property
    def organisation_logo(self):
        """Getter to organisation logo path."""
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
        """
        return self._supporters_logo

    @property
    def disclaimer(self):
        """Getter to disclaimer."""
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
        self._plot_style = QgsComposition.Preview
        self._save_as_raster = True

    @property
    def extent(self):
        return self._extent

    @extent.setter
    def extent(self, value):
        self._extent = value

    @property
    def map_settings(self):
        return self._map_settings

    @map_settings.setter
    def map_settings(self, value):
        self._map_settings = value

    @property
    def plot_style(self):
        return self._plot_style

    @property
    def save_as_raster(self):
        return self._save_as_raster


class ImpactReport(object):
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

        # For QGIS < 2.4 compatibility
        # QgsMapSettings is added in 2.4
        if qgis_version() < 20400:
            map_settings = self._iface.mapCanvas().mapRenderer()
        else:
            map_settings = self._iface.mapCanvas().mapSettings()

        self._qgis_composition_context = QGISCompositionContext(
            self._iface.mapCanvas().extent(),
            map_settings,
            300)
        self._keyword_io = KeywordIO()

    @property
    def inasafe_context(self):
        return self._inasafe_context

    @property
    def qgis_composition_context(self):
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
        return self._output_folder

    @output_folder.setter
    def output_folder(self, value):
        self._output_folder = value

    @property
    def impact_layer(self):
        """Getter to layer that will be used for stats, legend, reporting."""
        return self._impact_layer

    @impact_layer.setter
    def impact_layer(self, layer):
        """Set the layer that will be used for stats, legend and reporting.

        :param layer: Layer that will be used for stats, legend and reporting.
        :type layer: QgsMapLayer, QgsRasterLayer, QgsVectorLayer
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
        self._minimum_needs = value

    @property
    def map_title(self):
        """Get the map title from the layer keywords if possible.

        :returns: None on error, otherwise the title.
        :rtype: None, str
        """
        # noinspection PyBroadException
        try:
            title = self._keyword_io.read_keywords(self.impact_layer, 'map_title')
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

    def setup_composition(self):
        """Set up the composition ready."""
        # noinspection PyUnresolvedReferences
        self._template_composition.composition.setPlotStyle(
            QgsComposition.Preview)
        self._template_composition.composition.setPrintResolution(
            self.page_dpi)
        self._template_composition.composition.setPrintAsRaster(True)

    def load_template(self):
        """Load the template to composition."""
        # Get information for substitutions
        # date, time and plugin version
        date_time = self._keyword_io.read_keywords(self.layer, 'time_stamp')
        if date_time is None:
            date = ''
            time = ''
        else:
            tokens = date_time.split('_')
            date = tokens[0]
            time = tokens[1]
        long_version = get_version()
        tokens = long_version.split('.')
        version = '%s.%s.%s' % (tokens[0], tokens[1], tokens[2])
        # Get title of the layer
        title = self.map_title
        if not title:
            title = ''

        # Prepare the substitution map
        substitution_map = {
            'impact-title': title,
            'date': date,
            'time': time,
            'safe-version': version,  # deprecated
            'disclaimer': self.disclaimer,
            # These added in 3.2
            'version-title': tr('Version'),
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
                'Assessment carried out using InaSAFE release %s.' % version),
            'legend-title': tr('Legend'),
            'information-title': tr('Analysis information'),
            'supporters-title': tr('Report produced by')
        }

        # Load template
        self._template_composition.substitution = substitution_map
        try:
            self._template_composition.load_template()
        except TemplateLoadingError:
            raise

    @staticmethod
    def symbol_count(layer):
        """Get symbol count from whatever method we can get

        :param layer: QgsMapLayer
        :return: QgsMapLayer
        """
        try:
            return len(layer.legendSymbologyItems())
        except:
            pass

        try:
            return len(layer.rendererV2().legendSymbolItemsV2())
        except:
            pass

        return 1

    def draw_composition(self):
        """Draw all the components in the composition."""
        # This is deprecated - use inasafe-logo-<colour> rather
        safe_logo = self.composition.getComposerItemById(
            'safe-logo')
        # Next two options replace safe logo in 3.2
        black_inasafe_logo = self.composition.getComposerItemById(
            'black-inasafe-logo')
        white_inasafe_logo = self.composition.getComposerItemById(
            'white-inasafe-logo')
        north_arrow = self.composition.getComposerItemById(
            'north-arrow')
        organisation_logo = self.composition.getComposerItemById(
            'organisation-logo')
        supporters_logo = self.composition.getComposerItemById(
            'supporters-logo')

        if qgis_version() < 20600:
            if safe_logo is not None:
                # its deprecated so just use black_inasafe_logo
                safe_logo.setPictureFile(self.inasafe_logo)
            if black_inasafe_logo is not None:
                black_inasafe_logo.setPictureFile(self._black_inasafe_logo)
            if white_inasafe_logo is not None:
                white_inasafe_logo.setPictureFile(self._white_inasafe_logo)
            if north_arrow is not None:
                north_arrow.setPictureFile(self.north_arrow)
            if organisation_logo is not None:
                organisation_logo.setPictureFile(self.organisation_logo)
            if supporters_logo is not None:
                supporters_logo.setPictureFile(self.supporters_logo)
        else:
            if safe_logo is not None:
                # its deprecated so just use black_inasafe_logo
                safe_logo.setPicturePath(self.inasafe_logo)
            if black_inasafe_logo is not None:
                black_inasafe_logo.setPicturePath(self._black_inasafe_logo)
            if white_inasafe_logo is not None:
                white_inasafe_logo.setPicturePath(self._white_inasafe_logo)
            if north_arrow is not None:
                north_arrow.setPicturePath(self.north_arrow)
            if organisation_logo is not None:
                organisation_logo.setPicturePath(self.organisation_logo)
            if supporters_logo is not None:
                supporters_logo.setPicturePath(self.supporters_logo)

        # Set impact report table
        table = self.composition.getComposerItemById('impact-report')
        if table is not None:
            text = self._keyword_io.read_keywords(self.layer, 'impact_summary')
            if text is None:
                text = ''
            table.setText(text)
            table.setHtmlState(1)

        # Get the main map canvas on the composition and set its extents to
        # the event.
        composer_map = self.composition.getComposerItemById('impact-map')
        if composer_map is not None:
            # Recenter the composer map on the center of the extent
            # Note that since the composer map is square and the canvas may be
            # arbitrarily shaped, we center based on the longest edge
            canvas_extent = self.extent
            width = canvas_extent.width()
            height = canvas_extent.height()
            longest_width = width if width > height else height
            half_length = longest_width / 2
            center = canvas_extent.center()
            min_x = center.x() - half_length
            max_x = center.x() + half_length
            min_y = center.y() - half_length
            max_y = center.y() + half_length
            # noinspection PyCallingNonCallable
            square_extent = QgsRectangle(min_x, min_y, max_x, max_y)
            composer_map.setNewExtent(square_extent)

            # calculate intervals for grid
            split_count = 5
            x_interval = square_extent.width() / split_count
            composer_map.setGridIntervalX(x_interval)
            y_interval = square_extent.height() / split_count
            composer_map.setGridIntervalY(y_interval)

        legend = self.composition.getComposerItemById('impact-legend')
        if legend is not None:

            symbol_count = ImpactReport.symbol_count(self.layer)

            # add legend symbol count from extra_layers
            for l in self.extra_layers:
                symbol_count += ImpactReport.symbol_count(l)

            if symbol_count <= 5:
                legend.setColumnCount(1)
            else:
                legend.setColumnCount(symbol_count / 5 + 1)

            # Set back to blank to #2409
            legend.setTitle("")

            # Set Legend
            # Since QGIS 2.6, legend.model() is obsolete
            if qgis_version() < 20600:
                layer_set = [self.layer.id()]
                layer_set += [l.id() for l in self.extra_layers]
                legend.model().setLayerSet(layer_set)
                legend.synchronizeWithModel()
            else:
                root_group = legend.modelV2().rootGroup()
                root_group.addLayer(self.layer)
                for l in self.extra_layers:
                    root_group.addLayer(l)
                legend.synchronizeWithModel()

    def print_to_pdf(self, output_path):
        """A wrapper to print both the map and the impact table to PDF.

        :param output_path: Path on the file system to which the pdf should
            be saved. If None, a generated file name will be used. Note that
            the table will be prefixed with '_table'.
        :type output_path: str, unicode

        :returns: The map path and the table path to the pdfs generated.
        :rtype: tuple
        """
        # Print the map to pdf
        try:
            map_path = self.print_map_to_pdf(output_path)
        except TemplateLoadingError:
            raise

        # Print the table to pdf
        table_path = os.path.splitext(output_path)[0] + '_table.pdf'
        table_path = self.print_impact_table(table_path)

        return map_path, table_path

    def print_map_to_pdf(self, output_path):
        """Generate the printout for our final map as pdf.

        :param output_path: Path on the file system to which the pdf should be
            saved. If None, a generated file name will be used.
        :type output_path: str

        :returns: File name of the output file (equivalent to filename if
                provided).
        :rtype: str
        """
        LOGGER.debug('InaSAFE Map print_to_pdf called')
        self.setup_composition()
        try:
            self.load_template()
        except TemplateLoadingError:
            raise
        self.draw_composition()

        if output_path is None:
            output_path = unique_filename(
                prefix='report', suffix='.pdf', dir=temp_dir())

        self.composition.exportAsPDF(output_path)
        return output_path

    def print_impact_table(self, output_path):
        """Pint summary from impact layer to PDF.

        ..note:: The order of the report:
            1. Summary table
            2. Aggregation table
            3. Attribution table

        :param output_path: Output path.
        :type output_path: str

        :return: Path to generated pdf file.
        :rtype: str

        :raises: None
        """
        keywords = self._keyword_io.read_keywords(self.layer)

        if output_path is None:
            output_path = unique_filename(suffix='.pdf', dir=temp_dir())

        try:
            impact_template = get_report_template(self.layer.source())
            summary_table = impact_template.generate_html_report()
        except:
            summary_table = keywords.get('impact_summary', None)
        full_table = keywords.get('impact_table', None)
        aggregation_table = keywords.get('postprocessing_report', None)
        attribution_table = impact_attribution(keywords)

        # (AG) We will not use impact_table as most of the IF use that as:
        # impact_table = impact_summary + some information intended to be
        # shown on screen (see FloodOsmBuilding)
        # Unless the impact_summary is None, we will use impact_table as the
        # alternative
        html = m.Brand().to_html()
        html += m.Heading(tr('Analysis Results'), **INFO_STYLE).to_html()
        if summary_table is None:
            html += full_table
        else:
            html += summary_table

        if aggregation_table is not None:
            html += aggregation_table

        if attribution_table is not None:
            html += attribution_table.to_html()

        html = html_header() + html + html_footer()

        # Print HTML using composition
        # For QGIS < 2.4 compatibility
        # QgsMapSettings is added in 2.4
        if qgis_version() < 20400:
            map_settings = QgsMapRenderer()
        else:
            map_settings = QgsMapSettings()

        # A4 Portrait
        # TODO: Will break when we try to use larger print layouts TS
        paper_width = 210
        paper_height = 297

        # noinspection PyCallingNonCallable
        composition = QgsComposition(map_settings)
        # noinspection PyUnresolvedReferences
        composition.setPlotStyle(QgsComposition.Print)
        composition.setPaperSize(paper_width, paper_height)
        composition.setPrintResolution(300)

        # Add HTML Frame
        # noinspection PyCallingNonCallable
        html_item = QgsComposerHtml(composition, False)
        margin_left = 10
        margin_top = 10

        # noinspection PyCallingNonCallable
        html_frame = QgsComposerFrame(
            composition,
            html_item,
            margin_left,
            margin_top,
            paper_width - 2 * margin_left,
            paper_height - 2 * margin_top)
        html_item.addFrame(html_frame)

        # Set HTML
        # From QGIS 2.6, we can set composer HTML with manual HTML
        if qgis_version() < 20600:
            html_path = unique_filename(
                prefix='report', suffix='.html', dir=temp_dir())
            html_to_file(html, file_path=html_path)
            html_url = QUrl.fromLocalFile(html_path)
            html_item.setUrl(html_url)
        else:
            # noinspection PyUnresolvedReferences
            html_item.setContentMode(QgsComposerHtml.ManualHtml)
            # noinspection PyUnresolvedReferences
            html_item.setResizeMode(QgsComposerHtml.RepeatUntilFinished)
            html_item.setHtml(html)
            # RMN: This line below breaks in InaSAFE Headless after one
            # successful call. This is because the function is not
            # thread safe. Can't do anything about this, so avoid calling this
            # function in multithreaded way.
            html_item.loadHtml()

        composition.exportAsPDF(output_path)
        return output_path
