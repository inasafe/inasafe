from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.vector import Vector
from storage.utilities import ugettext as _


class DKIFloodBuildingImpactFunction(FunctionProvider):
    """Risk plugin for flood impact on building data

    :param requires category=='hazard' and \
                    subcategory=='flood'

    :param requires category=='exposure' and \
                    subcategory=='building' and \
                    layertype=='vector' and \
                    purpose=='dki'
    """

    target_field = 'FLOODED'
    plugin_name = _('Be unavailable to DKI')

    def run(self, layers):
        """Risk plugin for flood building impact
        """

        threshold = 1.0  # Flood threshold [m]

        # Extract data
        H = get_hazard_layer(layers)    # Depth
        E = get_exposure_layer(layers)  # Building locations

        # Interpolate hazard level to building locations
        # FIXME (Ole): How can we reconsile these?
        if H.is_raster:
            I = H.interpolate(E, attribute_name='depth')
        else:
            I = H.interpolate(E)

        # Extract relevant numerical data
        attributes = I.get_data()
        N = len(I)

        # List attributes to carry forward to result layer
        #attribute_names = I.get_attribute_names()

        # Calculate population impact
        count = 0
        buildings = {}
        affected_buildings = {}
        for i in range(N):
            if H.is_raster:
                # Get the interpolated depth
                x = float(attributes[i]['depth'])
                x = x > threshold
            elif H.is_vector:
                # Use interpolated polygon attribute
                res = attributes[i]['FLOODPRONE']
                if res is None:
                    x = False
                else:
                    x = (res.lower() == 'yes')

            usage = attributes[i]['type']
            if usage is not None and usage != 0:
                key = usage
            else:
                key = 'unknown'

            if key not in buildings:
                buildings[key] = 0
                affected_buildings[key] = 0

            # Count all buildings by type
            buildings[key] += 1
            if x is True:
                # Count affected buildings by type
                affected_buildings[key] += 1

            # Count total
            if x is True:
                count += 1

            # Add calculated impact to existing attributes
            attributes[i][self.target_field] = x

        # Lump small entries and 'unknown' into 'other' category
        for usage in buildings.keys():
            x = buildings[usage]
            if x < 25 or usage == 'unknown':
                if 'other' not in buildings:
                    buildings['other'] = 0
                    affected_buildings['other'] = 0

                buildings['other'] += x
                affected_buildings['other'] += affected_buildings[usage]
                del buildings[usage]
                del affected_buildings[usage]

        #print 'Building usage types'
        #for usage in buildings:
        #    print usage, buildings[usage], affected_buildings[usage]

        # Create report
        Hname = H.get_name()
        Ename = E.get_name()
        impact_summary = _('<b>In case of "%s" the estimated impact to "%s" '
                           'the possibility of &#58;</b><br><br><p>' % (Hname,
                                                                        Ename))
        impact_summary += ('<table class="table table-striped condensed'
                           ' bordered-table">'
                           '   <tr><th><b>%s</b></th>'
                           '<th><b>%s</b></th>'
                           '<th><b>%s</b></th></tr>'
                           '   <tr></tr>'
                           % (_('Building type'), _('Flooded'), _('Total')))

        for usage in buildings:
            s = ('   <tr><td>%s&#58;</td><td>%i</td><td>%i</td></tr>'
                 % (usage, affected_buildings[usage], buildings[usage]))
            impact_summary += s

        impact_summary += '</table>'

        impact_summary += '<br>'  # Blank separation row
        impact_summary += '<b>' + _('Assumption') + '&#58;</b><br>'
        impact_summary += _('Buildings will need to be closed when flooding '
                            ' levels exceed %.1f m' % threshold)

        # Create style
        style_classes = [dict(label=_('Opened'), min=0, max=0,
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
                   keywords={'impact_summary': impact_summary},
                   style_info=style_info)
        return V
