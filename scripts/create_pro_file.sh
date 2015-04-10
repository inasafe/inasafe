#!/bin/bash

SAFE_PYFILES=`find safe -name "**.py**" | grep -v "pyc$" | grep -v test`
REALTIME_PYFILES=`find realtime -name "**.py**" | grep -v "pyc$" | grep -v test`
UI_FILES=`find safe -name "**.ui**"`

PRO_FILE=inasafe.pro

echo "SOURCES = \\" > ${PRO_FILE}

# First add the SAFE files to the pro file
for FILE in ${SAFE_PYFILES}
do
  echo "    ${FILE} \\"  >> ${PRO_FILE}
done

# Now the realtime files - last file should not have a backslash
# so we handle add some logic to detect if we are on the last file
LAST_FILE=""
for FILE in ${REALTIME_PYFILES}
do
        if [ ! -z ${LAST_FILE} ]
        then
                echo "    ${LAST_FILE} \\" >> ${PRO_FILE}
        fi
        LAST_FILE=${FILE}
done
if [ ! -z ${LAST_FILE} ]
then
        echo "    ${LAST_FILE}" >> ${PRO_FILE}
fi

echo "
FORMS = \\" >> ${PRO_FILE}

LAST_FILE=""
for FILE in ${UI_FILES}
do
        if [ ! -z ${LAST_FILE} ]
        then
                echo "    ${LAST_FILE} \\" >> ${PRO_FILE}
        fi
        LAST_FILE=${FILE}
done
if [ ! -z ${LAST_FILE} ]
then
        echo "    ${LAST_FILE}" >> ${PRO_FILE}
fi

# Finally define which languages we are translating for

echo "
TRANSLATIONS = i18n/inasafe_id.ts \\
               i18n/inasafe_fr.ts \\
               i18n/inasafe_af.ts"  >> ${PRO_FILE}
