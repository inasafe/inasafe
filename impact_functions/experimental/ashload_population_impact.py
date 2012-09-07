import numpy

from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.raster import Raster


class TephraPopulationImpactFunction(FunctionProvider):
    """Risk plugin for flood impact

    :author HKV
    :rating 1
    :param requires category=='hazard' and \
                    subcategory.startswith('tephra') and \
                    layertype=='raster' and \
                    unit=='kg/m^2'

    :param requires category=='exposure' and \
                    subcategory.startswith('population') and \
                    layertype=='raster'
    """

    @staticmethod
    def run(layers):
        """Risk plugin for earthquake fatalities

        Input
          layers: List of layers expected to contain
              H: Raster layer of flood depth
              P: Raster layer of population data on the same grid as H
        """

        threshold = 1  # Load above which people are regarded affected [kg/m2]

        # Identify hazard and exposure layers
        inundation = get_hazard_layer(layers)    # Tephra load [kg/m2]
        population = get_exposure_layer(layers)  # Density [people/km^2]

        # Extract data as numeric arrays
        D = inundation.get_data(nan=0.0)  # Depth
        P = population.get_data(nan=0.0, scaling=True)  # Population density

        # Calculate impact as population exposed to depths > threshold
        I = numpy.where(D > threshold, P, 0)

        # Generate text with result for this study
        number_of_people_affected = numpy.nansum(I.flat)
        impact_summary = ('%i people affected by ash levels greater '
                   'than %i kg/m^2' % (number_of_people_affected,
                                       threshold))

        # Create raster object and return
        R = Raster(I,
                   projection=inundation.get_projection(),
                   geotransform=inundation.get_geotransform(),
                   name='People affected',
                   keywords={'impact_summary': impact_summary})
        return R
