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
import sys
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


def get_ifunction_list():
    LOGGER.debug('get IF list')
    registry = Registry()
    LOGGER.debug(registry.impact_functions)
    return registry.impact_functions


def show_names(ifs):
    for impact_function in ifs:
        print impact_function.__name__


# all paths are made to be absolute
def join_if_relative(path_argument):
    """Make path absolute with current directory as base.

    :param path_argument:
    :type path_argument:
    :returns:
    :rtype
    """
    if not os.path.isabs(path_argument):
        LOGGER.debug('joining path for ' + path_argument)
        return os.path.join(default_cli_dir, path_argument)
    else:
        return os.path.abspath(path_argument)


def get_hazard():
    try:
        if vector_hazard is not None:
            hazard_base = join_if_relative(vector_hazard)
            qhazard = QgsVectorLayer(
                hazard_base, 'cli_vector_hazard', 'ogr')
        elif raster_hazard is not None:
            hazard_base = join_if_relative(raster_hazard)
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


def get_exposure():
    try:
        if vector_exposure is not None:
            exposure_base = join_if_relative(vector_exposure)
            LOGGER.debug(exposure_base)
            qexposure = QgsVectorLayer(exposure_base, 'cli_vector', 'ogr')
        elif raster_exposure is not None:
            exposure_base = join_if_relative(raster_exposure)
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


def run_if():
    try:
        qhazard = get_hazard()
        qexposure = get_exposure()
        # IF
        impact_function_manager = ImpactFunctionManager()
        impact_function = impact_function_manager.get(
            shell_arguments['--impact-function'])
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
        write_results(impact_layer)
        build_report(impact_layer)
    except Exception as exc:
        print exc.message
        print exc.__doc__


def build_report(impact_layer):
    """
    To be called after shapefile has been written
    :param: impact_layer:
    :type: Vector
    """
    try:
        report_template = '/home/jannes/gitwork/inasafe/resources/qgis-composer-templates/inasafe-portrait-a4.qpt'
        impact_layer = QgsVectorLayer(output_file, 'cli_impact', 'ogr')
        LOGGER.debug(impact_layer.__doc__)
        layer_registry = QgsMapLayerRegistry.instance()
        layer_registry.removeAllMapLayers()
        layer_registry.addMapLayer(impact_layer)
        CANVAS.setExtent(impact_layer.extent())
        CANVAS.refresh()
        report = ImpactReport(IFACE, report_template, impact_layer)
        LOGGER.debug(os.path.splitext(output_file)[0] + '.pdf')
        map_path = report.print_map_to_pdf(os.path.splitext(output_file)[0] + '.pdf')
        print "Impact Map : " + map_path
        table_path = report.print_impact_table(os.path.splitext(output_file)[0] + '_table.pdf')
        print "Impact Summary Table : " + table_path
        layer_registry.removeAllMapLayers()

    except Exception as exc:
        print "HERE"
        print exc.message
        print exc.__doc__


def write_results(impact_layer):
    """This function writes the impact_layer in shapefile format
    :param impact_layer:
    :type Vector
    """
    try:
        impact_layer.write_to_file(join_if_relative(output_file))
    except Exception as exc:
        print exc.message

if __name__ == '__main__':
    print "python accent.py"
    print ""
    try:
        # Parse arguments, use usage.txt as a parameter definition
        shell_arguments = docopt.docopt(usage)
    except docopt.DocoptExit as e:
        print e.message

    # populate global vars with arguments from shell
    try:
        output_file = shell_arguments['--output-file']
    except Exception as e:
        LOGGER.debug(e.message)
    try:
        vector_hazard = shell_arguments['--vector-hazard']
    except Exception as e:
        LOGGER.debug(e.message)
    try:
        raster_hazard = shell_arguments['--raster-hazard']
    except Exception as e:
        LOGGER.debug(e.message)
    try:
        vector_exposure = shell_arguments['--vector-exposure']
    except Exception as e:
        LOGGER.debug(e.message)
    try:
        raster_exposure = shell_arguments['--raster-exposure']
    except Exception as e:
        LOGGER.debug(e.message)
    try:
        version = shell_arguments['--version']
    except Exception as e:
        LOGGER.debug(e.message)
    try:
        show_list = shell_arguments['--list-functions']
    except Exception as e:
        LOGGER.debug(e.message)
    try:
        extent = shell_arguments['--extent'].split(':')
        LOGGER.debug(extent)
    except Exception as e:
        LOGGER.debug(e.message)
    LOGGER.debug(shell_arguments)
    try:
        if show_list is True:
            # setup functions
            register_impact_functions()
            show_names(get_ifunction_list())
        elif version is True:
            print "QGIS VERSION: " + str(qgis_version())
        elif (extent is not None) and\
                ((vector_hazard is not None) or (raster_hazard is not None)) and\
                ((vector_exposure is not None) or (raster_exposure is not None)) and\
                (output_file is not None):
            LOGGER.debug('--RUN--')
            run_if()
            LOGGER.debug('--END RUN--')
    except Exception as excp:
        print excp.message
        print excp.__doc__


print " "

# INSTALL on Ubuntu with:
# chmod ug+x accent.py
# sudo ln -s `pwd`/accent.py  /usr/bin
