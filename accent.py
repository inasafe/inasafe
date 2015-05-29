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

"""

__author__ = 'Jannes Engelbrecht'
__date__ = '16/04/15'
import docopt
from safe.impact_functions.registry import Registry
from safe.impact_functions import register_impact_functions
from safe.test.utilities import get_qgis_app
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from qgis.core import (
    QgsRasterLayer,
    QgsVectorLayer,
    QgsMapLayerRegistry)
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.gis import qgis_version
import os
from safe.report.impact_report import ImpactReport
import logging


# arguments/options
output_file = None
vector_hazard = None
raster_hazard = None
vector_exposure = None
raster_exposure = None
version = None
show_list = None
extent = None
report_template = None

default_cli_dir = os.path.abspath(
    os.path.realpath(os.path.dirname(__file__)))
usage_dir = os.environ['InaSAFEQGIS']
usage = r""
usage_file = file(os.path.join(usage_dir, 'usage.txt'))
for delta in usage_file:
    usage += delta

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

LOGGER = logging.getLogger('InaSAFE')


class CliArgs(object):
    """Instance objects class for shell arguments.
    """
    def __init__(self, _arguments_):
        try:
            self.output_file = _arguments_['--output-file']
        except Exception as e:
            LOGGER.debug(e.message)
        try:
            self.hazard = _arguments_['--hazard']
        except Exception as e:
            LOGGER.debug(e.message)
        try:
            self.exposure = _arguments_['--exposure']
        except Exception as e:
            LOGGER.debug(e.message)
        try:
            self.version = _arguments_['--version']
        except Exception as e:
            LOGGER.debug(e.message)
        try:
            self.show_list = _arguments_['--list-functions']
        except Exception as e:
            LOGGER.debug(e.message)
        try:
            self.impact_function = _arguments_['--impact-function']
        except Exception as e:
            LOGGER.debug(e.message)
        try:
            self.extent = _arguments_['--extent'].split(':')
            LOGGER.debug(extent)
        except Exception as e:
            LOGGER.debug(e.message)
        try:
            self.report_template = _arguments_['--report-template']
            LOGGER.debug(report_template)
        except Exception as e:
            LOGGER.debug(e.message)


def get_ifunction_list():
    """Returns all available impact function ids.

    :returns: List of impact functions.
    :rtype: list
    """
    LOGGER.debug('get IF list')
    registry = Registry()
    LOGGER.debug(registry.impact_functions)
    return registry.impact_functions


def show_names(ifs):
    """Prints a list of strings.

    :param ifs: A list of impact function ids.
    :type: list of strings.
    """
    for impact_function in ifs:
        print impact_function.__name__


# all paths are made to be absolute
def join_if_relative(path_argument):
    """Make path absolute.

    :param path_argument: Absolute or relative path to a file.
    :type path_argument: str

    :returns: Absolute path to file.
    :rtype: str
    """
    if not os.path.isabs(path_argument):
        LOGGER.debug('joining path for ' + path_argument)
        return os.path.join(default_cli_dir, path_argument)
    else:
        return os.path.abspath(path_argument)


def get_hazard(cli_arguments):
    """Get hazard layer.

    :param cli_arguments: User inputs.
    :type cli_arguments: CliArgs

    :returns: Vector or Raster layer depending on input arguments.
    :rtype: QgsVectorLayer, QgsRasterLayer

    :raises: Exception
    """
    try:
        if os.path.splitext(cli_arguments.hazard)[1] == '.shp':
            hazard_base = join_if_relative(cli_arguments.hazard)
            qhazard = QgsVectorLayer(
                hazard_base, 'cli_vector_hazard', 'ogr')
        elif os.path.splitext(cli_arguments.hazard)[1] == '.asc':
            hazard_base = join_if_relative(cli_arguments.hazard)
            qhazard = QgsRasterLayer(
                hazard_base, 'cli_raster_hazard')
        if not qhazard.isValid():
            print "hazard layer is NOT VALID"
            print "Perhaps run-env-linux.sh /usr"
        else:
            print "hazard layer is VALID"
        return qhazard
    except Exception as exc:
        print exc.message
        print exc.__doc__


def get_exposure(cli_arguments):
    """Get exposure layer.

    :param cli_arguments: User inputs.
    :type cli_arguments: CliArgs

    :returns: Vector or Raster layer depending on input arguments.
    :rtype: QgsVectorLayer, QgsRasterLayer

    :raises: Exception
    """
    try:
        if os.path.splitext(cli_arguments.exposure)[1] == '.shp':
            exposure_base = join_if_relative(cli_arguments.exposure)
            LOGGER.debug(exposure_base)
            qexposure = QgsVectorLayer(exposure_base, 'cli_vector', 'ogr')
        elif os.path.splitext(cli_arguments.exposure)[1] == '.asc':
            exposure_base = join_if_relative(cli_arguments.exposure)
            LOGGER.debug(exposure_base)
            qexposure = QgsRasterLayer(exposure_base, 'cli_raster')
        else:
            print 'Error : Exposure layer'

        if not qexposure.isValid():
            print "exposure layer not valid"
            print "Perhaps run-env-linux.sh /usr"
        else:
            print "exposure layer is VALID!!"
        return qexposure
    except Exception as exc:
        print exc.message
        print exc.__doc__


def run_if(cli_arguments):
    """Runs an analysis and delegates producing pdf and .shp results.

        An impact layer object is created and used to write a shapefile.
        The shapefile path is given by user and used by build_report
        function to read from.

    :param cli_arguments: User inputs.
    :type cli_arguments: CliArgs

    :raises: Exception
    """
    try:
        qhazard = get_hazard(cli_arguments)
        qexposure = get_exposure(cli_arguments)
        # IF
        impact_function_manager = ImpactFunctionManager()
        impact_function = impact_function_manager.get(arguments.impact_function)
        keyword_io = KeywordIO()
    except Exception as exc:
        print exc.__doc__
        print exc.message
    try:
        from safe.utilities.analysis import Analysis
    except ImportError as ie:
        LOGGER.debug('Import error for Analysis module')
        print ie.message
        return None, None, None, None
    # Layers
    try:
        analysis = Analysis()
        analysis.hazard_layer = qhazard
        analysis.exposure_layer = qexposure
        analysis.hazard_keyword = keyword_io.read_keywords(qhazard)
        analysis.exposure_keyword = keyword_io.read_keywords(qexposure)
        analysis.clip_hard = False
        analysis.show_intermediate_layers = False
        analysis.run_in_thread_flag = False
        analysis.map_canvas = CANVAS
        # WIP
        # analysis.user_extent_crs(qexposure.extent)
        # analysis.user_extent(extent[0], extent[1], extent[2], extent[3])
        analysis.impact_function = impact_function
        analysis.setup_analysis()
        analysis.run_analysis()
        LOGGER.debug("end analysis :)")
        impact_layer = analysis.get_impact_layer()
        write_results(cli_arguments, impact_layer)
        build_report(cli_arguments)
    except Exception as exc:
        print exc.message
        print exc.__doc__


def build_report(cli_arguments):
    """Produces pdf products.

        To be called after shapefile has been written into
        arguments.output_file.

    :param cli_arguments: User inputs.
    :type cli_arguments: CliArgs

    :raises: Exception
    """
    try:
        impact_layer = QgsVectorLayer(cli_arguments.output_file, 'cli_impact', 'ogr')
        LOGGER.debug(impact_layer.__doc__)
        layer_registry = QgsMapLayerRegistry.instance()
        layer_registry.removeAllMapLayers()
        layer_registry.addMapLayer(impact_layer)
        CANVAS.setExtent(impact_layer.extent())
        CANVAS.refresh()
        report = ImpactReport(IFACE, cli_arguments.report_template, impact_layer)
        LOGGER.debug(os.path.splitext(cli_arguments.output_file)[0] + '.pdf')
        map_path = report.print_map_to_pdf(
            os.path.splitext(cli_arguments.output_file)[0] + '.pdf')
        print "Impact Map : " + map_path
        table_path = report.print_impact_table(
            os.path.splitext(cli_arguments.output_file)[0] + '_table.pdf')
        print "Impact Summary Table : " + table_path
        layer_registry.removeAllMapLayers()

    except Exception as exc:
        print "HERE"
        print exc.message
        print exc.__doc__


def write_results(cli_arguments, impact_layer):
    """Write the impact_layer in shapefile format.

    :param cli_arguments: User inputs.
    :type cli_arguments: CliArgs

    :param impact_layer: Analysis result used to produce file.
    :type QgsVectorLayer

    :raises: Exception
    """
    try:
        impact_layer.write_to_file(join_if_relative(cli_arguments.output_file))
    except Exception as exc:
        print exc.message

if __name__ == '__main__':
    print "python accent.py"
    print ""

    try:
        # Parse arguments, use usage.txt as syntax definition.
        shell_arguments = docopt.docopt(usage)
    except docopt.DocoptExit as e:
        print e.message

    arguments = CliArgs(shell_arguments)

    LOGGER.debug(shell_arguments)
    try:
        if arguments.show_list is True:
            # setup functions
            register_impact_functions()
            show_names(get_ifunction_list())
        elif arguments.version is True:
            print "QGIS VERSION: " + str(qgis_version())
        elif (arguments.extent is not None) and\
                (arguments.hazard is not None) and\
                (arguments.exposure is not None) and\
                (arguments.output_file is not None):
            LOGGER.debug('--BEGIN-RUN--')
            run_if(arguments)
            LOGGER.debug('--END RUN--')
    except Exception as excp:
        print excp.message
        print excp.__doc__


print " "

# INSTALL on Ubuntu with:
# chmod ug+x accent.py
# sudo ln -s `pwd`/accent.py  /usr/bin
