from third_party.odict import OrderedDict
from safe.impact_functions.core import (
    FunctionProvider, get_hazard_layer, get_exposure_layer, get_question)
from safe.storage.vector import Vector
from safe.common.utilities import (
    ugettext as tr,
    format_int,
    humanize_class,
    create_classes,
    create_label)
from safe.common.tables import Table, TableRow
from safe.engine.interpolation import (
    assign_hazard_values_to_exposure_data, make_circular_polygon)
from safe.common.exceptions import InaSAFEError


class VolcanoBuildingImpact(FunctionProvider):
    """Risk plugin for volcano building impact

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

    # Function documentations
    synopsis = tr('To assess the impacts of volcano eruption on building.')
    actions = tr(
        'Provide details about how many building would likely be affected by '
        'each hazard zones.')
    hazard_input = tr(
        'A hazard vector layer can be polygon or point. If polygon, it must '
        'have "KRB" attribute and the values for it are "Kawasan Rawan '
        'Bencana I", "Kawasan Rawan Bencana II", or "Kawasan Rawan Bencana '
        'III." If you want to see the name of the volcano in the result, '
        'you need to add "NAME" attribute for point data or "GUNUNG" '
        'attribute for polygon data.')
    exposure_input = tr(
        'Vector polygon layer extracted from OSM where each polygon '
        'represents the footprint of a building.')
    output = tr(
        'Vector layer contains Map of building exposed to volcanic hazard '
        'zones for each Kawasan Rawan Bencana or radius.')

    parameters = OrderedDict([
        ('distances [km]', [3, 5, 10])])

    def run(self, layers):
        """Risk plugin for volcano hazard on building/structure

        Input
          layers: List of layers expected to contain
              my_hazard: Hazard layer of volcano
              my_exposure: Vector layer of structure data on
              the same grid as my_hazard

        Counts number of building exposed to each volcano hazard zones.

        Return
          Map of building exposed to volcanic hazard zones
          Table with number of buildings affected
        """

        # Identify hazard and exposure layers
        my_hazard = get_hazard_layer(layers)  # Volcano hazard layer
        my_exposure = get_exposure_layer(layers)
        is_point_data = False

        question = get_question(my_hazard.get_name(),
                                my_exposure.get_name(),
                                self)

        # Input checks
        if not my_hazard.is_vector:
            msg = ('Input hazard %s  was not a vector layer as expected '
                   % my_hazard.get_name())
            raise Exception(msg)

        msg = ('Input hazard must be a polygon or point layer. I got %s '
               'with layer type %s' %
               (my_hazard.get_name(), my_hazard.get_geometry_name()))
        if not (my_hazard.is_polygon_data or my_hazard.is_point_data):
            raise Exception(msg)

        if my_hazard.is_point_data:
            # Use concentric circles
            radii = self.parameters['distances [km]']
            is_point_data = True

            centers = my_hazard.get_geometry()
            attributes = my_hazard.get_data()
            rad_m = [x * 1000 for x in radii]  # Convert to meters
            Z = make_circular_polygon(centers, rad_m, attributes=attributes)
            # To check
            category_title = 'Radius'
            my_hazard = Z

            category_names = rad_m
            name_attribute = 'NAME'  # As in e.g. the Smithsonian dataset
        else:
            # Use hazard map
            category_title = 'KRB'

            # FIXME (Ole): Change to English and use translation system
            category_names = ['Kawasan Rawan Bencana III',
                              'Kawasan Rawan Bencana II',
                              'Kawasan Rawan Bencana I']
            name_attribute = 'GUNUNG'  # As in e.g. BNPB hazard map

        # Get names of volcanos considered
        if name_attribute in my_hazard.get_attribute_names():
            D = {}
            for att in my_hazard.get_data():
                # Run through all polygons and get unique names
                D[att[name_attribute]] = None

            volcano_names = ''
            for name in D:
                volcano_names += '%s, ' % name
            volcano_names = volcano_names[:-2]  # Strip trailing ', '
        else:
            volcano_names = tr('Not specified in data')

        if not category_title in my_hazard.get_attribute_names():
            msg = ('Hazard data %s did not contain expected '
                   'attribute %s ' % (my_hazard.get_name(), category_title))
            raise InaSAFEError(msg)

        # Run interpolation function for polygon2raster
        P = assign_hazard_values_to_exposure_data(my_hazard, my_exposure)

        # Initialise attributes of output dataset with all attributes
        # from input polygon and a building count of zero
        new_attributes = my_hazard.get_data()

        categories = {}
        for attr in new_attributes:
            attr[self.target_field] = 0
            cat = attr[category_title]
            categories[cat] = 0

        # Count impacted building per polygon and total
        for attr in P.get_data():

            # Update building count for associated polygon
            poly_id = attr['polygon_id']
            if poly_id is not None:
                new_attributes[poly_id][self.target_field] += 1

                # Update building count for each category
                cat = new_attributes[poly_id][category_title]
                categories[cat] += 1

        # Count totals
        total = len(my_exposure)

        # Generate simple impact report
        blank_cell = ''
        table_body = [question,
                      TableRow([tr('Volcanos considered'),
                                '%s' % volcano_names, blank_cell],
                               header=True),
                      TableRow([tr('Distance [km]'), tr('Total'),
                                tr('Cumulative')],
                               header=True)]

        cum = 0
        for name in category_names:
            # prevent key error
            count = categories.get(name, 0)
            cum += count
            if is_point_data:
                name = int(name) / 1000
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

        # Create style
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']
        building_counts = [x[self.target_field] for x in new_attributes]
        classes = create_classes(building_counts, len(colours))
        interval_classes = humanize_class(classes)
        style_classes = []
        for i in xrange(len(colours)):
            style_class = dict()
            style_class['label'] = create_label(interval_classes[i])
            if i == 0:
                transparency = 100
                style_class['min'] = 0
            else:
                transparency = 30
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
        map_title = tr('Building affected by volcanic hazard zone')
        legend_notes = tr('Thousand separator is represented by \'.\'')
        legend_units = tr('(building)')
        legend_title = tr('Building count')

        # Create vector layer and return
        V = Vector(data=new_attributes,
                   projection=my_hazard.get_projection(),
                   geometry=my_hazard.get_geometry(as_geometry_objects=True),
                   name=tr('Buildings affected by volcanic hazard zone'),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'target_field': self.target_field,
                             'map_title': map_title,
                             'legend_notes': legend_notes,
                             'legend_units': legend_units,
                             'legend_title': legend_title},
                   style_info=style_info)
        return V
