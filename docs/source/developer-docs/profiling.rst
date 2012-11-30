.. _profiling:

Profiling
---------

Profiling a script in python is as easy as calling:
python -m cProfile myscript.py
see also: http://docs.python.org/2/library/profile.html#module-cProfile

the problem is that sometimes the code you want to profile deep in ianSAFE. You
can still get nice cProfiles by replacing the original call with a call to
cProfile.runctx()

so::

    self.preparePolygonLayerForAggr(theClippedHazardFilename, myHazardLayer)
would become::

    cProfile.runctx('self.preparePolygonLayerForAggr(theClippedHazardFilename, myHazardLayer)', globals(), locals())
see also http://stackoverflow.com/questions/1031657/profiling-self-and-arguments-in-python

You can put a raise statement right after the runctx call so the execution is
stopped and you can see your cProfile results in the console

