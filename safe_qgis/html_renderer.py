"""
InaSAFE Disaster risk assessment tool developed by AusAid -
  **InaSAFE map making module.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@linfiniti.com'
__version__ = '0.5.0'
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import time
import logging

from PyQt4 import QtCore, QtGui, QtWebKit
from safe_qgis.utilities import htmlHeader, htmlFooter, mmToPoints, pointsToMM
LOGGER = logging.getLogger('InaSAFE')

class HtmlRenderer():
    """A class for creating a map."""
    def __init__(self, thePageDpi):
        """Constructor for the Map class.

        Args:
            None
        Returns:
            None
        Raises:
            Any exceptions will be propagated.
        """
        LOGGER.debug('InaSAFE HtmlRenderer class initialised')

        self.pageDpi = thePageDpi
        # Need to keep state here for loadCompleted signals
        self.webView = None
        self.htmlPrintedFlag = False
        self.webView = None

    def renderHtmlToPixmap(self, theHtml, theWidthMM):
        """Render some HTML to a pixmap.

        Args:
            * theHtml - HTML to be rendered. It is assumed that the html
              is a snippet only, containing no body element - a standard
              header and footer will be appended.
            * theWidthMM- width of the table in mm - will be converted to
              points based on the resolution of our page.
        Returns:
            A QPixmap
        Raises:
            Any exceptions raised by the InaSAFE library will be propagated.
        """
        LOGGER.debug('InaSAFE Map renderHtmlToPixmap called')
        # Using 150dpi as the baseline, work out a standard text size
        # multiplier so that page renders equally well at different print
        # resolutions.
        myBaselineDpi = 150
        myFactor = float(self.pageDpi) / myBaselineDpi
        myWidthPx = mmToPoints(theWidthMM)
        myPage = QtWebKit.QWebPage()
        myFrame = myPage.mainFrame()
        myFrame.setTextSizeMultiplier(myFactor)
        myFrame.setScrollBarPolicy(QtCore.Qt.Vertical,
                                   QtCore.Qt.ScrollBarAlwaysOff)
        myFrame.setScrollBarPolicy(QtCore.Qt.Horizontal,
                                   QtCore.Qt.ScrollBarAlwaysOff)

        myHeader = htmlHeader()
        myFooter = htmlFooter()
        myHtml = myHeader + theHtml + myFooter
        myFrame.setHtml(myHtml)

        mySize = myFrame.contentsSize()
        mySize.setWidth(myWidthPx)
        myPage.setViewportSize(mySize)

        myPixmap = QtGui.QPixmap(mySize)
        myPixmap.fill(QtGui.QColor(255, 255, 255))
        myPainter = QtGui.QPainter(myPixmap)
        myFrame.render(myPainter)
        myPainter.end()
        return myPixmap

    def htmlToPrinter(self, theHtml, theOutputFilePath=None):
        """Render an html snippet into the printer, paginating as needed.

        Args:
            theHtml: str A string containing an html snippet. It will have a
                header and footer appended to it in order to make it a valid
                html document. The header will also apply the bootstrap theme
                to the document.
        Returns:
            None

        Raises:
            None
        """
        LOGGER.info('InaSAFE Map htmlToPrinter called')
        myHeader = htmlHeader()
        myFooter = htmlFooter()
        myHtml = myHeader + theHtml + myFooter
        del self.webView
        self.webView = QtWebKit.QWebView()
        myPage = self.webView.page()
        myFrame = myPage.mainFrame()

        myFrame.setScrollBarPolicy(QtCore.Qt.Vertical,
                                   QtCore.Qt.ScrollBarAlwaysOff)
        myFrame.setScrollBarPolicy(QtCore.Qt.Horizontal,
                                   QtCore.Qt.ScrollBarAlwaysOff)

        myHeader = htmlHeader()
        myFooter = htmlFooter()
        myHtml = myHeader + theHtml + myFooter
        myFrame.setHtml(myHtml)

        self.setupPrinter(theOutputFilePath)
        self.webView.print_(self.printer)
        #self.webView.loadFinished.connect(self.printWebPage)

        #QtCore.QObject.connect(self.webView,
        #                       QtCore.SIGNAL("loadFinished(bool)"),
        #                       self.printWebPage())
        #self.htmlPrintedFlag = False

        #myFilePath = unique_filename(suffix='.html', dir=temp_dir())
        #LOGGER.debug('Html written to %s' % myFilePath)
        #myFile = file(myFilePath, 'wt')
        #myFile.writelines(myHtml)
        #myFile.close()
        #self.webView.load(QtCore.QUrl(myFilePath))
        #self.webView.setHtml(myHtml)
        #myTimeOut = 10
        #myCounter = 0
        #mySleepPeriod = 1
        #while not self.htmlPrintedFlag and myCounter < myTimeOut:
        #    # Block until the event loop is done printing the page
        #    myCounter += 1
        #    time.sleep(mySleepPeriod)
        #if not self.htmlPrintedFlag:
        #    LOGGER.error('Failed to make a print out')
        return #self.htmlPrintedFlag

    def printWebPage(self):
        """Slot called when the page is loaded and ready for printing.

        Args: None
        Returns: None
        Raises: None
        """
        self.htmlPrintedFlag = True
        LOGGER.debug('printWebPage slot called')
        self.webView.print_(self.printer)
        QtCore.QObject.disconnect(self.webView,
                                  QtCore.SIGNAL("loadFinished(bool)"),
                                  self.printWebPage)
