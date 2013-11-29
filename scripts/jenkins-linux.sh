#!/bin/bash
export QGIS_PREFIX_PATH=/usr/local/qgis-2.0/
export PYTHONPATH=${QGIS_PREFIX_PATH}/share/qgis/python/:`pwd`
export LD_LIBRARY_PATH=${QGIS_PREFIX_PATH}/lib
export INASAFE_POPULATION_PATH=/var/lib/jenkins/jobs/InaSAFE-QGIS2/exposure/population.tif

# Make sure data dir is current and synced it its git clone
#scripts/update-test-data.sh
source /var/lib/jenkins/jobs/InaSAFE-QGIS2/env.sh

#Go on with metrics and tests
nosetests -v --with-id --with-xcoverage --with-xunit --verbose --cover-package=safe,safe_qgis,realtime safe safe_qgis realtime
make jenkins-pyflakes
make jenkins-pep8
make jenkins-pylint
make jenkins-sloccount
#make jenkins-qgis2-test
