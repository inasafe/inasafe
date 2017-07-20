#!/usr/bin/env bash

LOCALES=$*

python_safe=`find realtime/ -regex ".*\(ui\|py\)$" -type f`

# update .ts
echo "Please provide translations by editing the translation files below:"
for LOCALE in ${LOCALES}
do
echo "realtime/i18n/inasafe_"${LOCALE}".ts"
# Note we don't use pylupdate with qt .pro file approach as it is flakey
# about what is made available.
set -x
pylupdate4 -noobsolete ${python_safe} -ts realtime/i18n/inasafe_realtime_${LOCALE}.ts
done

