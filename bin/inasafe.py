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
import shutil
import logging
import os
import tempfile

from qgis.core import (
    QgsRasterLayer,
    QgsVectorLayer,
    QgsRectangle,
    QgsMapLayerRegistry,
    QgsCoordinateReferenceSystem)
from PyQt4.QtCore import QSettings

from docopt import docopt, DocoptExit
from safe.test.utilities import get_qgis_app
# make sure this line executes first
QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from safe.utilities.gis import qgis_version, validate_geo_array
from safe.utilities.osm_downloader import download
from safe.impact_function.impact_function import ImpactFunction
from safe.datastore.folder import Folder
from safe.definitions.constants import PREPARE_SUCCESS, ANALYSIS_SUCCESS
from safe.definitions.utilities import map_report_component
from safe.definitions.reports.components import (
    report_a4_blue,
    standard_impact_report_metadata_pdf)
from safe.report.impact_report import ImpactReport
from safe.report.report_metadata import ReportMetadata

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'

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
        self.output_dir = arguments_['--output-dir']
        self.hazard = arguments_['--hazard']
        self.exposure = arguments_['--exposure']
        self.version = arguments_['--version']
        self.report_template = arguments_['--report-template']
        # optional arguments
        if arguments_['--aggregation']:
            self.aggregation = arguments_['--aggregation']
        else:
            self.aggregation = None
            LOGGER.debug('no aggregation layer specified')

        if arguments_['--extent'] is not None:
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
        if ext in ['.shp', '.geojson', 'gpkg']:
            layer = QgsVectorLayer(layer_path, layer_base, 'ogr')
        elif ext in ['.asc', '.tif', '.tiff']:
            layer = QgsRasterLayer(layer_path, layer_base)
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


def get_aggregation(arguments):
    """Get aggregation layer.

    .. versionadded:: 4.xx

    :param arguments: User inputs.
    :type arguments: CommandLineArguments

    :returns: Vector or Raster layer depending on input arguments.
    :rtype: QgsVectorLayer, QgsRasterLayer

    :raises: Exception
    """
    return get_layer(arguments.aggregation, 'Aggregation Layer')


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
    aggregation = None
    if command_line_arguments.aggregation:
        aggregation = get_layer(command_line_arguments.aggregation)

    # Set up impact function
    impact_function = ImpactFunction()
    impact_function.hazard = hazard
    impact_function.exposure = exposure
    impact_function.aggregation = aggregation
    impact_function.map_canvas = CANVAS
    # Set the datastore
    impact_function.datastore = Folder(command_line_arguments.output_dir)
    impact_function.datastore.default_vector_format = 'geojson'
    # QSetting context
    settings = QSettings()
    crs = settings.value('inasafe/user_extent_crs', '', type=str)
    impact_function.requested_extent_crs = QgsCoordinateReferenceSystem(crs)
    try:
        impact_function.requested_extent = QgsRectangle(
            float(command_line_arguments.extent[0]),
            float(command_line_arguments.extent[1]),
            float(command_line_arguments.extent[2]),
            float(command_line_arguments.extent[3])
        )
    except AttributeError:
        print "No extents"
        pass

    # Prepare impact function
    status, message = impact_function.prepare()
    if status != PREPARE_SUCCESS:
        print message.to_text()
        return status, message, None

    status, message = impact_function.run()
    if status != ANALYSIS_SUCCESS:
        print message.to_text()
        return status, message, None

    return status, message, impact_function


def generate_impact_map_report(cli_arguments, impact_function, iface):
    """Generate impact map pdf from impact function.

    :param impact_function: The impact function used.
    :type impact_function: ImpactFunction

    :param iface: QGIS QGisAppInterface instance.
    :type iface: QGisAppInterface
    """
    hazard_layer = get_layer(cli_arguments.hazard, 'Hazard Layer')
    aggregation_layer = get_layer(
        cli_arguments.aggregation, 'Aggregation Layer')
    layer_registry = QgsMapLayerRegistry.instance()
    layer_registry.addMapLayers(impact_function.outputs)
    layer_registry.addMapLayer(hazard_layer)

    # create impact report instance
    report_metadata = ReportMetadata(
        metadata_dict=map_report_component(report_a4_blue))
    impact_report = ImpactReport(
        iface,
        report_metadata,
        impact_function=impact_function)
    # get the extent of impact layer
    impact_report.qgis_composition_context.extent = \
        impact_function.impact.extent()
    # set the ouput folder
    impact_report.output_folder = cli_arguments.output_dir

    return impact_report.process_components()


def generate_impact_report(cli_arguments, impact_function, iface):
    """Generate the impact report from an impact function.

    :param impact_function: The impact function used.
    :type impact_function: ImpactFunction

    :param iface: QGIS QGisAppInterface instance.
    :type iface: QGisAppInterface

    """
    # create impact report instance
    report_metadata = ReportMetadata(
        metadata_dict=standard_impact_report_metadata_pdf)
    impact_report = ImpactReport(
        iface,
        report_metadata,
        impact_function=impact_function)
    impact_report.output_folder = cli_arguments.output_dir

    return impact_report.process_components()


def build_report(cli_arguments, impact_function):
    """Produces pdf products.

        To be called after output files have been written into
        arguments.output_dir.

    .. versionadded:: 3.2

    :param cli_arguments: User inputs.
    :type cli_arguments: CommandLineArguments

    :raises: Exception
    """
    try:
        LOGGER.info('Building a report')
        # impact_layer = get_layer(cli_arguments.output_file, 'Impact Layer')
        # hazard_layer = get_layer(cli_arguments.hazard, 'Hazard Layer')
        # aggregation_layer = get_layer(
        #     cli_arguments.aggregation, 'Aggregation Layer')
        # layer_registry = QgsMapLayerRegistry.instance()
        # layer_registry.removeAllMapLayers()
        # extra_layers = [hazard_layer]
        # layer_registry.addMapLayer(impact_layer)
        # layer_registry.addMapLayers(extra_layers)
        # CANVAS.setExtent(impact_layer.extent())
        # CANVAS.refresh()
        # # FIXME : To make it work with InaSAFE V4.

        status, message = generate_impact_map_report(
            cli_arguments, impact_function, IFACE)
        if status != ImpactReport.REPORT_GENERATION_SUCCESS:
            raise Exception(message)

        status, message = generate_impact_report(
            cli_arguments, impact_function, IFACE)
        if status != ImpactReport.REPORT_GENERATION_SUCCESS:
            raise Exception(message)

        return status, message
        # LOGGER.debug(os.path.splitext(cli_arguments.output_file)[0] + '.pdf')
        # map_path = report.print_map_to_pdf(
        #     os.path.splitext(cli_arguments.output_file)[0] + '.pdf')
        # print "Impact Map : " + map_path
        # table_path = report.print_impact_table(
        #     os.path.splitext(cli_arguments.output_file)[0] + '_table.pdf')
        # print "Impact Summary Table : " + table_path
        # layer_registry.removeAllMapLayers()

    except Exception as exception:
        print exception.message
        print exception.__doc__
        raise RuntimeError


# def write_results(cli_arguments, impact_layer):
#     """Write the impact_layer in shapefile format.
#
#     .. versionadded:: 3.2
#
#     :param cli_arguments: User inputs.
#     :type cli_arguments: CommandLineArguments
#
#     :param impact_layer: Analysis result used to produce file.
#     :type impact_layer: Vector
#
#     :raises: Exception
#     """
#     try:
#         # RMN: check output filename.
#         # Is it conforming the standard?
#         abs_path = join_if_relative(cli_arguments.output_file)
#         basename, ext = os.path.splitext(abs_path)
#         if not ext:
#             # Extension is empty. Append extension
#             if impact_layer.is_raster:
#                 ext = '.tif'
#             else:
#                 ext = '.shp'
#             abs_path += ext
#
#         # RMN: copy impact data json
#         # new feature in InaSAFE 3.4
#         source_base_name, _ = os.path.splitext(impact_layer.name)
#         impact_data_json_source = '%s.json' % source_base_name
#         if os.path.exists(impact_data_json_source):
#             shutil.copy(
#                 impact_data_json_source,
#                 '%s.json' % basename)
#
#         impact_layer.write_to_file(abs_path)
#
#     except Exception as exception:
#         print exception.message
#         raise RuntimeError(exception.message)


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
        if arguments.version is True:
            print "QGIS VERSION: " + str(qgis_version()).replace('0', '.')
        # user is only interested in doing a download
        elif arguments.download and not arguments.exposure and not \
                arguments.hazard:
            print "downloading ..."
            download_exposure(arguments)

        elif arguments.hazard and arguments.output_file:
            # first do download if necessary
            if not arguments.exposure and arguments.download:
                download_exposure(arguments)

            if arguments.exposure is not None:
                run_impact_function(arguments)
            else:
                print "Download unsuccessful"
        elif arguments.report_template and arguments.output_file:
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
