"""
Disaster risk assessment tool developed by AusAid - **QGIS plugin implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or 
     (at your option) any later version.

.. note:: This source code was copied from the 'postgis viewer' application with 
     original authors:
     Copyright (c) 2010 by Ivan Mincik, ivan.mincik@gista.sk
     Copyright (c) 2011 German Carrillo, geotux_tuxman@linuxmail.org

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.0.1'
__date__ = '10/01/2011'
__copyright__ = 'Copyright (c) 2010 by Ivan Mincik, ivan.mincik@gista.sk and '
__copyright__ += 'Copyright (c) 2011 German Carrillo, geotux_tuxman@linuxmail.org'

class QgisInterface(QObject):
    """ Class to expose qgis objects and functionalities to plugins. This class is 
        here for enabling us to run unit tests only, and so most methods are 
        simply stubs."""
    def __init__(self, myApp, canvas):
        """ Constructor """
        QObject.__init__(self)
        self.myApp = myApp
        self.canvas = canvas
        self.toolBarPlugins = None

    def zoomFull(self):
        """ Zoom to the map full extent """
        self.canvas.zoomToFullExtent()

    def zoomToPrevious(self):
        """ Zoom to previous view extent """
        self.canvas.zoomToPreviousExtent()

    def zoomToNext(self):
        """ Zoom to next view extent """
        self.canvas.zoomToNextExtent()

    def addVectorLayer(self, vectorLayerPath, baseName, providerKey):
        """ Add a vector layer """
        layer = QgsVectorLayer(vectorLayerPath, baseName, providerKey)
        return self.myApp.addLayer(layer)

    def addRasterLayer(self, rasterLayerPath, baseName):
        """ Add a raster layer given a raster layer file name """
        layer = QgsRasterLayer(rasterLayerPath, baseName)
        return self.myApp.addLayer(layer)

    def activeLayer(self):
        """ Get pointer to the active layer (layer selected in the legend) """
        if self.myApp.activeLayer():
            return self.myApp.activeLayer().layer()
        return None

    def addToolBarIcon(self, qAction):
        """ Add an icon to the plugins toolbar """
        if not self.toolBarPlugins:
            self.toolBarPlugins = self.addToolBar("Plugins")
        self.toolBarPlugins.addAction(qAction)

    def removeToolBarIcon(self, qAction):
        """ Remove an action (icon) from the plugin toolbar """
        if not self.toolBarPlugins:
            self.toolBarPlugins = self.addToolBar("Plugins")
        self.toolBarPlugins.removeAction(qAction)

    def addToolBar(self, name):
        """ Add toolbar with specified name """
        toolBar = self.myApp.addToolBar(name)
        toolBar.setObjectName(name)
        return toolBar

    def mapCanvas(self):
        """ Return a pointer to the map canvas """
        return self.canvas

    def mainWindow(self):
        """ Return a pointer to the main window (instance of QgisApp in case of QGIS) """
        return self.myApp

    def addDockWidget(self, area, dockwidget):
        """ Add a dock widget to the main window """
        self.myApp.addDockWidget(area, dockwidget)
        dockwidget.show()

        # refresh the map canvas
        self.canvas.refresh()


class Plugins():
    """ Class to manage plugins (Read and load existing plugins) """
    def __init__(self, myApp, canvas, host, port, dbname, user, passwd):
        self.qgisInterface = QgisInterface(myApp, canvas)
        self.myApp = myApp
        self.plugins = []
        self.pluginsDirName = 'plugins'
        regExpString = '^def +classFactory\(.*iface.*(\):)$' # To find the classFactory line

        """ Validate that it is a plugins folder and loads them into the application """
        dir_plugins = os.path.join(os.path.dirname(__file__), self.pluginsDirName)

        if os.path.exists(dir_plugins):
            for root, dirs, files in os.walk(dir_plugins):
                bPlugIn = False

                if not dir_plugins == root:
                    if '__init__.py' in files:
                        for line in fileinput.input(os.path.join(root, '__init__.py')):
                            linea = line.strip()
                            if re.match(regExpString, linea):
                                bPlugIn = True
                                break
                        fileinput.close()

                        if bPlugIn:
                            plugin_name = os.path.basename(root)
                            f, filename, description = imp.find_module(plugin_name, [ dir_plugins ])

                            try:
                                package = imp.load_module(plugin_name, f, filename, description)
                                self.plugins.append(package.classFactory(self.qgisInterface, host, port, dbname, user, passwd))
                            except Exception, e:
                                print 'E: Plugin ' + plugin_name + ' could not be loaded. ERROR!:', e
                            else:
                                self.plugins[ -1 ].initGui()
                                print 'I: Plugin ' + plugin_name + ' successfully loaded!'
        else:
            print "Plugins folder not found."
