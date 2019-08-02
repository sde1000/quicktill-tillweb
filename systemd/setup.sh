#!/bin/bash

# This script is invoked by systemd prior to starting uwsgi
# The current working directory will be the repo's root directory
# DJANGO_SETTINGS_MODULE will already be set

if [ "${DJANGO_SETTINGS_MODULE}" = "" ]; then
    echo DJANGO_SETTINGS_MODULE is not set
    exit 1
fi

set -e

source venv/bin/activate
./manage.py collectstatic --no-input
./manage.py migrate
