"""Fatality model using BNPB Podes data.

This was obtained from the WFS server

http://gisserver.bnpb.go.id:8399/arcgis/rest/services
http://gisserver.bnpb.go.id:8399/arcgis/rest/services/demografi
http://gisserver.bnpb.go.id:8399/arcgis/rest/services/demografi/Populasi_Penduduk_Kecamatan/FeatureServer?f=pjson

using wget, followed by processing the gml to swap coordinates using the script
https://github.com/AIFDR/riab/blob/develop/extras/swap_gml_coords.py

Finally, it was converted to the .shp format.

Eventually, this will be scripted and eventually work directly with the WFS
- see https://github.com/AIFDR/riab/issues/62
"""

import numpy
from impact_functions.core import FunctionProvider
from impact_functions.core import get_hazard_layer, get_exposure_layer
from storage.raster import Raster
from storage.vector import Vector


class EarthquakeFatalityFunctionPodes(FunctionProvider):
    """Risk plugin for earthquake fatalities using Podes polygon data

    :author Allen
    :rating 1
    :param requires category=='hazard' and \
                subcategory.startswith('earthquake') and \
                layer_type=='raster' and \
                unit=='MMI'

    :param requires category=='exposure' and \
                subcategory.startswith('population') and \
                layer_type=='vector' and \
                geometry=='polygon'
    """

    target_field = 'FATALITIES'

    def run(self, layers,
            a=0.97429, b=11.037):
        """Risk plugin for earthquake fatalities

        Input
          layers: List of layers expected to contain
                  H: Raster layer of MMI ground shaking
                  E: Polygon population data
          a: Parameter for Allen impact function
          b: Parameter for Allen impact function
        """

        # Identify input layers
        H = get_hazard_layer(layers)   # Intensity
        E = get_exposure_layer(layers)  # Exposure - population counts

        # Interpolate hazard level to building locations
        H = H.interpolate(E)

        # Extract relevant numerical data
        coordinates = E.get_geometry()  # Stay with polygons
        shaking = H.get_data()
        N = len(shaking)

        # List attributes to carry forward to result layer
        attributes = E.get_attribute_names()

        # Calculate fatilities
        count = 0
        total = 0

        result_feature_set = []
        for i in range(N):
            mmi = float(shaking[i].values()[0])
            if mmi < 0.0:
                # FIXME: Hack until interpolation is fixed
                mmi = 0.0

            population_count = E.get_data('Jumlah_Pen', i)

            # Calculate impact
            F = 10 ** (a * mmi - b) * population_count

            # Collect shake level and calculated damage
            result_dict = {self.target_field: F,
                           'MMI': mmi}

            # Carry all orginal attributes forward
            for key in attributes:
                result_dict[key] = E.get_data(key, i)

            # Record result for this feature
            result_feature_set.append(result_dict)

            # Calculate statistics
            if not numpy.isnan(F):
                count += F
            total += population_count

        # Create report
        caption = ('<table border="0" width="320px">'
                   '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                   '   <tr><td>%s&#58;</td><td>%i</td></tr>'
                   '</table>' % ('Jumlah Penduduk', int(total),
                                 'Perkiraan Orang Meninggal', int(count)))

        # Create vector layer and return
        V = Vector(data=result_feature_set,
                   projection=E.get_projection(),
                   geometry=coordinates,
                   name='Estimated fatalities',
                   keywords={'caption': caption})

        return V

    def generate_style(self, data):
        """Generates a polygon SLD file based on the data values
        """

        # FIXME (Ole): Return static style to start with: ticket #144
        style = """<?xml version="1.0" encoding="UTF-8"?>
<sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>podes_sub_district</sld:Name>
    <sld:UserStyle>
      <sld:Name>podes_sub_district</sld:Name>
      <sld:Title/>
      <sld:FeatureTypeStyle>
        <sld:Name>name</sld:Name>
        <sld:Rule>
          <sld:Name>2</sld:Name>
          <sld:Title>0 to 2.0</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsLessThan>
              <ogc:PropertyName>FATALITIES</ogc:PropertyName>
              <ogc:Literal>2.0</ogc:Literal>
            </ogc:PropertyIsLessThan>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#FFFFBE</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#000000</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>10</sld:Name>
          <sld:Title>2.1 to 10</sld:Title>
          <ogc:Filter>
            <ogc:And>
            <ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyName>FATALITIES</ogc:PropertyName>
              <ogc:Literal>2.0</ogc:Literal>
              </ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyIsLessThan>
                <ogc:PropertyName>FATALITIES</ogc:PropertyName>
                <ogc:Literal>10</ogc:Literal>
              </ogc:PropertyIsLessThan>
            </ogc:And>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#F5B800</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#000000</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>25</sld:Name>
          <sld:Title>10.1 to 25</sld:Title>
          <ogc:Filter>
            <ogc:And>
            <ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyName>FATALITIES</ogc:PropertyName>
              <ogc:Literal>10.0</ogc:Literal>
              </ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyIsLessThan>
                <ogc:PropertyName>FATALITIES</ogc:PropertyName>
                <ogc:Literal>25</ogc:Literal>
              </ogc:PropertyIsLessThan>
            </ogc:And>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#F57A00</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#000000</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>50</sld:Name>
          <sld:Title>25.1 to 50</sld:Title>
          <ogc:Filter>
            <ogc:And>
            <ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyName>FATALITIES</ogc:PropertyName>
              <ogc:Literal>25.0</ogc:Literal>
              </ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyIsLessThan>
                <ogc:PropertyName>FATALITIES</ogc:PropertyName>
                <ogc:Literal>50</ogc:Literal>
              </ogc:PropertyIsLessThan>
            </ogc:And>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#F53D00</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#000000</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>50</sld:Name>
          <sld:Title>2.1 to 10</sld:Title>
          <ogc:Filter>
            <ogc:PropertyIsGreaterThanOrEqualTo>
              <ogc:PropertyName>FATALITIES</ogc:PropertyName>
              <ogc:Literal>50.0</ogc:Literal>
            </ogc:PropertyIsGreaterThanOrEqualTo>
          </ogc:Filter>
          <sld:PolygonSymbolizer>
            <sld:Fill>
              <sld:CssParameter name="fill">#A80000</sld:CssParameter>
            </sld:Fill>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#000000</sld:CssParameter>
            </sld:Stroke>
          </sld:PolygonSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>
"""

        return style
