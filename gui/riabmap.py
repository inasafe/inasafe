"""
Disaster risk assessment tool developed by AusAid -
  **RIAB map making module.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.2.0'
__date__ = '10/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

from qgis.core import (QgsComposition, QgsComposerMap, QgsComposerLabel)

from PyQt4 import QtCore, QtGui


class RiabMap():
    """A class for creating a map."""
    def __init__(self, theIface):
        """Constructor for the RiabMap class.
        Args:
            theIface - reference to the QGIS iface object
        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        self.iface = theIface

    def makePdf(self):
        """Method to createa  nice little pdf map.

        Args:
            None
        Returns:
            None
        Raises:
            Any exceptions raised by the RIAB library will be propogated.
        """
        myRenderer = self.iface.mapCanvas().mapRenderer()
        myComposition = QgsComposition(myRenderer)
        myComposition.setPlotStyle(QgsComposition.Print)
        #
        # Add a map to the composition
        #
        x, y = 0, 0
        w, h = myComposition.paperWidth(), myComposition.paperHeight()
        myComposerMap = QgsComposerMap(myComposition, x, y, w, h)
        myComposition.addItem(myComposerMap)
        #
        # Add a label
        #
        myLabel = QgsComposerLabel(myComposition)
        myLabel.setText("Risk in a Box")
        myLabel.adjustSizeToText()
        myComposition.addItem(myLabel)
        #
        # Print composition to pdf
        #
        myPrinter = QtGui.QPrinter()
        myPrinter.setOutputFormat(QtGui.QPrinter.PdfFormat)
        myPrinter.setOutputFileName("/tmp/out.pdf")
        myPrinter.setPaperSize(QtCore.QSizeF(myComposition.paperWidth(),
                                             myComposition.paperHeight()),
                                             QtGui.QPrinter.Millimeter)
        myPrinter.setFullPage(True)
        myPrinter.setColorMode(QtGui.QPrinter.Color)
        myPrinter.setResolution(myComposition.printResolution())

        myPainter = QtGui.QPainter(myPrinter)
        myPaperRectMM = myPrinter.pageRect(QtGui.QPrinter.Millimeter)
        myPaperRectPx = myPrinter.pageRect(QtGui.QPrinter.DevicePixel)
        myComposition.render(myPainter, myPaperRectPx, myPaperRectMM)
        myPainter.end()
