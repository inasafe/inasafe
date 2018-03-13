#!/usr/bin/env bash

docker run -d --name qgis-testing-environment -v ${PWD}:/tests_directory -e WITH_PYTHON_PEP=false -e ON_TRAVIS=false -e MUTE_LOGS=true -e DISPLAY=:99 kartoza/qgis-testing:boundlessgeo-2.14.7
sleep 10
docker exec -it qgis-testing-environment sh -c "qgis_setup.sh inasafe"
time docker exec -it qgis-testing-environment sh -c "qgis_testrunner.sh test_suite.test_package"
docker kill qgis-testing-environment
docker rm qgis-testing-environment
