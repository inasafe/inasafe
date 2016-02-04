<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="2.0.1-Dufour" minimumScale="0" maximumScale="1e+08" minLabelScale="0" maxLabelScale="1e+08" hasScaleBasedVisibilityFlag="0" scaleBasedLabelVisibilityFlag="0">
  <renderer-v2 symbollevels="0" type="RuleRenderer">
    <rules>
      <rule scalemaxdenom="25000" scalemindenom="1" label="1:25000">
        <rule filter="&quot;TYPE&quot; = 'Motorway or highway'" symbol="0" label="Motorway or highway"/>
        <rule filter="&quot;TYPE&quot; = 'Motorway link'" symbol="1" label="Motorway Link"/>
        <rule filter="&quot;TYPE&quot; = 'Primary road'" symbol="2" label="Primary road"/>
        <rule filter="&quot;TYPE&quot; = 'Primary link'" symbol="3" label="Primary link"/>
        <rule filter="&quot;TYPE&quot; = 'Tertiary'" symbol="4" label="Tertiary"/>
        <rule filter="&quot;TYPE&quot; = 'Tertiary link'" symbol="5" label="Tertiary link"/>
        <rule filter="&quot;TYPE&quot; = 'Secondary'" symbol="6" label="Secondary"/>
        <rule filter="&quot;TYPE&quot; = 'Secondary link'" symbol="7" label="Secondary link"/>
        <rule filter="&quot;TYPE&quot; = 'Road, residential, living street, etc.'" symbol="8" label="Road, residential, living street, etc."/>
        <rule filter="&quot;TYPE&quot; = 'Track'" symbol="9" label="Track"/>
        <rule filter="&quot;TYPE&quot; = 'Cycleway, footpath, etc.'" symbol="10" label="Cycleway, footpath etc."/>
      </rule>
      <rule scalemaxdenom="50000" symbol="11" scalemindenom="25001" label="25k to 50k">
        <rule filter=" &quot;TYPE&quot;  =  'Motorway or highway'" symbol="12" label="Motorway or highway"/>
        <rule filter="&quot;TYPE&quot; = 'Primary road'" symbol="13" label="Primary"/>
      </rule>
      <rule scalemaxdenom="10000000" symbol="14" scalemindenom="50001" label="50k +">
        <rule filter=" &quot;TYPE&quot;  =  'Motorway or highway' " symbol="15" label="Motorway or highway"/>
      </rule>
    </rules>
    <symbols>
      <symbol alpha="1" type="line" name="0">
        <layer pass="20" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="20,50,50,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="3.86"/>
          <prop k="width_unit" v="MM"/>
        </layer>
        <layer pass="21" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="94,146,148,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="3.56"/>
          <prop k="width_unit" v="MM"/>
        </layer>
      </symbol>
      <symbol alpha="1" type="line" name="1">
        <layer pass="18" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="20,50,50,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="2.2"/>
          <prop k="width_unit" v="MM"/>
        </layer>
        <layer pass="19" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="100,165,165,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="2.1"/>
          <prop k="width_unit" v="MM"/>
        </layer>
      </symbol>
      <symbol alpha="1" type="line" name="10">
        <layer pass="1" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="170,110,142,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="0.66"/>
          <prop k="width_unit" v="MM"/>
        </layer>
        <layer pass="1" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="255,255,255,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="dot"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="0.53"/>
          <prop k="width_unit" v="MM"/>
        </layer>
      </symbol>
      <symbol alpha="1" type="line" name="11">
        <layer pass="1" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="80,80,80,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="1"/>
          <prop k="width_unit" v="MM"/>
        </layer>
        <layer pass="2" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="248,248,248,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="0.8"/>
          <prop k="width_unit" v="MM"/>
        </layer>
      </symbol>
      <symbol alpha="1" type="line" name="12">
        <layer pass="1" class="SimpleLine" locked="1">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="20,50,50,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="3.86"/>
          <prop k="width_unit" v="MM"/>
        </layer>
        <layer pass="20" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="94,146,148,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="3.56"/>
          <prop k="width_unit" v="MM"/>
        </layer>
      </symbol>
      <symbol alpha="1" type="line" name="13">
        <layer pass="1" class="SimpleLine" locked="1">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="76,38,0,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="2.1"/>
          <prop k="width_unit" v="MM"/>
        </layer>
        <layer pass="16" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="255,206,128,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="1.9"/>
          <prop k="width_unit" v="MM"/>
        </layer>
      </symbol>
      <symbol alpha="1" type="line" name="14">
        <layer pass="1" class="SimpleLine" locked="0">
          <prop k="capstyle" v="square"/>
          <prop k="color" v="84,84,84,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="0.26"/>
          <prop k="width_unit" v="MM"/>
        </layer>
      </symbol>
      <symbol alpha="1" type="line" name="15">
        <layer pass="1" class="SimpleLine" locked="1">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="20,50,50,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="2.2"/>
          <prop k="width_unit" v="MM"/>
        </layer>
        <layer pass="16" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="100,165,165,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="2.1"/>
          <prop k="width_unit" v="MM"/>
        </layer>
      </symbol>
      <symbol alpha="1" type="line" name="2">
        <layer pass="16" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="76,38,0,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="3.56"/>
          <prop k="width_unit" v="MM"/>
        </layer>
        <layer pass="17" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="255,206,128,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="3.36"/>
          <prop k="width_unit" v="MM"/>
        </layer>
      </symbol>
      <symbol alpha="1" type="line" name="3">
        <layer pass="14" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="76,38,0,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="2.1"/>
          <prop k="width_unit" v="MM"/>
        </layer>
        <layer pass="15" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="255,206,128,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="1.9"/>
          <prop k="width_unit" v="MM"/>
        </layer>
      </symbol>
      <symbol alpha="1" type="line" name="4">
        <layer pass="1" class="SimpleLine" locked="1">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="214,214,214,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="2.26"/>
          <prop k="width_unit" v="MM"/>
        </layer>
        <layer pass="13" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="165,222,173,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="1.26"/>
          <prop k="width_unit" v="MM"/>
        </layer>
      </symbol>
      <symbol alpha="1" type="line" name="5">
        <layer pass="1" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="223,223,223,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="2.26"/>
          <prop k="width_unit" v="MM"/>
        </layer>
        <layer pass="11" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="165,222,173,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="1.26"/>
          <prop k="width_unit" v="MM"/>
        </layer>
      </symbol>
      <symbol alpha="1" type="line" name="6">
        <layer pass="1" class="SimpleLine" locked="0">
          <prop k="capstyle" v="square"/>
          <prop k="color" v="223,223,223,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="1.7"/>
          <prop k="width_unit" v="MM"/>
        </layer>
        <layer pass="9" class="SimpleLine" locked="0">
          <prop k="capstyle" v="square"/>
          <prop k="color" v="255,206,211,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="1.5"/>
          <prop k="width_unit" v="MM"/>
        </layer>
      </symbol>
      <symbol alpha="1" type="line" name="7">
        <layer pass="1" class="SimpleLine" locked="0">
          <prop k="capstyle" v="square"/>
          <prop k="color" v="223,223,223,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="1.4"/>
          <prop k="width_unit" v="MM"/>
        </layer>
        <layer pass="7" class="SimpleLine" locked="0">
          <prop k="capstyle" v="square"/>
          <prop k="color" v="255,206,211,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="1.2"/>
          <prop k="width_unit" v="MM"/>
        </layer>
      </symbol>
      <symbol alpha="1" type="line" name="8">
        <layer pass="1" class="SimpleLine" locked="1">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="80,80,80,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="1.6"/>
          <prop k="width_unit" v="MM"/>
        </layer>
        <layer pass="5" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="248,248,248,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="1.4"/>
          <prop k="width_unit" v="MM"/>
        </layer>
      </symbol>
      <symbol alpha="1" type="line" name="9">
        <layer pass="1" class="SimpleLine" locked="1">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="223,223,223,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="2.26"/>
          <prop k="width_unit" v="MM"/>
        </layer>
        <layer pass="3" class="SimpleLine" locked="0">
          <prop k="capstyle" v="round"/>
          <prop k="color" v="217,218,166,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="customdash_unit" v="MM"/>
          <prop k="joinstyle" v="round"/>
          <prop k="offset" v="0"/>
          <prop k="offset_unit" v="MM"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="1.26"/>
          <prop k="width_unit" v="MM"/>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <customproperties>
    <property key="labeling" value="pal"/>
    <property key="labeling/addDirectionSymbol" value="false"/>
    <property key="labeling/angleOffset" value="0"/>
    <property key="labeling/blendMode" value="0"/>
    <property key="labeling/bufferBlendMode" value="0"/>
    <property key="labeling/bufferColorA" value="255"/>
    <property key="labeling/bufferColorB" value="255"/>
    <property key="labeling/bufferColorG" value="255"/>
    <property key="labeling/bufferColorR" value="255"/>
    <property key="labeling/bufferDraw" value="true"/>
    <property key="labeling/bufferJoinStyle" value="64"/>
    <property key="labeling/bufferNoFill" value="false"/>
    <property key="labeling/bufferSize" value="1.2"/>
    <property key="labeling/bufferSizeInMapUnits" value="false"/>
    <property key="labeling/bufferTransp" value="0"/>
    <property key="labeling/centroidWhole" value="false"/>
    <property key="labeling/decimals" value="3"/>
    <property key="labeling/displayAll" value="false"/>
    <property key="labeling/dist" value="0"/>
    <property key="labeling/distInMapUnits" value="false"/>
    <property key="labeling/enabled" value="true"/>
    <property key="labeling/fieldName" value="name"/>
    <property key="labeling/fontBold" value="false"/>
    <property key="labeling/fontCapitals" value="0"/>
    <property key="labeling/fontFamily" value="FreeSansQGIS"/>
    <property key="labeling/fontItalic" value="false"/>
    <property key="labeling/fontLetterSpacing" value="0"/>
    <property key="labeling/fontLimitPixelSize" value="false"/>
    <property key="labeling/fontMaxPixelSize" value="10000"/>
    <property key="labeling/fontMinPixelSize" value="3"/>
    <property key="labeling/fontSize" value="8"/>
    <property key="labeling/fontSizeInMapUnits" value="false"/>
    <property key="labeling/fontStrikeout" value="false"/>
    <property key="labeling/fontUnderline" value="false"/>
    <property key="labeling/fontWeight" value="50"/>
    <property key="labeling/fontWordSpacing" value="0"/>
    <property key="labeling/formatNumbers" value="false"/>
    <property key="labeling/isExpression" value="false"/>
    <property key="labeling/labelOffsetInMapUnits" value="true"/>
    <property key="labeling/labelPerPart" value="false"/>
    <property key="labeling/leftDirectionSymbol" value="&lt;"/>
    <property key="labeling/limitNumLabels" value="false"/>
    <property key="labeling/maxCurvedCharAngleIn" value="20"/>
    <property key="labeling/maxCurvedCharAngleOut" value="-20"/>
    <property key="labeling/maxNumLabels" value="2000"/>
    <property key="labeling/mergeLines" value="true"/>
    <property key="labeling/minFeatureSize" value="10"/>
    <property key="labeling/multilineAlign" value="0"/>
    <property key="labeling/multilineHeight" value="1"/>
    <property key="labeling/namedStyle" value="Medium"/>
    <property key="labeling/obstacle" value="true"/>
    <property key="labeling/placeDirectionSymbol" value="0"/>
    <property key="labeling/placement" value="3"/>
    <property key="labeling/placementFlags" value="9"/>
    <property key="labeling/plussign" value="false"/>
    <property key="labeling/preserveRotation" value="true"/>
    <property key="labeling/previewBkgrdColor" value="#ffffff"/>
    <property key="labeling/priority" value="5"/>
    <property key="labeling/quadOffset" value="4"/>
    <property key="labeling/reverseDirectionSymbol" value="false"/>
    <property key="labeling/rightDirectionSymbol" value=">"/>
    <property key="labeling/scaleMax" value="10000000"/>
    <property key="labeling/scaleMin" value="1"/>
    <property key="labeling/scaleVisibility" value="false"/>
    <property key="labeling/shadowBlendMode" value="6"/>
    <property key="labeling/shadowColorB" value="0"/>
    <property key="labeling/shadowColorG" value="0"/>
    <property key="labeling/shadowColorR" value="0"/>
    <property key="labeling/shadowDraw" value="true"/>
    <property key="labeling/shadowOffsetAngle" value="135"/>
    <property key="labeling/shadowOffsetDist" value="1"/>
    <property key="labeling/shadowOffsetGlobal" value="true"/>
    <property key="labeling/shadowOffsetUnits" value="1"/>
    <property key="labeling/shadowRadius" value="1.5"/>
    <property key="labeling/shadowRadiusAlphaOnly" value="false"/>
    <property key="labeling/shadowRadiusUnits" value="1"/>
    <property key="labeling/shadowScale" value="100"/>
    <property key="labeling/shadowTransparency" value="30"/>
    <property key="labeling/shadowUnder" value="1"/>
    <property key="labeling/shapeBlendMode" value="0"/>
    <property key="labeling/shapeBorderColorA" value="255"/>
    <property key="labeling/shapeBorderColorB" value="128"/>
    <property key="labeling/shapeBorderColorG" value="128"/>
    <property key="labeling/shapeBorderColorR" value="128"/>
    <property key="labeling/shapeBorderWidth" value="0"/>
    <property key="labeling/shapeBorderWidthUnits" value="1"/>
    <property key="labeling/shapeDraw" value="false"/>
    <property key="labeling/shapeFillColorA" value="255"/>
    <property key="labeling/shapeFillColorB" value="255"/>
    <property key="labeling/shapeFillColorG" value="255"/>
    <property key="labeling/shapeFillColorR" value="255"/>
    <property key="labeling/shapeJoinStyle" value="64"/>
    <property key="labeling/shapeOffsetUnits" value="1"/>
    <property key="labeling/shapeOffsetX" value="0"/>
    <property key="labeling/shapeOffsetY" value="0"/>
    <property key="labeling/shapeRadiiUnits" value="1"/>
    <property key="labeling/shapeRadiiX" value="0"/>
    <property key="labeling/shapeRadiiY" value="0"/>
    <property key="labeling/shapeRotation" value="0"/>
    <property key="labeling/shapeRotationType" value="0"/>
    <property key="labeling/shapeSVGFile" value=""/>
    <property key="labeling/shapeSizeType" value="0"/>
    <property key="labeling/shapeSizeUnits" value="1"/>
    <property key="labeling/shapeSizeX" value="0"/>
    <property key="labeling/shapeSizeY" value="0"/>
    <property key="labeling/shapeTransparency" value="0"/>
    <property key="labeling/shapeType" value="0"/>
    <property key="labeling/textColorA" value="255"/>
    <property key="labeling/textColorB" value="0"/>
    <property key="labeling/textColorG" value="0"/>
    <property key="labeling/textColorR" value="0"/>
    <property key="labeling/textTransp" value="0"/>
    <property key="labeling/upsidedownLabels" value="0"/>
    <property key="labeling/wrapChar" value=""/>
    <property key="labeling/xOffset" value="0"/>
    <property key="labeling/yOffset" value="0"/>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerTransparency>0</layerTransparency>
  <displayfield>addr:housename</displayfield>
  <label>0</label>
  <labelattributes>
    <label fieldname="" text="Label"/>
    <family fieldname="" name="Ubuntu"/>
    <size fieldname="" units="pt" value="12"/>
    <bold fieldname="" on="0"/>
    <italic fieldname="" on="0"/>
    <underline fieldname="" on="0"/>
    <strikeout fieldname="" on="0"/>
    <color fieldname="" red="0" blue="0" green="0"/>
    <x fieldname=""/>
    <y fieldname=""/>
    <offset x="0" y="0" units="pt" yfieldname="" xfieldname=""/>
    <angle fieldname="" value="0" auto="0"/>
    <alignment fieldname="" value="center"/>
    <buffercolor fieldname="" red="255" blue="255" green="255"/>
    <buffersize fieldname="" units="pt" value="1"/>
    <bufferenabled fieldname="" on=""/>
    <multilineenabled fieldname="" on=""/>
    <selectedonly on=""/>
  </labelattributes>
  <edittypes>
    <edittype labelontop="0" editable="1" type="0" name="NAME"/>
    <edittype labelontop="0" editable="1" type="0" name="OSM_TYPE"/>
    <edittype labelontop="0" editable="1" type="0" name="TYPE"/>
    <edittype labelontop="0" editable="1" type="0" name="access"/>
    <edittype labelontop="0" editable="1" type="0" name="access:roof"/>
    <edittype labelontop="0" editable="1" type="0" name="addr:full"/>
    <edittype labelontop="0" editable="1" type="0" name="addr:housename"/>
    <edittype labelontop="0" editable="1" type="0" name="addr:housenumber"/>
    <edittype labelontop="0" editable="1" type="0" name="addr:interpolation"/>
    <edittype labelontop="0" editable="1" type="0" name="admin_level"/>
    <edittype labelontop="0" editable="1" type="0" name="aerialway"/>
    <edittype labelontop="0" editable="1" type="0" name="aeroway"/>
    <edittype labelontop="0" editable="1" type="0" name="amenity"/>
    <edittype labelontop="0" editable="1" type="0" name="area"/>
    <edittype labelontop="0" editable="1" type="0" name="barrier"/>
    <edittype labelontop="0" editable="1" type="0" name="bicycle"/>
    <edittype labelontop="0" editable="1" type="0" name="boundary"/>
    <edittype labelontop="0" editable="1" type="0" name="brand"/>
    <edittype labelontop="0" editable="1" type="0" name="bridge"/>
    <edittype labelontop="0" editable="1" type="0" name="building"/>
    <edittype labelontop="0" editable="1" type="0" name="building:levels"/>
    <edittype labelontop="0" editable="1" type="0" name="building:roof"/>
    <edittype labelontop="0" editable="1" type="0" name="building:structure"/>
    <edittype labelontop="0" editable="1" type="0" name="building:use"/>
    <edittype labelontop="0" editable="1" type="0" name="building:walls"/>
    <edittype labelontop="0" editable="1" type="0" name="capacity:persons"/>
    <edittype labelontop="0" editable="1" type="0" name="construction"/>
    <edittype labelontop="0" editable="1" type="0" name="covered"/>
    <edittype labelontop="0" editable="1" type="0" name="culvert"/>
    <edittype labelontop="0" editable="1" type="0" name="cutting"/>
    <edittype labelontop="0" editable="1" type="0" name="denomination"/>
    <edittype labelontop="0" editable="1" type="0" name="disused"/>
    <edittype labelontop="0" editable="1" type="0" name="embankment"/>
    <edittype labelontop="0" editable="1" type="0" name="flooded"/>
    <edittype labelontop="0" editable="1" type="0" name="foot"/>
    <edittype labelontop="0" editable="1" type="0" name="generator:source"/>
    <edittype labelontop="0" editable="1" type="0" name="harbour"/>
    <edittype labelontop="0" editable="1" type="0" name="highway"/>
    <edittype labelontop="0" editable="1" type="0" name="historic"/>
    <edittype labelontop="0" editable="1" type="0" name="horse"/>
    <edittype labelontop="0" editable="1" type="0" name="id"/>
    <edittype labelontop="0" editable="1" type="0" name="intermittent"/>
    <edittype labelontop="0" editable="1" type="0" name="junction"/>
    <edittype labelontop="0" editable="1" type="0" name="landuse"/>
    <edittype labelontop="0" editable="1" type="0" name="layer"/>
    <edittype labelontop="0" editable="1" type="0" name="leisure"/>
    <edittype labelontop="0" editable="1" type="0" name="lock"/>
    <edittype labelontop="0" editable="1" type="0" name="man_made"/>
    <edittype labelontop="0" editable="1" type="0" name="military"/>
    <edittype labelontop="0" editable="1" type="0" name="motorcar"/>
    <edittype labelontop="0" editable="1" type="0" name="name"/>
    <edittype labelontop="0" editable="1" type="0" name="natural"/>
    <edittype labelontop="0" editable="1" type="0" name="office"/>
    <edittype labelontop="0" editable="1" type="0" name="oneway"/>
    <edittype labelontop="0" editable="1" type="0" name="operator"/>
    <edittype labelontop="0" editable="1" type="0" name="osm_id"/>
    <edittype labelontop="0" editable="1" type="0" name="osm_type"/>
    <edittype labelontop="0" editable="1" type="0" name="place"/>
    <edittype labelontop="0" editable="1" type="0" name="population"/>
    <edittype labelontop="0" editable="1" type="0" name="power"/>
    <edittype labelontop="0" editable="1" type="0" name="power_source"/>
    <edittype labelontop="0" editable="1" type="0" name="public_transport"/>
    <edittype labelontop="0" editable="1" type="0" name="railway"/>
    <edittype labelontop="0" editable="1" type="0" name="ref"/>
    <edittype labelontop="0" editable="1" type="0" name="religion"/>
    <edittype labelontop="0" editable="1" type="0" name="route"/>
    <edittype labelontop="0" editable="1" type="0" name="service"/>
    <edittype labelontop="0" editable="1" type="0" name="shop"/>
    <edittype labelontop="0" editable="1" type="0" name="sport"/>
    <edittype labelontop="0" editable="1" type="0" name="surface"/>
    <edittype labelontop="0" editable="1" type="0" name="toll"/>
    <edittype labelontop="0" editable="1" type="0" name="tourism"/>
    <edittype labelontop="0" editable="1" type="0" name="tower:type"/>
    <edittype labelontop="0" editable="1" type="0" name="tracktype"/>
    <edittype labelontop="0" editable="1" type="0" name="tunnel"/>
    <edittype labelontop="0" editable="1" type="0" name="type"/>
    <edittype labelontop="0" editable="1" type="0" name="type:id"/>
    <edittype labelontop="0" editable="1" type="0" name="water"/>
    <edittype labelontop="0" editable="1" type="0" name="waterway"/>
    <edittype labelontop="0" editable="1" type="0" name="way_area"/>
    <edittype labelontop="0" editable="1" type="0" name="wetland"/>
    <edittype labelontop="0" editable="1" type="0" name="width"/>
    <edittype labelontop="0" editable="1" type="0" name="wood"/>
    <edittype labelontop="0" editable="1" type="0" name="z_order"/>
  </edittypes>
  <editform>/gisdata/InaSAFEPackages/Jakarta</editform>
  <editforminit></editforminit>
  <annotationform>/gisdata/InaSAFEPackages/Jakarta</annotationform>
  <editorlayout>generatedlayout</editorlayout>
  <excludeAttributesWMS/>
  <excludeAttributesWFS/>
  <attributeactions/>
</qgis>
