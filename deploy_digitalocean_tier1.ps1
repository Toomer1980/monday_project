# ==============================================================================
# Oracle Systems LLC - deploy_digitalocean_tier1.ps1 (Pure ASCII / PS 5.1 Safe)
# Packages DigitalOcean Tier 1 ($34.80/mo) configs, syncs deliverables to Spaces
# CDN via rclone, and bootstraps an Ubuntu 24.04 Droplet over native SSH/SCP.
#
# Examples:
#   .\deploy_digitalocean_tier1.ps1 -Domain "oraclesystemsllc.com" -PackageOnly
#   .\deploy_digitalocean_tier1.ps1 -DropletIP "164.92.x.x" -Domain "oraclesystemsllc.com" -BootstrapRemote
#   .\deploy_digitalocean_tier1.ps1 -UploadSpaces -SpacesRemote "dospaces:oracle-deliverables"
# ==============================================================================
param(
    [string]$DropletIP = "",
    [string]$SshUser = "root",
    [string]$SshKeyPath = "",
    [string]$Domain = "oraclesystemsllc.com",
    [string]$RepoUrl = "https://github.com/Toomer1980/monday_project.git",
    [string]$AdminEmail = "Toomer1980@gmail.com",
    [string]$SpacesRemote = "dospaces:oracle-deliverables",
    [switch]$PackageOnly,
    [switch]$UploadSpaces,
    [switch]$BootstrapRemote
)

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$BundleDir  = Join-Path $ProjectDir "deploy_bundle"
$Utf8NoBom  = New-Object System.Text.UTF8Encoding($false)
New-Item -ItemType Directory -Path $BundleDir -Force | Out-Null

Write-Host "=== DIGITALOCEAN TIER 1 (`$34.80/MO) DEPLOYMENT PACKAGER ===" -ForegroundColor Cyan
Write-Host "Target Domain: $Domain | Repo: $RepoUrl" -ForegroundColor Gray

# 1. Ensure requirements.txt exists for clean pip install on Ubuntu
$ReqPath = Join-Path $ProjectDir "requirements.txt"
if (-not (Test-Path $ReqPath)) {
    $ReqBody = @"
flask>=3.0.0
flask-socketio>=5.3.0
requests>=2.31.0
stripe>=10.0.0
gunicorn>=22.0.0
rich>=13.7.0
"@
    [System.IO.File]::WriteAllText($ReqPath, $ReqBody, $Utf8NoBom)
    Write-Host "[CREATED] requirements.txt in project root" -ForegroundColor Green
}

# 2. Generate systemd service (LF line endings for Linux)
$SystemdUnit = @"
[Unit]
Description=Oracle Systems LLC - SovereignCore Production Server
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=oracle
Group=oracle
WorkingDirectory=/opt/sovereigncore
EnvironmentFile=/opt/sovereigncore/.env
ExecStart=/opt/sovereigncore/venv/bin/gunicorn --workers 3 --threads 4 --bind 127.0.0.1:8000 --timeout 120 --access-logfile /opt/sovereigncore/logs/access.log --error-logfile /opt/sovereigncore/logs/error.log sovereign_daemon:app
Restart=always
RestartSec=5
MemoryMax=3G

[Install]
WantedBy=multi-user.target
"@ -replace "`r`n", "`n"
[System.IO.File]::WriteAllText((Join-Path $BundleDir "sovereigncore.service"), $SystemdUnit, $Utf8NoBom)

# 3. Generate Nginx reverse proxy config (LF line endings)
$NginxConf = @"
server {
    listen 80;
    server_name $Domain www.$Domain;

    client_max_body_size 250M;

    location /static/ {
        alias /opt/sovereigncore/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host `$host;
        proxy_set_header X-Real-IP `$remote_addr;
        proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto `$scheme;
        proxy_read_timeout 180s;
    }
}
"@ -replace "`r`n", "`n"
[System.IO.File]::WriteAllText((Join-Path $BundleDir "nginx_sovereigncore.conf"), $NginxConf, $Utf8NoBom)

# 4. Generate .env.production.template (never contains live secrets)
$EnvProdTmpl = @"
FLASK_ENV=production
PUBLIC_BASE_URL=https://$Domain
PORT=8000
STRIPE_SECRET_KEY=rk_live_REPLACE_ON_DROPLET
STRIPE_WEBHOOK_SECRET=whsec_REPLACE_ON_DROPLET
SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
SPACES_BUCKET=oracle-deliverables
"@ -replace "`r`n", "`n"
[System.IO.File]::WriteAllText((Join-Path $BundleDir ".env.production.template"), $EnvProdTmpl, $Utf8NoBom)

# 5. Generate Ubuntu 24.04 one-shot bootstrap script (LF line endings)
$BootstrapSh = @"
#!/usr/bin/env bash
set -euo pipefail

DOMAIN="$Domain"
REPO_URL="$RepoUrl"
ADMIN_EMAIL="$AdminEmail"
APP_DIR="/opt/sovereigncore"

export DEBIAN_FRONTEND=noninteractive
apt-get update && apt-get install -y python3-venv python3-pip nginx certbot python3-certbot-nginx ffmpeg git ufw

id -u oracle &>/dev/null || useradd -m -s /bin/bash oracle
mkdir -p "`$APP_DIR/logs" "`$APP_DIR/data" "`$APP_DIR/static/deliverables" "`$APP_DIR/audit_inbox"

if [ ! -d "`$APP_DIR/.git" ]; then
    git clone "`$REPO_URL" "`$APP_DIR"
else
    git -C "`$APP_DIR" pull origin main
fi

if [ ! -f "`$APP_DIR/.env" ]; then
    cp /tmp/oracle_deploy/.env.production.template "`$APP_DIR/.env"
    chmod 600 "`$APP_DIR/.env"
fi

python3 -m venv "`$APP_DIR/venv"
"`$APP_DIR/venv/bin/pip" install --upgrade pip
"`$APP_DIR/venv/bin/pip" install -r "`$APP_DIR/requirements.txt" gunicorn

chown -R oracle:oracle "`$APP_DIR"

cp /tmp/oracle_deploy/sovereigncore.service /etc/systemd/system/sovereigncore.service
cp /tmp/oracle_deploy/nginx_sovereigncore.conf /etc/nginx/sites-available/sovereigncore
ln -sf /etc/nginx/sites-available/sovereigncore /etc/nginx/sites-enabled/sovereigncore
rm -f /etc/nginx/sites-enabled/default

ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

nginx -t && systemctl reload nginx
certbot --nginx -d "`$DOMAIN" -d "www.`$DOMAIN" --non-interactive --agree-tos -m "`$ADMIN_EMAIL" --redirect || echo "[WARN] Certbot skipped - point DNS A record for `$DOMAIN to this Droplet IP first, then re-run certbot."

systemctl daemon-reload
systemctl enable --now sovereigncore
systemctl status sovereigncore --no-pager
"@ -replace "`r`n", "`n"
[System.IO.File]::WriteAllText((Join-Path $BundleDir "deploy_do_tier1.sh"), $BootstrapSh, $Utf8NoBom)

Write-Host "[PASS] Packaged 4 Linux deployment files into $BundleDir" -ForegroundColor Green
Get-ChildItem $BundleDir | Select-Object Name, Length | Format-Table -AutoSize

# Optional Step A: Sync static deliverables to DigitalOcean Spaces via rclone
if ($UploadSpaces) {
    $rcloneCmd = Get-Command rclone -ErrorAction SilentlyContinue
    if (-not $rcloneCmd) { throw "rclone not found in PATH." }
    $remoteRoot = ($SpacesRemote.Split(":")[0]) + ":"
    $remotes = & $rcloneCmd.Source listremotes 2>$null
    if ($remotes -notcontains $remoteRoot) {
        Write-Host "[ACTION NEEDED] Configure DigitalOcean Spaces remote once:" -ForegroundColor Yellow
        Write-Host "  rclone config create dospaces s3 provider DigitalOcean endpoint nyc3.digitaloceanspaces.com access_key_id YOUR_KEY secret_access_key YOUR_SECRET" -ForegroundColor Cyan
    } else {
        $delivDir = Join-Path $ProjectDir "static\deliverables"
        Write-Host "Uploading deliverables from $delivDir to $SpacesRemote..." -ForegroundColor Cyan
        & $rcloneCmd.Source copy $delivDir $SpacesRemote --update --transfers 2
        if ($LASTEXITCODE -eq 0) { Write-Host "[PASS] Deliverables synced to DigitalOcean Spaces!" -ForegroundColor Green }
    }
}

# Optional Step B: Push bundle and bootstrap remote Ubuntu 24.04 Droplet via SSH/SCP
if ($BootstrapRemote) {
    if (-not $DropletIP -or ($DropletIP -notmatch '^\d{1,3}(\.\d{1,3}){3}$')) { throw "Invalid -DropletIP '$DropletIP'. Provide a real DigitalOcean IPv4 address (e.g. 164.92.100.25)." }
    if (-not (Get-Command ssh -ErrorAction SilentlyContinue)) { throw "OpenSSH client (ssh/scp) not found on Windows." }

    $sshOpts = @("-o", "StrictHostKeyChecking=accept-new")
    if ($SshKeyPath -and (Test-Path $SshKeyPath)) { $sshOpts += @("-i", $SshKeyPath) }

    Write-Host "Uploading deployment bundle to ${SshUser}@${DropletIP}:/tmp/oracle_deploy ..." -ForegroundColor Cyan
    & ssh @sshOpts "${SshUser}@${DropletIP}" "mkdir -p /tmp/oracle_deploy"
    & scp @sshOpts (Join-Path $BundleDir "*") "${SshUser}@${DropletIP}:/tmp/oracle_deploy/"; if ($LASTEXITCODE -ne 0) { throw "SCP upload failed (exit $LASTEXITCODE)." }

    Write-Host "Running deploy_do_tier1.sh on $DropletIP ..." -ForegroundColor Cyan
    & ssh @sshOpts "${SshUser}@${DropletIP}" "chmod +x /tmp/oracle_deploy/deploy_do_tier1.sh && bash /tmp/oracle_deploy/deploy_do_tier1.sh"; if ($LASTEXITCODE -ne 0) { throw "Remote bootstrap failed (exit $LASTEXITCODE)." }
    Write-Host "[PASS] DigitalOcean Tier 1 Droplet bootstrap finished!" -ForegroundColor Green
    Write-Host "Next: SSH into $DropletIP, set live keys in /opt/sovereigncore/.env, then run: systemctl restart sovereigncore" -ForegroundColor Yellow
} elseif (-not $PackageOnly) {
    Write-Host "Ready to deploy! Once your `$24/mo Droplet is created, run:" -ForegroundColor Cyan
    Write-Host "  .\deploy_digitalocean_tier1.ps1 -DropletIP <DROPLET_IP> -Domain $Domain -BootstrapRemote" -ForegroundColor White
}