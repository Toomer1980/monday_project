# ==============================================================================
# Oracle Systems LLC - reconcile_stripe_crm.ps1 (Pure ASCII / PS 5.1 Safe)
# Polls Stripe /v1/invoices?status=paid, updates data\pronode_crm.db when any
# $24,999.50 M1 or $49,999 Pro_Node invoice is paid, and unlocks Tier 3 HA gate.
#
# Examples:
#   .\reconcile_stripe_crm.ps1
#   .\reconcile_stripe_crm.ps1 -Mode TEST
#   .\reconcile_stripe_crm.ps1 -RegisterTask
# ==============================================================================
param(
    [ValidateSet("AUTO","LIVE","TEST")]
    [string]$Mode = "AUTO",
    [switch]$RegisterTask,
    [int]$IntervalMinutes = 30
)

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$EnvFile    = Join-Path -Path $ProjectDir -ChildPath ".env"
$EnginePy   = Join-Path -Path $ProjectDir -ChildPath "Modules\stripe_crm_reconciler.py"
$InboxDir   = Join-Path -Path $ProjectDir -ChildPath "audit_inbox"
$Utf8NoBom  = New-Object System.Text.UTF8Encoding($false)
New-Item -ItemType Directory -Path $InboxDir -Force | Out-Null

if ($RegisterTask) {
    try {
        $selfPath = Join-Path -Path $ProjectDir -ChildPath "reconcile_stripe_crm.ps1"
        $act  = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$selfPath`" -Mode LIVE" -WorkingDirectory $ProjectDir
        $trig = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(3) -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes)
        $set  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        Register-ScheduledTask -TaskName "OracleSystems_StripeCRM_Reconciler" -Action $act -Trigger $trig -Settings $set -Description "Polls paid Stripe Pro_Node invoices every $IntervalMinutes min, updates CRM, and unlocks Tier 3 HA gate" -Force | Out-Null
        Write-Host "[PASS] Registered task: OracleSystems_StripeCRM_Reconciler (every $IntervalMinutes min)" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Task registration requires Admin PS: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

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

$LiveKey = $EnvMap["STRIPE_SECRET_KEY"]
if (-not $LiveKey) { $LiveKey = $env:STRIPE_SECRET_KEY }
$TestKey = $EnvMap["STRIPE_TEST_SECRET_KEY"]

if ($Mode -eq "AUTO") {
    if ($LiveKey -and ($LiveKey -match '^(sk|rk)_live_[A-Za-z0-9]+$')) { $Mode = "LIVE" }
    elseif ($TestKey -and ($TestKey -match '^(sk|rk)_test_[A-Za-z0-9]+$')) { $Mode = "TEST" }
    else { throw "No valid Stripe API key found in $EnvFile." }
}

$ApiKey = if ($Mode -eq "LIVE") { $LiveKey } else { $TestKey }
if (-not $ApiKey -or ($ApiKey -notmatch '^(sk|rk)_(live|test)_[A-Za-z0-9]+$')) {
    throw "Requested Mode=$Mode but no valid $Mode Stripe key is set in $EnvFile."
}

Write-Host "=== STRIPE-TO-CRM AUTO-RECONCILER [$Mode MODE] ===" -ForegroundColor Cyan
$authBytes = [System.Text.Encoding]::ASCII.GetBytes("${ApiKey}:")
$headers   = @{ Authorization = "Basic $([Convert]::ToBase64String($authBytes))" }

$resp = Invoke-RestMethod -Uri "https://api.stripe.com/v1/invoices?status=paid&limit=50" -Headers $headers -Method Get -TimeoutSec 20
$count = if ($resp.data) { $resp.data.Count } else { 0 }
Write-Host ("Fetched {0} paid Stripe invoice(s) in {1} mode." -f $count, $Mode) -ForegroundColor Gray

$outJson = Join-Path -Path $InboxDir -ChildPath ("stripe_paid_invoices_" + $Mode.ToLower() + ".json")
[System.IO.File]::WriteAllText($outJson, ($resp | ConvertTo-Json -Depth 6), $Utf8NoBom)

python $EnginePy $ProjectDir $outJson $Mode