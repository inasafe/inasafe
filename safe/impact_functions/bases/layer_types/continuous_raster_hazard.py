# coding=utf-8

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '28/05/15'


class ContinuousRasterHazardMixin(object):

    def __init__(self):
        self._hazard_threshold = None

    @property
    def hazard_threshold(self):
        return self._hazard_threshold

    @hazard_threshold.setter
    def hazard_threshold(self, value):
        self._hazard_threshold = value
