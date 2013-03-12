import numpy
from safe.impact_functions.core import (FunctionProvider,
                                        get_hazard_layer,
                                        get_exposure_layer,
                                        get_question)
from safe.storage.vector import Vector
from safe.common.utilities import (ugettext as tr,
                                   format_int)
from safe.common.tables import Table, TableRow
from safe.engine.interpolation import (assign_hazard_values_to_exposure_data,
                                       make_circular_polygon)
from safe.common.exceptions import InaSAFEError
from third_party.odict import OrderedDict


class VolcanoBuildingImpact(FunctionProvider):
    """Risk plugin for volcano evacuation

    :author AIFDR
    :rating 4
    :param requires category=='hazard' and \
                    subcategory in ['volcano'] and \
                    layertype=='vector'

    :param requires category=='exposure' and \
                    subcategory=='structure' and \
                    layertype=='vector'
    """

    title = tr('Be affected')
    target_field = 'buildings'

    # Function documentation
    synopsis = tr('To assess the impacts of volcano eruption on building.')
    actions = tr('Provide details about how many building would likely be '
                 'affected by each hazard zones.')
    hazard_input = tr('A hazard vector layer can be polygon or point. '
                      'If polygon, it must have "KRB" attribute and the value'
                      'for it are "Kawasan Rawan Bencana I", "Kawasan Rawan '
                      'Bencana II", or "Kawasan Rawan Bencana III."')
    exposure_input = tr('Vector polygon layer extracted from OSM '
                        'where each polygon represents the footprint of '
                        'a building.')
    output = tr('Vector layer contains Map of building exposed to volcanic '
                'hazard zones for each Kawasan Rawan Bencana or radius.')

    parameters = OrderedDict([
        ('distances [km]', [1, 2, 3, 5, 10]),
        ('volcano_name', 'All')])

    def run(self, layers):
        """Risk plugin for volcano hazard on building/structure

        Input
          layers: List of layers expected to contain
              H: Hazard layer of volcano
              P: Vector layer of structure data on the same grid as H

        Counts number of building exposed to each volcano hazard zones.

        Return
          Map of building exposed to volcanic hazard zones
          Table with number of buildings affected
        """

        # Identify hazard and exposure layers
        my_hazard = get_hazard_layer(layers)  # Volcano hazard layer
        my_exposure = get_exposure_layer(layers)

        question = get_question(my_hazard.get_name(),
                                my_exposure.get_name(),
                                self)

        # Input checks
        if not my_hazard.is_vector:
            msg = ('Input hazard %s  was not a vector layer as expected '
                   % my_hazard.get_name())
            raise Exception(msg)

        msg = ('Input hazard must be a polygon or point layer. '
               'I got %s with layer '
               'type %s' % (my_hazard.get_name(),
                            my_hazard.get_geometry_name()))
        if not (my_hazard.is_polygon_data or my_hazard.is_point_data):
            raise Exception(msg)

        if my_hazard.is_point_data:
            # Use concentric circles
            radii = self.parameters['distances [km]']

            centers = my_hazard.get_geometry()
            attributes = my_hazard.get_data()
            rad_m = [x * 1000 for x in radii]  # Convert to meters
            Z = make_circular_polygon(centers, rad_m, attributes=attributes)
            Z.write_to_file('Marapi_evac_zone_%s.shp' % str(radii))  # To check
            category_title = 'Radius'
            my_hazard = Z

            #category_names = ['%s m' % x for x in radii]
            category_names = radii
        else:
            # Use hazard map
            category_title = 'KRB'

            # FIXME (Ole): Change to English and use translation system
            category_names = ['Kawasan Rawan Bencana III',
                              'Kawasan Rawan Bencana II',
                              'Kawasan Rawan Bencana I']

        if not category_title in my_hazard.get_attribute_names():
            msg = ('Hazard data %s did not contain expected '
                   'attribute %s ' % (my_hazard.get_name(), category_title))
            raise InaSAFEError(msg)

        # Run interpolation function for polygon2raster
        P = assign_hazard_values_to_exposure_data(my_hazard, my_exposure)

        # Initialise attributes of output dataset with all attributes
        # from input polygon and a population count of zero
        new_attributes = my_hazard.get_data()

        categories = {}
        for attr in new_attributes:
            attr[self.target_field] = 0
            cat = attr[category_title]
            categories[cat] = 0

        # Count affected population per polygon and total
        total_affected = 0
        for attr in P.get_data():

            # Update building count for associated polygon
            poly_id = attr['polygon_id']
            if poly_id is not None:
                new_attributes[poly_id][self.target_field] += 1

                # Update building count for each category
                cat = new_attributes[poly_id][category_title]
                categories[cat] += 1

            # Update total
            total_affected += 1

        # Count totals
        total = len(my_exposure)

        # Generate simple impact report
        table_body = [question,
                      TableRow([tr('Buildings'), tr('Total'),
                                tr('Cumulative')],
                               header=True),
                      TableRow([tr('All'), format_int(total_affected), ''])]

        cum = 0
        for name in category_names:
            count = categories[name]
            cum += count
            table_body.append(TableRow([name, format_int(count),
                                        format_int(cum)]))

        table_body.append(TableRow(tr('Map shows buildings affected in '
                                      'each of volcano hazard polygons.')))
        impact_table = Table(table_body).toNewlineFreeString()

        # Extend impact report for on-screen display
        table_body.extend([TableRow(tr('Notes'), header=True),
                           tr('Total number of buildings %s in the viewable '
                              'area') % format_int(total),
                           tr('Only buildings available in OpenStreetMap '
                              'are considered.')])
        impact_summary = Table(table_body).toNewlineFreeString()
        map_title = tr('Buildings affected by volcanic hazard zone')

        # Define classes for legend for flooded building counts
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        building_counts = [x[self.target_field] for x in new_attributes]
        cls = [0] + numpy.linspace(1,
                                   max(building_counts),
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
                         transparency=0, size=1)
            style_classes.append(entry)

        # Override style info with new classes and name
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          legend_title=tr('Building Count'))

        # Create vector layer and return
        V = Vector(data=new_attributes,
                   projection=my_hazard.get_projection(),
                   geometry=my_hazard.get_geometry(as_geometry_objects=True),
                   name=tr('Buildings affected by volcanic hazard zone'),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'map_title': map_title,
                             'target_field': self.target_field},
                   style_info=style_info)
        return V
