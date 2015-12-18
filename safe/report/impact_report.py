# coding=utf-8
"""
Module to generate impact report using QgsComposition.

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

# noinspection PyUnresolvedReferences
from qgis.core import (
    QgsComposition,
    QgsRectangle,
    QgsMapLayer,
    QgsComposerHtml,
    QgsComposerFrame)

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
from safe.utilities.resources import resources_path
from safe.utilities.gis import qgis_version
from safe.utilities.utilities import impact_attribution, html_to_file
from safe.utilities.resources import html_footer, html_header, resource_url
from safe.utilities.i18n import tr
from safe.defaults import (
    white_inasafe_logo_path,
    black_inasafe_logo_path,
    supporters_logo_path,
    default_north_arrow_path)
from safe.report.template_composition import TemplateComposition

INFO_STYLE = styles.INFO_STYLE
LOGO_ELEMENT = m.Image(
    resource_url(
        resources_path('img', 'logos', 'inasafe-logo.png')),
    'InaSAFE Logo')
LOGGER = logging.getLogger('InaSAFE')


class ImpactReport(object):
    """A class for creating report using QgsComposition."""
    def __init__(self, iface, template, layer):
        """Constructor for the Composition Report class.

        :param iface: Reference to the QGIS iface object.
        :type iface: QgsAppInterface

        :param template: The QGIS template path.
        :type template: str
        """
        LOGGER.debug('InaSAFE Impact Report class initialised')
        self._iface = iface
        self._template = template
        self._layer = layer
        self._extent = self._iface.mapCanvas().extent()
        self._page_dpi = 300.0
        self._black_inasafe_logo = black_inasafe_logo_path()
        self._white_inasafe_logo = white_inasafe_logo_path()
        # User can change this path in preferences
        self._organisation_logo = supporters_logo_path()
        self._supporters_logo = supporters_logo_path()
        self._north_arrow = default_north_arrow_path()
        self._disclaimer = disclaimer()

        # For QGIS < 2.4 compatibility
        # QgsMapSettings is added in 2.4
        if qgis_version() < 20400:
            map_settings = self._iface.mapCanvas().mapRenderer()
        else:
            map_settings = self._iface.mapCanvas().mapSettings()

        self._template_composition = TemplateComposition(
            template_path=self.template,
            map_settings=map_settings)
        self._keyword_io = KeywordIO()

    @property
    def template(self):
        """Getter to the template"""
        return self._template

    @template.setter
    def template(self, template):
        """Set template that will be used for report generation.

        :param template: Path to composer template
        :type template: str
        """
        if isinstance(template, basestring) and os.path.exists(template):
            self._template = template
        else:
            self._template = resources_path(
                'qgis-composer-templates', 'a4-portrait-blue.qpt')

        # Also recreate template composition
        self._template_composition = TemplateComposition(
            template_path=self.template,
            map_settings=self._iface.mapCanvas().mapSettings())

    @property
    def layer(self):
        """Getter to layer that will be used for stats, legend, reporting."""
        return self._layer

    @layer.setter
    def layer(self, layer):
        """Set the layer that will be used for stats, legend and reporting.

        :param layer: Layer that will be used for stats, legend and reporting.
        :type layer: QgsMapLayer, QgsRasterLayer, QgsVectorLayer
        """
        self._layer = layer

    @property
    def composition(self):
        """Getter to QgsComposition instance."""
        return self._template_composition.composition

    @property
    def extent(self):
        """Getter to extent for map component in composition."""
        return self._extent

    @extent.setter
    def extent(self, extent):
        """Set the extent that will be used for map component in composition.

        :param extent: The extent.
        :type extent: QgsRectangle
        """
        if isinstance(extent, QgsRectangle):
            self._extent = extent
        else:
            self._extent = self._iface.mapCanvas().extent()

    @property
    def page_dpi(self):
        """Getter to page resolution in dots per inch."""
        return self._page_dpi

    @page_dpi.setter
    def page_dpi(self, page_dpi):
        """Set the page resolution in dpi.

        :param page_dpi: The page resolution in dots per inch.
        :type page_dpi: int
        """
        self._page_dpi = page_dpi

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
        return self._black_inasafe_logo

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

    @property
    def component_ids(self):
        """Getter to the component ids"""
        return self._template_composition.component_ids

    @component_ids.setter
    def component_ids(self, component_ids):
        """Set the component ids.

        :param component_ids: The component IDs that are needed in the
            composition.
        :type component_ids: list
        """
        if not isinstance(component_ids, list):
            self._template_composition.component_ids = []
        else:
            self._template_composition.component_ids = component_ids

    @property
    def missing_elements(self):
        """Getter to the missing elements."""
        return self._template_composition.missing_elements

    @property
    def map_title(self):
        """Get the map title from the layer keywords if possible.

        :returns: None on error, otherwise the title.
        :rtype: None, str
        """
        # noinspection PyBroadException
        try:
            title = self._keyword_io.read_keywords(self.layer, 'map_title')
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
                        self.layer, legend_attribute)
            except KeywordNotFoundError:
                pass
            except Exception:  # pylint: disable=broad-except
                pass
        return legend_attribute_dict

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
            longest_width = width
            if width < height:
                longest_width = height
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

            symbol_count = 1
            # noinspection PyUnresolvedReferences
            if self.layer.type() == QgsMapLayer.VectorLayer:
                renderer = self.layer.rendererV2()
                if renderer.type() in ['', '']:
                    symbol_count = len(self.layer.legendSymbologyItems())
            else:
                renderer = self.layer.renderer()
                if renderer.type() in ['']:
                    symbol_count = len(self.layer.legendSymbologyItems())

            if symbol_count <= 5:
                legend.setColumnCount(1)
            else:
                legend.setColumnCount(symbol_count / 5 + 1)

            # Set back to blank to #2409
            legend.setTitle("")

            # Set Legend
            # Since QGIS 2.6, legend.model() is obsolete
            if qgis_version() < 20600:
                legend.model().setLayerSet([self.layer.id()])
                legend.synchronizeWithModel()
            else:
                root_group = legend.modelV2().rootGroup()
                root_group.addLayer(self.layer)
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
            html_item.loadHtml()

        composition.exportAsPDF(output_path)
        return output_path
