#!/usr/bin/env bash
set -euo pipefail
APP_DIR="/opt/SovereignCore"
cd "$APP_DIR"

# 1. Verify HTTP 200 on local Gunicorn; auto-restart systemd unit if unhealthy
if ! curl -fsS --max-time 6 http://127.0.0.1:8000/api/exec-telemetry >/dev/null; then
  echo "[$(date -u)] [SELF-HEAL] Restarting sovereigncore.service..."
  systemctl restart sovereigncore.service
  sleep 3
fi

# 2. Run closed-loop learning & revenue velocity engines
.venv/bin/python Modules/autonomous_learning_swarm.py || true
.venv/bin/python Modules/revenue_velocity_engine.py || true
.venv/bin/python Modules/multiplatform_publisher.py || true
