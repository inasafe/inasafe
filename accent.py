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

usage = r""
usage_file = file('usage.txt')
for delta in usage_file:
    usage += delta


import docopt
from safe.impact_functions.registry import Registry
from safe.impact_functions import register_impact_functions
from safe.test.utilities import get_qgis_app
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from qgis.core import (
    QgsRasterLayer,
    QgsRaster,
    QgsPoint,
    QgsVectorLayer,
    QgsVectorFileWriter,
    QgsRectangle)
from safe.utilities.keyword_io import KeywordIO
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

# directories
# defaults look like cli\--hazard
#                       |--exposure
#                       |--results

default_cli_dir = os.path.abspath(os.path.join(
    os.path.realpath(os.path.dirname(__file__)), 'cli'))
default_hazard_dir = os.path.abspath(
    os.path.join(default_cli_dir, 'hazard'))
default_exposure_dir = os.path.abspath(
    os.path.join(default_cli_dir, 'exposure'))
default_results_dir = os.path.abspath(
    os.path.join(default_cli_dir, 'results'))


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


def get_qgis_app():
    LOGGER.debug('-- get qgis app --')
    """ Start one QGIS application.

    :returns: Handle to QGIS app, canvas, iface and parent. If there are any
        errors the tuple members will be returned as None.
    :rtype: (QgsApplication, CANVAS, IFACE, PARENT)

    If QGIS is already running the handle to that app will be returned.
    """

    try:
        from qgis.core import QgsApplication
        from qgis.gui import QgsMapCanvas  # pylint: disable=no-name-in-module
        # noinspection PyPackageRequirements
        from PyQt4 import QtGui, QtCore  # pylint: disable=W0621
        # noinspection PyPackageRequirements
        from PyQt4.QtCore import QCoreApplication, QSettings
        from safe.gis.qgis_interface import QgisInterface
    except ImportError:
        return None, None, None, None

    global QGIS_APP  # pylint: disable=W0603

    gui_flag = False  # run qgis in gui mode? does this make a difference?

    # AG: For testing purposes, we use our own configuration file instead
    # of using the QGIS apps conf of the host
    # noinspection PyCallByClass,PyArgumentList
    QCoreApplication.setOrganizationName('QGIS')
    # noinspection PyCallByClass,PyArgumentList
    QCoreApplication.setOrganizationDomain('qgis.org')
    # noinspection PyCallByClass,PyArgumentList
    QCoreApplication.setApplicationName('CLI')

    # noinspection PyPep8Naming
    QGIS_APP = QgsApplication(sys.argv, gui_flag)

    # Make sure QGIS_PREFIX_PATH is set in your env if needed!
    QGIS_APP.initQgis()
    s = QGIS_APP.showSettings()
    LOGGER.debug(s)

    # Save some settings
    settings = QSettings()
    settings.setValue('locale/overrideFlag', True)
    settings.setValue('locale/userLocale', 'en_US')

    global PARENT  # pylint: disable=W0603
    # noinspection PyPep8Naming
    PARENT = QtGui.QWidget()

    global CANVAS  # pylint: disable=W0603
    # noinspection PyPep8Naming
    CANVAS = QgsMapCanvas(PARENT)
    CANVAS.resize(QtCore.QSize(400, 400))

    global IFACE  # pylint: disable=W0603
    # QgisInterface is a stub implementation of the QGIS plugin interface
    # noinspection PyPep8Naming
    IFACE = QgisInterface(CANVAS)
    register_impact_functions()

    return QGIS_APP, CANVAS, IFACE, PARENT


def get_hazard():
    try:
        if raster_hazard is not None:
            hazard_base = os.path.join(default_hazard_dir, raster_hazard)
            LOGGER.debug(hazard_base)
            qhazard = QgsRasterLayer(hazard_base + '.asc', 'my raster')
        elif vector_hazard is not None:
            hazard_base = os.path.join(default_hazard_dir, vector_hazard)
            LOGGER.debug(hazard_base)
            qhazard = QgsVectorLayer(hazard_base + '.shp', 'my raster')
        # noinspection PyUnresolvedReferences
        if not qhazard.isValid():
            print "hazard raster layer not valid"
            print "Perhaps run-env-linux.sh /usr"
        else:
            print "hazard raster layer is VALID!!"
        hazard_extent = qhazard.extent()
        LOGGER.debug('hazard_extent')
        LOGGER.debug(hazard_extent)
        LOGGER.debug(qhazard.width())
        return qhazard
    except Exception as exc:
        print exc.message


def get_exposure():
    try:
        if vector_exposure is not None:
            exposure_base = os.path.join(default_exposure_dir, vector_exposure)
            LOGGER.debug(exposure_base)
            qexposure = QgsVectorLayer(exposure_base + '.shp', 'cli_vector', 'ogr')
        elif raster_exposure is not None:
            exposure_base = os.path.join(default_exposure_dir,  raster_exposure)
            LOGGER.debug(exposure_base)
            qexposure = QgsVectorLayer(exposure_base + '.tif', 'cli_raster', 'ogr')
        else:
            print 'Error : Exposure layer'

        if not qexposure.isValid():
            print "exposure vector layer not valid"
            print "Perhaps run-env-linux.sh /usr"
        else:
            print "exposure vector layer is VALID!!"
        # noinspection PyUnresolvedReferences
        exposure_extent = qexposure.extent()
        LOGGER.debug('exposure_extent')
        LOGGER.debug(exposure_extent)
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
    LOGGER.debug(shell_arguments['--impact-function'])

    keyword_io = KeywordIO()

    try:
        from safe.utilities.analysis import Analysis
    except ImportError:
        LOGGER.debug('**Import error**')
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
    impact_layer.write_to_file(
        os.path.join(default_results_dir, output_file))


if __name__ == '__main__':
    print "python accent.py"
    print ""

    try:
        # Parse arguments, use file docstring as a parameter definition
        shell_arguments = docopt.docopt(usage)
    except docopt.DocoptExit as e:
        print e.message

    # populate global vars with arguments from shell
    try:
        output_file = shell_arguments['--output-file']
    except Exception as e:
        print e.message
    try:
        vector_hazard = shell_arguments['--vector-hazard']
    except Exception as e:
        print e.message
    try:
        raster_hazard = shell_arguments['--raster-hazard']
    except Exception as e:
        print e.message
    try:
        vector_exposure = shell_arguments['--vector-exposure']
    except Exception as e:
        print e.message
    try:
        raster_exposure = shell_arguments['--raster-exposure']
    except Exception as e:
        print e.message
    try:
        version = shell_arguments['--version']
    except Exception as e:
        print e.message
    try:
        show_list = shell_arguments['--list-functions']
    except Exception as e:
        print e.message
    try:
        extent = shell_arguments['--extent'].split(':')
        LOGGER.debug(extent)
    except Exception as e:
        print e.message
    LOGGER.debug(shell_arguments)

    if show_list is True:
        # setup functions
        register_impact_functions()
        show_names(get_ifunction_list())

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

# run with :
# python accent.py --hazard=jakarta_flood_design --exposure=buildings
# --extent=106.8054130000000015,-6.1913361000000000,106.8380719000000028,-6.1672457999999999
# --impact-function=FloodRasterBuildingFunction success
