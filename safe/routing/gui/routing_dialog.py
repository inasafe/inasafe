# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid / DFAT -
**New Metadata for SAFE.**

Contact : etienne@kartoza.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.
"""

import logging
import shutil
from random import randint
from os.path import dirname, join, splitext

from processing.core.Processing import Processing
from processing.modeler import ModelerAlgorithm
from processing import runalg
from qgis.gui import QgsMapToolPan
from qgis.core import (
    QgsMapLayerRegistry,
    QgsVectorLayer,
    QgsSymbolV2,
    QgsRendererCategoryV2,
    QgsCategorizedSymbolRendererV2,
    QgsVectorGradientColorRampV2,
    QgsGraduatedSymbolRendererV2)
from PyQt4.QtGui import QDialog, QColor
from PyQt4 import uic
from PyQt4.QtCore import Qt, QVariant

from safe.common.exceptions import (
    KeywordNotFoundError,
    NoKeywordsFoundError)
from safe.utilities.qgis_utilities import display_information_message_box
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.utilities import add_ordered_combo_item
from safe.common.utilities import temp_dir, unique_filename

LOGGER = logging.getLogger('InaSAFE')

ui_file = join(dirname(__file__), 'routing_dialog_base.ui')
FORM_CLASS, BASE_CLASS = uic.loadUiType(ui_file)


class RoutingDialog(QDialog, FORM_CLASS):
    """Routing analysis."""

    def __init__(self, parent=None, iface=None):
        """Constructor for import dialog.

        :param parent: Optional widget to use as parent.
        :type parent: QWidget

        :param iface: An instance of QGisInterface.
        :type iface: QGisInterface
        """
        QDialog.__init__(self, parent)
        self.parent = parent
        self.setupUi(self)

        self.setWindowTitle(self.tr('InaSAFE Routing Analysis'))
        self.keyword_io = KeywordIO()
        self.iface = iface
        self.populate_combo()

    def populate_combo(self):
        """Add layers to combos according to keywords."""
        registry = QgsMapLayerRegistry.instance()
        layers = registry.mapLayers().values()

        self.cbo_hazard_layer.clear()
        self.cbo_roads_layer.clear()
        self.cbo_idp_layer.clear()

        for layer in layers:
            name = layer.name()
            source = layer.id()
            # See if there is a title for this layer, if not,
            # fallback to the layer's filename

            # noinspection PyBroadException
            try:
                title = self.keyword_io.read_keywords(layer, 'title')
            except NoKeywordsFoundError:
                # Skip if there are no keywords at all
                continue
            except:  # pylint: disable=W0702
                # automatically adding file name to title in keywords
                # See #575
                try:
                    self.keyword_io.update_keywords(layer, {'title': name})
                    title = name
                except UnsupportedProviderError:
                    continue
            else:
                # Lookup internationalised title if available
                title = self.tr(title)

            # noinspection PyBroadException
            try:
                layer_purpose = self.keyword_io.read_keywords(
                    layer, 'layer_purpose')
            except:  # pylint: disable=W0702
                # continue ignoring this layer
                continue

            if layer_purpose == 'hazard':
                # noinspection PyBroadException
                try:
                    hazard_type = self.keyword_io.read_keywords(
                        layer, 'hazard')
                except:  # pylint: disable=W0702
                    # continue ignoring this layer
                    continue
                if hazard_type == 'flood':
                    # noinspection PyBroadException
                    try:
                        hazard_geometry = self.keyword_io.read_keywords(
                            layer, 'layer_geometry')
                    except:  # pylint: disable=W0702
                        # continue ignoring this layer
                        continue
                    if hazard_geometry == 'polygon':
                        add_ordered_combo_item(
                            self.cbo_hazard_layer, title, source)
            elif layer_purpose == 'exposure':
                # noinspection PyBroadException
                try:
                    exposure_type = self.keyword_io.read_keywords(
                        layer, 'exposure')
                except:  # pylint: disable=W0702
                    # continue ignoring this layer
                    continue
                if exposure_type == 'road':
                    add_ordered_combo_item(self.cbo_roads_layer, title, source)
                else:
                    continue

            elif layer_purpose == 'idp':
                add_ordered_combo_item(self.cbo_idp_layer, title, source)

    def get_hazard_layer(self):
        """Get the QgsMapLayer currently selected in the hazard combo.

        Obtain QgsMapLayer id from the userrole of the QtCombo for hazard
        and return it as a QgsMapLayer.

        :returns: The currently selected map layer in the hazard combo.
        :rtype: QgsMapLayer

        """
        index = self.cbo_hazard_layer.currentIndex()
        if index < 0:
            return None
        layer_id = self.cbo_hazard_layer.itemData(
            index, Qt.UserRole)
        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        return layer

    def get_idp_layer(self):
        """Get the QgsMapLayer currently selected in the idp combo.

        Obtain QgsMapLayer id from the userrole of the QtCombo for idp
        and return it as a QgsMapLayer.

        :returns: Currently selected map layer in the exposure combo.
        :rtype: QgsMapLayer
        """

        index = self.cbo_idp_layer.currentIndex()
        if index < 0:
            return None
        layer_id = self.cbo_idp_layer.itemData(
            index, Qt.UserRole)
        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        return layer

    def get_roads_layer(self):
        """Get the QgsMapLayer currently selected in the exposure combo.

        Obtain QgsMapLayer id from the userrole of the QtCombo for roads
        and return it as a QgsMapLayer.

        :returns: Currently selected map layer in the exposure combo.
        :rtype: QgsMapLayer
        """

        index = self.cbo_roads_layer.currentIndex()
        if index < 0:
            return None
        layer_id = self.cbo_roads_layer.itemData(
            index, Qt.UserRole)
        layer = QgsMapLayerRegistry.instance().mapLayer(layer_id)
        return layer

    @staticmethod
    def replace_value(file_path, old, new):
        """Replace a value in a file by another one.

        :param file_path: The file path to edit.
        :type file_path: str

        :param old: The old value to replace.
        :type old: str

        :param new: The new value.
        :type new: str
        """
        new = unicode(new)
        f = open(file_path, 'r')
        file_data = f.read()
        f.close()

        new_data = file_data.replace(old, new)

        f = open(file_path, 'w')
        f.write(new_data)
        f.close()

    @staticmethod
    def add_processing_model(file_path):
        """Add a model file path to processing.

        :param file_path: The file path for the model.
        :type file_path: str

        :return The command line to use to call the model.
        :rtype str
        """
        model = ModelerAlgorithm.ModelerAlgorithm.fromFile(file_path)
        model.provider = Processing.modeler
        Processing.modeler.algs.append(model)
        command_line = model.commandLineName()
        Processing.algs['model'][command_line] = model
        return command_line

    @staticmethod
    def random_color():
        """Get a random hexadecimal color.

        :return: A random hexadecimal color.
        :rtype: str
        """
        r = randint(0, 255)
        g = randint(0, 255)
        b = randint(0, 255)
        return '#%02X%02X%02X' % (r, g, b)

    def accept(self):
        """Launch the routing analysis and display it in QGIS.
        Expected outputs:
          - Exit layer with costs
          - Route from exit to IDP
          - Flood edge with IDP
          - New IDP layer
          - New roads layer with flood edges (inundated, not inundated)
        """

        # Get forms input.
        roads_layer = self.get_roads_layer()
        flood_layer = self.get_hazard_layer()
        idp_layer = self.get_idp_layer()

        coefficient_flood_edge = self.spin_flood_edge.value()
        coefficient_road = self.spin_road.value()

        routable_model = join(
            dirname(dirname(__file__)), 'models', 'inasafe_network.model')
        model = self.add_processing_model(routable_model)

        flood_value_map = self.keyword_io.read_keywords(
            flood_layer, 'value_map')
        wet_value = flood_value_map['wet'][0]

        flood_field = self.keyword_io.read_keywords(flood_layer, 'field')

        # Get outputs.
        file_name_exit = unique_filename(suffix='-exit.shp')
        file_name_network = unique_filename(suffix='-network.shp')
        file_name_edge = unique_filename(suffix='-edges.shp')
        file_name_idp = unique_filename(suffix='-idp.shp')
        file_name_route = unique_filename(suffix='-routes.shp')

        # Run the model.
        runalg(
            model,
            roads_layer.source(),
            idp_layer.source(),
            flood_layer.source(),
            flood_field,
            wet_value,
            coefficient_road,
            coefficient_flood_edge,
            file_name_edge,
            file_name_idp,
            file_name_route,
            file_name_exit,
            file_name_network)

        # Styling with a QML for the network layer.
        network_qml = join(dirname(dirname(__file__)), 'styles', 'network.qml')
        base_name_network = splitext(file_name_network)[0]
        destination_network_qml = '%s.qml' % base_name_network
        shutil.copyfile(network_qml, destination_network_qml)
        self.replace_value(
            destination_network_qml, '{{flood_edge}}', coefficient_flood_edge)
        self.replace_value(
            destination_network_qml, '{{dry}}', coefficient_road)
        network_layer = QgsVectorLayer(file_name_network, 'Network', 'ogr')
        QgsMapLayerRegistry.instance().addMapLayer(network_layer)

        # Get one color for each IDP
        # value -> (color, label)
        list_idp = {}
        new_idp_layer = QgsVectorLayer(file_name_idp, 'IDP', 'ogr')
        id_field_index = new_idp_layer.dataProvider().fieldNameIndex('id')
        for feature in new_idp_layer.getFeatures():
            id = feature.attributes()[id_field_index]
            if id not in list_idp:
                list_idp[id] = (self.random_color(), id)

        # Styling the IDP layer.
        categories = []
        for idp_id, (color, label) in list_idp.items():
            symbol = QgsSymbolV2.defaultSymbol(new_idp_layer.geometryType())
            symbol.setColor(QColor(color))
            category = QgsRendererCategoryV2(str(idp_id), symbol, str(label))
            categories.append(category)

        expression = 'id'
        renderer = QgsCategorizedSymbolRendererV2(expression, categories)
        new_idp_layer.setRendererV2(renderer)
        QgsMapLayerRegistry.instance().addMapLayer(new_idp_layer)

        # Styling routes.
        routes_layer = QgsVectorLayer(file_name_route, 'Routes', 'ogr')
        categories = []
        for idp_id, (color, label) in list_idp.items():
            symbol = QgsSymbolV2.defaultSymbol(routes_layer.geometryType())
            symbol.setColor(QColor(color))
            category = QgsRendererCategoryV2(str(idp_id), symbol, str(label))
            categories.append(category)

        expression = 'id_idp'
        renderer = QgsCategorizedSymbolRendererV2(expression, categories)
        routes_layer.setRendererV2(renderer)
        QgsMapLayerRegistry.instance().addMapLayer(routes_layer)

        # Styling edges.
        edges_layer = QgsVectorLayer(file_name_edge, 'Edges', 'ogr')
        categories = []
        for idp_id, (color, label) in list_idp.items():
            symbol = QgsSymbolV2.defaultSymbol(edges_layer.geometryType())
            symbol.setColor(QColor(color))
            category = QgsRendererCategoryV2(str(idp_id), symbol, str(label))
            categories.append(category)

        expression = 'id_idp'
        renderer = QgsCategorizedSymbolRendererV2(expression, categories)
        edges_layer.setRendererV2(renderer)
        QgsMapLayerRegistry.instance().addMapLayer(edges_layer)

        # Styling exits.
        exits_layer = QgsVectorLayer(file_name_exit, 'Exits', 'ogr')
        symbol = QgsSymbolV2.defaultSymbol(idp_layer.geometryType())
        # noinspection PyCallByClass
        color_ramp = QgsVectorGradientColorRampV2.create({
            'color1': '0,255,0,255',
            'color2': '255,0,0,255',
            'stops': '0.5;255,255,0,255'})

        # noinspection PyCallByClass
        renderer = QgsGraduatedSymbolRendererV2.createRenderer(
            exits_layer,
            'cost',
            5,
            QgsGraduatedSymbolRendererV2.Jenks,
            symbol,
            color_ramp)

        exits_layer.setRendererV2(renderer)
        QgsMapLayerRegistry.instance().addMapLayer(exits_layer)

        # Reading existing keywords about exposure, hazard and IDP.
        idp_keywords = self.keyword_io.read_keywords(idp_layer)
        flood_keywords = self.keyword_io.read_keywords(flood_layer)
        roads_keywords = self.keyword_io.read_keywords(roads_layer)

        # General keywords IDP
        keywords = {}
        try:
            keywords['exposure_title'] = roads_keywords['title']
        except IndexError:
            pass
        try:
            keywords['hazard_title'] = flood_keywords['title']
        except IndexError:
            pass
        try:
            keywords['idp_title'] = idp_keywords['title']
        except IndexError:
            pass

        keywords['exposure'] = 'road'
        keywords['hazard'] = 'flood'

        new_idp_keywords = dict(keywords)
        new_idp_keywords['title'] = 'Routing analysis : IDP'
        self.keyword_io.write_keywords(new_idp_layer, new_idp_keywords)

        new_network_keywords = dict(keywords)
        new_network_keywords['title'] = 'Routing analysis : Network'
        self.keyword_io.write_keywords(network_layer, new_network_keywords)

        new_edge_keywords = dict(keywords)
        new_edge_keywords['title'] = 'Routing analysis : Edges'
        self.keyword_io.write_keywords(edges_layer, new_edge_keywords)

        new_route_keywords = dict(keywords)
        new_route_keywords['title'] = 'Routing analysis : Routes'
        self.keyword_io.write_keywords(routes_layer, new_route_keywords)

        new_exit_keywords = dict(keywords)
        new_exit_keywords['title'] = 'Routing analysis : Exits'
        self.keyword_io.write_keywords(exits_layer, new_exit_keywords)

        self.close()
