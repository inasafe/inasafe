<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories="AllStyleCategories" minScale="1e+08" maxScale="0" hasScaleBasedVisibilityFlag="0" version="3.10.0-A Coruña">
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
  </flags>
  <customproperties>
    <property key="WMSBackgroundLayer" value="false"/>
    <property key="WMSPublishDataSourceUrl" value="false"/>
    <property key="embeddedWidgets/count" value="0"/>
    <property key="identify/format" value="Value"/>
  </customproperties>
  <pipe>
    <rasterrenderer band="1" classificationMax="5.8627" alphaBand="-1" classificationMin="0" type="singlebandpseudocolor" opacity="1">
      <rasterTransparency/>
      <minMaxOrigin>
        <limits>MinMax</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Exact</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <rastershader>
        <colorrampshader colorRampType="DISCRETE" classificationMode="1" clip="0">
          <colorramp name="[source]" type="gradient">
            <prop v="255,245,240,255" k="color1"/>
            <prop v="103,0,13,255" k="color2"/>
            <prop v="0" k="discrete"/>
            <prop v="gradient" k="rampType"/>
            <prop v="0.13;254,224,210,255:0.26;252,187,161,255:0.39;252,146,114,255:0.52;251,106,74,255:0.65;239,59,44,255:0.78;203,24,29,255:0.9;165,15,21,255" k="stops"/>
          </colorramp>
          <item value="0.67746755388048" label="&lt;= 0.67746755388048" alpha="255" color="#fff5f0"/>
          <item value="1.35493510776096" label="0.67746755388048 - 1.35493510776096" alpha="255" color="#fee0d2"/>
          <item value="2.03240266164144" label="1.35493510776096 - 2.03240266164144" alpha="255" color="#fcbba1"/>
          <item value="2.70987021552192" label="2.03240266164144 - 2.70987021552192" alpha="255" color="#fc9272"/>
          <item value="3.3873377694024" label="2.70987021552192 - 3.3873377694024" alpha="255" color="#fb6a4a"/>
          <item value="4.06480532328288" label="3.3873377694024 - 4.06480532328288" alpha="255" color="#ef3b2c"/>
          <item value="4.69015998840332" label="4.06480532328288 - 4.69015998840332" alpha="255" color="#cb181d"/>
          <item value="5.21128887600369" label="4.69015998840332 - 5.21128887600369" alpha="255" color="#a50f15"/>
          <item value="inf" label="> 5.21128887600369" alpha="255" color="#67000d"/>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast contrast="0" brightness="0"/>
    <huesaturation grayscaleMode="0" colorizeRed="255" colorizeOn="0" colorizeBlue="128" colorizeGreen="128" colorizeStrength="100" saturation="0"/>
    <rasterresampler maxOversampling="2"/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
