# ==============================================================================
# Oracle Systems LLC - update_rclone_oauth.ps1 (Pure ASCII / PS 5.1 Safe)
# Guides you through creating your own Google Cloud OAuth Desktop client_id +
# client_secret, updates rclone remote 'gdrive' securely, reconnects OAuth,
# and verifies live sync with Oracle_Audit_2026 so Drive sync never expires.
#
# Examples:
#   .\update_rclone_oauth.ps1 -ShowGuideOnly
#   .\update_rclone_oauth.ps1 -ClientId "xxxx.apps.googleusercontent.com" -ClientSecret "GOCSPX-xxxx"
# ==============================================================================
param(
    [string]$RemoteName = "gdrive",
    [string]$ClientId = "",
    [string]$ClientSecret = "",
    [switch]$ShowGuideOnly
)

$ErrorActionPreference = "Stop"

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  CUSTOM GOOGLE CLOUD OAUTH CLIENT SETUP FOR RCLONE (PERMANENT SYNC)" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "1. Open https://console.cloud.google.com/ and create/select project 'OracleSystems-DriveSync'."
Write-Host "2. Go to APIs & Services -> Library -> search 'Google Drive API' -> click Enable."
Write-Host "3. Go to Google Auth Platform (OAuth consent screen) -> Audience -> External -> add your Gmail under Test Users."
Write-Host "4. Go to Clients -> Create Client -> Application type: 'Desktop app' -> Name: 'OracleRclone'."
Write-Host "5. Copy the Client ID (ends in .apps.googleusercontent.com) and Client Secret (starts with GOCSPX-)."
Write-Host "6. Also revoke any previously exposed rclone token at https://myaccount.google.com/permissions."
Write-Host "------------------------------------------------------------------------" -ForegroundColor DarkGray

if ($ShowGuideOnly) {
    Write-Host "Run this once you have your credentials:" -ForegroundColor Cyan
    Write-Host "  .\update_rclone_oauth.ps1 -ClientId `"YOUR_ID.apps.googleusercontent.com`" -ClientSecret `"GOCSPX-YOUR_SECRET`"" -ForegroundColor White
    exit 0
}

$rcloneCmd = Get-Command rclone -ErrorAction SilentlyContinue
if (-not $rcloneCmd) { throw "rclone is not installed. Run .\setup_gdrive_sync.ps1 first." }
$rcloneExe = $rcloneCmd.Source

if (-not $ClientId) {
    $ClientId = (Read-Host "Paste your Google OAuth Client ID (.apps.googleusercontent.com)").Trim()
}
if (-not $ClientSecret) {
    $sec = Read-Host "Paste your Google OAuth Client Secret (input hidden)" -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
    try { $ClientSecret = [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr).Trim() }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
}

if (-not $ClientId -or -not $ClientSecret) {
    throw "Both ClientId and ClientSecret are required."
}

$remotes = & $rcloneExe listremotes 2>$null
if ($remotes -contains "${RemoteName}:") {
    Write-Host "Updating existing rclone remote '${RemoteName}' with your custom OAuth client..." -ForegroundColor Cyan
    & $rcloneExe config update $RemoteName client_id $ClientId client_secret $ClientSecret scope drive
    Write-Host "Re-authorizing OAuth token in your browser..." -ForegroundColor Cyan
    & $rcloneExe config reconnect "${RemoteName}:"
} else {
    Write-Host "Creating new rclone remote '${RemoteName}' with your custom OAuth client..." -ForegroundColor Cyan
    & $rcloneExe config create $RemoteName drive client_id $ClientId client_secret $ClientSecret scope drive
}

if ($LASTEXITCODE -ne 0) { throw "rclone OAuth update failed (exit $LASTEXITCODE)." }

Write-Host "`nVerifying live Google Drive connection to ${RemoteName}:Oracle_Audit_2026 ..." -ForegroundColor Cyan
& $rcloneExe lsd "${RemoteName}:Oracle_Audit_2026"
if ($LASTEXITCODE -eq 0) {
    Write-Host "[PASS] Custom Google Cloud OAuth client active! Your Oracle_Audit_2026 sync will not expire." -ForegroundColor Green
} else {
    Write-Host "[WARN] Remote updated, but could not list Oracle_Audit_2026 yet. Check folder name in Google Drive." -ForegroundColor Yellow
}