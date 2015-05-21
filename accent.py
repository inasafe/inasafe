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
# noinspection PyPackageRequirements
# next line already done inside run_if
#from PyQt4 import QtGui  # pylint: disable=W0621
#import qgis.utils
from safe.impact_functions.registry import Registry
from safe.impact_functions import register_impact_functions
from safe.test.utilities import test_data_path, get_qgis_app
from safe.impact_functions.impact_function_manager import ImpactFunctionManager
from qgis.core import (
    QgsRasterLayer,
    QgsRaster,
    QgsPoint,
    QgsVectorLayer,
    QgsRectangle)
import os
import sys
import logging
LOGGER = logging.getLogger('InaSAFE')

# arguments/options
output_file = None
hazard = None
exposure = None
version = None
show_list = None
extent = None
# directories
default_dir = os.path.abspath(os.path.join(
    os.path.realpath(os.path.dirname(__file__)), 'cli'))

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


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

    gui_flag = False  # All test will run qgis in gui mode

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
    qhazard = None
    try:
        HAZARD_BASE = test_data_path(default_dir, 'hazard', 'continuous_flood_20_20')
        LOGGER.debug(HAZARD_BASE)
        qhazard = QgsRasterLayer(HAZARD_BASE + '.asc', 'my raster')
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
    except Exception as exc:
        print exc.message

    return qhazard


def get_exposure():
    try:
        EXPOSURE_BASE = test_data_path(default_dir, 'exposure', 'buildings')
        LOGGER.debug(EXPOSURE_BASE)
        qexposure = QgsVectorLayer(EXPOSURE_BASE + '.shp', 'ogr')
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
        arguments['--impact-function'])
    LOGGER.debug(arguments['--impact-function'])

    try:
        from safe.utilities.analysis import Analysis
        LOGGER.debug('imported')
    except ImportError:
        LOGGER.debug('**except** :(')
        return None, None, None, None
    analysis = Analysis()
    # Layers
    analysis.hazard_layer = qhazard
    analysis.exposure_layer = qexposure
    # analysis.user_extent
    # analysis.user_extent(
    #     106.8054130000000015, -6.1913361000000000,
    #     106.8380719000000028, -6.1672457999999999)
    print 'after'
    analysis.impact_function = impact_function
    LOGGER.debug(analysis)
    analysis.setup_analysis()
    LOGGER.debug('eeee')
    analysis.run_analysis()
    LOGGER.debug("end :)")


def set_pycharm_environ():
    try:
        charm_settings = {
            'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games',
            'PYTHONUNBUFFERED': '1',
            'SESSION': 'ubuntu',
            'LANG': 'en_ZA.UTF-8',
            'DEFAULTS_PATH': '/usr/share/gconf/ubuntu.default.path',
            'SHELL': '/bin/bash',
            'XDG_SESSION_PATH': '/org/freedesktop/DisplayManager/Session0',
            'XAUTHORITY': '/home/jannes/.Xauthority',
            'LANGUAGE': 'en_ZA:en',
            'SESSION_MANAGER': 'local/merensky:@/tmp/.ICE-unix/1702,unix/merensky:/tmp/.ICE-unix/1702',
            'SHLVL': '0',
            'MANDATORY_PATH': '/usr/share/gconf/ubuntu.mandatory.path',
            'JOB': 'dbus',
            'LD_LIBRARY_PATH': '/usr/local/src/pycharm-4.0.6/bin:',
            'QT4_IM_MODULE': 'xim',
            'COMPIZ_CONFIG_PROFILE': 'ubuntu',
            'TEXTDOMAIN': 'im-config',
            'SESSIONTYPE': 'gnome-session',
            'IM_CONFIG_PHASE': '1',
            'GIO_LAUNCHED_DESKTOP_FILE_PID': '2254',
            'GPG_AGENT_INFO': '/run/user/1000/keyring-nEkiCw/gpg:0:1',
            'HOME': '/home/jannes',
            'CLUTTER_IM_MODULE': 'xim',
            'SELINUX_INIT': 'YES',
            'GIO_LAUNCHED_DESKTOP_FILE': '/usr/share/applications/jetbrains-pycharm.desktop',
            'XDG_RUNTIME_DIR': '/run/user/1000',
            'INSTANCE': '',
            'PYTHONPATH': '$PYTHONPATH:/usr/share/qgis/python/plugins:/home/jannes/gitwork/inasafe/safe:/home/jannes/gitwork/inasafe',
            'COMPIZ_BIN_PATH': '/usr/bin/',
            'CLASSPATH': '/usr/local/src/pycharm-4.0.6/bin/../lib/bootstrap.jar:/usr/local/src/pycharm-4.0.6/bin/../lib/extensions.jar:/usr/local/src/pycharm-4.0.6/bin/../lib/util.jar:/usr/local/src/pycharm-4.0.6/bin/../lib/jdom.jar:/usr/local/src/pycharm-4.0.6/bin/../lib/log4j.jar:/usr/local/src/pycharm-4.0.6/bin/../lib/trove4j.jar:/usr/local/src/pycharm-4.0.6/bin/../lib/jna.jar',
            'SSH_AUTH_SOCK': '/run/user/1000/keyring-nEkiCw/ssh',
            'GDMSESSION': 'ubuntu',
            'XMODIFIERS': '@im=ibus',
            'INASAFE_POPULATION_PATH': '/home/jannes/gitwork/inasafe/realtime/fixtures/exposure/population.tif',
            'TEXTDOMAINDIR': '/usr/share/locale/',
            'XDG_SEAT_PATH': '/org/freedesktop/DisplayManager/Seat0',
            'PYCHARM_HELPERS_DIR': '/usr/local/src/pycharm-4.0.6/helpers/pycharm',
            'XDG_SESSION_ID': 'c1',
            'DBUS_SESSION_BUS_ADDRESS': 'unix:abstract=/tmp/dbus-EdUWo0i0Yq',
            'UPSTART_SESSION': 'unix:abstract=/com/ubuntu/upstart-session/1000/1534',
            'XDG_CONFIG_DIRS': '/etc/xdg/xdg-ubuntu:/usr/share/upstart/xdg:/etc/xdg',
            'GTK_MODULES': 'overlay-scrollbar:unity-gtk-module',
            'XDG_MENU_PREFIX': 'gnome-',
            'GDM_LANG': 'en_US',
            'PYCHARM_HOSTED': '1',
            'XDG_DATA_DIRS': '/usr/share/ubuntu:/usr/share/gnome:/usr/local/share/:/usr/share/',
            'DISPLAY': ':0',
            'XDG_MENU_PREFIX': 'gnome-',
            }
        for pycharm_setting in charm_settings:
            if pycharm_setting not in os.environ:
                os.environ[pycharm_setting] = charm_settings[pycharm_setting]
                LOGGER.debug('setting ' + pycharm_setting)
        pycharm_lines = ['/usr/share/qgis/python/plugins/processing',
         '/home/jannes/gitwork/inasafe/safe/gis/test',
         '/usr/local/lib/python2.7/dist-packages/pycharm-debug.egg',
         '/usr/lib/python2.7/dist-packages',
         '/home/jannes/gitwork/inasafe/safe/gis/test/$PYTHONPATH',
         '/usr/share/qgis/python/plugins',
         '/home/jannes/gitwork/inasafe/safe',
         '/home/jannes/gitwork/inasafe',
         '/usr/lib/python2.7',
         '/usr/lib/python2.7/plat-x86_64-linux-gnu',
         '/usr/lib/python2.7/lib-tk', '/usr/lib/python2.7/lib-old',
         '/usr/lib/python2.7/lib-dynload',
         '/usr/local/lib/python2.7/dist-packages',
         '/usr/lib/python2.7/dist-packages/PILcompat',
         '/usr/lib/python2.7/dist-packages/gst-0.10',
         '/usr/lib/python2.7/dist-packages/gtk-2.0',
         '/usr/lib/pymodules/python2.7',
         '/usr/lib/python2.7/dist-packages/ubuntu-sso-client',
         '/home/jannes/gitwork/inasafe/safe_extras',
         '/home/jannes/gitwork/inasafe/safe_extras/parameters']
        for l in pycharm_lines:
            if l not in sys.path:
                sys.path.append(l)
                LOGGER.debug('adding path:' + ' ' + l)
    except Exception as exc:
        print exc.message
        print exc.__doc__


if __name__ == '__main__':
    LOGGER.debug(sys.path)
    #set_pycharm_environ()
    print "python accent.py"
    print ""
    # setup functions
    register_impact_functions()
    # globals
    output_file = None
    hazard = None
    exposure = None
    version = None
    show_list = None
    extent = None
    try:
        # Parse arguments, use file docstring as a parameter definition
        arguments = docopt.docopt(usage)
        output_file = arguments['FILE']
        hazard = arguments['--hazard']
        exposure = arguments['--exposure']
        version = arguments['--version']
        show_list = arguments['--list-functions']
        extent = arguments['--extent']
        LOGGER.debug(arguments)
    # Handle invalid options
    except docopt.DocoptExit as e:
        print e.message

    if show_list:
        show_names(get_ifunction_list())

    elif (extent is not None) and\
            (hazard is not None) and\
            (exposure is not None):
        LOGGER.debug('--do an IF--')
        try:
            run_if()
        except Exception as e:
            print e.message
            print e.__doc__
        LOGGER.debug('-- just did an IF--')

