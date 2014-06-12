# coding=utf-8
"""
InaSAFE Disaster risk tool by Australian Aid - Volcano Impact on buildings

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from safe.common.utilities import OrderedDict
from safe.engine.utilities import buffer_points
from safe.impact_functions.core import (
    FunctionProvider, get_hazard_layer, get_exposure_layer, get_question)
from safe.impact_functions.impact_function_metadata import (
    ImpactFunctionMetadata)
from safe.metadata import (
    hazard_volcano,
    unit_volcano_categorical,
    layer_vector_polygon,
    layer_vector_point,
    exposure_structure,
    unit_building_type_type,
    exposure_definition,
    hazard_definition,
    unit_building_generic)
from safe.storage.vector import Vector
from safe.common.utilities import (
    ugettext as tr,
    format_int,
    humanize_class,
    create_classes,
    create_label,
    get_thousand_separator,
    get_non_conflicting_attribute_name)
from safe.common.tables import Table, TableRow
from safe.engine.interpolation import (
    assign_hazard_values_to_exposure_data)
from safe.common.exceptions import InaSAFEError, ZeroImpactException


class VolcanoBuildingImpact(FunctionProvider):
    # noinspection PyUnresolvedReferences
    """Risk plugin for volcano building impact.

    :author AIFDR
    :rating 4
    :param requires category=='hazard' and \
                    subcategory in ['volcano'] and \
                    layertype=='vector'

    :param requires category=='exposure' and \
                    subcategory=='structure' and \
                    layertype=='vector'
    """

    class Metadata(ImpactFunctionMetadata):
        """Metadata for Volcano Building Impact.

        .. versionadded:: 2.1

        We only need to re-implement get_metadata(), all other behaviours
        are inherited from the abstract base class.
        """

        @staticmethod
        def get_metadata():
            """Return metadata as a dictionary.

            This is a static method. You can use it to get the metadata in
            dictionary format for an impact function.

            :returns: A dictionary representing all the metadata for the
                concrete impact function.
            :rtype: dict
            """
            dict_meta = {
                'id': 'VolcanoBuildingImpact',
                'name': tr('Volcano Building Impact'),
                'impact': tr('Be affected'),
                'author': 'AIFDR',
                'date_implemented': 'N/A',
                'overview': tr('To assess the impacts of volcano eruption '
                               'on building.'),
                'categories': {
                    'hazard': {
                        'definition': hazard_definition,
                        'subcategory': hazard_volcano,
                        'units': [unit_volcano_categorical],
                        'layer_constraints': [
                            layer_vector_polygon,
                            layer_vector_point
                        ]
                    },
                    'exposure': {
                        'definition': exposure_definition,
                        'subcategory': exposure_structure,
                        'units': [
                            unit_building_type_type,
                            unit_building_generic],
                        'layer_constraints': [layer_vector_polygon]
                    }
                }
            }
            return dict_meta

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
        """Risk plugin for volcano hazard on building/structure.

        Counts number of building exposed to each volcano hazard zones.

        :param layers: List of layers expected to contain.
                * hazard_layer: Hazard layer of volcano
                * exposure_layer: Vector layer of structure data on
                the same grid as hazard_layer

        :returns: Map of building exposed to volcanic hazard zones.
                  Table with number of buildings affected
        :rtype: dict
        """
        # Identify hazard and exposure layers
        hazard_layer = get_hazard_layer(layers)  # Volcano hazard layer
        exposure_layer = get_exposure_layer(layers)
        is_point_data = False

        question = get_question(
            hazard_layer.get_name(), exposure_layer.get_name(), self)

        # Input checks
        if not hazard_layer.is_vector:
            msg = ('Input hazard %s  was not a vector layer as expected '
                   % hazard_layer.get_name())
            raise Exception(msg)

        msg = ('Input hazard must be a polygon or point layer. I got %s '
               'with layer type %s' %
               (hazard_layer.get_name(), hazard_layer.get_geometry_name()))
        if not (hazard_layer.is_polygon_data or hazard_layer.is_point_data):
            raise Exception(msg)

        if hazard_layer.is_point_data:
            # Use concentric circles
            radii = self.parameters['distances [km]']
            is_point_data = True

            centers = hazard_layer.get_geometry()
            attributes = hazard_layer.get_data()
            rad_m = [x * 1000 for x in radii]  # Convert to meters
            hazard_layer = buffer_points(centers, rad_m, data_table=attributes)
            # To check
            category_title = 'Radius'
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

        # Get names of volcanoes considered
        if name_attribute in hazard_layer.get_attribute_names():
            volcano_name_list = []
            for row in hazard_layer.get_data():
                # Run through all polygons and get unique names
                volcano_name_list.append(row[name_attribute])

            volcano_names = ''
            for name in volcano_name_list:
                volcano_names += '%s, ' % name
            volcano_names = volcano_names[:-2]  # Strip trailing ', '
        else:
            volcano_names = tr('Not specified in data')

        # Check if category_title exists in hazard_layer
        if not category_title in hazard_layer.get_attribute_names():
            msg = ('Hazard data %s did not contain expected '
                   'attribute %s ' % (hazard_layer.get_name(), category_title))
            # noinspection PyExceptionInherit
            raise InaSAFEError(msg)

        # Find the target field name that has no conflict with default
        # target
        attribute_names = hazard_layer.get_attribute_names()
        new_target_field = get_non_conflicting_attribute_name(
            self.target_field, attribute_names)
        self.target_field = new_target_field

        # Run interpolation function for polygon2raster
        interpolated_layer = assign_hazard_values_to_exposure_data(
            hazard_layer, exposure_layer)

        # Initialise attributes of output dataset with all attributes
        # from input polygon and a building count of zero
        new_data_table = hazard_layer.get_data()

        categories = {}
        for row in new_data_table:
            row[self.target_field] = 0
            category = row[category_title]
            categories[category] = 0

        # Count impacted building per polygon and total
        for row in interpolated_layer.get_data():
            # Update building count for associated polygon
            poly_id = row['polygon_id']
            if poly_id is not None:
                new_data_table[poly_id][self.target_field] += 1

                # Update building count for each category
                category = new_data_table[poly_id][category_title]
                categories[category] += 1

        # Count totals
        total = len(exposure_layer)

        # Generate simple impact report
        blank_cell = ''
        table_body = [question,
                      TableRow([tr('Volcanoes considered'),
                                '%s' % volcano_names, blank_cell],
                               header=True),
                      TableRow([tr('Distance [km]'), tr('Total'),
                                tr('Cumulative')],
                               header=True)]

        cumulative = 0
        for name in category_names:
            # prevent key error
            count = categories.get(name, 0)
            cumulative += count
            if is_point_data:
                name = int(name) / 1000
            table_body.append(TableRow([name, format_int(count),
                                        format_int(cumulative)]))

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
        building_counts = [x[self.target_field] for x in new_data_table]

        if max(building_counts) == 0 == min(building_counts):
            table_body = [
                question,
                TableRow([tr('Number of buildings affected'),
                          '%s' % format_int(cumulative), blank_cell],
                         header=True)]
            my_message = Table(table_body).toNewlineFreeString()
            raise ZeroImpactException(my_message)

        # Create style
        colours = ['#FFFFFF', '#38A800', '#79C900', '#CEED00',
                   '#FFCC00', '#FF6600', '#FF0000', '#7A0000']

        # Create Classes
        classes = create_classes(building_counts, len(colours))
        # Create Interval Classes
        interval_classes = humanize_class(classes)

        style_classes = []
        for i in xrange(len(colours)):
            style_class = dict()
            style_class['label'] = create_label(interval_classes[i])
            if i == 0:
                style_class['min'] = 0
            else:
                style_class['min'] = classes[i - 1]
            style_class['transparency'] = 30
            style_class['colour'] = colours[i]
            style_class['max'] = classes[i]
            style_classes.append(style_class)

        # Override style info with new classes and name
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          style_type='graduatedSymbol')

        # For printing map purpose
        map_title = tr('Buildings affected by volcanic hazard zone')
        legend_notes = tr('Thousand separator is represented by %s' %
                          get_thousand_separator())
        legend_units = tr('(building)')
        legend_title = tr('Building count')

        # Create vector layer and return
        impact_layer = Vector(
            data=new_data_table,
            projection=hazard_layer.get_projection(),
            geometry=hazard_layer.get_geometry(as_geometry_objects=True),
            name=tr('Buildings affected by volcanic hazard zone'),
            keywords={'impact_summary': impact_summary,
                      'impact_table': impact_table,
                      'target_field': self.target_field,
                      'map_title': map_title,
                      'legend_notes': legend_notes,
                      'legend_units': legend_units,
                      'legend_title': legend_title},
            style_info=style_info)
        return impact_layer
