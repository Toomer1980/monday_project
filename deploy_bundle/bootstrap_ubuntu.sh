#!/usr/bin/env bash
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
