# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**QGIS plugin implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. note:: This source code was copied from the 'postgis viewer' application
     with original authors:
     Copyright (c) 2010 by Ivan Mincik, ivan.mincik@gista.sk
     Copyright (c) 2011 German Carrillo, geotux_tuxman@linuxmail.org

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = ('Copyright (c) 2010 by Ivan Mincik, ivan.mincik@gista.sk and '
                 'Copyright (c) 2011 German Carrillo, '
                 'geotux_tuxman@linuxmail.org')

import logging
from PyQt4.QtCore import QObject, pyqtSlot, pyqtSignal
from qgis.core import QgsMapLayerRegistry
from qgis.gui import QgsMapCanvasLayer
LOGGER = logging.getLogger('InaSAFE')


#noinspection PyMethodMayBeStatic,PyPep8Naming
class QgisInterface(QObject):
    """Class to expose qgis objects and functionalities to plugins.

    This class is here for enabling us to run unit tests only,
    so most methods are simply stubs.
    """
    currentLayerChanged = pyqtSignal(QgsMapCanvasLayer)

    def __init__(self, canvas):
        """Constructor
        :param canvas:
        """
        QObject.__init__(self)
        self.canvas = canvas
        # Set up slots so we can mimic the behaviour of QGIS when layers
        # are added.
        LOGGER.debug('Initialising canvas...')
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().layersAdded.connect(self.addLayers)
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().layerWasAdded.connect(self.addLayer)

    @pyqtSlot('QStringList')
    def addLayers(self, theLayers):
        """Handle layers being added to the registry so they show up in canvas.

        :param theLayers: list<QgsMapLayer> list of map layers that were added
        .. note:: The QgsInterface api does not include this method,
            it is added here as a helper to facilitate testing.
        """
        #LOGGER.debug('addLayers called on qgis_interface')
        #LOGGER.debug('Number of layers being added: %s' % len(theLayers))
        #LOGGER.debug('Layer Count Before: %s' % len(self.canvas.layers()))
        myLayers = self.canvas.layers()
        myCanvasLayers = []
        for myLayer in myLayers:
            myCanvasLayers.append(QgsMapCanvasLayer(myLayer))
        for myLayer in theLayers:
            myCanvasLayers.append(QgsMapCanvasLayer(myLayer))

        self.canvas.setLayerSet(myCanvasLayers)
        #LOGGER.debug('Layer Count After: %s' % len(self.canvas.layers()))

    @pyqtSlot('QgsMapLayer')
    def addLayer(self, theLayer):
        """Handle a layer being added to the registry so it shows up in canvas.

        :param theLayer: list<QgsMapLayer> list of map layers that were added
        .. note: The QgsInterface api does not include this method, it is added
                 here as a helper to facilitate testing.

        .. note: The addLayer method was deprecated in QGIS 1.8 so you should
                 not need this method much.
        """
        pass

    def newProject(self):
        """Create new project
        """
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().removeAllMapLayers()

    # ---------------- API Mock for QgsInterface follows -------------------

    def zoomFull(self):
        """Zoom to the map full extent"""
        pass

    def zoomToPrevious(self):
        """Zoom to previous view extent"""
        pass

    def zoomToNext(self):
        """Zoom to next view extent"""
        pass

    def zoomToActiveLayer(self):
        """Zoom to extent of active layer"""
        pass

    def addVectorLayer(self, vectorLayerPath, baseName, providerKey):
        """Add a vector layer
        :param baseName:
        :param providerKey:
        :param vectorLayerPath:
        """
        pass

    def addRasterLayer(self, rasterLayerPath, baseName):
        """Add a raster layer given a raster layer file name
        :param rasterLayerPath:
        :param baseName:
        """
        pass

    def activeLayer(self):
        """Get pointer to the active layer (layer selected in the legend)"""
        # noinspection PyArgumentList
        myLayers = QgsMapLayerRegistry.instance().mapLayers()
        for myItem in myLayers:
            return myLayers[myItem]

    def addToolBarIcon(self, qAction):
        """Add an icon to the plugins toolbar
        :param qAction:
        """
        pass

    def removeToolBarIcon(self, qAction):
        """Remove an action (icon) from the plugin toolbar
        :param qAction:
        """
        pass

    def addToolBar(self, name):
        """Add toolbar with specified name
        :param name:
        """
        pass

    def mapCanvas(self):
        """Return a pointer to the map canvas"""
        return self.canvas

    def mainWindow(self):
        """Return a pointer to the main window

        In case of QGIS it returns an instance of QgisApp
        """
        pass

    def addDockWidget(self, area, dockwidget):
        """ Add a dock widget to the main window
        :param dockwidget:
        :param area:
        """
        pass
