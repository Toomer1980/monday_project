import os

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
OUT_DIR = os.path.join(PDIR, "deploy_bundle")
os.makedirs(OUT_DIR, exist_ok=True)

SYSTEMD_SVC = """[Unit]
Description=Oracle Systems LLC SovereignCore Production Daemon
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/SovereignCore
Environment=OPENBLAS_NUM_THREADS=1
Environment=OMP_NUM_THREADS=1
ExecStart=/opt/SovereignCore/.venv/bin/gunicorn --workers 2 --threads 4 --bind 127.0.0.1:8000 sovereign_daemon:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""

NGINX_CONF = """server {
    listen 80;
    server_name oraclesystemsllc.com www.oraclesystemsllc.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""

BOOTSTRAP_SH = """#!/usr/bin/env bash
set -euo pipefail
apt-get update -y && apt-get install -y python3-venv python3-pip nginx certbot python3-certbot-nginx ffmpeg
cd /opt/SovereignCore
python3 -m venv .venv
.venv/bin/pip install --upgrade pip gunicorn flask stripe google-api-python-client google-auth-oauthlib edge-tts pillow numpy fpdf2
cp deploy_bundle/systemd_sovereign.service /etc/systemd/system/sovereigncore.service
cp deploy_bundle/nginx_oraclesystemsllc.conf /etc/nginx/sites-available/oraclesystemsllc
ln -sf /etc/nginx/sites-available/oraclesystemsllc /etc/nginx/sites-enabled/oraclesystemsllc
rm -f /etc/nginx/sites-enabled/default
systemctl daemon-reload && systemctl enable --now sovereigncore && systemctl reload nginx
echo "[BOOTSTRAPPED] Run: certbot --nginx -d oraclesystemsllc.com -d www.oraclesystemsllc.com --non-interactive --agree-tos -m Toomer1980@gmail.com"
"""

open(os.path.join(OUT_DIR, "systemd_sovereign.service"), "w", encoding="utf-8", newline="\n").write(SYSTEMD_SVC)
open(os.path.join(OUT_DIR, "nginx_oraclesystemsllc.conf"), "w", encoding="utf-8", newline="\n").write(NGINX_CONF)
open(os.path.join(OUT_DIR, "bootstrap_ubuntu.sh"), "w", encoding="utf-8", newline="\n").write(BOOTSTRAP_SH)
print(f"[PHASE 40 PASS] Compiled Nov 27 DigitalOcean Tier 1 Linux deployment bundle -> {OUT_DIR}")
