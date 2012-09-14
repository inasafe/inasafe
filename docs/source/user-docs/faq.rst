Frequently Asked Questions
==========================



I found a bug, how should I report it?
--------------------------------------

We manage the project issues using a GitHub issue tracker. The
`InaSAFE <https://github.com/AIFDR/inasafe/issues?direction=desc&sort=created&state=open>`_
issue tracker is open to everyone, though you will first need to register a
(free) account on GitHub to use it. You can find the GitHub self-registration
page `here <https://github.com/signup/free>`_.

Why can't I find the plugin in the QGIS repositories?
-----------------------------------------------------

We do plan to publish the plugin at
`plugins.qgis.org <http://plugins.qgis.org/>`_ so that it can be effortlessly
installed from within QGIS, we are just no ready to do that yet. In the mean
time please use the manual installation procedure to install InaSAFE in QGIS.

Do I need to pay to use |project_name|?
---------------------------------------

No, the software is completely Free and Open Source.

What license is |project_name| published under?
-----------------------------------------------

|project_name| is published under the GPL version 2 license, the full text of
which is available at
`www.gnu.org/licenses/gpl-2.0.txt <http://www.gnu.org/licenses/gpl-2.0.txt>`_.


Under the terms of the license of you may freely copy, share and modify the
software, as long as you make it available under the same license.

How is the project funded?
--------------------------

The project is being developed 'for the good of humanity' and has been
jointly developed by `BNPB <http://www.bnpb.go.id/>`_,
`AusAid <http://www.ausaid.gov.au/>`_ &
`the World Bank <http://www.worldbank.org/>`_.

Could we request a new feature?
-------------------------------

If you have a feature request, please use the
`issue tracker <https://github.com/AIFDR/inasafe/issues?direction=desc&sort=created&state=open>`_
to let us know about it, using the same procedure as for bug reporting.


How do I rename a shape file and all the helper files?
::::::::::::::::::::::::::::::::::::::::::::::::::::::

Use the rename command. rename [ -v ] [ -n ] [ -f ] perlexpr [ files ].
For example::

    rename -v "s/^building/OSM_building_polygons_20110905/" building.*

How do I reproject a spatial data file to WGS84 geographic coordinates
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

For raster data, use gdalwarp, for example::

   gdalwarp -t_srs EPSG:4326 <source>.tif <target>.tif

For vector data use ogr2ogr. For example from TM-3 zone 48.2::

   ogr2ogr -s_srs EPSG:23834 -t_srs EPSG:4326 <target>.shp <source>.shp

How do I get Open Street Map building data into |project_name|?
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

For Indonesia, you can download latest collections at
`data.kompetisiosm.org <http://data.kompetisiosm.org>`_. or you can add our
Open Street Map building PostGIS mirror to InaSAFE:

 * Add PostGIS layer with host=203.77.224.77, database=osm,
   username=aifdr, port 5432, SSL mode=disable
 * Select view named vw_planet_osm_polygon

# * Build query: upper(geometrytype("way")) IN ('POLYGON','MULTIPOLYGON') AND BUILDING != ''

How do I take screen capture e.g. for use in a presentation?
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

On Ubuntu, get the packages gtk-recordmydesktop and mencoder
Record using recordmydesktop (start and stop icon in the top bar)
Convert to other formats using mencoder, e.g::

   mencoder -idx yogya_analysis-6.ogv -ovc lavc -oac lavc -lavcopts \
   vcodec=mpeg4:vpass=1 -of lavf -o yogya_analysis.avi

or::

   mencoder -idx yogya_analysis-6.ogv -ovc lavc -oac lavc -lavcopts \
   vcodec=wmv2 -of lavf -o yogya_analysis.wmv

