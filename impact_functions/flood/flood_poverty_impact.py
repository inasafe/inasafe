import numpy
from numpy import nansum as sum
from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.raster import Raster


class FloodPovertyImpactFunction(FunctionProvider):
    """Risk plugin for flood poverty impact

    :author HKV
    :rating 1
    :param requires category=='hazard' and \
                    subcategory.startswith('flood') and \
                    layertype=='raster' and \
                    unit=='m'

    :param requires category=='exposure' and \
                    subcategory.startswith('population') and \
                    layertype=='raster' and \
                    datatype=='households'
    """

    plugin_name = 'Dalam bahaya'

    @staticmethod
    def run(layers):
        """Risk plugin for earthquake fatalities

        Input
          layers: List of layers expected to contain
              H: Raster layer of flood depth
              P: Raster layer of poor household density on the same grid as H
        """

        # Depth above which people are regarded affected [m]
        threshold = 1.0

        # Identify hazard and exposure layers
        inundation = get_hazard_layer(layers)  # Flood inundation [m]
        poor_households = get_exposure_layer(layers)  # Poverty density

        # Extract data as numeric arrays
        D = inundation.get_data(nan=0.0)  # Depth

        # This is the new generic way of scaling (issue #168 and #172)
        P = poor_households.get_data(nan=0.0, scaling=True)
        I = numpy.where(D > threshold, P, 0)

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
                   #% ('Jumlah Rumah Tangga Miskin', total))

        caption += ('   <tr><td><b>%s&#58;</b></td>'
                    '<td align="right"><b>%s</b></td></tr>'
                    % ('Jumlah Rumah Tangga Terdampak (x 1000)', count))

        caption += '</table>'

        caption += '<br>'  # Blank separation row
        caption += '<b>Catatan&#58;</b><br>'
        caption += '- Jumlah Rumah Tangga Miskin %s<br>' % total
        caption += '- Jumlah dalam ribuan<br>'
        caption += ('- Rumah Tangga Miskin dalam bahaya ketika '
                    'banjir lebih dari %.1f m. ' % threshold)

        # Create raster object and return
        R = Raster(I,
                   projection=inundation.get_projection(),
                   geotransform=inundation.get_geotransform(),
                   name='People affected',
                   keywords={'caption': caption})
        return R
