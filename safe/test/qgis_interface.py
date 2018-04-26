# coding=utf-8

"""Fake QGIS Interface."""

import logging

from qgis.PyQt.QtCore import QObject, pyqtSlot, pyqtSignal
from qgis.core import QgsMapLayer, QgsProject
from qgis.gui import QgsLayerTreeMapCanvasBridge
# pylint: disable=no-name-in-module
from qgis.gui import QgsMessageBar

from safe.test.qgis_legend_interface import QgisLegend

__author__ = 'tim@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = (
    'Copyright (c) 2010 by Ivan Mincik, ivan.mincik@gista.sk and '
    'Copyright (c) 2011 German Carrillo, geotux_tuxman@linuxmail.org'
    'Copyright (c) 2014 Tim Sutton, tim@kartoza.com'
)

LOGGER = logging.getLogger('InaSAFE')


# noinspection PyMethodMayBeStatic,PyPep8Naming
class QgisInterface(QObject):

    """Class to expose qgis objects and functions to plugins.

    This class is here for enabling us to run unit tests only,
    so most methods are simply stubs.
    """

    currentLayerChanged = pyqtSignal(QgsMapLayer)
    layerSavedAs = pyqtSignal(QgsMapLayer, str)

    def __init__(self, canvas):
        """Constructor.

        :param canvas:
        """
        QObject.__init__(self)
        self.canvas = canvas
        self.legend = QgisLegend(canvas)
        self.message_bar = QgsMessageBar(None)
        # Set up slots so we can mimic the behaviour of QGIS when layers
        # are added.
        LOGGER.debug('Initialising canvas...')
        # noinspection PyArgumentList
        QgsProject.instance().layersAdded.connect(self.addLayers)
        # noinspection PyArgumentList
        QgsProject.instance().layerWasAdded.connect(self.addLayer)
        # noinspection PyArgumentList
        QgsProject.instance().removeAll.connect(self.removeAllLayers)

        # For processing module
        self.destCrs = None
        # For keeping track of which layer is active in the legend.
        self.active_layer = None

        # In the next section of code, we are going to do some monkey patching
        # to make the QGIS processing framework think that this mock QGIS IFACE
        # instance is the actual one. It will also ensure that the processing
        # algorithms are nicely loaded and available for use.

        # noinspection PyUnresolvedReferences
        from processing.tools import dataobjects

        # noinspection PyUnresolvedReferences
        import processing
        # noinspection PyUnresolvedReferences
        from processing.core.Processing import Processing
        # pylint: enable=F0401, E0611
        processing.classFactory(self)

        # We create our own getAlgorithm function below which will will monkey
        # patch in to the Processing class in QGIS in order to ensure that the
        # Processing.initialize() call is made before asking for an alg.

        @staticmethod
        def mock_getAlgorithm(name):
            """
            Modified version of the original getAlgorithm function.

            :param name: Name of the algorithm to load.
            :type name: str

            :return: An algorithm concrete class.
            :rtype: QgsAlgorithm  ?
            """
            Processing.initialize()
            # FIXME: Had some weird bug in QGIS 2.18 MacOSX (KyngChaos)
            try:
                providers = list(Processing.algs.values())
            except BaseException:
                providers = list(Processing.algs().values())

            for provider in providers:
                if name in provider:
                    return provider[name]
            return None

        # Now we let the monkey loose!
        Processing.getAlgorithm = mock_getAlgorithm
        # We also need to make dataobjects think that this iface is 'the one'
        # Note. the placement here (after the getAlgorithm monkey patch above)
        # is significant, so don't move it!
        dataobjects.iface = self

        # set up a layer tree bridge so that new added layers appear in legend
        self.layer_tree_root = QgsProject.instance().layerTreeRoot()
        self.bridge = QgsLayerTreeMapCanvasBridge(
            self.layer_tree_root, self.canvas)
        self.bridge.setCanvasLayers()

    def __getattr__(self, *args, **kwargs):
        # It's for processing module
        def dummy(*a, **kwa):
            _ = a, kwa  # NOQA
            return None
        return dummy

    def __iter__(self):
        # It's for processing module
        return self

    def __next__(self):
        # It's for processing module
        raise StopIteration

    def layers(self):
        # It's for processing module
        # simulate iface.legendInterface().layers()
        return list(QgsProject.instance().mapLayers().values())

    def addLayers(self, layers):
        """Handle layers being added to the registry so they show up in canvas.

        :param layers: list<QgsMapLayer> list of map layers that were added

        .. note:: The QgsInterface api does not include this method,
            it is added here as a helper to facilitate testing.
        """
        # LOGGER.debug('addLayers called on qgis_interface')
        # LOGGER.debug('Number of layers being added: %s' % len(layers))
        # LOGGER.debug('Layer Count Before: %s' % len(self.canvas.layers()))
        current_layers = self.canvas.layers()
        final_layers = []
        # We need to keep the record of the registered layers on our canvas!
        registered_layers = []
        for layer in current_layers:
            final_layers.append(layer)
            registered_layers.append(layer.id())
        for layer in layers:
            if layer.id() not in registered_layers:
                final_layers.append(layer)

        self.canvas.setLayers(final_layers)
        # LOGGER.debug('Layer Count After: %s' % len(self.canvas.layers()))

    @pyqtSlot(QgsMapLayer)
    def addLayer(self, layer):
        """Handle a layer being added to the registry so it shows up in canvas.

        :param layer: list<QgsMapLayer> list of map layers that were added

        .. note: The QgsInterface api does not include this method, it is added
                 here as a helper to facilitate testing.

        .. note: The addLayer method was deprecated in QGIS 1.8 so you should
                 not need this method much.
        """
        pass

    @pyqtSlot()
    def removeAllLayers(self, ):
        """Remove layers from the canvas before they get deleted.

        .. note:: This is NOT part of the QgisInterface API but is needed
            to support QgsProject.instance().removeAllLayers().

        """
        self.canvas.setLayers([])
        self.active_layer = None

    def newProject(self):
        """Create new project."""
        # noinspection PyArgumentList
        QgsProject.instance().removeAllMapLayers()

    # ---------------- API Mock for QgsInterface follows -------------------

    def zoomFull(self):
        """Zoom to the map full extent."""
        pass

    def zoomToPrevious(self):
        """Zoom to previous view extent."""
        pass

    def zoomToNext(self):
        """Zoom to next view extent."""
        pass

    def zoomToActiveLayer(self):
        """Zoom to extent of active layer."""
        pass

    def addVectorLayer(self, path, base_name, provider_key):
        """Add a vector layer.

        :param path: Path to layer.
        :type path: str

        :param base_name: Base name for layer.
        :type base_name: str

        :param provider_key: Provider key e.g. 'ogr'
        :type provider_key: str
        """
        pass

    def addRasterLayer(self, path, base_name):
        """Add a raster layer given a raster layer file name

        :param path: Path to layer.
        :type path: str

        :param base_name: Base name for layer.
        :type base_name: str
        """
        pass

    def setActiveLayer(self, layer):
        """Set the currently active layer in the legend.
        :param layer: Layer to make active.
        :type layer: QgsMapLayer, QgsVectorLayer, QgsRasterLayer
        """
        self.active_layer = layer

    def activeLayer(self):
        """Get pointer to the active layer (layer selected in the legend)."""
        if self.active_layer is not None:
            return self.active_layer
        else:
            return None

    def addToolBarIcon(self, action):
        """Add an icon to the plugins toolbar.

        :param action: Action to add to the toolbar.
        :type action: QAction
        """
        pass

    def removeToolBarIcon(self, action):
        """Remove an action (icon) from the plugin toolbar.

        :param action: Action to add to the toolbar.
        :type action: QAction
        """
        pass

    def addToolBar(self, name):
        """Add toolbar with specified name.

        :param name: Name for the toolbar.
        :type name: str
        """
        pass

    def mapCanvas(self):
        """Return a pointer to the map canvas."""
        return self.canvas

    def mainWindow(self):
        """Return a pointer to the main window.

        In case of QGIS it returns an instance of QgisApp.
        """
        pass

    def addDockWidget(self, area, dock_widget):
        """Add a dock widget to the main window.

        :param area: Where in the ui the dock should be placed.
        :type area:

        :param dock_widget: A dock widget to add to the UI.
        :type dock_widget: QDockWidget
        """
        pass

    def legendInterface(self):
        """Get the legend.

        See also discussion at:

        https://github.com/AIFDR/inasafe/pull/924/

        Implementation added for version 3.2.
        """
        return self.legend

    def messageBar(self):
        """Get the message bar.

        .. versionadded:: 3.2

        :returns: A QGIS message bar instance
        :rtype: QgsMessageBar
        """
        return self.message_bar
