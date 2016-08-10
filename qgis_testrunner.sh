#!/bin/bash
# Run a test inside QGIS
### Turn on debug mode ###
#set -x

TEST_NAME=$1

cd /tests_directory
echo "Running test $1 ..."
OUTPUT=$(unbuffer qgis --nologo --code /usr/bin/qgis_testrunner.py $TEST_NAME  2>/dev/null | tee /dev/tty)
EXIT_CODE="$?"
if [ -z "$OUTPUT" ]; then
    echo "ERROR: no output from the test runner! (exit code: ${EXIT_CODE})"
    exit 1
fi
echo $OUTPUT | grep -q "FAILED ("
RESULT_CODE="$?"
echo "Finished running test $1."
if [ "$RESULT_CODE" != "0" ];
    then exit 0;
fi
exit 1