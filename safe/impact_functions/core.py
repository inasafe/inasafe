# coding=utf-8
"""Function to manage self-registering plugins

The design is based on http://effbot.org/zone/metaclass-plugins.htm

To register the plugin, the module must be imported by the Python process
using it.
"""

import logging
from math import ceil
from collections import OrderedDict

from safe.defaults import default_minimum_needs

LOGGER = logging.getLogger('InaSAFE')


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
        population_needs_by_frequency[resource['frequency']].append(resource)

    return population_needs_by_frequency


def population_rounding_full(number):
    """This function performs a rigorous population rounding.

    :param number: The amount of people as calculated.
    :type number: int, float

    :returns: result and rounding bracket.
    :rtype: (int, int)
    """
    if number < 1000:
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


# ---------------------------------------
# Helpers for individual impact functions
# --------------------------------------
def get_hazard_layers(layers):
    """Get list of layers that have layer_purpose=='hazard'
    """

    return extract_layers(layers, 'layer_purpose', 'hazard')


def get_hazard_layer(layers):
    """Get hazard layer from list of layers

    If there are more than one, only the first is returned.
    Use get_hazard_layers if more are expected and needed

    If no layers fit the description None is returned
    """

    L = get_hazard_layers(layers)
    if len(L) > 0:
        return L[0]
    else:
        return None


def get_exposure_layers(layers):
    """Get list of layers that have layer_purpose=='exposure'
    """

    return extract_layers(layers, 'layer_purpose', 'exposure')


def get_exposure_layer(layers):
    """Get exposure layer from list of layers

    If there are more than one, only the first is returned.
    Use get_hazard_layers if more are expected and needed

    If no layers fit the description None is returned
    """

    L = get_exposure_layers(layers)
    if len(L) > 0:
        return L[0]
    else:
        return None


def extract_layers(layers, keyword, value):
    """Extract layers with specified keyword/value pair
    """

    extracted_layers = []
    for layer in layers:
        if value in layer.get_keywords(keyword):
            extracted_layers.append(layer)

    return extracted_layers
