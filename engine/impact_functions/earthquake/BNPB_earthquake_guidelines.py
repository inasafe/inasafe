"""Impact function based on Padang 2009 post earthquake survey

This impact function estimates percentual damage to buildings as a
function of ground shaking measured in MMI.
Buildings are currently assumed to be represented in OpenStreetMap with
attributes collected as during the July 2011 Indonesian mapping competition.

This impact function maps the OSM buildings into 2 classes:
Unreinforced masonry (URM) and reinforced masonry (RM) according to
the guidelines.
"""

from django.template.loader import render_to_string
from impact.plugins.core import FunctionProvider
from impact.plugins.core import get_hazard_layer, get_exposure_layer
from impact.storage.vector import Vector
from django.utils.translation import ugettext as _
from impact.plugins.utilities import PointZoomSize
from impact.plugins.utilities import PointClassColor
from impact.plugins.utilities import PointSymbol
from impact.plugins.mappings import osm2bnpb, unspecific2bnpb, sigab2bnpb

# Damage 'curves' for the two vulnerability classes
damage_parameters = {'URM': [6, 7],
                     'RM': [6, 8]}


class EarthquakeGuidelinesFunction(FunctionProvider):
    """Risk plugin for BNPB guidelines for earthquake damage to buildings

    :param requires category=='hazard' and \
                    subcategory.startswith('earthquake') and \
                    layer_type=='raster' and \
                    unit=='MMI'

    :param requires category=='exposure' and \
                    subcategory.startswith('building') and \
                    layer_type=='vector'
    """

    vclass_tag = 'VCLASS'
    target_field = 'DMGLEVEL'

    def run(self, layers):
        """Risk plugin for earthquake school damage
        """

        # Extract data
        H = get_hazard_layer(layers)    # Ground shaking
        E = get_exposure_layer(layers)  # Building locations

        keywords = E.get_keywords()
        if 'datatype' in keywords:
            datatype = keywords['datatype']
            if datatype.lower() == 'osm':
                # Map from OSM attributes to the guideline classes (URM and RM)
                E = osm2bnpb(E, target_attribute=self.vclass_tag)
            elif datatype.lower() == 'sigab':
                # Map from SIGAB attributes to the guideline classes
                # (URM and RM)
                E = sigab2bnpb(E)
            else:
                E = unspecific2bnpb(E, target_attribute=self.vclass_tag)
        else:
            E = unspecific2bnpb(E, target_attribute=self.vclass_tag)

        # Interpolate hazard level to building locations
        H = H.interpolate(E)

        # Extract relevant numerical data
        coordinates = E.get_geometry()
        shaking = H.get_data()
        N = len(shaking)

        # List attributes to carry forward to result layer
        attributes = E.get_attribute_names()

        # Calculate building damage
        count3 = 0
        count2 = 0
        count1 = 0
        building_damage = []
        for i in range(N):
            mmi = float(shaking[i].values()[0])

            building_class = E.get_data(self.vclass_tag, i)
            lo, hi = damage_parameters[building_class]

            if mmi < lo:
                damage = 1  # Low
                count1 += 1
            elif lo <= mmi < hi:
                damage = 2  # Medium
                count2 += 1
            else:
                damage = 3  # High
                count3 += 1

            # Collect shake level and calculated damage
            result_dict = {self.target_field: damage,
                           'MMI': mmi}

            # Carry all orginal attributes forward
            for key in attributes:
                result_dict[key] = E.get_data(key, i)

            # Record result for this feature
            building_damage.append(result_dict)

        # Create report
        caption = ('<table border="0" width="320px">'
                   '   <tr><th><b>%s</b></th><th><b>%s</b></th></th>'
                    '   <tr></tr>'
                    '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s (10-25%%)&#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s (25-50%%)&#58;</td><td>%i</td></tr>'
                    '   <tr><td>%s (50-100%%)&#58;</td><td>%i</td></tr>'
                    '</table>' % (_('Buildings'), _('Total'),
                                  _('All'), N,
                                  _('Low damage'), count1,
                                  _('Medium damage'), count2,
                                  _('High damage'), count3))

        # Create vector layer and return
        V = Vector(data=building_damage,
                   projection=E.get_projection(),
                   geometry=coordinates,
                   name='Estimated damage level',
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
        class_values = [{'min': -0.5, 'max': 0.5,
                         'color': '#cccccc', 'opacity': '1'},
                        {'min': 0.5, 'max': 1.5,
                         'color': '#fecc5c', 'opacity': '1'},
                        {'min': 1.5, 'max': 2.5,
                         'color': '#fd8d3c', 'opacity': '1'},
                        {'min': 2.5, 'max': 3.5,
                         'color': '#f31a1c', 'opacity': '1'}]

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
        """Generates a polygon SLD file based on the data values
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
              <ogc:PropertyName>DMGLEVEL</ogc:PropertyName>
              <ogc:Literal>1.5</ogc:Literal>
            </ogc:PropertyIsLessThan>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#1EFC7C</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#0EEC6C</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>2</sld:Name>
          <sld:Title>Medium</sld:Title>
          <ogc:Filter>
            <ogc:And>
            <ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyName>DMGLEVEL</ogc:PropertyName>
              <ogc:Literal>1.5</ogc:Literal>
              </ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyIsLessThan>
                <ogc:PropertyName>DMGLEVEL</ogc:PropertyName>
                <ogc:Literal>2.5</ogc:Literal>
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
          <sld:Name>3</sld:Name>
          <sld:Title>High</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyName>DMGLEVEL</ogc:PropertyName>
              <ogc:Literal>2.5</ogc:Literal>
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
"""

        return style

    def Xgenerate_style(self, data):
        """Generates a point SLD file based on the data values
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
        class_keys = [_('Low damage'), _('Medium damage'), _('High damage')]
        class_values = [{'min': 0.5, 'max': 1.5,
                         'color': '#0efc7c', 'opacity': '1'},
                        {'min': 1.5, 'max': 2.5,
                         'color': '#fded0c', 'opacity': '1'},
                        {'min': 2.5, 'max': 3.5,
                         'color': '#e31a1c', 'opacity': '1'}]

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
