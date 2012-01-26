"""Impact function based on Padang 2009 post earthquake survey

This impact function estimates percentual damage to buildings as a
function of ground shaking measured in MMI.
Buildings are assumed to fall the 9 classes below as described in
the Geoscience Australia/ITB 2009 Padang earthquake
survey (http://trove.nla.gov.au/work/38470066).

Class Building Type                              Median (MMI)  Beta (MMI)
-------------------------------------------------------------------------
1     URM with river rock walls                        7.5     0.11
2     URM with Metal Roof                              8.3     0.1
3     Timber frame with masonry in-fill                8.8     0.11
4     RC medium rise Frame with Masonry in-fill walls  8.4     0.05
5     Timber frame with stucco in-fill                 9.2     0.11
6     Concrete Shear wall  high rise* Hazus C2H        9.7     0.15
7     RC low rise Frame with Masonry in-fill walls     9       0.08
8     Confined Masonry                                 8.9     0.07
9     Timber frame residential                        10.5     0.15
"""

from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.vector import Vector
from storage.utilities import ugettext as _
from engine.numerics import cdf
from impact_functions.mappings import osm2padang, sigab2padang


# Damage curves for each of the nine classes derived from the Padang survey
damage_curves = {'1': dict(median=7.5, beta=0.11),
                 '2': dict(median=8.3, beta=0.1),
                 '3': dict(median=8.8, beta=0.11),
                 '4': dict(median=8.4, beta=0.05),
                 '5': dict(median=9.2, beta=0.11),
                 '6': dict(median=9.7, beta=0.15),
                 '7': dict(median=9.0, beta=0.08),
                 '8': dict(median=8.9, beta=0.07),
                 '9': dict(median=10.5, beta=0.15)}


class PadangEarthquakeBuildingDamageFunction(FunctionProvider):
    """Risk plugin for Padang earthquake damage to buildings

    :param requires category=='hazard' and \
                    subcategory.startswith('earthquake') and \
                    layer_type=='raster' and \
                    unit=='MMI'

    :param requires category=='exposure' and \
                    subcategory.startswith('building') and \
                    layer_type=='vector' and \
                    datatype in ['osm', 'itb', 'sigab']
    """
    
    # FIXME (TD): make the plugin_name work
    #plugin_name = "My Padang Test Function 4"

    def run(self, layers):
        """Risk plugin for Padang building survey
        """

        # Extract data
        H = get_hazard_layer(layers)    # Ground shaking
        E = get_exposure_layer(layers)  # Building locations

        datatype = E.get_keywords()['datatype']
        if datatype.lower() == 'osm':
            # Map from OSM attributes to the padang building classes
            E = osm2padang(E)
            vclass_tag = 'VCLASS'
        elif datatype.lower() == 'sigab':
            E = sigab2padang(E)
            vclass_tag = 'VCLASS'
        else:
            vclass_tag = 'TestBLDGCl'

        # Interpolate hazard level to building locations
        H = H.interpolate(E)

        # Extract relevant numerical data
        coordinates = E.get_geometry()
        shaking = H.get_data()
        N = len(shaking)

        # List attributes to carry forward to result layer
        attributes = E.get_attribute_names()

        # Calculate building damage
        count50 = 0
        count25 = 0
        count10 = 0
        count0 = 0
        building_damage = []
        for i in range(N):
            mmi = float(shaking[i].values()[0])

            building_class = E.get_data(vclass_tag, i)

            building_type = str(int(building_class))
            damage_params = damage_curves[building_type]
            beta = damage_params['beta']
            median = damage_params['median']
            percent_damage = cdf(mmi, mu=median, sigma=beta) * 100

            # Collect shake level and calculated damage
            result_dict = {self.target_field: percent_damage,
                           'MMI': mmi}

            # Carry all orginal attributes forward
            for key in attributes:
                result_dict[key] = E.get_data(key, i)

            # Record result for this feature
            building_damage.append(result_dict)

            # Calculate statistics
            if percent_damage < 10:
                count0 += 1

            if 10 <= percent_damage < 25:
                count10 += 1

            if 25 <= percent_damage < 50:
                count25 += 1

            if 50 <= percent_damage:
                count50 += 1

        # Create report
        caption = ('<font size="3"> <table border="0" width="320px">'
                   '   <tr><th><b>%s</b></th><th><b>%s</b></th></th>'
                    '   <tr></tr>'
                    '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s (<10%%)&#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s (10-25%%)&#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s (25-50%%)&#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s (50-100%%)&#58;</td><td>%i</td></tr>'
                    '</table></font>' % (_('Buildings'), _('Total'),
                                  _('All'), N,
                                  _('No damage'), count0,
                                  _('Low damage'), count10,
                                  _('Medium damage'), count25,
                                  _('High damage'), count50))

        # Create vector layer and return
        V = Vector(data=building_damage,
                   projection=E.get_projection(),
                   geometry=coordinates,
                   name='Estimated pct damage',
                   keywords={'caption': caption})
        return V
