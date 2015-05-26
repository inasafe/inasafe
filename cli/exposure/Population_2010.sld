<?xml version="1.0" encoding="UTF-8"?>
<sld:UserStyle xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml">
  <sld:Name>raster</sld:Name>
  <sld:Title>A very simple color map</sld:Title>
  <sld:Abstract>A very basic color map</sld:Abstract>
  <sld:FeatureTypeStyle>
    <sld:Name>name</sld:Name>
    <sld:FeatureTypeName>Feature</sld:FeatureTypeName>
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
       	<ColorMapEntry color="#ffffff" quantity="-9999.0" opacity="0"/>
	<!--<ColorMapEntry color="#CCCCFF" quantity="0.0"/>-->
        <ColorMapEntry color="#E1E1E1" quantity="1.0"/>
        <ColorMapEntry color="#FFFFBE" quantity="10"/>
        <ColorMapEntry color="#FFAA00" quantity="500"/>
        <ColorMapEntry color="#FF6600" quantity="1000"/>
        <ColorMapEntry color="#FF0000" quantity="10000"/>
        <ColorMapEntry color="#CC0000" quantity="100000"/>
        <ColorMapEntry color="#730000" quantity="200000"/>
        <ColorMapEntry color="#000000" quantity="300000"/>
	<!--Higher-->
        </sld:ColorMap>
      </sld:RasterSymbolizer>
    </sld:Rule>
  </sld:FeatureTypeStyle>
</sld:UserStyle>
