import numpy
from safe.impact_functions.core import (FunctionProvider,
                                        get_hazard_layer,
                                        get_exposure_layer,
                                        get_question,
                                        get_function_title)

from safe.common.tables import Table, TableRow
from safe.storage.raster import Raster


class FloodPopulationEvacuationFunction(FunctionProvider):
    """Impact function for flood evacuation (tutorial)

    :author AIFDR
    :rating 4
    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami'] and \
                    layertype=='raster' and \
                    unit=='m'

    :param requires category=='exposure' and \
                    subcategory=='population' and \
                    layertype=='raster'
    """

    title = 'be evacuated'

    synopsis = ('To assess the impacts of (flood or tsunami) inundation '
                'on population.')
    actions = ('Provide details about how many people would likely need '
               'to be evacuated, where they are located and what resources '
               'would be required to support them.')
    detailed_description = ('The population subject to inundation '
                            'exceeding a threshold (default 1m) is '
                            'calculated and returned as a raster layer.'
                            'In addition the total number and the required '
                            'needs in terms of the BNPB (Perka 7) ')

    permissible_hazard_input = ('A hazard raster layer where each cell '
                                'represents flood depth (in meters).')
    permissible_exposure_input = ('An exposure raster layer where each '
                                  'cell '
                                  'represent population count.')
    limitation = ('The default threshold of 1 meter was selected based on '
                  'consensus, not hard evidence.')

    parameters = {'threshold': 1.0}

    def run(self, layers):
        """Impact function for flood population evacuation

        Input
          layers: List of layers expected to contain
              H: Raster layer of flood depth
              P: Raster layer of population data on the same grid as H

        Counts number of people exposed to flood levels exceeding
        specified threshold.

        Return
          Map of population exposed to flood levels exceeding the threshold
          Table with number of people evacuated and supplies required
        """

        # Identify hazard and exposure layers
        inundation = get_hazard_layer(layers)  # Flood inundation [m]
        population = get_exposure_layer(layers)

        question = get_question(inundation.get_name(),
                                population.get_name(),
                                self)

        # Determine depths above which people are regarded affected [m]
        # Use thresholds from inundation layer if specified
        threshold = self.parameters['threshold']

        # Extract data as numeric arrays
        D = inundation.get_data(nan=0.0)  # Depth

        # Calculate impact as population exposed to depths > max threshold
        P = population.get_data(nan=0.0, scaling=True)

        # Create new array with positive population counts only for
        # pixels where inundation exceeds threshold.
        I = numpy.where(D >= threshold, P, 0)

        # Count population thus exposed to inundation
        evacuated = int(numpy.sum(I))

        # Count total population
        total = int(numpy.sum(P))

        # Calculate estimated needs based on BNPB Perka 7/2008 minimum bantuan

        # 400g per person per day
        rice = int(evacuated * 2.8)

        # 2.5L per person per day
        drinking_water = int(evacuated * 17.5)

        # 15L per person per day
        water = int(evacuated * 105)

        # assume 5 people per family (not in perka)
        family_kits = int(evacuated / 5)

        # 20 people per toilet
        toilets = int(evacuated / 20)

        # Generate impact report for the pdf map
        table_body = [question,
                      TableRow([('People in %.1f m of water' %
                                 threshold),
                                '%s' % evacuated],
                               header=True),
                      TableRow('Map shows population density needing '
                               'evacuation'),
                      TableRow(['Needs per week', 'Total'],
                               header=True),
            ['Rice [kg]', rice],
            ['Drinking Water [l]', drinking_water],
            ['Clean Water [l]', water],
            ['Family Kits', family_kits],
            ['Toilets', toilets]]
        impact_table = Table(table_body).toNewlineFreeString()

        # Extend impact report for on-screen display
        table_body.extend([TableRow('Notes', header=True),
                           'Total population: %s' % total,
                           'People need evacuation if flood levels '
                           'exceed %(eps).1f m' % {'eps': threshold},
                           'Minimum needs are defined in BNPB '
                           'regulation 7/2008'])
        impact_summary = Table(table_body).toNewlineFreeString()

        map_title = 'People in need of evacuation'

        # Generate 8 equidistant classes across the range of flooded population
        # 8 is the number of classes in the predefined flood population style
        # as imported
        classes = numpy.linspace(numpy.nanmin(I.flat[:]),
                                 numpy.nanmax(I.flat[:]), 8)

        # Define 8 colours - on for each class
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']

        # Create style associating each class with a colour and transparency.
        style_classes = []
        for i, cls in enumerate(classes):
            if i == 0:
                # Smallest class has 100% transparency
                transparency = 100
            else:
                # All the others are solid
                transparency = 0

            # Create labels for three of the classes
            if i == 1:
                label = 'Low [%.2f people/cell]' % cls
            elif i == 4:
                label = 'Medium [%.2f people/cell]' % cls
            elif i == 7:
                label = 'High [%.2f people/cell]' % cls
            else:
                label = ''

            # Style dictionary for this class
            d = dict(colour=colours[i],
                     quantity=cls,
                     transparency=transparency,
                     label=label)
            style_classes.append(d)

        # Create style info for impact layer
        style_info = dict(target_field=None,  # Only for vector data
                          legend_title='Population Density',
                          style_classes=style_classes)

        # Create raster object and return
        R = Raster(I,
                   projection=inundation.get_projection(),
                   geotransform=inundation.get_geotransform(),
                   name='Population which %s' % get_function_title(self),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'map_title': map_title},
                   style_info=style_info)
        return R
