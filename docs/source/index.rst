.. InaSAFE documentation master file, created by
   sphinx-quickstart on Tue Jan 10 12:22:06 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

|project_name| Documentation
============================

**INDONESIA SCENARIO ASSESSMENT FOR EMERGENCIES** (InaSAFE) is free software
that produces realistic natural hazard impact scenarios for better planning,
preparedness and response activities.

Concept
-------

To effectively prepare for future floods, earthquakes or tsunami you must first
understand the likely impacts that need to be managed. For example, to prepare
contingency plans for a severe flood in Jakarta, emergency managers need to
answer questions like:
  
* what are the areas likely to be affected;
* how many people will need to be evacuated and sheltered;
* which schools will be closed;
* which hospitals can still take patients; and
* what roads will be closed?

How does it work?
-----------------

InaSAFE provides a simple but rigorous way to combine data from scientists,
local governments and communities to provide insights into the likely impacts
of future disaster events. The software is focused on examining, in detail,
the impacts by a single hazard would have on specific sectors. e.g. location of
primary schools and estimated number of students affected by a possible tsunami
in Maumere (when it happened during the school hours).

Who can use it?
---------------

Anyone with basic computer skills can quickly learn to use InaSAFE to explore
the potential impacts of a disaster event and to produce maps and reports of
these impacts. The software leads a user through the process of asking a
specific question and has tools to estimate the likely damage that a hazard
will cause to people and critical infrastructure such as schools, hospitals,
roads, etc.

   Because the software is free and open, more advanced users can also add new
   questions and data from new sectors

Where does the data come from?
------------------------------

Effectively preparing for a disaster requires people from a wide range of
sectors and backgrounds to effectively work together and share their
experience, expertise, and resources. Using InaSAFE to develop a scenario
requires the same spirit of cooperation and sharing of expertise
and data.

InaSAFE is designed to use and combine existing data from science agencies,
local governments, and communities themselves. Normally, information on the
location of people and important assets are provided by local communities and
government departments responsible for each sector, often through a facilitated
part of a disaster preparedness and planning exercise.

Where appropriate spatial data doesn’t yet exist, external tools such as
OpenStreetMap (www.LearnOSM.org) can allow governments and communities to
quickly and easily map their assets that are important to them.

.. note:: It is important to note that InaSAFE is not a hazard modeling tool.
   Information on hazards needs to be provided either by technical experts,
   often from Government agencies, universities or technical consultants, or
   from communities themselves based on their previous experiences.
   
The more communities, scientists and governments share data and knowledge, the
more realistic and useful the InaSAFE scenario will be.

InaSAFE was conceived and initially developed by the Indonesia’s National
Disaster Management Agency (BNPB), the Australian Agency for International
Development (AusAID) and the World Bank.

You can find out more about the |project_name| project by visiting
`www.inasafe.org <http://www.inasafe.org/>`_.


.. figure::  ../screenshot.jpg
   :align:   center

A completed assement using the QGIS InaSAFE plugin, with an example of
the print ready pdf output the plugin produces.

.. figure::  ../screenshot2.jpg
   :align:   center

Vulnerable building footprints shown in red.

Open Source
-----------

The latest source code is available at
`https://github.com/AIFDR/inasafe <https://github.com/AIFDR/inasafe>`_ 
(must open in new window using right click) which contains modules for risk
calculations, gis functionality and functions for impact modelling.

Contact Details
---------------

Australia-Indonesia Facility for Disaster Reduction (AIFDR)
Menara Thamrin Suite 1505 | Jl. MH Thamrin Kav. 3, Jakarta 10250, Indonesia
Ph: +62 21 398 30088 | Fax: +62 21 398 30068 | www.aifdr.org


Contents
========

.. toctree::
   :maxdepth: 2

   user-docs/index
   developer-docs/index
   api-docs/index
   authors


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

