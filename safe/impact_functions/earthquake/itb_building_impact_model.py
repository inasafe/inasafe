"""Impact function based on ITB vulnerability model

   This model was developed by Institut Tecknologi Bandung (ITB) and
   implemented by Dr Hyeuk Ryu, Geoscience Australia

   Reference:

   Indonesian Earthquake Building-Damage and Fatality Models and
   Post Disaster Survey Guidelines Development,
   Bali, 27-28 February 2012, 54pp.

   Methodology:
   The ITB vulnerabilty model was heuristically developed (i.e. based on
   expert opinion) through the Bali workshop. The model is defined with
   two parameters (median, and lognormal standard deviation) of cumulative
   lognormal distribution. The building type classification used in the
   model was endorsed by expert group in thel Bali workshop.

   Limitations:
   The current model contains some dummy numbers.
   It should be updated once ITB publishes the final report on
   earthquake building damage model development.

"""

import os
from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.storage.vector import Vector
from safe.common.numerics import lognormal_cdf
from safe.common.utilities import ugettext as tr
from safe.common.utilities import verify
from safe.engine.interpolation import assign_hazard_values_to_exposure_data

path = os.path.dirname(__file__)


class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, _item):
        try:
            return dict.__getitem__(self, _item)
        except KeyError:
            value = self[_item] = type(self)()
            return value

# read vulnerability information
eng_filename = os.path.join(path, 'itb_vulnerability_eng.csv')
non_eng_filename = os.path.join(path, 'itb_vulnerability_non_eng.csv')

vul_curves = AutoVivification()
# Non-Engineere dbuildings
a = open(non_eng_filename).readlines()
for item in a[1:]:
    tmp = item.strip('\n').split(',')
    idx = tmp[0]  # structural type index
    vul_curves[idx]['median'] = float(tmp[5])
    vul_curves[idx]['beta'] = float(tmp[6])

# Engineered buildings
a = open(eng_filename).readlines()
for item in a[1:]:
    tmp = item.strip('\n').split(',')
    idx = tmp[0]  # structural type index
    vul_curves[idx]['median'] = float(tmp[6])
    vul_curves[idx]['beta'] = float(tmp[7])


class ITBEarthquakeBuildingDamageFunction(FunctionProvider):
    """Risk plugin for ITB earthquake damage to buildings in Padang

    :param requires category=='hazard' and \
                    subcategory=='earthquake' and \
                    layertype=='raster' and \
                    unit=='MMI' and \
                    disabled=='True'

    :param requires category=='exposure' and \
                    subcategory=='structure' and \
                    layertype=='vector' and \
                    datatype in ['osm', 'itb', 'sigab']
    """

    title = tr('Be damaged depending on building type')

    def run(self, layers):
        """Risk plugin for Padang building survey
        """

        # Extract data
        H = get_hazard_layer(layers)    # Ground shaking
        E = get_exposure_layer(layers)  # Building locations

        datatype = E.get_keywords()['datatype']
        vclass_tag = 'ITB_Class'
        if datatype.lower() == 'osm':
            # Map from OSM attributes to the ITB building classes
#            Emap = osm2itb(E)
            print 'osm2itb has not been implemented'
        elif datatype.lower() == 'sigab':
#            Emap = sigabitb(E)
            print 'sigab2itb has not been implemented'
        elif datatype.lower() == 'itb':
            Emap = E

        # Interpolate hazard level to building locations
        Hi = assign_hazard_values_to_exposure_data(H, Emap,
                                                   attribute_name='MMI')

        # Extract relevant numerical data
        coordinates = Emap.get_geometry()
        shaking = Hi.get_data()
        N = len(shaking)

        # List attributes to carry forward to result layer
        attributes = Emap.get_attribute_names()
        # Calculate building damage
        count50 = 0
        count25 = 0
        count10 = 0
        count0 = 0
        building_damage = []
        for i in range(N):
            mmi = float(shaking[i]['MMI'])

            building_class = Emap.get_data(vclass_tag, i)

            building_type = str(building_class)
            damage_params = vul_curves[building_type]
            beta = damage_params['beta']
            median = damage_params['median']

            msg = 'Invalid parameter value for ' + building_type
            verify(beta + median > 0.0, msg)
            percent_damage = lognormal_cdf(mmi,
                                           median=median,
                                           sigma=beta) * 100

            # Collect shake level and calculated damage
            result_dict = {self.target_field: percent_damage,
                           'MMI': mmi}

            # Carry all orginal attributes forward
            for key in attributes:
                result_dict[key] = Emap.get_data(key, i)

            # Record result for this feature
            building_damage.append(result_dict)

            # Debugging
            #if percent_damage > 0.01:
            #    print mmi, percent_damage

            # Calculate statistics
            if percent_damage < 10:
                count0 += 1

            if 10 <= percent_damage < 33:
                count10 += 1

            if 33 <= percent_damage < 66:
                count25 += 1

            if 66 <= percent_damage:
                count50 += 1

#        fid.close()
        # Create report
        Hname = H.get_name()
        Ename = E.get_name()
        impact_summary = ('<b>In case of "%s" the estimated impact to '
                           '"%s" '
                           'is&#58;</b><br><br><p>' % (Hname, Ename))
        impact_summary += ('<table border="0" width="320px">'
                   '   <tr><th><b>%s</b></th><th><b>%s</b></th></th>'
                    '   <tr></tr>'
                    '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s (<10%%)&#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s (10-33%%)&#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s (33-66%%)&#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s (66-100%%)&#58;</td><td>%i</td></tr>'
                    '</table></font>' % (tr('Buildings'), tr('Total'),
                                    tr('All'), N,
                                    tr('No damage'), count0,
                                    tr('Low damage'), count10,
                                    tr('Medium damage'), count25,
                                    tr('High damage'), count50))
        impact_summary += '<br>'  # Blank separation row
        impact_summary += '<b>' + tr('Assumption') + '&#58;</b><br>'
        # This is the proper text:
        #tr('Levels of impact are defined by post 2009 '
        #  'Padang earthquake survey conducted by Geoscience '
        #  'Australia and Institute of Teknologi Bandung.'))
        #tr('Unreinforced masonry is assumed where no '
        #  'structural information is available.'))
        impact_summary += tr('Levels of impact are defined by post 2009 '
                            'Padang earthquake survey conducted by Geoscience '
                            'Australia and Institute of Teknologi Bandung.')
        impact_summary += tr('Unreinforced masonry is assumed where no '
                            'structural information is available.')
        # Create style
        style_classes = [dict(label=tr('No damage'), min=0, max=10,
                              colour='#00ff00', transparency=1),
                         dict(label=tr('Low damage'), min=10, max=33,
                              colour='#ffff00', transparency=1),
                         dict(label=tr('Medium damage'), min=33, max=66,
                              colour='#ffaa00', transparency=1),
                         dict(label=tr('High damage'), min=66, max=100,
                              colour='#ff0000', transparency=1)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes)

        # Create vector layer and return
        V = Vector(data=building_damage,
                   projection=E.get_projection(),
                   geometry=coordinates,
                   name='Estimated pct damage',
                   keywords={'impact_summary': impact_summary},
                   style_info=style_info)
        return V
