
Development under MS Windows
============================

In this document we will walk you through the different activities you will
need to do as a windows developer wishing to work on the InaSAFE codebase.

Installation of version control tools
-------------------------------------

Setup msysgit
.............

To check out the code for development, you first need to install a git client.
We cover msysgit here, but you can also use
`tortoisegit <http://code.google.com/p/tortoisegit/downloads/list>`_
if you prefer (although the tortoise git procedure is not covered here).

To install msysgit (which is a command line git client), download the latest
version of the software from the 
`msysgit web site <http://code.google.com/p/msysgit/downloads/list>`_.
There is no need to get the 'full install' - just fetching the latest 'preview'
is good enough. For example at the time of writing I downloaded
:samp:`Git-1.7.9-preview20120201.exe`. The download is around 14mb in size.

Once the file is downloaded, run it and respond to the installer prompts as
illustrated below:

.. figure:: ../static/msysgit-step1.jpg
   :align:   center

   

.. figure:: ../static/msysgit-step2.jpg
   :align:   center

   

.. figure:: ../static/msysgit-step3.jpg
   :align:   center

   

.. figure:: ../static/msysgit-step4.jpg
   :align:   center

   

.. figure:: ../static/msysgit-step5.jpg
   :align:   center

   

.. figure:: ../static/msysgit-step6.jpg
   :align:   center

   

.. figure:: ../static/msysgit-step7.jpg
   :align:   center

   

.. figure:: ../static/msysgit-step8.jpg
   :align:   center

   

.. figure:: ../static/msysgit-step9.jpg
   :align:   center


Check out the code and the test data
------------------------------------

In this section we actually check out the source code and the test data
using the tools we installed above.

Clone the code repository
.........................

First open a GIT bash prompt as illustrated below:

.. figure:: ../static/msysgit-step10.jpg
   :align:   center


The repository can now be cloned by issuing the commands listed below.::

   cd  /c/Documents\ and\ Settings/<your username>/

   mkdir -p .qgis/python/plugins

   cd .qgis/python/plugins/

   git clone https://<your username>@github.com/AIFDR/inasafe.git inasafe-dev

.. note:: The items in angle brackets above should be replaced with your 
   personal details as required.

When the final command above runs, you should see something like this in the
console when the clone process is completed::

   $ git clone https://timlinux@github.com/AIFDR/inasafe.git inasafe-dev
   Cloning into 'inasafe'...
   remote: Counting objects: 5002, done.
   remote: Compressing objects: 100% (1526/1526), done.
   remote: Total 5002 (delta 3505), reused 4835 (delta 3338)
   Receiving objects: 100% (5002/5002), 2.38 MiB | 7 KiB/s, done.
   Resolving deltas: 100% (3505/3505), done.


Checkout the test data
......................

To check out the test data from git, first open a GIT bash prompt as illustrated below:

.. figure:: ../static/msysgit-step10.jpg
   :align:   center


The repository can now be cloned by issuing the commands listed below. (Already completed in previous step)::

   cd  /c/Documents\ and\ Settings/<your username>/.qgis/python/plugins/

   git clone https://<your username>@github.com/AIFDR/inasafe_data.git inasafe_data

.. note:: The items in angle brackets above should be replaced with your 
   personal details as required.

When the final command above runs, you should see something like this in the
console when the clone process is completed::

   $ git clone https://timlinux@github.com/AIFDR/inasafe_data.git inasafe_data
   Cloning into 'inasafe_data'...
   remote: Counting objects: 5002, done.
   remote: Compressing objects: 100% (1526/1526), done.
   remote: Total 5002 (delta 3505), reused 4835 (delta 3338)
   Receiving objects: 100% (5002/5002), 2.38 MiB | 7 KiB/s, done.
   Resolving deltas: 100% (3505/3505), done.

Install QGIS
............

Download the latest QGIS 'standalone' installer from http://download.qgis.org
and install it by running the installation wizard and accepting the defaults
throughout.

After opening QGIS (:menuselection:`Start --> All Programs --> Quantum GIS Lisboa --> Quantum GIS Desktop (1.8.0)`)
you need to enable the plugin from the plugin menu by doing :menuselection:`Plugins --> Manage Plugins`
and then search for the |project_name| plugin in the list and enable it.

Windows Caveats
...............

Our primary development platform is Linux (specifically Ubuntu Linux). Some
features of the development environment - particularly the **Make** tools do not
run on Windows. Some helper scripts have been written to substitute for make
but they do not have feature parity with the make scripts.


.. _windows-commandline_setup:

Command line environment setup
------------------------------

Create a shell launcher
.......................

A command line environment is useful for running unit tests and for developing
and testing standalone scripts written to use the |project_name| libraries.

We will create a custom shell launcher that will give you a python
shell environment using the python that comes bundled with QGIS, and that sets
various paths and evironment variables so everything works as expected. Save the 
following listing in <QGIS Install Dir>/bin/python-shell.bat::

   @echo off
   SET OSGEO4W_ROOT=C:\PROGRA~1\QUANTU~1
   call "%OSGEO4W_ROOT%"\bin\o4w_env.bat
   call "%OSGEO4W_ROOT%"\apps\grass\grass-6.4.2\etc\env.bat
   @echo off
   SET GDAL_DRIVER_PATH=%OSGEO4W_ROOT%\bin\gdalplugins\1.9
   path %PATH%;%OSGEO4W_ROOT%\apps\qgis\bin
   path %PATH%;%OSGEO4W_ROOT%\apps\grass\grass-6.4.2\lib
   path %PATH%;"%OSGEO4W_ROOT%\apps\Python27\Scripts\"
   
   set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python;
   set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\Python27\Lib\site-packages
   set QGIS_PREFIX_PATH=%OSGEO4W_ROOT%\apps\qgis
   cd "%HOMEPATH%\.qgis\python\plugins\inasafe-dev"
   start "Quantum GIS Shell" /B "cmd.exe" %*

.. note:: The QGIS_PREFIX_PATH environment variable should be unquoted!.

.. note:: You may need to replace PROGRA~1 above with PROGRA~2 if you are
   on 64bit windows.

.. note:: This script is for QGIS 1.8. You may need to do some adjustment if you are using another version of QGIS

For easy access to this shell launcher, right click on the qgis-shell.bat script
and (without releasing your initial right click) drag with the file onto your
start / windows button in the bottom left corner of the screen. 

Verifying your system path
..........................

To verify your path, launch your python shell (by clicking the python-shell.bat)
and then start a python shell. Now enter the follow simple script::

   import sys
   for item in sys.path:
       print item

Which should produce output like this::

   C:\Users\inasafe\.qgis\python\plugins\inasafe-dev
   C:\PROGRA~1\Quantum GIS Lisboa\apps\qgis\python
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\Lib\site-packages
   C:\PROGRA~1\Quantum GIS Lisboa\bin\python27.zip
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\DLLs
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\lib
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\lib\plat-win
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\lib\lib-tk
   C:\PROGRA~1\Quantum GIS Lisboa\bin
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\lib\site-packages\PIL
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\lib\site-packages\win32
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\lib\site-packages\win32\lib
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\lib\site-packages\Pythonwin
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\lib\site-packages\wx-2.8-msw-unicode

It is particularly the second and third lines that you need to have in place
so that the QGIS libs can found. Now dow a simple test to see if you can import
the QGIS libs::

   from qgis.core import *
   exit()

Assuming you get no error messages, you have a functional python command
line environment which you can use to test QGIS functionality with.

Nose testing tools
------------------

.. _windows-pip-setup:

Installing pip
..............

We need to install easy_install so that we can install pip so that we can
install nosetests and other python tools. Under windows you need to run a little
script to install easy_install and then use easy_install to install pypi.
Download the script on 
`this page <http://pypi.python.org/pypi/setuptools#windows>`_ called ez_setup.py
and save it somewhere familiar e.g. :samp:`c:\temp`.

.. note:: If you use windows 32bit, do not download the .exe file as said on 
   `the page <http://pypi.python.org/pypi/setuptools#windows>`_, but just download the ez_setup.py

Next launch the shell (python-shell.bat as described in
:ref:`windows-commandline_setup`) **as administrator** (by right clicking the
file and choosing run as administrator). Then from the command line, launch
:command:`ez_setup.py` by typing this::

   python c:\temp\ez_setup.py

.. note:: You will need to launch the shell as administrator whenever you 
   need to install python packages by pypi.

Now in the same shell, use easy setup to install pip (make sure you have added
the QGIS scripts dir to your shell launcher's - which should be the case if 
you have followed the notes in :ref:`windows-commandline_setup`)::
   
   easy_install pip

If the installation goes successfully, you should see output like this::

   Searching for pip
   Reading http://pypi.python.org/simple/pip/
   Reading http://pip.openplans.org
   Reading http://www.pip-installer.org
   Best match: pip 1.1
   Downloading http://pypi.python.org/packages/source/p/pip/pip-1.1.tar.gz#md5=62a9f08dd5dc69d76734568a6c040508
   Processing pip-1.1.tar.gz
   Running pip-1.1\setup.py -q bdist_egg --dist-dir c:\users\timsut~1\appdata\local
   \temp\easy_install--zkw-t\pip-1.1\egg-dist-tmp-mgb9he
   warning: no files found matching '*.html' under directory 'docs'
   warning: no previously-included files matching '*.txt' found under directory 'docs\_build'
   no previously-included directories found matching 'docs\_build\_sources'
   Adding pip 1.1 to easy-install.pth file
   Installing pip-script.py script to C:\PROGRA~2\QUANTU~1\apps\Python25\Scripts
   Installing pip.exe script to C:\PROGRA~2\QUANTU~1\apps\Python25\Scripts
   Installing pip.exe.manifest script to C:\PROGRA~2\QUANTU~1\apps\Python25\Scripts
   Installing pip-2.5-script.py script to C:\PROGRA~2\QUANTU~1\apps\Python25\Scripts
   Installing pip-2.5.exe script to C:\PROGRA~2\QUANTU~1\apps\Python25\Scripts
   Installing pip-2.5.exe.manifest script to C:\PROGRA~2\QUANTU~1\apps\Python25\Scripts
   
   Installed c:\progra~2\quantu~1\apps\python25\lib\site-packages\pip-1.1-py2.5.egg
   Processing dependencies for pip
   Finished processing dependencies for pip

Installing nose
...............

`Nose <http://somethingaboutorange.com/mrl/projects/nose/>`_ is a tool for 
automation of running python unit tests. With nose you can run a whole batch
of tests in one go. With the nosecover plugin you can also generate coverage
reports which will indicate how many lines of your code actually have been
tested. 


To install these tools, launch your python prompt as administrator and then do::

   pip install nose nose-cov

Running tests using nose
........................

Once they are installed, you can run the nose tests from windows by going to
the plugin directory/inasafe-dev folder (in your python-shell.bat shell session) and running::

   runtests.bat


Building sphinx documentation
-----------------------------

`Sphinx <http://sphinx.pocoo.org>`_ is a tool for building documentation that
has been written in the ReSTructured text markup language (a simple wiki like
format). You can build the sphinx documentation under windows using a helper
script provided in the docs directory of the |project_name| source directory,
but first you need to actually install sphinx.

Installing sphinx
.................

Launch your QGIS python shell environment (see :ref:`windows-pip-setup`) as 
administrator and then run the following command::

   pip install sphinx

The cloud-sptheme package installs the sphinx theme we are using.


Building the documentation
..........................

To build the documentation, open a QGIS python shell (no need to be admin) and
go into your inasafe-dev/docs directory. Now run the following command::

   make.bat html

.. note:: Only the html make target has been tested. To use other make targets
   you may need to perform further system administrative tasks.

Viewing the documentation
.........................

The documentation can be viewed from withing QGIS by clicking the :guilabel:`help`
button on the |project_name| dock panel, or you can view it in your browser by
opening a url similar to this one::

   file:///C:/Users/Tim%20Sutton/.qgis/python/plugins/inasafe/docs/_build/html/index.html


Developing using Eclipse (Windows)
----------------------------------

.. note:: This is optional - you can use any environment you like for editing
   python, or even a simple text editor.

If you wish to use an IDE for development, please refer to
`this article <http://linfiniti.com/2011/12/remote-debugging-qgis-python-plugins-with-pydev/>`_
for detailed information on how to get the basic Eclipse with PyDev setup.

Installing Eclipse
..................

You can download and install eclipse by getting the latest installer at
`eclipse.org <http://eclipse.org>`_. Just run the installer accepting all
defaults.

Installing PyDev
................

With Eclipse running, click  on :menuselection:`Help --> Eclipse Marketplace`
and from the resulting dialog that appears, type :kbd:`PyDev` into the search
box and then click :guilabel:`Go`. On the search results page, choose PyDev 
and click the :guilabel:`Install` button next to it. Agree to the license terms 
and accept the aptana certificate, then restart Eclipse as requested. 

Custom Eclipse Launcher
.......................

You need to create a custom Eclipse launcher in order to use Eclipse PyDev. The
process is similar to :ref:`windows-commandline_setup` in that you need to 
create a custom batch file that launches eclipse only after the osgeo4w
environment has been imported. Here are the typical contexts of the file::

   @echo off

   SET OSGEO4W_ROOT=C:\PROGRA~2\QUANTU~1
   call "%OSGEO4W_ROOT%"\bin\o4w_env.bat
   call "%OSGEO4W_ROOT%"\apps\grass\grass-6.4.2\etc\env.bat
   @echo off
   SET GDAL_DRIVER_PATH=%OSGEO4W_ROOT%\bin\gdalplugins\1.8
   path %PATH%;%OSGEO4W_ROOT%\apps\qgis\bin;%OSGEO4W_ROOT%\apps\grass\grass-6.4.2\lib
   set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python;
   set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\Python27\Lib\site-packages
   set QGIS_PREFIX_PATH=%OSGEO4W_ROOT%\apps\qgis
   "C:\Progra~2\eclipse\eclipse.exe"

.. note:: Use the path where your eclipse was extracted. Also note that PROGRA~2 may 
   be PROGRA~1 in 32bit windows.

Save this file under <QGIS Install Dir>/bin/python-shell.bat and then right-drag
it from explorer to your Windows start button to create an easily accessible 
shortcut to eclipse.

Creating a project
..................

The procedure for doing this is to do:
:menuselection:`File --> New --> Project...` and
then from the resulting dialog do :menuselection:`PyDev --> PyDev Project`.

In the resulting project dialog, set the following details:

* :guilabel:`Project name:` : :kbd:`inasafe`
* :guilabel:`Use default` : :kbd:`uncheck`
* :guilabel (windows):`Directory` : 
  :kbd:`C:\\Users\\<user>\\.qgis\\python\\plugins\\inasafe\\`
* :guilabel:`Choose project type` : :kbd:`Python`
* :guilabel:`Grammar Version` : :kbd:`2.7`
* :guilabel:`Add project directory to PYTHONPATH?` : :kbd:`check`

.. note:: The python shipped with QGIS for windows is version 2.7 so you should
   avoid using any additions to the python spec introduced in later versions.

At this point you should should click the link entitled 'Please configure an interpreter
in related preferences before continuing.' And on the resulting dialog do:

* :guilabel:`Python Interpreters: New...` : :kbd:`click this button`

In the dialog that appears do:

* :guilabel:`Interpreter Name` : :kbd:`QGIS Python 2.7`
* :guilabel:`Interpreter Executable` : 
  :kbd:`C:\\Program Files (x86)\\Quantum GIS Lisboa\\bin\\python.exe`
* :guilabel:`OK Button` : :kbd:`click this button`


Another dialog will appear. Tick the first entry in the list that points to
your::

      C:\\users\\inasafe\\Downloads\\eclipse\\plugins\\org.python.pydev
      _2.6.0.2012062818\\pysrc

The resulting list of python paths should look something like this::
   
   C:\Program Files\eclipse\plugins\org.python.pydev_2.6.0.2012062818\pysrc
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\DLLs
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\lib
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\lib\plat-win
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\lib\lib-tk
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\lib\site-packages
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\lib\site-packages\win32
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\lib\site-packages\win32\lib
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\lib\site-packages\Pythonwin
   C:\PROGRA~1\Quantum GIS Lisboa\apps\Python27\lib\site-packages\wx-2.8-msw-unicode

Click on the :guilabel:`New folder` button and add the QGIS python dir::

   C:\Program Files\Quantum GIS Lisboa\apps\qgis\python

* :guilabel:`OK Button` : :kbd:`click this button`

You will be returned to the Python Interpreters list and should see an entry for
**QGIS Python 2.7** listed there. Now do in the **Environment** tab:

:guilabel:`New`

In the dialog that appears 

:guilabel:`Name` : :kbd:`QGIS_PREFIX_PATH`
:guilabel:`Value` : :kbd:`C:\\PROGRA~1\\QUANTU~1\\apps\\qgis`

Then click ok to close the environment variable editor.

* :guilabel:`Ok` : :kbd:`click this button`

Then click finsih to finish the new project dialog
.

* :guilabel:`Finish` : :kbd:`click this button`


Remote Debugging with Eclipse
.............................

For remote debugging, you should add pydevd to your PYTHONPATH before starting
*QGIS*. Under Windows, the best way to do this is to add the following line to
:command:`qgis.bat` under C:\Program Files (x86)\Quantum GIS Wroclaw\bin::

   SET PYTHONPATH=%PYTHONPATH%;C:\Progra~1\eclipse\plugins\org.python.pydev.debug_2.3.0.2011121518\pysrc


.. note::

   (1) You need to add a settrace() line at the point in your code where 
   you would like to initiate remote debugging. After that, you can insert 
   eclipse debugger breakpoints as per normal.

   (2) If you are running with remote debugging enabled, be sure to start the
   PyDev debug server first before launching the Risk-in-a-box QGIS plugin
   otherwise QGIS will likely crash when it can't find the debug server.

   (3) Place the above PYTHONPATH command before the final line that launches
   QGIS!
   
   (4) The exact path used will vary on your system - check in your eclipse
   plugins folder for "org.python.pydev.debug_<some date> to identify the
   correct path.

To initiate a remote debugging session, add the settrace() directive to your
source file and then start the python remote debugging service from the PyDev
debug perspective. Then launch QGIS (or your command line application) and 
use the application until the settrace line is encountered. QGIS will appear
to freeze - this is normal. Now switch to Eclipse and you should see the 
settrace line has been highlighted in green and you can step through the code
using standard Eclipse debugging tools (done most easily from the debugging
perspective).

.. note:: Always remove or comment out settrace() when are done debugging!


Running Unit tests from the IDE
...............................

Using PyDev's build in test runner
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Python has very good integrated support for unit testing. The first thing
you should do after setting up the IDE project is to run the tests. You can run
tests in the following ways:

* For the entire inasafe package
* For individual sub packages (e.g. engine, gui, storage, impact_functions)
* for an individual test module within a package
* for an class within a test module
* for an individual method within a test class

You can view these individual entities by browsing and expanding nodes in the
project panel in the left of the IDE.

.. note:: If you run the test suite for the entire inasafe package, it
   will mistakenly treat the sphinx documentation conf.py (docs.source.conf)
   as a test and fail for that test. This is 'normal' and can be ignored.

Setting PyDev to use the Nose test runner
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can also configure Eclipse to run the tests using nose (which is
recommended). To do this first do:

:menuselection:`Window --> Preferences --> PyDev -- PyUnit`

Now set :guilabel:`TestRunner` to :kbd:`Nosetests` and set the following
options::

    -v --with-id --with-coverage --cover-package=storage,engine,impact_functions,gui

As with using Pydev's built in test runner, you can also run any module, class
etc. while using the nose test runner by right clicking on the item in the
PyDev package explorer.

.. note:: Actually, we can run the test runner until this step. But, we got a 
   problem, so you need to install python in your windows machine.
