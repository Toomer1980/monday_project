param([switch]$OpenMedia)
$ErrorActionPreference = "Stop"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
& "$ProjectDir\run_learning_curve.ps1" | Out-Null

$q = Get-Content "$ProjectDir\reports\learning_curve_ranked_queue.json" -Raw -Encoding UTF8 | ConvertFrom-Json
$s = $q.meta.next_recommended_short
if (-not $s) { Write-Host "[INFO] All 52 4D Shorts are published!" -ForegroundColor Green; exit 0 }

$szMb = if (Test-Path $s.upgraded_4d_mp4) { [math]::Round((Get-Item $s.upgraded_4d_mp4).Length / 1MB, 1) } else { 0 }
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  NEXT #1 LEARNING-CURVE 4D SHORT QUALITY INSPECTOR" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  Sequence   : Short #$($s.sequence) | Theme: $($s.theme) | Variant: $($s.ab_variant) | UCB1: $($s.ucb1_score)" -ForegroundColor Green
Write-Host "  4D Video   : $($s.upgraded_4d_mp4) ($szMb MB)" -ForegroundColor White
Write-Host "  3D Thumb   : $($s.thumb_3d_jpg)" -ForegroundColor Yellow
Write-Host "  MovieThumb : $($s.movie_thumb_mp4)" -ForegroundColor Yellow
Write-Host "  A/B Title  : $($s.ab_recommended_title)" -ForegroundColor Cyan
Write-Host "`n--- BOLD 4D DESCRIPTION (READY FOR YOUTUBE) ---" -ForegroundColor Cyan
Write-Host $s.description -ForegroundColor White

if ($OpenMedia) {
    if (Test-Path $s.thumb_3d_jpg)    { Start-Process $s.thumb_3d_jpg }
    if (Test-Path $s.upgraded_4d_mp4) { Start-Process $s.upgraded_4d_mp4 }
}