# ==============================================================================
# Oracle Systems LLC - oracle_hub.ps1 (Pure ASCII / PS 5.1 Safe)
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
    $fullN  = (Get-ChildItem (Join-Path $ProjectDir "Content_Vault_52Weeks") -Filter "*.mp4" -ErrorAction SilentlyContinue).Count
    $shortN = (Get-ChildItem (Join-Path $ProjectDir "Content_Vault_Shorts")  -Filter "*.mp4" -ErrorAction SilentlyContinue).Count

    Write-Host "========================================================================" -ForegroundColor Cyan
    Write-Host "   ORACLE SYSTEMS LLC // SOVEREIGNCORE MASTER COMMAND HUB (PS 5.1)" -ForegroundColor White
    Write-Host "========================================================================" -ForegroundColor Cyan
    Write-Host ("  Port 8000 : {0,-10} | RAM: {1}% ({2} GB free) | Vault: {3}/52 Full, {4}/52 Shorts" -f $(if ($portUp) { "ONLINE" } else { "OFFLINE" }), $ramPct, $freeGB, $fullN, $shortN) -ForegroundColor $(if ($portUp -and $ramPct -lt 85) { "Green" } else { "Yellow" })
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
        "sovereign_daemon.py","autonomous_youtube_bot.py","templates/oracle_3d_stage.html",
        "sovereign_supervisor.ps1","run_block10_treasury.ps1","setup_gdrive_sync.ps1",
        "publish_youtube_vault.ps1","send_pronode_invoice.ps1","deploy_digitalocean_tier1.ps1",
        "optimize_ram_and_boot.ps1","pronode_crm.ps1","generate_pronode_outreach.ps1",
        "test_stripe_webhook.ps1","oracle_hub.ps1",
        "deploy_bundle/sovereigncore.service","deploy_bundle/nginx_sovereigncore.conf",
        "deploy_bundle/.env.production.template","deploy_bundle/deploy_do_tier1.sh"
    )
    foreach ($f in $safe) { if (Test-Path (Join-Path $ProjectDir $f)) { git add -- $f 2>$null } }
    $diff = (git diff --cached) -join "`n"
    $rx = '(sk_live_[A-Za-z0-9]{16,}|sk_test_[A-Za-z0-9]{16,}|rk_live_[A-Za-z0-9]{16,}|whsec_[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|ya29\.[A-Za-z0-9\-_]{20,}|1//[0-9A-Za-z\-_]{20,}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY)'
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
        "0" { Run-SafeGitPush }
        "Q" { break }
        default { Write-Host "Invalid option." -ForegroundColor Yellow }
    }
    Write-Host ""
    Read-Host "Press Enter to return to Oracle Hub" | Out-Null
}