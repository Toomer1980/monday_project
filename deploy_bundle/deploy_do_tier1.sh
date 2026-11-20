#!/usr/bin/env bash
set -euo pipefail

DOMAIN="oraclesystemsllc.com"
REPO_URL="https://github.com/Toomer1980/monday_project.git"
ADMIN_EMAIL="Toomer1980@gmail.com"
APP_DIR="/opt/sovereigncore"

export DEBIAN_FRONTEND=noninteractive
apt-get update && apt-get install -y python3-venv python3-pip nginx certbot python3-certbot-nginx ffmpeg git ufw

id -u oracle &>/dev/null || useradd -m -s /bin/bash oracle
mkdir -p "$APP_DIR/logs" "$APP_DIR/data" "$APP_DIR/static/deliverables" "$APP_DIR/audit_inbox"

if [ ! -d "$APP_DIR/.git" ]; then
    git clone "$REPO_URL" "$APP_DIR"
else
    git -C "$APP_DIR" pull origin main
fi

if [ ! -f "$APP_DIR/.env" ]; then
    cp /tmp/oracle_deploy/.env.production.template "$APP_DIR/.env"
    chmod 600 "$APP_DIR/.env"
fi

python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt" gunicorn

chown -R oracle:oracle "$APP_DIR"

cp /tmp/oracle_deploy/sovereigncore.service /etc/systemd/system/sovereigncore.service
cp /tmp/oracle_deploy/nginx_sovereigncore.conf /etc/nginx/sites-available/sovereigncore
ln -sf /etc/nginx/sites-available/sovereigncore /etc/nginx/sites-enabled/sovereigncore
rm -f /etc/nginx/sites-enabled/default

ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

nginx -t && systemctl reload nginx
certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos -m "$ADMIN_EMAIL" --redirect || echo "[WARN] Certbot skipped - point DNS A record for $DOMAIN to this Droplet IP first, then re-run certbot."

systemctl daemon-reload
systemctl enable --now sovereigncore
systemctl status sovereigncore --no-pager