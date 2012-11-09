
Development under Gnu/Linux
===========================

Risk-in-a-box is built in python and runs as a plugin in `QGIS
<http://qgis.org>`_.


Quick Installation Guide - Linux (Debian based)
-----------------------------------------------

These instructions are for setting up a development version on a Debian based
linux system such as Ubuntu or Mint.

1. Goto the area where you do development, e.g cd ~/sandbox
2. wget bit.ly/inasafe-install
3. source ./inasafe-install

To verify that the installation works you can run the test suite from the
command line::

   cd inasafe-dev
   make test

This will run all the regression tests and also highlight any code issues.
Note that first time the tests are run they will pull 250MB of test data from
our git repository. See further notes on running tests below.

To run the plugin start QGIS and enable it from the
:menuselection:`Plugins --> Manage Plugins` menu.

If this doesn't work see section towards the end of this document about
dependencies and try to do a manual install.

Manual Installation Guide - Linux (Debian based)
------------------------------------------------

Dependencies
............

The Graphical User Interface components are built using
`PyQt4 <http://www.riverbankcomputing.co.uk/software/pyqt/intro>`_ and the QGIS
plugin API (useful resources: `the QGIS Python Cookbook
<http://qgis.org/pyqgis-cookbook/>`_ and `the QGIS C++ API documentation
<http://qgis.org/api/>`_).  As such it is helpful if you are familiar with these
technologies (python, Qt4, PyQt4, QGIS). In addition, the following are needed
on your machine in order to work effectively with the code base:

* git
* rsync
* pep8
* nosetests (with coverage plugin)
* python-numpy (for numerical computations)
* python-gdal (python bindings to underlying gis functionality)
* python-sphinx (compilation of documents)
* cloud-sptheme (sphinx theme)
* pyqt4-dev-tools (compiling ui and resources)
* qt4-doc (qt4 API documentation)
* pyflakes (test for bad coding style like unused imports / vars)
* python-nosexcover and python-coverage (code coverage reporting)

On an ubuntu system you can install these requirements using apt::

   sudo apt-get install git rsync pep8 python-nose python-coverage \
   python-gdal python-numpy python-sphinx pyqt4-dev-tools pyflakes

   sudo pip install cloud-sptheme python-nosexcover

In some cases these dependencies may already be on your system via installation
process you followed for QGIS.

Cloning the source code from git
................................

To develop on the plugin, you first need to copy it to your local system. If
you are a developer, the simplest way to do that is go to
`~/.qgis/python/plugins` and clone inasafe from our GitHub repository
page like this::

   git clone git://github.com/AIFDR/inasafe.git  (for read only)
   git clone git@github.com:AIFDR/inasafe.git    (to commit changes)


QGIS installed in a non-standard location
.........................................

For running unit tests that need QGIS, you may need to adjust *PYTHONPATH* and
*QGIS_PREFIX_PATH* if QGIS is running in a non standard location. For example with
QGIS built from source into /usr/local (and python bindings global install
option disabled), you could run these commands (or add them to your ~/.bashrc)::

   export QGIS_PREFIX_PATH=/usr/local
   export PYTHONPATH=$PYTHONPATH:/usr/local/share/qgis/python/

.. note:: The above can be set within Eclipse's project properties if you are
    running your tests using the PyDev IDE environment.


Adding inasafe to your python path:
...................................

Lastly, you should add the inasafe plugin folder to your PYTHONPATH so that
package and module paths can be resolved correctly. E.g::

   export PYTHONPATH=$PYTHONPATH:${HOME}/.qgis/python/plugins/inasafe

Once again you could add this to your .bashrc or set it in Eclipse for
convenience if needed.

.. _running-tests-label:

Running tests
.............

You can run all tests (which includes code coverage reports and other
diagnostics) by doing this within the inasafe plugin folder::

   make test

You can also run individual tests using nose. For example to run the
riabclipper test you would do::

   nosetests -v gui.test_riabclipper

Achievements
............

.. note:: This is optional and thus not hard coded into the 
   makefile.

Optionally you can enable nose achievments which is a motivational
tool that gives you little achievement awards based on your test
results::

sudo pip install git+git://github.com/exogen/nose-achievements.git

Now create this file in the root of your inasafe git checkout 
:file:`setup.cfg`::
   
   [nosetests]
   with-achievements=1

When you run tests occasionally achievements will be displayed
to you at the end of the test run. See the achievements home page
at http://exogen.github.com/nose-achievements/.

Developing using Eclipse (Linux)
--------------------------------
.. note:: This is optional - you can use any environment you like for editing
   python, or even a simple text editor.


If you wish to use an IDE for development, please refer to
`this article <http://linfiniti.com/2011/12/remote-debugging-qgis-python-plugins-with-pydev/>`_
for detailed information on how to get the basic Eclipse with PyDev setup.

Creating a project
..................

The procedure for doing this is to do:
:menuselection:`File --> New --> Project...` and
then from the resulting dialog do :menuselection:`PyDev --> PyDev Project`.

In the resulting project dialog, set the following details:

* :guilabel:`Project name:` : :kbd:`inasafe`
* :guilabel:`Use default` : :kbd:`uncheck`
* :guilabel (linux):`Directory` : :kbd:`/home/<your user name/.qgis/python/plugins/inasafe/`
* :guilabel (windows):`Directory` : :kbd:`/home/<your user name/.qgis/python/plugins/inasafe/`
* :guilabel:`Choose project type` : :kbd:`Python`
* :guilabel:`Grammar Version` : :kbd:`2.7`
* :guilabel:`Add project directory to PYTHONPATH?` : :kbd:`check`

At this point you should should click the link entitled 'Please configure an interpreter
in related preferences before continuing.' And on the resulting dialog do:

* :guilabel:`Python Interpreters: New...` : :kbd:`click this button`

In the dialog that appears do:

* :guilabel:`Interpreter Name` : :kbd:`System Python 2.7`
* :guilabel:`Interpreter Executable` : :kbd:`/usr/bin/python`
* :guilabel:`OK Button` : :kbd:`click this button`

Another dialog will appear. Tick the first entry in the list that points to
your::

   ~/.eclipse/org.eclipse.platform_3.7.0_155965261/plugins/org.python.pydev_2.3.0.2011121518/

(or simply click the 'Select All' button)

* :guilabel:`OK Button` : :kbd:`click this button`

You will be returned to the Python Interpreters list and should see an entry for
System Python 2.7 listed there. Now do in the *Libraries* tab:

* :guilabel:`Finish` : :kbd:`click this button`

Remote Debugging with Eclipse
.............................

For remote debugging, you should add pydevd to your PYTHONPATH before starting *QGIS*
for example (you will need to adjust these paths to match your system)::

	export PYTHONPATH=$PYTHONPATH:/home/timlinux/.eclipse/org.eclipse.platform_3.7.0_155965261/plugins/org.python.pydev.debug_2.3.0.2011121518/pysrc/

.. note::

   If you are running with remote debugging enabled, be sure to start the
   PyDev debug server first before launching the Risk-in-a-box QGIS plugin
   otherwise QGIS will likely crash when it can't find the debug server.

You will need to ensure that the PYTHONPATH containing your pydev package folder
is set before you launch QGIS - for example by adding the above line to your ~/.bashrc
or by making a small batch file containing the above export and then sourcing the file
before launching QGIS e.g.::

    source riab_paths.sh
    /usr/local/bin/qgis

Running Unit tests from the IDE
...............................

Python has very good integrated support for unit testing. The first thing
you should do after setting up the IDE project is to run the tests. You can run tests
in the following ways:

* For the entire inasafe package
* For individual sub packages (e.g. engine, gui, storage, impact_functions)
* for an individual test module within a package
* for an class within a test module
* for an individual method within a test class

You can view these individual entities by browsing and expanding nodes in the project
panel in the left of the IDE.

.. note:: If you run the test suite for the entire inasafe package, it
    will mistakenly treat the sphinx documentation conf.py (docs.source.conf)
    as a test and fail for that test. This is 'normal' and can be ignored.





