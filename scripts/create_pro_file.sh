#!/bin/bash

SAFE_PYFILES=`find safe -name "**.py**" | grep -v "pyc$" | grep -v test`
UI_FILES=`find safe -name "**.ui**"`

PRO_FILE=inasafe.pro

echo "SOURCES = \\" > ${PRO_FILE}

# First add the SAFE files to the pro file
for FILE in ${SAFE_PYFILES}
do
  echo "    ${FILE} \\"  >> ${PRO_FILE}
done

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
TRANSLATIONS = safe/i18n/inasafe_id.ts \\
               safe/i18n/inasafe_fr.ts \\
               safe/i18n/inasafe_es_ES.ts \\
               safe/i18n/inasafe_vi.ts \\
               safe/i18n/inasafe_af.ts"  >> ${PRO_FILE}
