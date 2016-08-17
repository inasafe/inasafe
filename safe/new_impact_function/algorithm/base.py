__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'base'
__date__ = '8/16/16'
__copyright__ = 'imajimatika@gmail.com'


class BaseAlgorithm(object):

    def __init__(self, **kwargs):
        """Initialize"""
        self.hazard = kwargs.get('hazard')
        self.exposure = kwargs.get('exposure')
        self.aggregation = kwargs.get('aggregation')
        self.extent = kwargs.get('extent')
        self.hazard_field = kwargs.get('hazard_field')
        self.aggregation_field = kwargs.get('aggregation_field')

    def run(self):
        """Run the algorithm

        :returns: Vector layer.
        :rtype: QgsVectorLayer
        """
        return self.exposure