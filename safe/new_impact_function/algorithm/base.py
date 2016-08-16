__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'base'
__date__ = '8/16/16'
__copyright__ = 'imajimatika@gmail.com'


class BaseAlgorithm(object):

    def __init__(self, hazard, exposure, aggregation, extent):
        """Initialize

        :param hazard: The hazard layer.
        :type hazard: QgsMapLayer

        :param exposure:
        :type exposure: QgsMapLayer

        :param aggregation:
        :type aggregation: QgsMapLayer

        :param extent: The extent
        :type extent: QgsRectangle
        """
        self.hazard = hazard
        self.exposure = exposure
        self.aggregation = aggregation
        self.extent = extent

    def run(self):
        """Run the algorithm

        :returns: Vector layer.
        :rtype: QgsVectorLayer
        """
        return self.exposure