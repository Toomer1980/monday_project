# ==============================================================================
# Oracle Systems LLC - audit_revenue_gaps.ps1 (Pure ASCII / PS 5.1 Safe)
# Scores every gate required to produce and compound real Stripe revenue,
# flags exact missing activations, and prints 1-step commands to close each gap.
# ==============================================================================
$ErrorActionPreference = "Continue"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
Set-Location $ProjectDir

$EnvFile = Join-Path -Path $ProjectDir -ChildPath ".env"
$EnvMap = @{}
if (Test-Path $EnvFile) {
    foreach ($line in (Get-Content $EnvFile -ErrorAction SilentlyContinue)) {
        $t = $line.Trim()
        if ($t -and (-not $t.StartsWith("#")) -and $t.Contains("=")) {
            $i = $t.IndexOf("=")
            $EnvMap[$t.Substring(0,$i).Trim()] = $t.Substring($i+1).Trim().Trim('"').Trim("'")
        }
    }
}

$Checks = @()
function Add-Check([string]$Name, [bool]$Passed, [string]$Detail, [string]$FixCmd) {
    $script:Checks += [PSCustomObject]@{ Gate = $Name; Pass = $Passed; Detail = $Detail; NextAction = $FixCmd }
}

# 1. Live Stripe Key & Payouts Enabled
$liveSnap = Join-Path -Path $ProjectDir -ChildPath "audit_inbox\stripe_live_api_snapshot.json"
$stripeOk = $false; $stripeDet = "Not polled yet"
if (Test-Path $liveSnap) {
    try {
        $s = Get-Content $liveSnap -Raw | ConvertFrom-Json
        $stripeOk = [bool]($s.live_api_connected -and $s.payouts_enabled)
        $stripeDet = ("Live OK | Pending: `${0:N2} | PayoutsEnabled: {1}" -f $s.pending_usd, $s.payouts_enabled)
    } catch {}
}
Add-Check "1. Live Stripe Payouts" $stripeOk $stripeDet ".\run_block10_treasury.ps1"

# 2. Local Storefront + /portal Upsell Online
$srvOk = $false; $upsellOk = $false
try {
    $r1 = Invoke-WebRequest -Uri "http://127.0.0.1:8000/store" -UseBasicParsing -TimeoutSec 4
    $r2 = Invoke-WebRequest -Uri "http://127.0.0.1:8000/portal" -UseBasicParsing -TimeoutSec 4
    $srvOk = ($r1.StatusCode -eq 200 -and $r2.StatusCode -eq 200)
    $upsellOk = ($r2.Content -match 'oracle-portal-upsell')
} catch {}
Add-Check "2. Store & Portal Upsell" ($srvOk -and $upsellOk) ("Store+Portal HTTP 200: $srvOk | Upsell Banner Active: $upsellOk") "Restart sovereign_daemon.py"

# 3. 104-Video 4D Vault Complete
$f4d = (Get-ChildItem (Join-Path -Path $ProjectDir -ChildPath "Content_Vault_4D_Full") -Filter "*_4D_MAX.mp4" -ErrorAction SilentlyContinue).Count
$s4d = (Get-ChildItem (Join-Path -Path $ProjectDir -ChildPath "Content_Vault_4D_Shorts") -Filter "*_4D_MAX.mp4" -ErrorAction SilentlyContinue).Count
Add-Check "3. 4D Content Vault" ($f4d -ge 52 -and $s4d -ge 52) ("$f4d/52 Full + $s4d/52 Shorts upgraded") ".\upgrade_52week_4d_vault.ps1 -Mode ALL"

# 4. YouTube Publishing Active (>0 uploaded)
$pubCnt = 0
$ytSt = Join-Path -Path $ProjectDir -ChildPath "data\youtube_publish_state.json"
if (Test-Path $ytSt) {
    try {
        $y = Get-Content $ytSt -Raw | ConvertFrom-Json
        $pubCnt = @($y.published_full).Count + @($y.published_shorts).Count
    } catch {}
}
Add-Check "4. YouTube Traffic Live" ($pubCnt -gt 0) ("$pubCnt/104 videos uploaded to YouTube (0 views = $0 traffic)") ".\publish_youtube_vault.ps1 -OpenUploadFolder"

# 5. Public Cloud Domain Active (Not localhost)
$pubUrl = $EnvMap["PUBLIC_BASE_URL"]
$cloudOk = [bool]($pubUrl -and ($pubUrl -notmatch '127\.0\.0\.1|localhost'))
Add-Check "5. Public Cloud Domain" $cloudOk ("PUBLIC_BASE_URL = $pubUrl") ".\deploy_digitalocean_tier1.ps1 -DropletIP <IP> -Domain oraclesystemsllc.com -BootstrapRemote"

# 6. B2B Pro_Node CRM Pipeline Populated (>0 prospects)
$crmCnt = 0
$crmDb = Join-Path -Path $ProjectDir -ChildPath "data\pronode_crm.db"
if (Test-Path $crmDb) {
    $crmCnt = [int](python -c "import sqlite3; c=sqlite3.connect(r'$crmDb'); print(c.execute('SELECT COUNT(*) FROM prospects').fetchone()[0]); c.close()" 2>$null)
}
Add-Check "6. B2B Pro_Node Leads" ($crmCnt -gt 0) ("$crmCnt prospect(s) in pronode_crm.db (Target: 20/week)") ".\import_pronode_prospects.ps1 -CsvPath .\data\weekly_prospects_template.csv -GenerateDrafts"

# 7. Gmail SMTP App Password Configured
$gp = $EnvMap["GMAIL_APP_PASSWORD"]
$gmailOk = [bool]($gp -and ($gp -notmatch 'PASTE_16_CHAR') -and ($gp.Replace(" ","").Length -ge 12))
Add-Check "7. Gmail Outreach SMTP" $gmailOk $(if ($gmailOk) { "16-char App Password configured" } else { "Still placeholder in .env" }) "Paste 16-char Google App Password into .env GMAIL_APP_PASSWORD="

# 8. Custom rclone Google Drive OAuth Client
$rcloneOk = $false; $rcloneDet = "Using expiring shared rclone client_id"
$rConf = Join-Path -Path $env:APPDATA -ChildPath "rclone\rclone.conf"
if (Test-Path $rConf) {
    $rcRaw = Get-Content $rConf -Raw -ErrorAction SilentlyContinue
    if ($rcRaw -match '(?m)^client_id\s*=\s*.+\.apps\.googleusercontent\.com') {
        $rcloneOk = $true
        $rcloneDet = "Custom Google Cloud OAuth client_id active"
    }
}
Add-Check "8. Permanent Drive Sync" $rcloneOk $rcloneDet ".\update_rclone_oauth.ps1"

# Print Scorecard
$passedN = ($Checks | Where-Object { $_.Pass }).Count
$totalN  = $Checks.Count
$pct     = [math]::Round(($passedN / $totalN) * 100.0, 0)

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ("  ORACLE SYSTEMS LLC // REVENUE READINESS SCORECARD: {0}% ({1}/{2} GATES)" -f $pct, $passedN, $totalN) -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan
foreach ($c in $Checks) {
    $tag = if ($c.Pass) { "[READY]  " } else { "[MISSING]" }
    $col = if ($c.Pass) { "Green" } else { "Yellow" }
    Write-Host ("{0} {1,-25} | {2}" -f $tag, $c.Gate, $c.Detail) -ForegroundColor $col
    if (-not $c.Pass) {
        Write-Host ("          -> Fix: {0}" -f $c.NextAction) -ForegroundColor Cyan
    }
}
Write-Host "========================================================================" -ForegroundColor Cyan