param(
    [switch]$PollStripeOrders,
    [switch]$RegisterAutoTask,
    [string]$CustomerName = "",
    [string]$CustomerEmail = "",
    [string]$FocusTopic = "Quantum Abundance & Sovereign Clarity",
    [string]$OrderId = "",
    [int]$DurationSec = 90
)
$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$Utf8NoBom  = New-Object System.Text.UTF8Encoding($false)

if ($RegisterAutoTask) {
    try {
        $act  = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ProjectDir\fulfill_aura49_order.ps1`" -PollStripeOrders -DurationSec 180" -WorkingDirectory $ProjectDir
        $trig = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(4) -RepetitionInterval (New-TimeSpan -Minutes 15)
        $set  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        Register-ScheduledTask -TaskName "OracleSystems_Aura49_AutoFulfill" -Action $act -Trigger $trig -Settings $set -Description "Polls paid $49 Stripe orders every 15 min and renders personalized 4D AuraVideo49 MP4 into deliverables\" -Force | Out-Null
        Write-Host "[PASS] Registered 15-min task: OracleSystems_Aura49_AutoFulfill" -ForegroundColor Green
    } catch { Write-Host "[WARN] Task registration needs Admin PS: $($_.Exception.Message)" -ForegroundColor Yellow }
}

if ($PollStripeOrders) {
    $envTxt = [IO.File]::ReadAllText("$ProjectDir\.env")
    $m = [regex]::Match($envTxt, '(?m)^STRIPE_SECRET_KEY\s*=\s*(.+)$')
    if (-not $m.Success) { throw "Missing STRIPE_SECRET_KEY in .env" }
    $key = $m.Groups[1].Value.Trim().Trim('"').Trim("'")
    $hdr = @{ Authorization = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${key}:")))" }
    $resp = Invoke-RestMethod -Uri "https://api.stripe.com/v1/charges?limit=50" -Headers $hdr -Method Get -TimeoutSec 20
    $chJson = "$ProjectDir\audit_inbox\stripe_live_charges_for_aura49.json"
    [IO.File]::WriteAllText($chJson, ($resp | ConvertTo-Json -Depth 6), $Utf8NoBom)
    $cfg = (@{ mode = "STRIPE_POLL"; charges_json = $chJson; duration_sec = $DurationSec } | ConvertTo-Json -Compress)
} else {
    if (-not $CustomerName) { $CustomerName = "VIP Sovereign Client" }
    if (-not $OrderId) { $OrderId = "AURA49_" + (Get-Date -Format "yyyyMMdd_HHmm") }
    $cfg = (@{ mode = "MANUAL"; customer_name = $CustomerName; customer_email = $CustomerEmail; focus_topic = $FocusTopic; order_id = $OrderId; duration_sec = $DurationSec } | ConvertTo-Json -Compress)
}

$b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($cfg))
python "$ProjectDir\Modules\aura49_custom_renderer.py" $ProjectDir $b64
if ($LASTEXITCODE -ne 0) { throw "Aura49 renderer failed (exit $LASTEXITCODE)." }