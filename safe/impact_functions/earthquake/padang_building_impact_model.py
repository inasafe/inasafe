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

from safe.impact_functions.core import FunctionProvider
from safe.impact_functions.core import get_hazard_layer, get_exposure_layer
from safe.impact_functions.core import get_question
from safe.storage.vector import Vector
from safe.common.utilities import ugettext as tr
from safe.common.numerics import lognormal_cdf
from safe.common.tables import Table, TableRow
from safe.impact_functions.mappings import osm2padang, sigab2padang
from safe.engine.interpolation import assign_hazard_values_to_exposure_data


# Damage curves for each of the nine classes derived from the Padang survey
damage_curves = {1: dict(median=7.5, beta=0.11),
                 2: dict(median=8.3, beta=0.1),
                 3: dict(median=8.8, beta=0.11),
                 4: dict(median=8.4, beta=0.05),
                 5: dict(median=9.2, beta=0.11),
                 6: dict(median=9.7, beta=0.15),
                 7: dict(median=9.0, beta=0.08),
                 8: dict(median=8.9, beta=0.07),
                 9: dict(median=10.5, beta=0.15)}


class PadangEarthquakeBuildingDamageFunction(FunctionProvider):
    """Risk plugin for Padang earthquake damage to buildings

    :param requires category=='hazard' and \
                    subcategory=='earthquake' and \
                    layertype=='raster' and \
                    unit=='MMI'

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

        question = get_question(H.get_name(),
                                E.get_name(),
                                self)

        # Map from different kinds of datasets to Padang vulnerability classes
        datatype = E.get_keywords()['datatype']
        vclass_tag = 'VCLASS'
        if datatype.lower() == 'osm':
            # Map from OSM attributes
            Emap = osm2padang(E)
        elif datatype.lower() == 'sigab':
            # Map from SIGAB attributes
            Emap = sigab2padang(E)
        else:
            Emap = E

        # Interpolate hazard level to building locations
        I = assign_hazard_values_to_exposure_data(H, Emap,
                                                  attribute_name='MMI')

        # Extract relevant numerical data
        attributes = I.get_data()
        N = len(I)

        # Calculate building damage
        count_high = count_medium = count_low = count_none = 0
        for i in range(N):
            mmi = float(attributes[i]['MMI'])

            building_type = Emap.get_data(vclass_tag, i)
            damage_params = damage_curves[building_type]
            beta = damage_params['beta']
            median = damage_params['median']
            percent_damage = lognormal_cdf(mmi,
                                           median=median,
                                           sigma=beta) * 100

            # Add calculated impact to existing attributes
            attributes[i][self.target_field] = percent_damage

            # Calculate statistics
            if percent_damage < 10:
                count_none += 1

            if 10 <= percent_damage < 33:
                count_low += 1

            if 33 <= percent_damage < 66:
                count_medium += 1

            if 66 <= percent_damage:
                count_high += 1

        # Generate impact report
        table_body = [question,
                      TableRow([tr('Buildings'), tr('Total')],
                               header=True),
                      TableRow([tr('All'), N]),
                      TableRow([tr('No damage'), count_none]),
                      TableRow([tr('Low damage'), count_low]),
                      TableRow([tr('Medium damage'), count_medium]),
                      TableRow([tr('High damage'), count_high])]

        table_body.append(TableRow(tr('Notes'), header=True))
        table_body.append(tr('Levels of impact are defined by post 2009 '
                            'Padang earthquake survey conducted by Geoscience '
                            'Australia and Institute of Teknologi Bandung.'))
        table_body.append(tr('Unreinforced masonry is assumed where no '
                            'structural information is available.'))

        impact_summary = Table(table_body).toNewlineFreeString()
        impact_table = impact_summary
        map_title = tr('Earthquake damage to buildings')

        # Create style
        style_classes = [dict(label=tr('No damage'), min=0, max=10,
                              colour='#00ff00', transparency=0),
                         dict(label=tr('Low damage'), min=10, max=33,
                              colour='#ffff00', transparency=0),
                         dict(label=tr('Medium damage'), min=33, max=66,
                              colour='#ffaa00', transparency=0),
                         dict(label=tr('High damage'), min=66, max=100,
                              colour='#ff0000', transparency=0)]
        style_info = dict(target_field=self.target_field,
                          style_classes=style_classes)

        # Create vector layer and return
        V = Vector(data=attributes,
                   projection=E.get_projection(),
                   geometry=E.get_geometry(),
                   name='Estimated pct damage',
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'map_title': map_title,
                             'target_field': self.target_field},
                   style_info=style_info)
        return V
