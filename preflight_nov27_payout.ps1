param(
    [switch]$SyncToDrive
)
$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$Utf8NoBom  = New-Object System.Text.UTF8Encoding($false)
$EnvFile    = "$ProjectDir\.env"
$ReportPath = "$ProjectDir\reports\Nov27_Payout_Preflight_$(Get-Date -Format 'yyyyMMdd').md"
$StagePath  = "$ProjectDir\Oracle_Audit_2026\Nov27_Payout_Preflight_Latest.md"

$EnvMap = @{}
if (Test-Path $EnvFile) {
    foreach ($ln in (Get-Content $EnvFile -ErrorAction SilentlyContinue)) {
        $t = $ln.Trim()
        if ($t -and (-not $t.StartsWith("#")) -and $t.Contains("=")) {
            $i = $t.IndexOf("=")
            $EnvMap[$t.Substring(0,$i).Trim()] = $t.Substring($i+1).Trim().Trim('"').Trim("'")
        }
    }
}

$LiveKey = $EnvMap["STRIPE_SECRET_KEY"]
if (-not $LiveKey) { $LiveKey = $env:STRIPE_SECRET_KEY }

# Poll Live Stripe API directly for real-time balance, payouts & account compliance
$availUsd = 0.0; $pendUsd = 0.0; $grossUsd = 0.0; $feeUsd = 0.0; $netUsd = 0.0
$payoutsEnabled = $false; $chargesEnabled = $false; $reqDueCount = 0; $liveOk = $false
$nextPayoutStr = "2026-11-27"

if ($LiveKey -and ($LiveKey -match '^(sk|rk)_live_[A-Za-z0-9]+$')) {
    try {
        $hdr = @{ Authorization = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${LiveKey}:")))" }
        $bal = Invoke-RestMethod -Uri "https://api.stripe.com/v1/balance" -Headers $hdr -Method Get -TimeoutSec 15
        $acc = Invoke-RestMethod -Uri "https://api.stripe.com/v1/account" -Headers $hdr -Method Get -TimeoutSec 15
        $txs = Invoke-RestMethod -Uri "https://api.stripe.com/v1/balance_transactions?type=charge&limit=100" -Headers $hdr -Method Get -TimeoutSec 15
        $pay = Invoke-RestMethod -Uri "https://api.stripe.com/v1/payouts?limit=5" -Headers $hdr -Method Get -TimeoutSec 15

        $availC = 0; foreach ($a in $bal.available) { if ($a.currency -eq "usd") { $availC += [int64]$a.amount } }
        $pendC  = 0; foreach ($p in $bal.pending)   { if ($p.currency -eq "usd") { $pendC  += [int64]$p.amount } }
        $availUsd = [math]::Round($availC / 100.0, 2)
        $pendUsd  = [math]::Round($pendC  / 100.0, 2)

        $gC = 0; $fC = 0; $nC = 0
        foreach ($tx in $txs.data) { $gC += [int64]$tx.amount; $fC += [int64]$tx.fee; $nC += [int64]$tx.net }
        $grossUsd = [math]::Round($gC / 100.0, 2)
        $feeUsd   = [math]::Round($fC / 100.0, 2)
        $netUsd   = [math]::Round($nC / 100.0, 2)

        $payoutsEnabled = [bool]$acc.payouts_enabled
        $chargesEnabled = [bool]$acc.charges_enabled
        $reqDueCount    = @($acc.requirements.currently_due | Where-Object { $_ }).Count
        $liveOk = $true

        if ($pay.data -and $pay.data.Count -gt 0 -and $pay.data[0].arrival_date) {
            $epoch = [DateTimeOffset]::FromUnixTimeSeconds([int64]$pay.data[0].arrival_date).UtcDateTime
            $nextPayoutStr = $epoch.ToString("yyyy-MM-dd")
        }
    } catch {
        Write-Host "[WARN] Live Stripe API poll error: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

$today     = (Get-Date).Date
$targetDt  = [datetime]::ParseExact("2026-11-27", "yyyy-MM-dd", $null)
$daysLeft  = ($targetDt - $today).Days

$taxRes    = [math]::Round($netUsd * 0.25, 2)
$postRes   = [math]::Round($netUsd - $taxRes, 2)
$tier1Host = 34.80
$leanTotal = 54.79
$buf3Mo    = 164.37
$gateUsd   = 100.00
$surp1Mo   = [math]::Round($postRes - $tier1Host, 2)
$gapGate   = [math]::Round([math]::Max(0.0, $gateUsd - $netUsd), 2)
$salesNeed = [int][math]::Ceiling($gapGate / 47.28)

# Cloud migration infrastructure readiness checks
$bundleFiles = @("deploy_bundle\sovereigncore.service","deploy_bundle\nginx_sovereigncore.conf","deploy_bundle\.env.production.template","deploy_bundle\deploy_do_tier1.sh")
$bundleReady = (@($bundleFiles | Where-Object { Test-Path "$ProjectDir\$_" }).Count -eq $bundleFiles.Count)
$sshReady    = [bool](Get-Command ssh -ErrorAction SilentlyContinue)
$pubUrl      = $EnvMap["PUBLIC_BASE_URL"]
$onTunnel    = ($pubUrl -match 'trycloudflare\.com')
$onDomain    = ($pubUrl -and ($pubUrl -notmatch '127\.0\.0\.1|localhost|trycloudflare\.com'))
$tier1Go     = ($liveOk -and $payoutsEnabled -and ($reqDueCount -eq 0) -and ($postRes -ge $tier1Host) -and $bundleReady)
$gateUnlocked = ($netUsd -ge $gateUsd)

$statusLabel = if ($gateUnlocked -and $tier1Go) { "GO - FULL TIER 1 LAUNCH UNLOCKED" }
               elseif ($tier1Go) { "CONDITIONAL GO - MONTH 1 FUNDED (HOLD UNTIL `$100 GATE OR LAUNCH NOW)" }
               else { "HOLD - STAY ON FREE CLOUDFLARE TUNNEL UNTIL REQUIREMENTS CLEAR" }

$lines = @(
    "# Oracle Systems LLC - Nov 27 Stripe Payout & DigitalOcean Tier 1 Pre-Flight",
    "- **Audit Timestamp:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') EST | **Countdown to Nov 27 Payout:** $daysLeft day(s)",
    "- **Overall Cloud Move Verdict:** $statusLabel",
    "",
    "## 1. Live Stripe Payout Reconciliation",
    "- **Stripe Live API Connected:** $liveOk | **Charges Enabled:** $chargesEnabled | **Payouts Enabled:** $payoutsEnabled | **Requirements Due:** $reqDueCount",
    ("- **Live Available Balance:** `${0:N2} | **Live Pending Balance:** `${1:N2} (Target Arrival: {2})" -f $availUsd, $pendUsd, $nextPayoutStr),
    ("- **Verified Charges Gross:** `${0:N2} | **Stripe Fees:** `${1:N2} | **Verified Net:** `${2:N2}" -f $grossUsd, $feeUsd, $netUsd),
    ("- **25% Tax Reserve Set-Aside:** `${0:N2} | **Post-Reserve Operating Cash:** `${1:N2}" -f $taxRes, $postRes),
    "",
    "## 2. DigitalOcean Tier 1 (`$34.80/mo) Funding & Runway Gates",
    ("- **Month 1 Hosting Coverage (`$34.80/mo):** Post-Reserve `${0:N2} -> Surplus/Deficit: `{1:+0.00;-0.00;0.00}` USD" -f $postRes, $surp1Mo),
    ("- **Block 10 `$100.00 Tier 1 Gate:** Gap `${0:N2} (~{1} more `$49 AuraVideo49 sale(s))" -f $gapGate, $salesNeed),
    ("- **3-Month Lean Buffer Target (Hosting + Google AI Pro = `$54.79/mo):** `${0:N2}" -f $buf3Mo),
    "",
    "## 3. Cloud Migration Technical Checklist",
    "- [$(if ($bundleReady) { 'PASS' } else { 'MISS' })] DigitalOcean deploy_bundle/ (systemd, Nginx, env template, bootstrap script)",
    "- [$(if ($sshReady)    { 'PASS' } else { 'MISS' })] Windows OpenSSH client (ssh/scp) available for 1-command deploy",
    "- [$(if ($onDomain)    { 'LIVE' } elseif ($onTunnel) { 'TEMP' } else { 'LOCAL' })] Active PUBLIC_BASE_URL: $pubUrl",
    "",
    "## Exact Launch Command When Ready",
    "  .\deploy_digitalocean_tier1.ps1 -DropletIP <YOUR_DROPLET_IPV4> -Domain oraclesystemsllc.com -BootstrapRemote"
)

$mdOut = ($lines -join "`r`n") + "`r`n"
[System.IO.File]::WriteAllText($ReportPath, $mdOut, $Utf8NoBom)
[System.IO.File]::WriteAllText($StagePath,  $mdOut, $Utf8NoBom)

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  NOV 27 STRIPE PAYOUT & TIER 1 CLOUD PRE-FLIGHT ($daysLeft DAYS TO PAYOUT)" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan
foreach ($l in $lines) {
    $col = if ($l -match '\[PASS\]|GO -') { "Green" } elseif ($l -match 'CONDITIONAL|TEMP|HOLD') { "Yellow" } elseif ($l -match '^## ') { "Cyan" } else { "White" }
    Write-Host $l -ForegroundColor $col
}
Write-Host "Saved report: $ReportPath (staged in Oracle_Audit_2026)" -ForegroundColor Gray

if ($SyncToDrive -and (Get-Command rclone -ErrorAction SilentlyContinue)) {
    rclone copy "$ProjectDir\Oracle_Audit_2026" "gdrive:Oracle_Audit_2026" --update
    Write-Host "[SYNCED] Pre-flight report synced to gdrive:Oracle_Audit_2026" -ForegroundColor Green
}