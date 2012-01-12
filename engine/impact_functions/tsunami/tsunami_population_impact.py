import numpy

from impact.plugins.core import FunctionProvider
from impact.plugins.core import get_hazard_layer, get_exposure_layer
from impact.storage.raster import Raster
from django.utils.translation import ugettext as _


class TsunamiPopulationImpactFunction(FunctionProvider):
    """Risk plugin for tsunami impact on population data

    :param requires category=='hazard' and \
                    subcategory.startswith('tsunami') and \
                    layer_type=='raster' and \
                    unit=='m'

    :param requires category=='exposure' and \
                    subcategory.startswith('population') and \
                    layer_type=='raster'

    """

    def run(self, layers):
        """Risk plugin for tsunami population
        """

        thresholds = [0.2, 0.3, 0.5, 0.8, 1.0]
        #threshold = 1  # Depth above which people are regarded affected [m]

        # Identify hazard and exposure layers
        inundation = get_hazard_layer(layers)    # Tsunami inundation [m]
        population = get_exposure_layer(layers)  # Population density

        # Extract data as numeric arrays
        D = inundation.get_data(nan=0.0)  # Depth
        P = population.get_data(nan=0.0, scaling=True)  # Population density

        # Calculate impact as population exposed to depths > 1m
        I_map = numpy.where(D > thresholds[-1], P, 0)

        # Generate text with result for this study
        number_of_people_affected = numpy.nansum(I_map.flat)

        # Do breakdown

        # Create report
        caption = ('<table border="0" width="320px">'
                   '   <tr><th><b>%s</b></th><th><b>%s</b></th></th>'
                   '   <tr></tr>' % ('Ambang batas', 'Jumlah orang terdampak'))

        counts = []
        for i, threshold in enumerate(thresholds):
            I = numpy.where(D > threshold, P, 0)
            counts.append(numpy.nansum(I.flat))

            caption += '   <tr><td>%s m</td><td>%i</td></tr>' % (threshold,
                                                                 counts[i])

        caption += '</table>'

        # Create raster object and return
        R = Raster(I_map,
                   projection=inundation.get_projection(),
                   geotransform=inundation.get_geotransform(),
                   name='People affected by more than 1m of inundation',
                   keywords={'caption': caption})
        return R

    def generate_style(self, data):
        """Generates and SLD file based on the data values
        """

        s = """<?xml version="1.0" encoding="UTF-8"?>
<sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>People affected by more than 1m of inundation</sld:Name>
    <sld:UserStyle>
      <sld:Name>People affected by more than 1m of inundation</sld:Name>
      <sld:Title>People Affected By More Than 1m Of Inundation</sld:Title>
      <sld:Abstract>People Affected By More Than 1m Of Inundation</sld:Abstract>
      <sld:FeatureTypeStyle>
        <sld:Name>People affected by more than 1m of inundation</sld:Name>
        <sld:Rule>
          <sld:RasterSymbolizer>
            <sld:Geometry>
              <ogc:PropertyName>geom</ogc:PropertyName>
            </sld:Geometry>
            <sld:ChannelSelection>
              <sld:GrayChannel>
                <sld:SourceChannelName>1</sld:SourceChannelName>
              </sld:GrayChannel>
            </sld:ChannelSelection>
            <sld:ColorMap>
              <sld:ColorMapEntry color="#ffffff" opacity="0" quantity="-9999.0"/>
              <sld:ColorMapEntry color="#38A800" opacity="0" quantity="0.01"/>
              <sld:ColorMapEntry color="#38A800" quantity="0.02"/>
              <sld:ColorMapEntry color="#79C900" quantity="0.05"/>
              <sld:ColorMapEntry color="#CEED00" quantity="0.1"/>
              <sld:ColorMapEntry color="#FFCC00" quantity="0.2"/>
              <sld:ColorMapEntry color="#FF6600" quantity="0.3"/>
              <sld:ColorMapEntry color="#FF0000" quantity="0.5"/>
              <sld:ColorMapEntry color="#7A0000" quantity="0.9"/>
            </sld:ColorMap>
          </sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>

        """

        return s
