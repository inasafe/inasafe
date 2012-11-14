
InaSAFE Realtime
================

InaSAFE Realtime is a component of the InaSAFE project designed for deployment
on a server and creation of Impact Maps a short interval after an event occurs.

The original prototype of the realtime system was implemented by Ole Nielsen
(AusAID). The subsequent port of the realtime system to InaSAFE was implemented
by Tim Sutton (Linfiniti Consulting CC., funded by The World Bank and the
AIFDR).

Currently the realtime system supports Earthquake fatality impact assessments,
though in future we invisage additional support for other disaster types being
facilited.

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

.. note:: Currently version e15f4a8383f425284622ce31a28098849f11a6fe is
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

To run the realtime component of InaSAFE, you need to have QGIS 2.0 and
the QGIS 2.0 python bindings installed. In addition the :samp:`pytz` module
is needed::

    sudo apt-get install python-tz

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

Additional configuration options
--------------------------------



Running a shake event
---------------------

Unit tests
-----------


Batch validation
----------------

http://quake.linfiniti.com/

Hosting the shakemaps
---------------------

