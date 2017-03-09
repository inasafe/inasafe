# coding=utf-8
"""
Module for basic renderer we support. Currently we have:

- Jinja2 Templating renderer
- QGIS Composition templating renderer

"""
import io
import logging
import os
from PyQt4 import QtXml
from tempfile import mkdtemp

from PyQt4.QtCore import QUrl
from PyQt4.QtGui import QImage, QPainter
from PyQt4.QtSvg import QSvgRenderer
from jinja2.environment import Environment
from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import FileSystemLoader
from qgis.core import (
    QgsMapLayer,
    QgsComposerFrame,
    QgsComposition,
    QgsComposerHtml,
    QgsRectangle,
    QgsLegendRenderer,
    QgsComposerLegendStyle)

from safe.common.exceptions import TemplateLoadingError
from safe.common.utilities import temp_dir
from safe.report.report_metadata import QgisComposerComponentsMetadata
from safe.utilities.i18n import tr

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


LOGGER = logging.getLogger('InaSAFE')


def jinja2_renderer(impact_report, component):
    """Versatile text renderer using Jinja2 Template.

    Render using Jinja2 template

    :param impact_report: ImpactReport contains data about the report that is
        going to be generated
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component: Contains the component metadata and context for
        rendering the output
    :type component:
        safe.report.report_metadata.QgisComposerComponentsMetadata

    :return: whatever type of output the component should be

    .. versionadded:: 4.0
    """
    context = component.context

    main_template_folder = impact_report.metadata.template_folder
    loader = FileSystemLoader(
        os.path.abspath(main_template_folder))
    extensions = [
        'jinja2.ext.i18n',
        'jinja2.ext.with_',
        'jinja2.ext.loopcontrols',
        'jinja2.ext.do',
    ]
    env = Environment(
        loader=loader,
        extensions=extensions)

    template = env.get_template(component.template)
    rendered = template.render(context)
    if component.output_format == 'string':
        return rendered
    elif component.output_format == 'file':
        if impact_report.output_folder is None:
            impact_report.output_folder = mkdtemp(dir=temp_dir())
        output_path = impact_report.component_absolute_output_path(
            component.key)

        # make sure directory is created
        dirname = os.path.dirname(output_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with io.open(output_path, mode='w', encoding='utf-8') as output_file:
            output_file.write(rendered)
        return output_path


def qgis_composer_html_renderer(impact_report, component):
    """HTML to PDF renderer using QGIS Composer.

    Render using qgis composer for a given impact_report data and component
    context for html input

    :param impact_report: ImpactReport contains data about the report that is
        going to be generated
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component: Contains the component metadata and context for
        rendering the output
    :type component:
        safe.report.report_metadata.QgisComposerComponentsMetadata

    :return: whatever type of output the component should be

    .. versionadded:: 4.0
    """
    context = component.context
    """:type: safe.report.extractors.composer.QGISComposerContext"""
    qgis_composition_context = impact_report.qgis_composition_context
    inasafe_context = impact_report.inasafe_context

    # load composition object
    composition = QgsComposition(qgis_composition_context.map_settings)

    if not context.html_frame_elements:
        # if no html frame elements at all, do not generate empty report.
        component.output = ''
        return component.output

    # Add HTML Frame
    for html_el in context.html_frame_elements:
        mode = html_el.get('mode')
        html_element = QgsComposerHtml(composition, False)
        """:type: qgis.core.QgsComposerHtml"""
        margin_left = html_el.get('margin_left', 10)
        margin_top = html_el.get('margin_top', 10)
        width = html_el.get('width', component.page_width - 2 * margin_left)
        height = html_el.get('height', component.page_height - 2 * margin_top)

        html_frame = QgsComposerFrame(
            composition,
            html_element,
            margin_left,
            margin_top,
            width,
            height)
        html_element.addFrame(html_frame)

        if html_element:
            if mode == 'text':
                text = html_el.get('text')
                text = text if text else ''
                html_element.setContentMode(QgsComposerHtml.ManualHtml)
                html_element.setResizeMode(
                    QgsComposerHtml.RepeatUntilFinished)
                html_element.setHtml(text)
                html_element.loadHtml()
            elif mode == 'url':
                url = html_el.get('url')
                html_element.setContentMode(QgsComposerHtml.Url)
                html_element.setResizeMode(
                    QgsComposerHtml.RepeatUntilFinished)
                qurl = QUrl.fromLocalFile(url)
                html_element.setUrl(qurl)

    # process to output

    # in case output folder not specified
    if impact_report.output_folder is None:
        impact_report.output_folder = mkdtemp(dir=temp_dir())
    output_path = impact_report.component_absolute_output_path(
        component.key)

    # make sure directory is created
    dirname = os.path.dirname(output_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

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


def qgis_composer_renderer(impact_report, component):
    """Default Map Report Renderer using QGIS Composer.

    Render using qgis composer for a given impact_report data and component
    context

    :param impact_report: ImpactReport contains data about the report that is
        going to be generated
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component: Contains the component metadata and context for
        rendering the output
    :type component:
        safe.report.report_metadata.QgisComposerComponentsMetadata

    :return: whatever type of output the component should be

    .. versionadded:: 4.0
    """
    context = component.context
    """:type: safe.report.extractors.composer.QGISComposerContext"""
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
        split_count = map_el.get('grid_split_count')
        layers = map_el.get('layers')
        map_extent_option = map_el.get('extent')
        composer_map = composition.getComposerItemById(item_id)
        """:type: qgis.core.QgsComposerMap"""
        if composer_map:
            composer_map.setKeepLayerSet(True)
            layer_set = [l.id() for l in layers if isinstance(l, QgsMapLayer)]
            composer_map.setLayerSet(layer_set)
            if map_extent_option and isinstance(
                    map_extent_option, QgsRectangle):
                # use provided map extent
                extent = map_extent_option
            else:
                # if map extent not provided, try to calculate extent
                # from list of given layers. Combine it so all layers were
                # shown properly
                extent = QgsRectangle()
                extent.setMinimal()
                for l in layers:
                    # combine extent if different layer is provided.
                    extent.combineExtentWith(l.extent())

            width = extent.width()
            height = extent.height()
            longest_width = width if width > height else height
            half_length = longest_width / 2
            margin = half_length / 5
            center = extent.center()
            min_x = center.x() - half_length - margin
            max_x = center.x() + half_length + margin
            min_y = center.y() - half_length - margin
            max_y = center.y() + half_length + margin

            # noinspection PyCallingNonCallable
            square_extent = QgsRectangle(min_x, min_y, max_x, max_y)

            composer_map.zoomToExtent(square_extent)
            composer_map.renderModeUpdateCachedImage()

            actual_extent = composer_map.extent()

            # calculate intervals for grid
            x_interval = actual_extent.width() / split_count
            composer_map.grid().setIntervalX(x_interval)
            y_interval = actual_extent.height() / split_count
            composer_map.grid().setIntervalY(y_interval)

    # calculate legend element
    for leg_el in context.map_legends:
        item_id = leg_el.get('id')
        title = leg_el.get('title')
        layers = leg_el.get('layers')
        symbol_count = leg_el.get('symbol_count')
        column_count = leg_el.get('column_count')

        legend = composition.getComposerItemById(item_id)
        """:type: qgis.core.QgsComposerLegend"""
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
            root_group = legend.modelV2().rootGroup()
            for l in layers:
                # used for customizations
                tree_layer = root_group.addLayer(l)
                QgsLegendRenderer.setNodeLegendStyle(
                    tree_layer, QgsComposerLegendStyle.Hidden)
            legend.synchronizeWithModel()

    # process to output

    # in case output folder not specified
    if impact_report.output_folder is None:
        impact_report.output_folder = mkdtemp(dir=temp_dir())

    def create_map_output(output_path, file_format, metadata):
        """Produce PDF Map output.

        :param output_path: the output path
        :type output_path: str

        :param file_format: file format of map output, PDF or PNG
        :type file_format: 'pdf', 'png'

        :param metadata: the component metadata
        :type metadata: QgisComposerComponentsMetadata

        :return: generated output path
        :rtype: str
        """

        # make sure directory is created
        dirname = os.path.dirname(output_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        # for QGIS composer only pdf and png output are available
        if file_format == QgisComposerComponentsMetadata.OutputFormat.PDF:
            try:
                composition.setPlotStyle(
                    impact_report.qgis_composition_context.plot_style)
                composition.setPrintResolution(metadata.page_dpi)
                composition.setPaperSize(
                    metadata.page_width, metadata.page_height)
                composition.setPrintAsRaster(
                    impact_report.qgis_composition_context.save_as_raster)

                composition.exportAsPDF(output_path)
            except Exception as exc:
                LOGGER.error(exc)
                return None
        elif file_format == QgisComposerComponentsMetadata.OutputFormat.PNG:
            # TODO: implement PNG generations
            raise Exception('Not yet supported')
        return output_path

    def create_qgis_template_output(output_path, qgis_composition):
        """Produce QGIS Template output.

        :param output_path: the output path
        :type output_path: str

        :param qgis_composition: QGIS Composition object to get template
            values
        :type qgis_composition: QgsComposition

        :return: generated output path
        :rtype: str
        """

        # make sure directory is created
        dirname = os.path.dirname(output_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        template_document = QtXml.QDomDocument()
        element = template_document.createElement('Composer')
        qgis_composition.writeXML(element, template_document)
        template_document.appendChild(element)

        with open(output_path, 'w') as f:
            f.write(template_document.toByteArray())

        return output_path

    output_format = component.output_format
    component_output_path = impact_report.component_absolute_output_path(
        component.key)
    component_output = None

    map_format = QgisComposerComponentsMetadata.OutputFormat.MAP_OUTPUT
    template_format = QgisComposerComponentsMetadata.OutputFormat.QPT
    if isinstance(output_format, list):
        component_output = []
        for i in range(len(output_format)):
            each_format = output_format[i]
            each_path = component_output_path[i]

            if each_format in map_format:
                result_path = create_map_output(
                    each_path, each_format, component)
                component_output.append(result_path)
            elif each_format == template_format:
                result_path = create_qgis_template_output(
                    each_path, composition)
                component_output.append(result_path)
    elif isinstance(output_format, dict):
        component_output = {}
        for key, each_format in output_format.iteritems():
            each_path = component_output_path[key]

            if each_format in map_format:
                result_path = create_map_output(
                    each_path, each_format, component)
                component_output[key] = result_path
            elif each_format == template_format:
                result_path = create_qgis_template_output(
                    each_path, composition)
                component_output[key] = result_path
    elif (output_format in
            QgisComposerComponentsMetadata.OutputFormat.SUPPORTED_OUTPUT):
        component_output = None

        if output_format in map_format:
            result_path = create_map_output(
                component_output_path, output_format, component)
            component_output = result_path
        elif output_format == template_format:
            result_path = create_qgis_template_output(
                component_output_path, composition)
            component_output = result_path

    component.output = component_output

    return component.output


def qt_svg_to_png_renderer(impact_report, component):
    """Render SVG into PNG.

    :param impact_report: ImpactReport contains data about the report that is
        going to be generated
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component: Contains the component metadata and context for
        rendering the output
    :type component:
        safe.report.report_metadata.QgisComposerComponentsMetadata

    :return: whatever type of output the component should be

    .. versionadded:: 4.0
    """
    context = component.context
    filepath = context['filepath']
    width = component.extra_args['width']
    height = component.extra_args['height']
    image_format = QImage.Format_ARGB32
    qimage = QImage(width, height, image_format)
    qimage.fill(0x00000000)
    renderer = QSvgRenderer(filepath)
    painter = QPainter(qimage)
    renderer.render(painter)
    # Should call painter.end() so that QImage is not used
    painter.end()

    # in case output folder not specified
    if impact_report.output_folder is None:
        impact_report.output_folder = mkdtemp(dir=temp_dir())
    output_path = impact_report.component_absolute_output_path(
        component.key)

    qimage.save(output_path)

    component.output = output_path
    return component.output
