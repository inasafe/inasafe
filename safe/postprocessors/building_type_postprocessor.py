# -*- coding: utf-8 -*-
"""**Postprocessors package.**

"""

__author__ = 'Marco Bernasocchi <marco@opengis.ch>'
__revision__ = '$Format:%H$'
__date__ = '10/10/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import itertools

from safe.postprocessors.abstract_postprocessor import AbstractPostprocessor

from safe.common.utilities import (
    ugettext as tr,
    OrderedDict)


class BuildingTypePostprocessor(AbstractPostprocessor):
    """
    Postprocessor that calculates building types related statistics.
    see the _calculate_* methods to see indicator specific documentation

    see :mod:`safe.defaults` for default values information
    """

    def __init__(self):
        """
        Constructor for postprocessor class,
        It takes care of defining self.impact_total
        """
        AbstractPostprocessor.__init__(self)
        self.impact_total = None
        self.impact_attrs = None
        self.target_field = None
        self.no_features = None
        self.type_fields = None
        self.valid_type_fields = None
        self.fields_values = OrderedDict([
            ('Medical', ['Clinic/Doctor', 'Hospital']),
            ('Schools', ['School', 'University/College', ]),
            ('Places of worship', ['Place of Worship - Unitarian',
                                   'Place of Worship - Islam',
                                   'Place of Worship - Buddhist',
                                   'Place of Worship']),
            ('Residential', ['Residential']),
            ('Government', ['Government']),
            ('Public Building', ['Public Building']),
            ('Fire Station', ['Fire Station']),
            ('Police Station', ['Police Station']),
            ('Supermarket', ['Supermarket']),
            ('Commercial', ['Commercial']),
            ('Industrial', ['Industrial']),
            ('Utility', ['Utility']),
            ('Sports Facility', ['Sports Facility']),
            ('Other', [])])

        self.known_types = []
        self._update_known_types()

    def description(self):
        """Describe briefly what the post processor does.

        :returns: The translated description.
        :rtype: str
        """
        return tr('Calculates building types related statistics.')

    def setup(self, params):
        """concrete implementation it takes care of the needed parameters being
         initialized

        :param params: dict of parameters to pass to the post processor
        """
        AbstractPostprocessor.setup(self, None)
        if (self.impact_total is not None or
                self.impact_attrs is not None or
                self.target_field is not None or
                self.valid_type_fields is not None or
                self.type_fields is not None):
            self._raise_error('clear needs to be called before setup')

        self.impact_total = params['impact_total']
        self.impact_attrs = params['impact_attrs']
        self.target_field = params['target_field']
        self.valid_type_fields = params['key_attribute']

        #find which attribute field has to be used
        self.type_fields = []
        try:
            for key in self.impact_attrs[0].iterkeys():
                if key.lower() in self.valid_type_fields:
                    self.type_fields.append(key)
        except IndexError:
            pass

        if len(self.type_fields) == 0:
            self.type_fields = None

        self.no_features = False
        #there are no features in this postprocessing polygon
        if self.impact_attrs == []:
            self.no_features = True

    def process(self):
        """Concrete implementation that performs all indicators calculations.
        """
        AbstractPostprocessor.process(self)

        if (self.impact_total is None or
                self.impact_attrs is None or
                self.target_field is None):
            self._log_message('%s not all params have been correctly '
                              'initialized, setup needs to be called before '
                              'process. Skipping this postprocessor'
                              % self.__class__.__name__)
        else:
            self._calculate_total()
            for title, field_values in self.fields_values.iteritems():
                self._calculate_type(title, field_values)

    def clear(self):
        """concrete implementation that ensures needed parameters are cleared.
        """
        AbstractPostprocessor.clear(self)
        self.impact_total = None
        self.impact_attrs = None
        self.target_field = None
        self.type_fields = None
        self.valid_type_fields = None

    def _calculate_total(self):
        """Indicator that shows total population.

        This indicator reports the total population.
        """

        name = tr('Total')
        if self.target_field is not None:
            name = '%s %s' % (name, tr(self.target_field).lower())

        result = self.impact_total
        try:
            result = int(round(result))
        except ValueError:
            result = self.NO_DATA_TEXT
        self._append_result(name, result)

    def _calculate_type(self, title, fields_values):
        """Indicator that shows total population.

        this indicator reports the building by type. the logic is:
        - look for the fields that occurs with a name included in
        self.valid_type_fields
        - look in those fields for any of the values of self.fields_values
        - if a record has one of the valid fields with one of the valid
        fields_values then it is considered affected
        """

        title = tr(title)
        if self.target_field is not None:
            title = '%s %s' % (title, tr(self.target_field).lower())

        result = 0
        if self.type_fields is not None:
            try:
                for building in self.impact_attrs:
                    for type_field in self.type_fields:
                        building_type = building[type_field]
                        if building_type in fields_values:
                            result += building[self.target_field]
                            break
                        elif self._is_unknown_type(building_type):
                            self._update_known_types(building_type)

                result = int(round(result))
            except (ValueError, KeyError):
                result = self.NO_DATA_TEXT
        else:
            if self.no_features:
                result = 0
            else:
                result = self.NO_DATA_TEXT
        self._append_result(title, result)

    def _is_unknown_type(self, building_type):
        """check if the given type is in any of the known_types dictionary

        :param building_type: the name of the type
        :type building_type: str

        :returns: Flag indicating if the building_type is unknown
        :rtype: boolean
        """

        is_unknown = building_type not in self.known_types
        return is_unknown

    def _update_known_types(self, building_type=None):
        """
        Adds a building_type (if passed) and updates the known_types list

        this is called each time a new unknown type is found and is needed so
        that self._is_unknown_type (which is called many times) to perform
        only a simple 'in' check

        :param building_type: the name of the type to add to the known types
        :type building_type: str
        """
        if type is not None:
            self.fields_values['Other'].append(building_type)

        # flatten self.fields_values.values()
        # using http://stackoverflow.com/questions/5286541/#5286614
        self.known_types = list(itertools.chain.from_iterable(
            itertools.repeat(x, 1) if isinstance(x, str) else x for x in
            self.fields_values.values()))
