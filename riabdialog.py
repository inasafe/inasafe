"""
/***************************************************************************
 RiabDialog
                                 A QGIS plugin
 Disaster risk assessment tool developed by AusAid
                             -------------------
        begin                : 2012-01-09
        copyright            : (C) 2012 by Australia Indonesia Facility for Disaster Reduction
        email                : ole.moller.nielsen@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.gui import *
from ui_riab import Ui_Riab
DEBUG=False
if DEBUG:
    import sys 
    #todo: softcode this path!
    sys.path.append("/home/timlinux/.eclipse/org.eclipse.platform_3.7.0_155965261/plugins/org.python.pydev.debug_2.2.4.2011110216/pysrc/")
    from pydevd import *

class RiabDialog(QtGui.QDialog):

    def __init__(self,iface):
        QtGui.QDialog.__init__(self)
        # Save reference to the QGIS interface
        self.iface = iface
        # Set up the user interface from Designer.
        self.ui = Ui_Riab()
        self.ui.setupUi(self)
        self.getLayers()

    def getLayers(self):
        for i in range(len(self.iface.mapCanvas().layers())):
            myLayer = self.iface.mapCanvas().layer(i)
            if myLayer.type() == myLayer.VectorLayer and myLayer.isUsingRendererV2():
                #if myLayer.geometryType() == QGis.Polygon:
                self.ui.lstLayers.addItem(myLayer.name()) #,myLayer.id())
        return 
