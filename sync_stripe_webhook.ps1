param(
    [switch]$CreateIfMissing,
    [string]$EndpointId = ""
)
$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$Utf8NoBom  = New-Object System.Text.UTF8Encoding($false)
$EnvFile    = "$ProjectDir\.env"
$PubUrlFile = "$ProjectDir\config\public_url.txt"
$IdFile     = "$ProjectDir\config\stripe_webhook_id.txt"

if (-not (Test-Path $PubUrlFile)) { throw "Missing $PubUrlFile. Run .\start_cloudflare_tunnel.ps1 first." }
$pubUrl = (Get-Content $PubUrlFile -Raw).Trim().TrimEnd("/")
if ($pubUrl -notmatch '^https://') { throw "Active URL is not HTTPS ($pubUrl). Start Cloudflare tunnel first." }
$targetUrl = "$pubUrl/api/webhook/stripe"

$envTxt = if (Test-Path $EnvFile) { [IO.File]::ReadAllText($EnvFile) } else { "" }
$m = [regex]::Match($envTxt, '(?m)^STRIPE_SECRET_KEY\s*=\s*(.+)$')
if (-not $m.Success) { throw "STRIPE_SECRET_KEY not found in $EnvFile." }
$liveKey = $m.Groups[1].Value.Trim().Trim('"').Trim("'")
if ($liveKey -notmatch '^(sk|rk)_live_[A-Za-z0-9]+$') { throw "STRIPE_SECRET_KEY in .env is not a valid LIVE key." }

$hdr = @{ Authorization = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${liveKey}:")))" }
Write-Host "=== STRIPE LIVE WEBHOOK AUTO-UPDATER ===" -ForegroundColor Cyan
Write-Host "Target Endpoint URL: $targetUrl" -ForegroundColor Gray

if (-not $EndpointId -and (Test-Path $IdFile)) {
    $EndpointId = (Get-Content $IdFile -Raw -ErrorAction SilentlyContinue).Trim()
}

$list = Invoke-RestMethod -Uri "https://api.stripe.com/v1/webhook_endpoints?limit=50" -Headers $hdr -Method Get -TimeoutSec 20
$matchEp = $null
foreach ($ep in @($list.data)) {
    if ($EndpointId -and ($ep.id -eq $EndpointId)) { $matchEp = $ep; break }
}
if (-not $matchEp) {
    foreach ($ep in @($list.data)) {
        if ($ep.url -match '/api/webhook/stripe') { $matchEp = $ep; break }
    }
}

if ($matchEp) {
    [IO.File]::WriteAllText($IdFile, $matchEp.id, $Utf8NoBom)
    if ($matchEp.url -eq $targetUrl -and $matchEp.status -eq "enabled") {
        Write-Host "[PASS] Stripe webhook $($matchEp.id) already synced -> $targetUrl" -ForegroundColor Green
        exit 0
    }
    $body = "url=$([uri]::EscapeDataString($targetUrl))&disabled=false"
    $upd  = Invoke-RestMethod -Uri "https://api.stripe.com/v1/webhook_endpoints/$($matchEp.id)" -Headers $hdr -Method Post -ContentType "application/x-www-form-urlencoded" -Body $body -TimeoutSec 20
    Write-Host "[UPDATED] Stripe webhook $($upd.id) rotated cleanly -> $($upd.url) (signing secret unchanged!)" -ForegroundColor Green
    exit 0
}

if (-not $CreateIfMissing) {
    Write-Host "[INFO] No existing '/api/webhook/stripe' webhook endpoint found in LIVE Stripe." -ForegroundColor Yellow
    Write-Host "  -> Run .\sync_stripe_webhook.ps1 -CreateIfMissing to create it & save STRIPE_WEBHOOK_SECRET automatically!" -ForegroundColor Cyan
    exit 0
}

Write-Host "Creating new LIVE Stripe webhook endpoint -> $targetUrl ..." -ForegroundColor Cyan
$events = @("checkout.session.completed","invoice.paid","payment_intent.succeeded")
$parts  = @("url=$([uri]::EscapeDataString($targetUrl))")
foreach ($ev in $events) { $parts += "enabled_events[]=$([uri]::EscapeDataString($ev))" }
$createBody = $parts -join "&"

$created = Invoke-RestMethod -Uri "https://api.stripe.com/v1/webhook_endpoints" -Headers $hdr -Method Post -ContentType "application/x-www-form-urlencoded" -Body $createBody -TimeoutSec 20
[IO.File]::WriteAllText($IdFile, $created.id, $Utf8NoBom)

if ($created.secret) {
    if ($envTxt -match '(?m)^STRIPE_WEBHOOK_SECRET=.*$') {
        $envTxt = [regex]::Replace($envTxt, '(?m)^STRIPE_WEBHOOK_SECRET=.*$', "STRIPE_WEBHOOK_SECRET=$($created.secret)")
    } else {
        $envTxt = $envTxt.TrimEnd() + "`r`nSTRIPE_WEBHOOK_SECRET=$($created.secret)`r`n"
    }
    [IO.File]::WriteAllText($EnvFile, $envTxt, $Utf8NoBom)
    Write-Host "[CREATED & SAVED] Live webhook $($created.id) active & new STRIPE_WEBHOOK_SECRET stored in .env!" -ForegroundColor Green
} else {
    Write-Host "[CREATED] Live webhook $($created.id) active at $($created.url)." -ForegroundColor Green
}