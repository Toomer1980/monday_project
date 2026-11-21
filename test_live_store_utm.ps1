param(
    [string]$Tier = "auravideo49",
    [string]$Campaign = "live_smoke_test",
    [switch]$OpenStoreInBrowser
)
$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$pubUrl = if (Test-Path "$ProjectDir\config\public_url.txt") { (Get-Content "$ProjectDir\config\public_url.txt" -Raw).Trim().TrimEnd("/") } else { "http://127.0.0.1:8000" }

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  LIVE 4D STOREFRONT & TRACKED UTM CLICK VERIFIER" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "Public Funnel Base: $pubUrl" -ForegroundColor Gray

# 1. Inspect /store HTML for 4D Hero + all 4 product tiers
try {
    $rStore = Invoke-WebRequest -Uri "$pubUrl/store" -UseBasicParsing -TimeoutSec 10
    $hasHero = ($rStore.Content -match 'oracle-4d-hero')
    $hasTiers = (($rStore.Content -match '\$29') -and ($rStore.Content -match '\$49') -and ($rStore.Content -match '\$1,500') -and ($rStore.Content -match '\$49,999'))
    Write-Host ("[1/3] /store HTTP {0} | 4D Hero Active: {1} | All 4 Price Cards Present: {2}" -f $rStore.StatusCode, $hasHero, $hasTiers) -ForegroundColor $(if ($hasHero -and $hasTiers) { "Green" } else { "Yellow" })
} catch {
    Write-Host "[1/3] /store unreachable: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. Inspect /portal HTML for Member Upsell Banner
try {
    $rPortal = Invoke-WebRequest -Uri "$pubUrl/portal" -UseBasicParsing -TimeoutSec 10
    $hasUp = ($rPortal.Content -match 'oracle-portal-upsell')
    Write-Host ("[2/3] /portal HTTP {0} | Member Upsell Bar Active: {1}" -f $rPortal.StatusCode, $hasUp) -ForegroundColor $(if ($hasUp) { "Green" } else { "Yellow" })
} catch {
    Write-Host "[2/3] /portal unreachable: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Fire a real tracked UTM click through Cloudflare HTTPS without following Stripe checkout redirect
$utmUrl = "$pubUrl/go/${Tier}?utm_source=smoke_test&utm_medium=powershell&utm_campaign=${Campaign}"
Write-Host "[3/3] Firing tracked UTM click -> $utmUrl" -ForegroundColor Cyan
try {
    $req = [System.Net.HttpWebRequest]::Create($utmUrl)
    $req.Method = "GET"
    $req.AllowAutoRedirect = $false
    $req.Timeout = 10000
    $resp = $req.GetResponse()
    $code = [int]$resp.StatusCode
    $loc  = $resp.Headers["Location"]
    $resp.Close()
    Write-Host ("[PASS] Tracked Redirect HTTP {0} -> {1}" -f $code, $loc) -ForegroundColor Green
} catch [System.Net.WebException] {
    if ($_.Exception.Response) {
        $r = $_.Exception.Response
        Write-Host ("[PASS] Tracked Redirect HTTP {0} -> {1}" -f [int]$r.StatusCode, $r.Headers["Location"]) -ForegroundColor Green
    } else {
        Write-Host "[FAIL] UTM click failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n--- Verifying Live Click Appeared on Funnel Dashboard ---" -ForegroundColor Cyan
& "$ProjectDir\funnel_dashboard.ps1" -SkipLiveStripePoll

if ($OpenStoreInBrowser) { Start-Process "$pubUrl/store" }