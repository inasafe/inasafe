from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from impact_functions.core import get_question
from impact_functions.styles import earthquake_fatality_style as style_info
from storage.raster import Raster
from storage.utilities import ugettext as _
from impact_functions.tables import Table, TableRow
from engine.numerics import normal_cdf

import numpy


class ITBFatalityFunction(FunctionProvider):
    """Indonesian Earthquake Fatality Model

    This model was developed by Institut Tecknologi Bandung (ITB) and
    implemented by Dr Hadi Ghasemi, Geoscience Australia


    Reference:

    Indonesian Earthquake Building-Damage and Fatality Models and
    Post Disaster Survey Guidelines Development,
    Bali, 27-28 February 2012, 54pp.


    Algorithm:

    In this study, the same functional form as Allen (2009) is adopted
    to express fatality rate as a function of intensity (see Eq. 10 in the
    report). The Matlab built-in function (fminsearch) for  Nelder-Mead
    algorithm is used to estimate the model parameters. The objective
    function (L2G norm) that is minimised during the optimisation is the
    same as the one used by Jaiswal et al. (2010).

    The coefficients used in the indonesian model are
    x=0.62275231, y=8.03314466, zeta=2.15

    Allen, T. I., Wald, D. J., Earle, P. S., Marano, K. D., Hotovec, A. J.,
    Lin, K., and Hearne, M., 2009. An Atlas of ShakeMaps and population
    exposure catalog for earthquake loss modeling, Bull. Earthq. Eng. 7,
    701-718.

    Jaiswal, K., and Wald, D., 2010. An empirical model for global earthquake
    fatality estimation, Earthq. Spectra 26, 1017-1037.


    Caveats and limitations:

    The current model is the result of the above mentioned workshop and
    reflects the best available information. However, the current model
    has a number of issues listed below and is expected to evolve further
    over time.

    1 - The model is based on limited number of observed fatality
        rates during 4 past fatal events.
    2 - The model clearly over-predicts the fatality rates at
        intensities higher than VIII.
    3 - The model only estimates the expected fatality rate for a given
        intensity level; however the associated uncertainty for the proposed
        model is not addressed.
    4 - There are few known mistakes in developing the current model:
        - rounding MMI values to the nearest 0.5,
        - Implementing Finite-Fault models of candidate events, and
        - consistency between selected GMPEs with those in use by BMKG.
          These issues will be addressed by ITB team in the final report.


    :author Hadi Ghasemi
    :rating 3

    :param requires category == 'hazard' and \
                    subcategory == 'earthquake' and \
                    layertype == 'raster' and \
                    unit == 'MMI'

    :param requires category == 'exposure' and \
                    subcategory == 'population' and \
                    layertype == 'raster'

    """

    plugin_name = _('Be affected by ground shaking')

    def run(self, layers,
            x=0.62275231, y=8.03314466, zeta=2.15):
        """Indonesian Earthquake Fatality Model

        Input
          layers: List of layers expected to contain
              H: Raster layer of MMI ground shaking
              P: Raster layer of population density

        """

        # Extract input layers
        intensity = get_hazard_layer(layers)
        population = get_exposure_layer(layers)

        question = get_question(intensity.get_name(),
                                population.get_name(),
                                self.plugin_name.lower())

        # Extract data grids
        H = intensity.get_data()   # Ground Shaking
        P = population.get_data()  # Population Density

        # Calculate population affected by each MMI level
        # FIXME (Ole): this range is 2-9. Should 10 be included?
        mmi_range = range(2, 10)
        number_exposed = {}
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
            number_exposed[mmi] = numpy.nansum(I.flat)
            number_of_fatalities[mmi] = numpy.nansum(F.flat)

        # Set resulting layer to zero when less than a threshold. This is to
        # try to achieve transparency (see issue #126) - but doesn't
        # seem to work.
        R[R < 0.01] = 0

        # Total statistics
        total = numpy.nansum(P.flat)

        # This might be reported in real time system as well
        fatalities = numpy.nansum(number_of_fatalities.values())

        # Generate impact report
        table_body = [question,
                      TableRow([_('Groundshaking (MMI)'),
                                _('# people impacted')],
                                header=True)]

        # Table of people exposed to each shake level
        for mmi in mmi_range:
            s = str(int(number_exposed[mmi])).rjust(10)
            #print s, len(s)
            row = TableRow([mmi, s],
                           col_align=['right', 'right'])

            # FIXME (Ole): Weirdly enought, the row object
            # has align="right" in it, but it doesn't work
            #print row
            table_body.append(row)

        # Add total fatality estimate
        s = str(int(fatalities)).rjust(10)
        table_body.append(TableRow([_('Number of fatalities'), s],
                                   header=True))
        table_body.append(TableRow(_('Notes:'), header=True))

        # FIXME (Ole): Need proper reference from Hadi
        table_body.append(_('Fatality model is from '
                            'Institute of Teknologi Bandung 2012.'))

        impact_summary = Table(table_body).toNewlineFreeString()
        impact_table = impact_summary
        map_title = _('Earthquake impact to population')

        # Create new layer and return
        L = Raster(R,
                   projection=population.get_projection(),
                   geotransform=population.get_geotransform(),
                   keywords={'impact_summary': impact_summary,
                             'total_population': total,
                             'total_fatalities': fatalities,
                             'impact_table': impact_table,
                             'map_title': map_title},
                   name=_('Estimated fatalities'),
                   style_info=style_info)

        # Maybe return a shape file with contours instead
        return L
