
================
Impact Functions
================

This document explains the purpose of impact functions and lists the 
different available impact function and the requirements each has to be 
used effectively.

.. note:: This document is still a work in progress.


What is an impact function?
---------------------------

In impact function is a software programme that computes a risk assessment
given a number of inputs. The risk assessment will typically have a spatial
component (e.g. a GIS layer which can be incorporated into a map) and a 
non-spatial component (e.g. a list of actions you may want to consider carrying out, 
or a list of estimates of disaster risk reduction elements such as how many 
bags of rice to make available).

Selecting an impact function
----------------------------

Impact functions are bundled with the InaSAFE software. The graphical user interface
(provided as a plugin for QGIS will offer a list of impact functions that can be 
used based on the layers you have loaded and their :doc:`keywords <keywords>`.

Exploring impact functions
--------------------------

You can use the impact function table to explore all of the possible impact functions
that can be used. They are listed in a table with a series of pick-lists (combo boxes)
above which can be used to filter the functions based on different criteria as
illustrated below.

.. figure:: ../static/impact_function_table_unfiltered.png
   :align:   center

When applying a filter set, the list of available functions that meet those criteria is
updated as shown below.

.. figure:: ../static/impact_function_table_filtered.png
   :align:   center

The impact function table is simply a browser to help you to familiarise yourself with
the functions available. For the actual usage of the functions you need to have
layers available (i.e. loaded in QGIS) with the appropriate keywords for your target function.


Creating impact functions
-------------------------

If you feel there is an important impact function which is missing, there are two
avenues you can follow:

* You can develop it yourself or with the aid of a programmer who has a good understanding
  of the python programming language.
* You can file a ticket on our `issue tracking system <https://github.com/AIFDR/inasafe/issues>`_, 
  and if time and resources allow we will implement it for you.

