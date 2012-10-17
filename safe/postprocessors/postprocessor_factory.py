"""
InaSAFE Disaster risk assessment tool developed by AusAid - **GUI Dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. todo:: Check raster is single band

"""

__author__ = 'marco@opengis.ch'
__revision__ = '$Format:%H$'
__date__ = '13/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import logging

# pylint: disable=W0611
from gender_postprocessor import GenderPostprocessor
from age_postprocessor import AgePostprocessor
# pylint: enable=W0611

LOGGER = logging.getLogger('InaSAFE')
#this _must_reflect the imported classes above
AVAILABLE_POSTPTOCESSORS = ['Gender', 'Age']


def get_post_processors(requested_postprocessors):
    """
    Creates a dictionary of applicable postprocessors
    :param requested_postprocessors: dictionary of requested
        postprocessors such as {'Gender': True, 'Age': False}
    :return: dict of postprocessors instances
        e.g. {'Gender':GenderPostprocessors instance}
    """

    postprocessor_instances = {}

    if requested_postprocessors is None or requested_postprocessors == {}:
        return postprocessor_instances

    for name, values in requested_postprocessors.iteritems():
        constr_id = name + 'Postprocessor'
        if values['on']:
            if name in AVAILABLE_POSTPTOCESSORS:
                #http://stackoverflow.com/a/554462
                constr = globals()[constr_id]
                instance = constr()
                postprocessor_instances[name] = instance
            else:
                LOGGER.debug(constr_id + ' is not a valid Postprocessor,'
                                         ' skipping it')

        else:
            LOGGER.debug(constr_id + ' user disabled, skipping it')

    return postprocessor_instances
