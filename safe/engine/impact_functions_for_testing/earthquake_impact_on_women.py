from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.impact_functions.core import get_question
from safe.impact_functions.styles import earthquake_fatality_style
from safe.storage.raster import Raster
from safe.common.tables import Table, TableRow
from safe.common.utilities import ugettext as tr

import numpy


class EarthquakeWomenImpactFunction(FunctionProvider):
    """Earthquake Impact on Women

    This model is proof of concept only and assumes an input dataset
    with gridded counts of females.

    It also assume the existence of the likely ration of pregnancies
    in the female population.

    Some stats are derived from SP2010_agregat_data_perProvinsin.dbf from
    http://dds.bps.go.id/eng/


    :author Ole Nielsen
    :rating 1

    :param requires category=='hazard' and \
                    subcategory=='earthquake' and \
                    layertype=='raster' and \
                    unit=='MMI'

    :param requires category=='exposure' and \
                    subcategory=='population' and \
                    layertype=='raster'

    """

    title = tr('Suffer because of gender')

    def run(self, layers,
            x=0.62275231, y=8.03314466):  # , zeta=2.15):
        """Gender specific earthquake impact model

        Input
          layers: List of layers expected to contain
              H: Raster layer of MMI ground shaking
              P: Raster layer of population density

        """

        # Define percentages of people being displaced at each mmi level
        displacement_rate = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0,
                             7: 0.1, 8: 0.5, 9: 0.75, 10: 1.0}

        # Extract input layers
        intensity = get_hazard_layer(layers)
        population = get_exposure_layer(layers)

        question = get_question(intensity.get_name(),
                                population.get_name(),
                                self)

        # Extract data grids
        H = intensity.get_data()   # Ground Shaking
        P = population.get_data()  # Population Density

        # Calculate population affected by each MMI level
        # FIXME (Ole): this range is 2-9. Should 10 be included?
        mmi_range = range(2, 10)
        number_of_exposed = {}
        number_of_fatalities = {}

        # Calculate fatality rates for observed Intensity values (H
        # based on ITB power model
        R = numpy.zeros(H.shape)
        for mmi in mmi_range:

            # Identify cells where MMI is in class i
            mask = (H > mmi - 0.5) * (H <= mmi + 0.5)

            # Count population affected by this shake level
            I = numpy.where(mask, P, 0)

            # Calculate expected number of fatalities per level
            fatality_rate = numpy.power(10.0, x * mmi - y)
            F = fatality_rate * I

            # Sum up fatalities to create map
            R += F

            # Generate text with result for this study
            # This is what is used in the real time system exposure table
            number_of_exposed[mmi] = numpy.nansum(I.flat)
            number_of_fatalities[mmi] = numpy.nansum(F.flat)

        # Set resulting layer to zero when less than a threshold. This is to
        # achieve transparency (see issue #126).
        R[R < 1] = numpy.nan

        # Total statistics
        total = numpy.nansum(P.flat)

        # Compute number of fatalities
        fatalities = numpy.nansum(number_of_fatalities.values())

        # Compute number of people displaced due to building collapse
        displaced = 0
        for mmi in mmi_range:
            displaced += displacement_rate[mmi] * number_of_exposed[mmi]
        displaced_women = displaced * 0.52  # Could be made province dependent
        displaced_pregnant_women = displaced_women * 0.01387  # CHECK

        # Generate impact report
        table_body = [question]

        # Add total fatality estimate
        s = str(int(fatalities)).rjust(10)
        table_body.append(TableRow([tr('Number of fatalities'), s],
                                   header=True))

        # Add total estimate of people displaced
        s = str(int(displaced)).rjust(10)
        table_body.append(TableRow([tr('Number of people displaced'), s],
                                   header=True))
        s = str(int(displaced_women)).rjust(10)
        table_body.append(TableRow([tr('Number of women displaced'), s],
                                   header=True))
        s = str(int(displaced_pregnant_women)).rjust(10)
        table_body.append(TableRow([tr('Number of pregnant women displaced'),
                                    s],
                                   header=True))

        table_body.append(TableRow(tr('Action Checklist:'), header=True))
        table_body.append(tr('Are enough shelters available for %i women?')
                          % displaced_women)
        table_body.append(tr('Are enough facilities available to assist %i '
                            'pregnant women?') % displaced_pregnant_women)

        table_body.append(TableRow(tr('Notes'), header=True))

        table_body.append(tr('Fatality model is from '
                            'Institute of Teknologi Bandung 2012.'))

        impact_summary = Table(table_body).toNewlineFreeString()
        impact_table = impact_summary
        map_title = tr('Earthquake impact to population')

        # Create new layer and return
        L = Raster(R,
                   projection=population.get_projection(),
                   geotransform=population.get_geotransform(),
                   keywords={'impact_summary': impact_summary,
                             'total_population': total,
                             'total_fatalities': fatalities,
                             'impact_table': impact_table,
                             'map_title': map_title},
                   name=tr('Estimated fatalities'),
                   style_info=earthquake_fatality_style)

        # Maybe return a shape file with contours instead
        return L
