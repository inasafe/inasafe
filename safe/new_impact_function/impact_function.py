__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'impact_function'
__date__ = '8/16/16'
__copyright__ = 'imajimatika@gmail.com'

from safe.new_impact_function.algorithm.line import LineAlgorithm
from safe.new_impact_function.algorithm.point import PointAlgorithm
from safe.new_impact_function.algorithm.polygon import PolygonAlgorithm
from safe.new_impact_function.algorithm.raster import RasterAlgorithm
from safe.new_impact_function.algorithm.indivisible_polygon import (
    IndivisiblePolygonAlgorithm
)


class ImpactFunction(object):
    """Impact Function."""

    def __init__(self, hazard, exposure, aggregation, extent):
        self.hazard = hazard
        self.exposure = exposure
        self.aggregation = aggregation
        self.extent = extent

        self.algorithm = None
        self.impact_layer = None

        self.set_algorithm()

    def set_algorithm(self):
        if self.exposure.keyword('layer_mode') == 'raster':
            self.algorithm = RasterAlgorithm
        elif self.exposure.keyword('layer_mode') == 'point':
            self.algorithm = PointAlgorithm
        elif self.exposure.keyword('exposure') == 'structure':
            self.algorithm = IndivisiblePolygonAlgorithm
        elif self.exposure.keyword('layer_mode') == 'line':
            self.algorithm = LineAlgorithm
        else:
            self.algorithm = PolygonAlgorithm

    def preprocess(self):
        """"""
        pass

    def run_algorithm(self):
        algorithm_instance = self.algorithm(
            self.hazard.layer,
            self.exposure.layer,
            self.aggregation.layer,
            self.extent
        )
        self.impact_layer = algorithm_instance.run()
        # Add impact keywords after this


    def post_process(self):
        """"""
        pass

    def run(self):
        pass