import numpy
from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from impact_functions.styles import flood_population_style as style_info
from storage.raster import Raster
from storage.utilities import ugettext as _
from impact_functions.tables import Table, TableRow


class FloodEvacuationFunction(FunctionProvider):
    """Risk plugin for flood evacuation

    :author AIFDR
    :rating 4
    :param requires category=='hazard' and \
                    subcategory in ['flood', 'tsunami'] and \
                    layertype=='raster' and \
                    unit=='m'

    :param requires category=='exposure' and \
                    subcategory=='population' and \
                    layertype=='raster' and \
                    datatype=='density'
    """

    plugin_name = _('Need evacuation')

    def run(self, layers):
        """Risk plugin for flood population evacuation

        Input
          layers: List of layers expected to contain
              H: Raster layer of flood depth
              P: Raster layer of population data on the same grid as H
        """

        # Depth above which people are regarded affected [m]
        threshold = 1.0  # Threshold [m]

        # Identify hazard and exposure layers
        inundation = get_hazard_layer(layers)  # Flood inundation [m]
        population = get_exposure_layer(layers)
        iname = inundation.get_name()
        pname = population.get_name()

        # Extract data as numeric arrays
        D = inundation.get_data(nan=0.0)  # Depth

        # Calculate impact as population exposed to depths > threshold
        P = population.get_data(nan=0.0, scaling=True)
        I = numpy.where(D > threshold, P, 0)

        # Count totals
        total = int(numpy.sum(P))
        evacuated = int(numpy.sum(I))

        # Don't show digits less than a 1000
        if total > 1000:
            total = total // 1000 * 1000
        if evacuated > 1000:
            evacuated = evacuated // 1000 * 1000

        # Calculate estimated needs based on BNPB Perka 7/2008 minimum bantuan
        rice = int(evacuated * 2.8)
        drinking_water = int(evacuated * 17.5)
        water = evacuated * 67
        family_kits = evacuated / 5
        toilets = evacuated / 20

        # Generate impact report for the pdf map
        table_body = [_('In the event of %s how many '
                        '%s might %s') % (iname, pname, plugin_name),
                      TableRow([_('People needing evacuation'),
                                '%i' % evacuated],
                               header=True),
                      TableRow([_('Needs per week'), _('Total')],
                               header=True),
                      [_('Rice [kg]'), int(rice)],
                      [_('Drinking Water [l]'), int(drinking_water)],
                      [_('Clean Water [l]'), int(water)],
                      [_('Family Kits'), int(family_kits)],
                      [_('Toilets'), int(toilets)]]
        impact_table = Table(table_body).toNewlineFreeString()

        # Extend impact report for on-screen display
        table_body.extend([TableRow(_('Notes:'), header=True),
                           _('Total population: %i') % total,
                           _('People need evacuation if flood levels '
                             'exceed %(eps)i m') % {'eps': threshold},
                           _('Minimum needs are defined in BNPB '
                             'regulation 7/2008')])
        impact_summary = Table(table_body).toNewlineFreeString()
        map_title = _('People in need of evacuation')
        style_info['legend_title'] = _('Population Density')

        # Create raster object and return
        R = Raster(I,
                   projection=inundation.get_projection(),
                   geotransform=inundation.get_geotransform(),
                   name=_('Population which %s' % (self.plugin_name.lower())),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'map_title': map_title},
                   style_info=style_info)
        return R
