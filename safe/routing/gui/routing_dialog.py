# coding=utf-8

import os
import logging

from qgis.gui import QgsMapToolPan
from qgis.core import QgsMapLayerRegistry
from PyQt4.QtGui import QDialog
from PyQt4 import uic

from safe.utilities.qgis_utilities import display_information_message_box
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.utilities import add_ordered_combo_item


LOGGER = logging.getLogger('InaSAFE')

ui_file = os.path.join(os.path.dirname(__file__), 'routing_dialog_base.ui')
FORM_CLASS, BASE_CLASS = uic.loadUiType(ui_file)


class RoutingDialog(QDialog, FORM_CLASS):
    """Routing analysis."""

    def __init__(self, parent=None, iface=None):
        """Constructor for import dialog.

        :param parent: Optional widget to use as parent
        :type parent: QWidget

        :param iface: An instance of QGisInterface
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
