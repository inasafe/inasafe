# -*- coding: utf-8 -*-
"""**Postprocessors package.**

.. tip::
   import like this from safe.postprocessors import get_post_processors and
   then call get_post_processors(requested_postprocessors)

"""

__author__ = 'Marco Bernasocchi <marco@opengis.ch>'
__revision__ = '$Format:%H$'
__date__ = '10/10/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

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
    Creates a dictionary of applicable postprocessor instances

    Args:
        * requested_postprocessors: dictionary of requested
            postprocessors such as
            {
            'Gender': {'on': True},
            'Age': {'on': True,
                    'params': {
                        'youth_ratio': defaults['YOUTH_RATIO'],
                        'adult_ratio': defaults['ADULT_RATIO'],
                        'elder_ratio': defaults['ELDER_RATIO']
                        }
                    }
            }
            with 'PostprocessorName': {'on': True} being the minimum needed to
            activate a postprocessor.
            If asked for unimplemented postprocessors, the factory will just
            skip it returning the valid ones
    Returns:
        dict of postprocessors instances e.g.
            {'Gender':GenderPostprocessors instance}
    """

    postprocessor_instances = {}

    if requested_postprocessors is None or requested_postprocessors == {}:
        return postprocessor_instances

    for name, values in requested_postprocessors.iteritems():
        constr_id = name + 'Postprocessor'
        try:
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
        except KeyError:
            LOGGER.debug(constr_id + ' has no "on" key, skipping it')

    return postprocessor_instances
