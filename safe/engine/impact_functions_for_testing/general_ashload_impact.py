from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.storage.vector import Vector
from safe.engine.interpolation import assign_hazard_values_to_exposure_data

# FIXME: Need style for this and allow the name to
# be different from Percen_da

# FIXME (Ole): I think this one can be deleted


class TephraBuildingImpactFunction(FunctionProvider):
    """Risk plugin for tephra damage (FIXME: Origin?)

    :param requires category=='hazard' and \
                    subcategory.startswith('tephra') and \
                    layertype=='raster' and \
                    unit=='kg/m^2'

    :param requires category=='exposure' and \
                    subcategory=='structure' and \
                    layertype=='vector'
    """

    @staticmethod
    def run(layers):
        """Risk plugin for tephra impact
        """

        # Extract data
        H = get_hazard_layer(layers)    # Ash load
        E = get_exposure_layer(layers)  # Building locations

        # Interpolate hazard level to building locations
        H = assign_hazard_values_to_exposure_data(H, E,
                                             attribute_name='load')

        # Calculate building damage
        count3 = 0
        count2 = 0
        count1 = 0
        count0 = 0
        result = []
        for i in range(len(E)):

            #-------------------
            # Extract parameters
            #-------------------
            load = H.get_data('load', i)

            #------------------------
            # Compute damage level
            #------------------------

            # FIXME: The thresholds have been greatly reduced
            # for the purpose of demonstration. Any real analyis
            # should bring them back to 0, 90, 150, 300
            if 0.01 <= load < 0.5:
                # Loss of crops and livestock
                impact = 0
                count0 += 1
            elif 0.5 <= load < 2.0:
                # Cosmetic damage
                impact = 1
                count1 += 1
            elif 2.0 <= load < 10.0:
                # Partial building collapse
                impact = 2
                count2 += 1
            elif load >= 10.0:
                # Complete building collapse
                impact = 3
                count3 += 1
            else:
                impact = 0
                count0 += 1

            result.append({'DAMAGE': impact, 'ASHLOAD': load})

        # Create report
        impact_summary = ('<font size="3"> <table border="0" width="320px">'
                   '   <tr><th><b>%s</b></th><th><b>%s</b></th></th>'
                    '   <tr></tr>'
                    '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                    '</table></font>' % ('Beban abu', 'Gedung dampak',
                                         '< 0.5 kg/m2', count0,
                                         '0.5 - 2 kg/m2', count1,
                                         '2 - 10 kg/m2', count2,
                                         '> 10 kg/m2', count3))
                    #'</table>' %
                    # ('Beban abu', 'Gedung dampak',
                    # 'Gangguan (< 90 kg/m2)', count0,
                    # 'Kerusakan kosmetik (90 - 150 kg/m2', count1,
                    # 'parsial runtuhnya (150 - 300 kg/m2', count2,
                    # 'runtuhnya lengkap (> 300 kg/m2', count3))

        V = Vector(data=result,
                   projection=E.get_projection(),
                   geometry=E.get_geometry(),
                   name='Estimated ashload damage',
                   keywords={'impact_summary': impact_summary})
        return V

    def generate_style(self, data):
        """Generates and SLD file based on the data values
        """

        DEFAULT_SYMBOL = 'square'

        symbol_field = None
        symbol_keys = [None, '']
        symbol_values = [DEFAULT_SYMBOL, DEFAULT_SYMBOL]

        # Zoom levels (large number means close up)
        scale_keys = [50000000000, 10000000000, 10000000, 5000000,
                      1000000, 500000, 250000, 100000]
        scale_values = [2, 4, 6, 8, 1, 1, 1, 1]

        # Predefined colour classes
        class_keys = ['< 90 kg/m2', '90 - 150 kg/m2',
                      '150 - 300 kg/m2', '> 300 kg/m2']
        class_values = [{'min': -0.5, 'max': 0.5,
                         'color': '#cccccc', 'transparency': '1'},
                        {'min': 0.5, 'max': 1.5,
                         'color': '#0EEC6C', 'transparency': '1'},
                        {'min': 1.5, 'max': 2.5,
                         'color': '#FD8D3C', 'transparency': '1'},
                        {'min': 2.5, 'max': 3.5,
                         'color': '#F31A1C', 'transparency': '1'}]

        _params = dict(name=data.get_name(),
                       damage_field=self.target_field,
                       symbol_field=symbol_field,
                       symbols=dict(zip(symbol_keys, symbol_values)),
                       scales=dict(zip(scale_keys, scale_values)),
                       classifications=dict(zip(class_keys, class_values)))
