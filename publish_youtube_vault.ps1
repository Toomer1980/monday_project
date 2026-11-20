# ==============================================================================
# Oracle Systems LLC - publish_youtube_vault.ps1 (v2.0 - 4D Vault + Learning Curve)
# Pulls next highest-scoring 4D Short & 4D Full Video from learning_curve_ranked_queue.json,
# stages the 4D .mp4, 3D pop-out .jpg thumbnail, animated movie-thumb, and bold 4D
# description into reports\youtube_queue\ready_to_upload\ for zero-friction publishing.
# ==============================================================================
param(
    [switch]$MarkNextPublished,
    [switch]$OpenUploadFolder
)

$ErrorActionPreference = "Stop"
$ProjectDir  = "C:\Users\toome\Desktop\SovereignCore"
Set-Location $ProjectDir

$Utf8NoBom   = New-Object System.Text.UTF8Encoding($false)
$StatePath   = Join-Path -Path $ProjectDir -ChildPath "data\youtube_publish_state.json"
$RankedPath  = Join-Path -Path $ProjectDir -ChildPath "reports\learning_curve_ranked_queue.json"
$QueueDir    = Join-Path -Path $ProjectDir -ChildPath "reports\youtube_queue"
$ReadyDir    = Join-Path -Path $QueueDir   -ChildPath "ready_to_upload"

New-Item -ItemType Directory -Path (Split-Path $StatePath) -Force | Out-Null
New-Item -ItemType Directory -Path $ReadyDir -Force | Out-Null

# Refresh Learning Curve rankings first so queue is always optimal
& (Join-Path -Path $ProjectDir -ChildPath "run_learning_curve.ps1") | Out-Null

$ranked = Get-Content $RankedPath -Raw -Encoding UTF8 | ConvertFrom-Json
$nextShort = $ranked.meta.next_recommended_short
$nextFull  = $ranked.meta.next_recommended_full

# Load state
$State = @{ published_full = @(); published_shorts = @(); last_updated = "" }
if (Test-Path $StatePath) {
    try {
        $parsed = Get-Content $StatePath -Raw | ConvertFrom-Json
        $State.published_full   = @($parsed.published_full)
        $State.published_shorts = @($parsed.published_shorts)
    } catch {}
}

Write-Host "=== 4D YOUTUBE VAULT PUBLISHER (LEARNING-CURVE RANKED) ===" -ForegroundColor Cyan
Write-Host ("Published Progress: {0}/52 Full Videos | {1}/52 Shorts" -f $State.published_full.Count, $State.published_shorts.Count) -ForegroundColor Gray

if ($nextShort) {
    $szMb = if (Test-Path $nextShort.upgraded_4d_mp4) { [math]::Round((Get-Item $nextShort.upgraded_4d_mp4).Length / 1MB, 1) } else { 0 }
    Write-Host "`n[TOP-RANKED 4D SHORT] Short #$($nextShort.sequence) | Theme: $($nextShort.theme) | Variant: $($nextShort.ab_variant) | Score: $($nextShort.ucb1_score)" -ForegroundColor Green
    Write-Host "  Video File : $($nextShort.upgraded_4d_mp4) ($szMb MB)" -ForegroundColor White
    Write-Host "  3D Thumb   : $($nextShort.thumb_3d_jpg)" -ForegroundColor Gray
    Write-Host "  A/B Title  : $($nextShort.ab_recommended_title)" -ForegroundColor Cyan
    [System.IO.File]::WriteAllText((Join-Path -Path $ReadyDir -ChildPath "NEXT_SHORT_TITLE.txt"), $nextShort.ab_recommended_title, $Utf8NoBom)
    [System.IO.File]::WriteAllText((Join-Path -Path $ReadyDir -ChildPath "NEXT_SHORT_DESCRIPTION.txt"), $nextShort.description, $Utf8NoBom)
    if (Test-Path $nextShort.thumb_3d_jpg) { Copy-Item $nextShort.thumb_3d_jpg (Join-Path -Path $ReadyDir -ChildPath "NEXT_SHORT_THUMB.jpg") -Force }
}

if ($nextFull) {
    $szMb = if (Test-Path $nextFull.upgraded_4d_mp4) { [math]::Round((Get-Item $nextFull.upgraded_4d_mp4).Length / 1MB, 1) } else { 0 }
    Write-Host "`n[TOP-RANKED 4D FULL VIDEO] Week #$($nextFull.sequence) | Theme: $($nextFull.theme) | Variant: $($nextFull.ab_variant) | Score: $($nextFull.ucb1_score)" -ForegroundColor Green
    Write-Host "  Video File : $($nextFull.upgraded_4d_mp4) ($szMb MB)" -ForegroundColor White
    Write-Host "  3D Thumb   : $($nextFull.thumb_3d_jpg)" -ForegroundColor Gray
    Write-Host "  A/B Title  : $($nextFull.ab_recommended_title)" -ForegroundColor Cyan
    [System.IO.File]::WriteAllText((Join-Path -Path $ReadyDir -ChildPath "NEXT_FULL_TITLE.txt"), $nextFull.ab_recommended_title, $Utf8NoBom)
    [System.IO.File]::WriteAllText((Join-Path -Path $ReadyDir -ChildPath "NEXT_FULL_DESCRIPTION.txt"), $nextFull.description, $Utf8NoBom)
    if (Test-Path $nextFull.thumb_3d_jpg) { Copy-Item $nextFull.thumb_3d_jpg (Join-Path -Path $ReadyDir -ChildPath "NEXT_FULL_THUMB.jpg") -Force }
}

if ($MarkNextPublished) {
    if ($nextShort) { $State.published_shorts += ($nextShort.slug + ".mp4") }
    if ($nextFull)  { $State.published_full   += ($nextFull.slug + ".mp4") }
    $State.last_updated = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    [System.IO.File]::WriteAllText($StatePath, ($State | ConvertTo-Json -Depth 4), $Utf8NoBom)
    Write-Host "`n[MARKED PUBLISHED] Logged in $StatePath & ready for next Learning Curve cycle." -ForegroundColor Cyan
}

Write-Host "`n=== LIVE UTM CLICK LEADERBOARD (/api/analytics/utm) ===" -ForegroundColor Cyan
try {
    $stats = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/analytics/utm" -Method Get -TimeoutSec 5
    Write-Host "Total Tracked Funnel Clicks: $($stats.total_clicks)" -ForegroundColor Green
    if ($stats.by_tier -and $stats.by_tier.Count -gt 0) { $stats.by_tier | Format-Table -AutoSize }
} catch {
    Write-Host "[INFO] Port 8000 offline or unreachable: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "Ready-to-upload titles, bold 4D descriptions & 3D thumbs staged in: $ReadyDir" -ForegroundColor Cyan
if ($OpenUploadFolder) { Start-Process explorer.exe $ReadyDir }