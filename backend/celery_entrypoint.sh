#!/usr/bin/env sh
set -e

if [ -d "/data" ]; then
  chown -R appuser:appuser /data
fi

exec gosu appuser "$@"
