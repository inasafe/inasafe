import numpy

from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.raster import Raster


class VolcanoPopulationImpactFunction(FunctionProvider):
    """Risk plugin for flood impact

    :author HKV
    :rating 1
    :param requires category=='hazard' and \
                    subcategory=='volcanic' and \
                    layertype=='raster'

    :param requires category=='exposure' and \
                    subcategory=='population' and \
                    layertype=='raster'
    """

    plugin_name = 'Might be subject to high volcano hazard'

    @staticmethod
    def run(layers):
        """Risk plugin for volcano population impact

        Input
          layers: List of layers expected to contain
              H: Raster layer of volcanic hazard level
              P: Raster layer of population data on the same grid as H
        """

        # Identify hazard and exposure layers
        # Volcanic hazard level [0-1]
        volcanic_hazard_level = get_hazard_layer(layers)
        population = get_exposure_layer(layers)  # Density [people/area]

        # Extract data as numeric arrays
        V = volcanic_hazard_level.get_data(nan=0.0)
        # Population density
        P = population.get_data(nan=0.0, scaling=True)

        # Calculate impact as population exposed to depths > threshold
        I = numpy.where(V > 2.0 / 3, P, 0)

        # Generate text with result for this study
        number_of_people_affected = numpy.nansum(I.flat)
        impact_summary = ('%i people affected by volcanic hazard level greater'
                          ' than 0.667' % number_of_people_affected)

        # Create raster object and return
        R = Raster(I,
                   projection=volcanic_hazard_level.get_projection(),
                   geotransform=volcanic_hazard_level.get_geotransform(),
                   name='People affected',
                   keywords={'impact_summary': impact_summary})
        return R
