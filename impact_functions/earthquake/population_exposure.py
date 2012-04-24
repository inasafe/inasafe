from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.raster import Raster
import numpy


class EarthquakePopulationExposureFunction(FunctionProvider):
    """Population Exposure to ground shaking

    :author Ole Nielsen
    :rating 3
    :param requires category=='hazard' and \
                subcategory.startswith('earthquake') and \
                layertype=='raster' and \
                unit=='MMI'

    :param requires category=='exposure' and \
                subcategory.startswith('population') and \
                layertype=='raster'
    """

    @staticmethod
    def run(layers):
        """Calculate population exposed to different levels of ground shaking

        Input
          layers: List of layers expected to contain
              H: Raster layer of MMI ground shaking
              P: Raster layer of population density
        """

        # Identify input layers
        intensity = get_hazard_layer(layers)
        population = get_exposure_layer(layers)

        # Extract data
        H = intensity.get_data(nan=0)
        P = population.get_data(nan=0)

        # Calculate exposure to MMI impact
        mmi_classes = range(1, 11)  # MMI classes considered (1-10)

        # Form result as keyword strings
        mmi_str = str(mmi_classes)[1:-1]  # Get rid of []
        count_str = ''

        for i in mmi_classes:
            # Identify cells where MMI is in class i
            mask = (H >= i - 0.5) * (H < i + 0.5)

            # Count population affected by this shake level
            count = round(numpy.nansum(P[mask]))
            if numpy.isnan(count):
                count = 0

            # Update keyword string
            count_str += '%i ' % count

        # Calculate fatality map (FIXME (Ole): Need to replaced by USGS model)
        a = 0.97429
        b = 11.037
        F = 10 ** (a * H - b) * P

        # Generate text with result for this study
        count = numpy.nansum(F.flat)
        total = numpy.nansum(P.flat)

        # Create report
        impact_summary = ('<table border="0" width="320px">'
                   '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                   '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                   '</table>' % ('Jumlah Penduduk', int(total),
                                 'Perkiraan Orang Meninggal', int(count)))

        # Create new layer and return
        R = Raster(F,
                   projection=population.get_projection(),
                   geotransform=population.get_geotransform(),
                   name='Estimated fatalities',
                   keywords={'impact_summary': impact_summary,
                             'mmi-classes': mmi_str,
                             'affected-population': count_str})
        return R
