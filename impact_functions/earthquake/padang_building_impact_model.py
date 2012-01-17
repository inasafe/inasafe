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

from storage.loader import render_to_string
from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.vector import Vector
from storage.utilities import ugettext as _
from impact_functions.utilities import PointZoomSize
from impact_functions.utilities import PointClassColor
from impact_functions.utilities import PointSymbol
from impact_functions.mappings import osm2padang, sigab2padang
import scipy.stats


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

    def run(self, layers):
        """Risk plugin for earthquake school damage
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
            percent_damage = scipy.stats.lognorm.cdf(mmi,
                                                     beta,
                                                     scale=median) * 100

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

    def generate_style(self, data):
        """Generates and SLD file based on the data values
        """

        if data.is_point_data:
            return self.generate_point_style(data)
        elif data.is_polygon_data:
            return self.generate_polygon_style(data)
        else:
            msg = 'Unknown style %s' % str(data)
            raise Exception(msg)

    def generate_point_style(self, data):
        """Generates and SLD file based on the data values
        """

        # Define default behaviour to be used when
        # - symbol attribute is missing
        # - attribute value is None or ''
        DEFAULT_SYMBOL = 'circle'

        symbol_field = None

        # FIXME: Replace these by dict and extend below
        symbol_keys = [None, '']
        symbol_values = [DEFAULT_SYMBOL, DEFAULT_SYMBOL]

        # Predefined scales and corresponding font sizes
        scale_keys = [10000000000, 10000000, 5000000,
                      1000000, 500000, 250000, 100000]
        scale_values = [3, 5, 8, 12, 14, 16, 18]

        # Predefined colour classes
        class_keys = ['No Damage', '10-25', '25-50', '50-100']
        class_values = [{'min': 0, 'max': 10,
                         'color': '#cccccc', 'opacity': '1'},
                        {'min': 10, 'max': 25,
                         'color': '#fecc5c', 'opacity': '1'},
                        {'min': 25, 'max': 50,
                         'color': '#fd8d3c', 'opacity': '1'},
                        {'min': 50, 'max': 100,
                         'color': '#e31a1c', 'opacity': '1'}]

        # Definition of symbols for each attribute value
        if self.symbol_field in data.get_attribute_names():

            # Get actual symbol field to use
            symbol_field = self.symbol_field

            symbols = {'Church/Mosque': 'ttf://ESRI US MUTCD 3#0x00F6',
                       'Commercial (office)': 'ttf://ESRI Business#0x0040',
                       'Hotel': 'ttf://ESRI Public1#0x00b6',
                       'Medical facility': 'ttf://ESRI Cartography#0x00D1',
                       'Other': 'ttf://ESRI Business#0x002D',
                       'Other industrial': 'ttf://ESRI Business#0x0043',
                       'Residential': 'ttf://ESRI Cartography#0x00d7',
                       'Retail': 'ttf://Comic Sans MS#0x0024',
                       'School': 'ttf://ESRI Cartography#0x00e5',
                       'Unknown': 'ttf://Comic Sans MS#0x003F',
                       'Warehouse': 'ttf://ESRI US MUTCD 3#0x00B5'}
        else:
            symbols = {None: DEFAULT_SYMBOL, '': DEFAULT_SYMBOL}

        # Generate sld style file
        params = dict(name=data.get_name(),
                      damage_field=self.target_field,
                      symbol_field=symbol_field,
                      symbols=symbols,
                      scales=dict(zip(scale_keys, scale_values)),
                      classifications=dict(zip(class_keys, class_values)))

        # The styles are in $RIAB_HOME/riab/impact/templates/impact/styles
        return render_to_string('impact/styles/point_classes.sld', params)

    def generate_polygon_style(self, data):
        """Generates and SLD file based on the data values
        """

        # FIXME (Ole): Return static style to start with: ticket #144
        style = """<?xml version="1.0" encoding="UTF-8"?>
<sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>earthquake_impact</sld:Name>
    <sld:UserStyle>
      <sld:Name>earthquake_impact</sld:Name>
      <sld:Title/>
      <sld:FeatureTypeStyle>
        <sld:Name>name</sld:Name>
        <sld:Rule>
          <sld:Name>1</sld:Name>
          <sld:Title>Low</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsLessThan>
              <ogc:PropertyName>%s</ogc:PropertyName>
              <ogc:Literal>10</ogc:Literal>
            </ogc:PropertyIsLessThan>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#CCCCCC</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#BCBCBC</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>2</sld:Name>
          <sld:Title>Medium</sld:Title>
          <ogc:Filter>
            <ogc:And>
            <ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyName>%s</ogc:PropertyName>
              <ogc:Literal>10</ogc:Literal>
              </ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyIsLessThan>
                <ogc:PropertyName>%s</ogc:PropertyName>
                <ogc:Literal>25</ogc:Literal>
              </ogc:PropertyIsLessThan>
            </ogc:And>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#FECC5C</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#EEBC4C</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>3</sld:Name>
          <sld:Title>Medium</sld:Title>
          <ogc:Filter>
            <ogc:And>
            <ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyName>%s</ogc:PropertyName>
              <ogc:Literal>25</ogc:Literal>
              </ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyIsLessThan>
                <ogc:PropertyName>%s</ogc:PropertyName>
                <ogc:Literal>50</ogc:Literal>
              </ogc:PropertyIsLessThan>
            </ogc:And>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#FD8D3C</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#ED7D2C</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>4</sld:Name>
          <sld:Title>High</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyName>%s</ogc:PropertyName>
              <ogc:Literal>50</ogc:Literal>
              </ogc:PropertyIsGreaterThanOrEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#F31A1C</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#E30A0C</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>
""" % ((self.target_field,) * 6)

        return style
