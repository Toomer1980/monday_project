param(
    [ValidateSet("public","unlisted","private")]
    [string]$Privacy = "public",
    [string]$ShortTime = "12:00PM",
    [string]$FullTime  = "6:00PM"
)
$ErrorActionPreference = "Stop"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"

$tasks = @(
    @{
        Name = "OracleSystems_YouTube_DailyShort"
        Args = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ProjectDir\upload_youtube_4d.ps1`" -UploadType Short -Privacy $Privacy -MaxUploads 1 -UploadNow"
        Trig = (New-ScheduledTaskTrigger -Daily -At $ShortTime)
        Desc = "Daily 12:00 PM EST automatic upload of #1 Learning-Curve-ranked 4D Short"
    },
    @{
        Name = "OracleSystems_YouTube_WeeklyFull"
        Args = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ProjectDir\upload_youtube_4d.ps1`" -UploadType FullVideo -Privacy $Privacy -MaxUploads 1 -UploadNow"
        Trig = (New-ScheduledTaskTrigger -Weekly -DaysOfWeek Friday -At $FullTime)
        Desc = "Weekly Friday 6:00 PM EST automatic upload of #1 Learning-Curve-ranked 4D Full Video"
    },
    @{
        Name = "OracleSystems_YouTube_Analytics_Daily"
        Args = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ProjectDir\pull_youtube_analytics.ps1`""
        Trig = (New-ScheduledTaskTrigger -Daily -At 7:45PM)
        Desc = "Daily 7:45 PM EST YouTube Data API v3 view/like/comment pull into UCB1 Learning Curve"
    }
)

Write-Host "=== REGISTERING AUTOMATED YOUTUBE 4D UPLOAD & ANALYTICS SCHEDULE ===" -ForegroundColor Cyan
foreach ($t in $tasks) {
    try {
        $act = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $t.Args -WorkingDirectory $ProjectDir
        $set = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        Register-ScheduledTask -TaskName $t.Name -Action $act -Trigger $t.Trig -Settings $set -Description $t.Desc -Force | Out-Null
        Write-Host "[PASS] Registered $($t.Name) ($($t.Desc))" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Could not register $($t.Name) (run Admin PS): $($_.Exception.Message)" -ForegroundColor Yellow
    }
}
Get-ScheduledTask -TaskName "OracleSystems_YouTube_*" -ErrorAction SilentlyContinue | Select-Object TaskName, State | Format-Table -AutoSize