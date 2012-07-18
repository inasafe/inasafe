"""InaSAFE Disaster risk assessment tool developed by AusAid -
  **GMT Grid Importer.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

This module was originally part of the first realtime shakemap tool prototype
and was ported to InaSAFE by Tim Sutton, 18 July 2012.

Convert shakemap data as received from BMKG to GeoTIFF
"""

__author__ = 'ole.moller.nielsen@gmail.com, tim@linfiniti.com'
__version__ = '0.5.0'
__revision__ = '$Format:%H$'
__date__ = '18/06/2012'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import sys


def usage():
    print 'Usage:'
    print '%s shakefilename.grd' % sys.argv[0]


if __name__ == '__main__':

    if len(sys.argv) != 2:
        usage()
    else:
        infile = sys.argv[1]

        print 'Processing file %s' % infile
        basename, ext = os.path.splitext(infile)
        if ext != '.grd':
            usage()

        ascfile = basename + '.asc'
        tiffile = basename + '.tif'
        sldfile = basename + '.sld'

        # Convert to ASCII using GDAL
        s = ('gdal_translate -a_nodata -9999 -a_srs EPSG:4326 '
             '-of AAIGrid -co FORCE_CELLSIZE=TRUE '
             '%s %s' % (infile, ascfile))
        print s
        os.system(s)

        # # Flip rows upside down due to GMT convention
        # # (http://trac.osgeo.org/gdal/ticket/2654)
        print 'Reversing latitudes'
        fid = open(ascfile)
        lines = fid.readlines()
        fid.close()

        fid = open(ascfile, 'w')

        # Write headers back
        for line in lines[:5]:
            fid.write(line)

        # Write data lines in reverse order
        data = lines[5:]
        for line in data[::-1]:
            fid.write(line)

        fid.close()

        # Convert to GeoTiff using GDAL
        s = ('gdal_translate -a_nodata -9999 -a_srs EPSG:4326 -of GTiff '
             '%s %s' % (ascfile, tiffile))
        print s
        os.system(s)

        # Establish standard style for shakemaps
        print 'Writing style file'
        fid = open(sldfile, 'w')
        fid.write("""<?xml version="1.0" encoding="UTF-8"?>
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
        <!--<ColorMapEntry color="#CCCCFF" quantity="0.0"/>-->
        <ColorMapEntry color="#ebeef7" quantity="1.0" opacity="0"/>
        <ColorMapEntry color="#bdccff" quantity="2.0"/>
        <ColorMapEntry color="#a7effe" quantity="3.0"/>
        <ColorMapEntry color="#8cffe9" quantity="4.0"/>
        <ColorMapEntry color="#94ff77" quantity="5.0"/>
        <ColorMapEntry color="#38A800" quantity="5.5"/>
        <ColorMapEntry color="#79C900" quantity="6"/>
        <ColorMapEntry color="#CEED00" quantity="6.5"/>
        <ColorMapEntry color="#FFCC00" quantity="7"/>
        <ColorMapEntry color="#FF6600" quantity="7.5"/>
        <ColorMapEntry color="#FF0000" quantity="8"/>
        <ColorMapEntry color="#7A0000" quantity="10"/>

        <!--Higher-->
        </sld:ColorMap>
      </sld:RasterSymbolizer>
    </sld:Rule>
  </sld:FeatureTypeStyle>
</sld:UserStyle>
""")
        fid.close()



# Setting colour maps from http://osgeo-org.1803224.n2.nabble.com/tiff-creation-with-a-colormap-td2025799.html
"""

Didrik Pinte wrote:

> Hi,
>
> Little technical question. I have (x,y,z) raster that i'm outputting to
> a GeoTiff file with the following code :
>
> driver_options = ['TFW=YES' 'COMPRESS=DEFLATE']
> dst_ds = driver.Create( filename, len(self.idx['X']),\
>                             len(self.idx['Y']), 1, gdal.GDT_Byte,\
>                             driver_options )
> [... coord sys lines ...]
> dst_ds.GetRasterBand(1).WriteArray( numpy.transpose(raster) )
>
> This creates a great raster in levels of gray.
>
> Used to matplotlib, how can I output this raster with a colormap [1]? Do
> I have to generate three bands ?


Didrik,

Create a gdal.ColorTable object and then write it with SetRasterColorTable()
on the band.   Makeu sure you do this right after the create, and before
writing the raster data or else it will be too late.

Without testing, this might look something like:

  dst_ds = driver.Create( filename, len(self.idx['X']),\
                             len(self.idx['Y']), 1, gdal.GDT_Byte,\
                             driver_options )

  ct = gdal.ColorTable()
  for i in range(256):
    ct.SetColorEntry( i, (255, 255 - i, i, 255) )
  dst_ds.GetRasterBand(1).SetRasterColorTable( ct )

The tuple passed to SetColorEntry() holds Red,Green,Blue,Alpha values.

Best regards,
--

"""
