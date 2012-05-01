from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.raster import Raster
from engine.numerics import normal_cdf

import numpy


class ITBFatalityFunction(FunctionProvider):
    """Earthquake Fatality Model based on ITB .......sdfaasdfasdfd

    Reference:

    xxxxx
    x
    xxx


    :author Hadi Ghasemi
    :rating 2

    :param requires category == 'hazard' and \
                    subcategory == 'earthquake' and \
                    layertype == 'raster' and \
                    unit == 'MMI'

    :param requires category == 'exposure' and \
                    subcategory == 'population' and \
                    layertype == 'raster'

    """

    @staticmethod
    def run(layers,
            x=0.62275231, y=8.03314466, zeta=2.15):
        """Risk plugin for earthquake fatalities

        Input
          H: Numerical array of hazard data
          E: Numerical array of exposure data

        Algorithm and coefficients are from:
        xxxxxxx

        teta=14.05, beta=0.17, zeta=2.1  # Coefficients for Indonesia.


        """

        # Identify input layers
        intensity = get_hazard_layer(layers)
        population = get_exposure_layer(layers)

        # Extract data grids
        H = intensity.get_data(nan=0)   # Ground Shaking
        P = population.get_data(nan=0)  # Population Density

        # Calculate population affected by each MMI level
        mmi_range = range(2, 10)
        number_of_people_affected = {}
        number_of_fatalities = {}
        
        # START HERE
        # Calculate fatality rates for observed Intensity values (H)
        # based on ITB power model
        FR = numpy.power(10.0,x*H-y)
        for mmi in mmi_range:
            mask = numpy.logical_and(mmi - 0.5 < H,
                                     H <= mmi + 0.5)
            I = numpy.where(mask, P, 0)
            # Calculate expected number of fatalities
            F = FR*I
            # Generate text with result for this study
            number_of_people_affected[mmi] = numpy.nansum(I.flat)
            number_of_fatalities[mmi] = numpy.nansum(F.flat)
            
        # Commented out        
        ## Calculate impact according to ITB model
        #logHazard = 1 / beta * numpy.log(H / teta)

        ## Convert array to be standard floats expected by cdf
        #arrayout = numpy.array([[float(value) for value in row]
        #                       for row in logHazard])
        #F = normal_cdf(arrayout * P)
        

        # Stats
        total = numpy.nansum(P.flat)
        fatalities = numpy.nansum(number_of_fatalities.values())
        print 'Total', total
        print 'Estimated fatalities', fatalities
        print 'Min', numpy.amin(number_of_fatalities.values())
        print 'Max', numpy.amax(number_of_fatalities.values())

        # STOP HERE
        # Generate text with result for this study
        impact_summary = generate_exposure_table(
                            mmi_range, number_of_people_affected)
        impact_summary += generate_fatality_table(fatalities)

        # Create new layer and return
        R = Raster(F,
                   projection=population.get_projection(),
                   geotransform=population.get_geotransform(),
                   keywords={'impact_summary': impact_summary},
                   name='Estimated fatalities')
        return R


def generate_exposure_table(mmi_range,
                            number_of_people_affected):
    """Helper to make html report
    """

    header = 'Jumlah Orang yg terkena dampak (x1000)'
    impact_summary = ('<font size="3"><table border="0" width="400px">'
               '   <tr><td><b>MMI</b></td><td><b>%s</b></td></tr>'
               % header)

    for mmi in mmi_range:
        impact_summary += ('   <tr><td>%i&#58;</td><td>%i</td></tr>'
                    % (mmi,
                       number_of_people_affected[mmi] / 1000))
    impact_summary += '<tr></tr>'
    impact_summary += '</table></font>'

    return impact_summary


def generate_fatality_table(fatalities):
    """Helper to make html report
    """

    impact_summary = ('<br>'
               '<font size="3"><table border="0" width="300px">'
               '    <tr><td><b>Jumlah Perkiraan Kematian</b></td>'
               '    <td><b>%i</b></td></tr>'
               '</table></font>' % fatalities)
    return impact_summary
