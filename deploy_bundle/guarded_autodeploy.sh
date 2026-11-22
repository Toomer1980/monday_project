#!/usr/bin/env bash
set -euo pipefail
APP_DIR="/opt/SovereignCore"
cd "$APP_DIR"

# Safe, test-gated auto-update from GitHub main with automatic rollback on failure
PREV_SHA=$(git rev-parse HEAD)
git fetch origin main --quiet
REMOTE_SHA=$(git rev-parse origin/main)
if [ "$PREV_SHA" = "$REMOTE_SHA" ]; then
  exit 0
fi

git pull --ff-only origin main
if .venv/bin/python -m py_compile sovereign_daemon.py Modules/*.py; then
  systemctl restart sovereigncore.service
  sleep 3
  if curl -fsS --max-time 6 http://127.0.0.1:8000/api/exec-telemetry >/dev/null; then
    echo "[$(date -u)] [AUTO-DEPLOY PASS] Promoted $REMOTE_SHA cleanly."
    exit 0
  fi
fi

echo "[$(date -u)] [AUTO-ROLLBACK] Health check failed; reverting to $PREV_SHA!"
git reset --hard "$PREV_SHA"
systemctl restart sovereigncore.service
