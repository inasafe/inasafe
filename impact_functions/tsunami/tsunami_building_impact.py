from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.vector import Vector
from storage.utilities import ugettext as _


class TsunamiBuildingImpactFunction(FunctionProvider):
    """Risk plugin for tsunami impact on building data

    :param requires category=='hazard' and \
                    subcategory.startswith('tsunami') and \
                    layertype in ['raster', 'vector']
                    

    :param requires category=='exposure' and \
                    subcategory.startswith('building') and \
                    layertype=='vector'
    """

    target_field = 'ICLASS'

    def run(self, layers):
        """Risk plugin for tsunami population
        """

        # Extract data
        H = get_hazard_layer(layers)    # Depth
        E = get_exposure_layer(layers)  # Building locations

        # Interpolate hazard level to building locations
        Hi = H.interpolate(E)

        # Extract relevant numerical data
        coordinates = E.get_geometry()
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
                dep = float(depth[i].values()[0])

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
            for key in attributes:
                result_dict[key] = E.get_data(key, i)

            # Record result for this feature
            population_impact.append(result_dict)

        # Create report
        if H.is_raster:
            caption = ('<table border="0" width="320px">'
                       '   <tr><th><b>%s</b></th><th><b>%s</b></th></th>'
                       '   <tr></tr>'
                       '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                       '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                       '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                       '</table>' % ('ketinggian tsunami', 'Jumlah gedung',
                                     '< 1 m', count0,
                                     '1 - 3 m', count1,
                                     '> 3 m', count3))
        else:
            caption = ('<table border="0" width="320px">'
                       '   <tr><th><b>%s</b></th><th><b>%s</b></th></th>'
                       '   <tr></tr>'
                       '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                       '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                       '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                       '</table>' % ('Terdampak oleh tsunami', 'Jumlah gedung',
                                     'Terdampak', count3,
                                     'Tidak terdampak', count0,
                                     'Semua', N))

        # Create vector layer and return
        V = Vector(data=population_impact,
                   projection=E.get_projection(),
                   geometry=coordinates,
                   name='Estimate of buildings affected',
                   keywords={'caption': caption})
        return V
