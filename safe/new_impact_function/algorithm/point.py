__author__ = 'ismailsunni'
__project_name__ = 'inasafe-dev'
__filename__ = 'point'
__date__ = '8/16/16'
__copyright__ = 'imajimatika@gmail.com'


from qgis.core import QgsVectorLayer
from safe.common.utilities import unique_filename, temp_dir
from safe.new_impact_function.algorithm.base import BaseAlgorithm


class PointAlgorithm(BaseAlgorithm):
    # Algorithm name : saga:addpolygonattributestopoints
    def run(self):
        """Run the algorithm"""
        output_directory = temp_dir(sub_dir='impact_algorithm_result')
        impact_filename = unique_filename(
            suffix='.shp', dir=output_directory)
        result = self.run_processing_algorithm(
            'saga:addpolygonattributestopoints',
            self.exposure,
            self.hazard,
            self.original_hazard_field,
            impact_filename
        )
        print impact_filename
        impact_layer = QgsVectorLayer(
            result['OUTPUT'], 'impact', 'ogr')

        return impact_layer
