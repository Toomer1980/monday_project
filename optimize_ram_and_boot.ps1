# ==============================================================================
# Oracle Systems LLC - optimize_ram_and_boot.ps1 (Pure ASCII / PS 5.1 Safe)
# 1) Measures RAM pressure on 7.82 GB laptop and logs top memory consumers
# 2) Safely trims idle Win32 working sets (EmptyWorkingSet) + clears temp caches
# 3) Registers clean Windows Logon tasks for sovereign_daemon.py,
#    sovereign_supervisor.ps1, and a 15-minute RAM >85% alert watchdog
#
# Examples:
#   .\optimize_ram_and_boot.ps1 -TrimNow
#   .\optimize_ram_and_boot.ps1 -TrimNow -RegisterBootTasks
#   .\optimize_ram_and_boot.ps1 -WatchdogCheck
# ==============================================================================
param(
    [switch]$TrimNow,
    [switch]$RegisterBootTasks,
    [switch]$WatchdogCheck,
    [double]$AlertThresholdPct = 85.0
)

$ErrorActionPreference = "Continue"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$LogFile    = Join-Path $ProjectDir "logs\ram_optimizer.log"
New-Item -ItemType Directory -Path (Split-Path $LogFile) -Force | Out-Null

function Write-RamLog([string]$msg, [string]$color = "Gray") {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [RAM-OPT] $msg"
    Add-Content -Path $LogFile -Value $line
    Write-Host $line -ForegroundColor $color
}

function Get-RamStats {
    $os = Get-CimInstance Win32_OperatingSystem
    $totGB  = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
    $freeGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
    $usedGB = [math]::Round($totGB - $freeGB, 2)
    $pct    = [math]::Round(($usedGB / $totGB) * 100.0, 1)
    return [PSCustomObject]@{ TotalGB = $totGB; UsedGB = $usedGB; FreeGB = $freeGB; UsedPct = $pct }
}

# Load Win32 EmptyWorkingSet P/Invoke once per session
if (-not ("OracleWin32.MemTrim" -as [type])) {
    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
namespace OracleWin32 {
    public static class MemTrim {
        [DllImport("psapi.dll", SetLastError = true)]
        public static extern bool EmptyWorkingSet(IntPtr hProcess);
    }
}
"@ -ErrorAction SilentlyContinue
}

$before = Get-RamStats
Write-RamLog ("RAM Before -> {0}% used ({1} GB used / {2} GB free of {3} GB)" -f $before.UsedPct, $before.UsedGB, $before.FreeGB, $before.TotalGB) "Cyan"

if (-not $WatchdogCheck) {
    Write-Host "`nTop 8 Memory Consumers:" -ForegroundColor Yellow
    Get-Process | Group-Object ProcessName | ForEach-Object {
        [PSCustomObject]@{
            Process   = $_.Name
            Instances = $_.Count
            RAM_MB    = [math]::Round((($_.Group | Measure-Object WorkingSet64 -Sum).Sum / 1MB), 1)
        }
    } | Sort-Object RAM_MB -Descending | Select-Object -First 8 | Format-Table -AutoSize
}

# Trim idle working sets safely if requested OR if WatchdogCheck sees RAM >= threshold
if ($TrimNow -or ($WatchdogCheck -and ($before.UsedPct -ge $AlertThresholdPct))) {
    Write-RamLog "Trimming non-critical process working sets & safe temp caches..." "Yellow"

    $trimmedCount = 0
    $protected = @("System", "Idle", "Registry", "smss", "csrss", "wininit", "services", "lsass", "Memory Compression")
    foreach ($proc in (Get-Process -ErrorAction SilentlyContinue)) {
        if ($protected -contains $proc.ProcessName) { continue }
        try {
            if ($proc.Handle -and $proc.WorkingSet64 -gt 30MB) {
                [void][OracleWin32.MemTrim]::EmptyWorkingSet($proc.Handle)
                $trimmedCount++
            }
        } catch {}
    }

    # Clear safe Python __pycache__ inside project & stale user temp files (>2 days old)
    Get-ChildItem -Path $ProjectDir -Directory -Recurse -Filter "__pycache__" -ErrorAction SilentlyContinue |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    $cutoff = (Get-Date).AddDays(-2)
    Get-ChildItem -Path $env:TEMP -File -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -lt $cutoff } |
        Remove-Item -Force -ErrorAction SilentlyContinue

    [System.GC]::Collect()
    Start-Sleep -Seconds 1

    $after = Get-RamStats
    $freedMB = [math]::Round(($after.FreeGB - $before.FreeGB) * 1024, 0)
    Write-RamLog ("RAM After  -> {0}% used ({1} GB free) | Trimmed {2} processes | Net freed: ~{3} MB" -f $after.UsedPct, $after.FreeGB, $trimmedCount, $freedMB) "Green"

    if ($after.UsedPct -ge $AlertThresholdPct) {
        Write-RamLog ("[ALERT] RAM still at {0}% (>= {1}% threshold). Close extra browser tabs or move SovereignCore to DigitalOcean Tier 1 ($34.80/mo)." -f $after.UsedPct, $AlertThresholdPct) "Red"
    }
}

# Register clean Windows Logon Boot Tasks + 15-Min RAM Watchdog
if ($RegisterBootTasks) {
    Write-Host "`n=== REGISTERING WINDOWS LOGON STARTUP & RAM WATCHDOG TASKS ===" -ForegroundColor Cyan
    $tasks = @(
        @{
            Name = "OracleSystems_SovereignDaemon_Boot"
            Exe  = "pythonw.exe"
            Args = "`"$ProjectDir\sovereign_daemon.py`""
            Trig = (New-ScheduledTaskTrigger -AtLogOn)
            Desc = "Starts Oracle Systems SovereignCore Flask daemon cleanly at Windows logon"
        },
        @{
            Name = "OracleSystems_Supervisor_Boot"
            Exe  = "powershell.exe"
            Args = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ProjectDir\sovereign_supervisor.ps1`""
            Trig = (New-ScheduledTaskTrigger -AtLogOn)
            Desc = "Runs single-instance Port 8000 self-healing watchdog at Windows logon"
        },
        @{
            Name = "OracleSystems_RAM_Watchdog_15Min"
            Exe  = "powershell.exe"
            Args = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ProjectDir\optimize_ram_and_boot.ps1`" -WatchdogCheck"
            Trig = (New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(2) -RepetitionInterval (New-TimeSpan -Minutes 15))
            Desc = "Checks laptop RAM every 15 minutes and auto-trims working sets if usage reaches 85%"
        }
    )

    foreach ($t in $tasks) {
        try {
            $act = New-ScheduledTaskAction -Execute $t.Exe -Argument $t.Args -WorkingDirectory $ProjectDir
            $set = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 0)
            Register-ScheduledTask -TaskName $t.Name -Action $act -Trigger $t.Trig -Settings $set -Description $t.Desc -Force | Out-Null
            Write-RamLog "[PASS] Registered task: $($t.Name)" "Green"
        } catch {
            Write-RamLog "[WARN] Could not register $($t.Name) (run PowerShell as Administrator): $($_.Exception.Message)" "Yellow"
        }
    }
}