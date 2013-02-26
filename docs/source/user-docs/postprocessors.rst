
================
Post-processors
================

This document explains the purpose of post-processors and lists the
different available post-processors and the requirements each has to be
used effectively.

What is a post-processor?
-------------------------

A postprocessor is a function that takes the results from the impact function
and calculates derivative indicators, for example if you have an affected
population total, the **Gender** post-processor will calculate gender specific
indicators such as additional nutritional requirements for pregnant women

Selecting a post-processor
--------------------------

Post-processors and their settings can be edited in the user configurable
function parameters dialog. To disable a post-processor simply change the
:guilabel:`Postprocessors` :samp:`"'on': True" to "'on': False"`.
The same is valid for any other setting you might encounter there.
If you don't see a post-processors field, it means that the impact function
you are trying to use does not support any post processor

.. figure:: ../static/postprocessor-config.png
   :align:   center

Each activated post-processor will create an additional report in the dock and
in the printout. If problems arise while post processing, the system will
inform you and will skip post-processing.

Creating post-processors
------------------------

If you feel there is an important post-processor which is missing, there are two
avenues you can follow:

* You can develop it yourself or with the aid of a programmer who has a good
  understanding of the python programming language.
* You can file a ticket on our `issue tracking system
  <https://github.com/AIFDR/inasafe/issues>`_, and if time and resources allow
  we will implement it for you.
