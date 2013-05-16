import numpy
from third_party.odict import OrderedDict
from safe.impact_functions.core import (
    FunctionProvider, get_hazard_layer, get_exposure_layer, get_question)
from safe.storage.vector import Vector
from safe.common.utilities import (
    ugettext as tr,
    format_int,
    round_thousand,
    get_defaults,
    humanize_class,
    create_classes,
    create_label)
from safe.common.tables import Table, TableRow, TableCell
from safe.engine.interpolation import assign_hazard_values_to_exposure_data

import logging
LOGGER = logging.getLogger('InaSAFE')


class FloodEvacuationFunctionVectorHazard(FunctionProvider):
    """Impact function for vector flood evacuation

    :author AIFDR
    :rating 4
    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami'] and \
                    layertype=='vector'

    :param requires category=='exposure' and \
                    subcategory=='population' and \
                    layertype=='raster'
    """

    title = tr('Need evacuation')
    # Function documentation
    synopsis = tr(
        'To assess the impacts of (flood or tsunami) inundation in vector '
        'format on population.')
    actions = tr(
        'Provide details about how many people would likely need to be '
        'evacuated, where they are located and what resources would be '
        'required to support them.')

    detailed_description = tr(
        'The population subject to inundation is determined whether in an '
        'area which affected or not. You can also set an evacuation '
        'percentage to calculate how many percent of the total population '
        'affected to be evacuated. This number will be used to estimate needs'
        ' based on BNPB Perka 7/2008 minimum bantuan.')

    hazard_input = tr(
        'A hazard vector layer which has attribute affected the value is '
        'either 1 or 0')
    exposure_input = tr(
        'An exposure raster layer where each cell represent population count.')
    output = tr(
        'Vector layer contains population affected and the minimum needs '
        'based on evacuation percentage.')

    target_field = 'population'
    defaults = get_defaults()
    parameters = OrderedDict([
        ('evacuation_percentage', 1),  # Percent of affected needing evacuation
        ('postprocessors', OrderedDict([
            ('Gender', {'on': True}),
            ('Age', {
                'on': True,
                'params': OrderedDict([
                    ('youth_ratio', defaults['YOUTH_RATIO']),
                    ('adult_ratio', defaults['ADULT_RATIO']),
                    ('elder_ratio', defaults['ELDER_RATIO'])])})]))])

    def run(self, layers):
        """Risk plugin for flood population evacuation

        Input
          layers: List of layers expected to contain
              my_hazard : Vector polygon layer of flood depth
              my_exposure : Raster layer of population data on the same
                            grid as my_hazard

        Counts number of people exposed to areas identified as flood prone

        Return
          Map of population exposed to flooding
          Table with number of people evacuated and supplies required
        """
        # Identify hazard and exposure layers
        my_hazard = get_hazard_layer(layers)  # Flood inundation
        my_exposure = get_exposure_layer(layers)

        question = get_question(my_hazard.get_name(),
                                my_exposure.get_name(),
                                self)

        # Check that hazard is polygon type
        if not my_hazard.is_vector:
            msg = ('Input hazard %s  was not a vector layer as expected '
                   % my_hazard.get_name())
            raise Exception(msg)

        msg = ('Input hazard must be a polygon layer. I got %s with layer '
               'type %s' % (my_hazard.get_name(),
                            my_hazard.get_geometry_name()))
        if not my_hazard.is_polygon_data:
            raise Exception(msg)

        # Run interpolation function for polygon2raster
        P = assign_hazard_values_to_exposure_data(my_hazard, my_exposure,
                                                  attribute_name='population')

        # Initialise attributes of output dataset with all attributes
        # from input polygon and a population count of zero
        new_attributes = my_hazard.get_data()
        category_title = 'affected'  # FIXME: Should come from keywords
        deprecated_category_title = 'FLOODPRONE'
        categories = {}
        for attr in new_attributes:
            attr[self.target_field] = 0
            try:
                cat = attr[category_title]
            except KeyError:
                cat = attr['FLOODPRONE']
            categories[cat] = 0

        # Count affected population per polygon, per category and total
        affected_population = 0
        for attr in P.get_data():

            affected = False
            if 'affected' in attr:
                res = attr['affected']
                if res is None:
                    x = False
                else:
                    x = bool(res)
                affected = x
            elif 'FLOODPRONE' in attr:
                # If there isn't an 'affected' attribute,
                res = attr['FLOODPRONE']
                if res is not None:
                    affected = res.lower() == 'yes'
            elif 'Affected' in attr:
                # Check the default attribute assigned for points
                # covered by a polygon
                res = attr['Affected']
                if res is None:
                    x = False
                else:
                    x = res
                affected = x
            else:
                # there is no flood related attribute
                msg = ('No flood related attribute found in %s. '
                       'I was looking fore either "Flooded", "FLOODPRONE" '
                       'or "Affected". The latter should have been '
                       'automatically set by call to '
                       'assign_hazard_values_to_exposure_data(). '
                       'Sorry I can\'t help more.')
                raise Exception(msg)

            if affected:
                # Get population at this location
                pop = float(attr['population'])

                # Update population count for associated polygon
                poly_id = attr['polygon_id']
                new_attributes[poly_id][self.target_field] += pop

                # Update population count for each category
                try:
                    cat = new_attributes[poly_id][category_title]
                except KeyError:
                    cat = new_attributes[poly_id][deprecated_category_title]
                categories[cat] += pop

                # Update total
                affected_population += pop

        affected_population = round_thousand(affected_population)
        # Estimate number of people in need of evacuation
        evacuated = (affected_population *
                     self.parameters['evacuation_percentage']
                     / 100.0)

        total = int(numpy.sum(my_exposure.get_data(nan=0, scaling=False)))

        # Don't show digits less than a 1000
        total = round_thousand(total)
        evacuated = round_thousand(evacuated)

        # Calculate estimated needs based on BNPB Perka 7/2008 minimum bantuan
        rice = evacuated * 2.8  # 400g per person per day
        drinking_water = evacuated * 17.5  # 2.5L per person per day
        water = evacuated * 105  # 15L per person per day
        family_kits = evacuated / 5  # assume 5 people per family
        toilets = evacuated / 20  # 20 people to 1 toilet

        # Generate impact report for the pdf map
        table_body = [question,
                      TableRow([tr('People affected'),
                                '%s*' % format_int(int(affected_population))],
                               header=True),
                      TableRow([tr('People needing evacuation'),
                                '%s*' % format_int(int(evacuated))],
                               header=True),
                      TableRow([
                          TableCell(
                              tr('* Number is rounded to the nearest 1000'),
                              col_span=2)],
                          header=False),
                      TableRow([tr('Evacuation threshold'),
                                '%s%%' % format_int(
                                    self.parameters['evacuation_percentage'])],
                               header=True),
                      TableRow(tr('Map shows population affected in each flood'
                                  ' prone area ')),
                      TableRow([tr('Needs per week'), tr('Total')],
                               header=True),
                      [tr('Rice [kg]'), format_int(int(rice))],
                      [tr('Drinking Water [l]'),
                       format_int(int(drinking_water))],
                      [tr('Clean Water [l]'), format_int(int(water))],
                      [tr('Family Kits'), format_int(int(family_kits))],
                      [tr('Toilets'), format_int(int(toilets))]]
        impact_table = Table(table_body).toNewlineFreeString()

        table_body.append(TableRow(tr('Action Checklist:'), header=True))
        table_body.append(TableRow(tr('How will warnings be disseminated?')))
        table_body.append(TableRow(tr('How will we reach stranded people?')))
        table_body.append(TableRow(tr('Do we have enough relief items?')))
        table_body.append(TableRow(tr('If yes, where are they located and how '
                                      'will we distribute them?')))
        table_body.append(TableRow(tr('If no, where can we obtain additional '
                                      'relief items from and how will we '
                                      'transport them to here?')))

        # Extend impact report for on-screen display
        table_body.extend([TableRow(tr('Notes'), header=True),
                           tr('Total population: %s') % format_int(total),
                           tr('People need evacuation if in area identified '
                              'as "Flood Prone"'),
                           tr('Minimum needs are defined in BNPB '
                              'regulation 7/2008')])
        impact_summary = Table(table_body).toNewlineFreeString()

        # Create style
        # Define classes for legend for flooded population counts
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        population_counts = [x['population'] for x in new_attributes]
        classes = create_classes(population_counts, len(colours))
        interval_classes = humanize_class(classes)

        # Define style info for output polygons showing population counts
        style_classes = []
        for i in xrange(len(colours)):
            style_class = dict()
            style_class['label'] = create_label(interval_classes[i])
            if i == 0:
                transparency = 100
                style_class['min'] = 0
            else:
                transparency = 0
                style_class['min'] = classes[i - 1]
            style_class['transparency'] = transparency
            style_class['colour'] = colours[i]
            style_class['max'] = classes[i]
            style_classes.append(style_class)

        # Override style info with new classes and name
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          style_type='graduatedSymbol')

        # For printing map purpose
        map_title = tr('People affected by flood prone areas')
        legend_notes = tr('Thousand separator is represented by \'.\'')
        legend_units = tr('(people per polygon)')
        legend_title = tr('Population Count')

        # Create vector layer and return
        V = Vector(data=new_attributes,
                   projection=my_hazard.get_projection(),
                   geometry=my_hazard.get_geometry(),
                   name=tr('Population affected by flood prone areas'),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'target_field': self.target_field,
                             'map_title': map_title,
                             'legend_notes': legend_notes,
                             'legend_units': legend_units,
                             'legend_title': legend_title},
                   style_info=style_info)
        return V
