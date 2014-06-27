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

# noinspection PyPackageRequirements
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

        self.page_dpi = float(page_dpi)
        # Need to keep state here for loadCompleted signals
        self.web_view = None
        self.html_loaded_flag = False
        self.printer = None

    # noinspection PyMethodMayBeStatic
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

        width_px = mm_to_points(width_mm, self.page_dpi)
        self.load_and_wait(html_snippet=html)
        frame = self.web_view.page().mainFrame()

        # Using 150dpi as the baseline, work out a standard text size
        # multiplier so that page renders equally well at different print
        # resolutions.
        #myBaselineDpi = 150
        #myFactor = float(self.page_dpi) / myBaselineDpi
        #myFrame.setTextSizeMultiplier(myFactor)

        size = frame.contentsSize()
        size.setWidth(width_px)
        self.web_view.page().setViewportSize(size)

        image = QtGui.QImage(size, QtGui.QImage.Format_RGB32)
        image.setDotsPerMeterX(dpi_to_meters(self.page_dpi))
        image.setDotsPerMeterY(dpi_to_meters(self.page_dpi))
        # Only works in Qt4.8
        #image.fill(QtGui.qRgb(255, 255, 255))
        # Works in older Qt4 versions
        image.fill(255 + 255 * 256 + 255 * 256 * 256)
        painter = QtGui.QPainter(image)
        frame.render(painter)
        painter.end()

        return image

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
            html_pdf_path = unique_filename(
                prefix='table', suffix='.pdf', dir=temp_dir())
        else:
            # We need to cast to python string in case we receive a QString
            html_pdf_path = str(filename)

        self.printer = setup_printer(html_pdf_path)
        self.load_and_wait(html_snippet=html)
        self.web_view.print_(self.printer)

        return html_pdf_path

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
            header = html_header()
            footer = html_footer()
            html = header + html_snippet + footer
        else:
            with open(html_path) as html_file:
                html = html_file.read()

        self.web_view = QtWebKit.QWebView()
        frame = self.web_view.page().mainFrame()
        frame.setScrollBarPolicy(
            QtCore.Qt.Vertical, QtCore.Qt.ScrollBarAlwaysOff)
        frame.setScrollBarPolicy(
            QtCore.Qt.Horizontal, QtCore.Qt.ScrollBarAlwaysOff)

        # noinspection PyUnresolvedReferences
        self.html_loaded_flag = False
        self.web_view.loadFinished.connect(self.html_loaded_slot)
        self.web_view.setHtml(html)
        my_counter = 0
        my_sleep_period = 0.1  # sec
        my_timeout = 20  # sec
        while not self.html_loaded_flag and my_counter < my_timeout:
            # Block until the event loop is done printing the page
            my_counter += my_sleep_period
            time.sleep(my_sleep_period)
            # noinspection PyArgumentList
            QtCore.QCoreApplication.processEvents()

        if not self.html_loaded_flag:
            LOGGER.error('Failed to load html')

        # noinspection PyUnresolvedReferences
        self.web_view.loadFinished.disconnect(self.html_loaded_slot)

    def html_loaded_slot(self, ok):
        """Slot called when the page is loaded.

        :param ok: Flag indicating if the html is loaded.
        :type ok: bool
        """
        self.html_loaded_flag = ok
        LOGGER.debug('htmlLoadedSlot slot called')
        # noinspection PyUnresolvedReferences

    def print_impact_table(self, keywords, filename=None):
        """High level table generator to print layer keywords.

        It gets the summary and impact table from a QgsMapLayer's keywords and
        renders to pdf, returning the resulting PDF file path.

        :param keywords: Impact layer keywords (required).
        :type keywords: dict

        :param filename: Name of the pdf file to create.
        :type filename: str

        :return: Path to generated pdf file.
        :rtype: str

        :raises: None
        """
        file_path = filename

        if filename is None:
            file_path = unique_filename(suffix='.pdf', dir=temp_dir())

        try:
            summary_table = keywords['impact_summary']
        except KeyError:
            summary_table = None

        attribution_table = impact_attribution(keywords)

        try:
            full_table = keywords['impact_table']
        except KeyError:
            full_table = None

        try:
            aggregation_table = keywords['postprocessing_report']
        except KeyError:
            aggregation_table = None

        # The order of the report:
        # 1. Summary table
        # 2. Aggregation table
        # 3. Attribution table

        # (AG) We will not use impact_table as most of the IF use that as:
        # impact_table = impact_summary + some information intended to be
        # shown on screen (see FloodOsmBuilding)
        # Unless the impact_summary is None, we will use impact_table as the
        # alternative
        html = ''
        if summary_table is None:
            html += '<h2>%s</h2>' % self.tr('Detailed Table')
            html += full_table
        else:
            html = '<h2>%s</h2>' % self.tr('Summary Table')
            html += summary_table

        if aggregation_table is not None:
            html += aggregation_table

        if attribution_table is not None:
            html += attribution_table.to_html()

        # new_file_path should be the same as file_path
        new_file_path = self.to_pdf(html, file_path)
        return new_file_path
