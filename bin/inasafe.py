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
import logging
import os

from qgis.core import (
    QgsRasterLayer,
    QgsVectorLayer,
    QgsRectangle,
    QgsMapLayerRegistry,
    QgsCoordinateReferenceSystem)

from docopt import docopt, DocoptExit

from safe.test.utilities import get_qgis_app
from safe.common.version import get_version
from safe.utilities.gis import qgis_version, validate_geo_array
from safe.utilities.osm_downloader import download
from safe.utilities.settings import setting
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

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

if 'InaSAFEQGIS' in os.environ:
    usage_dir = os.path.join(os.environ['InaSAFEQGIS'], 'bin')
else:
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

        self.hazard = arguments_['--hazard']
        self.exposure = arguments_['--exposure']
        self.output_dir = arguments_['--output-dir']
        self.version = arguments_['--version']

        # optional arguments
        if arguments_['--aggregation']:
            self.aggregation = arguments_['--aggregation']
        else:
            self.aggregation = None
            msg = 'No aggregation layer specified..'
            LOGGER.debug(msg)

        if arguments_['--extent'] is not None:
            self.extent = arguments_['--extent'].replace(',', '.').split(':')
        else:
            self.extent = None
            msg = 'No extent specified....'
            LOGGER.debug(msg)

        if arguments_['--download']:
            self.download = arguments_['--download']
            self.exposure_type = arguments_['--feature-type']
        else:
            self.download = False
            self.exposure_type = None
            LOGGER.debug('no download specified')


def download_exposure(cli_arguments):
    """Download OSM resources.

        Download layers from OSM within the download extent.

        This function might generate a popup.
        .. versionadded:: 3.2

    :param cli_arguments:  User inputs.
    :type cli_arguments: CommandLineArguments
    """
    extent = [
        float(cli_arguments.extent[0]),
        float(cli_arguments.extent[1]),
        float(cli_arguments.extent[2]),
        float(cli_arguments.extent[3])
        ]

    if not os.path.exists(cli_arguments.output_dir):
        os.makedirs(cli_arguments.output_dir)

    cli_arguments.exposure = os.path.join(
        cli_arguments.output_dir, cli_arguments.exposure_type)
    if validate_geo_array(extent):
        print 'Exposure download extent is valid'
        download(
            cli_arguments.exposure_type,
            cli_arguments.exposure,
            extent)
        if os.path.exists(cli_arguments.exposure + '.shp'):
            cli_arguments.exposure += '.shp'
            print 'Download successful'
            print 'Output: ' + cli_arguments.exposure
    else:
        print 'Exposure download extent is invalid'
        print str(extent)


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
        if ext in ['.shp', '.geojson', '.gpkg']:
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


def run_impact_function(cli_arguments):
    """Runs an analysis and delegates producing pdf and .geojson output layers.

    .. versionadded:: 3.2

    :param cli_arguments: User inputs.
    :type cli_arguments: CommandLineArguments
    """
    hazard = get_layer(cli_arguments.hazard, 'Hazard Layer')
    exposure = get_layer(cli_arguments.exposure, 'Exposure Layer')
    aggregation = None
    if cli_arguments.aggregation:
        aggregation = get_layer(cli_arguments.aggregation)

    # Set up impact function
    impact_function = ImpactFunction()
    impact_function.hazard = hazard
    impact_function.exposure = exposure
    impact_function.aggregation = aggregation
    # Set the datastore
    impact_function.datastore = Folder(cli_arguments.output_dir)
    impact_function.datastore.default_vector_format = 'geojson'

    # Set the extent
    if cli_arguments.extent:
        crs = setting('user_extent_crs', None, str)
        if crs:
            impact_function.requested_extent_crs = \
                QgsCoordinateReferenceSystem(crs)
        try:
            impact_function.requested_extent = QgsRectangle(
                float(cli_arguments.extent[0]),
                float(cli_arguments.extent[1]),
                float(cli_arguments.extent[2]),
                float(cli_arguments.extent[3])
            )
        except AttributeError:
            print "Extent is not valid..."
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

    :param cli_arguments: User inputs.
    :type cli_arguments: CommandLineArguments

    :param impact_function: The impact function used.
    :type impact_function: ImpactFunction

    :param iface: QGIS QGisAppInterface instance.
    :type iface: QGisAppInterface

    .. versionadded:: 4.0
    """
    hazard_layer = get_layer(cli_arguments.hazard, 'Hazard Layer')
    aggregation_layer = get_layer(
        cli_arguments.aggregation, 'Aggregation Layer')
    layer_registry = QgsMapLayerRegistry.instance()
    layer_registry.addMapLayers(impact_function.outputs)
    layer_registry.addMapLayers([hazard_layer, aggregation_layer])

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

    :param cli_arguments: User inputs.
    :type cli_arguments: CommandLineArguments

    :param impact_function: The impact function used.
    :type impact_function: ImpactFunction

    :param iface: QGIS QGisAppInterface instance.
    :type iface: QGisAppInterface

    .. versionadded:: 4.0

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

    :param impact_function: The impact function used.
    :type impact_function: ImpactFunction

    :raises: Exception
    """
    LOGGER.info('Building a report')
    status, message = generate_impact_map_report(
        cli_arguments, impact_function, IFACE)
    if status != ImpactReport.REPORT_GENERATION_SUCCESS:
        raise Exception(message.to_text())

    status, message = generate_impact_report(
        cli_arguments, impact_function, IFACE)
    if status != ImpactReport.REPORT_GENERATION_SUCCESS:
        raise Exception(message.to_text())

    return status, message

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
        args = CommandLineArguments(shell_arguments)
        LOGGER.debug(shell_arguments)
        if args.version is True:
            print "QGIS VERSION: " + str(qgis_version()).replace('0', '.')
            print "InaSAFE VERSION: " + get_version()

        # user is only interested in doing a download
        elif args.download and not args.hazard:
            print "Downloading ..."
            download_exposure(args)

        elif args.hazard and args.output_dir:
            # first do download if user asks to
            if args.download and not args.exposure:
                if args.extent:
                    download_exposure(args)
                else:
                    print 'Extent must be set when --download specified...'

            if args.exposure is not None:
                status, msg, impact_function = run_impact_function(args)
                if status != ANALYSIS_SUCCESS:
                    print 'Failed running impact function...'
                    print msg
                else:
                    print 'Running impact function is succesfull...'
                    print 'Building reports...'
                    status, msg = build_report(args, impact_function)
                    if status != ImpactReport.REPORT_GENERATION_SUCCESS:
                        print 'Failed building reports...'
                        print msg
            else:
                print "Download unsuccessful"
        else:
            print "Argument combination not recognised"
    except Exception as excp:
        print excp.message
        print excp.__doc__


print " "
