# Single-Instance Self-Repair Supervisor for Oracle Systems LLC
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$LockFile   = Join-Path $ProjectDir "logs\supervisor.pid"
$LogFile    = Join-Path $ProjectDir "logs\supervisor.log"
New-Item -ItemType Directory -Path (Split-Path $LockFile) -Force | Out-Null

# Prevent duplicate supervisor windows
if (Test-Path $LockFile) {
    $oldPid = Get-Content $LockFile -ErrorAction SilentlyContinue
    if ($oldPid -and (Get-Process -Id $oldPid -ErrorAction SilentlyContinue)) {
        Write-Host "Supervisor already running under PID $oldPid. Exiting duplicate." -ForegroundColor Yellow
        exit 0
    }
}
Set-Content -Path $LockFile -Value $PID

function Write-SupLog($msg) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [SUPERVISOR] $msg"
    Add-Content -Path $LogFile -Value $line
    Write-Host $line
}

Write-SupLog "Started self-repair supervisor (PID $PID)."
while ($true) {
    try {
        # 1. Rotate daemon.log if > 5 MB
        $dLog = Join-Path $ProjectDir "logs\daemon.log"
        if ((Test-Path $dLog) -and ((Get-Item $dLog).Length -gt 5MB)) {
            Move-Item $dLog "$dLog.old" -Force
            Write-SupLog "Rotated daemon.log (>5MB)."
        }

        # 2. Health-check port 8000 -> auto-restart if down or returning 500
        $healthy = $false
        try {
            $resp = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/download/secure-asset?token=HEALTHCHECK" -UseBasicParsing -TimeoutSec 5
            $healthy = ($resp.StatusCode -lt 500)
        } catch {
            if ($_.Exception.Response -and ($_.Exception.Response.StatusCode.value__ -eq 403)) {
                $healthy = $true
            }
        }

        if (-not $healthy) {
            Write-SupLog "Port 8000 unhealthy! Restarting sovereign_daemon.py..."
            Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue |
                ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
            Start-Sleep -Seconds 2
            Start-Process -FilePath "python" -ArgumentList "sovereign_daemon.py" -WorkingDirectory $ProjectDir -WindowStyle Minimized
            Write-SupLog "Restarted sovereign_daemon.py."
        }
    } catch {
        Write-SupLog "Watchdog cycle error: $($_.Exception.Message)"
    }
    Start-Sleep -Seconds 60
}