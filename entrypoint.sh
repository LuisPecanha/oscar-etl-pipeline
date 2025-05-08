#!/bin/sh
set -e

# ensure mount points exist
mkdir -p /app/data/processed /app/logs

# chown using the numeric UID and GID of appuser
chown -R "$(id -u appuser)":"$(id -g appuser)" /app/data/processed /app/logs

# drop privileges and run the main command
exec gosu appuser "$@"