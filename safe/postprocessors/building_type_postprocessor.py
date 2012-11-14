# -*- coding: utf-8 -*-
"""**Postprocessors package.**

"""

__author__ = 'Marco Bernasocchi <marco@opengis.ch>'
__revision__ = '$Format:%H$'
__date__ = '10/10/2012'
__license__ = "GPL"
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'


from safe.postprocessors.abstract_postprocessor import (
    AbstractPostprocessor)

from safe.common.utilities import ugettext as tr


class BuildingTypePostprocessor(AbstractPostprocessor):
    """
    Postprocessor that calculates age related statistics.
    see the _calculate_* methods to see indicator specific documentation

    see :mod:`safe.defaults` for default values information
    """

    def __init__(self):
        """
        Constructor for AgePostprocessor postprocessor class,
        It takes care of defining self.impact_total
        """
        AbstractPostprocessor.__init__(self)
        self.impact_total = None
        self.impact_attrs = None
        self.target_field = None

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
           self.target_field is not None):
            self._raise_error('clear needs to be called before setup')

        self.impact_total = params['impact_total']
        self.impact_attrs = params['impact_attrs']
        self.target_field = params['target_field']

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
            self._calculate_medical()
            self._calculate_place_of_worship()
            self._calculate_schools()

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

        #FIXME (MB) Shameless hack to deal with issue #368
        if self.impact_total > 8000000000 or self.impact_total < 0:
            self._append_result(myName, self.NO_DATA_TEXT)
            return

        myResult = self.impact_total
        try:
            myResult = int(round(myResult))
        except ValueError:
            myResult = self.NO_DATA_TEXT
        self._append_result(myName, myResult)

    def _calculate_place_of_worship(self):
        """Indicator that shows total population.

        this indicator reports the total population

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myName = tr('Place of worship')
        if self.target_field is not None:
            myName = '%s %s' % (myName, tr(self.target_field).lower())

        #FIXME (MB) Shameless hack to deal with issue #368
        if self.impact_total > 8000000000 or self.impact_total < 0:
            self._append_result(myName, self.NO_DATA_TEXT)
            return

        myResult = 0
        for building in self.impact_attrs:
            if (building[self.target_field] and
                building['amenity'] == 'place_of_worship'):
                myResult += building[self.target_field]

        try:
            myResult = int(round(myResult))
        except ValueError:
            myResult = self.NO_DATA_TEXT
        self._append_result(myName, myResult)

    def _calculate_medical(self):
        """Indicator that shows total population.

        this indicator reports the total population

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myName = tr('Hospitals')
        if self.target_field is not None:
            myName = '%s %s' % (myName, tr(self.target_field).lower())

        #FIXME (MB) Shameless hack to deal with issue #368
        if self.impact_total > 8000000000 or self.impact_total < 0:
            self._append_result(myName, self.NO_DATA_TEXT)
            return

        myResult = 0
        for building in self.impact_attrs:
            if (building[self.target_field] and
                building['amenity'] == 'hospital'):
                myResult += building[self.target_field]

        try:
            myResult = int(round(myResult))
        except ValueError:
            myResult = self.NO_DATA_TEXT
        self._append_result(myName, myResult)

    def _calculate_schools(self):
        """Indicator that shows total population.

        this indicator reports the total population

        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        myName = tr('Schools')
        if self.target_field is not None:
            myName = '%s %s' % (myName, tr(self.target_field).lower())

        #FIXME (MB) Shameless hack to deal with issue #368
        if self.impact_total > 8000000000 or self.impact_total < 0:
            self._append_result(myName, self.NO_DATA_TEXT)
            return

        myResult = 0
        for building in self.impact_attrs:
            if (building[self.target_field] and
                building['amenity'] == 'school'):
                myResult += building[self.target_field]

        try:
            myResult = int(round(myResult))
        except ValueError:
            myResult = self.NO_DATA_TEXT
        self._append_result(myName, myResult)
