==============
Nightly builds
==============

Nightly builds are created using fabric (http://fabfile.org) and a bash script.

Nightly builds are intended for early adopters / testers who want to use the
bleeding edge version of InaSAFE.

.. warning:: Using nightly builds may result in strange behaviour or bad things
  happening when you run your assessment. We try our best to keep the master
  in a good, usable and secure (for you) state, but we can't guarantee this
  will always be the case.

This document has two sections:


* How to configure QGIS to use the InaSAFE nightly builds repo.
* How to set up a nightly build server (intended only for sysadmins).

Configuring QGIS to use nightly builds.
---------------------------------------




Configuring the hosting of the nightly build repo.
--------------------------------------------------

Prepare your server:
....................

Install some packages::

    sudo apt-get install git fabric apache2

Do a read only checkout::

    cd ~
    mkdir -p ~/dev/python/
    cd ~/dev/python
    git clone git://github.com/AIFDR/inasafe.git inasafe-nightly

Initialise your configuration::

    SITE_NAME=inasafe-nightly.linfiniti.com fab


SITE_NAME=inasafe-nightly.linfiniti.com fab build_nightly
