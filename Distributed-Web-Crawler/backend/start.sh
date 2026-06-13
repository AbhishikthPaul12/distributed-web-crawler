#!/bin/sh
set -e

exec gunicorn \
  --bind "0.0.0.0:${PORT:-5000}" \
  --workers "${WEB_CONCURRENCY:-1}" \
  --timeout 120 \
  api.app:app
