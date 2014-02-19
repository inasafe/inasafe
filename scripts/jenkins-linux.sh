#!/bin/bash

in_array () {
  SEARCH_TERM=$1
  ARRAY=$2
  for ITEM in $ARRAY;
  do
    if [[ "$SEARCH_TERM" == "$ITEM" ]]; then
        return 0
    fi
  done
  return 1
}


export QGIS_PREFIX_PATH=/usr/local/qgis-2.0/
export PYTHONPATH=${QGIS_PREFIX_PATH}/share/qgis/python/:${QGIS_PREFIX_PATH}/share/qgis/python/plugins:`pwd`
echo "PYTHONPATH: $PYTHONPATH" > /tmp/path.txt
export LD_LIBRARY_PATH=${QGIS_PREFIX_PATH}/lib
export INASAFE_POPULATION_PATH=/var/lib/jenkins/jobs/InaSAFE-QGIS2/exposure/population.tif

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <test subpath>"
    echo "e.g."
    echo "$0 widgets"
    echo
    echo "Will run all tests in safe_qgis.widgets package"
    echo "and limit coverage report to that package"
    echo
    exit 1
fi

TEST=$1

ALLOWED_TESTS="batch impact_stats report test tools utilities widgets"

in_array "$1" "${ALLOWED_TESTS}"

VALID=$?

if [ ! $VALID ]; then
    echo 'Please use one of these for the parameters:'
    echo "${ALLOWED_TESTS[@]}"
    echo
    exit 1
fi

DIR=`pwd`
TEST_PATH="$DIR/safe_qgis/$TEST"

echo "Running tests in $PATH"


# Make sure data dir is current and synced it its git clone
#scripts/update-test-data.sh
source /var/lib/jenkins/jobs/InaSAFE-QGIS2/env.sh

#Go on with metrics and tests
make clean
xvfb-run --server-args="-screen 0, 1024x768x24" nosetests -v \
    --with-id --with-xcoverage --with-xunit --verbose \
    --cover-package=safe_qgis.${TEST} ${TEST_PATH}

make jenkins-pyflakes
make jenkins-pep8
make jenkins-pylint
make jenkins-sloccount
