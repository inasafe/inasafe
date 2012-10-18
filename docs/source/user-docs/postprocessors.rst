
================
Postprocessors
================

This document explains the purpose of postprocessors and lists the 
different available postprocessor and the requirements each has to be 
used effectively.

.. note:: This document is still a work in progress.


What is a postprocessor?
---------------------------

A postprocessor is a function that takes the results from the impact function
and calculates derivative indicators, for example if you have an affected
population total, the Gender postprocessor will calculate gender specific
indicators such as additional nutritional requirements for pregnant women

Selecting a postprocessor
----------------------------

Postprocessors and their settings can be edited in the user configurable
function parameters dialog.
To disable a postprocessor simply  change the "'on': True" to "'on': False".
The same is valid for any other setting you might encounter there.
If you don't see a postprocessors field, it means that the impact function
you are trying to use does not support any post processor

.. figure:: ../_static/postprocessor-config.png
   :align:   center

Each activated postprocessor will create an additional report in the dock and in
the printout. If problems arise while post processing, the system will gracefully
inform you and will skip postprocessing.

Creating postprocessors
-------------------------

If you feel there is an important postprocessor which is missing, there are two
avenues you can follow:

* You can develop it yourself or with the aid of a programmer who has a good understanding
  of the python programming language.
* You can file a ticket on our `issue tracking system <https://github.com/AIFDR/inasafe/issues>`_, 
  and if time and resources allow we will implement it for you.
