# coding=utf-8

"""Analysis Utilities."""

import os
from collections import OrderedDict
from PyQt4.QtCore import QDir, Qt
from qgis.core import QgsMapLayerRegistry, QgsProject, QgsMapLayer, QGis

from safe.definitions.utilities import definition, update_template_component
from safe.definitions.fields import hazard_class_field
from safe.definitions.reports.components import (
    standard_impact_report_metadata_pdf,
    map_report,
    infographic_report)
from safe.impact_function.style import hazard_class_style
from safe.report.extractors.util import layer_definition_type
from safe.report.report_metadata import ReportMetadata
from safe.report.impact_report import ImpactReport
from safe.utilities.gis import is_raster_layer, qgis_version
from safe.utilities.settings import setting

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def generate_impact_report(impact_function, iface):
    """Generate the impact report from an impact function.

    :param impact_function: The impact function used.
    :type impact_function: ImpactFunction

    :param iface: QGIS QGisAppInterface instance.
    :type iface: QGisAppInterface

    """
    # get the extra layers that we need
    extra_layers = []
    print_atlas = setting('print_atlas_report', False, bool)
    if print_atlas:
        extra_layers.append(impact_function.aggregation_summary)
    # create impact report instance
    report_metadata = ReportMetadata(
        metadata_dict=standard_impact_report_metadata_pdf)
    impact_report = ImpactReport(
        iface,
        report_metadata,
        impact_function=impact_function,
        extra_layers=extra_layers)

    # generate report folder

    # no other option for now
    # TODO: retrieve the information from data store
    if isinstance(impact_function.datastore.uri, QDir):
        layer_dir = impact_function.datastore.uri.absolutePath()
    else:
        # No other way for now
        return

    # We will generate it on the fly without storing it after datastore
    # supports
    impact_report.output_folder = os.path.join(layer_dir, 'output')
    return impact_report.process_components()


def generate_impact_map_report(impact_function, iface):
    """Generate impact map pdf from impact function.

    :param impact_function: The impact function used.
    :type impact_function: ImpactFunction

    :param iface: QGIS QGisAppInterface instance.
    :type iface: QGisAppInterface
    """
    # get the extra layers that we need
    extra_layers = []
    print_atlas = setting('print_atlas_report', False, bool)
    if print_atlas:
        extra_layers.append(impact_function.aggregation_summary)

    # get the hazard and exposure type
    hazard_layer = impact_function.hazard
    exposure_layer = impact_function.exposure

    hazard_type = layer_definition_type(hazard_layer)
    exposure_type = layer_definition_type(exposure_layer)

    # create impact report instance
    report_metadata = ReportMetadata(
        metadata_dict=update_template_component(
            component=map_report,
            hazard=hazard_type,
            exposure=exposure_type))
    impact_report = ImpactReport(
        iface,
        report_metadata,
        impact_function=impact_function,
        extra_layers=extra_layers)

    # Get other setting
    logo_path = setting('organisation_logo_path', None, basestring)
    impact_report.inasafe_context.organisation_logo = logo_path

    disclaimer_text = setting('reportDisclaimer', None, basestring)
    impact_report.inasafe_context.disclaimer = disclaimer_text

    north_arrow_path = setting('north_arrow_path', None, basestring)
    impact_report.inasafe_context.north_arrow = north_arrow_path

    # get the extent of impact layer
    impact_report.qgis_composition_context.extent = \
        impact_function.impact.extent()

    # generate report folder

    # no other option for now
    # TODO: retrieve the information from data store
    if isinstance(impact_function.datastore.uri, QDir):
        layer_dir = impact_function.datastore.uri.absolutePath()
    else:
        # No other way for now
        return

    # We will generate it on the fly without storing it after datastore
    # supports
    impact_report.output_folder = os.path.join(layer_dir, 'output')
    return impact_report.process_components()


def generate_infographic_report(impact_function, iface):
    """Generate impact map pdf from impact function.

    :param impact_function: The impact function used.
    :type impact_function: ImpactFunction

    :param iface: QGIS QGisAppInterface instance.
    :type iface: QGisAppInterface
    """
    # get the extra layers that we need
    extra_layers = []
    print_atlas = setting('print_atlas_report', False, bool)
    if print_atlas:
        extra_layers.append(impact_function.aggregation_summary)
    # create impact report instance
    report_metadata = ReportMetadata(
        metadata_dict=update_template_component(infographic_report))
    impact_report = ImpactReport(
        iface,
        report_metadata,
        impact_function=impact_function,
        extra_layers=extra_layers)

    # get the extent of impact layer
    impact_report.qgis_composition_context.extent = \
        impact_function.impact.extent()

    # generate report folder

    # no other option for now
    # TODO: retrieve the information from data store
    if isinstance(impact_function.datastore.uri, QDir):
        layer_dir = impact_function.datastore.uri.absolutePath()
    else:
        # No other way for now
        return

    # We will generate it on the fly without storing it after datastore
    # supports
    impact_report.output_folder = os.path.join(layer_dir, 'output')
    return impact_report.process_components()


def add_impact_layers_to_canvas(impact_function, iface):
    """Helper method to add impact layer to QGIS from impact function.

    :param impact_function: The impact function used.
    :type impact_function: ImpactFunction

    :param iface: QGIS QGisAppInterface instance.
    :type iface: QGisAppInterface
    """
    layers = impact_function.outputs
    name = impact_function.name

    # noinspection PyArgumentList
    root = QgsProject.instance().layerTreeRoot()
    group_analysis = root.insertGroup(0, name)
    group_analysis.setVisible(Qt.Checked)
    for layer in layers:
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().addMapLayer(layer, False)
        layer_node = group_analysis.addLayer(layer)

        # set layer title if any
        try:
            title = layer.keywords['title']
            if qgis_version() >= 21800:
                layer.setName(title)
            else:
                layer.setLayerName(title)
        except KeyError:
            pass

        visible_layers = [impact_function.impact.id()]
        print_atlas = setting('print_atlas_report', False, bool)
        if print_atlas:
            visible_layers.append(impact_function.aggregation_summary.id())
        # Let's enable only the more detailed layer. See #2925
        if layer.id() in visible_layers:
            layer_node.setVisible(Qt.Checked)
        elif is_raster_layer(layer):
            layer_node.setVisible(Qt.Checked)
        else:
            layer_node.setVisible(Qt.Unchecked)

        # we need to set analysis_impacted as an active layer because we need
        # to get all qgis variables that we need from this layer for
        # infographic.
        iface.setActiveLayer(impact_function.analysis_impacted)


def add_debug_layers_to_canvas(impact_function):
    """Helper method to add debug layers to QGIS from impact function.

    :param impact_function: The impact function used.
    :type impact_function: ImpactFunction
    """
    name = 'DEBUG %s' % impact_function.name
    root = QgsProject.instance().layerTreeRoot()
    group_debug = root.insertGroup(0, name)
    group_debug.setVisible(Qt.Unchecked)
    group_debug.setExpanded(False)

    # Let's style the hazard class in each layers.
    # noinspection PyBroadException
    try:
        classification = (
            impact_function.hazard.keywords['classification'])
        classification = definition(classification)

        classes = OrderedDict()
        for f in reversed(classification['classes']):
            classes[f['key']] = (f['color'], f['name'])
        hazard_class = hazard_class_field['key']
    except:
        # We might not have a classification. But this is the debug group so
        # let's not raise a new exception.
        classification = None

    datastore = impact_function.datastore
    for layer in datastore.layers():
        qgis_layer = datastore.layer(layer)
        if not isinstance(qgis_layer, QgsMapLayer):
            continue
        QgsMapLayerRegistry.instance().addMapLayer(
            qgis_layer, False)
        layer_node = group_debug.insertLayer(0, qgis_layer)
        layer_node.setVisible(Qt.Unchecked)
        layer_node.setExpanded(False)

        # Let's style layers which have a geometry and have
        # hazard_class
        if qgis_layer.type() == QgsMapLayer.VectorLayer:
            if qgis_layer.geometryType() != QGis.NoGeometry and classification:
                if qgis_layer.keywords['inasafe_fields'].get(hazard_class):
                    hazard_class_style(qgis_layer, classes, True)


def add_layer_to_canvas(layer, name, impact_function):
    """Helper method to add layer to QGIS.

    :param layer: The layer.
    :type layer: QgsMapLayer

    :param name: Layer name.
    :type name: str

    :param impact_function: The impact function used.
    :type impact_function: ImpactFunction

    :param iface: QGIS QGisAppInterface instance.
    :type iface: QGisAppInterface
    """
    group_name = impact_function.name

    # noinspection PyArgumentList
    root = QgsProject.instance().layerTreeRoot()
    group_analysis = root.findGroup(group_name)
    group_analysis.setVisible(Qt.Checked)

    layer.setLayerName(name)

    QgsMapLayerRegistry.instance().addMapLayer(layer, False)
    layer_node = group_analysis.addLayer(layer)

    layer_node.setVisible(Qt.Checked)


def remove_layer_from_canvas(layer, impact_function):
    """Helper method to remove layer from QGIS.

    :param layer: The layer.
    :type layer: QgsMapLayer

    :param impact_function: The impact function used.
    :type impact_function: ImpactFunction

    :param iface: QGIS QGisAppInterface instance.
    :type iface: QGisAppInterface
    """
    group_name = impact_function.name

    # noinspection PyArgumentList
    root = QgsProject.instance().layerTreeRoot()
    group_analysis = root.findGroup(group_name)
    group_analysis.setVisible(Qt.Checked)

    QgsMapLayerRegistry.instance().addMapLayer(layer, False)
    group_analysis.removeLayer(layer)
