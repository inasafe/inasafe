Risk-in-a-box Developer Documentation
=====================================

Code documentation
------------------

* :doc:`api-docs`
* :doc:`todo`

Issue tracker: https://github.com/AIFDR/risk_in_a_box/issues


Requirements to develop Risk-in-a-Box
-------------------------------------

Risk-in-a-box is built in python and runs as a plugin in `QGIS
<http://qgis.org>`_.  The Graphical User Interface components are built using
`PyQt4 <http://www.riverbankcomputing.co.uk/software/pyqt/intro>`_ and the QGIS
plugin API (useful resources: `the QGIS Python Cookbook
<http://qgis.org/pyqgis-cookbook/>`_ and `the QGIS C++ API documentation
<http://qgis.org/api/>`_).  As such it is helpful if you are familiar with these
technologies (python, Qt4, PyQt4, QGIS). In addition, the following are needed
on your machine in order to work effectively with the code base:

* git
* subversion
* pep8
* nosetests (with coverage plugin)
* python-numpy (for numerical computations)
* python-gdal (python bindings to underlying gis functionality)
* python-sphinx (compilation of documents)
* pyqt4-dev-tools (compiling ui and resources)
* qt4-doc (qt4 API documentation)


On an ubuntu system you can install these requirements using apt::

  sudo apt-get install git subversion pep8 python-nose python-coverage \
  python-gdal python-numpy python-sphinx pyqt4-dev-tools


In some cases these dependencies may already be on your system via installation
process you followed for QGIS.

Quick Installation Guide - Developers
-------------------------------------

To develop on the plugin, you first need to copy it to your local system. If
you are a developer, the simplest way to do that is go to
`~/.qgis/python/plugins` and clone risk_in_a_box from our GitHub repository
page like this::

  git clone git://github.com/AIFDR/risk_in_a_box.git  (for read only)
  git clone git@github.com:AIFDR/risk_in_a_box.git    (to commit changes)

To verify that the installation works you can run the test suite from the command line::

  make test

This will run all the regression tests and also highlight any code issues.
Note that first time the tests are run they will pull 250MB of test data from
our subversion repository (If asked for a password just hit Enter). See further 
notes on running tests below.


To run the plugin start QGIS and enable it from the :menuselection:`Plugins --> Manage Plugins`
menu. 

Remote Debugging with and IDE
.............................

If you wish to use an IDE for development, please refer to 
`this article <http://linfiniti.com/2011/12/remote-debugging-qgis-python-plugins-with-pydev/>`_
for detailed information on how you can do so.

For remote debugging, you should add pydevd to your PYTHONPATH before starting QGIS
for example (you will need to adjust these paths to match your system)::

	export PYTHONPATH=$PYTHONPATH:/home/timlinux/.eclipse/org.eclipse.platform_3.7.0_155965261/plugins/org.python.pydev.debug_2.3.0.2011121518/pysrc/

.. note::

   If you are running with remote debugging enabled, be sure to start the
   PyDev debug server first before launching the Risk-in-a-box QGIS plugin
   otherwise QGIS will likely crash when it can't find the debug server.

You will need to ensure that the PYTHONPATH containing your pydev package folder 
is set before you launch QGIS - for example by adding the above line to your ~/.bashrc. 

QGIS installed in a non-standard location
.........................................

For running unit tests that need QGIS, you may need to adjust PYTHONPATH and QGISPATH 
if QGIS is running in a non standard location. For example with QGIS built from source 
into /usr/local (and python bindings global install option disabled), you could run 
these commands (or add them to your ~/.bashrc)::

	export QGISPATH=/usr/local
	export PYTHONPATH=$PYTHONPATH:/usr/local/share/qgis/python/

.. note:: The above can be set within Eclipse's project properties if you are running 
your tests using the PyDev IDE environment.


Adding risk_in_a_box to your python path:
.........................................

Lastly, you should add the riab plugin folder to your PYTHONPATH so that 
package and module paths can be resolved correctly. E.g::

	export PYTHONPATH=$PYTHONPATH:${HOME}/.qgis/python/plugins/risk_in_a_box

Once again you could add this to your .bashrc or set it in Eclipse for convenience 
if needed.

Running tests
.............

You can run all tests (which includes code coverage reports and other 
diagnostics) by doing this within the risk_in_a_box plugin folder::

	make test

You can also run individual tests using nose. For example to run the riabclipper 
test you would do::

	nosetests -v gui.test_riabclipper


Coding Standards
================

Please observe the following coding standards when working on the codebase:

* Docstrings quoted with :samp:`"""`
* Simple strings in source code should be quoted with :samp:`'`
* Coding must follow a style guide. In case of Python it is `pep8 <http://www.python.org/dev/peps/pep-0008>`_ and 
  using the command line tool pep8 (or :samp:`make pep8`) to enforce this
* `Python documentation guide <http://www.python.org/dev/peps/pep-0257>`_
* Adherence to regression/unit testing wherever possible (:samp:`make test`)
* Use of github for revision control, issue tracking and management
* Simple deployment procedure - all dependencies must be delivered with 
  the plugin installer for QGIS or exist in standard QGIS installs.
* Develop in the spirit of XP/Agile, i.e. frequent releases, continuous 
  integration and iterative development. The master branch should always 
  be assumed to represent a working demo with all tests passing.


Branching guide
---------------

Risiko follows the following simple branching model:

*New development* takes place in *master*. Master should always be maintained in a 
usable state with tests passing and the code functional as far as possible such 
that we can create a new release from master at short notice.

*Releases* should take place in long lived branches named after the minor version number 
(we follow the `semantic versioning scheme <http://semver.org/>`_) so for example the first
release would be version 0.1 and would be in a branch from master called *release_0-1*.

After the minor release branch is made, the *point releases (patch)* are created as tags 
off that branch. For example the release flow for version 0.1.0  would be:

* branch release_0.1 from master
* apply any final polishing the the relase_0-1 branch
* when we are ready to release, tag the branch as release_0-1-0
* create packages from a checkout of the tag

After the release, development should take place in master. Additional short lived 
branches can be made off master while new features are worked on, and then merged into 
master when they are ready.

Optionally, development can also be carried out in independent forks of the risk_in_a_box 
repository and then merged into master when they are ready via a pull request or patch.

Commits to master that constitute bug fixes to existing features should be backported to 
the current release branch using the :samp:`git cherry-pick` command. Alternatively, if 
a fix is made in the release branch, the changeset should be applied to master where 
appropriate in order to ensure that master includes all bug fixes from the release branches. 


Process for developers adding a new feature
-------------------------------------------

Create a feature branch
    * git checkout -b <featurebranch> develop

Write new code and tests
    ...

Publish (if unfinished)
    * git push origin <featurebranch>

To keep branch up to date
    * git checkout <featurebranch>
    * git merge origin develop

When all tests pass, either merge into develop
    * git checkout master
    * git merge --no-ff <featurebranch>
      (possibly resolve conflict and verify test suite runs)
    * git push origin master

Or issue a pull request through github
    ..

To delete when branch is no longer needed (though it is preferable to do 
such work in a fork of the official repo).

    * git push origin :<featurebranch>


Process for checking out the release branch and applying a fix:
---------------------------------------------------------------

Create a local `tracking branch <http://book.git-scm.com/4_tracking_branches.html>`_::

	git fetch
	git branch --track release-0_1 origin/release-0_1
	git checkout release-0_1
	
Now apply your fix, test and commit::

	git commit -m "Fix issue #22 - results do not display"
	git push

To backport the fix to master do (you should test after cherry picking and 
before pushing though)::

	git checkout master
	git cherry-pick 0fh12
	git push

To checkout someone else's fork:
--------------------------------

Example::

	git remote add jeff git://githup.com/jj0hns0n/riab.git
	git remote update
	git checkout -b impact_map jeff/impact_map

