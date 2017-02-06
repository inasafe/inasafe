# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - ITB Earthquake
Impact Function on Population.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import numpy
import logging

from safe.common.utilities import OrderedDict
from safe.impact_functions.bases.continuous_rh_continuous_re import \
    ContinuousRHContinuousRE
from safe.impact_functions.earthquake.itb_earthquake_fatality_model\
    .metadata_definitions import ITBFatalityMetadata
from safe.impact_functions.core import (
    population_rounding)
from safe.storage.raster import Raster
from safe.common.utilities import (
    humanize_class,
    format_int,
    create_classes,
    create_label)
from safe.utilities.i18n import tr
from safe.gui.tools.minimum_needs.needs_profile import (
    add_needs_parameters,
    filter_needs_parameters
)
from safe.impact_reports.population_exposure_report_mixin import \
    PopulationExposureReportMixin

__author__ = 'lucernae'
__date__ = '24/03/15'

LOGGER = logging.getLogger('InaSAFE')


class ITBFatalityFunction(
        ContinuousRHContinuousRE,
        PopulationExposureReportMixin):
    # noinspection PyUnresolvedReferences
    """Indonesian Earthquake Fatality Model.

    This model was developed by Institut Teknologi Bandung (ITB) and
    implemented by Dr. Hadi Ghasemi, Geoscience Australia.


    Reference:

    Indonesian Earthquake Building-Damage and Fatality Models and
    Post Disaster Survey Guidelines Development,
    Bali, 27-28 February 2012, 54pp.


    Algorithm:

    In this study, the same functional form as Allen (2009) is adopted
    to express fatality rate as a function of intensity (see Eq. 10 in the
    report). The Matlab built-in function (fminsearch) for  Nelder-Mead
    algorithm was used to estimate the model parameters. The objective
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

    Note: Because of these caveats, decisions should not be made solely on
    the information presented here and should always be verified by ground
    truthing and other reliable information sources.
    """

    _metadata = ITBFatalityMetadata()

    def __init__(self):
        super(ITBFatalityFunction, self).__init__()
        PopulationExposureReportMixin.__init__(self)

        # AG: Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)
        self.hardcoded_parameters = OrderedDict([
            ('x', 0.62275231), ('y', 8.03314466),  # Model coefficients
            # Rates of people displaced for each MMI level
            # should be consistent with defined mmi range below. - Hyeuk
            ('displacement_rate', {
                2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0, 6: 1.0,
                7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0
            }),
            # it should be range(2,11) if mmi 10 is included. Otherwise we
            # should remove mmi 10 in the displacement_rate as well - Hyeuk
            ('mmi_range', range(2, 11)),
            ('step', 0.5),
            ('calculate_displaced_people', True)
        ])
        self.total_fatalities = None

    def compute_fatality_rate(self):
        """ITB method to compute fatality rate.
        """
        # As per email discussion with Ole, Trevor, Hadi, mmi < 4 will have
        # a fatality rate of 0 - Tim
        mmi_range = self.hardcoded_parameters['mmi_range']
        x = self.hardcoded_parameters['x']
        y = self.hardcoded_parameters['y']
        fatality_rate = {mmi: 0 if mmi < 4 else numpy.power(10.0, x * mmi - y)
                         for mmi in mmi_range}
        return fatality_rate

    @staticmethod
    def round_to_sum(prob_array):
        """
        Round a list of numbers while maintaining the sum.

        http://stackoverflow.com/questions/792460/
        how-to-round-floats-to-integers-while-preserving-their-sum

        :param prob_array: array
        :type prob_array: list(float)

        :returns: A list of rounded numbers whose sum is equal to the
            sum of the list of input numbers.
        :rtype: list
        """
        nsize = len(prob_array)
        array_sum = int(numpy.sum(prob_array))
        floor_array = numpy.floor(prob_array)
        lower_sum = int(numpy.sum(floor_array))
        diff_dic = dict(enumerate(prob_array - floor_array))

        difference = array_sum - lower_sum

        if difference > 0:
            # array is ordered in such a way that the numbers closest to the
            # next one are at the top.
            sorted_idx = sorted(diff_dic, key=diff_dic.get)
            idx_change = [
                sorted_idx[x] for x in range(nsize - difference, nsize)]
            floor_array[idx_change] += 1

        assert(array_sum == int(numpy.sum(floor_array)))
        return list(floor_array)

    def action_checklist(self):
        """Action checklist for the itb earthquake fatality report.

        :returns: The action checklist
        :rtype: list
        """
        total_fatalities = self.total_fatalities
        total_displaced = self.total_evacuated
        rounded_displaced = format_int(population_rounding(total_displaced))

        fields = super(ITBFatalityFunction, self).action_checklist()
        if total_fatalities:
            fields.append(tr(
                'Are there enough victim identification units available '
                'for %s people?') % (
                    format_int(population_rounding(total_fatalities))))
        if rounded_displaced:
            fields.append(
                tr('Are there enough covered floor areas available for '
                   '%s people?') % rounded_displaced)
            fields.append(tr(
                'Are there enough shelters and relief items available for '
                '%s people?') % rounded_displaced)
            fields.append(tr(
                'If yes, where are they located and how will we '
                'distribute them?'))
            fields.append(tr(
                'If no, where can we obtain additional relief items '
                'from and how will we transport them?'))
            fields.append(tr(
                'Are there enough water supply, sanitation, hygiene, food, '
                'shelter, medicines and relief items available for %s '
                'displaced people?') % rounded_displaced)

        return fields

    def notes(self):
        """Notes and caveats for the IF report.

        :returns: List containing notes.
        :rtype: list
        """
        fields = [
            tr('Total population in the analysis area: %s') %
            format_int(population_rounding(self.total_population)),
            tr('<sup>1</sup>People are displaced if they experience and '
               'survive a shake level of more than 5 on the MMI scale.'),
            tr('The fatality calculation assumes that no fatalities occur for '
               'shake levels below 4 and fatality counts of less than 50 are '
               'disregarded.'),
            tr('Fatality model is from Institut Teknologi Bandung 2012.'),
            tr('Map shows the estimation of displaced population.')
        ]
        # include any generic exposure specific notes from definitions
        fields = fields + self.exposure_notes()
        # include any generic hazard specific notes from definitions
        fields = fields + self.hazard_notes()
        return fields

    def compute_probability(self, total_fatalities_raw):
        """
        :param total_fatalities_raw:
        :return:
        """
        return None

    def run(self):
        """Indonesian Earthquake Fatality Model.

        Some additional notes to clarify behaviour:

        * Total population = all people within the analysis area
        * Affected population  = displaced people + people killed
        * Displaced = people * displacement rate for mmi level
        * Killed = people * mortality rate for mmi level
        * impact layer produced = affected population

        """
        displacement_rate = self.hardcoded_parameters['displacement_rate']
        fatality_rate = self.compute_fatality_rate()

        # Extract data grids
        hazard = self.hazard.layer.get_data()   # Ground Shaking
        # Population Density
        exposure = self.exposure.layer.get_data(scaling=True)

        # Calculate people affected by each MMI level
        mmi_range = self.hardcoded_parameters['mmi_range']
        number_of_exposed = {}
        number_of_displaced = {}
        number_of_fatalities = {}
        # Calculate fatality rates for observed Intensity values (hazard
        # based on ITB power model
        mask = numpy.zeros(hazard.shape)
        for mmi in mmi_range:
            # Identify cells where MMI is in class i and
            # count people affected by this shake level
            step = self.hardcoded_parameters['step']
            mmi_matches = numpy.where(
                (hazard > mmi - step) * (hazard <= mmi + step), exposure, 0)

            # Calculate expected number of fatalities per level
            exposed = numpy.nansum(mmi_matches)
            fatalities = fatality_rate[mmi] * exposed

            # Calculate expected number of displaced people per level
            displacements = displacement_rate[mmi] * (
                exposed - numpy.median(fatalities))

            # Adjust displaced people to disregard fatalities.
            # Set to zero if there are more fatalities than displaced.
            # displacements = numpy.where(
            #    displacements > fatalities, displacements - fatalities, 0)

            # Sum up numbers for map
            # We need to use matrices here and not just numbers #2235
            # filter out NaN to avoid overflow additions
            # Changed in 3.5.3 for Issue #3489 to correct mask
            # to that it returns affected (displaced + fatalities)
            mmi_matches = displacement_rate[mmi] * numpy.nan_to_num(
                mmi_matches)
            mask += mmi_matches   # Displaced

            # Generate text with result for this study
            # This is what is used in the real time system exposure table
            number_of_exposed[mmi] = exposed
            number_of_displaced[mmi] = displacements
            # noinspection PyUnresolvedReferences
            number_of_fatalities[mmi] = fatalities

        # Total statistics
        total_fatalities_raw = numpy.nansum(
            number_of_fatalities.values(), axis=0)

        # Compute probability of fatality in each magnitude bin
        if (self.__class__.__name__ == 'PAGFatalityFunction') or (
                self.__class__.__name__ == 'ITBBayesianFatalityFunction'):
            prob_fatality_mag = self.compute_probability(total_fatalities_raw)
        else:
            prob_fatality_mag = None

        # Compute number of fatalities
        self.total_population = numpy.nansum(number_of_exposed.values())
        self.total_fatalities = numpy.median(total_fatalities_raw)
        total_displaced = numpy.nansum(number_of_displaced.values())

        # As per email discussion with Ole, Trevor, Hadi, total fatalities < 50
        # will be rounded down to 0 - Tim
        # Needs to revisit but keep it alive for the time being - Hyeuk, Jono
        if self.total_fatalities < 50:
            self.total_fatalities = 0

        affected_population = self.affected_population
        affected_population[tr('Number of fatalities')] = self.total_fatalities
        affected_population[
            tr('Number of people displaced')] = total_displaced
        self.unaffected_population = (
            self.total_population - total_displaced - self.total_fatalities)
        self._evacuation_category = tr('Number of people displaced')

        self.minimum_needs = [
            parameter.serialize() for parameter in
            filter_needs_parameters(self.parameters['minimum needs'])
        ]
        total_needs = self.total_needs

        # Create style
        colours = ['#EEFFEE', '#FFFF7F', '#E15500', '#E4001B', '#730000']
        classes = create_classes(mask.flat[:], len(colours))
        interval_classes = humanize_class(classes)
        style_classes = []
        for i in xrange(len(interval_classes)):
            style_class = dict()
            style_class['label'] = create_label(interval_classes[i])
            style_class['quantity'] = classes[i]
            style_class['transparency'] = 30
            style_class['colour'] = colours[i]
            style_classes.append(style_class)

        style_info = dict(target_field=None,
                          style_classes=style_classes,
                          style_type='rasterStyle')

        impact_data = self.generate_data()

        extra_keywords = {
            'exposed_per_mmi': number_of_exposed,
            'total_population': self.total_population,
            'total_fatalities': population_rounding(self.total_fatalities),
            'total_fatalities_raw': self.total_fatalities,
            'fatalities_per_mmi': number_of_fatalities,
            'total_displaced': population_rounding(total_displaced),
            'displaced_per_mmi': number_of_displaced,
            'map_title': self.map_title(),
            'legend_notes': self.metadata().key('legend_notes'),
            'legend_units': self.metadata().key('legend_units'),
            'legend_title': self.metadata().key('legend_title'),
            'total_needs': total_needs,
            'prob_fatality_mag': prob_fatality_mag,
        }

        impact_layer_keywords = self.generate_impact_keywords(extra_keywords)

        # Create raster object and return
        impact_layer = Raster(
            mask,
            projection=self.exposure.layer.get_projection(),
            geotransform=self.exposure.layer.get_geotransform(),
            keywords=impact_layer_keywords,
            name=self.map_title(),
            style_info=style_info)

        impact_layer.impact_data = impact_data
        self._impact = impact_layer
        return impact_layer
