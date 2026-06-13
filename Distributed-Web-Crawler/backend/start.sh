#!/bin/sh
set -e

# Seed and index demo data on startup (no Render Shell needed on free tier)
python scripts/render_bootstrap.py || echo "Bootstrap skipped, starting API anyway..."

exec gunicorn \
  --bind "0.0.0.0:${PORT:-5000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout 30 \
  api.app:app
