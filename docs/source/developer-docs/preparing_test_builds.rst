==============
Test builds
==============

Test builds are created using fabric (http://fabfile.org) and a bash script.

Test builds are intended for early adopters / testers who want to use the
bleeding edge version of InaSAFE.

.. warning:: Using test builds may result in strange behaviour or bad things
  happening when you run your assessment. We try our best to keep the master
  in a good, usable and secure (for you) state, but we can't guarantee this
  will always be the case.

This document has two sections:

* How to configure QGIS to use the InaSAFE test builds repo.
* How to set up a test build server (intended only for sysadmins).

Configuring QGIS to use test builds (from Linfiniti server).
------------------------------------------------------------

* :menuselection:`Plugins --> Fetch Python Plugins --> Repository Tab --> Add...`
* :guilabel:`Name:` :kbd:`InaSAFE Testing`
* :guilabel:`URL:` :kbd:`http://inasafe-test.linfiniti.com/plugins.xml`
* :guilabel:`OK`

In the :guilabel:`Options` tab, tick the
:guilabel:`Show all plugins, even those marked as experimental` option.

You should now see the experimental versions of InaSAFE listed in the
:guilabel:`Plugins` tab.

.. note:: The URL may differ depending on where the test repo is hosted (see
    below).


Configuring the hosting of the test build repo.
--------------------------------------------------

Register a (sub)domain:
.......................

To host your repo, you should create a DNS domain or subdomain reserved
exclusively for use of the fabric script & repo. For example during the recent
floods in Jakarta (Jan 2013), we registered a new subdomain
'inasafe-crisis.linfiniti.com' by creating the following 'a record' (alias
record) on our DNS server configuration panel::

    record type     value
        a           inasafe-crisis.linfiniti.com

Prepare a server/name mapping:
..............................

The purpose of the server/name mapping is to determine what (sub)domain to
publish the repo under. This is carried out via a simple dictionary. For
example running :samp:`hostname` on the deployment server might return
'linfiniti' in which case to deploy the inasafe-crisis.linfiniti.com repo we
would add an entry to the fabfile.py as follows::

    def _all():
        """Things to do regardless of whether command is local or remote."""
        site_names = {
            'waterfall': 'inasafe-test.localhost',
            'spur': 'inasafe-test.localhost',
            'maps.linfiniti.com': 'inasafe-test.linfiniti.com',
            'linfiniti': 'inasafe-crisis.linfiniti.com}

Basically, this last key-value pair says 'if the hostname command on the server
returns "linfiniti" then deploy a web site called inasafe-crisis on that
server'. The resultant web site will have a new repository created that a
user could add to their QGIS plugin repository list as::

    http://inasafe-crisis.linfiniti.com/plugins.xml


Prepare your server:
....................

Install some packages (run this on the server)::

    sudo apt-get install git fabric apache2

Create a package:
.................

Initialise everything (run this on your desktop)::

    fab -H 188.40.123.80:8697 remote build_test

.. note:: You need to be able to authenticate on the server hosting the
    test builds.

The above would create a test package based on current master by default. You
can also specify a branch to build the package from like this::

    fab -H 188.40.123.80:8697 remote build_test_package:branch=version-1_1

Version number increments:
..........................

One problem you may want to consider is that if you release consecutive test
builds with the same version number, the python plugin manager in QGIS will not
indicate that a new package is available. For this reason we recommend adding
an incremental build number to the version numbers in :file:`__init__.py` and
:file:`metadata.txt`. For example::

    version=1.1.0-1

In this case the '-1' at the end of the version number designates that it
is build 1. You should manually increment this number and commit it **to
the branch you are building** each time before creating a package.
