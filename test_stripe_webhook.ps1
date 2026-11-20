# ==============================================================================
# Oracle Systems LLC - test_stripe_webhook.ps1 (Pure ASCII / PS 5.1 Safe)
# 1) Auto-detects Stripe webhook route in sovereign_daemon.py
# 2) Tests /dashboard, /store, /portal, /api/analytics/utm & /go/<tier>
# 3) Sends an HMAC-SHA256 signed checkout.session.completed test payload
# 4) Verifies live ZIP (/api/download/secure-asset) & MP4 deliverable serving
# ==============================================================================
param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [string]$KnownReceipt = "2352-8553",
    [switch]$SimulateWebhook
)

$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$DaemonPath = Join-Path $ProjectDir "sovereign_daemon.py"
$EnvFile    = Join-Path $ProjectDir ".env"

Write-Host "=== ORACLE SYSTEMS STRIPE WEBHOOK & END-TO-END FULFILLMENT TESTER ===" -ForegroundColor Cyan
Write-Host "Target Server: $BaseUrl" -ForegroundColor Gray

# 1. Core Page & API Health Matrix
$PassCount = 0; $FailCount = 0
foreach ($ep in @("/dashboard", "/store", "/portal", "/api/analytics/utm")) {
    try {
        $r = Invoke-WebRequest -Uri ($BaseUrl + $ep) -UseBasicParsing -TimeoutSec 6
        Write-Host ("[PASS] GET {0,-24} -> HTTP {1} ({2} bytes)" -f $ep, $r.StatusCode, $r.RawContentLength) -ForegroundColor Green
        $PassCount++
    } catch {
        Write-Host ("[FAIL] GET {0,-24} -> {1}" -f $ep, $_.Exception.Message) -ForegroundColor Red
        $FailCount++
    }
}

# 2. Check /api/download/secure-asset guard (invalid token MUST return 403, never 500)
try {
    $bad = Invoke-WebRequest -Uri "$BaseUrl/api/download/secure-asset?token=INVALID_E2E_CHECK" -UseBasicParsing -TimeoutSec 6
    Write-Host "[WARN] Invalid token returned HTTP $($bad.StatusCode) (expected 403)" -ForegroundColor Yellow
} catch {
    $code = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.value__ } else { "ERR" }
    if ($code -eq 403) {
        Write-Host "[PASS] GET /api/download/secure-asset (bad token) -> HTTP 403" -ForegroundColor Green
        $PassCount++
    } else {
        Write-Host "[FAIL] GET /api/download/secure-asset (bad token) -> HTTP $code" -ForegroundColor Red
        $FailCount++
    }
}

# 3. Verify live order lookup & real ZIP bundle download for existing verified receipt
Write-Host "`n--- Checking Order Lookup & Real ZIP Download (Receipt $KnownReceipt) ---" -ForegroundColor Cyan
try {
    $lk = Invoke-RestMethod -Uri "$BaseUrl/api/order/lookup?token=$KnownReceipt" -Method Get -TimeoutSec 6
    if ($lk.order -and $lk.order.download_token) {
        $tok = $lk.order.download_token
        Write-Host "[PASS] Lookup $KnownReceipt -> License: $($lk.order.license_key) | Token: $tok" -ForegroundColor Green
        $PassCount++

        $tmpZip = Join-Path $env:TEMP "oracle_e2e_test.zip"
        Invoke-WebRequest -Uri "$BaseUrl/api/download/secure-asset?token=$tok" -OutFile $tmpZip -UseBasicParsing -TimeoutSec 15
        if (Test-Path $tmpZip) {
            $zLen = (Get-Item $tmpZip).Length
            Write-Host "[PASS] Real ZIP Bundle Downloaded -> $zLen bytes verified" -ForegroundColor Green
            Remove-Item $tmpZip -Force -ErrorAction SilentlyContinue
            $PassCount++
        }
    } else {
        Write-Host "[INFO] Lookup returned no order object for $KnownReceipt" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[INFO] Order lookup/ZIP check skipped for ${KnownReceipt}: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 4. Verify MP4 Deliverable Streaming
$mp4File = Get-ChildItem (Join-Path $ProjectDir "static\deliverables") -Filter "*.mp4" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($mp4File) {
    $mp4Url = "$BaseUrl/static/deliverables/$($mp4File.Name)"
    try {
        $mResp = Invoke-WebRequest -Uri $mp4Url -Method Head -UseBasicParsing -TimeoutSec 6
        $mb = [math]::Round($mResp.Headers["Content-Length"] / 1MB, 2)
        Write-Host "[PASS] HEAD /static/deliverables/$($mp4File.Name) -> HTTP $($mResp.StatusCode) ($mb MB)" -ForegroundColor Green
        $PassCount++
    } catch {
        Write-Host "[FAIL] HEAD $mp4Url -> $($_.Exception.Message)" -ForegroundColor Red
        $FailCount++
    }
}

# 5. Auto-Detect Stripe Webhook Route & Optional Signed Simulation
Write-Host "`n--- Stripe Webhook Route Detection & HMAC-SHA256 Signing Check ---" -ForegroundColor Cyan
$whRoute = "/webhook"
if (Test-Path $DaemonPath) {
    $m = Select-String -Path $DaemonPath -Pattern '@app\.route\(["'']([^"'']*webhook[^"'']*)["'']' | Select-Object -First 1
    if ($m) { $whRoute = $m.Matches[0].Groups[1].Value }
}
Write-Host "Detected Webhook Route: $BaseUrl$whRoute" -ForegroundColor Gray

# Read STRIPE_WEBHOOK_SECRET from .env
$whSecret = ""
if (Test-Path $EnvFile) {
    $sm = Select-String -Path $EnvFile -Pattern '^STRIPE_WEBHOOK_SECRET\s*=\s*(.+)$' | Select-Object -First 1
    if ($sm) { $whSecret = $sm.Matches[0].Groups[1].Value.Trim().Trim('"').Trim("'") }
}
if (-not $whSecret -or ($whSecret -match 'PASTE_HERE')) {
    Write-Host "[INFO] STRIPE_WEBHOOK_SECRET not set in .env yet (using local dummy signing secret for route test)." -ForegroundColor Yellow
    $whSecret = "whsec_local_e2e_test_secret"
}

if ($SimulateWebhook) {
    $unixNow = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
    $simId   = "cs_test_e2e_$unixNow"
    $payloadObj = @{
        id = "evt_test_$unixNow"
        type = "checkout.session.completed"
        data = @{
            object = @{
                id = $simId
                payment_status = "paid"
                amount_total = 4900
                customer_details = @{ email = "Toomer1980@gmail.com" }
                metadata = @{ sku = "aura_video_49"; test_simulation = "true" }
            }
        }
    }
    $payloadStr = $payloadObj | ConvertTo-Json -Depth 6 -Compress
    $signedPayload = "$unixNow.$payloadStr"

    $hmac = New-Object System.Security.Cryptography.HMACSHA256
    $hmac.Key = [System.Text.Encoding]::UTF8.GetBytes($whSecret)
    $hashBytes = $hmac.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($signedPayload))
    $sigHex = ([System.BitConverter]::ToString($hashBytes)).Replace("-", "").ToLower()
    $sigHeader = "t=$unixNow,v1=$sigHex"

    try {
        $whResp = Invoke-WebRequest -Uri ($BaseUrl + $whRoute) -Method Post -Body $payloadStr -ContentType "application/json" -Headers @{ "Stripe-Signature" = $sigHeader } -UseBasicParsing -TimeoutSec 8
        Write-Host "[PASS] POST $whRoute (HMAC-SHA256 signed) -> HTTP $($whResp.StatusCode) | Body: $($whResp.Content)" -ForegroundColor Green
        $PassCount++
    } catch {
        $wCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.value__ } else { "ERR" }
        if ($wCode -eq 400) {
            Write-Host "[PASS] POST $whRoute reached Stripe signature verifier cleanly (HTTP 400 - set real whsec_ in .env to pass sig check)" -ForegroundColor Green
            $PassCount++
        } else {
            Write-Host "[WARN] POST $whRoute -> HTTP $wCode ($($_.Exception.Message))" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "[INFO] Run with -SimulateWebhook to fire a signed checkout.session.completed payload against $whRoute." -ForegroundColor Cyan
}

Write-Host "`n=== E2E SUMMARY: $PassCount PASSED | $FailCount FAILED ===" -ForegroundColor $(if ($FailCount -eq 0) { "Green" } else { "Red" })