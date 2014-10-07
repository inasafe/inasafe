__author__ = 'christian'
from collections import OrderedDict

class MinimumNeeds(object):

    def get_categories(self):
        return [u'resource', u'amount', u'unit', u'frequency', u'provenance']

    def get_need(self, resource):
        for need in self.minimum_needs:
            if need['name'] == resource:
                return need
        return None

    def get_minimum_needs(self):
        minimum_needs = [[r['name'], r['amount']] for r in self.minimum_needs]
        return OrderedDict(minimum_needs)

    def get_full_needs(self):
        return self.minimum_needs

    def set_need(self, resource, amount, units):
        self.minimum_needs.append({
            'name': resource,
            'amount': amount,
            'unit': units
        })

    def update_minimum_needs(self, minimum_needs):
        self.minimum_needs = minimum_needs

    def _defaults(self):
        """Helper to get the default minimum needs.

        .. note:: Key names will be translated.
        """
        rice = 'Rice'
        drinking_water = 'Drinking Water'
        water = 'Water'
        family_kits = 'Family Kits'
        toilets = 'Toilets'
        minimum_needs = [
            {'resource': rice, 'amount': 2.8, 'unit': 'kg',
                'frequency': 'weekly', 'provenance': 'BNPB'},
            {'resource': drinking_water, 'amount': 17.5, 'unit': 'l',
                'frequency': 'weekly', 'provenance': 'BNPB'},
            {'resource': water, 'amount': 67, 'unit': 'l',
                'frequency': 'weekly', 'provenance': 'BNPB'},
            {'resource': family_kits, 'amount': 0.2, 'unit': 'unit',
                'frequency': 'weekly', 'provenance': 'BNPB'},
            {'resource': toilets, 'amount': 0.05, 'unit': 'unit',
                'frequency': 'single', 'provenance': 'BNPB'},
        ]
        return minimum_needs

