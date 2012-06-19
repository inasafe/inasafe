#!/bin/bash

# A simple script to compute translation stats for each locale
#
# T. Sutton June, 2012

cd gui
REPORT=`lrelease inasafe.pro 2>/dev/null`
echo $REPORT| grep -o '[0-9]*\ finished\ and\ [0-9]*\ unfinished\|_[a-z][a-z]\.qm'|sed 's/_/Locale: /g'| sed 's/.qm//g'
cd ..

