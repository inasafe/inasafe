# coding=utf-8
"""Function to manage self-registering plugins.

The design is based on http://effbot.org/zone/metaclass-plugins.htm

To register the plugin, the module must be imported by the Python process
using it.

InaSAFE Disaster risk assessment tool developed by AusAid -
  **IS Utilities implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'christian@kartoza.com <Christian Christelis>'
__revision__ = '$Format:%H$'
__date__ = '29/04/2015'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import logging
from math import ceil
import numpy
from collections import OrderedDict

from safe.defaults import default_minimum_needs
from safe.gui.tools.minimum_needs.needs_profile import filter_needs_parameters
import safe.messaging as m
from safe.utilities.i18n import tr

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


def has_no_data(layer_data):
    """Determine whether or not a layer contains nan values.
    :param layer_data: Layer data that is to be inspected.
    :type layer_data: ndarry
    :return: The True if there is nodata in layer_data.
    :rtype: bool
    """
    return numpy.isnan(numpy.sum(layer_data))


def get_key_for_value(value, value_map):
    """Obtain the key of a value from a value map.

    :param value: The value mapped to a key in value_map.
    :type value: int, str, float

    :param value_map: A value mapping.
    :type value_map: dict

    :returns: A key for the value.
    :rtype: str
    """
    for key, values in value_map.iteritems():
        if value in values:
            return key
    return None


def no_population_impact_message(question):
    """Create a message that indicates that no population were impacted.

    :param question: A question sentence that will be used as the table
        caption.
    :type question: basestring

    :returns: An html document containing a nice message saying nobody was
        impacted.
    :rtype: basestring
    """
    message = m.Message()
    table = m.Table(
        style_class='table table-condensed table-striped')
    row = m.Row()
    label = m.ImportantText(tr('People impacted'))
    content = 0
    row.add(m.Cell(label))
    row.add(m.Cell(content))
    table.add(row)
    table.caption = question
    message.add(table)
    message = message.to_html(suppress_newlines=True)
    return message
