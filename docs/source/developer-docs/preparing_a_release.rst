===================
Preparing a release
===================

This document outlines the steps that need to be carried out in order
to issue a new release of the |project_name| plugin. The steps can be outlined
as follows and are described in detail below:

+ Identify what version number the new release will be assigned.
+ Close all issues marked as blockers for the release.
+ If needed, create a release branch
+ Update all source files to the new version number.
+ Update all source files for PEP8 and PEP257 compliance.
+ Ensure no assert statements are critical to code flow
+ Ensure that Qt resources and user interface files have been compiled
+ Ensure that user interface files meet HIG compliance
+ Enure all unit tests complete successfully and that tests that are expected
  to fail are documented.
+ Ensure that user acceptance testing has been carried out.
+ Ensure that all translation string lists have been updated and that the
  translation process has been carried out.
+ Ensure that all new and existing features are adequately documented.
+ Ensure that the API documentation is up to date.
+ Update the changelog.
+ Ensure that the sphinx documentation is compiled.
+ Generate python optimsed (.pyo) files for all sources.
+ Update the plugin metadata to reflect current version.
+ Generate a test package and validate in a clean room environment.
+ Optionally branch the release in the revision control system.
+ Tag the release in the revision control system.
+ Upload the updated package zip file to old QGIS python plugin repository.
+ Upload the updated package zip file to the new QGIS python plugin repository.
+ Make announcements and press releases as needed.


Release numbering
.................

|project_name| will follow the `semantic versioning system <http://semver.org/>`_.
Simply put, the following scheme should be applied to version numbers:

.. table::

   ===================  ============================================================
    Version Increment     Intention
   ===================  ============================================================
    Major e.g 1.0.0     API incompatibility with the previous major release.
    Minor e.g. 1.1.0    API compatibility and extension over previous minor release.
    Point e.g. 1.1.1    API compatibility, bug fixes for previous point release.
    Alpha e.g. 1.0.0a   Feature incomplete preview of a minor or major release
    RC e.g. 1.1.0rc1    Feature complete preview of a minor or major release
   ===================  ============================================================

To identify the next release number, the table above can simply be appled. Here
are a couple of examples.

* You have fixed various bugs without adding new features or breaking the API,
  and you are ready to immediately publish your work. Result: **New point
  release.**
* You have implemented many new features, some of which required breaking API
  compatibility with the existing major release. Now you would like to make
  a public preview of your work before committing to a final release. Result:
  **New major release candidate.**


**Outcome:** A version number for the next release eg. 0.1.0.

Issue completion
................

Having determined the release number, you should use the GitHub *labels*
capability to assign a label matching the release to each blocking ticket.
There is no fixed rule on which tickets should be tagged for the release - the
best judgment of developers and managers should be used based on severity of
issues, available time to deadline, budget etc.

**Outcome:** At the end of  this step all `issues <https://github.com/AIFDR/inasafe/issues>`_
tagged for the release should be closed.


Branching
.........

Branching is requred for Major and Minor releases. The process of branching
is described in :doc:`version_control` whose accompanying illustration is
repeated below for your convenience:

.. figure:: ../static/release-workflow.png
   :align:   center

The purpose of creating a branch is to isolate incompatible and possibly
unstable changes that take place in the *master branch* from stable code
that forms the basis of a release. You will note from the diagram above
that branches are named after the minor version, and are tagged with the point
version at the point of release.

**Outcome:** If needed, create a release branch which provides a 'known good'
version that can be returned to at any point in time.

Updating the source version number
..................................

In the preample to any source file there should be a standard header as
described in the :doc:`coding_standards` document. Included in this header
section is the version number e.g.::

   __version__ = '0.1.0'

This number should be updated in every source file prior to release. Under
linux this can easily be done using the :command:`rpl` command (which can
easily be installed (by doing for example :command:`sudo apt-get install rpl`).

Using th example above, to update version numbers for minor release '0.1.1'
you could issue the following command at the root of the plugin source tree::

   rpl "__version__ = '0.1.0'" "__version__ = '0.1.1'" *.py

**Outcome::** Every source file should be updated to indicate the version number.

PEP8 and PEP257 compliance
..........................

These **Python Enhancement Proposals** (PEP) relate to the formatting
of python source code. In particular they mandate spacing, layout, line lengths
and so on. The outcome of PEP8 and PEP257 compliance is code that is
consistently formatted accross the whole code base, regardless of authorship.

This consistency makes it easier to incorporate new members into the project
team and to collaborate effectively within the team. A number of tools are
available to help you to identify PEP8 and PEP257 transgressions, and there
is a Makefile target (:command:`make pep8` which will do a PEP8 test for you).
Under the Eclipse/PyDev IDE, there is also on the fly checking support which
can be enabled and that will notify you of any compliance issues as illutrated
in the screenshot below.

.. figure:: ../static/pep8-highlighting.jpeg
   :align:   center


**Outcome:** All source files for PEP8 and PEP257 compliance.

Check for assert statements
...........................

Using assert to raise exceptions in non test code can have bad side effects
because if python is run in optimised mode e.g. python -O, these lines are
ignored and the program logic will no longer work as expected.
On some platforms the use of python optimised code is mandated and we are
likely to get hard to investigate bug reports from end users at some
unspecified point in the future.

.. note:: This is a 'soft' requirement - since the python code for the plugin
   will be executed by the QGIS python internals, we can be fairly certain that
   python code will be executed with out the -O optimisation option for the
   short term.

**Outcome:** No assert statements used to control logic flow.

Compile Qt resources and user interface files
.............................................

The Qt4 resource and user interface definition files supplied with Risk in a
Box need to be compiled before they can be deployed. There are two utility
functions provided by Qt4 for this purpose:

* :command:`pyuic4` - A tool to compile Qt4 user interface definition files
  (.ui) into python source code. The .ui files contain xml which describes the
  placement of widgets within a user interface file.
* :command:`pyrcc4` - A tool to compile Qt4 resource files into python source
  code. Qt4 resources are 'in-code' representations of application resources
  needed at run time. These include images, icons, html, css etc. - whatever
  the application may need to use at runtime without resorting to retrieving
  assets from the filesystem.

The compilation of these resources if the default make target in the root and
*gui* python package. To compile them simply do::

   cd <inasafe source>
   make


**Outcome:** Qt resources and user interface files have been compiled

HIG Compliance
..............

The InaSAFE human interface guidelnes (HIG) are described in the :ref:`hig-label`
document. User interface should strive to comply with these guidelines. As
an over-arching principle, before any release, the user interface elements that
comprise that release should be tested both for usability and to ensure that
they are functional.

There is no automated test system for HIG. Before making a release of HIG
compliance, each dialog should be manually tested and inspected.

**Outcome:** A consistent, user friendly and functional graphical user interface
environment for the software that comprises the releases.

Unit Testing
............

During the development process, unit tests should be written (following the
principles of test driven development). A good test suite allows the code to
be shipped with confidence knowing it will behave as expected. At the time of
release, all the tests in the test suite should either pass or have documented
reasons as to why they fail, and that they are expected to fail.

In addition, tests should provide a code coverage of 80% or better of the
shipped code base. More informationn on running unit tests is included in
:ref:`running-tests-label`.

**Outcome:** All unit tests complete successfully, or when expected
to fail are documented accordingly.

User Acceptance Testing
-----------------------

While unit testing provides a quantitative measure of the code's robustness,
user acceptance testing provides a qualitative measure. The plugin should
be made available to 'invested' users to test with real world data and in
real world usage scenarios. Any issues with workflow, ease of use, quality of
model outputs and reports etc. should be identified at this point and remedied.

**Outcome:** Software that works in real world usage.

Document new features
---------------------

New features in the release should be well documented using the procedure
described in :ref:`documenting-new-features-howto-label`.

**Outcome:** All new and existing features are adequately documented.

API Documentation
-----------------

In addition to documenting new features, any new python modules introduced
during the development work leading up to the release need to be included
in the API documentation. This process is described in detail in the
:ref:`api-documentation-howto-label` document.

**Outcome:** The API is completely documented with rich, relevant documentation.


Update the changelog
--------------------

A changelog should be maintained (:file:`docs/sources/user-docs/changelog.rst`)
that lists the key new features and improvement made with each release. Use
the :doc:`../user-docs/changelog` file to guide the style of any edits and
additions made.

The changelog should not exhaustively list every commit that took place. Rather
it should list the key features and bug fixes that were made during the
release cycle.

.. note:: New release changesets should be introduced to this file **at the top**
   so that the newest release is alwas listed first.

**Outcome:** A succinct list of changes and improvements that were made during
the release cycle.

Finalise translations
.....................

The |project_name| plugin is built from the ground up for internationalization.
In particular the following two languages are supported as part of this
project:

* English
* Bahasa Indonesian

There are three components of the project that require translation:

+ The Graphical User Interface - primarily the :file:`gui` python package.
  Qt4 .ts files are used for these translations.
+ The |project_name| libraries - these components provide the underlying
  functionality of the scenario assessment. Python gettext is used for these
  translations.
+ The sphinx documentation - this is translated using gettext.

The translation process for the first two items above is documented in
detail in :doc:`i18n`. The sphinx translation process is not yet well
documented, although it will be similar to the gettext process.

The final strings should be made available to translators before the release,
during which time a string freeze should be in effect on the release code tree.

Once the translation files have been updated, they should be converted to
compiled string lists (.qm and .mo files for Qt4 and gettext respectively) and
made available as part of the distribution.

**Outcome:** The released plugin will be multilingual supporting both
indonesian and english.

Compile the sphinx documentation
--------------------------------

Once documentation is completed, it should be compiled using
:command:`make docs` and the :command:`git status` command should be used to
ensure that all generated documentation is also under version control.

**Outcome:** Sphinx documentation is compiled providing complete documentation
to be shipped with the plugin.

Update plugin metadata
----------------------

QGIS uses specific metadata to register the plugin. At the time of writing
the mechanism for registering this metadata is in transition from an in-source
based system to an .ini file based system. In the interim, both should be
maintained.

The in-source metadata is updated by editing the :file:`__init__.py` file
in the top level directory of the source tree::

   def name():
      """A user friendly name for the plugin."""
      return '|project_name|'


   def description():
       """A one line description for the plugin."""
       return 'InaSAFE Disaster risk assessment tool developed by AusAid and World Bank'


   def version():
       """Version of the plugin."""
       return 'Version 0.1'


   def icon():
       """Icon path for the plugin."""
       return 'icon.png'


   def qgisMinimumVersion():
       """Minimum version of QGIS needed to run this plugin -
       currently set to 1.7."""
       return '1.7'

In general only the version function needs to be updated to reflect the new
version of the InaSAFE plugin.

.. note:: The above will be deprecated with the release of QGIS 2.0, see
   below for the alternative method of describing the plugin.

For newer versions of QGIS (1.8+), the :file:`metadata.txt` will be used to
store descriptive information about the plugin. Simply edit this file with
a text editor and update it as needed.

**Outcome:** The plugin metadata to reflects the current version of Risk in a
Box.

Generate a test package
-----------------------

At this point a test package should be generated that can be used to test
the plugin in a clean room environment. A clean room environment comprises a
system that has a fresh operating system installation with the desired version
of QGIS installed, and **no other software**. It is probably a good practice
to use machine virtualisation for this purpose, for example with images
of a windows and a linux system installed. Some virtualisation tools such as
vmware provide the ability to create a system snapshot and roll back to it.

To generate a test package, use the :file:`scripts/release.sh` bash script.

For exampled to create a test package for version 0.1.0 of the software,
issue the following command::

   scripts/release.sh 0.1.0

The generated package will be placed in the /tmp directory of your linux system.

Once the clean system is started, extract the package contents into the user's
personal plugin directory. For example under Linux::

   mkdir -p ~/.qgis/python/plugins
   cd ~/.qgis/python/plugins
   unzip inasafe.0.1.0.zip

Now start QGIS and enable the plugin in the QGIS plugin manager (
:menuselection:`Plugins --> Manage Plugins`).

Branch the release
------------------

This step is only done for minor and major releases, point releases are only
tagged. The branch should be named after the major and minor version numbers
only - for example: :samp:`version-1_0`. The following console log illustrates
how to create a local branch, push it to the origin repository, remove the local
branch and then track the repository version of the branch localy::

   git branch version-0_1
   git push origin version-0_1
   git branch -D version-0_1
   git fetch origin
   git branch --track version-0_1 origin/version-0_1
   git checkout version-0_1


**Outcome:** A branch on the remote repository named after the majon and minor
version numbers.

Tag the release
---------------

Tagging the release provides a 'known good' state for the software which
represents a point in time where all of the above items in this list have
been checked. The tag should be named after the major, minor and point release
for example :samp:`version-0_1_0`. If the release is a releas candidate or
and alpha release the letters :samp:`rc` or :samp:`a` resepectively should
be appended respectively, along with the related number. For example version
0.1.0 alpha 1 would be tagged as :samp:`version-0_1_0a1`. To tag the release
simply do it in git as illustrated below.::

   git tag version-0_1_0
   git push --tags origin version-0_1_0

.. note:: 1) Replace 'dot' separators with underscores for the version number.
   2) You can differentiate release **branches** from release **tags** by the
   fact that branch names have only the minor version number (e.g.
   :samp:`version-0_4`) whereas release tags are reserved for point releases
   (e.g. :samp:`version-0_4_1`).

**Outcome:** The release is tagged in GIT and can be checked out at any point
in the future. The tagged source tree can easily be downloaded at any point by
visiting https://github.com/AIFDR/inasafe/tags

Upload the package
------------------

QGIS provides an online plugin repository that centralizes the distribution
and retrieval of plugins. It is the most efficient way to make your plugin
available to the world at large.

* Upload the updated package zip file to old QGIS python plugin repository.
* Upload the updated package zip file to the new QGIS python plugin repository.

Press announcements
-------------------

Once the release has been made, an announcement should be made to inform
interested parties about the availability of the new software. A pro-forma
announcement is provided below **(Trevor or Ole todo)**::

   Dear |project_name| Users

   We are pleased to announce the immediate availability of the newest
   version of |project_name| (version X.X.X). This version includes numerous
   bug fixes and improvements over the previous release::

   ----- changelog goes here -------------

   We welcome any feedback you may have on this release. You can use our
   issue tracker (requires free account) to notify us of any issues you may
   have encountered whilst using the system. The tracker is available here:

   https://github.com/AIFDR/inasafe/issues

   This project is supported by the Australian Aid Agency and the World Bank.

   Best regards

   (Name of person)

A standard list of contacts should be compiled and the notification sent to
all those listed.


**Outcome:** Interested parties are informed about the availability of the
new release.
