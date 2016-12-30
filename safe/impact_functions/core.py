# coding=utf-8
"""Helper method for impact functions."""

import logging
from math import ceil
from collections import OrderedDict

from PyQt4.QtCore import QPyNullVariant

from safe.defaults import default_minimum_needs
from safe.gui.tools.minimum_needs.needs_profile import filter_needs_parameters

LOGGER = logging.getLogger('InaSAFE')

__copyright__ = "Copyright 2016, The InaSAFE Project"
__license__ = "GPL version 3"
__email__ = "info@inasafe.org"
__revision__ = '$Format:%H$'


def evacuated_population_weekly_needs(
        population,
        minimum_needs=None):
    """Calculate estimated needs using minimum needs as specified or the
    default.

    :param population: The number of evacuated population.
    :type: int, float

    :param minimum_needs: Ratios used to calculate weekly needs in parameter
     form.
    :type minimum_needs: list,

    :returns: The needs for the evacuated population.
    :rtype: dict
    """
    if not minimum_needs:
        minimum_needs = default_minimum_needs()

    minimum_needs = filter_needs_parameters(minimum_needs)
    population_needs = OrderedDict()
    for resource in minimum_needs:
        resource = resource.serialize()
        amount = resource['value']
        name = resource['name']
        population_needs[name] = int(ceil(population * float(amount)))

    return population_needs


def evacuated_population_needs(population, minimum_needs):
    """Calculate estimated needs using minimum needs configuration provided
    in full_minimum_needs.

    :param population: The number of evacuated population.
    :type: int, float

    :param minimum_needs: Ratios to use when calculating minimum needs.
        Defaults to perka 7 as described in assumptions below.
    :type minimum_needs: list

    :returns: The needs for the evacuated population.
    :rtype: dict
    """
    # Rizky : filter, only for valid serialized ResourceParameter
    minimum_needs = [n for n in minimum_needs if 'frequency' in n]
    frequencies = []
    for resource in minimum_needs:
        if resource['frequency'] not in frequencies:
            frequencies.append(resource['frequency'])

    population_needs_by_frequency = OrderedDict([
        [frequency, []] for frequency in frequencies])

    for resource in minimum_needs:
        if resource['unit']['abbreviation']:
            resource_name = '%s [%s]' % (
                resource['name'],
                resource['unit']['abbreviation'])
        else:
            resource_name = resource['name']
        amount_pp = resource['value']
        resource['amount'] = int(ceil(population * float(amount_pp)))
        resource['table name'] = resource_name
        # Cleaning NULL
        for key, value in resource.items():
            if isinstance(value, QPyNullVariant):
                resource[key] = None
            if isinstance(value, dict):
                for inner_key, inner_value in value.items():
                    if isinstance(inner_value, QPyNullVariant):
                        value[inner_key] = None
        population_needs_by_frequency[resource['frequency']].append(resource)

    return population_needs_by_frequency


def population_rounding_full(number):
    """This function performs a rigorous population rounding.

    :param number: The amount of people as calculated.
    :type number: int, float

    :returns: result and rounding bracket.
    :rtype: (int, int)
    """
    if number < 10:
        rounding = 1
    elif number < 1000:
        rounding = 10
    elif number < 100000:
        rounding = 100
    else:
        rounding = 1000
    number = int(rounding * ceil(1.0 * number / rounding))
    return number, rounding


def population_rounding(number):
    """A shorthand for population_rounding_full(number)[0].

    :param number: The amount of people as calculated.
    :type number: int, float

    :returns: result and rounding bracket.
    :rtype: int
    """
    return population_rounding_full(number)[0]
