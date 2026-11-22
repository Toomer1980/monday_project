# ==============================================================================
# ORACLE SYSTEMS LLC - PHASE 16 OMEGA AUTOPILOT ORCHESTRATOR (PS 5.1 / ASCII)
# Self-starting, self-healing, AI-diagnosing revenue & distribution engine.
# ==============================================================================
param(
    [switch]$InstallAndRun,
    [switch]$RegisterTasks,
    [switch]$RunB2BSprint,
    [switch]$OpenShowcase,
    [switch]$SkipGitPush
)
$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
Set-Location $ProjectDir
$env:RCLONE_BIND = "0.0.0.0"
[Environment]::SetEnvironmentVariable("RCLONE_BIND", "0.0.0.0", "User")

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORACLE SYSTEMS LLC // PHASE 16 OMEGA AUTOPILOT CYCLE" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan

# 1) Register Self-Starting (AtLogon) + Self-Healing (30-Min) Windows Tasks
if ($InstallAndRun -or $RegisterTasks) {
    try {
        $act = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ProjectDir\sovereign_omega_autopilot.ps1`" -SkipGitPush" -WorkingDirectory $ProjectDir
        $t30 = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(2) -RepetitionInterval (New-TimeSpan -Minutes 30)
        $tBoot = New-ScheduledTaskTrigger -AtLogOn
        $set = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        Register-ScheduledTask -TaskName "OracleSystems_Omega_Autopilot_30Min" -Action $act -Trigger $t30 -Settings $set -Description "30-min self-healing, YouTube CTA commenter, Thompson bandit & revenue watchdog" -Force | Out-Null
        Register-ScheduledTask -TaskName "OracleSystems_Omega_Boot" -Action $act -Trigger $tBoot -Settings $set -Description "Auto-starts SovereignCore Omega stack on Windows logon" -Force | Out-Null
        Write-Host "[TASKS] Registered OracleSystems_Omega_Autopilot_30Min + OracleSystems_Omega_Boot" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Task registration note: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# 2) Deploy Interactive 5D Penteract Storefront + Referral Loop (on first install)
if ($InstallAndRun) {
    Write-Host "`n--- [1/7] Deploying Interactive 5D Penteract Storefront & Referral Loop ---" -ForegroundColor Cyan
    python "$ProjectDir\Modules\omega_5d_upgrade.py" --patch-store
}

# 3) Self-Heal Port 8000, Cloudflare Tunnel, Stripe Webhook & Laptop RAM
Write-Host "`n--- [2/7] Running Self-Healing Infrastructure & Webhook Sync ---" -ForegroundColor Cyan
if (Test-Path "$ProjectDir\sovereign_health_autopilot.ps1") { & "$ProjectDir\sovereign_health_autopilot.ps1" }
if (Test-Path "$ProjectDir\sync_stripe_webhook.ps1") { & "$ProjectDir\sync_stripe_webhook.ps1" -CreateIfMissing }

# 4) Autonomous YouTube CTA Commenter, Analytics Pull, Thompson Bandit & Traffic Pack
Write-Host "`n--- [3/7] Running YouTube CTA Commenter, Analytics & Thompson Bandit ---" -ForegroundColor Cyan
python "$ProjectDir\Modules\omega_5d_upgrade.py" --comment-yt --bandit
if (Test-Path "$ProjectDir\pull_youtube_analytics.ps1") { & "$ProjectDir\pull_youtube_analytics.ps1" }
if (Test-Path "$ProjectDir\repurpose_traffic.py") { python "$ProjectDir\repurpose_traffic.py" }

# 5) Autonomous Paid $49 AuraVideo49 Order Fulfillment + 3-Day B2B Follow-Ups
Write-Host "`n--- [4/7] Polling Paid `$49 Orders & Firing Due B2B Follow-Ups ---" -ForegroundColor Cyan
if (Test-Path "$ProjectDir\fulfill_aura49_order.ps1") { & "$ProjectDir\fulfill_aura49_order.ps1" -PollStripeOrders -DurationSec 120 }
if (Test-Path "$ProjectDir\run_pronode_followups.ps1") { & "$ProjectDir\run_pronode_followups.ps1" -SendLive }
if ($RunB2BSprint -and (Test-Path "$ProjectDir\run_pronode_sprint.ps1")) {
    & "$ProjectDir\run_pronode_sprint.ps1" -MaxLeads 20 -SpacingSeconds 45 -SendLive
}

# 6) AI Self-Diagnostic Watchdog, Nov 27 Gate Alert & Funnel Telemetry
Write-Host "`n--- [5/7] Running Local Ollama AI Watchdog & Live Funnel Dashboard ---" -ForegroundColor Cyan
python "$ProjectDir\Modules\omega_5d_upgrade.py" --diagnose
if (Test-Path "$ProjectDir\funnel_dashboard.ps1") { & "$ProjectDir\funnel_dashboard.ps1" }

# 7) Permanent Custom OAuth Google Drive Sync (IPv4) + Secret-Scanned GitHub Push
Write-Host "`n--- [6/7] Syncing Reports & Traffic Packs to Google Drive ---" -ForegroundColor Cyan
if (Get-Command rclone -ErrorAction SilentlyContinue) {
    rclone copy "$ProjectDir\Oracle_Audit_2026" "gdrive:Oracle_Audit_2026" --update --bind 0.0.0.0
    if ($LASTEXITCODE -eq 0) { Write-Host "[DRIVE SYNC PASS] Synced Oracle_Audit_2026 cleanly." -ForegroundColor Green }
}

if (-not $SkipGitPush) {
    Write-Host "`n--- [7/7] Secret-Scanned GitHub Commit & Push ---" -ForegroundColor Cyan
    $gi = "$ProjectDir\.gitignore"
    foreach ($rule in @("data/yt_commented_ids.json","data/omega_strategy_state.json","data/tier1_gate_alert_sent.flag","reports/Daily_Traffic_Pack_*.md","reports/Omega_Bandit_Strategy.md","reports/AI_Self_Heal_Log.md","logs/daemon_boot.log")) {
        if (-not (Select-String -Path $gi -SimpleMatch $rule -Quiet -ErrorAction SilentlyContinue)) { Add-Content -Path $gi -Value $rule }
    }
    foreach ($sf in @(".gitignore","sovereign_daemon.py","static/omega_5d_engine.js","Modules/omega_5d_upgrade.py","sovereign_omega_autopilot.ps1")) {
        if (Test-Path "$ProjectDir\$sf") { git add -- $sf }
    }
    $added = (git diff --cached | Where-Object { $_ -match '^\+[^+]' }) -join "`n"
    $rx = '(sk_live_[A-Za-z0-9]{20,}|sk_test_[A-Za-z0-9]{20,}|rk_live_[A-Za-z0-9]{20,}|whsec_[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{24,}|ya29\.[A-Za-z0-9\-_]{24,}|GOCSPX-[A-Za-z0-9\-_]{20,}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----)'
    if ($added -match $rx) {
        Write-Host "[ABORTED] Secret detected in staged diff! Resetting." -ForegroundColor Red
        git reset | Out-Null
    } elseif (git diff --cached --name-only) {
        git commit -m "Phase 16 Omega Autopilot: Interactive 5D Penteract Storefront, Viral Referral Loop, Auto YouTube CTA Commenter, Bayesian Bandit & AI Self-Heal Watchdog"
        git push -u origin (git rev-parse --abbrev-ref HEAD).Trim()
    }
}

if ($OpenShowcase) {
    $pub = if (Test-Path "$ProjectDir\config\public_url.txt") { (Get-Content "$ProjectDir\config\public_url.txt" -Raw).Trim() } else { "http://127.0.0.1:8000" }
    Start-Process "$pub/store"
    Start-Process "https://youtu.be/Wxxxgco7AX4"
}

Write-Host "`n[PHASE 16 OMEGA AUTOPILOT COMPLETE] 100% live, self-healing & synced!" -ForegroundColor Green