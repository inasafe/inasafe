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
__version__ = '0.5.1'
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import time
import logging

from PyQt4 import QtCore, QtGui, QtWebKit
from safe_qgis.utilities import (htmlHeader,
                                 htmlFooter,
                                 mmToPoints,
                                 setupPrinter)
from safe_interface import unique_filename, temp_dir
from safe_qgis.exceptions import KeywordNotFoundException
from keyword_io import KeywordIO
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

    def renderHtmlToPixmap(self, theHtml, theWidthMM):
        """Render some HTML to a pixmap.

        Args:
            * theHtml - HTML to be rendered. It is assumed that the html
              is a snippet only, containing no body element - a standard
              header and footer will be appended.
            * theWidthMM- width of the table in mm - will be converted to
              points based on the resolution of our page.
        Returns:
            QPixmap
        Raises:
            Any exceptions raised by the InaSAFE library will be propagated.
        """
        LOGGER.debug('InaSAFE Map renderHtmlToPixmap called')
        # Using 150dpi as the baseline, work out a standard text size
        # multiplier so that page renders equally well at different print
        # resolutions.
        myBaselineDpi = 150
        myFactor = float(self.pageDpi) / myBaselineDpi
        myWidthPx = mmToPoints(theWidthMM, self.pageDpi)
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

    def experimentalHtmlToPrinter(self, theHtml, theOutputFilePath=None):
        """Render an html snippet into the printer, paginating as needed.

        In this one we try to print directly without needing sig/slot
        completion notification.

        Currently this doesnt work in tests (which is the whole point).

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
        LOGGER.info('InaSAFE Map printToPdf called')
        myHeader = htmlHeader()
        myFooter = htmlFooter()
        myHtml = myHeader + theHtml + myFooter
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

        self.printer = setupPrinter(theOutputFilePath)
        self.webView.print_(self.printer)

        return  # self.htmlPrintedFlag

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
        myHeader = htmlHeader()
        myFooter = htmlFooter()
        myHtml = myHeader + theHtml + myFooter

        self.printer = setupPrinter(myHtmlPdfPath)

        self.webView = QtWebKit.QWebView()
        self.webView.loadFinished.connect(self.readToPrintSlot)

        self.htmlPrintedFlag = False

        # This is just for debugging
        myHtmlFilePath = os.path.splitext(myHtmlPdfPath)[0] + '.html'
        myHtmlFile = file(myHtmlFilePath, 'wt')
        myHtmlFile.write(myHtml)
        myHtmlFile.close()
        LOGGER.debug('Html written to: %s' % myHtmlFilePath)

        self.webView.load(QtCore.QUrl(myHtmlFilePath))
        #self.webView.setHtml(myHtml)
        QtCore.QCoreApplication.processEvents()

        myTimeOut = 20
        myCounter = 0
        mySleepPeriod = 1
        while not self.htmlPrintedFlag and myCounter < myTimeOut:
            # Block until the event loop is done printing the page
            myCounter += 1
            time.sleep(mySleepPeriod)
            QtCore.QCoreApplication.processEvents()

        if not self.htmlPrintedFlag:
            # Bodge for if signal isnt received after 10s - doesrnt really work
            # TODO get web page printing in unit test context where there is
            # no event loop....TS
            LOGGER.error('Failed to make a print out, forcing')
            #self.readToPrintSlot()
        return myHtmlPdfPath

    def readToPrintSlot(self):
        """Slot called when the page is loaded and ready for printing.

        Args: None
        Returns: None
        Raises: None
        """
        self.htmlPrintedFlag = True
        LOGGER.debug('readToPrintSlot slot called')
        self.webView.print_(self.printer)
        QtCore.QObject.disconnect(self.webView,
                                  QtCore.SIGNAL("loadFinished(bool)"),
                                  self.readToPrintSlot)

    def printImpactTable(self, theLayer, theFilename=None):
        """High level table generator to print layer keywords.

        It gets the summary and impact table from a QgsMapLayer's keywords and
        renders to pdf, returning the resulting PDF file path.

        Args:
            * theLayer: QgsMapLayer instance (required)

        """
        myFilePath = theFilename
        if theFilename is None:
            myFilePath = unique_filename(suffix='.pdf', dir=temp_dir())

        myKeywordIO = KeywordIO()
        try:
            mySummaryTable = myKeywordIO.readKeywords(
                theLayer, 'impact_summary')
        except KeywordNotFoundException:
            mySummaryTable = None

        try:
            myFullTable = myKeywordIO.readKeywords(
                theLayer, 'impact_table')
        except KeywordNotFoundException:
            myFullTable = None

        try:
            myAggregationTable = myKeywordIO.readKeywords(
                theLayer, 'postprocessing_report')
        except KeywordNotFoundException:
            myAggregationTable = None

        myHtml = ''
        if mySummaryTable != myFullTable and mySummaryTable is not None:
            myHtml = '<h2>%s</h2>' % self.tr('Summary Table')
            myHtml += mySummaryTable
            if myAggregationTable is not None:
                myHtml += myAggregationTable
            myHtml += '<h2>%s</h2>' % self.tr('Detailed Table')
            myHtml += myFullTable
        else:
            if myAggregationTable is not None:
                myHtml = myAggregationTable
            if myFullTable is not None:
                myHtml += myFullTable

        # myNewFilePath should be the same as myFilePath
        myNewFilePath = self.printToPdf(myHtml, myFilePath)
        return myNewFilePath
