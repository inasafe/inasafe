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
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import time
import logging

from PyQt4 import QtCore, QtGui, QtWebKit
from safe_qgis.utilities import (htmlHeader,
                                 htmlFooter,
                                 mmToPoints,
                                 dpiToMeters,
                                 setupPrinter,
                                 impactLayerAttribution)
from safe_interface import unique_filename, temp_dir
LOGGER = logging.getLogger('InaSAFE')


class HtmlRenderer():
    """A class for creating a map."""
    def __init__(self, thePageDpi):
        """Constructor for the Map class.

        Args:
            thePageDpi: int - desired resolution for image rendered outputs.
        Returns:
            None
        Raises:
            Any exceptions will be propagated.
        """
        LOGGER.debug('InaSAFE HtmlRenderer class initialised')

        self.pageDpi = thePageDpi
        # Need to keep state here for loadCompleted signals
        self.webView = None
        self.htmlLoadedFlag = False

    def tr(self, theString):
        """We implement this since we do not inherit QObject.

        Args:
           theString - string for translation.
        Returns:
           Translated version of theString.
        Raises:
           no exceptions explicitly raised.
        """
        return QtCore.QCoreApplication.translate('HtmlRenderer', theString)

    def renderHtmlToImage(self, theHtml, theWidthMM):
        """Render some HTML to a pixmap.

        Args:
            * theHtml - HTML to be rendered. It is assumed that the html
              is a snippet only, containing no body element - a standard
              header and footer will be appended.
            * theWidthMM- width of the table in mm - will be converted to
              points based on the resolution of our page.
        Returns:
            QImage
        Raises:
            Any exceptions raised by the InaSAFE library will be propagated.
        """
        LOGGER.debug('InaSAFE Map renderHtmlToImage called')

        myWidthPx = mmToPoints(theWidthMM, self.pageDpi)
        self.loadAndWait(theHtmlSnippet=theHtml)
        myFrame = self.webView.page().mainFrame()

        # Using 150dpi as the baseline, work out a standard text size
        # multiplier so that page renders equally well at different print
        # resolutions.
        #myBaselineDpi = 150
        #myFactor = float(self.pageDpi) / myBaselineDpi
        #myFrame.setTextSizeMultiplier(myFactor)

        mySize = myFrame.contentsSize()
        mySize.setWidth(myWidthPx)
        self.webView.page().setViewportSize(mySize)

        myImage = QtGui.QImage(mySize, QtGui.QImage.Format_RGB32)
        myImage.setDotsPerMeterX(dpiToMeters(self.pageDpi))
        myImage.setDotsPerMeterY(dpiToMeters(self.pageDpi))
        # Only works in Qt4.8
        #myImage.fill(QtGui.qRgb(255, 255, 255))
        # Works in older Qt4 versions
        myImage.fill(255 + 255 * 256 + 255 * 256 * 256)
        myPainter = QtGui.QPainter(myImage)
        myFrame.render(myPainter)
        myPainter.end()
        myImage.save('/tmp/test.png')
        return myImage

    def printToPdf(self, theHtml, theFilename=None):
        """Render an html snippet into the printer, paginating as needed.

        Args:
            * theHtml: str A string containing an html snippet. It will have a
                header and footer appended to it in order to make it a valid
                html document. The header will also apply the bootstrap theme
                to the document.
            * theFilename: str String containing a pdf file path that the
                output will be written to.
        Returns:
            str: The file path of the output pdf (which is the same as the
                theFilename parameter if it was specified.

        Raises:
            None
        """
        LOGGER.info('InaSAFE Map printToPdf called')
        if theFilename is None:
            myHtmlPdfPath = unique_filename(prefix='table',
                                           suffix='.pdf',
                                           dir=temp_dir('work'))
        else:
            # We need to cast to python string in case we receive a QString
            myHtmlPdfPath = str(theFilename)

        self.printer = setupPrinter(myHtmlPdfPath)
        self.loadAndWait(theHtmlSnippet=theHtml)
        self.webView.print_(self.printer)

        return myHtmlPdfPath

    def loadAndWait(self, theHtmlPath=None, theHtmlSnippet=None):
        """Load some html to a web view and wait till it is done."""
        if theHtmlSnippet:
            myHeader = htmlHeader()
            myFooter = htmlFooter()
            myHtml = myHeader + theHtmlSnippet + myFooter
        else:
            myFile = file(theHtmlPath, 'rt')
            myHtml = myFile.readlines()
            myFile.close()

        self.webView = QtWebKit.QWebView()
        myFrame = self.webView.page().mainFrame()
        myFrame.setScrollBarPolicy(QtCore.Qt.Vertical,
                                   QtCore.Qt.ScrollBarAlwaysOff)
        myFrame.setScrollBarPolicy(QtCore.Qt.Horizontal,
                                   QtCore.Qt.ScrollBarAlwaysOff)

        self.webView.loadFinished.connect(self.htmlLoadedSlot)
        self.webView.setHtml(myHtml)
        self.htmlLoadedFlag = False
        myTimeOut = 20
        myCounter = 0
        mySleepPeriod = 1
        while not self.htmlLoadedFlag and myCounter < myTimeOut:
            # Block until the event loop is done printing the page
            myCounter += 1
            time.sleep(mySleepPeriod)
            QtCore.QCoreApplication.processEvents()

        if not self.htmlLoadedFlag:
            LOGGER.error('Failed to load html')

    def htmlLoadedSlot(self):
        """Slot called when the page is loaded.

        Args: None
        Returns: None
        Raises: None
        """
        self.htmlLoadedFlag = True
        LOGGER.debug('htmlLoadedSlot slot called')
        QtCore.QObject.disconnect(self.webView,
                                  QtCore.SIGNAL("loadFinished(bool)"),
                                  self.htmlLoadedSlot)

    def printImpactTable(self, theKeywords, theFilename=None):
        """High level table generator to print layer keywords.

        It gets the summary and impact table from a QgsMapLayer's keywords and
        renders to pdf, returning the resulting PDF file path.

        Args:
            theKeywords: dic containing impact layer keywords (required)

        Returns:
            str: Path to generated pdf file.

        Raises:
            None

        """
        myFilePath = theFilename

        if theFilename is None:
            myFilePath = unique_filename(suffix='.pdf', dir=temp_dir())

        try:
            mySummaryTable = theKeywords['impact_summary']
        except KeyError:
            mySummaryTable = None

        myAttributionTable = impactLayerAttribution(theKeywords)

        try:
            myFullTable = theKeywords['impact_table']
        except KeyError:
            myFullTable = None

        try:
            myAggregationTable = theKeywords['postprocessing_report']
        except KeyError:
            myAggregationTable = None

        myHtml = ''
        if mySummaryTable != myFullTable and mySummaryTable is not None:
            myHtml = '<h2>%s</h2>' % self.tr('Summary Table')
            myHtml += mySummaryTable
            if myAggregationTable is not None:
                myHtml += myAggregationTable
            if myAttributionTable is not None:
                myHtml += myAttributionTable
            myHtml += '<h2>%s</h2>' % self.tr('Detailed Table')
            myHtml += myFullTable
        else:
            if myAggregationTable is not None:
                myHtml = myAggregationTable
            if myFullTable is not None:
                myHtml += myFullTable
            if myAttributionTable is not None:
                myHtml += myAttributionTable

        # myNewFilePath should be the same as myFilePath
        myNewFilePath = self.printToPdf(myHtml, myFilePath)
        return myNewFilePath
