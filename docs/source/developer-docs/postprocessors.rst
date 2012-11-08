
==============
Postprocessors
==============

This document explains the purpose of postprocessors and lists the 
different available postprocessor and the requirements each has to be 
used effectively.

.. note:: This document is still a work in progress.


What is a postprocessor?
------------------------

A postprocessor is a function that takes the results from the impact function
and calculates derivative indicators, for example if you have an affected
population total, the Gender postprocessor will calculate gender specific
indicators such as additional nutritional requirements for pregnant women


Creating postprocessors
-----------------------

Adding a new postprocessor is as simple as adding a new class called
XxxxxxPostprocessor that inherits AbstractPostprocessor with one mandatory
method (process), 2 optional ones and as many indicators as you need.

the minimal class could look like this:
::

    class MySuperPostprocessor(AbstractPostprocessor):
        def __init__(self):
            AbstractPostprocessor.__init__(self)

        def setup(self, params):
            AbstractPostprocessor.setup(self, None)

        def process(self):
            AbstractPostprocessor.process(self)

        def clear(self):
            AbstractPostprocessor.clear(self)

        def _calculate_my_indicator(self):
            x = 5
            A = 0.5
            myResult = 10 * x / A
            self._append_result('My Indicator', myResult)

After that you need to import the new class into postprocessor_factory and
update AVAILABLE_POSTPTOCESSORS to include the postprocessor prefix (e.g.
MySuper if the class is called MySuperPostprocessor)

As last step you have to update or add the *parameters* variable to the impact
functions that you want to use the new postprocessor. This will need to include
a dicionary of the available postprocessors as shown below.
::

    parameters = {
            'thresholds': [0.3, 0.5, 1.0],
            'postprocessors':
                {'Gender': {'on': True},
                 'Age': {'on': True,
                         'params': {
                            'youth_ratio': defaults['YOUTH_RATIO'],
                            'adult_ratio': defaults['ADULT_RATIO'],
                            'elder_ratio': defaults['ELDER_RATIO']
                            }
                        },
                  'MySuper': {'on': True}
                 }
            }

or as a minimum:
::

    parameters = {'postprocessors':{'MySuper': {'on': True}}}

for implementation examples see AgePostprocessor and GenderPostprocessor which
both use mandatory and optional parameters

Output
------
Dock.postprocOutput will hold the result datastructure (shown below) of all the
postprocessors. The structure is then parsed by Dock.getPostprocOutput() and
stored in the impact layer's keywords

Data structure of results
.........................
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
