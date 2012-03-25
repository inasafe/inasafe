from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.vector import Vector
from storage.utilities import ugettext as _


class BNPBFloodBuildingImpactFunction(FunctionProvider):
    """Flood impact on building data according to BNPB Perka 2

    :param requires category == 'hazard' and \
                    subcategory == 'flood' and \
                    layertype == 'raster'

    :param requires category == 'exposure' and \
                    subcategory == 'building' and \
                    layertype == 'vector'
    """

    target_field = 'LEVEL'  # The levels are 1: < 1m, 2: 1-3m and 3: > 3m
    plugin_name = _('Rawan Banjir')  # Name that will show up in GUI

    def run(self, layers):
        """Separate exposed elements by depth [m]:
        < 1     Rendah
        1 - 3   Sedang
        > 3     Tinggi
        """

        # Extract data
        H = get_hazard_layer(layers)    # Depth
        E = get_exposure_layer(layers)  # Building locations

        # Interpolate hazard level to building locations
        I = H.interpolate(E)

        # Extract relevant numerical data
        attributes = I.get_data()
        N = len(I)

        # List attributes to carry forward to result layer
        attribute_names = E.get_attribute_names()

        # Calculate building impact
        rendah = 0
        sedang = 0
        tinggi = 0
        building_impact = []
        for i in range(N):

            # Get the interpolated depth
            x = float(attributes[i].values()[0])

            # Assign impact level (nilai) depending on depth and count
            if x < 1:
                nilai = 1
                rendah += 1
            elif 1 <= x < 3:
                nilai = 2
                sedang += 1
            else:
                nilai = 3
                tinggi += 1

            # Record depth and impact level for this feature
            building_impact.append({'depth': x,
                                    self.target_field: nilai})

        # Create summary report
        Hname = H.get_name()
        Ename = E.get_name()
        table = _('<b>In case of "%s" the estimated impact to "%s" '
                  'the possibility of &#58;</b><br><br><p>' % (Hname,
                                                               Ename))
        table += ('<table border="0" width="320px">'
                  '   <tr><th><b>%s</b></th><th><b>%s</b></th></th>'
                  '   <tr></tr>'
                  '   <tr><td>%s &#58;</td><td>%i</td></tr>'
                  '   <tr><td>%s &#58;</td><td>%i</td></tr>'
                  '   <tr><td>%s &#58;</td><td>%i</td></tr>'
                  '   <tr><td>%s &#58;</td><td>%i</td></tr>'
                  '</table>' % (_('Ketinggian Banjir'), _('Jumlah gedung'),
                                _('All'), N,
                                _('< 1 m'), rendah,
                                _('1 - 3 m'), sedang,
                                _('> 3 m'), tinggi))

        table += '<br>'  # Blank separation row
        table += '<b>' + _('Based on BNPB Perka 2 - 2012') + '</b><br>'

        # Create style
        style_classes = [dict(label=_('< 1 m'), min=1, max=1,
                              colour='#00FF00',  # Green
                              transparency=0, size=1),
                         dict(label=_('1 - 3 m'), min=2, max=2,
                              colour='#FFFF00',  # Yellow
                              transparency=0, size=1),
                         dict(label=_('> 3 m'), min=3, max=3,
                              colour='#FF0000',  # Red
                              transparency=0, size=1)]

        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes)

        # Create vector layer and return
        V = Vector(data=building_impact,
                   projection=E.get_projection(),
                   geometry=E.get_geometry(),
                   name=_('Estimated buildings affected'),
                   keywords={'impact_summary': table},
                   style_info=style_info)
        return V
