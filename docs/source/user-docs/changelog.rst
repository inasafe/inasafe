
==========
Whats new?
==========


Changelog for version 1.0.1
---------------------------

* Fix https://github.com/AIFDR/inasafe/issues/374
* Fix https://github.com/AIFDR/inasafe/issues/375

Changelog for version 1.0.0
---------------------------

* Added post processor infrastructure including gender and age specific indicators
* Added data source attribution
* Various GUI updates
* Added use of transparency in generated maps
* Added an earthquake impact function
* Documentation updates
* Many bugfixes and architectural improvements
* Better internationalisation support

Changelog for version 0.5.2
---------------------------

* This is a bugfix update to address some minor translation issues in the
  InaSAFE package.

Changelog for version 0.5.1
---------------------------

* This is a bugfix update to reduce the size of the InaSAFE package.

Changelog for version 0.5.0
---------------------------

* Better documentation. See http://inasafe.org/contents.html
* Time stamp and other metadata added to generated map PDF.
* Initial support for parameterisation of impact functions.
* Updated logging infrastructure including support for logging to the
  QGIS log panel.
* Fixed missing InaSAFE icon in QGIS plugin manager.
* Fixes for help system under windows.
* Multi-page support for generated report PDF (which is now created as a
  separate document).
* Ability to combine polygon hazard  (such as flood prone areas) with
  population density.
* Option to use entire intersection of hazard and exposure instead of clipping
  to the somewhat arbitrary viewport (the training revealed that this was a bit
  confusing)
* Aggregation of raster impact layers by arbitrary polygon layers (such as
  kelurahan boundaries)
* Limited support for runtime configuration of impact functions (e.g. by
  changing thresholds). This is an interim measure while the team is working on
  a GUI to manipulate impact functions more generally.
* More DRR actions added to impact function reports (such as how will warnings
  be disseminated, how will we reach stranded people etc.)
* Volcanic (zonal hazard) impact assessments on building and population
* New function table view that lists all the available impact functions and allows
  them to be filtered by different criteria.
* Lots of small improvements to error reporting, GUI, translations and code quality.

Changelog for version 0.4.1
...........................

* This is a minor bugfix release with packaging and documentation related
  changes only so that InaSAFE can be deployed via the official QGIS repository.
* Added InaSAFE tutorial to sphinx documentation

Changelog for version 0.4.0
...........................
* Ability to automatically handle multipart vector data: https://github.com/AIFDR/inasafe/issues/160
* Better error reporting:

 * https://github.com/AIFDR/inasafe/issues/170
 * https://github.com/AIFDR/inasafe/issues/161
 * https://github.com/AIFDR/inasafe/issues/157

* Bug fixing:

 * https://github.com/AIFDR/inasafe/issues/159
 * https://github.com/AIFDR/inasafe/issues/156
 * https://github.com/AIFDR/inasafe/issues/173
 * https://github.com/AIFDR/inasafe/issues/166
 * https://github.com/AIFDR/inasafe/issues/162

* InaSAFE APIs better defined: https://github.com/AIFDR/inasafe/issues/134
* Release procedure developed: https://github.com/AIFDR/inasafe/issues/109
* Added estimate of displaced people to earthquake fatality model: https://github.com/AIFDR/inasafe/commit/04f0e1d
* Achieved 100% translation for Bahasa Indonesia
* Made bundled test and demo data public with associated license information
* Added AusAid and World Bank logos to dock
* Fixed bug with flood population evacuation reporting units



Changelog for version 0.3.0
...........................
* Documentation updates - extended guides for using the |project_name| dock and
  keyword editors.
* Support for remote layers in keywords editor and scenario modelling
* Added options dialog
* Support for using all layers in hazard and exposure combos, not just visible
  ones (configurable in options dialog)
* Support for displaying keywords title in QGIS layer list (configurable in
  options dialog)
* When selecting a hazard or exposure layer, its keywords are now displayed
  in the results area.
* Performance improvements when toggling layer visibility and adding and
  removing layers.
* Support for QGIS 1.8 when it is released
* Numerous other 'under the hood' bug fixes and improvements
* Migrated code base from RIAB to InaSAFE and restructured the code base
* Added additional tests

Changelog for version 0.2.1:
............................
* Correct translation of 'run' in indonesian. Closes #128
* Updated so that version number is shown in dock
* Removed generated file from polygon test
* Removed the -dev designation from branch releases
* Fix indent error causing noise to show in qgis plugin manager
* Fixed typo - BNPD to BNPB
* Fixed bug where close button does not dispose of the help dialog
* Fixed an issue that prevented the use of earthquake functions when using
  keywords with lowercase mmi. Closes #142
* Fix for mac clipping issues - the plugin should work on OSX now. Closes #141.
  Note that OSX users should upgrade to GDAL 1.9 available here:
  http://www.kyngchaos.com/software/qgis

Changelog for version 0.2.1:
............................

* Map printing support
* Improved translation support and Indonesian translation updates
* Rebranded from Risk in a Box to InaSAFE
* Documentation updates and documented windows developer procedures
* Support for generating documentation and running tests under Windows
* Scripts for semi-automatic packaging of a release
* Improvements to Impact calculator algorithms

Changelog for version 0.1.0:
............................

* First QGIS plugin implementation of |project_name|.
* Migrated calculation engine from Risiko project.
* Implemented support for polygon hazard layers.
* Added dock widget for designing and executing a scenario model.
* Added the keyword editor for assigning metadata to input files.
* Added integrated context help tool.
* Removed django specific dependencies from the InaSAFE libs.
* removed dependency on SciPy
* Support for internationalisation.
* Comprehensive documentation system.

