from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.impact_functions.core import get_question
from safe.storage.vector import Vector
from safe.common.utilities import ugettext as _
from safe.common.tables import Table, TableRow
from safe.engine.interpolation import assign_hazard_values_to_exposure_data


#FIXME: need to normalise all raster data Ole/Kristy
class CategorisedHazardBuildingImpactFunction(FunctionProvider):
    """Impact plugin for categorising hazard impact on building data

    :author The Author
    :rating The Rating
    :detail The Detail
    :param requires category=='hazard' and \
                    unit=='normalised' and \
                    layertype=='raster'

    :param requires category=='exposure' and \
                    subcategory=='structure' and \
                    layertype=='vector'
    :citation citation1
    :citation citation2 \
                next citation2
    """

    target_field = 'ICLASS'
    title = _('Be affected')

    def run(self, layers):
        """Impact plugin for hazard impact
        """

        # Extract data
        H = get_hazard_layer(layers)    # Value
        E = get_exposure_layer(layers)  # Building locations

        question = get_question(H.get_name(),
                                E.get_name(),
                                self)

        # Interpolate hazard level to building locations
        H = assign_hazard_values_to_exposure_data(H, E,
                                             attribute_name='hazard_level',
                                             mode='constant')

        # Extract relevant numerical data
        coordinates = H.get_geometry()
        category = H.get_data()
        N = len(category)

        # List attributes to carry forward to result layer
        #attributes = E.get_attribute_names()

        # Calculate building impact according to guidelines
        count2 = 0
        count1 = 0
        count0 = 0
        building_impact = []
        for i in range(N):
            # Get category value
            val = float(category[i]['hazard_level'])

            # Classify buildings according to value
##            if val >= 2.0 / 3:
##                affected = 2
##                count2 += 1
##            elif 1.0 / 3 <= val < 2.0 / 3:
##                affected = 1
##                count1 += 1
##            else:
##                affected = 0
##                count0 += 1
            ## FIXME it would be good if the affected were words not numbers
            ## FIXME need to read hazard layer and see category or keyword
            if val == 3:
                affected = 3
                count2 += 1
            elif val == 2:
                affected = 2
                count1 += 1
            elif val == 1:
                affected = 1
                count0 += 1
            else:
                affected = 'None'

            # Collect depth and calculated damage
            result_dict = {self.target_field: affected,
                           'CATEGORY': val}

            # Record result for this feature
            building_impact.append(result_dict)

        # Create impact report
        # Generate impact summary
        table_body = [question,
                      TableRow([_('Category'), _('Affected')],
                               header=True),
                      TableRow([_('High'), count2]),
                      TableRow([_('Medium'), count1]),
                      TableRow([_('Low'), count0]),
                      TableRow([_('All'), N])]

        table_body.append(TableRow(_('Notes'), header=True))
        table_body.append(_('Categorised hazard has only 3'
                            ' classes, high, medium and low.'))

        impact_summary = Table(table_body).toNewlineFreeString()
        impact_table = impact_summary
        map_title = _('Categorised hazard impact on buildings')

        #FIXME it would be great to do categorized rather than grduated
        # Create style
        style_classes = [dict(label=_('Low'), min=1, max=1,
                              colour='#1EFC7C', transparency=0, size=1),
                         dict(label=_('Medium'), min=2, max=2,
                              colour='#FFA500', transparency=0, size=1),
                         dict(label=_('High'), min=3, max=3,
                              colour='#F31A1C', transparency=0, size=1)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes)

        # Create vector layer and return
        name = 'Buildings Affected'

        V = Vector(data=building_impact,
                   projection=E.get_projection(),
                   geometry=coordinates,
                   geometry_type=E.geometry_type,
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'map_title': map_title},
                   name=name,
                   style_info=style_info)
        return V
