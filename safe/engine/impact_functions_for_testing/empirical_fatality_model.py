import numpy

from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.storage.raster import Raster
from safe.common.numerics import normal_cdf


class EmpiricalFatalityFunction(FunctionProvider):
    """Risk plugin for earthquake damage based on empirical results

    :author Hadi Ghasemi
    :rating 2

    :param requires category=='doesnotexist'
    :param requires title=='neverwas'
    """

    @staticmethod
    def run(layers,
            teta=14.05, beta=0.17):  # zeta=2.15):
        """Risk plugin for earthquake fatalities

        Input
          H: Numerical array of hazard data
          E: Numerical array of exposure data
        """

        # Suppress warnings about invalid value in multiply and divide zero
        # http://comments.gmane.org/gmane.comp.python.numeric.general/43218
        # http://docs.scipy.org/doc/numpy/reference/generated/numpy.seterr.html
        old_numpy_setting = numpy.seterr(invalid='ignore')
        numpy.seterr(divide='ignore')

        # Identify input layers
        intensity = get_hazard_layer(layers)
        population = get_exposure_layer(layers)

        # Extract data
        H = intensity.get_data(nan=0)
        P = population.get_data(nan=0)

        # Calculate impact
        logHazard = 1 / beta * numpy.log(H / teta)

        # Convert array to be standard floats expected by cdf
        arrayout = numpy.array([[float(value) for value in row]
                               for row in logHazard])
        x = arrayout * P
        F = normal_cdf(x)

        numpy.seterr(**old_numpy_setting)

        # Create new layer and return
        R = Raster(F,
                   projection=population.get_projection(),
                   geotransform=population.get_geotransform(),
                   name='Estimated fatalities')
        return R
