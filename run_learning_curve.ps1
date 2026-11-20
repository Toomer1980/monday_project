# ==============================================================================
# Oracle Systems LLC - run_learning_curve.ps1 (Pure ASCII / PS 5.1 Safe)
# Executes the UCB1 Explore/Exploit Learning Curve engine to re-rank unpublished
# 4D videos by live UTM clicks + Stripe sales and rotate A/B title hooks.
# ==============================================================================
param(
    [switch]$RegisterDailyTask
)

$ErrorActionPreference = "Stop"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$EnginePy   = Join-Path -Path $ProjectDir -ChildPath "Modules\learning_curve_engine.py"

if ($RegisterDailyTask) {
    try {
        $selfPath = Join-Path -Path $ProjectDir -ChildPath "run_learning_curve.ps1"
        $act  = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$selfPath`"" -WorkingDirectory $ProjectDir
        $trig = New-ScheduledTaskTrigger -Daily -At 8:00PM
        $set  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        Register-ScheduledTask -TaskName "OracleSystems_LearningCurve_Daily" -Action $act -Trigger $trig -Settings $set -Description "Daily UCB1 Explore/Exploit re-ranking of 52-week 4D YouTube upload queue based on live clicks and Stripe sales" -Force | Out-Null
        Write-Host "[PASS] Registered daily task: OracleSystems_LearningCurve_Daily (8:00 PM EST)" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Task registration requires Admin PS: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

python $EnginePy $ProjectDir
if ($LASTEXITCODE -ne 0) { throw "Learning curve engine exited with code $LASTEXITCODE." }