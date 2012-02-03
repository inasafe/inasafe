from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.raster import Raster
from engine.numerics import cdf

import numpy


class USGSFatalityFunction(FunctionProvider):
    """Risk plugin for earthquake damage based on empirical results

    :author Hadi Ghasemi
    :rating 2

    :param requires category == 'hazard' and \
                    subcategory == 'earthquake' and \
                    layertype == 'raster' and \
                    unit=='MMI'

    :param requires category == 'exposure' and \
                    subcategory == 'population' and \
                    layertype == 'raster' and \
                    disabled == 'notinuse'
    """

    @staticmethod
    def run(layers,
            teta=14.05, beta=0.17, zeta=2.15):
        """Risk plugin for earthquake fatalities

        Input
          H: Numerical array of hazard data
          E: Numerical array of exposure data

        Algorithm and coefficients are from:

        An Empirical Model for Global Earthquake Fatality Estimation.
        Kishor Jaiswal and David Wald.
        Earthquake Spectra, Volume 26, No. 4, pages 1017-1037, November 2010.


        teta=14.05, beta=0.17, zeta=2.1  # Coefficients for Indonesia.


        """

        # Identify input layers
        intensity = get_hazard_layer(layers)
        population = get_exposure_layer(layers)

        print intensity.get_resolution()
        print population.get_resolution()

        # Extract data
        H = intensity.get_data(nan=0)   # Ground Shaking
        P = population.get_data(nan=0)  # Population Density

        import cPickle
        name = intensity.get_name()
        print name
        fid = open('/home/nielso/population_%s.pck' % name, 'wb')
        cPickle.dump(P, fid)
        fid.close()

        fid = open('/home/nielso/intensity_%s.pck' % name, 'wb')
        cPickle.dump(H, fid)
        fid.close()

        # Calculate population affected by each MMI level
        mmi_range = range(2, 10)
        number_of_people_affected = {}
        for mmi in mmi_range:
            mask = numpy.logical_and(mmi - 0.5 < H,
                                     H <= mmi + 0.5)
            I = numpy.where(mask, P, 0)

            # Generate text with result for this study
            number_of_people_affected[mmi] = numpy.nansum(I.flat)

        # Calculate impact according to equation (1) in the
        # Kishor and Wald 2010
        logHazard = 1 / beta * numpy.log(H / teta)

        # Convert array to be standard floats expected by cdf
        arrayout = numpy.array([[float(value) for value in row]
                               for row in logHazard])
        F = cdf(arrayout * P)

        # Stats
        total = numpy.nansum(P.flat)
        fatalities = numpy.nansum(F)
        print 'Total', total
        print 'Estimated fatalities', fatalities
        print 'Min', numpy.amin(F)
        print 'Max', numpy.amax(F)

        # Generate text with result for this study
        caption = generate_exposure_table(mmi_range,
                                          number_of_people_affected)
        caption += generate_fatality_table(fatalities)

        # Create new layer and return
        R = Raster(F,
                   projection=population.get_projection(),
                   geotransform=population.get_geotransform(),
                   keywords={'caption': caption},
                   name='Estimated fatalities')
        return R


def generate_exposure_table(mmi_range,
                            number_of_people_affected):
    """Helper to make html report
    """

    header = 'Jumlah Orang yg terkena dampak (x1000)'
    caption = ('<font size="3"><table border="0" width="400px">'
               '   <tr><td><b>MMI</b></td><td><b>%s</b></td></tr>'
               % header)

    for mmi in mmi_range:
        caption += ('   <tr><td>%i&#58;</td><td>%i</td></tr>'
                    % (mmi,
                       number_of_people_affected[mmi] / 1000))
    caption += '<tr></tr>'
    caption += '</table></font>'

    return caption


def generate_fatality_table(fatalities):
    """Helper to make html report
    """

    caption = ('<br>'
               '<font size="3"><table border="0" width="300px">'
               '    <tr><td><b>Jumlah Perkiraan Kematian</b></td>'
               '    <td><b>%i</b></td></tr>'
               '</table></font>' % fatalities)
    return caption
