#!/bin/bash

# You can use this script as the 'execute shell' in a jenkins job.
# For example, set the 'command' contents to this to run the safe package tests:
#
# #!/bin/bash
# scripts/jenkins-linux.sh
#
# Note that since you are fetching the script from Git that you want jenkins
# to run, you will have to build at least once (and probably it will fail)
# before the script is available on the jenkins server for it to be run.
#
# Tim Sutton, February 2014
#

# Configuration option:
# Add packages to this list if you want to be able to run the tests for that package
ALLOWED_TESTS="safe realtime batch impact_stats report test tools utilities widgets"

# You should not need to edit anything after this point.
# -------------------------------------------------------------------------

# Check we got at least and only one input parameter.
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


# Subroutine to determine if an array contains an element
# Usage:
# in_array "foo" "foo bar foobar"
# will match to foo

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


# Main script logic from here
# -------------------------------------------------------------------------


# Set up needed QGIS environment variables
export QGIS_PREFIX_PATH=/usr/local/qgis-2.0/
export PYTHONPATH=${QGIS_PREFIX_PATH}/share/qgis/python/:${QGIS_PREFIX_PATH}/share/qgis/python/plugins:`pwd`
echo "PYTHONPATH: $PYTHONPATH" > /tmp/path.txt
export LD_LIBRARY_PATH=${QGIS_PREFIX_PATH}/lib
export INASAFE_POPULATION_PATH=/var/lib/jenkins/jobs/InaSAFE-QGIS2/exposure/population.tif

in_array "$1" "${ALLOWED_TEST_PACKAGES}"

VALID=$?

if [ ! $VALID ]; then
    echo 'Please use one of these for the parameters:'
    echo "${ALLOWED_TESTS[@]}"
    echo
    exit 1
fi

DIR=`pwd`
TEST_PACKAGE=$1
echo "Running tests in $PATH"

# Make sure data dir is current and synced it its git clone
#scripts/update-test-data.sh
source /var/lib/jenkins/jobs/InaSAFE-QGIS2/env.sh

#Go on with metrics and tests
make clean
if [[ $TEST_PACKAGE == 'safe' ]] || [[ $TEST_PACKAGE == 'realtime' ]]; then
    # special case for safe or realtime package
    TEST_PATH="$DIR/$TEST_PACKAGE"
    xvfb-run --server-args="-screen 0, 1024x768x24" nosetests -v \
        --with-id --with-xcoverage --with-xunit --verbose \
        --cover-package=${TEST_PACKAGE} ${TEST_PATH}
else
    # all other packages get dealt with the same way
    TEST_PATH="$DIR/safe_qgis/$TEST_PACKAGE"
    xvfb-run --server-args="-screen 0, 1024x768x24" nosetests -v \
        --with-id --with-xcoverage --with-xunit --verbose \
        --cover-package=safe_qgis.${TEST_PACKAGE} ${TEST_PATH}
fi

make jenkins-pyflakes
make jenkins-pep8
make jenkins-pylint
make jenkins-sloccount
