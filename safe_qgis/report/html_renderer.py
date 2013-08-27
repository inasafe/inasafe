# coding=utf-8
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
from safe_qgis.utilities.utilities import (
    html_header,
    html_footer,
    mm_to_points,
    dpi_to_meters,
    setup_printer,
    impact_attribution)
from safe_qgis.safe_interface import unique_filename, temp_dir
LOGGER = logging.getLogger('InaSAFE')


class HtmlRenderer():
    """A class for creating a map."""
    def __init__(self, page_dpi):
        """Constructor for the Map class.

        :param page_dpi: Desired resolution for image rendered outputs.
        :type page_dpi: int, float
        """
        LOGGER.debug('InaSAFE HtmlRenderer class initialised')

        self.pageDpi = float(page_dpi)
        # Need to keep state here for loadCompleted signals
        self.webView = None
        self.htmlLoadedFlag = False

    def tr(self, string):
        """We implement this since we do not inherit QObject.

        :param string: String for translation.
        :type string: str

        :returns: Translated version of string.
        :rtype: str
        """
        # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
        return QtCore.QCoreApplication.translate('HtmlRenderer', string)

    def html_to_image(self, html, width_mm):
        """Render some HTML to a pixmap.

        :param html: HTML to be rendered. It is assumed that the html
              is a snippet only, containing no body element - a standard
              header and footer will be appended.
        :type html: str

        :param width_mm: width of the table in mm - will be converted to
              points based on the resolution of our page.
        :type width_mm: int

        :returns: An image containing the rendered html.
        :rtype: QImage
        """
        LOGGER.debug('InaSAFE Map renderHtmlToImage called')

        myWidthPx = mm_to_points(width_mm, self.pageDpi)
        self.load_and_wait(html_snippet=html)
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
        myImage.setDotsPerMeterX(dpi_to_meters(self.pageDpi))
        myImage.setDotsPerMeterY(dpi_to_meters(self.pageDpi))
        # Only works in Qt4.8
        #myImage.fill(QtGui.qRgb(255, 255, 255))
        # Works in older Qt4 versions
        myImage.fill(255 + 255 * 256 + 255 * 256 * 256)
        myPainter = QtGui.QPainter(myImage)
        myFrame.render(myPainter)
        myPainter.end()
        myImage.save('/tmp/test.png')
        return myImage

    def to_pdf(self, html, filename=None):
        """Render an html snippet into the printer, paginating as needed.

        :param html: A string containing an html snippet. It will have a
            header and footer appended to it in order to make it a valid
            html document. The header will also apply the bootstrap theme
            to the document.
        :type html: str

        :param filename: String containing a pdf file path that the
            output will be written to. If no file name is given we will make
            up one for you - nice eh?
        :type filename: str

        :returns: The file path of the output pdf (which is the same as the
            filename parameter if it was specified).
        :rtype: str
        """
        LOGGER.info('InaSAFE Map printToPdf called')
        if filename is None:
            myHtmlPdfPath = unique_filename(
                prefix='table', suffix='.pdf', dir=temp_dir('work'))
        else:
            # We need to cast to python string in case we receive a QString
            myHtmlPdfPath = str(filename)

        self.printer = setup_printer(myHtmlPdfPath)
        self.load_and_wait(html_snippet=html)
        self.webView.print_(self.printer)

        return myHtmlPdfPath

    def load_and_wait(self, html_path=None, html_snippet=None):
        """Load some html to a web view and wait till it is done.

        :param html_path: The path to an html document (file). This option
            is mutually exclusive to html_snippet.
        :type html_path: str

        :param html_snippet: Some html you want rendered in the form of a
            string. It will be 'topped and tailed' with with standard header
            and footer. This option is mutually exclusive to html_path.
        :type html_snippet: str
        """
        if html_snippet:
            myHeader = html_header()
            myFooter = html_footer()
            myHtml = myHeader + html_snippet + myFooter
        else:
            myFile = file(html_path, 'rt')
            myHtml = myFile.readlines()
            myFile.close()

        self.webView = QtWebKit.QWebView()
        myFrame = self.webView.page().mainFrame()
        myFrame.setScrollBarPolicy(QtCore.Qt.Vertical,
                                   QtCore.Qt.ScrollBarAlwaysOff)
        myFrame.setScrollBarPolicy(QtCore.Qt.Horizontal,
                                   QtCore.Qt.ScrollBarAlwaysOff)

        # noinspection PyUnresolvedReferences
        self.webView.loadFinished.connect(self.html_loaded_slot)
        self.webView.setHtml(myHtml)
        self.htmlLoadedFlag = False
        myTimeOut = 20
        myCounter = 0
        mySleepPeriod = 1
        while not self.htmlLoadedFlag and myCounter < myTimeOut:
            # Block until the event loop is done printing the page
            myCounter += 1
            time.sleep(mySleepPeriod)
            # noinspection PyArgumentList
            QtCore.QCoreApplication.processEvents()

        if not self.htmlLoadedFlag:
            LOGGER.error('Failed to load html')

    def html_loaded_slot(self):
        """Slot called when the page is loaded.
        """
        self.htmlLoadedFlag = True
        LOGGER.debug('htmlLoadedSlot slot called')
        # noinspection PyUnresolvedReferences
        self.webView.loadFinished.disconnect(self.html_loaded_slot)

    def print_impact_table(self, keywords, filename=None):
        """High level table generator to print layer keywords.

        It gets the summary and impact table from a QgsMapLayer's keywords and
        renders to pdf, returning the resulting PDF file path.


        :param keywords: Impact layer keywords (required).
        :type keywords: dict

        :param filename: Name of the pdf file to create.
        :type filename: str

        Returns:
            str: Path to generated pdf file.

        Raises:
            None

        """
        myFilePath = filename

        if filename is None:
            myFilePath = unique_filename(suffix='.pdf', dir=temp_dir())

        try:
            mySummaryTable = keywords['impact_summary']
        except KeyError:
            mySummaryTable = None

        myAttributionTable = impact_attribution(keywords)

        try:
            myFullTable = keywords['impact_table']
        except KeyError:
            myFullTable = None

        try:
            myAggregationTable = keywords['postprocessing_report']
        except KeyError:
            myAggregationTable = None

        myHtml = ''
        if mySummaryTable != myFullTable and mySummaryTable is not None:
            myHtml = '<h2>%s</h2>' % self.tr('Summary Table')
            myHtml += mySummaryTable
            if myAggregationTable is not None:
                myHtml += myAggregationTable
            if myAttributionTable is not None:
                myHtml += myAttributionTable.to_html()
            myHtml += '<h2>%s</h2>' % self.tr('Detailed Table')
            myHtml += myFullTable
        else:
            if myAggregationTable is not None:
                myHtml = myAggregationTable
            if myFullTable is not None:
                myHtml += myFullTable
            if myAttributionTable is not None:
                myHtml += myAttributionTable.to_html()

        # myNewFilePath should be the same as myFilePath
        myNewFilePath = self.to_pdf(myHtml, myFilePath)
        return myNewFilePath
