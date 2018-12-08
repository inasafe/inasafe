#!/usr/bin/env bash
IMAGE=qgis/qgis
QGIS_VERSION_TAG=release-3_4

DISPLAY=${DISPLAY:-:99}

if [ "${DISPLAY}" != ":99" ]; then
    xhost +
fi

docker run -d --name qgis-testing-environment \
    -v ${PWD}:/tests_directory \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e WITH_PYTHON_PEP=false \
    -e ON_TRAVIS=false \
    -e INASAFE_DISABLE_WELCOME_MESSAGE=1 \
    -e INASAFE_LOGGING_LEVEL=50 \
    -e MUTE_LOGS=true \
    -e DISPLAY=${DISPLAY} \
    ${IMAGE}:${QGIS_VERSION_TAG}


sleep 10
docker exec -it qgis-testing-environment sh -c "pip3 install -r /tests_directory/REQUIREMENTS.txt"
docker exec -it qgis-testing-environment sh -c "pip3 install -r /tests_directory/REQUIREMENTS_TESTING.txt"

docker exec -it qgis-testing-environment sh -c "qgis_setup.sh inasafe"

# FIX default installation because the sources must be in "inasafe" parent folder
docker exec -it qgis-testing-environment sh -c "rm -f  /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/inasafe"
docker exec -it qgis-testing-environment sh -c "ln -s /tests_directory/ /root/.local/share/QGIS/QGIS3/profiles/default/python/plugins/inasafe"

# Run the real test
time docker exec -it qgis-testing-environment sh -c "qgis_testrunner.sh test_suite.test_package"

docker kill qgis-testing-environment
docker rm qgis-testing-environment
