import numpy
from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.impact_functions.core import get_question
from safe.storage.vector import Vector
from safe.storage.clipping import clip_raster_by_polygons
from safe.common.utilities import ugettext as _
from safe.common.tables import Table, TableRow


class FloodEvacuationFunctionVectorHazard(FunctionProvider):
    """Risk plugin for flood evacuation

    :author AIFDR
    :rating 4
    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami'] and \
                    layertype=='vector'

    :param requires category=='exposure' and \
                    subcategory=='population' and \
                    layertype=='raster' and \
                    datatype=='density'
    """

    title = _('Need evacuation')
    target_field = 'population'

    def run(self, layers):
        """Risk plugin for flood population evacuation

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

        # Depth above which people are regarded affected [m]
        #threshold = 1.0  # Threshold [m]

        # Identify hazard and exposure layers
        inundation = get_hazard_layer(layers)  # Flood inundation
        population = get_exposure_layer(layers)

        question = get_question(inundation.get_name(),
                                population.get_name(),
                                self)

        # Check that hazard is polygon type
        if not inundation.is_vector:
            msg = ('Input hazard %s  was not a vector layer as expected '
                   % inundation.get_name())
            raise Exception(msg)

        msg = ('Input hazard must be a polygon layer. I got %s with layer '
               'type %s' % (inundation.get_name(),
                            inundation.get_geometry_name()))
        if not inundation.is_polygon_data:
            raise Exception(msg)

        # Extract data as numeric arrays
        #geometry = inundation.get_geometry()  # Flood footprints
        attributes = inundation.get_data()    # Flood attributes

        # Separate population grid points by flood footprints
        print 'Clip'
        L = clip_raster_by_polygons(population, inundation)

        print 'Sum'
        # Sum up population affected by polygons
        evacuated = 0
        attributes = []
        minpop = 1000
        maxpop = -minpop
        for l in L:
            values = l[1]
            s = numpy.sum(values)
            if s < minpop:
                minpop = s
            if s > maxpop:
                maxpop = s
            attributes.append({self.target_field: int(s)})
            evacuated += s

        print 'minpop', minpop
        print 'maxpop', maxpop

        # Count totals
        total = int(numpy.sum(population.get_data(nan=0, scaling=False)))

        # Don't show digits less than a 1000
        if total > 1000:
            total = total // 1000 * 1000
        if evacuated > 1000:
            evacuated = evacuated // 1000 * 1000
        print 'Done'

        # Calculate estimated needs based on BNPB Perka 7/2008 minimum bantuan
        rice = evacuated * 2.8
        drinking_water = evacuated * 17.5
        water = evacuated * 67
        family_kits = evacuated / 5
        toilets = evacuated / 20

        # Generate impact report for the pdf map
        table_body = [question,
                      TableRow([_('People needing evacuation'),
                                '%i' % evacuated],
                               header=True),
                      TableRow(_('Map shows population affected in each flood '
                                 'prone area ')),
                      TableRow([_('Needs per week'), _('Total')],
                               header=True),
                      [_('Rice [kg]'), int(rice)],
                      [_('Drinking Water [l]'), int(drinking_water)],
                      [_('Clean Water [l]'), int(water)],
                      [_('Family Kits'), int(family_kits)],
                      [_('Toilets'), int(toilets)]]
        impact_table = Table(table_body).toNewlineFreeString()

        # Extend impact report for on-screen display
        table_body.extend([TableRow(_('Notes'), header=True),
                           _('Total population: %i') % total,
                           _('People need evacuation if in area identified '
                             'as "Flood Prone"'),
                           _('Minimum needs are defined in BNPB '
                             'regulation 7/2008')])
        impact_summary = Table(table_body).toNewlineFreeString()
        map_title = _('People affected by flood prone areas')

        # Generare 8 intervals across the range of flooded population
        cls = numpy.linspace(minpop, maxpop, 9)
        print 'cls', cls, len(cls)

        # Define style info for output polygons showing population counts
        style_classes = [dict(label=_('Nil'),
                              colour='#FFFFFF', min=cls[0], max=cls[1],
                              transparency=0, size=1),
                         dict(label=_('Low'),
                              colour='#38A800', min=cls[1], max=cls[2],
                              transparency=0, size=1),
                         dict(label=_('Low'),
                              colour='#79C900', min=cls[2], max=cls[3],
                              transparency=0, size=1),
                         dict(label=_('Low'),
                              colour='#CEED00', min=cls[3], max=cls[4],
                              transparency=0, size=1),
                         dict(label=_('Medium'),
                              colour='#FFCC00', min=cls[4], max=cls[5],
                              transparency=0, size=1),
                         dict(label=_('Medium'),
                              colour='#FF6600', min=cls[5], max=cls[6],
                              transparency=0, size=1),
                         dict(label=_('Medium'),
                              colour='#FF0000', min=cls[6], max=cls[7],
                              transparency=0, size=1),
                         dict(label=_('High'),
                              colour='#7A0000', min=cls[7], max=cls[8],
                              transparency=0, size=1)]

        #style_classes[1]['label'] = _('Low [%i people/area]') % classes[1]
        #style_classes[4]['label'] = _('Medium [%i people/area]') % classes[4]
        #style_classes[7]['label'] = _('High [%i people/area]') % classes[7]

        # Override style info with new classes and name
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          legend_title=_('Population Count'))

        # Create vector layer and return
        V = Vector(data=attributes,
                   projection=inundation.get_projection(),
                   geometry=inundation.get_geometry(),
                   name=_('Population affected by flood prone areas'),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'map_title': map_title},
                   style_info=style_info)
        return V
