# ==============================================================================
# ORACLE SYSTEMS LLC // NOV 27 DIGITALOCEAN TIER 1 ONE-COMMAND CLOUD CUTOVER
# Usage: .\Run_Nov27_Cloud_Cutover.ps1 -DropletIP <IP> -Domain oraclesystemsllc.com
# ==============================================================================
param(
    [Parameter(Mandatory=$true)][string]$DropletIP,
    [string]$Domain = "oraclesystemsllc.com",
    [string]$SshUser = "root",
    [switch]$PromoteToProduction
)
$ErrorActionPreference = "Continue"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
Set-Location $ProjectDir

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORACLE SYSTEMS LLC // DIGITALOCEAN TIER 1 CUTOVER -> $Domain ($DropletIP)" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan

# 1. Package clean deployment tarball (excludes giant video vault & caches; keeps app, static, tarot_deck, voices, data, .env)
$tarOut = "$ProjectDir\deploy_bundle\sovereigncore_cloud_release.tar.gz"
if (Test-Path $tarOut) { Remove-Item $tarOut -Force }
tar -czf $tarOut sovereign_daemon.py .env Modules static assets/tarot_deck data config deploy_bundle deliverables/Oracle_4D_Creator_Asset_Pack_15.zip 2>$null
Write-Host "[1/4] Packaged cloud release archive -> $tarOut" -ForegroundColor Green

# 2. Upload & unpack on Ubuntu Droplet
ssh -o StrictHostKeyChecking=accept-new "$SshUser@$DropletIP" "mkdir -p /opt/SovereignCore"
scp $tarOut "$SshUser@${DropletIP}:/opt/SovereignCore/release.tar.gz"
ssh "$SshUser@$DropletIP" "cd /opt/SovereignCore && tar -xzf release.tar.gz && chmod +x deploy_bundle/bootstrap_ubuntu.sh && bash deploy_bundle/bootstrap_ubuntu.sh"
Write-Host "[2/4] Bootstrapped Gunicorn + Systemd + Nginx on $DropletIP" -ForegroundColor Green

# 3. Provision free Let's Encrypt HTTPS SSL certificate
ssh "$SshUser@$DropletIP" "certbot --nginx -d $Domain -d www.$Domain --non-interactive --agree-tos -m Toomer1980@gmail.com --redirect"
Write-Host "[3/4] Provisioned HTTPS SSL certificate for https://$Domain" -ForegroundColor Green

# 4. Run live DNS/SSL/Endpoint/Webhook cutover verifier
if (Test-Path "$ProjectDir\verify_do_tier1_cutover.ps1") {
    if ($PromoteToProduction) {
        & "$ProjectDir\verify_do_tier1_cutover.ps1" -Domain $Domain -ExpectedIP $DropletIP -PromoteToProduction
    } else {
        & "$ProjectDir\verify_do_tier1_cutover.ps1" -Domain $Domain -ExpectedIP $DropletIP
    }
}
Write-Host "[4/4] DigitalOcean Tier 1 cutover workflow complete!" -ForegroundColor Green
