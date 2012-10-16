
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

Postprocessors and their settings can be edited in the user configurable function
parameters dialog.
To disable a postprocessor simply  change the "'on': True" to "'on': False".
the same is valid for any other setting they you might encounter there.
If you don't see a postprocessors field, it means that the impact function
you are trying to use does not support any post processor

.. figure:: ../_static/postprocessor-config.png
   :align:   center


Creating postprocessors
-------------------------

If you feel there is an important postprocessor which is missing, there are two
avenues you can follow:

* You can develop it yourself or with the aid of a programmer who has a good understanding
  of the python programming language.
* You can file a ticket on our `issue tracking system <https://github.com/AIFDR/inasafe/issues>`_, 
  and if time and resources allow we will implement it for you.

adding a new postprocessor is as simple as adding a new class with one mandatory
method, 2 optional ones and as many indicators as you need.

for implementation examples see AgePostprocessor which uses mandatory and
optional parameters


Data structure
-------------------------

E.g.

::

    {'Gender': [
        (QString(u'JAKARTA BARAT'), OrderedDict([(u'Total', {'value': 278349, 'metadata': {}}),
                                                 (u'Females count', {'value': 144741, 'metadata': {}}),
                                                 (u'Females weekly hygiene packs', {'value': 114881, 'metadata': {'description': 'Females hygiene packs for weekly use'}})])),
        (QString(u'JAKARTA UTARA'), OrderedDict([(u'Total', {'value': 344655, 'metadata': {}}),
                                                 (u'Females count', {'value': 179221, 'metadata': {}}),
                                                 (u'Females weekly hygiene packs', {'value': 142247, 'metadata': {'description': 'Females hygiene packs for weekly use'}})]))],
     'Age': [
        (QString(u'JAKARTA BARAT'), OrderedDict([(u'Total', {'value': 278349, 'metadata': {}}),
                                                 (u'Youth count', {'value': 73206, 'metadata': {}}),
                                                 (u'Adult count', {'value': 183432, 'metadata': {}}),
                                                 (u'Elderly count', {'value': 21990, 'metadata': {}})])),
        (QString(u'JAKARTA UTARA'), OrderedDict([(u'Total', {'value': 344655, 'metadata': {}}),
                                                 (u'Youth count', {'value': 90644, 'metadata': {}}),
                                                 (u'Adult count', {'value': 227128, 'metadata': {}}),
                                                 (u'Elderly count', {'value': 27228, 'metadata': {}})]))
        ]
    }
