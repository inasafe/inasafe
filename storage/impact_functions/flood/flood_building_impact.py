from django.template.loader import render_to_string
from impact.plugins.core import FunctionProvider
from impact.plugins.core import get_hazard_layer, get_exposure_layer
from impact.storage.vector import Vector
#from django.utils.translation import ugettext as _
from impact.plugins.utilities import PointZoomSize
from impact.plugins.utilities import PointClassColor
from impact.plugins.utilities import PointSymbol
import scipy.stats


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
                    '</table>' % ('Buildings', 'Total',
                                  'All', N,
                                  'Inundated', count,
                                  'Not inundated', N - count))

        # Create vector layer and return
        V = Vector(data=building_impact,
                   projection=E.get_projection(),
                   geometry=coordinates,
                   name='Estimated buildings affected',
                   keywords={'caption': caption})
        return V

    def generate_style(self, data):
        """Generates and SLD file based on the data values
        """

        DEFAULT_SYMBOL = 'circle'

        symbol_field = None
        symbol_keys = [None, '']
        symbol_values = [DEFAULT_SYMBOL, DEFAULT_SYMBOL]

        scale_keys = [10000000000, 10000000, 5000000, 1000000,
                      500000, 250000, 100000]
        scale_values = [5, 5, 5, 5, 5, 8, 14]

        class_keys = ['Not affected', 'Greater than 10 cm']
        class_values = [{'min': 0, 'max': 90,
                         'color': '#cccccc', 'opacity': '0.2'},
                        {'min': 90, 'max': 100,
                         'color': '#F31a0c', 'opacity': '1'}]

        if self.symbol_field in data.get_attribute_names():
            symbol_field = self.symbol_field

            symbol_keys.extend(['Church/Mosque', 'Commercial (office)',
                                'Hotel',
                                'Medical facility', 'Other',
                                'Other industrial',
                                'Residential', 'Retail', 'School',
                                'Unknown', 'Warehouse'])

            symbol_values.extend([DEFAULT_SYMBOL, DEFAULT_SYMBOL,
                                  DEFAULT_SYMBOL,
                                  DEFAULT_SYMBOL, DEFAULT_SYMBOL,
                                  DEFAULT_SYMBOL,
                                  DEFAULT_SYMBOL, DEFAULT_SYMBOL,
                                  DEFAULT_SYMBOL,
                                  DEFAULT_SYMBOL, DEFAULT_SYMBOL])

        params = dict(name=data.get_name(),
                      damage_field=self.target_field,
                      symbol_field=symbol_field,
                      symbols=dict(zip(symbol_keys, symbol_values)),
                      scales=dict(zip(scale_keys, scale_values)),
                      classifications=dict(zip(class_keys, class_values)))

        return render_to_string('impact/styles/point_classes.sld', params)
