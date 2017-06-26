#!/usr/bin/env python
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
import shutil

__author__ = 'Jannes Engelbrecht'
__date__ = '16/04/15'

import logging
import os
import tempfile

from PyQt4.QtCore import QSettings
from docopt import docopt, DocoptExit
from qgis.core import (
    QgsRasterLayer,
    QgsVectorLayer,
    QgsRectangle,
    QgsMapLayerRegistry,
    QgsCoordinateReferenceSystem)


from safe.test.utilities import get_qgis_app
# make sure this line executes first
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.impact_functions.loader import register_impact_functions
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from safe.report.impact_report import ImpactReport
from safe.storage.utilities import safe_to_qgis_layer
from safe.utilities.gis import qgis_version, validate_geo_array
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.osm_downloader import download

current_dir = os.path.abspath(
    os.path.realpath(os.getcwd()))
usage_dir = os.path.dirname(os.path.abspath(__file__))
usage = r""
usage_file = file(os.path.join(usage_dir, 'usage.txt'))
for delta in usage_file:
    usage += delta
LOGGER = logging.getLogger('InaSAFE')


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
            # Extent is in the format: xmin,ymin,xmax,ymax
            # example: -10.01,10.01,-9.01,11.01
            try:
                self.extent = arguments_['--extent'].split(',')
                # convert to float
                self.extent = [float(n) for n in self.extent]
                if len(self.extent) != 4:
                    raise ValueError()
            except ValueError as e:
                e.message = 'Improperly formatted Extent option'
                raise
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


def get_layer(layer_path, layer_base=None):
    """Get layer from path.

    .. versionadded:: 3.3

    :param layer_path: layer full name
    :type layer_path: str

    :param layer_base: layer base name (title)
    :type layer_base: str

    :returns: Vector or Raster layer depending on input arguments.
    :rtype: QgsVectorLayer, QgsRasterLayer

    :raises: Exception
    """
    layer = None
    try:
        layer_path = join_if_relative(layer_path)
        basename, ext = os.path.splitext(os.path.basename(layer_path))
        if not layer_base:
            layer_base = basename
        if ext == '.shp':
            layer = QgsVectorLayer(
                layer_path, layer_base, 'ogr')
        elif ext in ['.asc', '.tif', '.tiff']:
            layer = QgsRasterLayer(
                layer_path, layer_base)
        else:
            print "Unknown filetype " + layer_base
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
    return get_layer(arguments.hazard, 'Hazard Layer')


def get_exposure(arguments):
    """Get exposure layer.

    .. versionadded:: 3.2

    :param arguments: User inputs.
    :type arguments: CommandLineArguments

    :returns: Vector or Raster layer depending on input arguments.
    :rtype: QgsVectorLayer, QgsRasterLayer

    :raises: Exception
    """
    return get_layer(arguments.exposure, 'Exposure Layer')


def impact_function_setup(
        command_line_arguments, hazard, exposure, aggregation=None):
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

    impact_function.hazard = hazard
    impact_function.exposure = exposure
    impact_function.aggregation = aggregation
    impact_function.clip_hard = False
    impact_function.show_intermediate_layers = False
    impact_function.run_in_thread_flag = False
    impact_function.map_canvas = CANVAS
    # QSetting context
    settings = QSettings()
    # Default extent CRS is EPSG:4326
    impact_function.requested_extent_crs = QgsCoordinateReferenceSystem(
        'EPSG:4326')
    try:
        impact_function.requested_extent = QgsRectangle(
            float(command_line_arguments.extent[0]),
            float(command_line_arguments.extent[1]),
            float(command_line_arguments.extent[2]),
            float(command_line_arguments.extent[3])
        )
        # Use HazardExposureBoundingBox settings
        settings.setValue(
            'inasafe/analysis_extents_mode',
            'HazardExposureBoundingBox')
    except AttributeError:
        print "No extents"
        pass
    return impact_function


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
    impact_function = impact_function_setup(
        command_line_arguments, hazard, exposure, aggregation)
    impact_function.run_analysis()
    impact_layer = impact_function.impact
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
        impact_layer = get_layer(cli_arguments.output_file, 'Impact Layer')
        hazard_layer = get_layer(cli_arguments.hazard, 'Hazard Layer')
        layer_registry = QgsMapLayerRegistry.instance()
        layer_registry.removeAllMapLayers()
        extra_layers = [hazard_layer]
        layer_registry.addMapLayer(impact_layer)
        layer_registry.addMapLayers(extra_layers)
        if cli_arguments.extent:
            report_extent = QgsRectangle(*cli_arguments.extent)
        else:
            report_extent = impact_layer.extent()
        CANVAS.setExtent(report_extent)
        CANVAS.refresh()
        report = ImpactReport(
            IFACE, cli_arguments.report_template, impact_layer,
            extra_layers=extra_layers)
        report.extent = report_extent
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
    :type impact_layer: Vector

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

        # RMN: copy impact data json
        # new feature in InaSAFE 3.4
        source_base_name, _ = os.path.splitext(impact_layer.filename)
        impact_data_json_source = '%s.json' % source_base_name
        if os.path.exists(impact_data_json_source):
            shutil.copy(
                impact_data_json_source,
                '%s.json' % basename)

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
