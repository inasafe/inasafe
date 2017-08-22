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
from PyQt4.QtGui import QImage, QPainter, QPrinter
from PyQt4.QtSvg import QSvgRenderer
from jinja2.environment import Environment
from jinja2.loaders import FileSystemLoader
from qgis.core import (
    QgsMapLayer,
    QgsComposerFrame,
    QgsComposition,
    QgsComposerHtml,
    QgsComposerPicture,
    QgsRectangle,
    QgsLegendRenderer,
    QgsComposerLegendStyle,
    QgsComposerMap,
    QgsComposerLegend,
    QgsCoordinateTransform,
    QgsProject,
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


def composition_item(composer, item_id, item_class):
    """Fetch a specific item according to its type in a composer.

    We got some problem with QgsComposition::getComposerItemById. Don't use it,
    and use this function instead.
    See https://github.com/inasafe/inasafe/issues/4271

    :param composer: The composer to look in.
    :type composer: QgsComposition

    :param item_id: The ID of the item to look for.
    :type item_id: basestring

    :param item_class: The expected class name.
    :type item_class: cls

    :return: The composition item, inherited class of QgsComposerItem.
    """
    if item_class.__name__ == 'QgsComposerMap':
        # It needs this condition for Rohmat (Ubuntu)
        item = composer.getComposerItemById(item_id)
        if isinstance(item, QgsComposerMap):
            return item

    # Normal behaviour
    for item in composer.items():
        if isinstance(item, item_class):
            if item.id() == item_id:
                return item

    # Note from Etienne
    # Still no item? No problem, let's try something else to fetch the map.
    if item_class.__name__ == 'QgsComposerMap':
        maps = composer.composerMapItems()
        for composer_map in maps:
            if composer_map.displayName() == item_id:
                return composer_map

    # We found nothing
    return None


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


def create_qgis_pdf_output(
        impact_report,
        output_path,
        composition,
        file_format,
        metadata):
    """Produce PDF output using QgsComposition.

    :param output_path: The output path.
    :type output_path: str

    :param composition: QGIS Composition object.
    :type composition: qgis.core.QgsComposition

    :param qgis_composition_context: QGIS Composition context used by renderer.
    :type qgis_composition_context: safe.report.impact_report.
        QGISCompositionContext

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
    if composition.atlasComposition().enabled() and (
                print_atlas and aggregation_summary_layer):
        output_path = atlas_renderer(
            composition, aggregation_summary_layer, output_path, file_format)
    # for QGIS composer only pdf and png output are available
    elif file_format == QgisComposerComponentsMetadata.OutputFormat.PDF:
        try:
            composition.setPlotStyle(
                qgis_composition_context.plot_style)
            composition.setPrintResolution(metadata.page_dpi)
            composition.setPaperSize(
                metadata.page_width, metadata.page_height)
            composition.setPrintAsRaster(
                qgis_composition_context.save_as_raster)

            composition.exportAsPDF(output_path)
        except Exception as exc:
            LOGGER.error(exc)
            return None
    elif file_format == QgisComposerComponentsMetadata.OutputFormat.PNG:
        # TODO: implement PNG generations
        raise Exception('Not yet supported')
    return output_path


def create_qgis_template_output(output_path, composition):
    """Produce QGIS Template output.

    :param output_path: The output path.
    :type output_path: str

    :param composition: QGIS Composition object to get template.
        values
    :type composition: qgis.core.QgsComposition

    :return: Generated output path.
    :rtype: str
    """
    # make sure directory is created
    dirname = os.path.dirname(output_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    template_document = QtXml.QDomDocument()
    element = template_document.createElement('Composer')
    composition.writeXML(element, template_document)
    template_document.appendChild(element)

    with open(output_path, 'w') as f:
        f.write(template_document.toByteArray())

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
                    composition,
                    each_format,
                    component)
                component_output.append(result_path)
            elif each_format == template_format:
                result_path = create_qgis_template_output(
                    each_path, composition)
                component_output.append(result_path)
    elif isinstance(output_format, dict):
        component_output = {}
        for key, each_format in output_format.iteritems():
            each_path = component_output_path[key]

            if each_format in doc_format:
                result_path = create_qgis_pdf_output(
                    impact_report,
                    each_path,
                    composition,
                    each_format,
                    component)
                component_output[key] = result_path
            elif each_format == template_format:
                result_path = create_qgis_template_output(
                    each_path, composition)
                component_output[key] = result_path
    elif (output_format in
            QgisComposerComponentsMetadata.OutputFormat.SUPPORTED_OUTPUT):
        component_output = None

        if output_format in doc_format:
            result_path = create_qgis_pdf_output(
                impact_report,
                component_output_path,
                composition,
                output_format,
                component)
            component_output = result_path
        elif output_format == template_format:
            result_path = create_qgis_template_output(
                component_output_path, composition)
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
        image = composition_item(composition, item_id, QgsComposerPicture)
        """:type: qgis.core.QgsComposerPicture"""
        if image and path:
            image.setPicturePath(path)

    # replace html frame
    for html_el in context.html_frame_elements:
        item_id = html_el.get('id')
        mode = html_el.get('mode')
        composer_item = composition.getComposerItemById(item_id)
        try:
            html_element = composition.getComposerHtmlByItem(composer_item)
        except:
            pass
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

    original_crs = impact_report.impact_function.impact.crs()
    destination_crs = qgis_composition_context.map_settings.destinationCrs()
    coord_transform = QgsCoordinateTransform(original_crs, destination_crs)

    # resize map extent
    for map_el in context.map_elements:
        item_id = map_el.get('id')
        split_count = map_el.get('grid_split_count')
        layers = map_el.get('layers')
        map_extent_option = map_el.get('extent')
        composer_map = composition_item(composition, item_id, QgsComposerMap)
        """:type: qgis.core.QgsComposerMap"""
        if composer_map:
            composer_map.setKeepLayerSet(True)
            layer_set = [l.id() for l in layers if isinstance(l, QgsMapLayer)]
            composer_map.setLayerSet(layer_set)
            if map_extent_option and isinstance(
                    map_extent_option, QgsRectangle):
                # use provided map extent
                extent = coord_transform.transform(map_extent_option)
                for l in layers:
                    layer_extent = coord_transform.transform(l.extent())
                    if l.name() == map_overview['id']:
                        map_overview_extent = layer_extent
            else:
                # if map extent not provided, try to calculate extent
                # from list of given layers. Combine it so all layers were
                # shown properly
                map_overview_extent = None
                extent = QgsRectangle()
                extent.setMinimal()
                for l in layers:
                    # combine extent if different layer is provided.
                    layer_extent = coord_transform.transform(l.extent())
                    extent.combineExtentWith(layer_extent)
                    if l.name() == map_overview['id']:
                        map_overview_extent = layer_extent

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

            if component.key == 'population-infographic' and (
                    map_overview_extent):
                square_extent = map_overview_extent

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

        legend = composition_item(composition, item_id, QgsComposerLegend)
        """:type: qgis.core.QgsComposerLegend"""
        if legend:
            # set column count
            if column_count:
                legend.setColumnCount(column_count)
            elif symbol_count <= 7:
                legend.setColumnCount(1)
            else:
                legend.setColumnCount(symbol_count / 7 + 1)

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
                    composition,
                    each_format,
                    component)
                component_output.append(result_path)
            elif each_format == template_format:
                result_path = create_qgis_template_output(
                    each_path, composition)
                component_output.append(result_path)
    elif isinstance(output_format, dict):
        component_output = {}
        for key, each_format in output_format.iteritems():
            each_path = component_output_path[key]

            if each_format in doc_format:
                result_path = create_qgis_pdf_output(
                    impact_report,
                    each_path,
                    composition,
                    each_format,
                    component)
                component_output[key] = result_path
            elif each_format == template_format:
                result_path = create_qgis_template_output(
                    each_path, composition)
                component_output[key] = result_path
    elif (output_format in
            QgisComposerComponentsMetadata.OutputFormat.SUPPORTED_OUTPUT):
        component_output = None

        if output_format in doc_format:
            result_path = create_qgis_pdf_output(
                impact_report,
                component_output_path,
                composition,
                output_format,
                component)
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


def atlas_renderer(composition, coverage_layer, output_path, file_format):
    """Extract composition using atlas generation.

    :param composition: QGIS Composition object used for producing the report.
    :type composition: qgis.core.QgsComposition

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
    composer_map = composition_item(composition, 'impact-map', QgsComposerMap)
    composer_map.setAtlasDriven(True)
    composer_map.setAtlasScalingMode(QgsComposerMap.Auto)

    # setup the atlas composition and composition atlas mode
    atlas_composition = composition.atlasComposition()
    atlas_composition.setCoverageLayer(coverage_layer)
    atlas_composition.setComposerMap(composer_map)
    atlas_composition.prepareMap(composer_map)
    atlas_on_single_file = atlas_composition.singleFile()
    composition.setAtlasMode(QgsComposition.ExportAtlas)

    if file_format == QgisComposerComponentsMetadata.OutputFormat.PDF:
        if not atlas_composition.filenamePattern():
            atlas_composition.setFilenamePattern(
                "'output_'||@atlas_featurenumber")
        output_directory = os.path.dirname(output_path)

        printer = QPrinter(QPrinter.HighResolution)
        painter = QPainter()

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
        atlas_composition.setPredefinedScales(project_scales)

        if not atlas_composition.beginRender() and (
                atlas_composition.featureFilterErrorString()):
            msg = 'Atlas processing error: {error}'.format(
                error=atlas_composition.featureFilterErrorString())
            LOGGER.error(msg)
            return

        if atlas_on_single_file:
            atlas_composition.prepareForFeature(0)
            composition.beginPrintAsPDF(printer, output_path)
            composition.beginPrint(printer)
            if not painter.begin(printer):
                msg = ('Atlas processing error: '
                       'Cannot write to {output}.').format(output=output_path)
                LOGGER.error(msg)
                return

        LOGGER.info('Exporting Atlas')

        atlas_output = []
        for feature_index in range(atlas_composition.numFeatures()):
            if not atlas_composition.prepareForFeature(feature_index):
                msg = ('Atlas processing error: Exporting atlas error at '
                       'feature number {index}').format(index=feature_index)
                LOGGER.error(msg)
                return
            if not atlas_on_single_file:
                # we need another printer object fot multi file atlas
                multi_file_printer = QPrinter(QPrinter.HighResolution)
                current_filename = atlas_composition.currentFilename()
                output_path = os.path.join(
                    output_directory, current_filename + '.pdf')
                composition.beginPrintAsPDF(multi_file_printer, output_path)
                composition.beginPrint(multi_file_printer)
                if not painter.begin(multi_file_printer):
                    msg = ('Atlas processing error: Cannot write to '
                           '{output}.').format(output=output_path)
                    LOGGER.error(msg)
                    return
                composition.doPrint(multi_file_printer, painter)
                painter.end()
                composition.georeferenceOutput(output_path)
                atlas_output.append(output_path)
            else:
                composition.doPrint(printer, painter, feature_index > 0)

        atlas_composition.endRender()

        if atlas_on_single_file:
            painter.end()
            return output_path

        return atlas_output
