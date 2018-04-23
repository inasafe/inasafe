# coding=utf-8
"""
This module contains the abstract class of the MinimumNeeds. The storage
logic is omitted here.
"""
from builtins import object

__author__ = 'Christian Christelis <christian@kartoza.com>'
__date__ = '05/10/2014'
__copyright__ = ('Copyright 2014, Australia Indonesia Facility for '
                 'Disaster Reduction')

import json
from collections import OrderedDict
from os import remove
from os.path import exists, dirname

from safe.utilities.i18n import tr


class MinimumNeeds(object):

    """A abstract class for handling the minimum needs.

    The persistence logic is excluded from this class.

    .. versionadded:: 2.2.
    """

    # Default Name for minimum needs items
    Rice = tr('Rice')
    Drinking_water = tr('Drinking Water')
    Water = tr('Clean Water')
    Family_kits = tr('Family Kits')
    Toilets = tr('Toilets')
    Weekly_hygiene_packs = tr("Weekly Hygiene Packs")
    Additional_rice = tr(
        'Additional Weekly Rice kg for Pregnant and Lactating Women')

    def get_need(self, resource):
        """Get a resource from the minimum_needs.

        :param resource: The resource name
        :type resource: basestring

        :returns: resource needed.
        :rtype: dict, None
        """
        for need in self.minimum_needs:
            if need['name'] == resource:
                return need
        return None

    def get_minimum_needs(self):
        """Get the minimum needed information about the minimum needs.

        That is the resource and the amount.

        :returns: minimum needs
        :rtype: OrderedDict
        """
        minimum_needs = OrderedDict()
        for resource in self.minimum_needs['resources']:
            if resource['Unit abbreviation']:
                name = '%s [%s]' % (
                    tr(resource['Resource name']),
                    resource['Unit abbreviation']
                )
            else:
                name = tr(resource['Resource name'])
            amount = resource['Default']
            minimum_needs[name] = amount
        return OrderedDict(minimum_needs)

    def get_full_needs(self):
        """The full list of minimum needs with all fields.


        :returns: minimum needs
        :rtype: dict
        """
        return self.minimum_needs

    def set_need(self, resource, amount, units, frequency='weekly'):
        """Append a single new minimum need entry to the list.

        :param resource: Minimum need resource name.
        :type resource: basestring

        :param amount: Amount per person per time interval
        :type amount: int, float

        :param units: The unit that the resource is measured in.
        :type: basestring

        :param frequency: How regularly the unit needs to be dispatched
        :type: basestring  # maybe at some point fix this to a selection.
        """
        self.minimum_needs['resources'].append({
            'Resource name': resource,
            'Default': amount,
            'Unit abbreviation': units,
            'Frequency': frequency
        })

    def update_minimum_needs(self, minimum_needs):
        """Overwrite the internal minimum needs with new needs.

         Validate the new minimum needs. If ok, set these as the internal
         minimum needs.

        :param minimum_needs: The new minimum
        :type minimum_needs: dict

        :returns: Returns success code, -1 for failure, 0 for success.
        :rtype: int
        """
        if not isinstance(minimum_needs, dict):
            return -1

        # noinspection PyAttributeOutsideInit
        self.minimum_needs = minimum_needs
        return 0

    @classmethod
    def _defaults(cls):
        """Helper to get the default minimum needs.

        .. note:: Key names will be translated.
        """
        minimum_needs = {
            "resources": [
                {
                    "Default": "2.8",
                    "Minimum allowed": "0",
                    "Maximum allowed": "100",
                    "Frequency": "weekly",
                    "Resource name": cls.Rice,
                    "Resource description": "Basic food",
                    "Unit": "kilogram",
                    "Units": "kilograms",
                    "Unit abbreviation": "kg",
                    "Readable sentence": (
                        "Each person should be provided with {{ Default }} "
                        "{{ Units }} of {{ Resource name }} {{ Frequency }}.")
                },
                {
                    "Default": "17.5",
                    "Minimum allowed": "0",
                    "Maximum allowed": "100",
                    "Frequency": "weekly",
                    "Resource name": cls.Drinking_water,
                    "Resource description": "For drinking",
                    "Unit": "litre",
                    "Units": "litres",
                    "Unit abbreviation": "l",
                    "Readable sentence": (
                        "Each person should be provided with {{ Default }} "
                        "{{ Units }} of {{ Resource name }} {{ Frequency }} "
                        "for drinking.")
                },
                {
                    "Default": "67",
                    "Minimum allowed": "10",
                    "Maximum allowed": "100",
                    "Frequency": "weekly",
                    "Resource name": cls.Water,
                    "Resource description": "For washing",
                    "Unit": "litre",
                    "Units": "litres",
                    "Unit abbreviation": "l",
                    "Readable sentence": (
                        "Each person should be provided with {{ Default }} "
                        "{{ Units }} of {{ Resource name }} {{ Frequency }} "
                        "for washing.")
                },
                {
                    "Default": "0.2",
                    "Minimum allowed": "0.1",
                    "Maximum allowed": "1",
                    "Frequency": "weekly",
                    "Resource name": cls.Family_kits,
                    "Resource description": "Hygiene kits",
                    "Unit": "",
                    "Units": "",
                    "Unit abbreviation": "",
                    "Readable sentence": (
                        "Each family of 5 persons should be provided with 1 "
                        "Family Kit per week.")
                },
                {
                    "Default": "0.05",
                    "Minimum allowed": "0.02",
                    "Maximum allowed": "1",
                    "Frequency": "single",
                    "Resource name": cls.Toilets,
                    "Resource description": "",
                    "Unit": "",
                    "Units": "",
                    "Unit abbreviation": "",
                    "Readable sentence": (
                        "A Toilet should be provided for every 20 persons.")
                }
            ],
            "provenance": "The minimum needs are based on Perka 7/2008.",
            "profile": "BNPB_en"
        }
        return minimum_needs

    def read_from_file(self, filename):
        """Read from an existing json file.

        :param filename: The file to be written to.
        :type filename: basestring, str

        :returns: Success status. -1 for unsuccessful 0 for success
        :rtype: int
        """
        if not exists(filename):
            return -1
        with open(filename) as fd:
            needs_json = fd.read()
            try:
                minimum_needs = json.loads(needs_json)
            except (TypeError, ValueError):
                minimum_needs = None

        if not minimum_needs:
            return -1

        return self.update_minimum_needs(minimum_needs)

    def write_to_file(self, filename):
        """Write minimum needs as json to a file.

        :param filename: The file to be written to.
        :type filename: basestring, str
        """
        if not exists(dirname(filename)):
            return -1
        with open(filename, 'w') as fd:
            needs_json = json.dumps(self.minimum_needs)
            fd.write(needs_json)
        return 0

    @staticmethod
    def remove_file(filename):
        """Remove a minimum needs file.

        :param filename: The file to be removed.
        :type filename: basestring, str
        """
        if not exists(dirname(filename)):
            return -1
        try:
            remove(filename)
        except OSError:
            return -1
        return 0
