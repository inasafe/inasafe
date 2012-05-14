
Frequently Asked Questions
==========================


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


How does the documentation work?
::::::::::::::::::::::::::::::::

The |project_name| documentation files are written using the RST format
(`quickreference guide <http://docutils.sourceforge.net/docs/user/rst/quickref.html>`_)
and stored with the source code in github::

   https://github.com/AIFDR/inasafe/tree/master/docs/source

The RST files are used for two products:
  * HTML files generated using Sphinx (http://sphinx.pocoo.org) by running
    https://github.com/AIFDR/inasafe/blob/master/docs/Makefile. These
    files are accessible through both the file browser and the help button
    available in |project_name|
  * The web site http://readthedocs.org/docs/inasafe which automatically
    reads the RST files from github to update its content. The steps to achieve
    this are

  1. Register the project on the dashboard at ReadTheDocs
     (http://readthedocs.org/dashboard/inasafe/edit).
     In particular, this form points to the github repository where the RST
     files reside.
  2. Either manually build the project by clicking 'Build latest version' on
     http://readthedocs.org/dashboard/inasafe/ or by activating the
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


For details on the find command see `this article <http://rushi.wordpress.com/2008/08/05/find-replace-across-multiple-files-in-linux/>`_.

.. _faq-revision-label:

How did you embed the git version SHA1 into each .py file?
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

The format was derived using the `git log format tag <http://schacon.github.com/git/git-log.html>`_.
It is stored in the source of each python as::
   
   __revision__ = '$Format:%H$'

'%H' being the format tag for the SHA1. The __revision__ is **not** updated
with each commit. Rather is is registered with git for replacement when using
git-archive by doing this::
   
   echo "*.py export-subst" > .gitattributes
   git add .gitattributes

The above only needs to be done once and then all python files with format
substitutions will be replaced when running git-archive. The actual substition
takes place at the time that a git archive is generated (git archive creates a
copy of the repo with all repository metadata stripped out). For example::
  
  git archive version-0_3 | tar -x -C /tmp/inasafe-0.3.0

You can verify SHA1 replacement has been made by doing::
   
   cat /tmp/inasafe/gui/is_plugin.py | grep revision
   __revision__ = 'a515345e43b25d065e1ae0d73687c13531ea4c9c'

The deployment of version tagged files is automated by using the 
:file:`scripts\release.sh` script.
   
