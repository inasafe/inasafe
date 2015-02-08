#!/bin/bash
LOCALES=$*

# get newest .py file
NEWESTPY=0
PYTHONFILES=$(find . -name '*.py' | grep -v venv)
for PYTHONFILE in ${PYTHONFILES}
do
  PYTHONFILEMOD=$(stat -c %Y ${PYTHONFILE})
  if [[ "${PYTHONFILEMOD}" -gt "${NEWESTPY}" ]]
  then
    NEWESTPY=${PYTHONFILEMOD}
  fi
done

# Qt translation stuff
# for .ts file
UPDATE=false
for LOCALE in ${LOCALES}
do
  TSFILE="i18n/inasafe_"${LOCALE}".ts"
  TSMODTIME=$(stat -c %Y ${TSFILE})
  if [ ${NEWESTPY} -gt ${TSMODTIME} ]
  then
    UPDATE=true
    break
  fi
done

if [ ${UPDATE} == true ]
# retrieve all python files in safe and realtime
then
  python_safe=`find safe/ -regex ".*\(ui\|py\)$" -type f`
  python_realtime=`find realtime/ -regex ".*\(ui\|py\)$" -type f`
  # concat list of files
  python_all="$python_safe $python_realtime"

  # update .ts
  echo "Please provide translations by editing the translation files below:"
  for LOCALE in ${LOCALES}
  do
    echo "i18n/inasafe_"${LOCALE}".ts"
    # Note we don't use pylupdate with qt .pro file approach as it is flakey
    # about what is made available.
    set -x
    pylupdate4 -noobsolete ${python_all} -ts i18n/inasafe_${LOCALE}.ts
  done
else
  echo "No need to edit any translation files (.ts) because no python files "
  echo "has been updated since the last update translation. "
fi

