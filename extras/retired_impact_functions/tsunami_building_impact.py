from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.storage.vector import Vector
from safe.common.utilities import ugettext as tr

# Largely superseded by flood impact functions, but keep as it
# will be needed to test impact on roads from both raster and polygon
# hazard layers


class TsunamiBuildingImpactFunction(FunctionProvider):
    """Risk plugin for tsunami impact on building data

    :param requires category=='hazard' and \
                    subcategory=='tsunami' and \
                    layertype in ['raster', 'vector']

    :param requires category=='exposure' and \
                    subcategory in ['building', 'road'] and \
                    layertype=='vector' and \
                    disabled==True
    """

    target_field = 'ICLASS'
    plugin_name = tr('Be affected by tsunami')

    def run(self, layers):
        """Risk plugin for tsunami population
        """

        # Extract data
        H = get_hazard_layer(layers)    # Depth
        E = get_exposure_layer(layers)  # Building locations

        # Interpolate hazard level to building locations
        Hi = H.interpolate(E, attribute_name='depth')

        # Extract relevant numerical data
        coordinates = Hi.get_geometry()
        depth = Hi.get_data()
        N = len(depth)

        # List attributes to carry forward to result layer
        attributes = E.get_attribute_names()

        # Calculate building impact according to guidelines
        count3 = 0
        count1 = 0
        count0 = 0
        population_impact = []
        for i in range(N):

            if H.is_raster:
                # Get depth
                dep = float(depth[i]['depth'])

                # Classify buildings according to depth
                if dep >= 3:
                    affected = 3  # FIXME: Colour upper bound is 100 but
                    count3 += 1          # does not catch affected == 100
                elif 1 <= dep < 3:
                    affected = 2
                    count1 += 1
                else:
                    affected = 1
                    count0 += 1
            elif H.is_vector:
                dep = 0  # Just put something here
                cat = depth[i]['Affected']
                if cat is True:
                    affected = 3
                    count3 += 1
                else:
                    affected = 1
                    count0 += 1

            # Collect depth and calculated damage
            result_dict = {self.target_field: affected,
                           'DEPTH': dep}

            # Carry all original attributes forward
            # FIXME: This should be done in interpolation. Check.
            #for key in attributes:
            #    result_dict[key] = E.get_data(key, i)

            # Record result for this feature
            population_impact.append(result_dict)

        # Create report
        Hname = H.get_name()
        Ename = E.get_name()
        if H.is_raster:
            impact_summary = ('<b>In case of "%s" the estimated impact to '
                           '"%s" '
                           'is&#58;</b><br><br><p>' % (Hname, Ename))
            impact_summary += ('<table border="0" width="320px">'
                       '   <tr><th><b>%s</b></th><th><b>%s</b></th></tr>'
                       '   <tr></tr>'
                       '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                       '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                       '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                       '</table>' % (tr('Impact'), tr('Number of buildings'),
                                     tr('Low'), count0,
                                     tr('Medium'), count1,
                                     tr('High'), count3))
        else:
            impact_summary = ('<table border="0" width="320px">'
                       '   <tr><th><b>%s</b></th><th><b>%s</b></th></tr>'
                       '   <tr></tr>'
                       '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                       '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                       '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                       '</table>' % ('Terdampak oleh tsunami',
                                     'Jumlah gedung',
                                     'Terdampak', count3,
                                     'Tidak terdampak', count0,
                                     'Semua', N))

        impact_summary += '<br>'  # Blank separation row
        impact_summary += '<b>' + tr('Assumption') + '&#58;</b><br>'
        impact_summary += ('Levels of impact are defined by BNPB\'s '
                            '<i>Pengkajian Risiko Bencana</i>')
        impact_summary += ('<table border="0" width="320px">'
                       '   <tr><th><b>%s</b></th><th><b>%s</b></th></tr>'
                       '   <tr></tr>'
                       '   <tr><td>%s&#58;</td><td>%s&#58;</td></tr>'
                       '   <tr><td>%s&#58;</td><td>%s&#58;</td></tr>'
                       '   <tr><td>%s&#58;</td><td>%s&#58;</td></tr>'
                       '</table>' % (tr('Impact'), tr('Tsunami height'),
                                     tr('Low'), '<1 m',
                                     tr('Medium'), '1-3 m',
                                     tr('High'), '>3 m'))

        # Create style
        style_classes = [dict(label='< 1 m', min=0, max=1,
                              colour='#1EFC7C', transparency=0, size=1),
                         dict(label='1 - 3 m', min=1, max=2,
                              colour='#FFA500', transparency=0, size=1),
                         dict(label='> 3 m', min=2, max=4,
                              colour='#F31A1C', transparency=0, size=1)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes)

        # Create vector layer and return
        if Hi.is_line_data:
            name = 'Roads flooded'
        elif Hi.is_point_data:
            name = 'Buildings flooded'

        V = Vector(data=population_impact,
                   projection=E.get_projection(),
                   geometry=coordinates,
                   keywords={'impact_summary': impact_summary},
                   geometry_type=Hi.geometry_type,
                   name=name,
                   style_info=style_info)
        return V
