# ==============================================================================
# Oracle Systems LLC - morning_briefing.ps1 (Pure ASCII / PS 5.1 Safe)
# 1-Screen Daily Executive Status: Stripe, Payout ETA, Vault, CRM, RAM & Port 8000
# ==============================================================================
param(
    [switch]$RefreshStripe,
    [switch]$TrimRamIfHigh
)

$ErrorActionPreference = "Continue"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
Set-Location $ProjectDir

if ($RefreshStripe -and (Test-Path ".\stripe_live_alerts.ps1")) {
    .\stripe_live_alerts.ps1 | Out-Null
}

# 1. Hardware & Port 8000 Telemetry
$os = Get-CimInstance Win32_OperatingSystem
$totGB  = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$freeGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
$ramPct = [math]::Round((($totGB - $freeGB) / $totGB) * 100.0, 1)

if ($TrimRamIfHigh -and ($ramPct -ge 85.0) -and (Test-Path ".\optimize_ram_and_boot.ps1")) {
    .\optimize_ram_and_boot.ps1 -TrimNow | Out-Null
    $os = Get-CimInstance Win32_OperatingSystem
    $freeGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
    $ramPct = [math]::Round((($totGB - $freeGB) / $totGB) * 100.0, 1)
}

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ("  ORACLE SYSTEMS LLC // MORNING EXECUTIVE BRIEFING ({0})" -f (Get-Date -Format "yyyy-MM-dd HH:mm")) -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan

Write-Host "`n[1] INFRASTRUCTURE & SERVER HEALTH" -ForegroundColor Yellow
Write-Host ("  Laptop RAM : {0}% used ({1} GB free / {2} GB total)" -f $ramPct, $freeGB, $totGB) -ForegroundColor $(if ($ramPct -lt 85) { "Green" } else { "Red" })
foreach ($ep in @("/dashboard", "/store", "/portal")) {
    try {
        $r = Invoke-WebRequest -Uri ("http://127.0.0.1:8000" + $ep) -UseBasicParsing -TimeoutSec 4
        Write-Host ("  Endpoint {0,-12} : HTTP {1} (ONLINE)" -f $ep, $r.StatusCode) -ForegroundColor Green
    } catch {
        Write-Host ("  Endpoint {0,-12} : OFFLINE / ERROR" -f $ep) -ForegroundColor Red
    }
}

# 2. Live Stripe Balance & Payout Countdown
Write-Host "`n[2] LIVE STRIPE TREASURY & PAYOUT COUNTDOWN" -ForegroundColor Yellow
$alertStatePath = Join-Path -Path $ProjectDir -ChildPath "logs\stripe_alert_state.json"
$b10StatePath   = Join-Path -Path $ProjectDir -ChildPath "logs\block10_state.json"

$availUsd = 0.0; $pendUsd = 47.28; $payoutDateStr = "2026-11-27"; $payoutStatus = "scheduled_initial"
if (Test-Path $alertStatePath) {
    try {
        $as = Get-Content $alertStatePath -Raw | ConvertFrom-Json
        $availUsd = [double]$as.available_usd
        $pendUsd  = [double]$as.pending_usd
        if ($as.payout_date)   { $payoutDateStr = $as.payout_date }
        if ($as.payout_status) { $payoutStatus  = $as.payout_status }
    } catch {}
} elseif (Test-Path $b10StatePath) {
    try {
        $bs = Get-Content $b10StatePath -Raw | ConvertFrom-Json
        $availUsd = [double]$bs.stripe_available_usd
        $pendUsd  = [double]$bs.stripe_pending_usd
        if ($bs.next_payout_date) { $payoutDateStr = $bs.next_payout_date }
    } catch {}
}

$daysLeft = ([datetime]::ParseExact($payoutDateStr, "yyyy-MM-dd", $null) - (Get-Date).Date).Days
Write-Host ("  Available Balance : `${0:N2} USD" -f $availUsd) -ForegroundColor Green
Write-Host ("  Pending Balance   : `${0:N2} USD" -f $pendUsd) -ForegroundColor Cyan
Write-Host ("  Next Payout ETA   : {0} ({1} day(s) remaining | Status: {2})" -f $payoutDateStr, $daysLeft, $payoutStatus) -ForegroundColor White

# 3. 52-Week YouTube Vault Progress
Write-Host "`n[3] YOUTUBE 52-WEEK VAULT & UTM CLICKS" -ForegroundColor Yellow
$fullN  = (Get-ChildItem (Join-Path -Path $ProjectDir -ChildPath "Content_Vault_52Weeks") -Filter "*.mp4" -ErrorAction SilentlyContinue).Count
$shortN = (Get-ChildItem (Join-Path -Path $ProjectDir -ChildPath "Content_Vault_Shorts")  -Filter "*.mp4" -ErrorAction SilentlyContinue).Count
$pubFull = 0; $pubShort = 0
$ytState = Join-Path -Path $ProjectDir -ChildPath "data\youtube_publish_state.json"
if (Test-Path $ytState) {
    try {
        $ys = Get-Content $ytState -Raw | ConvertFrom-Json
        $pubFull  = @($ys.published_full).Count
        $pubShort = @($ys.published_shorts).Count
    } catch {}
}
Write-Host ("  Vault On Disk     : {0}/52 Full Videos | {1}/52 Shorts" -f $fullN, $shortN) -ForegroundColor Green
Write-Host ("  Published Count   : {0}/52 Full Videos | {1}/52 Shorts" -f $pubFull, $pubShort) -ForegroundColor Gray

# 4. Pro_Node B2B CRM Follow-Ups
Write-Host "`n[4] PRO_NODE (`$49,999) B2B CRM & OUTREACH QUEUE" -ForegroundColor Yellow
if (Test-Path ".\pronode_crm.ps1") {
    .\pronode_crm.ps1 -Action Summary
    .\pronode_crm.ps1 -Action Due
}
$draftCount = (Get-ChildItem (Join-Path -Path $ProjectDir -ChildPath "reports\outreach") -File -Filter "*.txt" -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '^\d{8}_ID\d+_' }).Count
Write-Host ("  Queued Outreach Drafts Ready to Send : {0}" -f $draftCount) -ForegroundColor Cyan

# 5. Scheduled Automation Status
Write-Host "`n[5] AUTOMATED WINDOWS TASKS" -ForegroundColor Yellow
Get-ScheduledTask -TaskName "OracleSystems_*" -ErrorAction SilentlyContinue | Select-Object TaskName, State | Format-Table -AutoSize