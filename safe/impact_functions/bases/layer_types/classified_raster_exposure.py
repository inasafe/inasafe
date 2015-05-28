# coding=utf-8
__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '28/05/15'


class ClassifiedRasterExposure(object):

    def __init__(self):
        self._exposure_layer = None

    def set_up_exposure_layer(self, exposure):
        """Set up the hazard value
        :param exposure: QgsRasterLayer or Raster data types
        :type exposure: QgsRasterLayer, Raster
        """
        self._exposure_layer = exposure
