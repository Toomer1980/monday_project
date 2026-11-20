param([switch]$SkipLearningCurve)
$ErrorActionPreference = "Stop"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
Write-Host "=== PULLING LIVE YOUTUBE ANALYTICS (VIEWS / LIKES / COMMENTS) ===" -ForegroundColor Cyan
python "$ProjectDir\Modules\youtube_analytics_puller.py" $ProjectDir
if (-not $SkipLearningCurve) {
    Write-Host "`n--- Feeding Live YouTube Metrics into UCB1 Learning Curve ---" -ForegroundColor Cyan
    & "$ProjectDir\run_learning_curve.ps1"
}