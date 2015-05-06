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

import logging
LOGGER = logging.getLogger('InaSAFE')

# globals
output_file = None
hazard = None
exposure = None
version = None
show_list = None


def get_ifunction_list():
    registry = Registry()
    return registry.impact_functions


def show_names(ifs):
    for impact_function in ifs:
        print impact_function.__name__

if __name__ == '__main__':
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
        # Count is a mandatory option, caps is optional
        output_file = arguments['FILE']
        hazard = arguments['--hazard']
        exposure = arguments['--exposure']
        version = arguments['--version']
        show_list = arguments['--list']
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
        print "do an IF dude!"

