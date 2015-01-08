# coding=utf-8
"""
Module to generate report using QgsComposition.

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
    QgsLayerTreeGroup)

from safe.defaults import disclaimer
from safe.common.utilities import temp_dir, unique_filename
from safe.common.version import get_version
from safe.common.exceptions import (
    KeywordNotFoundError, LoadingTemplateError)
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.resources import resources_path
from safe.utilities.gis import qgis_version
from safe.defaults import (
    default_organisation_logo_path,
    default_north_arrow_path)
from safe.report.template_composition import TemplateComposition

LOGGER = logging.getLogger('InaSAFE')


class MapReport(object):
    """A class for creating report using QgsComposition."""
    def __init__(self, iface, template, layer):
        """Constructor for the Composition Report class.

        :param iface: Reference to the QGIS iface object.
        :type iface: QgsAppInterface

        :param template: The QGIS template path.
        :type template: str
        """
        LOGGER.debug('InaSAFE Map class initialised')

        self.iface = iface
        self.keyword_io = KeywordIO()
        self.page_dpi = 300.0

        self._template = template
        self._layer = layer
        self._template_composition = None
        self._extent = self.iface.mapCanvas().extent()
        self._safe_logo = resources_path(
            'img', 'logos', 'inasafe-logo-url.svg')
        self._org_logo = default_organisation_logo_path()
        self._north_arrow = default_north_arrow_path()
        self._disclaimer = disclaimer()
        self._template_composition = TemplateComposition(
            template_path=self.template,
            map_settings=self.iface.mapCanvas().mapSettings())

    @property
    def template(self):
        """Getter to the template"""
        return self._template

    @template.setter
    def template(self, template):
        """Set the template.

        :param template: The template.
        :type template: str
        """
        self._template = template

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
        self._extent = extent

    @property
    def template(self):
        """Getter to the template path."""
        return self._template

    @template.setter
    def template(self, template):
        """Set template that will be used for report generation.

        :param template: Path to composer template
        :type template: str
        """
        if isinstance(template, str) and os.path.exists(template):
            self._template = template
        else:
            self._template = resources_path(
                'qgis-composer-templates', 'inasafe-portrait-a4.qpt')

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
        if isinstance(north_arrow_path, str) and os.path.exists(
                north_arrow_path):
            self._north_arrow = north_arrow_path
        else:
            self._north_arrow = default_north_arrow_path()

    @property
    def safe_logo(self):
        """Getter to safe logo path."""
        return self._safe_logo

    @safe_logo.setter
    def safe_logo(self, logo):
        """Set image that will be used as safe logo in reports.

        :param logo: Path to the safe logo image.
        :type logo: str
        """
        if isinstance(logo, str) and os.path.exists(logo):
            self._safe_logo = logo
        else:
            self._safe_logo = default_organisation_logo_path()

    @property
    def org_logo(self):
        """Getter to organisation logo path."""
        return self._org_logo

    @org_logo.setter
    def org_logo(self, logo):
        """Set image that will be used as organisation logo in reports.

        :param logo: Path to the organisation logo image.
        :type logo: str
        """
        if isinstance(logo, str) and os.path.exists(logo):
            self._org_logo = logo
        else:
            self._org_logo = default_organisation_logo_path()

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
        if not isinstance(text, str):
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
        try:
            title = self.keyword_io.read_keywords(self.layer, 'map_title')
            return title
        except KeywordNotFoundError:
            return None
        except Exception:
            return None

    def setup_composition(self):
        """Set up the composition ready."""
        # noinspection PyUnresolvedReferences
        self._template_composition.composition.setPlotStyle(
            QgsComposition.Preview)
        self._template_composition.composition.setPrintResolution(self.page_dpi)
        self._template_composition.composition.setPrintAsRaster(True)

    def load_template(self):
        """Load the template to composition."""
        # Get information for substitutions
        # date, time and plugin version
        date_time = self.keyword_io.read_keywords(self.layer, 'time_stamp')
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
            'safe-version': version,
            'disclaimer': self.disclaimer
        }

        # Load template
        self._template_composition.substitution = substitution_map
        try:
            self._template_composition.load_template()
        except LoadingTemplateError:
            raise

    def draw_composition(self):
        """Draw all the components in the composition."""
        # Set InaSAFE logo
        image = self.composition.getComposerItemById('safe-logo')
        if image is not None:
            if qgis_version() < 20500:
                image.setPictureFile(self.safe_logo)
            else:
                image.setPicturePath(self.safe_logo)

        # Set north arrow
        image = self.composition.getComposerItemById('north-arrow')
        if image is not None:
            if qgis_version() < 20500:
                image.setPictureFile(self.north_arrow)
            else:
                image.setPicturePath(self.north_arrow)

        # Set organisation logo
        image = self.composition.getComposerItemById('organisation-logo')
        if image is not None:
            if qgis_version() < 20500:
                image.setPictureFile(self.org_logo)
            else:
                image.setPicturePath(self.org_logo)

        # Set impact report table
        table = self.composition.getComposerItemById('impact-report')
        if table is not None:
            text = self.keyword_io.read_keywords(self.layer, 'impact_summary')
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
            legend_attributes = self.map_legend_attributes()
            legend_title = legend_attributes.get('legend_title', None)

            symbol_count = 1
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

            if legend_title is None:
                legend_title = ""
            legend.setTitle(legend_title)

            # Set Legend
            # From QGIS 2.6, legend.model() is obsolete
            if qgis_version() < 20600:
                legend.model().setLayerSet([self.layer.id()])
                legend.synchronizeWithModel()
            else:
                root_group = legend.modelV2().rootGroup()
                root_group.addLayer(self.layer)
                legend.synchronizeWithModel()

    def print_to_pdf(self, output_path):
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
        except LoadingTemplateError:
            raise
        self.draw_composition()

        if output_path is None:
            output_path = unique_filename(
                prefix='report', suffix='.pdf', dir=temp_dir())

        self.composition.exportAsPDF(output_path)
        return output_path

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
                    self.keyword_io.read_keywords(
                        self.layer, legend_attribute)
            except KeywordNotFoundError:
                pass
            except Exception:
                pass
        return legend_attribute_dict
