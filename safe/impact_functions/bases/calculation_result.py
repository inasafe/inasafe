# coding=utf-8
from safe.common.exceptions import NoImpactClassFoundError

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/05/15'


class VectorImpactCalculation(object):
    """Class to store impact function calculation results.

    """
    def __init__(self):
        self._impact_map = None
        self._hazard_map = None
        self._impacted_count = None
        self._total_count = None
        self._impact_layer = None

    @property
    def hazard_map(self):
        return self._hazard_map

    @hazard_map.setter
    def hazard_map(self, value):
        """The classified hazard map by hazard type.

        Only valid for Classified Hazard.
        :param value: The dictionary of the classified hazard
        :type value: dict
        """
        self._hazard_map = value

    @property
    def impact_map(self):
        return self._impact_map

    @impact_map.setter
    def impact_map(self, value):
        """The classified impact map by exposure type.

        Only valid for Classified Exposure
        :param value: The dictionary of the calculation results
        :type value: dict
        """
        self._impact_map = value

    @property
    def impacted_count(self):
        return self._impacted_count

    @impacted_count.setter
    def impacted_count(self, value):
        """
        :param value: The number of object impacted
        :type value: int
        """
        self._impacted_count = value

    @property
    def total_count(self):
        return self._total_count

    @total_count.setter
    def total_count(self, value):
        self._total_count = value

    @property
    def impact_layer(self):
        return self._impact_layer

    @impact_layer.setter
    def impact_layer(self, value):
        self._impact_layer = value

    def get_hazard_by_class(self, requested_class):
        if requested_class in self.hazard_map:
            return self.hazard_map[requested_class]
        else:
            message = 'The requested hazard class %s is not exists' % (
                requested_class)
            raise NoImpactClassFoundError(message)

    def get_impacted_by_class(self, requested_class):
        if requested_class in self.impact_map:
            return self.impact_map[requested_class]['impacted']
        else:
            message = 'The requested impacted class %s is not exists' % (
                requested_class)
            raise NoImpactClassFoundError(message)

    def get_total_by_class(self, requested_class):
        if requested_class in self.impact_map:
            return self.impact_map[requested_class]['total']
        else:
            message = 'The requested impacted class %s is not exists' % (
                requested_class)
            raise NoImpactClassFoundError(message)
