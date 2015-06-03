# coding=utf-8
"""InaSAFE Disaster risk tool by Australian Aid - ITB Earthquake
Impact Function on Population.

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'lucernae'
__date__ = '24/03/15'

import numpy
import logging

from safe.common.utilities import OrderedDict
from safe.impact_functions.base import ImpactFunction
from safe.impact_functions.earthquake.itb_earthquake_fatality_model\
    .metadata_definitions import ITBFatalityMetadata
from safe.impact_functions.core import (
    evacuated_population_needs,
    population_rounding_full,
    population_rounding)
from safe.storage.raster import Raster
from safe.common.utilities import (
    format_int,
    humanize_class,
    create_classes,
    create_label,
    get_thousand_separator)
from safe.common.tables import Table, TableRow
from safe.common.exceptions import InaSAFEError
from safe.utilities.i18n import tr
from safe.gui.tools.minimum_needs.needs_profile import add_needs_parameters, \
    get_needs_provenance_value, filter_needs_parameters

LOGGER = logging.getLogger('InaSAFE')


class ITBFatalityFunction(ImpactFunction):
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

        # AG: Use the proper minimum needs, update the parameters
        self.parameters = add_needs_parameters(self.parameters)
        self.hardcoded_parameters = OrderedDict([
            ('x', 0.62275231), ('y', 8.03314466),  # Model coefficients
            # Rates of people displaced for each MMI level
            ('displacement_rate', {
                1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 1.0,
                7: 1.0, 8: 1.0, 9: 1.0, 10: 1.0
            }),
            ('mmi_range', range(2, 10)),
            ('step', 0.5),
            ('calculate_displaced_people', True)
        ])

    def fatality_rate(self, mmi):
        """ITB method to compute fatality rate.

        :param mmi:
        """
        # As per email discussion with Ole, Trevor, Hadi, mmi < 4 will have
        # a fatality rate of 0 - Tim
        if mmi < 4:
            return 0

        x = self.hardcoded_parameters['x']
        y = self.hardcoded_parameters['y']
        # noinspection PyUnresolvedReferences
        return numpy.power(10.0, x * mmi - y)

    def run(self, layers=None):
        """Indonesian Earthquake Fatality Model.

        Input:

        :param layers: List of layers expected to contain,

                hazard: Raster layer of MMI ground shaking

                exposure: Raster layer of population count
        """
        self.validate()
        self.prepare(layers)

        displacement_rate = self.hardcoded_parameters['displacement_rate']

        # Extract input layers
        intensity = self.hazard
        population = self.exposure

        # Extract data grids
        hazard = intensity.get_data()   # Ground Shaking
        exposure = population.get_data(scaling=True)  # Population Density

        # Calculate people affected by each MMI level
        # FIXME (Ole): this range is 2-9. Should 10 be included?
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
            mmi_matches = numpy.where(
                (hazard > mmi - self.hardcoded_parameters['step']) * (
                    hazard <= mmi + self.hardcoded_parameters['step']),
                exposure, 0)

            # Calculate expected number of fatalities per level
            fatality_rate = self.fatality_rate(mmi)
            fatalities = fatality_rate * mmi_matches

            # Calculate expected number of displaced people per level
            try:
                displacements = displacement_rate[mmi] * mmi_matches
            except KeyError, e:
                msg = 'mmi = %i, mmi_matches = %s, Error msg: %s' % (
                    mmi, str(mmi_matches), str(e))
                # noinspection PyExceptionInherit
                raise InaSAFEError(msg)

            # Adjust displaced people to disregard fatalities.
            # Set to zero if there are more fatalities than displaced.
            displacements = numpy.where(
                displacements > fatalities, displacements - fatalities, 0)

            # Sum up numbers for map
            mask += displacements   # Displaced

            # Generate text with result for this study
            # This is what is used in the real time system exposure table
            number_of_exposed[mmi] = numpy.nansum(mmi_matches.flat)
            number_of_displaced[mmi] = numpy.nansum(displacements.flat)
            # noinspection PyUnresolvedReferences
            number_of_fatalities[mmi] = numpy.nansum(fatalities.flat)

        # Total statistics
        total_population, rounding = population_rounding_full(
            numpy.nansum(exposure.flat))

        # Compute number of fatalities
        total_fatalities = population_rounding(numpy.nansum(
            number_of_fatalities.values()))
        # As per email discussion with Ole, Trevor, Hadi, total fatalities < 50
        # will be rounded down to 0 - Tim
        if total_fatalities < 50:
            total_fatalities = 0

        # Compute number of people displaced due to building collapse
        total_displaced = population_rounding(
            numpy.nansum(number_of_displaced.values()))

        # Generate impact report
        table_body = [self.question]

        # Add total fatality estimate
        s = format_int(total_fatalities)
        table_body.append(TableRow([tr('Number of fatalities'), s],
                                   header=True))

        if self.hardcoded_parameters['calculate_displaced_people']:
            # Add total estimate of people displaced
            s = format_int(total_displaced)
            table_body.append(TableRow([tr('Number of people displaced'), s],
                                       header=True))
        else:
            total_displaced = 0

        # Add estimate of total population in area
        s = format_int(int(total_population))
        table_body.append(TableRow([tr('Total number of people'), s],
                                   header=True))

        minimum_needs = [
            parameter.serialize() for parameter in
            filter_needs_parameters(self.parameters['minimum needs'])
        ]

        # Generate impact report for the pdf map
        table_body = [
            self.question, TableRow(
                [tr('Fatalities'), '%s' % format_int(total_fatalities)],
                header=True),
            TableRow(
                [tr('People displaced'), '%s' % format_int(total_displaced)],
                header=True),
            TableRow(tr('Map shows the estimation of displaced population'))]

        total_needs = evacuated_population_needs(
            total_displaced, minimum_needs)
        for frequency, needs in total_needs.items():
            table_body.append(TableRow(
                [
                    tr('Needs should be provided %s' % frequency),
                    tr('Total')
                ],
                header=True))
            for resource in needs:
                table_body.append(TableRow([
                    tr(resource['table name']),
                    format_int(resource['amount'])]))
        table_body.append(TableRow(tr('Provenance'), header=True))
        table_body.append(TableRow(get_needs_provenance_value(
            self.parameters)))

        table_body.append(TableRow(tr('Action Checklist:'), header=True))

        if total_fatalities > 0:
            table_body.append(tr('Are there enough victim identification '
                                 'units available for %s people?') %
                              format_int(total_fatalities))
        if total_displaced > 0:
            table_body.append(tr('Are there enough shelters and relief items '
                                 'available for %s people?')
                              % format_int(total_displaced))
            table_body.append(TableRow(tr('If yes, where are they located and '
                                          'how will we distribute them?')))
            table_body.append(TableRow(tr('If no, where can we obtain '
                                          'additional relief items from and '
                                          'how will we transport them?')))

        # Extend impact report for on-screen display
        table_body.extend([TableRow(tr('Notes'), header=True),
                           tr('Total population: %s') % format_int(
                               total_population),
                           tr('People are considered to be displaced if '
                              'they experience and survive a shake level'
                              'of more than 5 on the MMI scale '),
                           tr('The fatality calculation assumes that '
                              'no fatalities occur for shake levels below 4 '
                              'and fatality counts of less than 50 are '
                              'disregarded.'),
                           tr('All values are rounded up to the nearest '
                              'integer in order to avoid representing human '
                              'lives as fractions.')])

        table_body.append(TableRow(tr('Notes'), header=True))
        table_body.append(
            tr('Fatality model is from Institut Teknologi Bandung 2012.'))
        table_body.append(
            tr('Population numbers rounded up to the nearest %s.') % rounding)

        # Result
        impact_summary = Table(table_body).toNewlineFreeString()
        impact_table = impact_summary

        # Create style
        colours = ['#EEFFEE', '#FFFF7F', '#E15500', '#E4001B', '#730000']
        classes = create_classes(mask.flat[:], len(colours))
        interval_classes = humanize_class(classes)
        style_classes = []
        for i in xrange(len(interval_classes)):
            style_class = dict()
            style_class['label'] = create_label(interval_classes[i])
            style_class['quantity'] = classes[i]
            if i == 0:
                transparency = 100
            else:
                transparency = 30
            style_class['transparency'] = transparency
            style_class['colour'] = colours[i]
            style_classes.append(style_class)

        style_info = dict(target_field=None,
                          style_classes=style_classes,
                          style_type='rasterStyle')

        # For printing map purpose
        map_title = tr('Earthquake impact to population')
        legend_notes = tr('Thousand separator is represented by %s' %
                          get_thousand_separator())
        legend_units = tr('(people per cell)')
        legend_title = tr('Population Count')

        # Create raster object and return
        raster = Raster(
            mask,
            projection=population.get_projection(),
            geotransform=population.get_geotransform(),
            keywords={
                'impact_summary': impact_summary,
                'total_population': total_population,
                'total_fatalities': total_fatalities,
                'fatalities_per_mmi': number_of_fatalities,
                'exposed_per_mmi': number_of_exposed,
                'displaced_per_mmi': number_of_displaced,
                'impact_table': impact_table,
                'map_title': map_title,
                'legend_notes': legend_notes,
                'legend_units': legend_units,
                'legend_title': legend_title,
                'total_needs': total_needs},
            name=tr('Estimated displaced population per cell'),
            style_info=style_info)
        self._impact = raster
        return raster
