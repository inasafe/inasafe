# coding=utf-8

"""Analysis Utilities."""

from collections import OrderedDict

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtXml import QDomDocument
from qgis.core import (
    Qgis,
    QgsWkbTypes,
    QgsMapLayer,
    QgsProject,
)

from safe.definitions.constants import MULTI_EXPOSURE_ANALYSIS_FLAG
from safe.definitions.fields import hazard_class_field
from safe.definitions.utilities import definition
from safe.gis.tools import load_layer
from safe.impact_function.impact_function_utilities import (
    FROM_CANVAS,
)
from safe.impact_function.style import hazard_class_style
from safe.utilities.gis import qgis_version
from safe.utilities.metadata import active_classification
from safe.utilities.settings import setting

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def add_impact_layers_to_canvas(impact_function, group=None, iface=None):
    """Helper method to add impact layer to QGIS from impact function.

    :param impact_function: The impact function used.
    :type impact_function: ImpactFunction

    :param group: An existing group as a parent, optional.
    :type group: QgsLayerTreeGroup

    :param iface: QGIS QgisAppInterface instance.
    :type iface: QgisAppInterface
    """
    layers = impact_function.outputs
    name = impact_function.name

    if group:
        group_analysis = group
    else:
        # noinspection PyArgumentList
        root = QgsProject.instance().layerTreeRoot()
        group_analysis = root.insertGroup(0, name)
        group_analysis.setVisible(Qt.Checked)

    group_analysis.setExpanded(group is None)

    for layer in layers:
        # noinspection PyArgumentList
        QgsProject.instance().addMapLayer(layer, False)
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
        QgsProject.instance().addMapLayer(
            qgis_layer, False)
        layer_node = group_debug.insertLayer(0, qgis_layer)
        layer_node.setVisible(Qt.Unchecked)
        layer_node.setExpanded(False)

        # Let's style layers which have a geometry and have
        # hazard_class
        if qgis_layer.type() == QgsMapLayer.VectorLayer:
            if qgis_layer.geometryType() != QgsWkbTypes.NoGeometry and classification:
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

    :param iface: QGIS QgisAppInterface instance.
    :type iface: QgisAppInterface
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
            style.setContent(layer_definition[3])
            layer = load_layer(layer_definition[2], layer_definition[1])[0]
            layer.importNamedStyle(style)
            QgsProject.instance().addMapLayer(layer, False)
            layer_node = group_analysis.addLayer(layer)
            layer_node.setVisible(Qt.Checked)
        else:
            if layer_definition[2] == impact_function.name:
                for layer in impact_function.outputs:
                    if layer.keywords['layer_purpose'] == layer_definition[1]:
                        QgsProject.instance().addMapLayer(
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
                                QgsProject.instance().addMapLayer(
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

    QgsProject.instance().addMapLayer(layer, False)
