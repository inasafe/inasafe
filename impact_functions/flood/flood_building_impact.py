from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.vector import Vector
from storage.utilities import ugettext as _


class FloodBuildingImpactFunction(FunctionProvider):
    """Risk plugin for flood impact on building data

    :param requires category=='hazard' and \
                    subcategory.startswith('flood') and \
                    layertype in ['raster', 'vector']

    :param requires category=='exposure' and \
                    subcategory.startswith('building') and \
                    layertype=='vector'
    """

    target_field = 'AFFECTED'
    plugin_name = _('Be temporarily closed')

    # Is never called but would be nice to do here
    #def __init__(self):
    #    self.target_field = 'AFFECTED'
    #    self.plugin_name = _('Temporarily Closed')

    def run(self, layers):
        """Risk plugin for tsunami population
        """

        threshold = 1.0  # Flood threshold [m]

        # Extract data
        H = get_hazard_layer(layers)    # Depth
        E = get_exposure_layer(layers)  # Building locations

        # FIXME (Ole): interpolate does not carry original name through,
        # so get_name gives "Vector Layer" :-)

        # Interpolate hazard level to building locations
        I = H.interpolate(E)

        # Extract relevant numerical data
        attributes = I.get_data()
        N = len(I)

        # List attributes to carry forward to result layer
        attribute_names = E.get_attribute_names()

        # Calculate population impact
        count = 0
        building_impact = []
        for i in range(N):
            if H.is_raster:
                # Get the interpolated depth
                x = float(attributes[i].values()[0])
                x = x > threshold
            elif H.is_vector:
                # Use interpolated polygon attribute
                x = attributes[i]['Affected']

            # Tag and count
            if x is True:
                affected = 1  # FIXME Ole this is unused
                count += 1
            else:
                affected = 0  # FIXME Ole this is unused

            # Collect depth and calculated damage
            result_dict = {self.target_field: x}

            # Carry all original attributes forward
            # FIXME (Ole): Make this part of the interpolation (see issue #101)
            for key in attribute_names:
                result_dict[key] = E.get_data(key, i)

            # Record result for this feature
            building_impact.append(result_dict)

        # Create report
        Hname = H.get_name()
        Ename = E.get_name()
        impact_summary = _('<b>In case of hazard "%s" the estimated impact to '
                           'exposure "%s" '
                           'is&#58;</b><br><br><p>' % (Hname, Ename))
        impact_summary += ('<table border="0" width="320px">'
                   '   <tr><th><b>%s</b></th><th><b>%s</b></th></th>'
                    '   <tr></tr>'
                    '   <tr><td>%s &#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s &#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s &#58;</td><td>%i</td></tr>'
                    '</table>' % (_('Status'), _('Number of buildings'),
                                  _('Closed'), count,
                                  _('Opened'), N - count,
                                  _('All'), N))



        impact_summary += '<br>'  # Blank separation row
        impact_summary += '<b>' + _('Assumption') + '&#58;</b><br>'
        impact_summary += _('Buildings that will need to close when flood'
                            ' levels exceed %.1f m' % threshold)

        # Create style
        style_classes = [dict(label=_('Opened'), min=0, max=0,
                              colour='#1EFC7C', transparency=0, size=1),
                         dict(label=_('Closed'), min=1, max=1,
                              colour='#F31A1C', transparency=0, size=1)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes)

        # Create vector layer and return
        V = Vector(data=building_impact,
                   projection=E.get_projection(),
                   geometry=E.get_geometry(),
                   name=_('Estimated buildings affected'),
                   keywords={'impact_summary': impact_summary},
                   style_info=style_info)
        return V
