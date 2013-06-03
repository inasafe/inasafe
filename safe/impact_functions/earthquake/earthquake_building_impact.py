from safe.common.utilities import OrderedDict
from safe.impact_functions.core import (
    FunctionProvider, get_hazard_layer, get_exposure_layer, get_question)
from safe.storage.vector import Vector
from safe.common.utilities import (ugettext as tr, format_int)
from safe.common.tables import Table, TableRow
from safe.engine.interpolation import assign_hazard_values_to_exposure_data

import logging

LOGGER = logging.getLogger('InaSAFE')


class EarthquakeBuildingImpactFunction(FunctionProvider):
    """Earthquake impact on building data

    :param requires category=='hazard' and \
                    subcategory=='earthquake'

    :param requires category=='exposure' and \
                    subcategory=='structure' and \
                    layertype=='vector'
    """

    target_field = 'Shake_cls'
    statistics_type = 'class_count'
    statistics_classes = [0, 1, 2, 3]
    title = tr('Be affected')
    parameters = OrderedDict([('low_threshold', 6),
                              ('medium_threshold', 7),
                              ('high_threshold', 8),
                              ('postprocessors', OrderedDict([
                              ('AggregationCategorical', {'on': False})]))
                              ])

    def run(self, layers):
        """Earthquake impact to buildings (e.g. from Open Street Map)
        """

        LOGGER.debug('Running earthquake building impact')

        # Thresholds for mmi breakdown
        t0 = self.parameters['low_threshold']
        t1 = self.parameters['medium_threshold']
        t2 = self.parameters['high_threshold']

        class_1 = tr('Low')
        class_2 = tr('Medium')
        class_3 = tr('High')

        # Extract data
        my_hazard = get_hazard_layer(layers)    # Depth
        my_exposure = get_exposure_layer(layers)  # Building locations

        question = get_question(my_hazard.get_name(),
                                my_exposure.get_name(),
                                self)

        # Define attribute name for hazard levels
        hazard_attribute = 'mmi'

        # Determine if exposure data have NEXIS attributes
        attribute_names = my_exposure.get_attribute_names()
        if ('FLOOR_AREA' in attribute_names and
            'BUILDING_C' in attribute_names and
                'CONTENTS_C' in attribute_names):
            is_NEXIS = True
        else:
            is_NEXIS = False

        # Interpolate hazard level to building locations
        my_interpolate_result = assign_hazard_values_to_exposure_data(
            my_hazard, my_exposure, attribute_name=hazard_attribute)

        # Extract relevant exposure data
        #attribute_names = my_interpolate_result.get_attribute_names()
        attributes = my_interpolate_result.get_data()

        N = len(my_interpolate_result)

        # Calculate building impact
        lo = 0
        me = 0
        hi = 0
        building_values = {}
        contents_values = {}
        for key in range(4):
            building_values[key] = 0
            contents_values[key] = 0
        for i in range(N):
            # Classify building according to shake level
            # and calculate dollar losses

            if is_NEXIS:
                try:
                    area = float(attributes[i]['FLOOR_AREA'])
                except (ValueError, KeyError):
                    #print 'Got area', attributes[i]['FLOOR_AREA']
                    area = 0.0

                try:
                    building_value_density = float(attributes[i]['BUILDING_C'])
                except (ValueError, KeyError):
                    #print 'Got bld value', attributes[i]['BUILDING_C']
                    building_value_density = 0.0

                try:
                    contents_value_density = float(attributes[i]['CONTENTS_C'])
                except (ValueError, KeyError):
                    #print 'Got cont value', attributes[i]['CONTENTS_C']
                    contents_value_density = 0.0

                building_value = building_value_density * area
                contents_value = contents_value_density * area

            try:
                x = float(attributes[i][hazard_attribute])  # MMI
            except TypeError:
                x = 0.0
            if t0 <= x < t1:
                lo += 1
                cls = 1
            elif t1 <= x < t2:
                me += 1
                cls = 2
            elif t2 <= x:
                hi += 1
                cls = 3
            else:
                # Not reported for less than level t0
                cls = 0

            attributes[i][self.target_field] = cls

            if is_NEXIS:
                # Accumulate values in 1M dollar units
                building_values[cls] += building_value
                contents_values[cls] += contents_value

        if is_NEXIS:
            # Convert to units of one million dollars
            for key in range(4):
                building_values[key] = int(building_values[key] / 1000000)
                contents_values[key] = int(contents_values[key] / 1000000)

        if is_NEXIS:
            # Generate simple impact report for NEXIS type buildings
            table_body = [question,
                          TableRow([tr('Hazard Level'),
                                    tr('Buildings Affected'),
                                    tr('Buildings value ($M)'),
                                    tr('Contents value ($M)')],
                                   header=True),
                          TableRow([class_1, format_int(lo),
                                    format_int(building_values[1]),
                                    format_int(contents_values[1])]),
                          TableRow([class_2, format_int(me),
                                    format_int(building_values[2]),
                                    format_int(contents_values[2])]),
                          TableRow([class_3, format_int(hi),
                                    format_int(building_values[3]),
                                    format_int(contents_values[3])])]
        else:
            # Generate simple impact report for unspecific buildings
            table_body = [question,
                          TableRow([tr('Hazard Level'),
                                    tr('Buildings Affected')],
                          header=True),
                          TableRow([class_1, format_int(lo)]),
                          TableRow([class_2, format_int(me)]),
                          TableRow([class_3, format_int(hi)])]

        table_body.append(TableRow(tr('Notes'), header=True))
        table_body.append(tr('High hazard is defined as shake levels greater '
                             'than %i on the MMI scale.') % t2)
        table_body.append(tr('Medium hazard is defined as shake levels '
                             'between %i and %i on the MMI scale.') % (t1, t2))
        table_body.append(tr('Low hazard is defined as shake levels '
                             'between %i and %i on the MMI scale.') % (t0, t1))
        if is_NEXIS:
            table_body.append(tr('Values are in units of 1 million Australian '
                                 'Dollars'))

        impact_summary = Table(table_body).toNewlineFreeString()
        impact_table = impact_summary

        # Create style
        style_classes = [dict(label=class_1, value=t0,
                              colour='#ffff00', transparency=1),
                         dict(label=class_2, value=t1,
                              colour='#ffaa00', transparency=1),
                         dict(label=class_3, value=t2,
                              colour='#ff0000', transparency=1)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes,
                          style_type='categorizedSymbol')

        # For printing map purpose
        map_title = tr('Building affected by earthquake')
        legend_notes = tr('The level of the impact is according to the '
                          'threshold the user input.')
        legend_units = tr('(mmi)')
        legend_title = tr('Impact level')

        # Create vector layer and return
        V = Vector(data=attributes,
                   projection=my_interpolate_result.get_projection(),
                   geometry=my_interpolate_result.get_geometry(),
                   name=tr('Estimated buildings affected'),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'map_title': map_title,
                             'legend_notes': legend_notes,
                             'legend_units': legend_units,
                             'legend_title': legend_title,
                             'target_field': self.target_field,
                             'statistics_type': self.statistics_type,
                             'statistics_classes': self.statistics_classes},
                   style_info=style_info)

        LOGGER.debug('Created vector layer  %s' % str(V))
        return V
