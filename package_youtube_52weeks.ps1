# ==============================================================================
# Oracle Systems LLC - package_youtube_52weeks.ps1 (Pure ASCII / PS 5.1 Safe)
# Scans all 52 Full Videos + 52 Shorts on disk, builds a full 1-year schedule,
# generates SEO titles, hashtags, and live Stripe funnel descriptions, and
# exports reports\youtube_52week_manifest.csv + .json (+ Oracle_Audit_2026 copy).
#
# Examples:
#   .\package_youtube_52weeks.ps1
#   .\package_youtube_52weeks.ps1 -StartDate "2026-11-21" -BaseUrl "https://oraclesystemsllc.com"
# ==============================================================================
param(
    [string]$StartDate = "",
    [string]$BaseUrl = ""
)

$ErrorActionPreference = "Stop"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$FullDir    = Join-Path -Path $ProjectDir -ChildPath "Content_Vault_52Weeks"
$ShortsDir  = Join-Path -Path $ProjectDir -ChildPath "Content_Vault_Shorts"
$ReportsDir = Join-Path -Path $ProjectDir -ChildPath "reports"
$StagingDir = Join-Path -Path $ProjectDir -ChildPath "Oracle_Audit_2026"
$Utf8NoBom  = New-Object System.Text.UTF8Encoding($false)

New-Item -ItemType Directory -Path $ReportsDir -Force | Out-Null
New-Item -ItemType Directory -Path $StagingDir -Force | Out-Null

$startDt = if ($StartDate) { [datetime]::ParseExact($StartDate, "yyyy-MM-dd", $null) } else { (Get-Date).Date.AddDays(1) }

# Resolve public domain if configured in .env
if (-not $BaseUrl) {
    $envFile = Join-Path -Path $ProjectDir -ChildPath ".env"
    if (Test-Path $envFile) {
        $m = Select-String -Path $envFile -Pattern '^PUBLIC_BASE_URL\s*=\s*(.+)$' | Select-Object -First 1
        if ($m) { $BaseUrl = $m.Matches[0].Groups[1].Value.Trim().TrimEnd("/") }
    }
}
$useUtm = ($BaseUrl -and ($BaseUrl -notmatch '127\.0\.0\.1|localhost'))

function Build-ManifestRow([System.IO.FileInfo]$file, [string]$kind, [int]$index, [datetime]$pubDate) {
    $slug = $file.BaseName
    $topic = ($slug -replace '^(Week|Short)_\d+_', '') -replace '_', ' '
    $num = "{0:D2}" -f ($index + 1)

    if ($kind -eq "Short") {
        $seoTitle = "#Shorts $topic | Oracle Systems Collective Reading (#$num)"
        $tags     = "shorts,tarot,collective reading,oracle systems,$($topic.ToLower()),breakthrough,abundance"
        $thumbTxt = ($topic.ToUpper() + " // SHIFT NOW")
        $pubTime  = "12:00 EST"
    } else {
        $seoTitle = "Week $num Collective Reading: $topic - Sudden Financial & Spiritual Alignment"
        $tags     = "tarot reading,collective tarot,oracle systems,$($topic.ToLower()),financial breakthrough,2026 tarot,2027 tarot"
        $thumbTxt = ("WEEK $num : " + $topic.ToUpper())
        $pubTime  = "18:00 EST"
    }

    if ($useUtm) {
        $med = $kind.ToLower()
        $link49   = "$BaseUrl/go/auravideo49?utm_source=youtube&utm_medium=$med&utm_campaign=$slug"
        $link29   = "$BaseUrl/go/tier29?utm_source=youtube&utm_medium=$med&utm_campaign=$slug"
        $link1500 = "$BaseUrl/go/fullstorefront?utm_source=youtube&utm_medium=$med&utm_campaign=$slug"
    } else {
        $link49   = "https://buy.stripe.com/6oU28rb29evn8di7UxcQU00"
        $link29   = "https://buy.stripe.com/bJefZheeldrj1OU8YBcQU01"
        $link1500 = "https://buy.stripe.com/28E9AT6LT0Ex79e7UxcQU03"
    }

    $desc = @(
        $seoTitle,
        "",
        "Order your Personalized 3D/4K Aura Reading Video (`$49): $link49",
        "Starter Tier Access (`$29): $link29",
        "Full Oracle Systems Storefront Bundle (`$1,500): $link1500",
        "",
        "Campaign ID: $slug | Oracle Systems LLC",
        "#tarot #collective #oraclesystems #breakthrough #abundance"
    ) -join "`n"

    return [PSCustomObject][ordered]@{
        Sequence       = $num
        Type           = $kind
        PublishDate    = $pubDate.ToString("yyyy-MM-dd")
        PublishTime    = $pubTime
        FileName       = $file.Name
        FilePath       = $file.FullName
        SizeMB         = [math]::Round($file.Length / 1MB, 2)
        ThumbnailText  = $thumbTxt
        SeoTitle       = $seoTitle
        Tags           = $tags
        PrimaryCtaUrl  = $link49
        StorefrontUrl  = $link1500
        Description    = $desc
    }
}

$FullFiles  = Get-ChildItem -Path $FullDir   -Filter "*.mp4" -ErrorAction SilentlyContinue | Sort-Object Name
$ShortFiles = Get-ChildItem -Path $ShortsDir -Filter "*.mp4" -ErrorAction SilentlyContinue | Sort-Object Name

# Schedule: 1 Short per day starting startDt; 1 Full Video every Friday starting next Friday
$daysToFri = (5 - [int]$startDt.DayOfWeek + 7) % 7
$firstFri  = $startDt.AddDays($daysToFri)

$Rows = @()
for ($i = 0; $i -lt $ShortFiles.Count; $i++) {
    $Rows += Build-ManifestRow $ShortFiles[$i] "Short" $i ($startDt.AddDays($i))
}
for ($i = 0; $i -lt $FullFiles.Count; $i++) {
    $Rows += Build-ManifestRow $FullFiles[$i] "FullVideo" $i ($firstFri.AddDays($i * 7))
}

$Rows = $Rows | Sort-Object PublishDate, Type

$CsvOut  = Join-Path -Path $ReportsDir -ChildPath "youtube_52week_manifest.csv"
$JsonOut = Join-Path -Path $ReportsDir -ChildPath "youtube_52week_manifest.json"

$Rows | Export-Csv -Path $CsvOut -NoTypeInformation -Encoding UTF8
[System.IO.File]::WriteAllText($JsonOut, ($Rows | ConvertTo-Json -Depth 4), $Utf8NoBom)

# Stage manifest CSV in Oracle_Audit_2026 for Google Drive visibility
Copy-Item -Path $CsvOut -Destination (Join-Path -Path $StagingDir -ChildPath "youtube_52week_manifest.csv") -Force

$totalMB = [math]::Round((($Rows | Measure-Object SizeMB -Sum).Sum), 1)
Write-Host "=== 52-WEEK YOUTUBE BATCH MANIFEST PACKAGED ===" -ForegroundColor Cyan
Write-Host ("Total Assets  : {0} Full Videos + {1} Shorts = {2} Scheduled Uploads ({3} MB total)" -f $FullFiles.Count, $ShortFiles.Count, $Rows.Count, $totalMB) -ForegroundColor Green
Write-Host ("Schedule Span : {0} through {1}" -f $Rows[0].PublishDate, $Rows[-1].PublishDate) -ForegroundColor White
Write-Host ("Link Mode     : " + $(if ($useUtm) { "UTM Redirects ($BaseUrl/go/...)" } else { "Direct Live Stripe Payment Links" })) -ForegroundColor Gray
Write-Host ("Manifest CSV  : $CsvOut") -ForegroundColor Cyan
Write-Host ("Manifest JSON : $JsonOut") -ForegroundColor Cyan