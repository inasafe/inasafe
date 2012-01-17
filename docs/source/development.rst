Risk-in-a-box Developer Documentation
=====================================

   api-docs
   todo

To use Risk-in-a-Box with QGIS
------------------------------

* python-numpy
* python-gdal


To develop Risk-in-a-Box
------------------------

* git
* subversion
* pep8
* nosetests (with coverage plugin)
* ...

On an ubuntu system you can install these requirements using apt::

  sudo apt-get install git subversion pep8 python-nose python-coverage

Whilst under development, you will need to install scipy into your python 
installation too (we are working to remove this if possible)::

  sudo apt-get install python-scipy


Quick Installation Guide - Developers
-------------------------------------

To develop on the plugin, you first need to copy it to your local system. If you are a developer,
the simplest way to do that is to clone it from our GitHub repository page like this::

  git clone git://github.com/AIFDR/risk_in_a_box.git  (for read only)
  git clone git@github.com:AIFDR/risk_in_a_box.git    (to commit changes)

Place the local repository under `~/.qgis/python/plugins` and then restart QGIS. If you wish to
an IDE for development, please refer to `this article <http://linfiniti.com/2011/12/remote-debugging-qgis-python-plugins-with-pydev/>`_
for detailed information on how you can do so.

If you wish to debug the plugin, (referring once again to the above article), make a copy
of pydevpath.txt.templ to pydevpath.txt e.g.::

  cp pydevpath.txt.templ pydevpath.txt

Then replace the path to your pydevd module as described in the above article.


.. note::

   If you are running with remote debugging enabled, be sure to start the
   PyDev debug server first before launching the Risk-in-a-box QGIS plugin
   otherwise QGIS will likely crash when it can't find the debug server.


If you wish to run the unit tests, please make a local copy of the qgispath.txt.templ template
and adjust the path contained in that file to match your QGIS installation path e.g.::

  cp qgispath.txt.templ qgispath.txt

In order to run the tests, you should install 'discover' e.g.::

  sudo pip install discover

Then you can run the tests (from within the risk_in_a_box toplevel directory) like this::

  python -m discover


