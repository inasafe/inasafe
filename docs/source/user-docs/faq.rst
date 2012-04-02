Frequently Asked Questions
==========================


How do I rename a shape file and all the helper files?
::::::::::::::::::::::::::::::::::::::::::::::::::::::

  Use the rename command. rename [ -v ] [ -n ] [ -f ] perlexpr [ files ].
  For example
    rename -v "s/^building/OSM_building_polygons_20110905/" building.*

How do I reproject a spatial data file to WGS84 geographic coordinates
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

  For raster data, use gdalwarp, for example
  gdalwarp -t_srs EPSG:4326 <source>.tif <target>.tif

  For vector data use ogr2ogr. For example from TM-3 zone 48.2
  ogr2ogr -s_srs EPSG:23834 -t_srs EPSG:4326 <target>.shp <source>.shp

How do I get Open Street Map building data into |project_name|?
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

  For Indonesia, you can download latest collections at http://data.kompetisiosm.org

  or you can add our Open Street Map building PostGIS mirror to riab::

 * Add PostGIS layer with host=203.77.224.77, database=osm, username=aifdr, port 5432, SSL mode=disable
 * Select view named vw_planet_osm_polygon
 * We don't yet have direct support for PostGIS, so save the layer as a
   shapefile, load it and add the appropriate keywords (category: exposure, subcategory: building)
# * Build query: upper(geometrytype("way")) IN ('POLYGON','MULTIPOLYGON') AND BUILDING != ''

How do I take screen capture e.g. for use in a presentation?
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

  On Ubuntu, get the packages gtk-recordmydesktop and mencoder
  Record using recordmydesktop (start and stop icon in the top bar)
  Convert to other formats using mencoder, e.g.

<pre>
  mencoder -idx yogya_analysis-6.ogv -ovc lavc -oac lavc -lavcopts vcodec=mpeg4:vpass=1 -of lavf -o yogya_analysis.avi
</pre> 

  or

<pre>
  mencoder -idx yogya_analysis-6.ogv -ovc lavc -oac lavc -lavcopts vcodec=wmv2 -of lavf -o yogya_analysis.wmv
</pre>

How does the documentation work?::

  The |project_name| documentation files are written using the RST format
  (http://docutils.sourceforge.net/docs/user/rst/quickref.html) and stored with
  the source code in github:
  https://github.com/AIFDR/inasafe/tree/master/docs/source

  The RST files are used for two products:
  * HTML files generated using Sphinx (http://sphinx.pocoo.org) by running
    https://github.com/AIFDR/inasafe/blob/master/docs/Makefile. These
    files are accessible through both the file browser and the help button
    available in |project_name|
  * The web site http://readthedocs.org/docs/risk-in-a-box which automatically
    reads the RST files from github to update its content. The steps to achieve
    this are

  1. Register the project on the dashboard at ReadTheDocs
     (http://readthedocs.org/dashboard/risk-in-a-box/edit).
     In particular, this form points to the github repository where the RST
     files reside.
  2. Either manually build the project by clicking 'Build latest version' on
     http://readthedocs.org/dashboard/risk-in-a-box/ or by activating the
     service hook for ReadTheDocs at github:
     https://github.com/AIFDR/inasafe/admin/hooks


How do I replace a string across multiple files
:::::::::::::::::::::::::::::::::::::::::::::::

To replace string layer_type, say, with layertype across all python files
in project, do::

   find . -name "*.py" -print | xargs sed -i 's/layer_type/layertype/g'

Alternative you can install the 'rpl' command line tool::

   sudo apt-get install rpl

Using rpl is much simpler, just do::

   rpl "oldstring" "newstring" *.py


For details see
http://rushi.wordpress.com/2008/08/05/find-replace-across-multiple-files-in-linux/

