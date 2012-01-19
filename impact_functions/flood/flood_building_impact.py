from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.vector import Vector
from storage.utilities import ugettext as _


class FloodBuildingImpactFunction(FunctionProvider):
    """Risk plugin for flood impact on building data

    :param requires category=='hazard' and \
                    subcategory.startswith('flood') and \
                    layer_type=='raster' and \
                    unit=='m'

    :param requires category=='exposure' and \
                    subcategory.startswith('building')
    """

    target_field = 'AFFECTED'

    def run(self, layers):
        """Risk plugin for tsunami population
        """

        # Extract data
        H = get_hazard_layer(layers)    # Depth
        E = get_exposure_layer(layers)  # Building locations

        # Interpolate hazard level to building locations
        H = H.interpolate(E)

        # Extract relevant numerical data
        coordinates = E.get_geometry()
        depth = H.get_data()
        N = len(depth)

        # List attributes to carry forward to result layer
        attributes = E.get_attribute_names()

        #print attributes
        #print 'Number of population points', N

        # Calculate population impact
        count = 0
        building_impact = []
        for i in range(N):
            dep = float(depth[i].values()[0])

            # Tag and count
            if dep > 0.1:
                affected = 99.5
                count += 1
            else:
                affected = 0

            # Collect depth and calculated damage
            result_dict = {'AFFECTED': affected,
                           'DEPTH': dep}

            # Carry all original attributes forward
            for key in attributes:
                result_dict[key] = E.get_data(key, i)

            # Record result for this feature
            building_impact.append(result_dict)

        # Create report
        caption = ('<table border="0" width="320px">'
                   '   <tr><th><b>%s</b></th><th><b>%s</b></th></th>'
                    '   <tr></tr>'
                    '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s (> 10 cm) &#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s (< 10 cm) &#58;</td><td>%i</td></tr>'
                    '</table>' % (_('Buildings'), _('Total'),
                                  _('All'), N,
                                  _('Inundated'), count,
                                  _('Not inundated'), N - count))

        # Create vector layer and return
        V = Vector(data=building_impact,
                   projection=E.get_projection(),
                   geometry=coordinates,
                   name='Estimated buildings affected',
                   keywords={'caption': caption})
        return V
