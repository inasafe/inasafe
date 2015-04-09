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

# pylint: disable=unused-import
from gender_postprocessor import GenderPostprocessor
from age_postprocessor import AgePostprocessor
from aggregation_postprocessor import AggregationPostprocessor
from building_type_postprocessor import BuildingTypePostprocessor
from road_type_postprocessor import RoadTypePostprocessor
from aggregation_categorical_postprocessor import \
    AggregationCategoricalPostprocessor
from minimum_needs_postprocessor import MinimumNeedsPostprocessor
from safe.utilities.i18n import tr
# pylint: enable=unused-import

LOGGER = logging.getLogger('InaSAFE')
# this _must_reflect the imported classes above
# please put the value of this dictionary in
# safe/common/dynamic_translations.py for the run time translation
AVAILABLE_POSTPTOCESSORS = {
    'Gender': 'Gender',
    'Age': 'Age',
    'Aggregation': 'Aggregation',
    'BuildingType': 'Building type',
    'RoadType': 'Road type',
    'AggregationCategorical': 'Aggregation categorical',
    'MinimumNeeds': 'Minimum needs'}


def get_postprocessors(requested_postprocessors):
    """
    Creates a dictionary of applicable postprocessor instances

    :param requested_postprocessors: The postprocessors to return e.g. ::

                {
                'Gender': [BooleanParameter],
                'Age': [BooleanParameter, FloatParameter ....]
                }

            with 'PostprocessorName': [BooleanParameter]
            being the minimum needed to activate a postprocessor.

            If asked for unimplemented postprocessors, the factory will just
            skip it returning the valid ones
    :type requested_postprocessors: dict e.g. name:[list_elements]

    :returns: Dict of postprocessors instances e.g.::

            {'Gender': GenderPostprocessors instance}

    :rtype: dict

    """
    postprocessor_instances = {}

    if requested_postprocessors is None or requested_postprocessors == {}:
        return postprocessor_instances
    for name, values in requested_postprocessors.iteritems():
        constructor_class_name = name + 'Postprocessor'
        try:
            if values[0].value:
                if name in AVAILABLE_POSTPTOCESSORS.keys():
                    # http://stackoverflow.com/a/554462
                    constructor = globals()[constructor_class_name]
                    instance = constructor()
                    postprocessor_instances[name] = instance
                else:
                    LOGGER.debug(
                        constructor_class_name + ' is not a valid '
                                                 'Postprocessor, skipping it')
            else:
                LOGGER.debug(
                    constructor_class_name + ' user disabled, skipping it')
        except KeyError:
            LOGGER.debug(
                constructor_class_name + ' has no "on" key, skipping it')

    return postprocessor_instances


def get_postprocessor_human_name(postprocessor):
    """Returns the human readable name of  post processor

    :param postprocessor: Machine name of the postprocessor
    :type postprocessor:

    :returns: The human readable name
    :rtype: str
    """
    # Sunni : translete it first
    human_name_translated = tr(AVAILABLE_POSTPTOCESSORS[postprocessor])
    return human_name_translated
