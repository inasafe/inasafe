# coding=utf-8

"""Analysis Utilities."""

import os
from collections import OrderedDict
from copy import deepcopy

from PyQt4.QtCore import QDir, Qt
from PyQt4.QtXml import QDomDocument
from qgis.core import (
    QGis,
    QgsMapLayer,
    QgsMapLayerRegistry,
    QgsProject,
    QgsRasterLayer,
)

from safe.definitions.constants import MULTI_EXPOSURE_ANALYSIS_FLAG
from safe.definitions.exposure import exposure_population
from safe.definitions.fields import hazard_class_field
from safe.definitions.reports.components import (
    map_report, all_default_report_components, infographic_report)
from safe.definitions.reports.infographic import map_overview
from safe.definitions.utilities import definition, update_template_component
from safe.gis.tools import load_layer
from safe.impact_function.impact_function_utilities import (
    FROM_CANVAS,
)
from safe.impact_function.style import hazard_class_style
from safe.report.impact_report import ImpactReport
from safe.report.report_metadata import ReportMetadata
from safe.utilities.gis import qgis_version
from safe.utilities.metadata import active_classification
from safe.utilities.settings import setting
from safe.utilities.unicode import get_string

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def generate_report(impact_function, iface):
    """Generate Impact Report from an Impact Function.

    :param impact_function: The impact function to be used.
    :type impact_function: ImpactFunction

    :param iface: QGIS QGisAppInterface instance.
    :type iface: QGisAppInterface
    """
    # generate report from component definition
    report_components = deepcopy(all_default_report_components)

    # don't generate infographic if exposure is not population
    exposure_type = definition(
        impact_function.provenance['exposure_keywords']['exposure'])
    map_overview_layer = None
    if exposure_type != exposure_population:
        report_components.remove(infographic_report)
    else:
        map_overview_layer = QgsRasterLayer(
            map_overview['path'], 'Overview')
        add_layer_to_canvas(
            map_overview_layer, map_overview['id'])

    extra_layers = []
    print_atlas = setting('print_atlas_report', False, bool)

    hazard_type = definition(
        impact_function.provenance['hazard_keywords']['hazard'])
    aggregation_summary_layer = impact_function.aggregation_summary

    if print_atlas:
        extra_layers.append(aggregation_summary_layer)

    for component in report_components:
        # create impact report instance

        if component['key'] == map_report['key']:
            report_metadata = ReportMetadata(
                metadata_dict=update_template_component(
                    component=component,
                    hazard=hazard_type,
                    exposure=exposure_type))
        else:
            report_metadata = ReportMetadata(
                metadata_dict=update_template_component(component))

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
        error_code, message = impact_report.process_components()
        if error_code == ImpactReport.REPORT_GENERATION_FAILED:
            break

    if map_overview_layer:
        QgsMapLayerRegistry.instance().removeMapLayer(map_overview_layer)

    return error_code, message


def add_impact_layers_to_canvas(impact_function, group=None, iface=None):
    """Helper method to add impact layer to QGIS from impact function.

    :param impact_function: The impact function used.
    :type impact_function: ImpactFunction

    :param group: An existing group as a parent, optional.
    :type group: QgsLayerTreeGroup

    :param iface: QGIS QGisAppInterface instance.
    :type iface: QGisAppInterface
    """
    layers = impact_function.outputs
    name = impact_function.name

    if iface:
        # noinspection PyArgumentList
        root = QgsProject.instance().layerTreeRoot()
        group_analysis = root.insertGroup(0, name)
        group_analysis.setVisible(Qt.Checked)
    else:
        group_analysis = group

    group_analysis.setExpanded(group is None)

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
        else:
            layer_node.setVisible(Qt.Unchecked)

        # we need to set analysis_impacted as an active layer because we need
        # to get all qgis variables that we need from this layer for
        # infographic.
        if iface:
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
    hazard_keywords = impact_function.provenance['hazard_keywords']
    exposure_keywords = impact_function.provenance['exposure_keywords']

    # Let's style the hazard class in each layers.
    # noinspection PyBroadException
    try:
        classification = active_classification(
            hazard_keywords, exposure_keywords['exposure'])
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


def add_layers_to_canvas_with_custom_orders(
        order, impact_function, iface=None):
    """Helper to add layers to the map canvas following a specific order.

    From top to bottom in the legend:
        [
            ('FromCanvas', layer name, full layer URI, QML),
            ('FromAnalysis', layer purpose, layer group, None),
            ...
        ]

        The full layer URI is coming from our helper.

    :param order: Special structure the list of layers to add.
    :type order: list

    :param impact_function: The multi exposure impact function used.
    :type impact_function: MultiExposureImpactFunction

    :param iface: QGIS QGisAppInterface instance.
    :type iface: QGisAppInterface
    """
    root = QgsProject.instance().layerTreeRoot()
    root.setVisible(False)  # Make all layers hidden.

    group_analysis = root.insertGroup(0, impact_function.name)
    group_analysis.setVisible(Qt.Checked)
    group_analysis.setCustomProperty(MULTI_EXPOSURE_ANALYSIS_FLAG, True)

    # Insert layers in the good order in the group.
    for layer_definition in order:
        if layer_definition[0] == FROM_CANVAS['key']:
            style = QDomDocument()
            style.setContent(get_string(layer_definition[3]))
            layer = load_layer(layer_definition[2], layer_definition[1])[0]
            layer.importNamedStyle(style)
            QgsMapLayerRegistry.instance().addMapLayer(layer, False)
            layer_node = group_analysis.addLayer(layer)
            layer_node.setVisible(Qt.Checked)
        else:
            if layer_definition[2] == impact_function.name:
                for layer in impact_function.outputs:
                    if layer.keywords['layer_purpose'] == layer_definition[1]:
                        QgsMapLayerRegistry.instance().addMapLayer(
                            layer, False)
                        layer_node = group_analysis.addLayer(layer)
                        layer_node.setVisible(Qt.Checked)
                        try:
                            title = layer.keywords['title']
                            if qgis_version() >= 21800:
                                layer.setName(title)
                            else:
                                layer.setLayerName(title)
                        except KeyError:
                            pass
                        break
            else:
                for sub_impact_function in impact_function.impact_functions:
                    # Iterate over each sub impact function used in the
                    # multi exposure analysis.
                    if sub_impact_function.name == layer_definition[2]:
                        for layer in sub_impact_function.outputs:
                            purpose = layer_definition[1]
                            if layer.keywords['layer_purpose'] == purpose:
                                QgsMapLayerRegistry.instance().addMapLayer(
                                    layer, False)
                                layer_node = group_analysis.addLayer(
                                    layer)
                                layer_node.setVisible(Qt.Checked)
                                try:
                                    title = layer.keywords['title']
                                    if qgis_version() >= 21800:
                                        layer.setName(title)
                                    else:
                                        layer.setLayerName(title)
                                except KeyError:
                                    pass
                                break

    if iface:
        iface.setActiveLayer(impact_function.analysis_impacted)


def add_layer_to_canvas(layer, name):
    """Helper method to add layer to QGIS.

    :param layer: The layer.
    :type layer: QgsMapLayer

    :param name: Layer name.
    :type name: str

    """
    if qgis_version() >= 21800:
        layer.setName(name)
    else:
        layer.setLayerName(name)

    QgsMapLayerRegistry.instance().addMapLayer(layer, False)
