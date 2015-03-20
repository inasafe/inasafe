# coding=utf-8
"""Function to manage self-registering plugins

The design is based on http://effbot.org/zone/metaclass-plugins.htm

To register the plugin, the module must be imported by the Python process
using it.
"""

import logging
from math import ceil
from collections import OrderedDict

from safe.utilities.i18n import tr
from safe.defaults import default_minimum_needs
from safe.impact_functions.impact_function_manager import ImpactFunctionManager

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
    """Get list of layers that have category=='hazard'
    """

    return extract_layers(layers, 'category', 'hazard')


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
    """Get list of layers that have category=='exposure'
    """

    return extract_layers(layers, 'category', 'exposure')


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


def get_question(hazard_title, exposure_title, impact_function):
    """Rephrase the question asked.

    :param hazard_title: Hazard title.
    :type hazard_title: str

    :param exposure_title: Exposure title.
    :type exposure_title: str

    :param impact_function: An impact function object.
    :type impact_function: ImpactFunction
    """

    function_title = ImpactFunctionManager.get_function_title(impact_function)
    return (tr('In the event of <i>%(hazard)s</i> how many '
               '<i>%(exposure)s</i> might <i>%(impact)s</i>')
            % {'hazard': hazard_title.lower(),
               'exposure': exposure_title.lower(),
               'impact': function_title.lower()})


def convert_to_old_keywords(converter, keywords):
    """Convert new keywords system to old keywords system by aliases.

    Since we have new keywords system in definitions.py and assigned by wizard,
    it will have backward incompatibility because the current impact function
    selector still use the old system.

     This method will convert new keywords to old keyword that has the same
     objective.

     :param converter: a dictionary that contains all possible aliases
        from new keywords to old keywords.
     :type converter: dict

     :param keywords: list of dictionary keyword
     :type keywords: list

     .. versionadded:: 2.1
    """
    for keyword in keywords:
        for key, value in keyword.iteritems():
            try:
                aliases = converter[key]
                for alias_key, alias_value in aliases.iteritems():
                    if value.lower() in alias_value:
                        keyword[key] = alias_key
                        break
            except KeyError:
                pass
