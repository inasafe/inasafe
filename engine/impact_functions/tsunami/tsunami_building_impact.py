#from django.template.loader import render_to_string
from impact.plugins.core import FunctionProvider
from impact.plugins.core import get_hazard_layer, get_exposure_layer
from impact.storage.vector import Vector
from django.utils.translation import ugettext as _
from impact.plugins.utilities import PointZoomSize
from impact.plugins.utilities import PointClassColor
from impact.plugins.utilities import PointSymbol
import scipy.stats


class TsunamiBuildingImpactFunction(FunctionProvider):
    """Risk plugin for tsunami impact on building data

    :param requires category=='hazard' and \
                    subcategory.startswith('tsunami') and \
                    layer_type=='raster' and \
                    unit=='m'

    :param requires category=='exposure' and \
                    subcategory.startswith('building') and \
                    layer_type=='vector' and \
                    datatype=='osm'
    """

    target_field = 'ICLASS'

    def run(self, layers):
        """Risk plugin for tsunami population
        """

        # Extract data
        H = get_hazard_layer(layers)    # Depth
        E = get_exposure_layer(layers)  # Building locations

        #print 'Number of polygons', len(E)

        # Interpolate hazard level to building locations
        H = H.interpolate(E)

        # Extract relevant numerical data
        coordinates = E.get_geometry()
        depth = H.get_data()
        N = len(depth)

        # List attributes to carry forward to result layer
        attributes = E.get_attribute_names()

        # Calculate building impact according to guidelines
        count3 = 0
        count1 = 0
        count0 = 0
        population_impact = []
        for i in range(N):

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

            # Collect depth and calculated damage
            result_dict = {self.target_field: affected,
                           'DEPTH': dep}

            # Carry all original attributes forward
            for key in attributes:
                result_dict[key] = E.get_data(key, i)

            # Record result for this feature
            population_impact.append(result_dict)

        # Create report
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

        # Create vector layer and return
        V = Vector(data=population_impact,
                   projection=E.get_projection(),
                   geometry=coordinates,
                   name='Estimate of buildings affected',
                   keywords={'caption': caption})
        return V

    def generate_style(self, data):
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
              <ogc:PropertyName>ICLASS</ogc:PropertyName>
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
              <ogc:PropertyName>ICLASS</ogc:PropertyName>
              <ogc:Literal>1.5</ogc:Literal>
              </ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyIsLessThan>
                <ogc:PropertyName>ICLASS</ogc:PropertyName>
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
              <ogc:PropertyName>ICLASS</ogc:PropertyName>
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
        """Generates and SLD file based on the data values
        """
        #DEFAULT_SYMBOL = 'ttf://Webdings#0x0067'
        DEFAULT_SYMBOL = 'circle'

        symbol_field = None
        symbol_keys = [None, '']
        symbol_values = [DEFAULT_SYMBOL, DEFAULT_SYMBOL]

        # Zoom levels (large number means close up)
        scale_keys = [50000000000, 10000000000, 10000000, 5000000,
                      1000000, 500000, 250000, 100000]
        scale_values = [2, 4, 6, 8, 1, 1, 1, 1]

        # Predefined colour classes
        class_keys = ['< 1 m', '1 - 3 m', '> 3 m']
        class_values = [{'min': 0.5, 'max': 1.5,
                         'color': '#cccccc', 'opacity': '1'},
                        {'min': 1.5, 'max': 2.5,
                         'color': '#fd8d3c', 'opacity': '1'},
                        {'min': 2.5, 'max': 3.5,
                         'color': '#e31a1c', 'opacity': '1'}]

        if self.symbol_field in data.get_attribute_names():
            symbol_field = self.symbol_field

            symbol_keys.extend(['Church/Mosque', 'Commercial (office)',
                                'Hotel',
                                'Medical facility', 'Other',
                                'Other industrial',
                                'Residential', 'Retail', 'School',
                                'Unknown', 'Warehouse'])

            symbol_values.extend([DEFAULT_SYMBOL, DEFAULT_SYMBOL,
                                  DEFAULT_SYMBOL,
                                  DEFAULT_SYMBOL, DEFAULT_SYMBOL,
                                  DEFAULT_SYMBOL,
                                  DEFAULT_SYMBOL, DEFAULT_SYMBOL,
                                  DEFAULT_SYMBOL,
                                  DEFAULT_SYMBOL, DEFAULT_SYMBOL])

        params = dict(name=data.get_name(),
                      damage_field=self.target_field,
                      symbol_field=symbol_field,
                      symbols=dict(zip(symbol_keys, symbol_values)),
                      scales=dict(zip(scale_keys, scale_values)),
                      classifications=dict(zip(class_keys, class_values)))

        return render_to_string('impact/styles/point_classes.sld', params)
