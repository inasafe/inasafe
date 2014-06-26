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
from safe.common.utilities import ugettext as tr

# pylint: disable=W0611
from gender_postprocessor import GenderPostprocessor
from age_postprocessor import AgePostprocessor
from aggregation_postprocessor import AggregationPostprocessor
from building_type_postprocessor import BuildingTypePostprocessor
from road_type_postprocessor import RoadTypePostprocessor
from aggregation_categorical_postprocessor import \
    AggregationCategoricalPostprocessor
from minimum_needs_postprocessor import MinimumNeedsPostprocessor
# pylint: enable=W0611

LOGGER = logging.getLogger('InaSAFE')
#this _must_reflect the imported classes above
# please put the value of this dictionary in
# safe/common/dynamic_translations.py for the run time translation
AVAILABLE_POSTPTOCESSORS = {'Gender': 'Gender',
                            'Age': 'Age',
                            'Aggregation': 'Aggregation',
                            'BuildingType': 'Building type',
                            'RoadType': 'Road type',
                            'AggregationCategorical':
                            'Aggregation categorical',
                            'MinimumNeeds': 'Minimum needs'
                            }


def get_postprocessors(requested_postprocessors, aoi_mode):
    """
    Creates a dictionary of applicable postprocessor instances

    Args:
        * requested_postprocessors: dictionary of requested
            postprocessors such as::

                {
                'Gender': {'on': True},
                'Age': {'on': True,
                        'params': {
                            'youth_ratio': defaults['YOUTH_RATIO'],
                            'adult_ratio': defaults['ADULT_RATIO'],
                            'elderly_ratio': defaults['ELDERLY_RATIO']
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

        # Flag specifying if aggregation is required. If set, postprocessor
        # will be disabled when AOI mode is enabled.
        requires_aggregation = True
        # lets check if the IF has a
        # ['params']['disable_for_entire_area_aggregation']
        # that would turn off the current postprocessor if in aoi_mode
        if aoi_mode:
            try:
                requires_aggregation = (
                    values['params']['disable_for_entire_area_aggregation'])
            except KeyError:
                pass

        try:
            if values['on'] and requires_aggregation:
                if name in AVAILABLE_POSTPTOCESSORS.keys():
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


def get_postprocessor_human_name(postprocesor):
    """
    Returns the human readable name of  post processor

    Args:
        * postprocessor: Machine name of the postprocessor

    Returns:
        str with the human readable name
    """
    # Sunni : translete it first
    human_name_translated = tr(AVAILABLE_POSTPTOCESSORS[postprocesor])
    return human_name_translated
