# coding=utf-8
"""Analysis Utilities"""
import os
from collections import OrderedDict
from PyQt4.QtCore import QDir, Qt
from PyQt4.QtCore import QSettings
from qgis.core import QgsMapLayerRegistry, QgsProject, QgsMapLayer, QGis

from safe.definitionsv4.utilities import definition
from safe.definitionsv4.fields import hazard_class_field
from safe.definitionsv4.report import (
    standard_impact_report_metadata_pdf,
    report_a4_portrait_blue)
from safe.impact_function.style import hazard_class_style
from safe.gui.tools.minimum_needs.needs_profile import NeedsProfile
from safe.reportv4.report_metadata import ReportMetadata
from safe.reportv4.impact_report import ImpactReport as ImpactReportV4

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
    # get minimum needs profile
    minimum_needs = NeedsProfile()
    minimum_needs.load()

    # create impact report instance
    report_metadata = ReportMetadata(
        metadata_dict=standard_impact_report_metadata_pdf)
    impact_report = ImpactReportV4(
        iface,
        report_metadata,
        impact_function=impact_function,
        minimum_needs_profile=minimum_needs)

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
    impact_report.process_component()


def generate_impact_map_report(impact_function, iface):
    """Generate impact map pdf from impact function.

    :param impact_function: The impact function used.
    :type impact_function: ImpactFunction

    :param iface: QGIS QGisAppInterface instance.
    :type iface: QGisAppInterface
    """
    # create impact report instance
    report_metadata = ReportMetadata(
        metadata_dict=report_a4_portrait_blue)
    impact_report = ImpactReportV4(
        iface,
        report_metadata,
        impact_function=impact_function)

    # Get other setting
    settings = QSettings()
    logo_path = settings.value(
        'inasafe/organisation_logo_path', '', type=str)
    impact_report.inasafe_context.organisation_logo = logo_path

    disclaimer_text = settings.value(
        'inasafe/reportDisclaimer', '', type=str)
    impact_report.inasafe_context.disclaimer = disclaimer_text

    north_arrow_path = settings.value(
        'inasafe/north_arrow_path', '', type=str)
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
    impact_report.process_component()


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

        # Let's enable only the more detailed layer. See #2925
        if layer.id() == impact_function.impact.id():
            layer_node.setVisible(Qt.Checked)
            iface.setActiveLayer(layer)
        else:
            layer_node.setVisible(Qt.Unchecked)


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
    classification = (
        impact_function.hazard.keywords['classification'])
    classification = definition(classification)

    classes = OrderedDict()
    for f in reversed(classification['classes']):
        classes[f['key']] = (f['color'], f['name'])
    hazard_class = hazard_class_field['key']

    datastore = impact_function.datastore
    for layer in datastore.layers():
        qgis_layer = datastore.layer(layer)
        QgsMapLayerRegistry.instance().addMapLayer(
            qgis_layer, False)
        layer_node = group_debug.insertLayer(0, qgis_layer)
        layer_node.setVisible(Qt.Unchecked)
        layer_node.setExpanded(False)

        # Let's style layers which have a geometry and have
        # hazard_class
        if qgis_layer.type() == QgsMapLayer.VectorLayer:
            if qgis_layer.geometryType() != QGis.NoGeometry:
                if qgis_layer.keywords['inasafe_fields'].get(hazard_class):
                    hazard_class_style(qgis_layer, classes, True)
