InaSAFE
=======

[![InaSAFE Screenshot](http://inasafe.org/wp-content/uploads/2017/06/InaSAFE-screenshot-lores-1.jpg)](http://www.inasafe.org)

InaSAFE is free software that allows disaster managers to study realistic
natural hazard impact scenarios for better planning, preparedness and
response activities. InaSAFE is a plugin for [QGIS](http://qgis.org).

For more information about InaSAFE and its documentation please visit [inasafe.org](http://www.inasafe.org).

The latest source code is available at
[https://github.com/inasafe/inasafe](https://github.com/inasafe/inasafe),
which contains modules for risk calculations, GIS functionality and
functions for impact modelling.


* Current Travis test status master: [![Travis Build Status](https://travis-ci.org/inasafe/inasafe.svg?branch=master)](https://travis-ci.org/inasafe/inasafe)
* Current Landscape code health master: [![Landscape Code Health](https://landscape.io/github/inasafe/inasafe/master/landscape.svg?style=flat)](https://landscape.io/github/inasafe/inasafe/master)
* Current Travis test status develop: [![Travis Build Status](https://travis-ci.org/inasafe/inasafe.svg?branch=develop)](https://travis-ci.org/inasafe/inasafe)
* Current Landscape code health develop: [![Code Health](https://landscape.io/github/inasafe/inasafe/develop/landscape.svg?style=flat)](https://landscape.io/github/inasafe/inasafe/develop)
* PyPi Downloads for InaSAFE: [![PyPI version](https://badge.fury.io/py/inasafe-core.svg)](https://badge.fury.io/py/inasafe-core)
* PyPi Downloads for the old 'safe' library (currently unmaintained): [![PyPI version](https://badge.fury.io/py/python-safe.svg)](https://badge.fury.io/py/python-safe)
* Github download: [![Github All Releases](https://img.shields.io/github/downloads/inasafe/inasafe/total.svg)]()

Quick Installation Guide
========================

You first need to have [QGIS](http://qgis.org/) installed. Grab your free copy from [the QGIS download page](http://download.qgis.org).

To install the InaSAFE plugin, use the plugin manager in [QGIS](http://qgis.org):

  Plugins → Manage and Install Plugins

Then search for "InaSAFE", select it and click the install button.
The plugin will now be added to your plugins menu.

**Note:** You may need to restart QGIS if upgrading from a prior version.

Participation
=============

We work under the philosophy that stakeholders should have access to the
development and source code, and be able to participate in every level of the 
project - we invite comments, suggestions and contributions.  See
[our milestones list](https://github.com/AIFDR/inasafe/issues/milestones) and
[our open issues list](https://github.com/inasafe/inasafe/issues?q=is%3Aopen+is%3Aissue+no%3Amilestone)
for known bugs and outstanding tasks. You can also chat live with our developers
and community members using the link below.

[![Join the chat at https://gitter.im/AIFDR/inasafe](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/AIFDR/inasafe?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)


System Requirements
-------------------

 - A standard PC with at least 4GB of RAM running Windows, Linux or Mac OS X
 - The QGIS Open Source Geographic Information System (http://www.qgis.org).
   Although InaSAFE will probably run on any version of QGIS version above 2.0
   or newer, our supported version is the latest Long Term Release version
   of QGIS.

Running tests
-------------------

 - InaSAFE is using the Unittest Python framework.
 - Different ways that you can run tests:
   - On Travis using a Pull Request
   - In QGIS Desktop if you enable `developer mode` in Plugins -> InaSAFE -> Options -> Advanced, restart QGIS and then click the run tests button.
   - Using docker `make docker-test`
   - Using PyCharm if you set up the dev environment with the qgis_prefix_path

History
=======

* In March 2011, Risk In A Box (the predecessor to InaSAFE) was built as a web 
  application running as a GeoNode Plugin.
* InaSAFE development as a QGIS plugin started in January 2012.
* In October 2012, version 1.0 of InaSAFE was launched at the [5th Asian ministerial conference on disaster risk reduction (AMCDRR)](http://www.unisdr.org/we/inform/events/23540) where it was demonstrated to 
  the then president of Indonesia, Susilo Bambang Yudhoyono who praised the project.
* On 30 Jan 2013, InaSAFE was awarded the prestigious [Black Duck Open Source Rookie of the Year Award](https://www.blackducksoftware.com/open-source-rookies).
* Version 2.0 of InaSAFE was released in January, 2014.
* Version 3.0 was released in March 2015 which added support
  for using the QGIS API within impact functions.
* Version 4.0 was released in March 2017.
* Version 5.0 was released in November 2018 which add support for QGIS 3.x

Disclaimer
==========

InaSAFE has been jointly developed by the Indonesian Government-BNPB, the
Australian Government, the World Bank-GFDRR and independent contributors.
These agencies and the individual software developers of InaSAFE take no
responsibility for the correctness of outputs from InaSAFE or decisions 
derived as a consequence.


License
=======

InaSAFE is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License version 3 (GPLv3) as
published by the Free Software Foundation.

The full GNU General Public License is available in LICENSE.txt or
http://www.gnu.org/licenses/gpl.html


Disclaimer of Warranty (GPLv3)
==============================

There is no warranty for the program, to the extent permitted by
applicable law. Except when otherwise stated in writing the copyright
holders and/or other parties provide the program "as is" without warranty
of any kind, either expressed or implied, including, but not limited to,
the implied warranties of merchantability and fitness for a particular
purpose. The entire risk as to the quality and performance of the program
is with you. Should the program prove defective, you assume the cost of
all necessary servicing, repair or correction.


Limitation of Liability (GPLv3)
===============================

In no event unless required by applicable law or agreed to in writing
will any copyright holder, or any other party who modifies and/or conveys
the program as permitted above, be liable to you for damages, including any
general, special, incidental or consequential damages arising out of the
use or inability to use the program (including but not limited to loss of
data or data being rendered inaccurate or losses sustained by you or third
parties or a failure of the program to operate with any other programs),
even if such holder or other party has been advised of the possibility of
such damages.

