import numpy
from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from impact_functions.styles import flood_population_style as style_info
from storage.raster import Raster
from storage.utilities import ugettext as _
from impact_functions.tables import (Table, TableRow, TableCell)
from storage.utilities import ugettext as _


class FloodEvacuationFunction(FunctionProvider):
    """Risk plugin for flood evacuation

    :author HKV
    :rating 1
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

        # Extract data as numeric arrays
        D = inundation.get_data(nan=0.0)  # Depth

        # Calculate impact as population exposed to depths > threshold
        P = population.get_data(nan=0.0, scaling=True)
        I = numpy.where(D > threshold, P, 0)

        # Count totals
        total = int(numpy.sum(P))
        number_of_people_affected = int(numpy.sum(I))

        # Create impact_table based on BNPB Perka 7/2008 minimum bantuan
        # Weekly needs (see issue #82)
        rice = number_of_people_affected * 2.8
        drinking_water = number_of_people_affected * 17.5
        water = number_of_people_affected * 67
        family_kits = number_of_people_affected / 5
        toilets = number_of_people_affected / 20

        #table_header_row = TableRow(['Bantuan', 'Jumlah'], header=True)
        #table_body = [table_header_row,
        #              [_('Beras [kg]'), rice],
        #              [_('Air Minum [l]'), drinking_water],
        #              [_('Air Bersih [l]'), water],
        #              [_('Kit Keluarga'), family_kits],
        #              [_('Jamban Keluarga'), toilets],
        #              _('Sumber: BNPB Perka 7/2008')]
        table_header_row = TableRow(['Needs', 'Total'], header=True)
        table_body = [table_header_row,
                      [_('Rice [kg]'), rice],
                      [_('Drinking Water [l]'), drinking_water],
                      [_('Clean Water [l]'), water],
                      [_('Family Kits'), family_kits],
                      [_('Toilets'), toilets],
                      _('Source: BNPB Pachment 7/2008')]
       impact_table = Table(table_body).toNewlineFreeString()


        # Create summary table
        total1000 = str(total / 1000)
        count1000 = str(number_of_people_affected / 1000)

        iname = inundation.get_name()
        pname = population.get_name()
        #table_caption = _('Apabila terjadi "%s" perkiraan dampak '
        #                 'terhadap "%s" kemungkinan yang terjadi&#58;'
        #                  % (iname, pname))
        #table_body.extend([[_('Perlu Evakuasi (x 1000)'), '%s' % count1000],
        #              [TableCell(_('Catatan:'), header=True, col_span=2)],
        #              [TableCell(_('Jumlah penduduk Jakarta %s'
        #                                 % total1000), col_span=2)],
        #              [TableCell(_('Jumlah dalam ribuan'), col_span=2)],
        #              [TableCell(_('Penduduk perlu dievakuasi ketika'
        #                                'banjir lebih dari %i m.'
        #                                % threshold), col_span=2)],
        #              [TableCell(_('Minimum Bantuan per minggu (BNPB perka'
        #                         ' 7/2008)'), col_span=2)]
        #              ])
        table_caption = _('In case of "%s" the estimated impact to '
                         '"%s" is:'
                          % (iname, pname))
        table_body.extend([[_('Need Evacuation (x 1000)'), '%s' % count1000],
                      [TableCell(_('Notes:'), header=True, col_span=2)],
                      [TableCell(_('Total population Jakarta %s'
                                         % total1000), col_span=2)],
                      [TableCell(_('Totals are given in thousands'), col_span=2)],
                      [TableCell(_('People need evacuation if flood levels '
                                   'exceed %i m.' % threshold), col_span=2)],
                      [TableCell(_('Minimum needs are per week as defined '
                                   'in BNPB regulation 7/2008)'), col_span=2)]
                      ])

        impact_summary = Table(table_body,
                               caption=table_caption).toNewlineFreeString()

        #map_title = _('Penduduk yang Mungkin dievakuasi')
        map_title = _('People in need of evacuation')

        #style_info['legend_title'] = _('Kepadatan Penduduk')
        style_info['legend_title'] = _('Population Density')

        # Create raster object and return
        R = Raster(I,
                   projection=inundation.get_projection(),
                   geotransform=inundation.get_geotransform(),
                   #name=_('Penduduk yang %s' % (self.plugin_name.lower())),
                   name=_('Population which %s' % (self.plugin_name.lower())),
                   keywords={'impact_summary': impact_summary,
                             'impact_table': impact_table,
                             'map_title': map_title},
                   style_info=style_info)
        return R
