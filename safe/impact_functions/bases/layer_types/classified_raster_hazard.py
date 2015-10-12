# coding=utf-8

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '07/05/15'


class ClassifiedRasterHazardMixin(object):

    def __init__(self):
        self._hazard_class_mapping = None

    @property
    def hazard_class_mapping(self):
        return self._hazard_class_mapping

    @hazard_class_mapping.setter
    def hazard_class_mapping(self, value):
        self._hazard_class_mapping = value
