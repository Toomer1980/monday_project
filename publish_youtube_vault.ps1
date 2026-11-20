# ==============================================================================
# Oracle Systems LLC - publish_youtube_vault.ps1 (Pure ASCII / PS 5.1 Safe)
# Manages 52 Full Videos + 52 Shorts publishing queue, injects UTM-tracked
# storefront links (/go/auravideo49, /go/tier29, /go/fullstorefront), and
# pulls live A/B click rankings from /api/analytics/utm.
# ==============================================================================
param(
    [switch]$MarkNextPublished,
    [string]$BaseUrl = ""
)

$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
Set-Location $ProjectDir

$Utf8NoBom  = New-Object System.Text.UTF8Encoding($false)
$FullDir    = Join-Path $ProjectDir "Content_Vault_52Weeks"
$ShortsDir  = Join-Path $ProjectDir "Content_Vault_Shorts"
$StatePath  = Join-Path $ProjectDir "data\youtube_publish_state.json"
$QueueDir   = Join-Path $ProjectDir "reports\youtube_queue"
New-Item -ItemType Directory -Path (Split-Path $StatePath) -Force | Out-Null
New-Item -ItemType Directory -Path $QueueDir -Force | Out-Null

# Resolve public base URL (prefer live domain from .env or public_url.txt; fallback to live Stripe links if local)
if (-not $BaseUrl) {
    $envFile = Join-Path $ProjectDir ".env"
    if (Test-Path $envFile) {
        $m = Select-String -Path $envFile -Pattern '^PUBLIC_BASE_URL\s*=\s*(.+)$' | Select-Object -First 1
        if ($m) { $BaseUrl = $m.Matches[0].Groups[1].Value.Trim().TrimEnd("/") }
    }
}
if (-not $BaseUrl) { $BaseUrl = "http://127.0.0.1:8000" }
$IsPublicDomain = ($BaseUrl -notmatch '127\.0\.0\.1|localhost')

# Load or initialize state
$State = @{ published_full = @(); published_shorts = @(); last_updated = "" }
if (Test-Path $StatePath) {
    try {
        $parsed = Get-Content $StatePath -Raw | ConvertFrom-Json
        $State.published_full   = @($parsed.published_full)
        $State.published_shorts = @($parsed.published_shorts)
    } catch {}
}

$FullFiles  = Get-ChildItem -Path $FullDir   -Filter "*.mp4" -ErrorAction SilentlyContinue | Sort-Object Name
$ShortFiles = Get-ChildItem -Path $ShortsDir -Filter "*.mp4" -ErrorAction SilentlyContinue | Sort-Object Name

$NextFull  = $FullFiles  | Where-Object { $State.published_full   -notcontains $_.Name } | Select-Object -First 1
$NextShort = $ShortFiles | Where-Object { $State.published_shorts -notcontains $_.Name } | Select-Object -First 1

function Build-Metadata([System.IO.FileInfo]$file, [string]$medium) {
    $slug = $file.BaseName
    $cleanTitle = ($slug -replace '^(Week|Short)_\d+_', '') -replace '_', ' '
    $prefix = if ($medium -eq "short") { "#Shorts | " } else { "Oracle Systems Collective Reading: " }
    $title = "$prefix$cleanTitle - Sudden Alignment & Breakthrough"

    if ($IsPublicDomain) {
        $auraLink  = "$BaseUrl/go/auravideo49?utm_source=youtube&utm_medium=$medium&utm_campaign=$slug"
        $tier29    = "$BaseUrl/go/tier29?utm_source=youtube&utm_medium=$medium&utm_campaign=$slug"
        $storeLink = "$BaseUrl/go/fullstorefront?utm_source=youtube&utm_medium=$medium&utm_campaign=$slug"
    } else {
        # Direct live Stripe links (work immediately even before custom cloud domain is active)
        $auraLink  = "https://buy.stripe.com/6oU28rb29evn8di7UxcQU00"
        $tier29    = "https://buy.stripe.com/bJefZheeldrj1OU8YBcQU01"
        $storeLink = "https://buy.stripe.com/28E9AT6LT0Ex79e7UxcQU03"
    }

    $desc = @"
$title

Claim your personalized 3D/4K Aura Reading Video ($49):
$auraLink

Starter Tier Access ($29):
$tier29

Full Oracle Systems Storefront Bundle ($1,500):
$storeLink

Campaign Tracking ID: $slug ($medium)
#tarot #collective #oraclesystems #breakthrough #abundance #shorts
"@
    return [ordered]@{
        file        = $file.FullName
        filename    = $file.Name
        size_mb     = [math]::Round($file.Length / 1MB, 2)
        medium      = $medium
        campaign    = $slug
        title       = $title
        description = $desc
        utm_ready   = $IsPublicDomain
    }
}

Write-Host "=== YOUTUBE 52-WEEK VAULT PUBLISHER & UTM TRACKER ===" -ForegroundColor Cyan
Write-Host ("Full Videos: {0}/{1} published | Shorts: {2}/{3} published" -f $State.published_full.Count, $FullFiles.Count, $State.published_shorts.Count, $ShortFiles.Count) -ForegroundColor Gray
Write-Host ("Link Mode: " + $(if ($IsPublicDomain) { "Tracked UTM Redirects ($BaseUrl/go/...)" } else { "Direct Live Stripe Links (upgrade to cloud domain in .env to enable public UTM clicks)" })) -ForegroundColor Gray

$Payload = [ordered]@{
    generated_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    next_short    = if ($NextShort) { Build-Metadata $NextShort "short" } else { $null }
    next_full     = if ($NextFull)  { Build-Metadata $NextFull  "video" } else { $null }
}

$QueueJsonPath = Join-Path $QueueDir "next_upload_package.json"
[System.IO.File]::WriteAllText($QueueJsonPath, ($Payload | ConvertTo-Json -Depth 6), $Utf8NoBom)

if ($Payload.next_short) {
    Write-Host "`n[NEXT DAILY SHORT] $($Payload.next_short.filename) ($($Payload.next_short.size_mb) MB)" -ForegroundColor Green
    Write-Host "  Title: $($Payload.next_short.title)" -ForegroundColor White
    [System.IO.File]::WriteAllText((Join-Path $QueueDir "next_short_description.txt"), $Payload.next_short.description, $Utf8NoBom)
}
if ($Payload.next_full) {
    Write-Host "`n[NEXT WEEKLY FULL VIDEO] $($Payload.next_full.filename) ($($Payload.next_full.size_mb) MB)" -ForegroundColor Green
    Write-Host "  Title: $($Payload.next_full.title)" -ForegroundColor White
    [System.IO.File]::WriteAllText((Join-Path $QueueDir "next_full_description.txt"), $Payload.next_full.description, $Utf8NoBom)
}

if ($MarkNextPublished) {
    if ($NextShort) { $State.published_shorts += $NextShort.Name }
    if ($NextFull)  { $State.published_full   += $NextFull.Name }
    $State.last_updated = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    [System.IO.File]::WriteAllText($StatePath, ($State | ConvertTo-Json -Depth 4), $Utf8NoBom)
    Write-Host "`n[MARKED PUBLISHED] Updated $StatePath" -ForegroundColor Cyan
}

# Pull live A/B UTM click leaderboard from local SovereignCore API
Write-Host "`n=== LIVE UTM CLICK LEADERBOARD (/api/analytics/utm) ===" -ForegroundColor Cyan
try {
    $stats = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/analytics/utm" -Method Get -TimeoutSec 5
    Write-Host "Total Tracked Funnel Clicks: $($stats.total_clicks)" -ForegroundColor Green
    if ($stats.by_tier -and $stats.by_tier.Count -gt 0) {
        $stats.by_tier | Format-Table -AutoSize
    }
    if ($stats.top_campaigns -and $stats.top_campaigns.Count -gt 0) {
        $stats.top_campaigns | Format-Table -AutoSize
    }
} catch {
    Write-Host "[INFO] Could not fetch /api/analytics/utm yet: $($_.Exception.Message)" -ForegroundColor Yellow
}
Write-Host "Upload package saved to: $QueueDir" -ForegroundColor Cyan