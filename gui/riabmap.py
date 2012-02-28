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
        myPageHeight = 297  # height in mm
        myPageWidth = 210  # width in mm
        myDpi = 300
        myMargin = 10  # margin in mm
        myRenderer = self.iface.mapCanvas().mapRenderer()
        myComposition = QgsComposition(myRenderer)
        myComposition.setPlotStyle(QgsComposition.Print)
        myComposition.setPaperSize(myPageWidth, myPageHeight)
        myComposition.setPrintResolution(myDpi)
        myWidth = myComposition.paperWidth()
        myHeight = myComposition.paperWidth()
        #
        # Create a printer device (we are 'printing' to a pdf
        #
        myPrinter = QtGui.QPrinter()
        myPrinter.setOutputFormat(QtGui.QPrinter.PdfFormat)
        myPrinter.setOutputFileName(theFilename)
        myPrinter.setPaperSize(QtCore.QSizeF(myWidth,
                                             myHeight),
                                             QtGui.QPrinter.Millimeter)
        myPrinter.setFullPage(True)
        myPrinter.setColorMode(QtGui.QPrinter.Color)
        myResolution = myComposition.printResolution()
        myPrinter.setResolution(myResolution)
        #
        # Add a picture - riab logo on right
        #
        myPicture1 = QgsComposerPicture(myComposition)
        myPicture1.setPictureFile(':/plugins/riab/icon.png')
        myPicture1.setItemPosition(myWidth - 30, 1, 30, 30)
        myPicture1.setFrame(False)
        myComposition.addItem(myPicture1)
        #
        # Add a picture - bnpb logo on left
        #
        myPicture2 = QgsComposerPicture(myComposition)
        myPicture2.setPictureFile(':/plugins/riab/bnpb_logo.png')
        myPicture2.setItemPosition(1, 1, 30, 30)
        myPicture2.setFrame(False)
        myComposition.addItem(myPicture2)
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
        myWidth = (myPicture1.boundingRect().width() +
                   myPicture2.boundingRect().width() +
                   10)
        myHeight = myFontMetrics.height() + 10
        myLabel.setItemPosition(myPicture1.boundingRect().width() + 5,
                                1,
                                myWidth,
                                myHeight)
        myLabel.setFrame(False)
        myComposition.addItem(myLabel)
        #
        # Add a map to the composition
        #
        x, y = 0, 0
        w, h = myComposition.paperWidth(), myComposition.paperHeight()
        myComposerMap = QgsComposerMap(myComposition, x, y, w, h)
        myComposition.addItem(myComposerMap)
        #
        # Render the composition to our pdf printer
        #
        myPainter = QtGui.QPainter(myPrinter)
        myPaperRectMM = myPrinter.pageRect(QtGui.QPrinter.Millimeter)
        myPaperRectPx = myPrinter.pageRect(QtGui.QPrinter.DevicePixel)
        myComposition.render(myPainter, myPaperRectPx, myPaperRectMM)
        myPainter.end()
