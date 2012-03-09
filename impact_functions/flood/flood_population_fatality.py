import numpy
from numpy import nansum as sum
from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from impact_functions.styles import flood_population_style as style_info
from storage.raster import Raster


class FloodFatalityFunction(FunctionProvider):
    """Risk plugin for flood fatality

    :author HKV
    :rating 1
    :param requires category=='hazard' and \
                    subcategory.startswith('flood') and \
                    layertype=='raster' and \
                    unit=='m'

    :param requires category=='exposure' and \
                    subcategory=='population' and \
                    layertype=='raster' and \
                    datatype=='density'
    """

    plugin_name = 'Meninggal'

    def run(self, layers):
        """Risk plugin for earthquake fatalities

        Input
          layers: List of layers expected to contain
              H: Raster layer of flood depth
              P: Raster layer of population data on the same grid as H
        """

        # Depth above which people are regarded affected [m]
        threshold = 1.5  # Threshold [m]

        # Identify hazard and exposure layers
        inundation = get_hazard_layer(layers)  # Flood inundation [m]
        population = get_exposure_layer(layers)

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

        # Generate text with result for this study
        total = str(int(numpy.sum(P) / 1000))
        count = str(int(numpy.sum(I) / 1000))

        # Create report
        iname = inundation.get_name()
        pname = population.get_name()
        impact_summary = ('<b>Apabila terjadi "%s" perkiraan dampak '
                          'terhadap "%s" kemungkinan yang terjadi&#58;'
                          '</b><br><br><p>' % (iname, pname))
        impact_summary += ('<table border="0" width="320px">')
        impact_summary += ('   <tr><td><b>%s&#58;</b></td>'
                    '<td align="right"><b>%s</b></td></tr>'
                    % ('Meninggal (x 1000)', count))

        impact_summary += '</table>'

        impact_summary += '<br>'  # Blank separation row
        impact_summary += '<b>Catatan&#58;</b><br>'
        impact_summary += '- Jumlah penduduk Jakarta %s<br>' % total
        impact_summary += '- Jumlah dalam ribuan<br>'
        impact_summary += ('- Penduduk dianggap meninggal ketika '
                           'banjir lebih dari %.1f m.' % threshold)

        # Create raster object and return
        R = Raster(I,
                   projection=inundation.get_projection(),
                   geotransform=inundation.get_geotransform(),
                   name='Penduduk yang %s' % (self.plugin_name.lower()),
                   keywords={'impact_summary': impact_summary},
                   style_info=style_info)

        return R
