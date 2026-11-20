# ==============================================================================
# Oracle Systems LLC - oracle_hub.ps1 (v11 Executive Complete / Pure ASCII PS 5.1)
# Master Terminal Command Center for SovereignCore Automation Suite
# ==============================================================================
$ErrorActionPreference = "Continue"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
Set-Location $ProjectDir

function Show-Header {
    Clear-Host
    $os = Get-CimInstance Win32_OperatingSystem
    $totGB  = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
    $freeGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
    $ramPct = [math]::Round((($totGB - $freeGB) / $totGB) * 100.0, 1)
    $portUp = [bool](Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue)
    $f4d = (Get-ChildItem "$ProjectDir\Content_Vault_4D_Full"   -Filter "*_4D_MAX.mp4" -ErrorAction SilentlyContinue).Count
    $s4d = (Get-ChildItem "$ProjectDir\Content_Vault_4D_Shorts" -Filter "*_4D_MAX.mp4" -ErrorAction SilentlyContinue).Count
    $t3d = (Get-ChildItem "$ProjectDir\Content_Vault_4D_Thumbnails" -Filter "*_3D_Thumb.jpg" -ErrorAction SilentlyContinue).Count
    $pubUrl = if (Test-Path "$ProjectDir\config\public_url.txt") { (Get-Content "$ProjectDir\config\public_url.txt" -Raw).Trim() } else { "LOCAL ONLY" }

    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host "  ORACLE SYSTEMS LLC // SOVEREIGNCORE EXECUTIVE HUB (v11 COMPLETE)" -ForegroundColor White
    Write-Host "============================================================================" -ForegroundColor Cyan
    Write-Host ("  Port 8000: {0,-7} | RAM: {1}% ({2}GB free) | 4D Vault: {3}/52F {4}/52S {5}T" -f $(if ($portUp) { "ONLINE" } else { "OFFLINE" }), $ramPct, $freeGB, $f4d, $s4d, $t3d) -ForegroundColor $(if ($portUp -and $ramPct -lt 85) { "Green" } else { "Yellow" })
    Write-Host ("  Public Funnel: {0}" -f $pubUrl) -ForegroundColor Cyan
    Write-Host "----------------------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host "  [1] Block 10 Treasury Audit + Live Stripe API Poll + Google Drive Sync"
    Write-Host "  [2] Live Conversion Funnel Dashboard (Stripe + YouTube + UTM + CRM)"
    Write-Host "  [3] Pro_Node (`$49,999) B2B CRM (Summary / List / Add / Due / Invoice)"
    Write-Host "  [4] Pro_Node B2B Lead Builder, ICP Scorer & CSV Formatter"
    Write-Host "  [5] Pro_Node Weekly 20-Lead Throttled Outreach Sprint (DryRun / Live)"
    Write-Host "  [6] Run Stripe Webhook & End-to-End ZIP/MP4 Fulfillment Self-Test"
    Write-Host "  [7] Self-Healing Health Autopilot (Port 8000, Tunnel, RAM, Tasks, Disk)"
    Write-Host "  [8] Package or Deploy DigitalOcean Tier 1 (`$34.80/mo) Cloud Server"
    Write-Host "  [9] Nov 27 Stripe Payout & DigitalOcean Tier 1 Cloud Pre-Flight"
    Write-Host "  [A] Guided Gate Activation Wizard (Take Revenue Readiness to 100%)"
    Write-Host "  [B] Configure Gmail App Password in .env & Send Live Test Email"
    Write-Host "  [C] Verify Google Cloud OAuth (YouTube API v3 + rclone Drive)"
    Write-Host "  [D] Run 1-Screen Morning Executive Briefing (Stripe + Vault + CRM)"
    Write-Host "  [E] Run AES-256 Encrypted Backup & Drive Sync (or Restore)"
    Write-Host "  [F] Preview #1 Ranked 4D Short, 3D Thumbnail & Bold 4D Copy"
    Write-Host "  [G] Stripe-to-CRM Auto-Reconciler (Paid Pro_Node -> Unlock Tier 3 HA)"
    Write-Host "  [H] Upgrade /store 4D Hero + Refresh One-Click Desktop Shortcuts"
    Write-Host "  [I] Update Custom rclone Google Cloud OAuth Client (Permanent Sync)"
    Write-Host "  [K] Execute UCB1 Learning Curve Engine (Re-Rank 4D Queue + A/B Hooks)"
    Write-Host "  [L] Live Revenue Readiness Scorecard (Exact Gaps & Fixes)"
    Write-Host "  [M] YouTube Data API v3 4D Auto-Uploader (DryRun / Live Upload)"
    Write-Host "  [N] Start Free Cloudflare HTTPS Tunnel + 24/7 Watchdog"
    Write-Host "  [O] Schedule Automatic YouTube Uploads (Daily 12PM + Fri 6PM + 7:45PM)"
    Write-Host "  [P] Pull Live YouTube Views/Likes -> Feed Into UCB1 Learning Curve"
    Write-Host "  [W] Open Visual Showcase (Live 4D Store, Portal, 3D Thumbs & GitHub)"
    Write-Host "  [0] Safe Secret-Scanned GitHub Commit & Push (Toomer1980/monday_project)"
    Write-Host "  [Q] Quit"
    Write-Host "============================================================================" -ForegroundColor Cyan
}

function Run-SafeGitPush {
    Write-Host "`n=== SAFE SECRET-SCANNED GITHUB PUSH ===" -ForegroundColor Cyan
    $safe = @(
        ".gitignore","pyproject.toml","requirements.txt",
        "config/sovereign_block10.toml","config/sovereign_treasury.ini",
        "Modules/block10_treasury_engine.py","Modules/revenue_engine.py",
        "Modules/pronode_crm_engine.py","Modules/pronode_outreach_engine.py",
        "Modules/pronode_csv_importer.py","Modules/stripe_crm_reconciler.py",
        "Modules/oracle_4d_vault_upgrader.py","Modules/learning_curve_engine.py",
        "Modules/youtube_api_uploader.py","Modules/youtube_analytics_puller.py",
        "Modules/verify_youtube_oauth.py","Modules/pronode_lead_formatter.py",
        "Modules/funnel_dashboard_engine.py","Modules/pronode_sprint_engine.py",
        "Modules/storefront_4d_patcher.py",
        "sovereign_daemon.py","autonomous_youtube_bot.py","templates/oracle_3d_stage.html",
        "sovereign_supervisor.ps1","run_block10_treasury.ps1","setup_gdrive_sync.ps1",
        "publish_youtube_vault.ps1","send_pronode_invoice.ps1","deploy_digitalocean_tier1.ps1",
        "optimize_ram_and_boot.ps1","pronode_crm.ps1","generate_pronode_outreach.ps1",
        "import_pronode_prospects.ps1","send_pronode_outreach.ps1","stripe_live_alerts.ps1",
        "morning_briefing.ps1","backup_sovereigncore.ps1","package_youtube_52weeks.ps1",
        "reconcile_stripe_crm.ps1","create_desktop_shortcuts.ps1","update_rclone_oauth.ps1",
        "upgrade_52week_4d_vault.ps1","run_learning_curve.ps1","audit_revenue_gaps.ps1",
        "upload_youtube_4d.ps1","schedule_youtube_uploads.ps1","start_cloudflare_tunnel.ps1",
        "watch_cloudflare_tunnel.ps1","pull_youtube_analytics.ps1","verify_google_oauth.ps1",
        "build_pronode_leads.ps1","preflight_nov27_payout.ps1","funnel_dashboard.ps1",
        "setup_gmail_smtp.ps1","run_pronode_sprint.ps1","preview_next_4d_upload.ps1",
        "open_visual_showcase.ps1","upgrade_storefront_4d.ps1","sovereign_health_autopilot.ps1",
        "activate_missing_gates.ps1","test_stripe_webhook.ps1","oracle_hub.ps1",
        "Launch_OracleHub.cmd","Run_MorningBriefing.cmd",
        "deploy_bundle/sovereigncore.service","deploy_bundle/nginx_sovereigncore.conf",
        "deploy_bundle/.env.production.template","deploy_bundle/deploy_do_tier1.sh"
    )
    foreach ($f in $safe) { if (Test-Path "$ProjectDir\$f") { git add -- $f 2>$null } }
    $added = (git diff --cached | Where-Object { $_ -match '^\+[^+]' }) -join "`n"
    $rx = '(sk_live_[A-Za-z0-9]{20,}|sk_test_[A-Za-z0-9]{20,}|rk_live_[A-Za-z0-9]{20,}|whsec_[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{24,}|ya29\.[A-Za-z0-9\-_]{24,}|GOCSPX-[A-Za-z0-9\-_]{20,}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----)'
    if ($added -match $rx) {
        Write-Host "[ABORTED] Real secret detected in staged diff! Resetting index." -ForegroundColor Red
        git reset | Out-Null; return
    }
    $names = git diff --cached --name-only
    if (-not $names) { Write-Host "[INFO] GitHub already up to date." -ForegroundColor Yellow; return }
    $msg = Read-Host "Commit message (Enter for default)"
    if (-not $msg) { $msg = "Oracle Hub v11 sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm')" }
    git commit -m $msg
    if ($LASTEXITCODE -eq 0) { $br = (git rev-parse --abbrev-ref HEAD).Trim(); git push -u origin $br }
}

while ($true) {
    Show-Header
    $c = (Read-Host "Select action").Trim().ToUpper()
    switch ($c) {
        "1" { .\run_block10_treasury.ps1 }
        "2" { .\funnel_dashboard.ps1 }
        "3" {
            $sub = (Read-Host "CRM Action [Summary / List / Due / Add / Invoice / ExportCsv]").Trim()
            if (-not $sub) { $sub = "Summary" }
            if ($sub -ieq "Add") {
                $co = Read-Host "Company"; $ct = Read-Host "Contact"; $em = Read-Host "Email"; $nt = Read-Host "Notes"
                .\pronode_crm.ps1 -Action Add -Company $co -Contact $ct -Email $em -Stage Lead -Notes $nt
            } else { .\pronode_crm.ps1 -Action $sub }
        }
        "4" {
            $inCsv = (Read-Host "Raw CSV path (or type ADD for interactive entry)").Trim()
            if ($inCsv -ieq "ADD") { .\build_pronode_leads.ps1 -InteractiveAdd -ImportToCrm }
            elseif ($inCsv) { .\build_pronode_leads.ps1 -InputCsv $inCsv -ImportToCrm }
            else { .\build_pronode_leads.ps1 }
        }
        "5" {
            $go = (Read-Host "Send live throttled emails via Gmail SMTP? (Y = LIVE, N = DryRun)").Trim().ToUpper()
            if ($go -eq "Y") { .\run_pronode_sprint.ps1 -SendLive } else { .\run_pronode_sprint.ps1 }
        }
        "6" { .\test_stripe_webhook.ps1 -SimulateWebhook }
        "7" { .\sovereign_health_autopilot.ps1 -RegisterDailyTask }
        "8" {
            $ip = (Read-Host "Droplet IPv4 (blank = PackageOnly)").Trim()
            $dom = (Read-Host "Domain (default oraclesystemsllc.com)").Trim()
            if (-not $dom) { $dom = "oraclesystemsllc.com" }
            if ($ip) { .\deploy_digitalocean_tier1.ps1 -DropletIP $ip -Domain $dom -BootstrapRemote } else { .\deploy_digitalocean_tier1.ps1 -Domain $dom -PackageOnly }
        }
        "9" { .\preflight_nov27_payout.ps1 }
        "A" { .\activate_missing_gates.ps1 }
        "B" { .\setup_gmail_smtp.ps1 }
        "C" {
            $imp = (Read-Host "Auto-import JSON from Downloads & test live YouTube? (Y/N)").Trim().ToUpper()
            if ($imp -eq "Y") { .\verify_google_oauth.ps1 -AutoImportFromDownloads -TestLiveYouTube } else { .\verify_google_oauth.ps1 }
        }
        "D" { .\morning_briefing.ps1 -RefreshStripe -TrimRamIfHigh }
        "E" { .\backup_sovereigncore.ps1 -RegisterWeeklyTask }
        "F" { .\preview_next_4d_upload.ps1 -OpenMedia }
        "G" { .\reconcile_stripe_crm.ps1 -Mode AUTO -RegisterTask }
        "H" { .\upgrade_storefront_4d.ps1; .\create_desktop_shortcuts.ps1 }
        "I" { .\update_rclone_oauth.ps1 }
        "K" { .\run_learning_curve.ps1 -RegisterDailyTask }
        "L" { .\audit_revenue_gaps.ps1 }
        "M" {
            $ut = (Read-Host "Type [Short/FullVideo/Both] (default Short)").Trim(); if (-not $ut) { $ut = "Short" }
            $pr = (Read-Host "Privacy [public/unlisted/private] (default public)").Trim(); if (-not $pr) { $pr = "public" }
            $go = (Read-Host "Upload live now? (Y = LIVE, N = DryRun)").Trim().ToUpper()
            if ($go -eq "Y") { .\upload_youtube_4d.ps1 -UploadType $ut -Privacy $pr -UploadNow } else { .\upload_youtube_4d.ps1 -UploadType $ut -Privacy $pr }
        }
        "N" { .\watch_cloudflare_tunnel.ps1 -RegisterBootTask -RunOnce }
        "O" { .\schedule_youtube_uploads.ps1 }
        "P" { .\pull_youtube_analytics.ps1 }
        "W" { .\open_visual_showcase.ps1 }
        "0" { Run-SafeGitPush }
        "Q" { break }
        default { Write-Host "Invalid option." -ForegroundColor Yellow }
    }
    Write-Host ""
    Read-Host "Press Enter to return to Oracle Hub" | Out-Null
}