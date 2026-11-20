param([switch]$RegisterDailyTask)
$ErrorActionPreference = "Continue"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
Set-Location $ProjectDir

if ($RegisterDailyTask) {
    try {
        $act  = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ProjectDir\sovereign_health_autopilot.ps1`"" -WorkingDirectory $ProjectDir
        $trig = New-ScheduledTaskTrigger -Daily -At 9:00AM
        $set  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        Register-ScheduledTask -TaskName "OracleSystems_HealthAutopilot_Daily" -Action $act -Trigger $trig -Settings $set -Description "Daily 9:00 AM self-healing check for Port 8000, Cloudflare tunnel, RAM, disk, and scheduled tasks" -Force | Out-Null
        Write-Host "[PASS] Registered daily task: OracleSystems_HealthAutopilot_Daily (9:00 AM)" -ForegroundColor Green
    } catch { Write-Host "[WARN] Task registration needs Admin PS: $($_.Exception.Message)" -ForegroundColor Yellow }
}

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORACLE SYSTEMS LLC // SELF-HEALING HEALTH AUTOPILOT" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan

# 1. Port 8000 self-heal
$pUp = [bool](Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue)
if (-not $pUp) {
    Write-Host "[HEAL] Port 8000 offline -> starting sovereign_daemon.py..." -ForegroundColor Yellow
    Start-Process -FilePath "python" -ArgumentList "sovereign_daemon.py" -WorkingDirectory $ProjectDir -WindowStyle Minimized
    Start-Sleep -Seconds 4
    $pUp = [bool](Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue)
}
Write-Host ("[1/5] Port 8000 Server   : {0}" -f $(if ($pUp) { "ONLINE (PASS)" } else { "OFFLINE (FAIL)" })) -ForegroundColor $(if ($pUp) { "Green" } else { "Red" })

# 2. Cloudflare tunnel self-heal
if (Test-Path "$ProjectDir\watch_cloudflare_tunnel.ps1") {
    & "$ProjectDir\watch_cloudflare_tunnel.ps1" -RunOnce
}

# 3. RAM check & auto-trim if >80%
$os = Get-CimInstance Win32_OperatingSystem
$totGB  = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$freeGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
$ramPct = [math]::Round((($totGB - $freeGB) / $totGB) * 100.0, 1)
if ($ramPct -gt 80.0 -and (Test-Path "$ProjectDir\optimize_ram_and_boot.ps1")) {
    Write-Host "[HEAL] RAM at $ramPct% -> auto-trimming working sets..." -ForegroundColor Yellow
    & "$ProjectDir\optimize_ram_and_boot.ps1" -TrimNow | Out-Null
    $os = Get-CimInstance Win32_OperatingSystem
    $freeGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
    $ramPct = [math]::Round((($totGB - $freeGB) / $totGB) * 100.0, 1)
}
Write-Host ("[3/5] Laptop RAM Health  : {0}% used ({1} GB free of {2} GB)" -f $ramPct, $freeGB, $totGB) -ForegroundColor $(if ($ramPct -lt 82) { "Green" } else { "Yellow" })

# 4. Disk space check
$drv = Get-PSDrive C
$freeDisk = [math]::Round($drv.Free / 1GB, 1)
Write-Host ("[4/5] Disk Free Space C: : {0} GB free" -f $freeDisk) -ForegroundColor $(if ($freeDisk -gt 25) { "Green" } else { "Red" })

# 5. Scheduled Tasks & .env Git Safety
$tasks = @(Get-ScheduledTask -TaskName "OracleSystems_*" -ErrorAction SilentlyContinue)
$envTracked = [bool](git ls-files ".env" 2>$null)
Write-Host ("[5/5] Scheduled Tasks    : {0} OracleSystems_* task(s) active | .env Tracked by Git: {1}" -f $tasks.Count, $envTracked) -ForegroundColor $(if (-not $envTracked) { "Green" } else { "Red" })
if ($tasks.Count -gt 0) { $tasks | Select-Object TaskName, State | Format-Table -AutoSize }