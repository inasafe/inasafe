#!/usr/bin/python
# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**CLI implementation for inasafe project.**

Contact : jannes@kartoza.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

    Note :
        cli: command line interface
    .. versionadded:: 3.2
"""
from safe.storage.core import read_layer

__author__ = 'Jannes Engelbrecht'
__date__ = '16/04/15'

import os
import logging
import tempfile

from docopt import docopt, DocoptExit
from qgis.core import (
    QgsRasterLayer,
    QgsVectorLayer,
    QgsRectangle,
    QgsMapLayerRegistry,
    QgsCoordinateReferenceSystem)
from PyQt4.QtCore import QSettings

from safe.impact_functions import register_impact_functions
from safe.test.utilities import get_qgis_app
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.gis import qgis_version, validate_geo_array
from safe.report.impact_report import ImpactReport
from safe.utilities.osm_downloader import download
from headless.tasks.utilities import generate_styles
from safe.storage.utilities import safe_to_qgis_layer

current_dir = os.path.abspath(
    os.path.realpath(os.environ['PWD']))
usage_dir = os.environ['InaSAFEQGIS'] + '/bin'
usage = r""
usage_file = file(os.path.join(usage_dir, 'usage.txt'))
for delta in usage_file:
    usage += delta
LOGGER = logging.getLogger('InaSAFE')
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class CommandLineArguments(object):
    """Instance objects class for shell arguments.
        .. versionadded:: 3.2
    """
    def __init__(self, arguments_=None):
        LOGGER.debug('CommandLineArguments')
        if not arguments_:
            return
        self.output_file = arguments_['--output-file']
        self.hazard = arguments_['--hazard']
        self.exposure = arguments_['--exposure']
        self.aggregation = arguments_['--aggregation']
        self.version = arguments_['--version']
        self.show_list = arguments_['--list-functions']
        self.impact_function = arguments_['--impact-function']
        self.report_template = arguments_['--report-template']
        # optional arguments
        if not arguments_['--extent'] is None:
            self.extent = arguments_['--extent'].replace(',', '.').split(':')
        else:
            LOGGER.debug('no extent specified')
        if arguments_['--download']:
            self.download = arguments_['--download']
            self.exposure_layers = arguments_['--layers']
            print self.exposure_layers
        else:
            self.download = False
            self.exposure_layers = None
            LOGGER.debug('no download specified')


def download_exposure(command_line_arguments):
    """Download OSM resources.

        Download layers from OSM within the download extent.

        This function might generate a popup.
        .. versionadded:: 3.2

    :param command_line_arguments:  User inputs.
    :type command_line_arguments: CommandLineArguments
    """
    extent = [
        float(command_line_arguments.extent[0]),
        float(command_line_arguments.extent[1]),
        float(command_line_arguments.extent[2]),
        float(command_line_arguments.extent[3])
        ]

    # make a temporary directory for exposure download
    command_line_arguments.exposure = tempfile.mkdtemp() + '/exposure'
    print 'temp directory: ' + command_line_arguments.exposure
    if validate_geo_array(extent):
        print "Exposure download extent is valid"
    else:
        print "Exposure is invalid"
        print str(extent)

    download(
        command_line_arguments.exposure_layers,
        command_line_arguments.exposure,
        extent)
    if os.path.exists(command_line_arguments.exposure + '.shp'):
        print "download successful"
        command_line_arguments.exposure += '.shp'


def get_impact_function_list(arguments):
    """Returns all available impact function ids.

    .. versionadded:: 3.2

    :returns: List of impact functions.
    :rtype: list
    """
    LOGGER.debug('get IF list')
    manager = ImpactFunctionManager()
    if arguments.hazard and arguments.exposure:
        hazard = get_hazard(arguments)
        exposure = get_exposure(arguments)
        keyword_io = KeywordIO()
        hazard_keyword = keyword_io.read_keywords(hazard)
        exposure_keyword = keyword_io.read_keywords(exposure)
        ifs = manager.filter_by_keywords(hazard_keyword, exposure_keyword)
    else:
        ifs = manager.filter()
    LOGGER.debug(ifs)
    return ifs


def show_impact_function_names(impact_functions):
    """Prints a list of impact functions.

    .. versionadded:: 3.2

    :param impact_functions: A list of impact function ids.
    :type: list of strings.
    """
    manager = ImpactFunctionManager()
    print ""
    print "Available Impact Function:"
    for impact_function in impact_functions:
        print manager.get_function_id(impact_function)
    print ""


# all paths are made to be absolute
def join_if_relative(path_argument):
    """Make path absolute.

    .. versionadded:: 3.2

    :param path_argument: Absolute or relative path to a file.
    :type path_argument: str

    :returns: Absolute path to file.
    :rtype: str
    """
    if not os.path.isabs(path_argument):
        LOGGER.debug('joining path for ' + path_argument)
        return os.path.join(current_dir, path_argument)
    else:
        return os.path.abspath(path_argument)


def get_layer(layer_path):
    """Get layer from path.

    .. versionadded:: 3.2

    :param layer_path: User inputs.
    :type layer_path: CommandLineArguments

    :returns: Vector or Raster layer depending on input arguments.
    :rtype: QgsVectorLayer, QgsRasterLayer

    :raises: Exception
    """
    layer = None
    try:
        if os.path.splitext(layer_path)[1] == '.shp':
            layer_base = join_if_relative(layer_path)
            layer = QgsVectorLayer(
                layer_base, 'cli_vector_hazard', 'ogr')
        elif os.path.splitext(layer_path)[1] in \
                ['.asc', '.tif', '.tiff']:
            layer_base = join_if_relative(layer_path)
            layer = QgsRasterLayer(
                layer_base, 'cli_raster_hazard')
        else:
            print "Unknown filetype " + layer_path
        if layer is not None and layer.isValid():
            print "layer is VALID"
        else:
            print "layer is NOT VALID"
            print "Perhaps run-env-linux.sh /usr"
        return layer
    except Exception as exception:
        print exception.message
        print exception.__doc__


def get_hazard(arguments):
    """Get hazard layer.

    .. versionadded:: 3.2

    :param arguments: User inputs.
    :type arguments: CommandLineArguments

    :returns: Vector or Raster layer depending on input arguments.
    :rtype: QgsVectorLayer, QgsRasterLayer

    :raises: Exception
    """
    return get_layer(arguments.hazard)


def get_exposure(arguments):
    """Get exposure layer.

    .. versionadded:: 3.2

    :param arguments: User inputs.
    :type arguments: CommandLineArguments

    :returns: Vector or Raster layer depending on input arguments.
    :rtype: QgsVectorLayer, QgsRasterLayer

    :raises: Exception
    """
    return get_layer(arguments.exposure)


def analysis_setup(command_line_arguments, hazard, exposure,
                   aggregation=None):
    """Sets up an analysis object.

    .. versionadded:: 3.2

    :param command_line_arguments: User inputs.
    :type command_line_arguments: CommandLineArguments

    :param hazard: Hazard layer
    :type hazard: QgsLayer

    :param exposure: Exposure Layer
    :type exposure: QgsLayer

    :param aggregation: Aggregation Layer
    :type aggregation: QgsLayer

    :raises: Exception
    """
    # IF
    impact_function_manager = ImpactFunctionManager()
    impact_function = impact_function_manager.get(
        command_line_arguments.impact_function)
    keyword_io = KeywordIO()

    try:
        from safe.utilities.analysis import Analysis
    except ImportError as ie:
        LOGGER.debug('Import error for Analysis module')
        print ie.message
        raise ImportError
    analysis = Analysis()
    analysis.impact_function = impact_function
    analysis.hazard = hazard
    analysis.exposure = exposure
    analysis.aggregation = aggregation
    # analysis.hazard_keyword = keyword_io.read_keywords(hazard)
    # analysis.exposure_keyword = keyword_io.read_keywords(exposure)
    analysis.clip_hard = False
    analysis.show_intermediate_layers = False
    analysis.run_in_thread_flag = False
    analysis.map_canvas = CANVAS
    # QSetting context
    settings = QSettings()
    crs = settings.value('inasafe/analysis_extent_crs', '', type=str)
    analysis.user_extent_crs = QgsCoordinateReferenceSystem(crs)
    try:
        analysis.user_extent = QgsRectangle(
            float(command_line_arguments.extent[0]),
            float(command_line_arguments.extent[1]),
            float(command_line_arguments.extent[2]),
            float(command_line_arguments.extent[3])
        )
    except AttributeError:
        print "No extents"
        pass
    analysis.setup_analysis()
    return analysis


def run_impact_function(command_line_arguments):
    """Runs an analysis and delegates producing pdf and .shp results.

        An impact layer object is created and used to write a shapefile.
        The shapefile path is given by user and used by build_report
        function to read from.

    .. versionadded:: 3.2

    :param command_line_arguments: User inputs.
    :type command_line_arguments: CommandLineArguments
    """
    hazard = get_hazard(command_line_arguments)
    exposure = get_exposure(command_line_arguments)
    aggregation = get_layer(command_line_arguments.aggregation)
    analysis = analysis_setup(
        command_line_arguments, hazard, exposure, aggregation)
    analysis.run_analysis()
    impact_layer = analysis.impact_layer
    qgis_impact_layer = safe_to_qgis_layer(impact_layer)
    write_results(command_line_arguments, impact_layer)

    return impact_layer


def build_report(cli_arguments):
    """Produces pdf products.

        To be called after shapefile has been written into
        arguments.output_file.

    .. versionadded:: 3.2

    :param cli_arguments: User inputs.
    :type cli_arguments: CommandLineArguments

    :raises: Exception
    """
    try:
        LOGGER.info('Building a report')
        basename, ext = os.path.splitext(cli_arguments.output_file)
        if ext == '.shp':
            impact_layer = QgsVectorLayer(
                cli_arguments.output_file, 'Impact Layer', 'ogr')
        elif ext == '.tif':
            impact_layer = QgsRasterLayer(
                cli_arguments.output_file, 'Impact Layer')
        layer_registry = QgsMapLayerRegistry.instance()
        layer_registry.removeAllMapLayers()
        layer_registry.addMapLayer(impact_layer)
        CANVAS.setExtent(impact_layer.extent())
        CANVAS.refresh()
        report = ImpactReport(
            IFACE, cli_arguments.report_template, impact_layer)
        LOGGER.debug(os.path.splitext(cli_arguments.output_file)[0] + '.pdf')
        map_path = report.print_map_to_pdf(
            os.path.splitext(cli_arguments.output_file)[0] + '.pdf')
        print "Impact Map : " + map_path
        table_path = report.print_impact_table(
            os.path.splitext(cli_arguments.output_file)[0] + '_table.pdf')
        print "Impact Summary Table : " + table_path
        layer_registry.removeAllMapLayers()

    except Exception as exception:
        print exception.message
        print exception.__doc__
        raise RuntimeError


def write_results(cli_arguments, impact_layer):
    """Write the impact_layer in shapefile format.

    .. versionadded:: 3.2

    :param cli_arguments: User inputs.
    :type cli_arguments: CommandLineArguments

    :param impact_layer: Analysis result used to produce file.
    :type impact_layer: QgsVectorLayer

    :raises: Exception
    """
    try:
        # RMN: check output filename.
        # Is it conforming the standard?
        abs_path = join_if_relative(cli_arguments.output_file)
        basename, ext = os.path.splitext(abs_path)
        if not ext:
            # Extension is empty. Append extension
            if impact_layer.is_raster:
                ext = '.tif'
            else:
                ext = '.shp'
            abs_path += ext
        impact_layer.write_to_file(abs_path)
    except Exception as exception:
        print exception.message
        raise RuntimeError(exception.message)


if __name__ == '__main__':
    print "inasafe"
    print ""
    try:
        # Parse arguments, use usage.txt as syntax definition.
        LOGGER.debug('Parse argument')
        shell_arguments = docopt(usage)
        LOGGER.debug('Parse done')
    except DocoptExit as exc:
        print exc.message

    try:
        arguments = CommandLineArguments(shell_arguments)

        LOGGER.debug(shell_arguments)
        if arguments.show_list is True:
            # setup functions
            register_impact_functions()
            show_impact_function_names(get_impact_function_list(arguments))
        elif arguments.version is True:
            print "QGIS VERSION: " + str(qgis_version()).replace('0', '.')
        # user is only interested in doing a download
        elif arguments.download is True and\
                arguments.exposure is None and\
                arguments.hazard is None:
            print "downloading ..."
            download_exposure(arguments)

        elif (arguments.hazard is not None) and\
                (arguments.output_file is not None):
            # first do download if necessary
            if arguments.exposure is None and arguments.download is True:
                download_exposure(arguments)

            if arguments.exposure is not None:
                run_impact_function(arguments)
            else:
                print "Download unsuccessful"
        elif (arguments.report_template is not None and
                arguments.output_file is not None):
            print "Generating report"
            build_report(arguments)
        else:
            print "Argument combination not recognised"
    except Exception as excp:
        print excp.message
        print excp.__doc__


print " "

# INSTALL on Ubuntu with:
# chmod ug+x inasafe
# sudo ln -s `pwd`/inasafe  /usr/bin
