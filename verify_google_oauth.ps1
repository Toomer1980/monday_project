param(
    [switch]$AutoImportFromDownloads,
    [switch]$TestLiveYouTube,
    [string]$RemoteName = "gdrive"
)
$ErrorActionPreference = "Continue"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$TargetJson = "$ProjectDir\config\youtube_client_secret.json"
$DlDir      = Join-Path -Path $env:USERPROFILE -ChildPath "Downloads"

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORACLE SYSTEMS LLC // GOOGLE CLOUD OAUTH VERIFIER (YOUTUBE + RCLONE)" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan

# Check Downloads folder for newly downloaded Google Cloud Desktop OAuth JSON
if (-not (Test-Path $TargetJson) -and (Test-Path $DlDir)) {
    $found = Get-ChildItem -Path $DlDir -Filter "client_secret_*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($found) {
        if ($AutoImportFromDownloads) {
            Copy-Item -Path $found.FullName -Destination $TargetJson -Force
            Write-Host "[AUTO-IMPORTED] Copied $($found.Name) -> config\youtube_client_secret.json" -ForegroundColor Green
        } else {
            Write-Host "[DETECTED IN DOWNLOADS] Found $($found.Name)!" -ForegroundColor Yellow
            Write-Host "  -> Run .\verify_google_oauth.ps1 -AutoImportFromDownloads -TestLiveYouTube to install & connect it!" -ForegroundColor Cyan
        }
    }
}

Write-Host "`n--- [Gate 1/2] YouTube Data API v3 OAuth JSON ---" -ForegroundColor Cyan
$modeArg = if ($TestLiveYouTube) { "LIVE" } else { "CHECK" }
python "$ProjectDir\Modules\verify_youtube_oauth.py" $ProjectDir $modeArg

Write-Host "`n--- [Gate 2/2] rclone Google Drive Custom OAuth Client ---" -ForegroundColor Cyan
$rConf = Join-Path -Path $env:APPDATA -ChildPath "rclone\rclone.conf"
if (-not (Test-Path $rConf)) {
    Write-Host "[MISSING] rclone config not found at $rConf. Run .\setup_gdrive_sync.ps1 -ConfigureNow" -ForegroundColor Yellow
} else {
    $raw = Get-Content $rConf -Raw -ErrorAction SilentlyContinue
    $hasCustomId  = ($raw -match '(?m)^client_id\s*=\s*.+\.apps\.googleusercontent\.com')
    $hasCustomSec = ($raw -match '(?m)^client_secret\s*=\s*\S{10,}')
    $hasToken     = ($raw -match '(?m)^token\s*=\s*\{')
    if ($hasCustomId -and $hasCustomSec) {
        Write-Host "[PASS] Custom Google Cloud OAuth client_id & client_secret active in rclone.conf" -ForegroundColor Green
    } else {
        Write-Host "[ACTION NEEDED] rclone is still using the expiring shared client_id (CustomID=$hasCustomId, CustomSecret=$hasCustomSec, Token=$hasToken)" -ForegroundColor Yellow
        Write-Host "  -> Fix: .\update_rclone_oauth.ps1 -ClientId `"YOUR_ID.apps.googleusercontent.com`" -ClientSecret `"YOUR_CLIENT_SECRET`"" -ForegroundColor Cyan
    }

    $rcCmd = Get-Command rclone -ErrorAction SilentlyContinue
    if ($rcCmd) {
        Write-Host "Testing live Drive listing (${RemoteName}:Oracle_Audit_2026)..." -ForegroundColor Gray
        $lsOut = & $rcCmd.Source lsf "${RemoteName}:Oracle_Audit_2026" --max-depth 1 2>&1
        if ($LASTEXITCODE -eq 0) {
            $cnt = @($lsOut | Where-Object { $_ -and ($_ -notmatch '^NOTICE:') }).Count
            Write-Host "[LIVE PASS] Connected to ${RemoteName}:Oracle_Audit_2026 ($cnt top-level item(s) accessible)" -ForegroundColor Green
        } else {
            Write-Host "[WARN] Drive listing returned exit ${LASTEXITCODE}: $($lsOut -join ' ')" -ForegroundColor Yellow
        }
    }
}