#!/bin/sh
# Ensure script exits on error
set -e

# 1) Create necessary directories if missing
mkdir -p /app/data/processed /app/logs

# 2) Fix ownership to the non-root user
chown -R appuser:appgroup /app/data/processed /app/logs

# 3) Drop privileges and execute the main process as appuser
exec gosu appuser "$@"