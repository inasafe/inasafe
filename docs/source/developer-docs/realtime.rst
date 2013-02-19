InaSAFE Realtime
================

InaSAFE Realtime is a component of the InaSAFE project designed for deployment
on a server and creation of Impact Maps a short interval after an event occurs.

Currently the realtime system supports Earthquake fatality impact assessments,
though in future we envisage additional support for other disaster types being
facilitated.

.. note:: This work was funded by the Australia-Indonesia Facility for Disaster
          Reduction, Geoscience Australia and the GFDRR. We thank you for your
          support.

Historical Note
---------------

The original prototype of the realtime system was implemented by Ole Nielsen
(AusAID). The subsequent port of the realtime system to InaSAFE was implemented
by Tim Sutton (Linfiniti Consulting CC., funded by The World Bank and the
AIFDR).


Supported Platforms
-------------------

Currently only Ubuntu 12.04 is supported. The software may work or can easily
be made to work on other platforms but it is untested.

Generated Products
------------------

For every shake event, the tool produces a number of GIS products:

* A raster layer interpolated from the original MMI point matrix and symbolized
    according to the MMI scale colours.
* A vector (shapefile) layer generated from the original MMI point matrix and
    symbolized according to the MMI scale colours.
* A vector (shapefile) layer depicting MMI isolines and symbolized according to
    the MMI scale colours.
* A cities layer (shapefile) which lists the affected cities along with key
    data such as distance from and direction to epicenter, number of people resident in the city, mmi exposure etc.

In addition to the above mentioned GIS products, the following 3 files are
created for each event:

* A PNG file containing a single page report as illustrated above.
* A large PNG image which contains exactly the same content as the pdf but in
    an image format.
* A thumbnail PNG image which contains a reduced size image of the report.

Architecture
------------

InaSAFE Realtime is implemented by four main python modules:

* **ftp_client** - A generic tool to fetch directory listings and
    files from a remote server.
* **shake_data** - A mostly generic tool to fetch shake files from
    an ftp server. There is an expectation that the server layout
    follows a simple flat structure where files are named
    after the shake event and are in the format of shake data as
    provided by the USGS (XXXXXX TODO fact check XXXX).
    :samp:`ftp://118.97.83.243/20110413170148.inp.zip`
    **Note:** This data is now no longer hosted via ftp and requires an ssh
    account in order to retrieve it.
* **shake_event** - A rather monolithic module that 'knows' how to
    fetch, unpack, process and generate a report for a quake event.
    The module logic is based on the standard shake data packaging
    format supplied by the USGS. We have restricted out implementation
    to require only the :file:`grid.xml` file contained in the inp.zip
    file in the downloaded zip file.
* **make_map** - A simple python tool for running one or multiple shake
    analyses.

InaSAFE has strong dependencies on QGIS (http://qgis.org) which is
used for much of the data processing and reporting functionality.

.. note:: Currently version 779e16603ee3fb8781c85a0e95913a1f6bbd2d6a is
    the 'known good' SHA1.

Two of these dependencies is a template QGIS project and a map
composition template. We have designed the realtime reporting engine
to allow end users to customise the map report to their needs with little
or no programming. The primary way to achieve this is by opening the custom
template :file:`realtime/fixtures/realtime-template.qpt` in QGIS and modifying
its contents. You could also build a new template from scratch provided the
item IDs listed in the section that follows are used.

Installation
------------

The supported platform is currently Ubuntu 12.04 LTS. The instructions provided
below are for that OS. First we are going to hand build QGIS. This may not be
needed in future once 2.0 packages are available, but for now it is
recommended.::

  sudo apt-get install python-software-properties
  sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
  sudo apt-get update
  sudo apt-get build-dep qgis
  cd ~
  mkdir -p dev/cpp
  sudo mkdir /home/web
  sudo chown <youruser>.<youruser> /home/web
  cd ~/dev/cpp
  sudo apt-get install git cmake-curses-gui
  git clone git://github.com/qgis/Quantum-GIS.git

At this point you should enter ‘yes’ when prompted::

  cd Quantum-GIS
  mkdir build
  cd build
  cmake .. -DCMAKE_INSTALL_PREFIX=/usr/local/qgis-realtime \
  -DCMAKE_BUILD_TYPE=Debug
  make -j4
  sudo mkdir /usr/local/qgis-realtime
  sudo chown <youruser>.<youruser> /usr/local/qgis-realtime
  make install

At this point you can test if your hand build QGIS is working by doing::

  export LD_LIBRARY_PATH=/usr/local/qgis-realtime/lib
  export QGIS_PREFIX_PATH=/usr/local/qgis-realtime
  export PYTHONPATH=/usr/local/qgis-realtime/share/qgis/python
  python
  from qgis.core import *
  ctrl-d

You should see something like the listing below::

  timlinux@waterfall:~/dev/python/inasafe-realtime$ python
  Python 2.7.3 (default, Sep 26 2012, 21:51:14)
  [GCC 4.7.2] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  >>> from qgis.core import *
  >>>

Get InaSAFE ::

  cd ~
  mkdir -p dev/python
  cd dev/python
  git clone git://github.com/AIFDR/inasafe.git inasafe-realtime
  cd inasafe-realtime
  sudo apt-get install python-tz paramikio

Setup Apache::

  sudo apt-get install apache2-mpm-worker
  cd /etc/apache2/sites-available
  sudo cp ~/dev/python/inasafe-realtime/realtime/fixtures/web/quake-apache.conf .
  sudo apt-get install rpl
  sudo chown <yourname>.<yourname> quake-apache.conf
  rpl “quake.linfiniti.com” “quake.<yourhost>” quake-apache.conf

For local testing only you can use quake.localhost for your host then add this to your /etc/hosts::

  127.0.0.1 localhost quake.localhost

Now deploy your site:

  sudo a2dissite default
  sudo a2enssite quake.apache.conf
  cd /home
  chmod a+X web
  mkdir web/quake
  chmod a+X web/quake
  cd /home/web/quake

Just for testing do::

  mkdir public
  echo 'Hello' > public/foo.txt
  sudo service apache2 restart

Open your web browser and point it to : http://quake.localhost

You should see a basic directory listing containing file foo.

Now copy over some required datasets::

  cd ~/dev/python/inasafe-realtime/realtime/fixtures/
  wget http://quake.linfiniti.com/indonesia.sqlite

  mkdir ~/dev/python/inasafe-realtime/realtime/fixtures/exposure
  cd ~/dev/python/inasafe-realtime/realtime/fixtures/exposure
  wget http://quake.linfiniti.com/population.tif
  wget http://quake.linfiniti.com/population.keywords

  cd /home/web/quake/public
  wget http://quake.linfiniti.com/web.tar.gz
  tar xfz web.tar.gz
  rm web.tar.gz


Running your first report::

  cd ~/dev/python/inasafe-realtime
  scripts/make-latest-shakemap.sh

Running all back reports::

  cd ~/dev/python/inasafe-realtime
  scripts/make-all-shakemaps.sh

Listing shake files on ftp server::

  cd ~/dev/python/inasafe-realtime
  scripts/make-list-shakes.sh


Cron Jobs::

There are two cron jobs - one to run the latest shake event regularly, and one
to synchronise all the shake outputs::

  crontab -e

Now add these lines (replacing <yourname>)::

  * * * * * /home/<yourname>/dev/python/inasafe-realtime/realtime/fixtures/web/make-public.sh
  * * * * * /home/<yourname>/bin/realtime.sh


Finally make a small script to run the analysis every minute::

  cd ~
  mkdir bin
  cd bin
  touch realtime.sh
  chmod +x realtime.sh

Now edit the file and set its content to this::

  #!/bin/bash
  cd /home/<yourname>/dev/python/inasafe-realtime
  scripts/make-latest-shakemap.sh



You also need to have the standard datasets needed for the cartography:

* population
* indonesia.sqlite (can be changed by adjusting the QGIS project).

QGIS Map Template Elements
--------------------------

This section describes the various elements that comprise the standard map
template, and which you can modify directly in the template. These fall into
three groups:

* **Static elements**.
* **Elements containing tokens for replacement**.
* **Elements that are directly updated by the renderer**.

Static Elements
................

These are e.g. logos which are not touched by the realtime map renderer at all.
You can remove or replace them with your own elements as needed.

* **logo-left** - the logo element at the top left corner of the map layout.
* **right-logo** - the logo element at the top right corner of the map layout.
* **overview-map** - a map overview showing the locality of the event. This
    is the overview frame for map-0 (the main map in the layout). It is
    locked and limited to show the population layer only.
* **legend** - a map legend, by default configured to show only the layer for
    the population layer. It is locked and limited to the population layer.

Elements containing tokens for replacement
..........................................

In this case the element name is not significant, only the token(s) it
contains. At render time any of the tokens in these elements will be replaced
with translated (if an alternative locale is in effect) content from the
map renderer according to the keywords listed below in this document.

* **main-title** - the main title at the top of the page. By default this
    element contains the keyword:
    :samp:`[map-name]`.
* **intensity-date** - the date and intensity of the event. By default this
    label contains the following replacement tokens:
    :samp:`M[mmi] [date] [time]`
* **position-depth** - the position (lon, lat) and depth of the event. By
    default this label contains the following replacement tokens:
    :samp:`[longitude-name] [longitude-value] [latitude-name] [latitude-value] [depth-name] [depth-value] [depth-unit]`
* **location-description** - the postion of the event described relative to
    the nearest major populated place. By default this label contains the
    following replacement tokens:
    :samp:`[located-label] [distance] [distance-unit], [bearing-degrees] [bearing-compass] [direction-relation] [place-name]`
* **elapsed-time** - the time elapsed between the event and when this report
    was generated. By default this label contains the following replacement
    tokens:
    :samp:`[elapsed-time-label] [elapsed-time]`
* **scalebar** - the scalebar which reflects the scale of the main map.
    This is **Currently disabled**.
* **disclaimer** - A block of text for displaying caveats, cautionary notes,
    interpretive information and so on. This contains the following replacement
    tokens: :samp:`[limitations]`.
* **credits** - A block of text for displaying credits on the map output.
    This contains the following replacement tokens: :samp:`[credits]`.

Elements that are directly updated by the renderer
..................................................

In this case any content that may be present in the element is completely
replaced by the realtime map renderer, although certain styling options
(e.g. graticule settings on the map) will remain in effect.

* **impacts-table** - a table generated by ShakeEvent which will list the
    number of modelled affected people in each of the MMI bands. This is an
    HTML element and output will fail if it is not present.
* **main-map** - primary map used to display the event and neighbouring towns.
    Developers can set a minimum number of neighbouring towns to display using
    the ShakeEvent api. This is a map element and output will fail if it is
    not present. This is an HTML element and output will fail if it is not
    present.
* **affected-cities** - a table generated by ShakeEvent which will list the
    closes N cities (configurable using the ShakeEvent api) listed in order of
    shake intensity then number of people likely to be affected.


Replaceable Keywords
---------------------

This section describes tokenised keywords that are passed to the map template.
To insert any of these keywords into the map template, simply enclose the
key in [] (e.g. [place-name]) and it will be replaced by the text value (e.g.
Tondano). The list includes static phrases which have been internationalised
(and so will display in the language of the selected map local, defaulting to
English where no translation if available. In cases where static definitions
are used (e.g. [credits]) you can substitute your own definitions by creating
your own template. More on that below in the next section.

* **map-name**: Estimated Earthquake Impact
* **exposure-table-name**: Estimated number of people exposed to each MMI level
* **city-table-name**: Places Affected
* **legend-name**: Population density
* **limitations**: This impact estimation is automatically generated and only takes
  into account the population and cities affected by different
  levels of ground shaking. The estimate is based on ground
  shaking data from BMKG, population density data from asiapop
  .org, place information from geonames.org and software developed
  by BNPB. Limitations in the estimates of ground shaking,
  population  data and place names datasets may result in
  significant misrepresentation of the on-the-ground situation in
  the figures shown here. Consequently decisions should not be
  made solely on the information presented here and should always
  be verified by ground truthing and other reliable information
  sources.
* **credits**: Supported by the Australia-Indonesia Facility for Disaster
  Reduction and Geoscience Australia.
* **place-name**: Tondano
* **depth-name**: Depth
* **location-info**: M 5.0 26-7-2012 2:15:35 Latitude: 12 '36.00"S Longitude:
  124'27'0.00"E Depth: 11.0km Located 2.50km SSW of Tondano
* **depth-unit**: km
* **bearing-compass**: SSW
* **distance-unit**: km
* **mmi**: 5.0
* **longitude-name**: Longitude
* **date**: 26-7-2012
* **time**: 2:15:35
* **formatted-date-time: 26-Jul-12 02:15:35
* **located-label**: Located
* **bearing-degrees**: -163.055923462
* **distance**: 2.50
* **direction-relation**: of
* **latitude-name**: Latitude
* **latitude-value**: 12'36.00"S
* **longitude-value**: 12'4'27.00
* **depth-value**: 11.0
* **version**: Version: 1.0.1
* **bearing-text**: bearing
* **elapsed-time-name**: Elapsed time
* **elapsed-time**: 26-Jul-12 02:15:35
* **fatalities-name**: Estimated Fatalities
* **fatalities-range**: 5 - 55
* **fatalities-count**: 55


Customising the template
------------------------

You have a few options to customise the template - we have gone to great
lengths to ensure that you can flexibly adjust the report composition
**without doing any programming**. There are three primary ways you can achieve
this:

* Moving replacement tags into different elements, or removing them completely.
* Moving the template elements themselves around or adding / removing them
    completely.
* Creating your own template from scratch and pointing the realtime tool to
    your preferred template.


The template is provided as :file:`realtime/fixtures/realtime-template.qpt`
and can be modified by opening the template using the QGIS map composer,
making your changes and then overwriting the template. You should take care
to test your template changes before deploying them to a live server, and
after deploying them to a live server.

If you wish to use your own custom template, you need to specify the
:samp:`INSAFE_REALTIME_TEMPLATE` environment variable, populating it with
the path to your preferred template file.

QGIS Realtime Project
---------------------

The cartography provided in the realtime maps is loaded from the
:file:`realtime/fixtures/realtime.qgs` QGIS project file. You can open this
file using QGIS, change the layers and their symbology, and your changes
will be reflected in the generated realtime shake report.

There are however some caveats to this:

* The overview map has locked layers
* The main map should always have a population layer with grayscale legend
  matching that provided in the original. If you do remove / change the
  population layer you should also remove / change the population layer legend.

If you wish to use your own custom project, you need to specify the
:samp:`INSAFE_REALTIME_PROJECT` environment variable, populating it with
the path to your preferred project file.

Configuration of population data
--------------------------------

Population data is used as the 'exposure' dataset for shake reports.
The following priority will be used to determine the path of the population
raster dataset.
# the class attribute **self.populationRasterPath**
    will be checked and if not None it will be used.
# the environment variable :samp:`INASAFE_POPULATION_PATH` will be
   checked if set it will be used.
# A hard coded path of
   :file:`/fixtures/exposure/population.tif` will be checked.
# A hard coded path of
   :file:`/usr/local/share/inasafe/exposure/population.tif` will be used.


Running a shake event
---------------------

To run a single event locally on a system with an X-Server you can
use the provided script :file:`scripts/make-shakemap.sh`. The script can be
used with the following options:

* **--list**: :samp:`scripts/make-shakemap.sh --list` - retrieve a list of
    all known shake events on the server. Events are listed as their full
    ftp url e.g. :file:`ftp://118.97.83.243/20121106084105.out.zip` and
    both *inp* and *out* files are listed.
* **[event id]**: :samp:`scripts/make-shakemap.sh 20121106084105` - retrieve
    and process a single shake event. A pdf, png and thumbnail will be produced.
* **--all**: :samp:`scripts/make-shakemap.sh --all` - process all identified
    events on the server in batch mode. **Note:** this is experimental and
    not production ready - we recommend to use the approach described in
    :ref:`realtime-batch`.
* **no parameters**: :samp:`scripts/make-shakemap.sh` - fetch and process
    the latest existing shake dataset. This is typically what you would want
    to use as the target of a cron job.

.. note:: The :file:`make_shakemap.sh` script is just a thin wrapper around
    the python :mod:`realtime.make_map` python module.

.. note:: An english local shakemap will always be generated regardless of
    the locale you have chosen (using the INASAFE_LOCALE env var). This en
    version will be in addition to your chosen locale.

Unit tests
-----------

A complete set of unit tests is provided with the realtime package for InaSAFE.
You can execute these tests like this::

    nosetests -v --with-id --with-xcoverage --with-xunit --verbose \
        --cover-package=realtime realtime

There are also a number of Jenkins tasks provided in the Makefile for InaSAFE
to automate testing on our continuous integration server. You can view the
current state of these tests by visiting this URL:

http://jenkins.linfiniti.com/job/InaSAFE-Realtime/

.. _realtime-batch:

Batch validation & running
---------------------------


The :file:`scripts/make-all-shakemaps.sh` provided in the InaSAFE source tree
will automate the production of one shakemap report per event found on the
shake ftp server. It contains a number of environment variable settings which
can be used to control batch execution. First a complete script listing::

    #!/bin/bash

    export QGIS_DEBUG=0
    export QGIS_LOG_FILE=/tmp/inasafe/realtime/logs/qgis.log
    export QGIS_DEBUG_FILE=/tmp/inasafe/realtime/logs/qgis-debug.log
    export QGIS_PREFIX_PATH=/usr/local/qgis-realtime/
    export PYTHONPATH=/usr/local/qgis-realtime/share/qgis/python/:`pwd`
    export LD_LIBRARY_PATH=/usr/local/qgis-realtime/lib
    export INASAFE_WORK_DIR=/home/web/quake
    export SAFE_POPULATION_PATH=/var/lib/jenkins/jobs/InaSAFE-Realtime/exposure/population.tif
    for FILE in `xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/make_map.py --list | grep -v inp | grep -v Proces`
    do
        FILE=`echo $FILE | sed 's/ftp:\/\/118.97.83.243\///g'`
        FILE=`echo $FILE | sed 's/.out.zip//g'`
        echo "Running: $FILE"
        xvfb-run -a --server-args="-screen 0, 1024x768x24" python realtime/make_map.py $FILE
    done
    exit

An example of the output produced from such a batch run is provided at:

http://quake.linfiniti.com/



Hosting the shakemaps
---------------------

In this section we describe how to easily host the shakemaps on a public web
site.

An apache configuration file and a set of resources are provided to make it easy
to host the shakemap outputs. The resources provided can easily be modified to
provide a pleasing, user friendly directory listing of shakemap reports.

.. note:: You should adapt the paths used below to match the configuration of
    your system.

First create a file (as root / sudo) with this content in your
:file:`/etc/apache2/sites-available/quake-apache.conf.` for example::

    <VirtualHost *:80>
      ServerAdmin tim@linfiniti.com
      ServerName quake.linfiniti.com

      DocumentRoot /home/web/quake/public/
      <Directory /home/web/quake/public/>
        Options Indexes FollowSymLinks
        IndexOptions +FancyIndexing
        IndexOptions +FoldersFirst
        IndexOptions +XHTML
        IndexOptions +HTMLTable
        IndexOptions +SuppressRules
        HeaderName resource/header.html
        ReadmeName resource/footer.html
        IndexStyleSheet "resource/bootstrap.css"
        IndexIgnore .htaccess /resource
        AllowOverride None
        Order allow,deny
        allow from all
      </Directory>

      ErrorLog /var/log/apache2/quake.linfiniti.error.log
      CustomLog /var/log/apache2/quake.linfiniti.access.log combined
      ServerSignature Off

    </VirtualHost>

Now make the :file:`/home/web/quake/public` directory in which the outputs will
be hosted::

    mkdir -p /home/web/quake/public

Unpack the :file:`realtime/fixtures/web/resource` directory into the
above mentioned public directory. For example::

    cd /home/web/quake/public
    cp -r ~/dev/python/inasafe/realtime/fixtures/web/resource .

Next ensure that apache has read access to your hosting directory::

    chmod +X /home/web/quake/public
    chmod +X /home/web/quake/public/resource

You can customise the look and feel of the hosted site by editing the files in
:file:`/home/web/quake/public/resource` (assumes basic knowledge of HTML).

Lastly, you should regularly run a script to move generated pdf and png
outputs into the public directory. An example of such a script is provided as
:file:`realtime/fixtures/web/make-public.sh`. To run this script regularly, you
could add it to a cron job e.g.::

    crontab -e

And then add a line like this to the cron file::

    * * * * * /home/timlinux/dev/python/inasafe-realtime/realtime/fixtures/web/make-public.sh

.. note:: The resources used in the above examples are all available in the
    source code under :file:`realtime/fixtures/web`.









http://paradox460.newsvine.com/_news/2008/04/05/1413490-how2-stylish-apache-directory-listings
