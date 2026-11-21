param(
    [switch]$RegisterWeeklyTask,
    [switch]$OpenPdf,
    [switch]$SkipDriveSync
)
$ErrorActionPreference = "Continue"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
Set-Location $ProjectDir

if ($RegisterWeeklyTask) {
    try {
        $act  = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ProjectDir\generate_weekly_exec_report.ps1`"" -WorkingDirectory $ProjectDir
        $trig = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 7:00PM
        $set  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        Register-ScheduledTask -TaskName "OracleSystems_WeeklyExecReport_Sunday" -Action $act -Trigger $trig -Settings $set -Description "Weekly Sunday 7:00 PM Executive PDF + Markdown Report synced to Google Drive" -Force | Out-Null
        Write-Host "[PASS] Registered weekly task: OracleSystems_WeeklyExecReport_Sunday (Sunday 7:00 PM)" -ForegroundColor Green
    } catch { Write-Host "[WARN] Task registration needs Admin PS: $($_.Exception.Message)" -ForegroundColor Yellow }
}

# Refresh live Stripe snapshot first
if (Test-Path "$ProjectDir\funnel_dashboard.ps1") { & "$ProjectDir\funnel_dashboard.ps1" | Out-Null }

python "$ProjectDir\Modules\weekly_exec_pdf_engine.py" $ProjectDir

if (-not $SkipDriveSync -and (Get-Command rclone -ErrorAction SilentlyContinue)) {
    Write-Host "Syncing Executive PDF & Markdown report to gdrive:Oracle_Audit_2026 ..." -ForegroundColor Cyan
    rclone copy "$ProjectDir\Oracle_Audit_2026" "gdrive:Oracle_Audit_2026" --update
    if ($LASTEXITCODE -eq 0) { Write-Host "[SYNCED] Weekly Executive PDF & Markdown uploaded to Google Drive (Oracle_Audit_2026)!" -ForegroundColor Green }
}

if ($OpenPdf) {
    $pdf = Get-ChildItem "$ProjectDir\reports" -Filter "Executive_Weekly_Report_*.pdf" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($pdf) { Start-Process $pdf.FullName }
}