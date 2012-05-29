from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from impact_functions.core import get_question
from storage.vector import Vector
from storage.utilities import ugettext as _
from impact_functions.tables import Table, TableRow


class FloodBuildingImpactFunction(FunctionProvider):
    """Risk plugin for flood impact on building data

    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami'] and \
                    layertype in 'raster'

    :param requires category=='exposure' and \
                    subcategory=='building' and \
                    layertype=='vector'
    """

    target_field = 'AFFECTED'
    plugin_name = _('Be temporarily closed')

    def run(self, layers):
        """Generic building impact
        """

        threshold = 1.0  # Flood threshold [m]

        # Extract data
        H = get_hazard_layer(layers)    # Depth
        E = get_exposure_layer(layers)  # Building locations

        question = get_question(H.get_name(),
                                E.get_name(),
                                self.plugin_name.lower())

        # Interpolate hazard level to building locations
        I = H.interpolate(E, attribute_name='depth')

        # Extract relevant numerical data
        attributes = I.get_data()
        N = len(I)

        # Calculate building impact
        count = 0
        for i in range(N):
            # Determine if the interpolated depth is above threshold
            x = float(attributes[i]['depth']) > threshold

            # Tag and count
            if x is True:
                count += 1

            # Add calculated impact to existing attributes
            attributes[i][self.target_field] = x

        # Generate impact report
        table_body = [question,
                      TableRow([_('Status'), _('Number of buildings')],
                               header=True),
                      TableRow([_('Closed'), count]),
                      TableRow([_('Open'), N - count]),
                      TableRow([_('All'), N])]

        table_body.append(TableRow(_('Notes:'), header=True))
        table_body.append(_('Buildings will need to close if flood'
                            ' levels exceed %.1f m') % threshold)

        impact_summary = Table(table_body).toNewlineFreeString()
        impact_table = impact_summary
        map_title = _('Buildings that need to close due flooding')

        # Create style
        style_classes = [dict(label=_('Open'), min=0, max=0,
                              colour='#1EFC7C', transparency=0, size=1),
                         dict(label=_('Closed'), min=1, max=1,
                              colour='#F31A1C', transparency=0, size=1)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes)

        # Create vector layer and return
        V = Vector(data=attributes,
                   projection=I.get_projection(),
                   geometry=I.get_geometry(),
                   name=_('Estimated buildings affected'),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'map_title': map_title},
                   style_info=style_info)
        return V
