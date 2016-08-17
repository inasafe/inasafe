__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'point'
__date__ = '8/16/16'
__copyright__ = 'imajimatika@gmail.com'


from qgis.core import QgsVectorLayer
from safe.new_impact_function.algorithm.base import BaseAlgorithm


class PointAlgorithm(BaseAlgorithm):
    # Algorithm name : saga:addpolygonattributestopoints
    def run(self):
        """Run the algorithm"""
        result = self.run_processing_algorithm(
            'saga:addpolygonattributestopoints',
            self.exposure,
            self.hazard,
            self.original_hazard_field,
            None
        )
        impact_layer = QgsVectorLayer(
            result['OUTPUT'], 'impact', 'ogr')

        return impact_layer
