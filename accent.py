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
    QgsVectorLayer)
from safe.utilities.keyword_io import KeywordIO
from safe.utilities.gis import qgis_version
import os
import sys
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
            print "hazard raster layer is NOT VALID"
            print "Perhaps run-env-linux.sh /usr"
        else:
            print "hazard raster layer is VALID"
        return qhazard
    except Exception as exc:
        print exc.message


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
            print "exposure vector layer not valid"
            print "Perhaps run-env-linux.sh /usr"
        else:
            print "exposure vector layer is VALID!!"
        return qexposure
    except Exception as exc:
        print exc.message
        print exc.__doc__


def run_if():
    qhazard = get_hazard()
    qexposure = get_exposure()
    # IF
    impact_function_manager = ImpactFunctionManager()
    impact_function = impact_function_manager.get(
        shell_arguments['--impact-function'])
    keyword_io = KeywordIO()
    try:
        from safe.utilities.analysis import Analysis
    except ImportError:
        LOGGER.debug('Import error for Analysis module')
        print ImportError.message
        return None, None, None, None
    analysis = Analysis()
    # Layers
    try:
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
        print 'begin analysis setup'
        analysis.setup_analysis()
        print 'stop analysis setup'
    except Exception as exc:
        print exc.message
    try:
        analysis.run_analysis()
        LOGGER.debug("end analysis :)")
    except Exception as exc:
        print exc.message
    try:
        impact_layer = analysis.get_impact_layer()
    except Exception as exc:
        print exc.message
    # analysis result output
    if impact_layer is None:
        print "Error : No impact layer generated"
    LOGGER.debug(type(impact_layer))
    LOGGER.debug(impact_layer.__doc__)
    write_results(impact_layer)
    # do report


def write_results(impact_layer):
    """This function writes the impact_layer in shapefile format
    :param impact_layer:
    :type Vector
    """
    impact_layer.write_to_file(join_if_relative(output_file))


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
        try:
            run_if()
        except Exception as e:
            print e.message
            print e.__doc__
        LOGGER.debug('--END RUN--')

# print line to make it look nice
print " "

# INSTALL on Ubuntu with:
# chmod ug+x accent.py
# sudo ln -s `pwd`/accent.py  /usr/bin
#
# RUN example :
#
# python accent.py to list all IFs then
# python accent.py --raster-hazard=jakarta_flood_design.asc --vector-exposure=buildings.shp
# --extent=106.8054130000000015,-6.1913361000000000,106.8380719000000028,-6.1672457999999999
# --impact-function=FloodRasterBuildingFunction success
