# coding=utf-8

"""
Module for basic renderer we support. Currently we have:

- Jinja2 Templating renderer
- QGIS Composition templating renderer
"""


import io
import logging
import os
import sip
from tempfile import mkdtemp

from qgis.PyQt import QtXml
from qgis.PyQt.QtCore import QUrl, QRectF

from qgis.PyQt.QtGui import QImage, QPainter
from qgis.PyQt.QtSvg import QSvgRenderer
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from qgis.core import (
    QgsMapLayer,
    QgsLayoutMultiFrame,
    QgsLayoutFrame,
    QgsPrintLayout,
    QgsLayoutExporter,
    QgsLayoutItemHtml,
    QgsLayoutItemPicture,
    QgsLayoutItemPage,
    QgsRectangle,
    QgsLegendRenderer,
    QgsLegendStyle,
    QgsLayoutItemMap,
    QgsLayoutItemLegend,
    QgsCoordinateTransform,
    QgsProject,
    QgsReadWriteContext,
    PROJECT_SCALES
)

from safe.common.exceptions import TemplateLoadingError
from safe.common.utilities import temp_dir
from safe.definitions.reports.infographic import map_overview
from safe.report.report_metadata import QgisComposerComponentsMetadata
from safe.utilities.i18n import tr
from safe.utilities.settings import general_setting, setting

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


LOGGER = logging.getLogger('InaSAFE')


def layout_item(layout, item_id, item_class):
    """Fetch a specific item according to its type in a layout.

    There's some sip casting conversion issues with QgsLayout::itemById.
    Don't use it, and use this function instead.
    See https://github.com/inasafe/inasafe/issues/4271

    :param layout: The layout to look in.
    :type layout: QgsLayout

    :param item_id: The ID of the item to look for.
    :type item_id: basestring

    :param item_class: The expected class name.
    :type item_class: cls

    :return: The layout item, inherited class of QgsLayoutItem.
    """
    item = layout.itemById(item_id)
    if item is None:
        # no match!
        return item

    if issubclass(item_class, QgsLayoutMultiFrame):
        # finding a multiframe by frame id
        frame = sip.cast(item, QgsLayoutFrame)
        multi_frame = frame.multiFrame()
        return sip.cast(multi_frame, item_class)
    else:
        # force sip to correctly cast item to required type
        return sip.cast(item, item_class)


def jinja2_renderer(impact_report, component):
    """Versatile text renderer using Jinja2 Template.

    Render using Jinja2 template.

    :param impact_report: ImpactReport contains data about the report that is
        going to be generated.
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component: Contains the component metadata and context for
        rendering the output.
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


def create_qgis_pdf_output(
        impact_report,
        output_path,
        layout,
        file_format,
        metadata):
    """Produce PDF output using QgsLayout.

    :param output_path: The output path.
    :type output_path: str

    :param layout: QGIS Layout object.
    :type layout: qgis.core.QgsPrintLayout

    :param qgis_composition_context: QGIS Composition context used by renderer.
    :type qgis_composition_context: safe.report.impact_report.
        QgsLayoutContext

    :param file_format: file format of map output, PDF or PNG.
    :type file_format: 'pdf', 'png'

    :param metadata: The component metadata.
    :type metadata: QgisComposerComponentsMetadata

    :return: Generated output path.
    :rtype: str
    """
    # make sure directory is created
    dirname = os.path.dirname(output_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    qgis_composition_context = impact_report.qgis_composition_context
    aggregation_summary_layer = (
        impact_report.impact_function.aggregation_summary)

    # process atlas generation
    print_atlas = setting('print_atlas_report', False, bool)
    if layout.atlas().enabled() and (
            print_atlas and aggregation_summary_layer):
        output_path = atlas_renderer(
            layout, aggregation_summary_layer, output_path, file_format)
    # for QGIS layout only pdf and png output are available
    elif file_format == QgisComposerComponentsMetadata.OutputFormat.PDF:
        try:
            exporter = QgsLayoutExporter(layout)
            settings = QgsLayoutExporter.PdfExportSettings()
            settings.dpi = metadata.page_dpi
            settings.rasterizeWholeImage = \
                qgis_composition_context.save_as_raster
            # settings.forceVectorOutput = False
            # settings.exportMetadata = True

            # TODO: ABP: check that page size is set on the pages
            res = exporter.exportToPdf(output_path, settings)
            if res != QgsLayoutExporter.Success:
                LOGGER.error('Error exporting to {}'.format(
                    exporter.errorFile()))
                return None
        except Exception as exc:
            LOGGER.error(exc)
            return None
    elif file_format == QgisComposerComponentsMetadata.OutputFormat.PNG:
        # TODO: implement PNG generation
        raise Exception('Not yet supported')
    return output_path


def create_qgis_template_output(output_path, layout):
    """Produce QGIS Template output.

    :param output_path: The output path.
    :type output_path: str

    :param composition: QGIS Composition object to get template.
        values
    :type composition: qgis.core.QgsLayout

    :return: Generated output path.
    :rtype: str
    """
    # make sure directory is created
    dirname = os.path.dirname(output_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    context = QgsReadWriteContext()
    context.setPathResolver(QgsProject.instance().pathResolver())

    layout.saveAsTemplate(output_path, context)
    return output_path


def qgis_composer_html_renderer(impact_report, component):
    """HTML to PDF renderer using QGIS Composer.

    Render using qgis composer for a given impact_report data and component
    context for html input.

    :param impact_report: ImpactReport contains data about the report that is
        going to be generated.
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component: Contains the component metadata and context for
        rendering the output.
    :type component:
        safe.report.report_metadata.QgisComposerComponentsMetadata

    :return: Whatever type of output the component should be.

    .. versionadded:: 4.0
    """
    context = component.context

    # QGIS3: not used
    # qgis_composition_context = impact_report.qgis_composition_context

    # create new layout with A4 portrait page
    layout = QgsPrintLayout(QgsProject.instance())
    page = QgsLayoutItemPage(layout)
    page.setPageSize('A4', orientation=QgsLayoutItemPage.Portrait)
    layout.pageCollection().addPage(page)

    if not context.html_frame_elements:
        # if no html frame elements at all, do not generate empty report.
        component.output = ''
        return component.output

    # Add HTML Frame
    for html_el in context.html_frame_elements:
        mode = html_el.get('mode')
        html_element = QgsLayoutItemHtml(layout)
        margin_left = html_el.get('margin_left', 10)
        margin_top = html_el.get('margin_top', 10)
        width = html_el.get('width', component.page_width - 2 * margin_left)
        height = html_el.get('height', component.page_height - 2 * margin_top)

        html_frame = QgsLayoutFrame(layout, html_element)
        html_frame.attemptSetSceneRect(
            QRectF(margin_left, margin_top, width, height))
        html_element.addFrame(html_frame)

        if html_element:
            if mode == 'text':
                text = html_el.get('text')
                text = text if text else ''
                html_element.setContentMode(QgsLayoutItemHtml.ManualHtml)
                html_element.setResizeMode(
                    QgsLayoutItemHtml.RepeatUntilFinished)
                html_element.setHtml(text)
                html_element.loadHtml()
            elif mode == 'url':
                url = html_el.get('url')
                html_element.setContentMode(QgsLayoutItemHtml.Url)
                html_element.setResizeMode(
                    QgsLayoutItemHtml.RepeatUntilFinished)
                qurl = QUrl.fromLocalFile(url)
                html_element.setUrl(qurl)

    # Attempt on removing blank page. Notes: We assume that the blank page
    # will always appears in the last x page(s), not in the middle.

    pc = layout.pageCollection()
    index = pc.pageCount()
    while pc.pageIsEmpty(index):
        pc.deletePage(index)
        index -= 1

    # process to output

    # in case output folder not specified
    if impact_report.output_folder is None:
        impact_report.output_folder = mkdtemp(dir=temp_dir())
    component_output_path = impact_report.component_absolute_output_path(
        component.key)
    component_output = None

    output_format = component.output_format

    doc_format = QgisComposerComponentsMetadata.OutputFormat.DOC_OUTPUT
    template_format = QgisComposerComponentsMetadata.OutputFormat.QPT
    if isinstance(output_format, list):
        component_output = []
        for i in range(len(output_format)):
            each_format = output_format[i]
            each_path = component_output_path[i]

            if each_format in doc_format:
                result_path = create_qgis_pdf_output(
                    impact_report,
                    each_path,
                    layout,
                    each_format,
                    component)
                component_output.append(result_path)
            elif each_format == template_format:
                result_path = create_qgis_template_output(
                    each_path, layout)
                component_output.append(result_path)
    elif isinstance(output_format, dict):
        component_output = {}
        for key, each_format in list(output_format.items()):
            each_path = component_output_path[key]

            if each_format in doc_format:
                result_path = create_qgis_pdf_output(
                    impact_report,
                    each_path,
                    layout,
                    each_format,
                    component)
                component_output[key] = result_path
            elif each_format == template_format:
                result_path = create_qgis_template_output(
                    each_path, layout)
                component_output[key] = result_path
    elif (output_format in
            QgisComposerComponentsMetadata.OutputFormat.SUPPORTED_OUTPUT):
        component_output = None

        if output_format in doc_format:
            result_path = create_qgis_pdf_output(
                impact_report,
                component_output_path,
                layout,
                output_format,
                component)
            component_output = result_path
        elif output_format == template_format:
            result_path = create_qgis_template_output(
                component_output_path, layout)
            component_output = result_path

    component.output = component_output

    return component.output


def qgis_composer_renderer(impact_report, component):
    """Default Map Report Renderer using QGIS Composer.

    Render using qgis composer for a given impact_report data and component
    context.

    :param impact_report: ImpactReport contains data about the report that is
        going to be generated.
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component: Contains the component metadata and context for
        rendering the output.
    :type component:
        safe.report.report_metadata.QgisComposerComponentsMetadata

    :return: Whatever type of output the component should be.

    .. versionadded:: 4.0
    """
    context = component.context
    qgis_composition_context = impact_report.qgis_composition_context

    # load composition object
    layout = QgsPrintLayout(QgsProject.instance())

    # load template
    main_template_folder = impact_report.metadata.template_folder

    # we do this condition in case custom template was found
    if component.template.startswith('../qgis-composer-templates/'):
        template_path = os.path.join(main_template_folder, component.template)
    else:
        template_path = component.template

    with open(template_path) as template_file:
        template_content = template_file.read()

    document = QtXml.QDomDocument()

    # Replace
    for k, v in context.substitution_map.items():
        template_content = template_content.replace('[{}]'.format(k), v)

    document.setContent(template_content)

    rwcontext = QgsReadWriteContext()
    load_status = layout.loadFromTemplate(
        document, rwcontext)

    if not load_status:
        raise TemplateLoadingError(
            tr('Error loading template: %s') % template_path)

    # replace image path
    for img in context.image_elements:
        item_id = img.get('id')
        path = img.get('path')
        image = layout_item(layout, item_id, QgsLayoutItemPicture)
        if image and path:
            image.setPicturePath(path)

    # replace html frame
    for html_el in context.html_frame_elements:
        item_id = html_el.get('id')
        mode = html_el.get('mode')
        html_element = layout_item(layout, item_id, QgsLayoutItemHtml)
        if html_element:
            if mode == 'text':
                text = html_el.get('text')
                text = text if text else ''
                html_element.setContentMode(QgsLayoutItemHtml.ManualHtml)
                html_element.setHtml(text)
                html_element.loadHtml()
            elif mode == 'url':
                url = html_el.get('url')
                html_element.setContentMode(QgsLayoutItemHtml.Url)
                qurl = QUrl.fromLocalFile(url)
                html_element.setUrl(qurl)

    original_crs = impact_report.impact_function.crs
    destination_crs = qgis_composition_context.map_settings.destinationCrs()
    coord_transform = QgsCoordinateTransform(original_crs,
                                             destination_crs,
                                             QgsProject.instance())

    # resize map extent
    for map_el in context.map_elements:
        item_id = map_el.get('id')
        split_count = map_el.get('grid_split_count')
        layers = [
            _layer for _layer in map_el.get('layers') if isinstance(
                _layer, QgsMapLayer)
        ]
        map_extent_option = map_el.get('extent')
        composer_map = layout_item(layout, item_id, QgsLayoutItemMap)

        for index, _layer in enumerate(layers):
            # we need to check whether the layer is registered or not
            registered_layer = (
                QgsProject.instance().mapLayer(_layer.id()))
            if registered_layer:
                if not registered_layer == _layer:
                    layers[index] = registered_layer
            else:
                QgsProject.instance().addMapLayer(_layer)

        """:type: qgis.core.QgsLayoutItemMap"""
        if composer_map:

            # Search for specified map extent in the template.
            min_x = composer_map.extent().xMinimum() if (
                impact_report.use_template_extent) else None
            min_y = composer_map.extent().yMinimum() if (
                impact_report.use_template_extent) else None
            max_x = composer_map.extent().xMaximum() if (
                impact_report.use_template_extent) else None
            max_y = composer_map.extent().yMaximum() if (
                impact_report.use_template_extent) else None

            composer_map.setKeepLayerSet(True)
            layer_set = [_layer for _layer in layers if isinstance(
                _layer, QgsMapLayer)]
            composer_map.setLayers(layer_set)
            map_overview_extent = None
            if map_extent_option and isinstance(
                    map_extent_option, QgsRectangle):
                # use provided map extent
                extent = coord_transform.transform(map_extent_option)
                for layer in layer_set:
                    layer_extent = coord_transform.transform(layer.extent())
                    if layer.name() == map_overview['id']:
                        map_overview_extent = layer_extent
            else:
                # if map extent not provided, try to calculate extent
                # from list of given layers. Combine it so all layers were
                # shown properly
                extent = QgsRectangle()
                extent.setMinimal()
                for layer in layer_set:
                    # combine extent if different layer is provided.
                    layer_extent = coord_transform.transform(layer.extent())
                    extent.combineExtentWith(layer_extent)
                    if layer.name() == map_overview['id']:
                        map_overview_extent = layer_extent

            width = extent.width()
            height = extent.height()
            longest_width = width if width > height else height
            half_length = longest_width / 2
            margin = half_length / 5
            center = extent.center()
            min_x = min_x or (center.x() - half_length - margin)
            max_x = max_x or (center.x() + half_length + margin)
            min_y = min_y or (center.y() - half_length - margin)
            max_y = max_y or (center.y() + half_length + margin)

            # noinspection PyCallingNonCallable
            square_extent = QgsRectangle(min_x, min_y, max_x, max_y)

            if component.key == 'population-infographic' and (
                    map_overview_extent):
                square_extent = map_overview_extent

            composer_map.zoomToExtent(square_extent)
            composer_map.invalidateCache()

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
        layers = [
            _layer for _layer in leg_el.get('layers') if isinstance(
                _layer, QgsMapLayer)
        ]
        symbol_count = leg_el.get('symbol_count')
        column_count = leg_el.get('column_count')

        legend = layout_item(layout, item_id, QgsLayoutItemLegend)
        """:type: qgis.core.QgsLayoutItemLegend"""
        if legend:
            # set column count
            if column_count:
                legend.setColumnCount(column_count)
            elif symbol_count <= 7:
                legend.setColumnCount(1)
            else:
                legend.setColumnCount(symbol_count / 7 + 1)

            # set legend title
            if title is not None and not impact_report.legend_layers:
                legend.setTitle(title)

            # set legend
            root_group = legend.model().rootGroup()
            for _layer in layers:
                # we need to check whether the layer is registered or not
                registered_layer = (
                    QgsProject.instance().mapLayer(_layer.id()))
                if registered_layer:
                    if not registered_layer == _layer:
                        _layer = registered_layer
                else:
                    QgsProject.instance().addMapLayer(_layer)
                # used for customizations
                tree_layer = root_group.addLayer(_layer)
                if impact_report.legend_layers or (
                        not impact_report.multi_exposure_impact_function):
                    QgsLegendRenderer.setNodeLegendStyle(
                        tree_layer, QgsLegendStyle.Hidden)
            legend.adjustBoxSize()
            legend.updateFilterByMap(False)

    # process to output

    # in case output folder not specified
    if impact_report.output_folder is None:
        impact_report.output_folder = mkdtemp(dir=temp_dir())

    output_format = component.output_format
    component_output_path = impact_report.component_absolute_output_path(
        component.key)
    component_output = None

    doc_format = QgisComposerComponentsMetadata.OutputFormat.DOC_OUTPUT
    template_format = QgisComposerComponentsMetadata.OutputFormat.QPT
    if isinstance(output_format, list):
        component_output = []
        for i in range(len(output_format)):
            each_format = output_format[i]
            each_path = component_output_path[i]

            if each_format in doc_format:
                result_path = create_qgis_pdf_output(
                    impact_report,
                    each_path,
                    layout,
                    each_format,
                    component)
                component_output.append(result_path)
            elif each_format == template_format:
                result_path = create_qgis_template_output(
                    each_path, layout)
                component_output.append(result_path)
    elif isinstance(output_format, dict):
        component_output = {}
        for key, each_format in list(output_format.items()):
            each_path = component_output_path[key]

            if each_format in doc_format:
                result_path = create_qgis_pdf_output(
                    impact_report,
                    each_path,
                    layout,
                    each_format,
                    component)
                component_output[key] = result_path
            elif each_format == template_format:
                result_path = create_qgis_template_output(
                    each_path, layout)
                component_output[key] = result_path
    elif (output_format in
            QgisComposerComponentsMetadata.OutputFormat.SUPPORTED_OUTPUT):
        component_output = None

        if output_format in doc_format:
            result_path = create_qgis_pdf_output(
                impact_report,
                component_output_path,
                layout,
                output_format,
                component)
            component_output = result_path
        elif output_format == template_format:
            result_path = create_qgis_template_output(
                component_output_path, layout)
            component_output = result_path

    component.output = component_output

    return component.output


def qt_svg_to_png_renderer(impact_report, component):
    """Render SVG into PNG.

    :param impact_report: ImpactReport contains data about the report that is
        going to be generated.
    :type impact_report: safe.report.impact_report.ImpactReport

    :param component: Contains the component metadata and context for
        rendering the output.
    :type component:
        safe.report.report_metadata.QgisComposerComponentsMetadata

    :return: Whatever type of output the component should be.

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


def atlas_renderer(layout, coverage_layer, output_path, file_format):
    """Extract composition using atlas generation.

    :param layout: QGIS Print Layout object used for producing the report.
    :type layout: qgis.core.QgsPrintLayout

    :param coverage_layer: Coverage Layer used for atlas map.
    :type coverage_layer: QgsMapLayer

    :param output_path: The output path of the product.
    :type output_path: str

    :param file_format: File format of map output, 'pdf' or 'png'.
    :type file_format: str

    :return: Generated output path(s).
    :rtype: str, list
    """
    # set the composer map to be atlas driven
    composer_map = layout_item(
        layout, 'impact-map', QgsLayoutItemMap)
    composer_map.setAtlasDriven(True)
    composer_map.setAtlasScalingMode(QgsLayoutItemMap.Auto)

    # setup the atlas composition and composition atlas mode
    atlas_composition = layout.atlas()
    atlas_composition.setCoverageLayer(coverage_layer)
    atlas_on_single_file = layout.customProperty('singleFile', True)

    if file_format == QgisComposerComponentsMetadata.OutputFormat.PDF:
        if not atlas_composition.filenameExpression():
            atlas_composition.setFilenameExpression(
                "'output_'||@atlas_featurenumber")
        output_directory = os.path.dirname(output_path)

        # we need to set the predefined scales for atlas
        project_scales = []
        scales = QgsProject.instance().readListEntry(
            "Scales", "/ScalesList")[0]
        has_project_scales = QgsProject.instance().readBoolEntry(
            "Scales", "/useProjectScales")[0]
        if not has_project_scales or not scales:
            scales_string = str(general_setting("Map/scales", PROJECT_SCALES))
            scales = scales_string.split(',')
        for scale in scales:
            parts = scale.split(':')
            if len(parts) == 2:
                project_scales.append(float(parts[1]))
        layout.reportContext().setPredefinedScales(project_scales)

        settings = QgsLayoutExporter.PdfExportSettings()

        LOGGER.info('Exporting Atlas')
        atlas_output = []
        if atlas_on_single_file:
            res, error = QgsLayoutExporter.exportToPdf(
                atlas_composition, output_path, settings)
            atlas_output.append(output_path)
        else:
            res, error = QgsLayoutExporter.exportToPdfs(
                atlas_composition, output_directory, settings)

        if res != QgsLayoutExporter.Success:
            LOGGER.error(error)

        return atlas_output
