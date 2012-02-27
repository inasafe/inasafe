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

from qgis.core import (QgsComposition,
                       QgsComposerMap,
                       QgsComposerLabel,
                       QgsComposerPicture)

from PyQt4 import QtCore, QtGui
# Don't remove this even if it is flagged as unused by your ide
# it is needed for qrc:/ url resolution. See Qt Resources docs.
import resources


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

    def makePdf(self, theFilename):
        """Method to createa  nice little pdf map.

        Args:
            theFilename - a string containing a filename path with .pdf
            extension
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
        myFontSize = 24
        myFontWeight = 1
        myItalicsFlag = False
        myFont = QtGui.QFont('verdana',
                             myFontSize,
                             myFontWeight,
                             myItalicsFlag)
        myLabel = QgsComposerLabel(myComposition)
        myLabel.setFont(myFont)
        myHeading = 'Risk in a Box'
        myLabel.setText(myHeading)
        myLabel.adjustSizeToText()
        myFontMetrics = QtGui.QFontMetrics(myFont)
        myWidth = myFontMetrics.width(myHeading)
        myLabel.setItemPosition(int((w / 2) - int(myWidth / 2)), 1, 30, 30)
        myLabel.setFrame(False)
        myComposition.addItem(myLabel)
        #
        # Add a picture - riab logo on right
        #
        myPicture = QgsComposerPicture(myComposition)
        myPicture.setPictureFile(':/plugins/riab/icon.png')
        myPicture.setItemPosition(w - 30, 1, 30, 30)
        myPicture.setFrame(False)
        myComposition.addItem(myPicture)\
        #
        # Add a picture - bnpb logo on left
        #
        myPicture = QgsComposerPicture(myComposition)
        myPicture.setPictureFile(':/plugins/riab/bnpb_logo.png')
        myPicture.setItemPosition(1, 1, 30, 30)
        myPicture.setFrame(False)
        myComposition.addItem(myPicture)
        #
        # Print composition to pdf
        #
        myPrinter = QtGui.QPrinter()
        myPrinter.setOutputFormat(QtGui.QPrinter.PdfFormat)
        myPrinter.setOutputFileName(theFilename)
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
