import os

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
BUNDLE = os.path.join(PDIR, "deploy_bundle")
os.makedirs(BUNDLE, exist_ok=True)

CLOUD_WATCHDOG_SH = """#!/usr/bin/env bash
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
"""

GUARDED_AUTODEPLOY_SH = """#!/usr/bin/env bash
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
"""

INSTALL_247_SH = """#!/usr/bin/env bash
set -euo pipefail
APP_DIR="/opt/SovereignCore"
chmod +x "$APP_DIR/deploy_bundle/cloud_watchdog.sh" "$APP_DIR/deploy_bundle/guarded_autodeploy.sh"

cat >/etc/systemd/system/oracle-swarm-watchdog.service <<'EOF'
[Unit]
Description=Oracle Systems 24/7 Self-Healing & Learning Swarm Tick
After=network.target sovereigncore.service

[Service]
Type=oneshot
WorkingDirectory=/opt/SovereignCore
ExecStart=/opt/SovereignCore/deploy_bundle/cloud_watchdog.sh
EOF

cat >/etc/systemd/system/oracle-swarm-watchdog.timer <<'EOF'
[Unit]
Description=Run Oracle Systems Swarm Watchdog every 15 minutes (24/7/365)

[Timer]
OnBootSec=2min
OnUnitActiveSec=15min
Unit=oracle-swarm-watchdog.service

[Install]
WantedBy=timers.target
EOF

cat >/etc/systemd/system/oracle-guarded-autodeploy.service <<'EOF'
[Unit]
Description=Oracle Systems Guarded GitHub Auto-Deploy (with Auto-Rollback)
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/opt/SovereignCore
ExecStart=/opt/SovereignCore/deploy_bundle/guarded_autodeploy.sh
EOF

cat >/etc/systemd/system/oracle-guarded-autodeploy.timer <<'EOF'
[Unit]
Description=Check GitHub main for verified updates every 30 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=30min
Unit=oracle-guarded-autodeploy.service

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable --now oracle-swarm-watchdog.timer oracle-guarded-autodeploy.timer
echo "[24/7/365 CLOUD SWARM ACTIVE] Independent of laptop power or hardware!"
"""

open(os.path.join(BUNDLE, "cloud_watchdog.sh"), "w", encoding="utf-8", newline="\n").write(CLOUD_WATCHDOG_SH)
open(os.path.join(BUNDLE, "guarded_autodeploy.sh"), "w", encoding="utf-8", newline="\n").write(GUARDED_AUTODEPLOY_SH)
open(os.path.join(BUNDLE, "install_247_cloud_swarm.sh"), "w", encoding="utf-8", newline="\n").write(INSTALL_247_SH)
print(f"[24/7 CLOUD SWARM PACKAGER PASS] Wrote cloud_watchdog.sh, guarded_autodeploy.sh & install_247_cloud_swarm.sh -> {BUNDLE}")
