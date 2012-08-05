from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layers
from safe.impact_functions.styles import earthquake_fatality_style as style_info
from safe.storage.raster import Raster
import numpy


class EarthquakeFatalityFunction(FunctionProvider):
    """Risk plugin for earthquake damage

    :author Allen
    :rating 1
    :param requires category=='hazard' and \
                subcategory.startswith('earthquake') and \
                layertype=='raster' and \
                unit=='MMI'

    :param requires category=='exposure' and \
                subcategory.startswith('population') and \
                layertype=='raster'
    """

    @staticmethod
    def run(layers,
            a=0.97429, b=11.037):
        """Risk plugin for earthquake fatalities

        Input
          layers: List of layers expected to contain
              H: Raster layer of MMI ground shaking
              P: Raster layer of population data on the same grid as H
        """

        # Identify input layers
        intensity = get_hazard_layer(layers)

        # Get population and gender ratio
        population = gender_ratio = None
        for layer in get_exposure_layers(layers):
            keywords = layer.get_keywords()

            if 'datatype' not in keywords:
                population = layer
            else:
                datatype = keywords['datatype']

                if not 'ratio' in datatype:
                    population = layer
                else:
                    # 'female' in datatype and 'ratio' in datatype:
                    gender_ratio_unit = keywords['unit']

                    msg = ('Unit for gender ratio must be either '
                           '"percent" or "ratio"')
                    if gender_ratio_unit not in ['percent', 'ratio']:
                        raise RuntimeError(msg)

                    gender_ratio = layer

        msg = 'No population layer was found in: %s' % str(layers)
        if population is None:
            raise RuntimeError(msg)

        # Extract data
        H = intensity.get_data(nan=0)
        P = population.get_data(nan=0)
        #print
        #print 'Population', population.get_name()

        # Calculate impact
        F = 10 ** (a * H - b) * P

        if gender_ratio is not None:
            # Extract gender ratio at each pixel (as ratio)
            G = gender_ratio.get_data(nan=0)
            if gender_ratio_unit == 'percent':
                G /= 100

            # Calculate breakdown
            P_female = P * G
            P_male = P - P_female

            F_female = F * G
            F_male = F - F_female

        # Generate text with result for this study
        count = numpy.nansum(F.flat)
        total = numpy.nansum(P.flat)

        # Create report
        impact_summary = ('<table border="0" width="320px">'
                   '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                   % ('Jumlah Penduduk', int(total)))
        if gender_ratio is not None:
            impact_summary += ('        <tr><td>%s&#58;</td><td>%i</td></tr>'
                        % (' - Wanita', int(numpy.nansum(P_female.flat))))
            impact_summary += ('        <tr><td>%s&#58;</td><td>%i</td></tr>'
                        % (' - Pria', int(numpy.nansum(P_male.flat))))
        impact_summary += ('   <tr><td>%s&#58;</td><td>%i</td></tr>'
                    % ('Perkiraan Orang Meninggal', int(count)))

        if gender_ratio is not None:
            impact_summary += ('        <tr><td>%s&#58;</td><td>%i</td></tr>'
                        % (' - Wanita', int(numpy.nansum(F_female.flat))))
            impact_summary += ('        <tr><td>%s&#58;</td><td>%i</td></tr>'
                        % (' - Pria', int(numpy.nansum(F_male.flat))))

        impact_summary += '</table>'

        # Create new layer and return
        R = Raster(F,
                   projection=population.get_projection(),
                   geotransform=population.get_geotransform(),
                   name='Estimated fatalities',
                   keywords={'impact_summary': impact_summary})
                   #style_info=style_info)  # See issue #126
        return R
