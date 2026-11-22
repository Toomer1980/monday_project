#!/usr/bin/env bash
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
