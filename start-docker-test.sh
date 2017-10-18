#!/usr/bin/env bash

docker run -d --name qgis-testing-environment -v ${PWD}:/tests_directory -e ON_TRAVIS=false -e MUTE_LOGS=true -e DISPLAY=:99 kartoza/qgis-testing:boundlessgeo-2.14.7
sleep 10
docker exec -it qgis-testing-environment sh -c "qgis_setup.sh inasafe"
docker exec -it qgis-testing-environment sh -c "pip install --upgrade pep257"
docker exec -it qgis-testing-environment sh -c "pip install --upgrade flake8"
