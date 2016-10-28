# coding=utf-8
import logging
import os
from tempfile import mkdtemp

from PyQt4 import QtXml

import io
import jinja2
from PyQt4.QtCore import QUrl
from jinja2.environment import Environment
from jinja2.loaders import PackageLoader, BaseLoader, FileSystemLoader
from qgis.core import QgsComposition, QgsComposerHtml, QgsRectangle

from safe.common.utilities import temp_dir
from safe.utilities.i18n import tr
from safe.common.exceptions import TemplateLoadingError
from safe.report.impact_report import ImpactReport
from safe.utilities.gis import qgis_version

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '10/19/16'


LOGGER = logging.getLogger('InaSAFE')


def jinja2_renderer(impact_report, component):
    """
    Render using Jinja2 template

    :param impact_report: ImpactReport contains data about the report that is
        going to be generated
    :type impact_report: safe.reportv4.impact_report.ImpactReport

    :param component: Contains the component metadata and context for
        rendering the output
    :type component: safe.reportv4.report_metadata.QgisComposerComponentsMetadata

    :return: whatever type of output the component should be
    """
    context = component.context

    main_template_folder = impact_report.metadata.template_folder
    loader = FileSystemLoader(
        os.path.abspath(main_template_folder))
    env = Environment(loader=loader)

    template = env.get_template(component.template)
    rendered = template.render(context)
    if component.output_format == 'string':
        return rendered
    elif component.output_format == 'file':
        if impact_report.output_folder is None:
            impact_report.output_folder = mkdtemp(dir=temp_dir())
        output_path = os.path.join(
            impact_report.output_folder, component.output_path)
        with io.open(output_path, mode='w', encoding='utf-8') as output_file:
            output_file.write(rendered)
        return output_path


def qgis_composer_renderer(impact_report, component):
    """
    Render using qgis composer for a given impact_report data and component
    context

    :param impact_report: ImpactReport contains data about the report that is
        going to be generated
    :type impact_report: safe.reportv4.impact_report.ImpactReport

    :param component: Contains the component metadata and context for
        rendering the output
    :type component: safe.reportv4.report_metadata.QgisComposerComponentsMetadata

    :return: whatever type of output the component should be
    """
    context = component.context
    """:type: safe.reportv4.extractors.composer.QGISComposerContext"""
    qgis_composition_context = impact_report.qgis_composition_context
    inasafe_context = impact_report.inasafe_context

    # load composition object
    composition = QgsComposition(qgis_composition_context.map_settings)

    # load template
    main_template_folder = impact_report.metadata.template_folder
    template_path = os.path.join(main_template_folder, component.template)

    with open(template_path) as template_file:
        template_content = template_file.read()

    document = QtXml.QDomDocument()
    document.setContent(template_content)

    load_status = composition.loadFromTemplate(
        document, context.substitution_map)

    if not load_status:
        raise TemplateLoadingError(
            tr('Error loading template: %s') % template_path)

    # replace image path
    if qgis_version() < 20600:
        for img in context.image_elements:
            item_id = img.get('id')
            path = img.get('path')
            image = composition.getComposerItemById(item_id)
            """:type: qgis.core.QgsComposerPicture"""
            if image is not None and path is not None:
                try:
                    image.setPicturePath(path)
                except:
                    pass
    else:
        for img in context.image_elements:
            item_id = img.get('id')
            path = img.get('path')
            image = composition.getComposerItemById(item_id)
            """:type: qgis.core.QgsComposerPicture"""
            if image is not None and path is not None:
                try:
                    image.setPictureFile(path)
                except:
                    pass

    # replace html frame
    for html_el in context.html_frame_elements:
        item_id = html_el.get('id')
        mode = html_el.get('mode')
        html_element = composition.getComposerItemById(item_id)
        """:type: qgis.core.QgsComposerHtml"""
        if html_element:
            if mode == 'text':
                text = html_el.get('text')
                text = text if text else ''
                html_element.setContentMode(QgsComposerHtml.ManualHtml)
                html_element.setHtml(text)
                html_element.loadHtml()
            elif mode == 'url':
                url = html_el.get('url')
                html_element.setContentMode(QgsComposerHtml.Url)
                qurl = QUrl.fromLocalFile(url)
                html_element.setUrl(qurl)

    # resize map extent
    for map_el in context.map_elements:
        item_id = map_el.get('id')
        extent = map_el.get('extent')
        split_count = map_el.get('grid_split_count')
        composer_map = composition.getComposerItemById(item_id)
        """:type: qgis.core.QgsComposerMap"""
        if composer_map:
            canvas_extent = extent
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
            x_interval = square_extent.width() / split_count
            composer_map.setGridIntervalX(x_interval)
            y_interval = square_extent.height() / split_count
            composer_map.setGridIntervalY(y_interval)

    # calculate legend element
    for leg_el in context.map_legends:
        item_id = leg_el.get('id')
        title = leg_el.get('title')
        layers = leg_el.get('layers')
        symbol_count = leg_el.get('symbol_count')
        column_count = leg_el.get('column_count')

        legend = composition.getComposerItemById(item_id)
        if legend:
            # set column count
            if column_count:
                legend.setColumnCount(column_count)
            elif symbol_count <= 5:
                legend.setColumnCount(1)
            else:
                legend.setColumnCount(symbol_count / 5 + 1)

            # set legend title
            if title is not None:
                legend.setTitle(title)

            # set legend
            # Since QGIS 2.6, legend.model() is obsolete
            if qgis_version() < 20600:
                layer_set = [l.id() for l in layers]
                legend.model().setLayerSet(layer_set)
                legend.synchronizeWithModel()
            else:
                root_group = legend.modelV2().rootGroup()
                for l in layers:
                    root_group.addLayer(l)
                legend.synchronizeWithModel()

    # process to output

    # in case output folder not specified
    if impact_report.output_folder is None:
        impact_report.output_folder = mkdtemp(dir=temp_dir())
    output_path = os.path.join(
        impact_report.output_folder, component.output_path)
    output_format = component.output_format
    # for QGIS composer only pdf and png output are available
    if output_format == 'pdf':
        try:
            composition.setPlotStyle(
                impact_report.qgis_composition_context.plot_style)
            composition.setPrintResolution(component.page_dpi)
            composition.setPaperSize(
                component.page_width, component.page_height)
            composition.setPrintAsRaster(
                impact_report.qgis_composition_context.save_as_raster)

            composition.exportAsPDF(output_path)
            component.output = output_path
        except Exception as exc:
            LOGGER.error(exc)
    return component.output
