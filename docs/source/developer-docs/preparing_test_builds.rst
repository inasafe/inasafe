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

You should now see the experimental versions of InaSAFE listed in the
:guilabel:`Plugins` tab.

.. note:: The URL may differ depending on where the test repo is hosted (see
    below).


Configuring the hosting of the test build repo.
--------------------------------------------------

Prepare your server:
....................

Install some packages (run this on the server)::

    sudo apt-get install git fabric apache2

Initialise everything (run this on your desktop)::

    fab -H 188.40.123.80:8697 remote build_test

.. note:: You need to be able to authenticate on the server hosting the
    test builds.

The above would create a test package based on current master by default. You
can also specify a branch to build the package from like this::

    fab -H 188.40.123.80:8697 remote build_test_package:branch=version-2_0
