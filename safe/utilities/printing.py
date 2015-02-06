# coding=utf-8
"""Printing related utilities."""
# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=W0611
from PyQt4 import QtGui, QtCore

from safe.utilities.utilities import LOGGER


def points_to_mm(points, dpi):
    """Convert measurement in points to one in mm.

    :param points: A distance in points.
    :type points: int

    :param dpi: Dots per inch to use for the calculation (based on in the
        print / display medium).
    :type dpi: int

    :returns: points converted value as mm.
    :rtype: int
    """
    inch_as_mm = 25.4
    mm = (float(points) / dpi) * inch_as_mm
    return mm


def dpi_to_meters(dpi):
    """Convert dots per inch (dpi) to dots per meters.

    :param dpi: Dots per inch in the print / display medium.
    :type dpi: int, float

    :returns: dpi converted value.
    :rtype: int
    """
    inch_as_mm = 25.4
    inches_per_m = 1000.0 / inch_as_mm
    dots_per_m = inches_per_m * dpi
    return dots_per_m


def setup_printer(
        filename,
        resolution=300,
        page_height=297,
        page_width=210,
        page_margin=None):
    """Create a QPrinter instance defaulted to print to an A4 portrait pdf.

    :param filename: Filename for the pdf print device.
    :type filename: str

    :param resolution: Resolution (in dpi) for the output.
    :type resolution: int

    :param page_height: Height of the page in mm.
    :type page_height: int

    :param page_width: Width of the page in mm.
    :type page_width: int

    :param page_margin: Page margin in mm in form [left, top, right, bottom].
    :type page_margin: list
    """
    #
    # Create a printer device (we are 'printing' to a pdf
    #
    LOGGER.debug('InaSAFE Map setupPrinter called')
    printer = QtGui.QPrinter()
    printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
    printer.setOutputFileName(filename)
    printer.setPaperSize(
        QtCore.QSizeF(page_width, page_height),
        QtGui.QPrinter.Millimeter)
    printer.setColorMode(QtGui.QPrinter.Color)
    printer.setResolution(resolution)

    if page_margin is None:
        page_margin = [10, 10, 10, 10]
    printer.setPageMargins(
        page_margin[0],
        page_margin[1],
        page_margin[2],
        page_margin[3],
        QtGui.QPrinter.Millimeter)
    return printer


def mm_to_points(mm, dpi):
    """Convert measurement in mm to one in points.

    :param mm: A distance in millimeters.
    :type mm: int, float

    :returns: mm converted value as points.
    :rtype: int, float

    :param dpi: Dots per inch to use for the calculation (based on in the
        print / display medium).
    :type dpi: int, float

    """
    inch_as_mm = 25.4
    points = (mm * dpi) / inch_as_mm
    return points
