"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
 - **Module inasafe.**

This script initializes the plugin, making it known to QGIS.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__version__ = '0.6.0'
__date__ = '10/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import os


def name():
    """A user friendly name for the plugin."""
    return 'InaSAFE'


def description():
    """A one line description for the plugin."""
    return ('InaSAFE Disaster Scenario Assessment for Emergencies'
            ' tool developed by BNPB, AusAID, World Bank')


def version():
    """Version of the plugin."""
    return 'Version 0.5.0'


def qgisMinimumVersion():
    """Minimum version of QGIS needed to run this plugin

       This is currently set to 1.7
    """
    return '1.7'


def icon():
    """Icon path for the plugin - metadata.txt it will override this"""
    return os.path.join(os.path.dirname(__file__), 'safe_qgis', 'resources',
                        'img', 'icon.png')


def classFactory(iface):
    """Load Plugin class from file Plugin"""

    # setup the logging
    #import logging
    #logger = logging.getLogger('risiko')

    # TODO (TD): Change to read from a log file see
    # http://docs.python.org/howto/logging-cookbook.html#logging-cookbook
    # FIXME (TD): Logger is working at this level but not in the impact
    #functions!!
    #logger.setLevel(logging.DEBUG)
    #ch = logging.FileHandler('risiko.log')
    #fmt_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    #formatter = logging.Formatter(fmt_str)
    #ch.setFormatter(formatter)
    #logger.addHandler(ch)

    # Try loading the FunctionProvider
    #from impact_functions.core import FunctionProvider
    # FIXME (TD): reload doesn't seem to reload the plugins anything

    #logger.debug("reload core 3")
    from safe_qgis.plugin import Plugin
    return Plugin(iface)
