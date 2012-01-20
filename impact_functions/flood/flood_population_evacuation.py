import numpy
from numpy import nansum as sum
from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layers
from storage.raster import Raster


class FloodEvacuationFunction(FunctionProvider):
    """Risk plugin for flood evacuation

    :author HKV
    :rating 1
    :param requires category=='hazard' and \
                    subcategory.startswith('flood') and \
                    layer_type=='raster' and \
                    unit=='m'

    :param requires category=='exposure' and \
                    subcategory.startswith('population') and \
                    layer_type=='raster' and \
                    datatype=='population'
    """

    plugin_name = 'Perlu Evakuasi'

    @staticmethod
    def run(layers):
        """Risk plugin for earthquake fatalities

        Input
          layers: List of layers expected to contain
              H: Raster layer of flood depth
              P: Raster layer of population data on the same grid as H
        """

        # Depth above which people are regarded affected [m]
        threshold = 1.0  # Threshold [m]

        # Identify hazard and exposure layers
        inundation = get_hazard_layer(layers)  # Flood inundation [m]

        # Get population and gender ratio
        population = gender_ratio = None
        for layer in get_exposure_layers(layers):
            keywords = layer.get_keywords()

            if 'datatype' not in keywords:
                population = layer
            else:
                datatype = keywords['datatype']

                if 'population' in datatype:
                    population = layer

                if 'female' in datatype and 'ratio' in datatype:
                    gender_ratio_unit = keywords['unit']

                    msg = ('Unit for gender ratio must be either '
                           '"percent" or "ratio"')
                    assert gender_ratio_unit in ['percent', 'ratio'], msg

                    gender_ratio = layer

        msg = 'No population layer was found in: %s' % str(layers)
        assert population is not None, msg

        # Extract data as numeric arrays
        D = inundation.get_data(nan=0.0)  # Depth

        # Calculate impact as population exposed to depths > threshold
        if population.get_resolution(native=True, isotropic=True) < 0.0005:
            # Keep this for backwards compatibility just a little while
            # This uses the original custom population set and
            # serves as a reference

            P = population.get_data(nan=0.0)  # Population density
            pixel_area = 2500
            I = numpy.where(D > threshold, P, 0) / 100000.0 * pixel_area
        else:
            # This is the new generic way of scaling (issue #168 and #172)
            P = population.get_data(nan=0.0, scaling=True)
            I = numpy.where(D > threshold, P, 0)

        if gender_ratio is not None:
            # Extract gender ratio at each pixel (as ratio)
            G = gender_ratio.get_data(nan=0.0)
            if gender_ratio_unit == 'percent':
                G /= 100

            # Calculate breakdown
            P_female = P * G
            P_male = P - P_female

            I_female = I * G
            I_male = I - I_female

        # Generate text with result for this study
        total = str(int(sum(P.flat) / 1000))
        count = str(int(sum(I.flat) / 1000))

        # Create report
        iname = inundation.get_name()
        pname = poor_households.get_name()
        caption = ('<b>Apabila terjadi "%s" perkiraan dampak terhadap "%s" '
                   'kemungkinan yang terjadi&#58;</b><br><br><p>' % (iname,
                                                                     pname))
        caption += ('<table border="0" width="320px">')
                   #'   <tr><td><b>%s&#58;</b></td>'
                   #'<td align="right"><b>%s</b></td></tr>'
                   #% ('Jumlah Penduduk', total))
        # if gender_ratio is not None:
        #     total_female = str(int(sum(P_female.flat) / 1000))
        #     total_male = str(int(sum(P_male.flat) / 1000))

        #     caption += ('        <tr><td>%s&#58;</td>'
        #                 '<td align="right">%s</td></tr>'
        #                 % (' - Wanita', total_female))
        #     caption += ('        <tr><td>%s&#58;</td>'
        #                 '<td align="right">%s</td></tr>'
        #                 % (' - Pria', total_male))
        #    caption += '<tr><td>&nbsp;</td></tr>'  # Blank separation row

        caption += ('   <tr><td><b>%s&#58;</b></td>'
                    '<td align="right"><b>%s</b></td></tr>'
                    % ('Perlu Evakuasi (x 1000)', count))

        if gender_ratio is not None:
            affected_female = str(int(sum(I_female.flat) / 1000))
            affected_male = str(int(sum(I_male.flat) / 1000))

            caption += ('        <tr><td>%s&#58;</td>'
                        '<td align="right">%s</td></tr>'
                        % (' - Wanita', affected_female))
            caption += ('        <tr><td>%s&#58;</td>'
                        '<td align="right">%s</td></tr>'
                        % (' - Pria', affected_male))

        caption += '</table>'

        caption += '<br>'  # Blank separation row
        caption += '<b>Catatan&#58;</b><br>'
        caption += '- Jumlah penduduk Jakarta %s<br>' % total
        caption += '- Jumlah dalam ribuan<br>'
        caption += ('- Penduduk dianggap perlu dievakuasi ketika '
                    'banjir lebih dari %.1f m.' % threshold)

        # Create raster object and return
        R = Raster(I,
                   projection=inundation.get_projection(),
                   geotransform=inundation.get_geotransform(),
                   name='People evacuated',
                   keywords={'caption': caption})
        return R
