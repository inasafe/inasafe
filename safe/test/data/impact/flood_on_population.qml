<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="2.8.1-Wien" minimumScale="0" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <pipe>
    <rasterrenderer opacity="1" alphaBand="-1" classificationMax="nan" classificationMinMaxOrigin="Unknown" band="1" classificationMin="nan" type="singlebandpseudocolor">
      <rasterTransparency>
        <singleValuePixelList>
          <pixelListEntry min="0" max="1" percentTransparent="100"/>
        </singleValuePixelList>
      </rasterTransparency>
      <rastershader>
        <colorrampshader colorRampType="INTERPOLATED" clip="111">
          <item alpha="255" value="1" label="[0 - 1]" color="#ffffff"/>
          <item alpha="255" value="9.12851" label="[1 - 9] Low" color="#38a800"/>
          <item alpha="255" value="17.257" label="[9 - 17]" color="#79c900"/>
          <item alpha="255" value="25.3855" label="[17 - 25]" color="#ceed00"/>
          <item alpha="255" value="33.514" label="[25 - 34] Medium" color="#ffcc00"/>
          <item alpha="255" value="41.6426" label="[34 - 42]" color="#ff6600"/>
          <item alpha="255" value="49.7711" label="[42 - 50]" color="#ff0000"/>
          <item alpha="255" value="57.8996" label="[50 - 58] High" color="#7a0000"/>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness="0" contrast="0"/>
    <huesaturation colorizeGreen="128" colorizeOn="0" colorizeRed="255" colorizeBlue="128" grayscaleMode="0" saturation="0" colorizeStrength="100"/>
    <rasterresampler maxOversampling="2"/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
