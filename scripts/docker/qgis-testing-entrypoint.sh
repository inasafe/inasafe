#!/usr/bin/env bash

# Docker entrypoint file intended for docker-compose recipe for running unittests

set -e

source /tests_directory/scripts/docker/inasafe-test-pre-scripts.sh

# Run supervisor
# This is the default command of qgis/qgis but we will run it in background
supervisord -c /etc/supervisor/supervisord.conf &

# Wait for XVFB
sleep 10

exec "$@"
