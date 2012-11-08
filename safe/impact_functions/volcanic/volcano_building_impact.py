import numpy
from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.impact_functions.core import get_question
from safe.storage.vector import Vector
from safe.common.utilities import ugettext as _
from safe.common.tables import Table, TableRow
from safe.engine.interpolation import assign_hazard_values_to_exposure_data
from safe.engine.interpolation import make_circular_polygon
from safe.common.exceptions import InaSAFEError


class VolcanoBuildingImpact(FunctionProvider):
    """Risk plugin for flood evacuation

    :author AIFDR
    :rating 4
    :param requires category=='hazard' and \
                    subcategory in ['volcano'] and \
                    layertype=='vector'

    :param requires category=='exposure' and \
                    subcategory=='structure' and \
                    layertype=='vector'
    """

    title = _('Be affected')
    target_field = 'buildings'

    parameters = dict(distances=[1000, 2000, 3000, 5000, 10000],
                      volcano_name='All')

    def run(self, layers):
        """Risk plugin for flood population evacuation

        Input
          layers: List of layers expected to contain
              H: Raster layer of volcano depth
              P: Raster layer of population data on the same grid as H

        Counts number of people exposed to flood levels exceeding
        specified threshold.

        Return
          Map of population exposed to volcanic hazard zones
          Table with number of buildings affected
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
            radii = self.parameters['distances']

            centers = H.get_geometry()
            attributes = H.get_data()
            Z = make_circular_polygon(centers, radii, attributes=attributes)
            Z.write_to_file('Marapi_evac_zone_%s.shp' % str(radii))  # To check
            category_title = 'Radius'
            H = Z

            #category_names = ['%s m' % x for x in radii]
            category_names = radii
        else:
            # Use hazard map
            category_title = 'KRB'

            # FIXME (Ole): Change to English and use translation system
            category_names = ['Kawasan Rawan Bencana III',
                              'Kawasan Rawan Bencana II',
                              'Kawasan Rawan Bencana I']

        if not category_title in H.get_attribute_names():
            msg = ('Hazard data %s did not contain expected '
                   'attribute %s ' % (H.get_name(), category_title))
            raise InaSAFEError(msg)

        # Run interpolation function for polygon2raster
        P = assign_hazard_values_to_exposure_data(H, E)

        # Initialise attributes of output dataset with all attributes
        # from input polygon and a population count of zero
        new_attributes = H.get_data()

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
        total = len(E)

        # Generate simple impact report
        table_body = [question,
                      TableRow([_('Buildings'), _('Total'), _('Cumulative')],
                               header=True),
                      TableRow([_('All'), total_affected])]

        cum = 0
        for name in category_names:
            count = categories[name]
            cum += count
            table_body.append(TableRow([name, int(count), int(cum)]))

        table_body.append(TableRow(_('Map shows buildings affected in '
                                     'each of volcano hazard polygons.')))
        impact_table = Table(table_body).toNewlineFreeString()

        # Extend impact report for on-screen display
        table_body.extend([TableRow(_('Notes'), header=True),
                           _('Total number of buildings %i in the viewable '
                             'area') % total,
                           _('Only buildings available in Open Street Map'
                             'are considered.')])
        impact_summary = Table(table_body).toNewlineFreeString()
        map_title = _('Buildings affected by volcanic hazard zone')

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
                label = _('0')
            else:
                label = _('%i - %i') % (lo, hi)

            entry = dict(label=label, colour=colour, min=lo, max=hi,
                         transparency=0, size=1)
            style_classes.append(entry)

        # Override style info with new classes and name
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          legend_title=_('Building Count'))

        # Create vector layer and return
        V = Vector(data=new_attributes,
                   projection=H.get_projection(),
                   geometry=H.get_geometry(as_geometry_objects=True),
                   name=_('Buildings affected by volcanic hazard zone'),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'map_title': map_title,
                             'target_field': self.target_field},
                   style_info=style_info)
        return V
