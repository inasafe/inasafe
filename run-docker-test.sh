#!/usr/bin/env bash
docker exec -it qgis-testing-environment sh -c "qgis_testrunner.sh test_suite.test_package"
