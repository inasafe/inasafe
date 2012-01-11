<?xml version="1.0" encoding="UTF-8"?>
<sld:UserStyle xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml">
  <sld:Name>raster</sld:Name>
  <sld:Title>Earthquake Intensity map</sld:Title>
  <sld:Abstract>Earthquake Intensity (MMI) map</sld:Abstract>
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
	<!--<ColorMapEntry color="#f3cb74" quantity="0.0"/>-->
        <ColorMapEntry color="#ffff11" quantity="0.03" opacity="0"/>
        <ColorMapEntry color="#5AE633" quantity="0.1"/>
        <ColorMapEntry color="#73FF55" quantity=".25"/>
        <ColorMapEntry color="#00A977" quantity=".5"/>
        <ColorMapEntry color="#34a899" quantity=".75"/>
        <ColorMapEntry color="#1f7eAA" quantity="1.0"/>
        <ColorMapEntry color="#1F43DD" quantity="1.5"/>
        <ColorMapEntry color="#0C00FF" quantity="2.0"/>
        </sld:ColorMap>
      </sld:RasterSymbolizer>
    </sld:Rule>
  </sld:FeatureTypeStyle>
</sld:UserStyle>