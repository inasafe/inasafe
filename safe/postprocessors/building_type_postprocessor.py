# -*- coding: utf-8 -*-
"""**Postprocessors package.**

"""

__author__ = 'Marco Bernasocchi <marco@opengis.ch>'
__revision__ = '$Format:%H$'
__date__ = '10/10/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'


from safe.postprocessors.abstract_postprocessor import AbstractPostprocessor

from safe.common.utilities import ugettext as tr


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
        self.type_fields = None
        self.valid_type_fields = ['AMENITY', 'TYPE']
        self.fields_values = {'Hospitals': ['medical', 'clinic', 'hospital'],
                      'Places of worship': ['place_of_worship'],
                      'Schools': ['school']}

    def description(self):
        """Describe briefly what the post processor does.

        Args:
            None

        Returns:
            Str the translated description

        Raises:
            Errors are propagated
        """
        return tr('Calculates building types related statistics.')

    def setup(self, params):
        """concrete implementation it takes care of the needed parameters being
         initialized

        Args:
            params: dict of parameters to pass to the post processor
        Returns:
            None
        Raises:
            None
        """
        AbstractPostprocessor.setup(self, None)
        if (self.impact_total is not None or
           self.impact_attrs is not None or
           self.target_field is not None or
           self.type_fields is not None):
            self._raise_error('clear needs to be called before setup')

        self.impact_total = params['impact_total']
        self.impact_attrs = params['impact_attrs']
        self.target_field = params['target_field']

        #find which attribute field has to be used
        self.type_fields = []
        try:
            for key in self.impact_attrs[0].iterkeys():
                if key in self.valid_type_fields:
                    self.type_fields.append(key)
        except IndexError:
            pass

        if len(self.type_fields) == 0:
            self.type_fields = None

        #there are no features in this postprocessing polygon
        if self.impact_attrs == []:
            self.noFeatures = True
        else:
            self.noFeatures = False
#        self._log_message('BuildingType postprocessor, using field: %s' %
#                          self.type_field)

    def process(self):
        """concrete implementation it takes care of the needed parameters being
         available and performs all the indicators calculations

        Args:
            None
        Returns:
            None
        Raises:
            None
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
        """concrete implementation it takes care of the needed parameters being
         properly cleared

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        AbstractPostprocessor.clear(self)
        self.impact_total = None
        self.impact_attrs = None
        self.target_field = None
        self.type_fields = None

    def _calculate_total(self):
        """Indicator that shows total population.

        this indicator reports the total population

        Args:
            None
        Returns:
            None
        Raises:
            None
        """

        myName = tr('Total')
        if self.target_field is not None:
            myName = '%s %s' % (myName, tr(self.target_field).lower())

        myResult = self.impact_total
        try:
            myResult = int(round(myResult))
        except ValueError:
            myResult = self.NO_DATA_TEXT
        self._append_result(myName, myResult)

    def _calculate_type(self, title, fields_values):
        """Indicator that shows total population.

        this indicator reports the building by type. the logic is:
        - look for the fields that occurs with a name included in
        self.valid_type_fields
        - look in those fields for any of the values of self.fields_values
        - if a record has one of the valid fields with one of the valid
        fields_values then it is considered affected

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myName = tr(title)
        if self.target_field is not None:
            myName = '%s %s' % (myName, tr(self.target_field).lower())

        myResult = 0
        if self.type_fields is not None:
            try:
                for building in self.impact_attrs:
                    for type_field in self.type_fields:
                        if building[type_field] in fields_values:
                            myResult += building[self.target_field]
                            break

                myResult = int(round(myResult))
            except (ValueError, KeyError):
                myResult = self.NO_DATA_TEXT
        else:
            if self.noFeatures:
                myResult = 0
            else:
                myResult = self.NO_DATA_TEXT
        self._append_result(myName, myResult)
