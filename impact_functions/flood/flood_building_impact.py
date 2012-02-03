from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.vector import Vector
from storage.utilities import ugettext as _


class FloodBuildingImpactFunction(FunctionProvider):
    """Risk plugin for flood impact on building data

    :param requires category=='hazard' and \
                    subcategory.startswith('flood') and \
                    layertype=='raster' and \
                    unit=='m'

    :param requires category=='exposure' and \
                    subcategory.startswith('building')
    """

    target_field = 'AFFECTED'
    plugin_name = 'Ditutup Sementara'

    def run(self, layers):
        """Risk plugin for tsunami population
        """

        threshold = 1.0  # Flood threshold [m]

        # Extract data
        H_org = get_hazard_layer(layers)    # Depth
        E = get_exposure_layer(layers)  # Building locations

        # FIXME (Ole): interpolate does not carry original name through,
        # so get_name gives "Vector Layer" :-)

        # Interpolate hazard level to building locations
        H = H_org.interpolate(E)

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
            if dep > threshold:
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
        Hname = H_org.get_name()
        Ename = E.get_name()
        caption = ('<b>Apabila terjadi "%s" perkiraan dampak terhadap "%s" '
                   'kemungkinan yang terjadi&#58;</b><br><br><p>' % (Hname,
                                                                     Ename))
        caption += ('<table border="0" width="320px">'
                   '   <tr><th><b>%s</b></th><th><b>%s</b></th></th>'
                    '   <tr></tr>'
                    '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s &#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s &#58;</td><td>%i</td></tr>'
                    #'   <tr><td>%s (> %.2f m) &#58;</td><td>%i</td></tr>'
                    #'   <tr><td>%s (< %.2f m) &#58;</td><td>%i</td></tr>'
                    '</table>' % (_('Gedung'), _('Jumlah'),
                                  _('Semua'), N,
                                  #_('Terendam'), threshold, count,
                                  #_('Tidak terendam'), threshold, N - count))
                                  _('Ditutup'), count,
                                  _('Dibuka'), N - count))

        caption += '<br>'  # Blank separation row
        caption += '<b>Anggapan&#58;</b><br>'
        caption += ('Bangunan perlu ditutup ketika banjir '
                   'lebih dari %.1f m' % threshold)

        # Create style
        style_classes = [dict(label=_('Dibuka'), min=0, max=90,
                              colour='#1EFC7C', opacity=1),
                         dict(label=_('Ditutup'), min=90, max=100,
                              colour='#F31A1C', opacity=1)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes)

        # Create vector layer and return
        V = Vector(data=building_impact,
                   projection=E.get_projection(),
                   geometry=coordinates,
                   name='Estimated buildings affected',
                   keywords={'caption': caption},
                   style_info=style_info)
        return V
