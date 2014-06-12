InaSAFE
=======

InaSAFE is free software that allows disaster managers to study realistic
natural hazard impact scenarios for better planning, preparedness and
response activities. InaSAFE is a plugin for [QGIS](http://qgis.org).

For more information about InaSAFE and its documentation please visit [inasafe.org] (http://www.inasafe.org).

The latest source code is available at
[https://github.com/AIFDR/inasafe](https://github.com/AIFDR/inasafe),
which contains modules for risk calculations, GIS functionality and
functions for impact modelling.


Story queue on Waffle:
[![Stories in Ready](https://badge.waffle.io/AIFDR/inasafe.png?label=ready)](http://waffle.io/AIFDR/inasafe)
[![Stories in In Progress](https://badge.waffle.io/AIFDR/inasafe.png?label=ready)](http://waffle.io/AIFDR/inasafe)

Current test status for master branch:
* [![Build Status](http://jenkins.inasafe.org/job/inasafe-qgis2/badge/icon)](http://jenkins.inasafe.org/job/inasafe-qgis2/) - ALL Tests
* [![Build Status](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-master/job/inasafe-qgis2-impact-stats-test/badge/icon)](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-master/job/inasafe-qgis2-impact-stats-test/) - impact-stats-test
* [![Build Status](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-master/job/inasafe-qgis2-realtime-test/badge/icon)](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-master/job/inasafe-qgis2-realtime-test/) - realtime-test
* [![Build Status](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-master/job/inasafe-qgis2-report-test/badge/icon)](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-master/job/inasafe-qgis2-report-test/) - report-test
* [![Build Status](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-master/job/inasafe-qgis2-safe-package/badge/icon)](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-master/job/inasafe-qgis2-safe-package/) - safe-package
* [![Build Status](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-master/job/inasafe-qgis2-test/badge/icon)](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-master/job/inasafe-qgis2-test/) - test
* [![Build Status](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-master/job/inasafe-qgis2-tools-test/badge/icon)](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-master/job/inasafe-qgis2-tools-test/) - tools-test
* [![Build Status](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-master/job/inasafe-qgis2-utilities-test/badge/icon)](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-master/job/inasafe-qgis2-utilities-test/) - utilities-test
* [![Build Status](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-master/job/inasafe-qgis2-widgets-test/badge/icon)](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-master/job/inasafe-qgis2-widgets-test/) - widgets-test

Current test status for develop branch:
* [![Build Status](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-develop/job/impact-stats-test/badge/icon)](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-develop/job/impact-stats-test/) - impact-stats-test
* [![Build Status](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-develop/job/realtime-test/badge/icon)](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-develop/job/realtime-test/) - realtime-test
* [![Build Status](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-develop/job/report-test/badge/icon)](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-develop/job/report-test/) - report-test
* [![Build Status](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-develop/job/safe-package/badge/icon)](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-develop/job/safe-package/) - safe-package
* [![Build Status](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-develop/job/test/badge/icon)](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-develop/job/test/) - test
* [![Build Status](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-develop/job/tools-test/badge/icon)](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-develop/job/tools-test/) - tools-test
* [![Build Status](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-develop/job/utilities-test/badge/icon)](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-develop/job/utilities-test/) - utilities-test
* [![Build Status](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-develop/job/widgets-test/badge/icon)](http://jenkins.inasafe.org/view/QGIS2-InaSAFE-develop/job/widgets-test/) - widgets-test

PyPi Downloads for the 'safe' library:
[![Downloads](https://pypip.in/d/python-safe/badge.png)](https://crate.io/packages/python-safe)
[![Downloads](https://pypip.in/v/python-safe/badge.png)](https://crate.io/packages/python-safe)



Quick Installation Guide
========================

You first need to have [QGIS](http://qgis.org/) installed. Grab your free
copy from [the QGIS download page](http://download/qgis.org).

To install the InaSAFE plugin, use the plugin manager in
[QGIS](http://qgis.org):

  Plugins → Manage and Install Plugins → Get more tab

Then search for "InaSAFE", select it and click the install button.
The plugin will now be added to your plugins menu.

**Note:** You may need to restart QGIS if upgrading from a prior version.


System Requirements
-------------------

 - A standard PC with at least 4GB of RAM running Windows, Linux or Mac OS X
 - The QGIS Open Source Geographic Information System (http://www.qgis.org).
   InaSAFE requires QGIS version 1.7 or newer.

Limitations
===========

InaSAFE is a new project. The current code development started in
earnest in January 2012 and there is still much to be done.  However,
we work under the philosophy that stakeholders should have access to the
development and source code from the very beginning and invite
comments, suggestions and contributions.  See
[our milestones list](https://github.com/AIFDR/inasafe/issues/milestones) and
[our open issues list](https://github.com/AIFDR/inasafe/issues?page=1&state=open)
for known bugs and outstanding tasks.


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



