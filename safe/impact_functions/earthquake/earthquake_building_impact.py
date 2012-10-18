from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.impact_functions.core import get_question
from safe.storage.vector import Vector
from safe.common.utilities import ugettext as tr
from safe.common.tables import Table, TableRow
from safe.engine.interpolation import assign_hazard_values_to_exposure_data

import logging

LOGGER = logging.getLogger('InaSAFE')


class EarthquakeBuildingImpactFunction(FunctionProvider):
    """Inundation impact on building data

    :param requires category=='hazard' and \
                    subcategory=='earthquake'

    :param requires category=='exposure' and \
                    subcategory=='structure' and \
                    layertype=='vector'
    """

    target_field = 'Shake_cls'
    title = tr('Be affected')

    def run(self, layers):
        """Earthquake impact to buildings (e.g. from Open Street Map)
        """

        LOGGER.debug('Running earthquake building impact')

        # Thresholds for mmi breakdown
        t0 = 6
        t1 = 7
        t2 = 8

        class_1 = tr('Low')
        class_2 = tr('Medium')
        class_3 = tr('High')

        # Extract data
        H = get_hazard_layer(layers)    # Depth
        E = get_exposure_layer(layers)  # Building locations

        # Thin out buildings for testing
        #E = Vector(geometry=E.get_geometry()[::1000],
        #           data=E.get_data()[::1000],
        #           geometry_type=E.get_geometry_type(),
        #           projection=E.get_projection(),
        #           name=E.get_name())

        question = get_question(H.get_name(),
                                E.get_name(),
                                self)

        # Determine attribute name for hazard levels
        hazard_attribute = 'mmi'

        # Interpolate hazard level to building locations
        I = assign_hazard_values_to_exposure_data(H, E,
                                             attribute_name=hazard_attribute)

        # Extract relevant exposure data
        #attribute_names = I.get_attribute_names()
        attributes = I.get_data()

        N = len(I)

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

            x = float(attributes[i][hazard_attribute])  # MMI
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

            # Accumulate values in 1M dollar units
            building_values[cls] += building_value
            contents_values[cls] += contents_value

        # Convert to units of one million dollars
        for key in range(4):
            building_values[key] = int(building_values[key] / 1000000)
            contents_values[key] = int(contents_values[key] / 1000000)

        # Generate simple impact report
        table_body = [question,
                      TableRow([tr('Hazard Level'),
                                tr('Buildings Affected'),
                                tr('Buildings value ($M)'),
                                tr('Contents value ($M)')],
                               header=True),
                      TableRow([class_1, lo,
                                building_values[1],
                                contents_values[1]]),
                      TableRow([class_2, me,
                                building_values[2],
                                contents_values[2]]),
                      TableRow([class_3, hi,
                                building_values[3],
                                contents_values[3]])]

        table_body.append(TableRow(tr('Notes'), header=True))
        table_body.append(tr('High hazard is defined as shake levels greater '
                             'than %i on the MMI scale.') % t2)
        table_body.append(tr('Medium hazard is defined as shake levels '
                             'between %i and %i on the MMI scale.') % (t1, t2))
        table_body.append(tr('Low hazard is defined as shake levels '
                             'between %i and %i on the MMI scale.') % (t0, t1))
        table_body.append(tr('Values are in units of 1 million Australian '
                             'Dollars'))

        impact_summary = Table(table_body).toNewlineFreeString()
        impact_table = impact_summary
        map_title = tr('Buildings inundated')

        # Create style
        style_classes = [dict(label=class_1, min=1, max=1,
                              colour='#ffff00', transparency=1),
                         dict(label=class_2, min=2, max=2,
                              colour='#ffaa00', transparency=1),
                         dict(label=class_3, min=3, max=3,
                              colour='#ff0000', transparency=1)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes)

        # Create vector layer and return
        V = Vector(data=attributes,
                   projection=I.get_projection(),
                   geometry=I.get_geometry(),
                   name=tr('Estimated buildings affected'),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'map_title': map_title,
                             'target_field': self.target_field},
                   style_info=style_info)

        LOGGER.debug('Created vector layer  %s' % str(V))
        return V
