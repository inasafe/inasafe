import numpy
from safe.impact_functions.core import (
    FunctionProvider,
    get_hazard_layer,
    get_exposure_layers)
from safe.storage.raster import Raster
from safe.common.utilities import verify, format_int

# Want to use the human readable name in the impact function
# pylint: disable=E0611
from numpy import nansum
# pylint: enable=E0611


class HKVFloodImpactFunctionTEST(FunctionProvider):
    """Risk plugin for flood impact

    :author HKV
    :rating 1
    :param requires category=='hazard' and \
                    subcategory=='flood' and \
                    layertype=='raster' and \
                    unit=='m'

    :param requires category=='exposure' and \
                    subcategory=='population' and \
                    layertype=='raster' and \
                    datatype=='density'
    """

    plugin_name = 'HKVtest'

    @staticmethod
    def run(layers):
        """Risk plugin for earthquake fatalities

        Input
          layers: List of layers expected to contain
              H: Raster layer of flood depth
              P: Raster layer of population data on the same grid as H
        """

        # Depth above which people are regarded affected [m]
        threshold = 0.1
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

                if 'ratio' not in datatype:
                    population = layer
                else:
                    # if 'female' in datatype and 'ratio' in datatype:
                    gender_ratio_unit = keywords['unit']

                    msg = ('Unit for gender ratio must be either '
                           '"percent" or "ratio"')
                    if gender_ratio_unit not in ['percent', 'ratio']:
                        raise Exception(msg)

                    gender_ratio = layer

        msg = 'No population layer was found in: %s' % str(layers)
        verify(population is not None, msg)

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
        total = format_int(int(nansum(P.flat) / 1000))
        count = format_int(int(nansum(I.flat) / 1000))

        # Create report
        impact_summary = ('<table border="0" width="320px">'
                   '   <tr><td><b>%s&#58;</b></td>'
                   '<td align="right"><b>%s</b></td></tr>'
                   % ('Jumlah Penduduk', total))
        if gender_ratio is not None:
            total_female = format_int(int(nansum(P_female.flat) / 1000))
            total_male = format_int(int(nansum(P_male.flat) / 1000))

            impact_summary += ('        <tr><td>%s&#58;</td>'
                        '<td align="right">%s</td></tr>'
                        % (' - Wanita', total_female))
            impact_summary += ('        <tr><td>%s&#58;</td>'
                        '<td align="right">%s</td></tr>'
                        % (' - Pria', total_male))
            impact_summary += '<tr><td>&nbsp;</td></tr>'  # Blank row

        impact_summary += ('   <tr><td><b>%s&#58;</b></td>'
                    '<td align="right"><b>%s</b></td></tr>'
                    % ('Perkiraan Jumlah Terdampak (> %.1fm)' % threshold,
                       count))

        if gender_ratio is not None:
            affected_female = format_int(int(nansum(I_female.flat) / 1000))
            affected_male = format_int(int(nansum(I_male.flat) / 1000))

            impact_summary += ('        <tr><td>%s&#58;</td>'
                        '<td align="right">%s</td></tr>'
                        % (' - Wanita', affected_female))
            impact_summary += ('        <tr><td>%s&#58;</td>'
                        '<td align="right">%s</td></tr>'
                        % (' - Pria', affected_male))

        impact_summary += '</table>'

        impact_summary += '<br>'  # Blank separation row
        impact_summary += 'Catatan&#58; Semua nomor x 1000'

        # Create raster object and return
        R = Raster(I,
                   projection=inundation.get_projection(),
                   geotransform=inundation.get_geotransform(),
                   name='People affected',
                   keywords={'impact_summary': impact_summary})
        return R
