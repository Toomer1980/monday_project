# ==============================================================================
# Oracle Systems LLC - oracle_hub.ps1 (Pure ASCII / PS 5.1 Safe)
# Master Terminal Command Center for SovereignCore Automation Suite (Phase 6)
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
    $fullN  = (Get-ChildItem (Join-Path -Path $ProjectDir -ChildPath "Content_Vault_52Weeks") -Filter "*.mp4" -ErrorAction SilentlyContinue).Count
    $shortN = (Get-ChildItem (Join-Path -Path $ProjectDir -ChildPath "Content_Vault_Shorts")  -Filter "*.mp4" -ErrorAction SilentlyContinue).Count
    $v4dN   = (Get-ChildItem (Join-Path -Path $ProjectDir -ChildPath "Content_Vault_4D_Thumbnails") -Filter "*_3D_Thumb.jpg" -ErrorAction SilentlyContinue).Count

    Write-Host "========================================================================" -ForegroundColor Cyan
    Write-Host "   ORACLE SYSTEMS LLC // SOVEREIGNCORE MASTER COMMAND HUB (PHASE 10)" -ForegroundColor White
    Write-Host "========================================================================" -ForegroundColor Cyan
    Write-Host ("  Port 8000 : {0,-8} | RAM: {1}% ({2} GB free) | Vault: {3}/52 Full, {4}/52 Shorts | 4D Thumbs: {5}" -f $(if ($portUp) { "ONLINE" } else { "OFFLINE" }), $ramPct, $freeGB, $fullN, $shortN, $v4dN) -ForegroundColor $(if ($portUp -and $ramPct -lt 85) { "Green" } else { "Yellow" })
    Write-Host "------------------------------------------------------------------------" -ForegroundColor DarkGray
    Write-Host "  [1] Block 10 Treasury Audit + Live Stripe API Poll + Google Drive Sync"
    Write-Host "  [2] YouTube 52-Week Vault Publisher & Live UTM Click Leaderboard"
    Write-Host "  [3] Pro_Node (`$49,999) B2B CRM (Summary / Add / List / Due / Invoice)"
    Write-Host "  [4] Generate B2B Outreach Emails & 3-Min Live Sandbox Demo Checklist"
    Write-Host "  [5] Send Standalone Pro_Node Stripe ACH Invoice (`$24,999.50 / `$49,999)"
    Write-Host "  [6] Run Stripe Webhook & End-to-End ZIP/MP4 Fulfillment Self-Test"
    Write-Host "  [7] Trim Laptop RAM Now & Check/Register Windows Logon Boot Tasks"
    Write-Host "  [8] Package or Deploy DigitalOcean Tier 1 (`$34.80/mo) Cloud Server"
    Write-Host "  [9] Check / Re-Authorize rclone Google Drive Sync (Oracle_Audit_2026)"
    Write-Host "  [A] Bulk-Import 20-Lead CSV into Pro_Node CRM + Auto-Draft Outreach"
    Write-Host "  [B] Preview or Send Queued Pro_Node Outreach Emails via Gmail SMTP"
    Write-Host "  [C] Poll Live Stripe Balance & Pop Desktop Payout Alert (10-Min Watch)"
    Write-Host "  [D] Run 1-Screen Morning Executive Briefing (Stripe + Vault + CRM)"
    Write-Host "  [E] Run AES-256 Encrypted Backup & Sync to Google Drive (or Restore)"
    Write-Host "  [F] Package Standard 52-Week YouTube Upload Manifest"
    Write-Host "  [G] Run Stripe-to-CRM Auto-Reconciler (Paid Pro_Node -> Unlock Tier 3 HA)"
    Write-Host "  [H] Create/Refresh One-Click Desktop Shortcuts for Oracle Suite"
    Write-Host "  [I] Update Custom Google Cloud OAuth Client for rclone (Permanent Sync)"
    Write-Host "  [J] Upgrade 52-Week Vault to 3D/4D Tesseract + Mobius Templates & Thumbs"
    Write-Host "  [K] Execute UCB1 Learning Curve Engine (Re-Rank 4D Queue + A/B Hooks)"
    Write-Host "  [L] Run Live Revenue Readiness Scorecard (Exact Gaps & Fixes)"
    Write-Host "  [M] YouTube Data API v3 4D Auto-Uploader (Short / FullVideo / DryRun)"
    Write-Host "  [N] Start Free Cloudflare HTTPS Tunnel + 24/7 Watchdog (Live Public URL)"
    Write-Host "  [O] Schedule Automatic YouTube 4D Uploads (Daily 12PM + Fri 6PM)"
    Write-Host "  [P] Pull Live YouTube Views/Likes -> Feed Into UCB1 Learning Curve"
    Write-Host "  [R] Verify Google Cloud OAuth JSON (YouTube API v3 + rclone Drive)"
    Write-Host "  [S] Pro_Node (`$49,999) B2B Lead List Builder, ICP Scorer & CSV Formatter"
    Write-Host "  [T] Run Nov 27 Stripe Payout & DigitalOcean Tier 1 Cloud Pre-Flight"
    Write-Host "  [U] Live Stripe + YouTube + UTM + CRM Conversion Funnel Dashboard"
    Write-Host "  [V] Configure Gmail App Password in .env & Send Test Pro_Node Email"
    Write-Host "  [W] Open Visual Showcase (Live Store, Portal, 4D Thumbs & GitHub)"
    Write-Host "  [0] Safe Secret-Scanned GitHub Commit & Push (Toomer1980/monday_project)"
    Write-Host "  [Q] Quit"
    Write-Host "========================================================================" -ForegroundColor Cyan
}

function Run-SafeGitPush {
    Write-Host "`n=== SAFE SECRET-SCANNED GITHUB PUSH ===" -ForegroundColor Cyan
    $safe = @(
        ".gitignore","pyproject.toml","requirements.txt",
        "config/sovereign_block10.toml","config/sovereign_treasury.ini",
        "Modules/block10_treasury_engine.py","Modules/revenue_engine.py",
        "Modules/pronode_crm_engine.py","Modules/pronode_outreach_engine.py",
        "Modules/pronode_csv_importer.py","Modules/stripe_crm_reconciler.py",
        "Modules/oracle_4d_vault_upgrader.py","Modules/learning_curve_engine.py","Modules/youtube_api_uploader.py","Modules/youtube_analytics_puller.py","Modules/verify_youtube_oauth.py","Modules/pronode_lead_formatter.py","Modules/funnel_dashboard_engine.py",
        "sovereign_daemon.py","autonomous_youtube_bot.py","templates/oracle_3d_stage.html",
        "sovereign_supervisor.ps1","run_block10_treasury.ps1","setup_gdrive_sync.ps1",
        "publish_youtube_vault.ps1","send_pronode_invoice.ps1","deploy_digitalocean_tier1.ps1",
        "optimize_ram_and_boot.ps1","pronode_crm.ps1","generate_pronode_outreach.ps1",
        "import_pronode_prospects.ps1","send_pronode_outreach.ps1","stripe_live_alerts.ps1",
        "morning_briefing.ps1","backup_sovereigncore.ps1","package_youtube_52weeks.ps1",
        "reconcile_stripe_crm.ps1","create_desktop_shortcuts.ps1","update_rclone_oauth.ps1",
        "upgrade_52week_4d_vault.ps1","run_learning_curve.ps1","audit_revenue_gaps.ps1","upload_youtube_4d.ps1","schedule_youtube_uploads.ps1","start_cloudflare_tunnel.ps1","watch_cloudflare_tunnel.ps1","pull_youtube_analytics.ps1","verify_google_oauth.ps1","build_pronode_leads.ps1","preflight_nov27_payout.ps1","funnel_dashboard.ps1","setup_gmail_smtp.ps1","open_visual_showcase.ps1","Launch_OracleHub.cmd","Run_MorningBriefing.cmd",
        "test_stripe_webhook.ps1","oracle_hub.ps1",
        "deploy_bundle/sovereigncore.service","deploy_bundle/nginx_sovereigncore.conf",
        "deploy_bundle/.env.production.template","deploy_bundle/deploy_do_tier1.sh"
    )
    foreach ($f in $safe) { if (Test-Path (Join-Path -Path $ProjectDir -ChildPath $f)) { git add -- $f 2>$null } }
    $diff = (git diff --cached) -join "`n"
    $rx = '(sk_live_[A-Za-z0-9]{16,}|sk_test_[A-Za-z0-9]{16,}|rk_live_[A-Za-z0-9]{16,}|whsec_[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|ya29\.[A-Za-z0-9\-_]{20,}|1//[0-9A-Za-z\-_]{20,}|GOCSPX-[A-Za-z0-9\-_]{16,}|GMAIL_APP_PASSWORD\s*=\s*[a-z]{16}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY)'
    if ($diff -match $rx) {
        Write-Host "[ABORTED] Secret pattern detected in staged diff! Resetting index." -ForegroundColor Red
        git reset | Out-Null
        return
    }
    $names = git diff --cached --name-only
    if (-not $names) {
        Write-Host "[INFO] Repository already up to date." -ForegroundColor Yellow
        return
    }
    $msg = Read-Host "Commit message (press Enter for default)"
    if (-not $msg) { $msg = "Oracle Hub sync: $(Get-Date -Format 'yyyy-MM-dd HH:mm')" }
    git commit -m $msg
    if ($LASTEXITCODE -eq 0) {
        $br = (git rev-parse --abbrev-ref HEAD).Trim()
        git push -u origin $br
    }
}

while ($true) {
    Show-Header
    $choice = (Read-Host "Select action").Trim().ToUpper()
    switch ($choice) {
        "1" { .\run_block10_treasury.ps1 }
        "2" {
            $mark = (Read-Host "Mark next Short + Full video as published? (Y/N)").Trim().ToUpper()
            if ($mark -eq "Y") { .\publish_youtube_vault.ps1 -MarkNextPublished } else { .\publish_youtube_vault.ps1 }
        }
        "3" {
            $sub = (Read-Host "CRM Action [Summary / List / Due / Add / Invoice / ExportCsv]").Trim()
            if (-not $sub) { $sub = "Summary" }
            if ($sub -ieq "Add") {
                $co = Read-Host "Company Name"
                $ct = Read-Host "Contact Name"
                $em = Read-Host "Email"
                $st = Read-Host "Stage [Lead/Contacted/DemoBooked/ProposalSent] (default Lead)"
                if (-not $st) { $st = "Lead" }
                $nt = Read-Host "Notes"
                .\pronode_crm.ps1 -Action Add -Company $co -Contact $ct -Email $em -Stage $st -Notes $nt
            } elseif ($sub -ieq "Invoice") {
                .\pronode_crm.ps1 -Action List
                $pidNum = [int](Read-Host "Prospect ID")
                $ms = Read-Host "Milestone [M1/M2/Full] (default M1)"
                if (-not $ms) { $ms = "M1" }
                $md = Read-Host "Mode [TEST/LIVE] (default TEST)"
                if (-not $md) { $md = "TEST" }
                $go = (Read-Host "Actually send via Stripe now? (Y = Send, N = DryRun)").Trim().ToUpper()
                if ($go -eq "Y") { .\pronode_crm.ps1 -Action Invoice -Id $pidNum -Milestone $ms -InvoiceMode $md -SendInvoice }
                else { .\pronode_crm.ps1 -Action Invoice -Id $pidNum -Milestone $ms -InvoiceMode $md -DryRun }
            } else {
                .\pronode_crm.ps1 -Action $sub
            }
        }
        "4" {
            $all = (Read-Host "Generate for ALL active prospects? (Y = All, N = Due Today Only)").Trim().ToUpper()
            if ($all -eq "Y") { .\generate_pronode_outreach.ps1 -AllActive } else { .\generate_pronode_outreach.ps1 }
        }
        "5" {
            $cn = Read-Host "Client Name"
            $ce = Read-Host "Client Email"
            $ms = Read-Host "Milestone [M1/M2/Full] (default M1)"
            if (-not $ms) { $ms = "M1" }
            $md = Read-Host "Mode [TEST/LIVE] (default TEST)"
            if (-not $md) { $md = "TEST" }
            $go = (Read-Host "Send invoice via Stripe? (Y = Send, N = DryRun)").Trim().ToUpper()
            if ($go -eq "Y") { .\send_pronode_invoice.ps1 -ClientName $cn -ClientEmail $ce -Milestone $ms -Mode $md -SendInvoice }
            else { .\send_pronode_invoice.ps1 -ClientName $cn -ClientEmail $ce -Milestone $ms -Mode $md -DryRun }
        }
        "6" { .\test_stripe_webhook.ps1 -SimulateWebhook }
        "7" {
            $reg = (Read-Host "Also register/refresh Windows Logon boot tasks? (Y/N)").Trim().ToUpper()
            if ($reg -eq "Y") { .\optimize_ram_and_boot.ps1 -TrimNow -RegisterBootTasks } else { .\optimize_ram_and_boot.ps1 -TrimNow }
        }
        "8" {
            $ip = (Read-Host "DigitalOcean Droplet IPv4 (leave blank to PackageOnly)").Trim()
            $dom = (Read-Host "Domain (default oraclesystemsllc.com)").Trim()
            if (-not $dom) { $dom = "oraclesystemsllc.com" }
            if ($ip) { .\deploy_digitalocean_tier1.ps1 -DropletIP $ip -Domain $dom -BootstrapRemote }
            else { .\deploy_digitalocean_tier1.ps1 -Domain $dom -PackageOnly }
        }
        "9" { .\setup_gdrive_sync.ps1 -ConfigureNow }
        "A" {
            $csvP = (Read-Host "Path to prospect CSV (press Enter to view template path)").Trim()
            if (-not $csvP) { .\import_pronode_prospects.ps1 }
            else {
                $dr = (Read-Host "Dry-Run preview first? (Y/N)").Trim().ToUpper()
                if ($dr -eq "Y") { .\import_pronode_prospects.ps1 -CsvPath $csvP -DryRun }
                else { .\import_pronode_prospects.ps1 -CsvPath $csvP -GenerateDrafts }
            }
        }
        "B" {
            $go = (Read-Host "Send queued drafts via Gmail SMTP now? (Y = LIVE SEND, N = Preview)").Trim().ToUpper()
            if ($go -eq "Y") { .\send_pronode_outreach.ps1 -SendNow } else { .\send_pronode_outreach.ps1 }
        }
        "C" {
            $reg = (Read-Host "Register/refresh 10-minute background alert task? (Y/N)").Trim().ToUpper()
            if ($reg -eq "Y") { .\stripe_live_alerts.ps1 -NotifyAlways -RegisterAlertTask } else { .\stripe_live_alerts.ps1 -NotifyAlways }
        }
        "D" { .\morning_briefing.ps1 -RefreshStripe -TrimRamIfHigh }
        "E" {
            $rf = (Read-Host "Backup now (press Enter) OR paste .zip.enc path to Restore").Trim()
            if ($rf) { .\backup_sovereigncore.ps1 -RestoreFile $rf }
            else { .\backup_sovereigncore.ps1 -RegisterWeeklyTask }
        }
        "F" { .\package_youtube_52weeks.ps1 }
        "G" {
            $md = (Read-Host "Mode [AUTO / LIVE / TEST] (default AUTO)").Trim().ToUpper()
            if (-not $md) { $md = "AUTO" }
            $rt = (Read-Host "Also register 30-min background task? (Y/N)").Trim().ToUpper()
            if ($rt -eq "Y") { .\reconcile_stripe_crm.ps1 -Mode $md -RegisterTask } else { .\reconcile_stripe_crm.ps1 -Mode $md }
        }
        "H" { .\create_desktop_shortcuts.ps1 }
        "I" {
            $g = (Read-Host "Show setup guide only? (Y = Guide, N = Enter Client ID & Secret now)").Trim().ToUpper()
            if ($g -eq "Y") { .\update_rclone_oauth.ps1 -ShowGuideOnly } else { .\update_rclone_oauth.ps1 }
        }
        "J" {
            $vm = (Read-Host "4D Upgrade Mode [META_ONLY / TEST_FIRST / ALL] (default TEST_FIRST)").Trim().ToUpper()
            if (-not $vm) { $vm = "TEST_FIRST" }
            $fs = (Read-Host "Full video length in seconds (default 1800 = 30 min)").Trim()
            if (-not $fs) { $fs = "1800" }
            $ss = (Read-Host "Short video length in seconds (default 175 = 2m55s max Short)").Trim()
            if (-not $ss) { $ss = "175" }
            .\upgrade_52week_4d_vault.ps1 -Mode $vm -FullDurationSec ([int]$fs) -ShortDurationSec ([int]$ss)
        }
        "K" { .\run_learning_curve.ps1 -RegisterDailyTask }
        "L" { .\audit_revenue_gaps.ps1 }
        "M" {
            $ut = (Read-Host "Type [Short/FullVideo/Both] (default Short)").Trim()
            if (-not $ut) { $ut = "Short" }
            $pr = (Read-Host "Privacy [public/unlisted/private] (default unlisted)").Trim()
            if (-not $pr) { $pr = "unlisted" }
            $go = (Read-Host "Upload live now? (Y = LIVE, N = DryRun)").Trim().ToUpper()
            if ($go -eq "Y") { .\upload_youtube_4d.ps1 -UploadType $ut -Privacy $pr -UploadNow } else { .\upload_youtube_4d.ps1 -UploadType $ut -Privacy $pr }
        }
        "N" {
            $wb = (Read-Host "Register 24/7 Logon Watchdog too? (Y/N)").Trim().ToUpper()
            if ($wb -eq "Y") { .\watch_cloudflare_tunnel.ps1 -RegisterBootTask -RunOnce } else { .\start_cloudflare_tunnel.ps1 }
        }
        "O" { .\schedule_youtube_uploads.ps1 }
        "P" { .\pull_youtube_analytics.ps1 }
        "R" {
            $imp = (Read-Host "Auto-import client_secret_*.json from Downloads & test live YouTube? (Y/N)").Trim().ToUpper()
            if ($imp -eq "Y") { .\verify_google_oauth.ps1 -AutoImportFromDownloads -TestLiveYouTube } else { .\verify_google_oauth.ps1 }
        }
        "S" {
            $inCsv = (Read-Host "Raw CSV path (or type ADD for interactive lead entry)").Trim()
            if ($inCsv -ieq "ADD") { .\build_pronode_leads.ps1 -InteractiveAdd -ImportToCrm }
            elseif ($inCsv) { .\build_pronode_leads.ps1 -InputCsv $inCsv -ImportToCrm }
            else { .\build_pronode_leads.ps1 }
        }
        "T" { .\preflight_nov27_payout.ps1 }
        "U" { .\funnel_dashboard.ps1 }
        "V" { .\setup_gmail_smtp.ps1 }
        "W" { .\open_visual_showcase.ps1 }
        "0" { Run-SafeGitPush }
        "Q" { break }
        default { Write-Host "Invalid option." -ForegroundColor Yellow }
    }
    Write-Host ""
    Read-Host "Press Enter to return to Oracle Hub" | Out-Null
}