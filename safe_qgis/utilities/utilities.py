# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
  **IS Utilities implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '29/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import re
import sys
import traceback
import logging
import uuid
import webbrowser

#noinspection PyPackageRequirements
from PyQt4 import QtCore, QtGui, Qt
#noinspection PyPackageRequirements
from PyQt4.QtCore import QCoreApplication, QFile, QUrl

from qgis.core import (
    QGis,
    QgsRasterLayer,
    QgsMapLayer,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsVectorLayer)

from safe_qgis.exceptions import MemoryLayerCreationError

from safe_qgis.safe_interface import (
    ErrorMessage,
    safeTr,
    get_version,
    unique_filename,
    messaging as m,
    styles)

INFO_STYLE = styles.INFO_STYLE

#do not remove this even if it is marked as unused by your IDE
#resources are used by html footer and header the comment will mark it unused
#for pylint
# noinspection PyUnresolvedReferences
from safe_qgis.ui import resources_rc  # pylint: disable=W0611

LOGGER = logging.getLogger('InaSAFE')


def tr(text):
    """We define a tr() alias here since the utilities implementation below
    is not a class and does not inherit from QObject.
    .. note:: see http://tinyurl.com/pyqt-differences

    :param text: String to be translated
    :type text: str

    :returns: Translated version of the given string if available, otherwise
        the original string.
    :rtype: str
    """
    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
    return QCoreApplication.translate('@default', text)


def get_error_message(exception, context=None, suggestion=None):
    """Convert exception into an ErrorMessage containing a stack trace.


    :param exception: Exception object.
    :type exception: Exception

    :param context: Optional context message.
    :type context: str

    :param suggestion: Optional suggestion.
    :type suggestion: str

    .. see also:: https://github.com/AIFDR/inasafe/issues/577

    :returns: An error message with stack trace info suitable for display.
    :rtype: ErrorMessage
    """

    trace = ''.join(traceback.format_tb(sys.exc_info()[2]))

    problem = m.Message(m.Text(exception.__class__.__name__))

    if str(exception) is None or str(exception) == '':
        problem.append = m.Text(tr('No details provided'))
    else:
        problem.append = m.Text(str(exception))

    suggestion = suggestion
    if suggestion is None and hasattr(exception, 'suggestion'):
        suggestion = exception.message

    error_message = ErrorMessage(
        problem,
        detail=context,
        suggestion=suggestion,
        traceback=trace
    )

    args = exception.args
    for arg in args:
        error_message.details.append(arg)

    return error_message


def get_wgs84_resolution(layer):
    """Return resolution of raster layer in EPSG:4326.

    If input layer is already in EPSG:4326, simply return the resolution
    If not, work it out based on EPSG:4326 representations of its extent.

    :param layer: Raster layer
    :type layer: QgsRasterLayer or QgsMapLayer

    :returns: The resolution of the given layer.
    :rtype: float

    """

    msg = tr(
        'Input layer to getWGS84resolution must be a raster layer. '
        'I got: %s' % str(layer.type())[1:-1])
    if not layer.type() == QgsMapLayer.RasterLayer:
        raise RuntimeError(msg)

    if layer.crs().authid() == 'EPSG:4326':
        cell_size = layer.rasterUnitsPerPixelX()

    else:
        # Otherwise, work it out based on EPSG:4326 representations of
        # its extent

        # Reproject extent to EPSG:4326
        geo_crs = QgsCoordinateReferenceSystem()
        geo_crs.createFromSrid(4326)
        transform = QgsCoordinateTransform(layer.crs(), geo_crs)
        extent = layer.extent()
        projected_extent = transform.transformBoundingBox(extent)

        # Estimate cell size
        columns = layer.width()
        geo_width = abs(
            projected_extent.xMaximum() -
            projected_extent.xMinimum())
        cell_size = geo_width / columns

    return cell_size


def html_header():
    """Get a standard html header for wrapping content in.

    :returns: A header containing a web page preamble in html - up to and
        including the body open tag.
    :rtype: str
    """
    file_path = QtCore.QFile(':/plugins/inasafe/header.html')
    if not file_path.open(QtCore.QIODevice.ReadOnly):
        return '----'
    stream = QtCore.QTextStream(file_path)
    header = stream.readAll()
    file_path.close()
    return header


def html_footer():
    """Get a standard html footer for wrapping content in.

    :returns: A header containing a web page closing content in html - up to
        and including the body close tag.
    :rtype: str
    """
    file_path = QtCore.QFile(':/plugins/inasafe/footer.html')
    if not file_path.open(QtCore.QIODevice.ReadOnly):
        return '----'
    stream = QtCore.QTextStream(file_path)
    footer = stream.readAll()
    file_path.close()
    return footer


def qgis_version():
    """Get the version of QGIS.

    :returns: QGIS Version where 10700 represents QGIS 1.7 etc.
    :rtype: int
    """
    version = unicode(QGis.QGIS_VERSION_INT)
    version = int(version)
    return version


def layer_attribute_names(layer, allowed_types, current_keyword=None):
    """Iterates over the layer and returns int or string fields.

    :param layer: A vector layer whose attributes shall be returned.
    :type layer: QgsVectorLayer, QgsMapLayer

    :param allowed_types: List of QVariant that are acceptable for the
        attribute. e.g.: [QtCore.QVariant.Int, QtCore.QVariant.String].
    :type allowed_types: list(QVariant)

    :param current_keyword: The currently stored keyword for the attribute.
    :type current_keyword: str

    :returns: A two-tuple containing all the attribute names of attributes
        that have int or string as field type (first element) and the position
        of the current_keyword in the attribute names list, this is None if
        current_keyword is not in the list of attributes (second element).
    :rtype: tuple(list(str), int)
    """

    if layer.type() == QgsMapLayer.VectorLayer:
        provider = layer.dataProvider()
        provider = provider.fields()
        fields = []
        selected_index = None
        i = 0
        for f in provider:
            # show only int or string fields to be chosen as aggregation
            # attribute other possible would be float
            if f.type() in allowed_types:
                current_field_name = f.name()
                fields.append(current_field_name)
                if current_keyword == current_field_name:
                    selected_index = i
                i += 1
        return fields, selected_index
    else:
        return None, None


def create_memory_layer(layer, new_name=''):
    """Return a memory copy of a layer

    :param layer: QgsVectorLayer that shall be copied to memory.
    :type layer: QgsVectorLayer

    :param new_name: The name of the copied layer.
    :type new_name: str

    :returns: An in-memory copy of a layer.
    :rtype: QgsMapLayer
    """

    if new_name is '':
        new_name = layer.name() + ' TMP'

    if layer.type() == QgsMapLayer.VectorLayer:
        vector_type = layer.geometryType()
        if vector_type == QGis.Point:
            type_string = 'Point'
        elif vector_type == QGis.Line:
            type_string = 'Line'
        elif vector_type == QGis.Polygon:
            type_string = 'Polygon'
        else:
            raise MemoryLayerCreationError('Layer is whether Point nor '
                                           'Line nor Polygon')
    else:
        raise MemoryLayerCreationError('Layer is not a VectorLayer')

    crs = layer.crs().authid().lower()
    uuid_string = str(uuid.uuid4())
    uri = '%s?crs=%s&index=yes&uuid=%s' % (type_string, crs, uuid_string)
    memory_layer = QgsVectorLayer(uri, new_name, 'memory')
    memory_provider = memory_layer.dataProvider()

    provider = layer.dataProvider()
    vector_fields = provider.fields()

    fields = []
    for i in vector_fields:
        fields.append(i)

    memory_provider.addAttributes(fields)

    for ft in provider.getFeatures():
        memory_provider.addFeatures([ft])

    return memory_layer


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


def setup_printer(filename, resolution=300, page_height=297, page_width=210):
    """Create a QPrinter instance defaulted to print to an A4 portrait pdf.

    :param filename: Filename for the pdf print device.
    :type filename: str

    :param resolution: Resolution (in dpi) for the output.
    :type resolution: int

    :param page_height: Height of the page in mm.
    :type page_height: int

    :param page_width: Width of the page in mm.
    :type page_width: int
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
    printer.setFullPage(True)
    printer.setColorMode(QtGui.QPrinter.Color)
    printer.setResolution(resolution)
    return printer


def humanise_seconds(seconds):
    """Utility function to humanise seconds value into e.g. 10 seconds ago.

    The function will try to make a nice phrase of the seconds count
    provided.

    .. note:: Currently seconds that amount to days are not supported.

    :param seconds: Mandatory seconds value e.g. 1100.
    :type seconds: int

    :returns: A humanised version of the seconds count.
    :rtype: str
    """
    days = seconds / (3600 * 24)
    day_modulus = seconds % (3600 * 24)
    hours = day_modulus / 3600
    hour_modulus = day_modulus % 3600
    minutes = hour_modulus / 60

    if seconds < 60:
        return tr('%i seconds' % seconds)
    if seconds < 120:
        return tr('a minute')
    if seconds < 3600:
        return tr('%s minutes' % minutes)
    if seconds < 7200:
        return tr('over an hour')
    if seconds < 86400:
        return tr('%i hours and %i minutes' % (hours, minutes))
    else:
        # If all else fails...
        return tr('%i days, %i hours and %i minutes' % (
            days, hours, minutes))


def impact_attribution(keywords, inasafe_flag=False):
    """Make a little table for attribution of data sources used in impact.

    :param keywords: A keywords dict for an impact layer.
    :type keywords: dict

    :param inasafe_flag: bool - whether to show a little InaSAFE promotional
        text in the attribution output. Defaults to False.

    :returns: An html snippet containing attribution information for the impact
        layer. If no keywords are present or no appropriate keywords are
        present, None is returned.
    :rtype: safe.messaging.Message
    """
    if keywords is None:
        return None

    join_words = ' - %s ' % tr('sourced from')
    hazard_details = tr('Hazard details')
    hazard_title_keywords = 'hazard_title'
    hazard_source_keywords = 'hazard_source'
    exposure_details = tr('Exposure details')
    exposure_title_keywords = 'exposure_title'
    exposure_source_keyword = 'exposure_source'

    if hazard_title_keywords in keywords:
        # We use safe translation infrastructure for this one (rather than Qt)
        hazard_title = safeTr(keywords[hazard_title_keywords])
    else:
        hazard_title = tr('Hazard layer')

    if hazard_source_keywords in keywords:
        # We use safe translation infrastructure for this one (rather than Qt)
        hazard_source = safeTr(keywords[hazard_source_keywords])
    else:
        hazard_source = tr('an unknown source')

    if exposure_title_keywords in keywords:
        exposure_title = keywords[exposure_title_keywords]
    else:
        exposure_title = tr('Exposure layer')

    if exposure_source_keyword in keywords:
        exposure_source = keywords[exposure_source_keyword]
    else:
        exposure_source = tr('an unknown source')

    report = m.Message()
    report.add(m.Heading(hazard_details, **INFO_STYLE))
    report.add(m.Paragraph(
        hazard_title,
        join_words,
        hazard_source))

    report.add(m.Heading(exposure_details, **INFO_STYLE))
    report.add(m.Paragraph(
        exposure_title,
        join_words,
        exposure_source))

    if inasafe_flag:
        report.add(m.Heading(tr('Software notes'), **INFO_STYLE))
        # noinspection PyUnresolvedReferences
        inasafe_phrase = tr(
            'This report was created using InaSAFE version %s. Visit '
            'http://inasafe.org to get your free copy of this software!'
            'InaSAFE has been jointly developed by BNPB, AusAid/AIFDRR & the '
            'World Bank') % (get_version())

        report.add(m.Paragraph(m.Text(inasafe_phrase)))
    return report


def add_ordered_combo_item(combo, text, data=None):
    """Add a combo item ensuring that all items are listed alphabetically.

    Although QComboBox allows you to set an InsertAlphabetically enum
    this only has effect when a user interactively adds combo items to
    an editable combo. This we have this little function to ensure that
    combos are always sorted alphabetically.

    :param combo: Combo box receiving the new item.
    :type combo: QComboBox

    :param text: Display text for the combo.
    :type text: str

    :param data: Optional UserRole data to be associated with the item.
    :type data: QVariant, str
    """
    size = combo.count()
    for myCount in range(0, size):
        item_text = str(combo.itemText(myCount))
        # see if text alphabetically precedes myItemText
        if cmp(str(text).lower(), item_text.lower()) < 0:
            combo.insertItem(myCount, text, data)
            return
        # otherwise just add it to the end
    combo.insertItem(size, text, data)


def is_polygon_layer(layer):
    """Check if a QGIS layer is vector and its geometries are polygons.

    :param layer: A vector layer.
    :type layer: QgsVectorLayer, QgsMapLayer

    :returns: True if the layer contains polygons, otherwise False.
    :rtype: bool

    """
    try:
        return (layer.type() == QgsMapLayer.VectorLayer) and (
            layer.geometryType() == QGis.Polygon)
    except AttributeError:
        return False


def is_point_layer(layer):
    """Check if a QGIS layer is vector and its geometries are points.

    :param layer: A vector layer.
    :type layer: QgsVectorLayer, QgsMapLayer

    :returns: True if the layer contains points, otherwise False.
    :rtype: bool
    """
    try:
        return (layer.type() == QgsMapLayer.VectorLayer) and (
            layer.geometryType() == QGis.Point)
    except AttributeError:
        return False


def is_raster_layer(layer):
    """Check if a QGIS layer is raster.

    :param layer: A layer.
    :type layer: QgsRaster, QgsMapLayer, QgsVectorLayer

    :returns: True if the layer contains polygons, otherwise False.
    :rtype: bool
    """
    try:
        return layer.type() == QgsMapLayer.RasterLayer
    except AttributeError:
        return False


def extent_to_geo_array(extent, source_crs, dest_crs=None):
    """Convert the supplied extent to geographic and return as an array.

    :param extent: Rectangle defining a spatial extent in any CRS.
    :type extent: QgsRectangle

    :param source_crs: Coordinate system used for extent.
    :type source_crs: QgsCoordinateReferenceSystem

    :returns: a list in the form [xmin, ymin, xmax, ymax] where all
            coordinates provided are in Geographic / EPSG:4326.
    :rtype: list

    """

    if dest_crs is None:
        geo_crs = QgsCoordinateReferenceSystem()
        geo_crs.createFromSrid(4326)
    else:
        geo_crs = dest_crs

    transform = QgsCoordinateTransform(source_crs, geo_crs)

    # Get the clip area in the layer's crs
    transformed_extent = transform.transformBoundingBox(extent)

    geo_extent = [
        transformed_extent.xMinimum(),
        transformed_extent.yMinimum(),
        transformed_extent.xMaximum(),
        transformed_extent.yMaximum()]
    return geo_extent


def viewport_geo_array(map_canvas):
    """Obtain the map canvas current extent in EPSG:4326.

    :param map_canvas: A map canvas instance.
    :type map_canvas: QgsMapCanvas

    :returns: A list in the form [xmin, ymin, xmax, ymax] where all
        coordinates provided are in Geographic / EPSG:4326.
    :rtype: list

    .. note:: Delegates to extent_to_geo_array()
    """

    # get the current viewport extent
    rectangle = map_canvas.extent()

    if map_canvas.hasCrsTransformEnabled():
        crs = map_canvas.mapRenderer().destinationCrs()
    else:
        # some code duplication from extentToGeoArray here
        # in favour of clarity of logic...
        crs = QgsCoordinateReferenceSystem()
        crs.createFromSrid(4326)

    return extent_to_geo_array(rectangle, crs)


def read_impact_layer(impact_layer):
    """Helper function to read and validate a safe native spatial layer.

    :param impact_layer: Layer object as provided by InaSAFE engine.
    :type impact_layer: read_layer

    :returns: Valid QGIS layer or None
    :rtype: None, QgsRasterLayer, QgsVectorLayer
    """

    # noinspection PyUnresolvedReferences
    message = tr(
        'Input layer must be a InaSAFE spatial object. '
        'I got %s') % (str(type(impact_layer)))
    if not hasattr(impact_layer, 'is_inasafe_spatial_object'):
        raise Exception(message)
    if not impact_layer.is_inasafe_spatial_object:
        raise Exception(message)

    # Get associated filename and symbolic name
    file_name = impact_layer.get_filename()
    name = impact_layer.get_name()

    qgis_layer = None
    # Read layer
    if impact_layer.is_vector:
        qgis_layer = QgsVectorLayer(file_name, name, 'ogr')
    elif impact_layer.is_raster:
        qgis_layer = QgsRasterLayer(file_name, name)

    # Verify that new qgis layer is valid
    if qgis_layer.isValid():
        return qgis_layer
    else:
        # noinspection PyUnresolvedReferences
        message = tr(
            'Loaded impact layer "%s" is not valid') % file_name
        raise Exception(message)


def map_qrc_to_file(match, destination_directory):
    """Map a qrc:/ path to its correspondent file:/// and create it.

    For example qrc:/plugins/inasafe/ajax-loader.gif
    is converted to file:////home/marco/.qgis2/python/plugins/
    inasafe-master/safe_qgis/resources/img/ajax-loader.gif

    If the qrc asset is non file based (i.e. is compiled in resources_rc
    .pc) then a copy of is extracted to destination_directory.

    :param match: The qrc path to be mapped matched from a regular
        expression such as re.compile('qrc:/plugins/inasafe/([-./ \\w]*)').
    :type match: re.match object

    :param destination_directory: The destination path to copy non file based
        qrc assets.
    :type destination_directory: str

    :returns: File path to the resource or None if the resource could
        not be created.
    :rtype: None, str
    """
    # Resource alias on resources.qrc
    resource_alias = match.group(1)

    # The resource path (will be placed inside destination_directory)
    resource_path = os.path.join(destination_directory, resource_alias)

    # The file (resource) might be here due to a previous copy
    if not os.path.isfile(resource_path):
        # Get resource directory tree
        resource_path_directory = os.path.dirname(resource_path)

        # Create dirs recursively if resource_path_directory does not exist
        if not os.path.exists(resource_path_directory):
            os.makedirs(resource_path_directory)

        # Now, copy from qrc to file system
        source_file = ':/plugins/inasafe/%s' % resource_alias
        # noinspection PyTypeChecker
        copy_successful = QFile.copy(source_file, resource_path)
        if not copy_successful:
            #copy somehow failed
            resource_path = None

    #noinspection PyArgumentList
    return QUrl.fromLocalFile(resource_path).toString()


def open_in_browser(file_path):
    """Open a file in the default web browser.

    :param file_path: Path to the file that should be opened.
    :type file_path: str
    """
    webbrowser.open('file://%s' % file_path)


def html_to_file(html, file_path=None, open_browser=False):
    """Save the html to an html file adapting the paths to the filesystem.

    if a file_path is passed, it is used, if not a unique_filename is
    generated.

    qrc:/..../ paths gets converted to file:///..../

    :param html: the html for the output file.
    :type html: str

    :param file_path: the path for the html output file.
    :type file_path: str

    :param open_browser: if true open the generated html in an external browser
    :type open_browser: bool
    """
    if file_path is None:
        file_path = unique_filename(suffix='.html')

    file_dir = os.path.dirname(file_path)
    reg_exp = re.compile(r'qrc:/plugins/inasafe/([-./ \w]*)')
    html = reg_exp.sub(lambda match: map_qrc_to_file(match, file_dir),
                       html)

    with open(file_path, 'w') as f:
        f.write(html)

    if open_browser:
        open_in_browser(file_path)


def qt_at_least(needed_version, test_version=None):
    """Check if the installed Qt version is greater than the requested

    :param needed_version: minimally needed Qt version in format like 4.8.4
    :type needed_version: str

    :param test_version: Qt version as returned from Qt.QT_VERSION. As in
     0x040100 This is used only for tests
    :type test_version: int

    :returns: True if the installed Qt version is greater than the requested
    :rtype: bool
    """
    major, minor, patch = needed_version.split('.')
    needed_version = '0x0%s0%s0%s' % (major, minor, patch)
    needed_version = int(needed_version, 0)

    installed_version = Qt.QT_VERSION
    if test_version is not None:
        installed_version = test_version

    if needed_version <= installed_version:
        return True
    else:
        return False
