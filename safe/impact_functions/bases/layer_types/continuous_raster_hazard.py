# coding=utf-8

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '28/05/15'


class ContinuousRasterHazardMixin(object):

    def __init__(self):
        self._hazard_threshold = None
        self._hazard_layer = None

    def set_up_hazard_layer(self, hazard):
        """Set up the hazard value.

        :param hazard: QgsRasterLayer or Raster data types
        :type hazard: QgsRasterLayer, Raster
        """
        self._hazard_layer = hazard

    @property
    def hazard_threshold(self):
        return self._hazard_threshold

    @hazard_threshold.setter
    def hazard_threshold(self, value):
        self._hazard_threshold = value
