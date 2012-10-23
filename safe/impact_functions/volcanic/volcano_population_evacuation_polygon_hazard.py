import numpy
from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.impact_functions.core import get_question
from safe.impact_functions.core import format_int
from safe.storage.vector import Vector
from safe.common.utilities import ugettext as tr
from safe.common.tables import Table, TableRow
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.engine.interpolation import make_circular_polygon
from safe.common.exceptions import InaSAFEError


class VolcanoPolygonHazardPopulation(FunctionProvider):
    """Impact function for volcano hazard zones impact on population

    :author AIFDR
    :rating 4
    :param requires category=='hazard' and \
                    subcategory in ['volcano'] and \
                    layertype=='vector'

    :param requires category=='exposure' and \
                    subcategory=='population' and \
                    layertype=='raster'
    """

    title = tr('Need evacuation')
    target_field = 'population'

    parameters = {'R [km]': [3, 5, 10]}

    def run(self, layers):
        """Risk plugin for flood population evacuation

        Input
          layers: List of layers expected to contain
              H: Raster layer of volcano depth
              P: Raster layer of population data on the same grid as H

        Counts number of people exposed to flood levels exceeding
        specified threshold.

        Return
          Map of population exposed to flood levels exceeding the threshold
          Table with number of people evacuated and supplies required
        """

        # Identify hazard and exposure layers
        H = get_hazard_layer(layers)  # Flood inundation
        E = get_exposure_layer(layers)

        question = get_question(H.get_name(),
                                E.get_name(),
                                self)

        # Input checks
        if not H.is_vector:
            msg = ('Input hazard %s  was not a vector layer as expected '
                   % H.get_name())
            raise Exception(msg)

        msg = ('Input hazard must be a polygon or point layer. '
               'I got %s with layer '
               'type %s' % (H.get_name(),
                            H.get_geometry_name()))
        if not (H.is_polygon_data or H.is_point_data):
            raise Exception(msg)

        if H.is_point_data:
            # Use concentric circles
            radii = self.parameters['R [km]']

            centers = H.get_geometry()
            attributes = H.get_data()
            rad_m = [x * 1000 for x in radii]  # Convert to meters
            H = make_circular_polygon(centers,
                                      rad_m,
                                      attributes=attributes)
            #H.write_to_file('Evac_zones_%s.shp' % str(radii))  # To check

            category_title = 'Radius'
            category_header = tr('Distance [km]')
            category_names = radii

            name_attribute = 'NAME'  # As in e.g. the Smithsonian dataset
        else:
            # Use hazard map
            category_title = 'KRB'
            category_header = tr('Category')

            # FIXME (Ole): Change to English and use translation system
            category_names = ['Kawasan Rawan Bencana III',
                              'Kawasan Rawan Bencana II',
                              'Kawasan Rawan Bencana I']

            name_attribute = 'GUNUNG'  # As in e.g. BNPB hazard map
            attributes = H.get_data()

        # Get names of volcanos considered
        if name_attribute in H.get_attribute_names():
            D = {}
            for att in H.get_data():
                # Run through all polygons and get unique names
                D[att[name_attribute]] = None

            volcano_names = ''
            for name in D:
                volcano_names += '%s, ' % name
            volcano_names = volcano_names[:-2]  # Strip trailing ', '
        else:
            volcano_names = tr('Not specified in data')

        if not category_title in H.get_attribute_names():
            msg = ('Hazard data %s did not contain expected '
                   'attribute %s ' % (H.get_name(), category_title))
            raise InaSAFEError(msg)

        # Run interpolation function for polygon2raster
        P = assign_hazard_values_to_exposure_data(H, E,
                                                  attribute_name='population')

        # Initialise attributes of output dataset with all attributes
        # from input polygon and a population count of zero
        new_attributes = H.get_data()

        categories = {}
        for attr in new_attributes:
            attr[self.target_field] = 0
            cat = attr[category_title]
            categories[cat] = 0

        # Count affected population per polygon and total
        evacuated = 0
        for attr in P.get_data():
            # Get population at this location
            pop = float(attr['population'])

            # Update population count for associated polygon
            poly_id = attr['polygon_id']
            new_attributes[poly_id][self.target_field] += pop

            # Update population count for each category
            cat = new_attributes[poly_id][category_title]
            categories[cat] += pop

        # Count totals
        total = int(numpy.sum(E.get_data(nan=0)))

        # Don't show digits less than a 1000
        if total > 1000:
            total = total // 1000 * 1000

        # Count number and cumulative for each zone
        cum = 0
        pops = {}
        cums = {}
        for name in category_names:
            if category_title == 'Radius':
                key = name * 1000  # Convert to meters
            else:
                key = name

            pop = int(categories[key])

            if pop > 1000:
                pop = pop // 1000 * 1000

            cum += pop
            if cum > 1000:
                cum = cum // 1000 * 1000

            pops[name] = pop
            cums[name] = cum

        # Use final accumulation as total number needing evac
        evacuated = cum

        # Calculate estimated needs based on BNPB Perka
        # 7/2008 minimum bantuan
        # FIXME (Ole): Refactor into one function to be shared
        rice = int(evacuated * 2.8)
        drinking_water = int(evacuated * 17.5)
        water = int(evacuated * 67)
        family_kits = int(evacuated / 5)
        toilets = int(evacuated / 20)

        # Generate impact report for the pdf map
        blank_cell = ''
        table_body = [question,
                      TableRow([tr('Volcanos considered'),
                                '%s' % volcano_names, blank_cell],
                               header=True),
                      TableRow([tr('People needing evacuation'),
                                '%s' % format_int(evacuated),
                                blank_cell],
                                header=True),
                      TableRow([category_header,
                                tr('Total'), tr('Cumulative')],
                               header=True)]

        for name in category_names:
            table_body.append(TableRow([name,
                                        format_int(pops[name]),
                                        format_int(cums[name])]))

        table_body.extend([TableRow(tr('Map shows population affected in '
                                       'each of volcano hazard polygons.')),
                           TableRow([tr('Needs per week'), tr('Total'),
                                     blank_cell],
                                    header=True),
                           [tr('Rice [kg]'), format_int(rice), blank_cell],
                           [tr('Drinking Water [l]'),
                            format_int(drinking_water), blank_cell],
                           [tr('Clean Water [l]'), format_int(water),
                            blank_cell],
                           [tr('Family Kits'), format_int(family_kits),
                            blank_cell],
                           [tr('Toilets'), format_int(toilets),
                            blank_cell]])
        impact_table = Table(table_body).toNewlineFreeString()

        # Extend impact report for on-screen display
        table_body.extend([TableRow(tr('Notes'), header=True),
                           tr('Total population %s in the viewable area')
                           % format_int(total),
                           tr('People need evacuation if they are within the '
                              'volcanic hazard zones.')])
        impact_summary = Table(table_body).toNewlineFreeString()
        map_title = tr('People affected by volcanic hazard zone')

        # Define classes for legend for flooded population counts
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        population_counts = [x[self.target_field] for x in new_attributes]
        cls = [0] + numpy.linspace(1,
                                   max(population_counts),
                                   len(colours)).tolist()

        # Define style info for output polygons showing population counts
        style_classes = []
        for i, colour in enumerate(colours):
            lo = cls[i]
            hi = cls[i + 1]

            if i == 0:
                label = tr('0')
            else:
                label = tr('%i - %i') % (lo, hi)

            entry = dict(label=label, colour=colour, min=lo, max=hi,
                         transparency=50, size=1)
            style_classes.append(entry)

        # Override style info with new classes and name
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          legend_title=tr('Population Count'))

        # Create vector layer and return
        V = Vector(data=new_attributes,
                   projection=H.get_projection(),
                   geometry=H.get_geometry(as_geometry_objects=True),
                   name=tr('Population affected by volcanic hazard zone'),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'map_title': map_title,
                             'target_field': self.target_field},
                   style_info=style_info)
        return V
