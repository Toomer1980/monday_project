param(
    [switch]$SendLive,
    [switch]$RegisterDailyTask,
    [int]$SpacingSeconds = 35
)
$ErrorActionPreference = "Stop"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
if ($RegisterDailyTask) {
    try {
        $act  = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ProjectDir\run_pronode_followups.ps1`" -SendLive" -WorkingDirectory $ProjectDir
        $trig = New-ScheduledTaskTrigger -Daily -At 10:00AM
        $set  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        Register-ScheduledTask -TaskName "OracleSystems_ProNode_Followups_Daily" -Action $act -Trigger $trig -Settings $set -Description "Daily 10:00 AM automated 3-day follow-ups for contacted Pro_Node prospects" -Force | Out-Null
        Write-Host "[PASS] Registered daily task: OracleSystems_ProNode_Followups_Daily (10:00 AM)" -ForegroundColor Green
    } catch { Write-Host "[WARN] Task registration needs Admin PS: $($_.Exception.Message)" -ForegroundColor Yellow }
}
$mode = if ($SendLive) { "LIVE" } else { "DRYRUN" }
python "$ProjectDir\Modules\pronode_followup_engine.py" $ProjectDir $mode $SpacingSeconds