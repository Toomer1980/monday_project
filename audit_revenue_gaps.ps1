$ErrorActionPreference = "Continue"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
Set-Location $ProjectDir

$EnvMap = @{}
if (Test-Path "$ProjectDir\.env") {
    foreach ($ln in (Get-Content "$ProjectDir\.env" -ErrorAction SilentlyContinue)) {
        $t = $ln.Trim()
        if ($t -and (-not $t.StartsWith("#")) -and $t.Contains("=")) {
            $i = $t.IndexOf("=")
            $EnvMap[$t.Substring(0,$i).Trim()] = $t.Substring($i+1).Trim().Trim('"').Trim("'")
        }
    }
}

$Checks = @()
function Add-Check([string]$N, [bool]$Ok, [string]$Det, [string]$Fix) {
    $script:Checks += [PSCustomObject]@{ Gate = $N; Pass = $Ok; Detail = $Det; Fix = $Fix }
}

# 1. Live Stripe Payouts
$sOk = $false; $sDet = "Not polled"
if (Test-Path "$ProjectDir\audit_inbox\stripe_live_api_snapshot.json") {
    try {
        $s = Get-Content "$ProjectDir\audit_inbox\stripe_live_api_snapshot.json" -Raw | ConvertFrom-Json
        $sOk = [bool]($s.live_api_connected -and $s.payouts_enabled)
        $sDet = ("Live OK | Pending: `${0:N2} | PayoutsEnabled: {1}" -f $s.pending_usd, $s.payouts_enabled)
    } catch {}
}
Add-Check "1. Live Stripe Payouts" $sOk $sDet ".\run_block10_treasury.ps1"

# 2. Storefront 4D Hero (6 Cards) + Portal Upsell
$srvOk = $false; $heroOk = $false
try {
    $r1 = Invoke-WebRequest -Uri "http://127.0.0.1:8000/store"  -UseBasicParsing -TimeoutSec 4
    $r2 = Invoke-WebRequest -Uri "http://127.0.0.1:8000/portal" -UseBasicParsing -TimeoutSec 4
    $srvOk = ($r1.StatusCode -eq 200 -and $r2.StatusCode -eq 200)
    $heroOk = (($r1.Content -match 'oracle-4d-hero') -and ($r2.Content -match 'oracle-portal-upsell'))
} catch {}
Add-Check "2. 4D Store & Upsell" ($srvOk -and $heroOk) ("HTTP 200: $srvOk | 6-Card 4D Hero + Portal Upsell: $heroOk") ".\upgrade_storefront_4d.ps1"

# 3. 104-Video 4D Vault + $15 Pack ZIP
$f4d = (Get-ChildItem "$ProjectDir\Content_Vault_4D_Full" -Filter "*_4D_MAX.mp4" -ErrorAction SilentlyContinue).Count
$s4d = (Get-ChildItem "$ProjectDir\Content_Vault_4D_Shorts" -Filter "*_4D_MAX.mp4" -ErrorAction SilentlyContinue).Count
$zipOk = Test-Path "$ProjectDir\deliverables\Oracle_4D_Creator_Asset_Pack_15.zip"
Add-Check "3. 4D Vault & Asset Pack" ($f4d -ge 52 -and $s4d -ge 52 -and $zipOk) ("$f4d/52 Full + $s4d/52 Shorts | `$15 ZIP Ready: $zipOk") ".\build_4d_asset_pack.ps1"

# 4. YouTube OAuth + Live Uploads
$ytSec = Test-Path "$ProjectDir\config\youtube_client_secret.json"
$pubCnt = 0
if (Test-Path "$ProjectDir\data\youtube_publish_state.json") {
    try {
        $y = Get-Content "$ProjectDir\data\youtube_publish_state.json" -Raw | ConvertFrom-Json
        $pubCnt = @($y.published_full).Count + @($y.published_shorts).Count
    } catch {}
}
Add-Check "4. YouTube API & Uploads" ($ytSec -and $pubCnt -gt 0) ("OAuth JSON: $ytSec | Published: $pubCnt/104") ".\upload_youtube_4d.ps1 -UploadType Short -Privacy public -UploadNow"

# 5. Public HTTPS Funnel & Live Stripe Webhook
$pubUrl = $EnvMap["PUBLIC_BASE_URL"]
$whId   = if (Test-Path "$ProjectDir\config\stripe_webhook_id.txt") { (Get-Content "$ProjectDir\config\stripe_webhook_id.txt" -Raw).Trim() } else { "" }
$pubOk  = [bool]($pubUrl -and ($pubUrl -match '^https://') -and $whId)
Add-Check "5. HTTPS Funnel & Webhook" $pubOk ("URL: $pubUrl | Webhook: $whId") ".\sync_stripe_webhook.ps1 -CreateIfMissing"

# 6. B2B Pro_Node CRM Pipeline Populated
$crmCnt = 0
if (Test-Path "$ProjectDir\data\pronode_crm.db") {
    $crmCnt = [int](python -c "import sqlite3; c=sqlite3.connect(r'$ProjectDir\data\pronode_crm.db'); print(c.execute('SELECT COUNT(*) FROM prospects').fetchone()[0]); c.close()" 2>$null)
}
Add-Check "6. B2B Pro_Node CRM" ($crmCnt -gt 0) ("$crmCnt prospect(s) in pronode_crm.db") ".\build_pronode_leads.ps1 -InteractiveAdd -ImportToCrm"

# 7. Outbound Email (Gmail API HTTPS 443 OR App Password)
$gmailTok = Test-Path "$ProjectDir\config\gmail_token.json"
$gp = $EnvMap["GMAIL_APP_PASSWORD"]
$gmOk = [bool]($gmailTok -or ($gp -and ($gp -notmatch 'PASTE_16_CHAR') -and ($gp.Replace(" ","").Length -ge 12)))
$gmDet = if ($gmailTok) { "Gmail API HTTPS/443 Authorized (Bypassing SMTP block)" } elseif ($gmOk) { "SMTP App Password set" } else { "Not authorized yet" }
Add-Check "7. Outbound Email Engine" $gmOk $gmDet "python .\Modules\google_mail_engine.py ."

# 8. Permanent Custom rclone OAuth Client
$rOk = $false; $rDet = "Using expiring shared rclone client_id"
$rConf = Join-Path -Path $env:APPDATA -ChildPath "rclone\rclone.conf"
if (Test-Path $rConf) {
    $rcRaw = Get-Content $rConf -Raw -ErrorAction SilentlyContinue
    if ($rcRaw -match '(?m)^client_id\s*=\s*.+\.apps\.googleusercontent\.com') { $rOk = $true; $rDet = "Custom Google Cloud OAuth client_id active" }
}
Add-Check "8. Permanent Drive Sync" $rOk $rDet ".\update_rclone_oauth.ps1"

$passN = ($Checks | Where-Object { $_.Pass }).Count
$pct   = [math]::Round(($passN / $Checks.Count) * 100.0, 0)
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ("  ORACLE SYSTEMS LLC // REVENUE READINESS SCORECARD: {0}% ({1}/{2} GATES)" -f $pct, $passN, $Checks.Count) -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan
foreach ($c in $Checks) {
    $tag = if ($c.Pass) { "[READY]  " } else { "[MISSING]" }
    $col = if ($c.Pass) { "Green" } else { "Yellow" }
    Write-Host ("{0} {1,-25} | {2}" -f $tag, $c.Gate, $c.Detail) -ForegroundColor $col
    if (-not $c.Pass) { Write-Host ("          -> Fix: {0}" -f $c.Fix) -ForegroundColor Cyan }
}
Write-Host "========================================================================" -ForegroundColor Cyan