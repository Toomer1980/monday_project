param(
    [switch]$RunOnce,
    [switch]$RegisterBootTask,
    [int]$CheckIntervalSec = 60
)
$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$Utf8NoBom  = New-Object System.Text.UTF8Encoding($false)
$LockFile   = "$ProjectDir\logs\cf_watchdog.pid"
$LogFile    = "$ProjectDir\logs\cf_watchdog.log"
$PubUrlFile = "$ProjectDir\config\public_url.txt"
$StartPs    = "$ProjectDir\start_cloudflare_tunnel.ps1"

function Write-WLog([string]$msg, [string]$col = "Gray") {
    $ln = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [CF-WATCH] $msg"
    Add-Content -Path $LogFile -Value $ln
    Write-Host $ln -ForegroundColor $col
}

function Show-TunnelNotice([string]$Url) {
    try {
        Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
        Add-Type -AssemblyName System.Drawing -ErrorAction Stop
        $ni = New-Object System.Windows.Forms.NotifyIcon
        $ni.Icon = [System.Drawing.SystemIcons]::Information
        $ni.BalloonTipTitle = "Oracle Systems - Cloudflare Tunnel Active"
        $ni.BalloonTipText  = "Live URL: $Url (Webhook: $Url/api/webhook/stripe)"
        $ni.Visible = $true
        $ni.ShowBalloonTip(7000)
        Start-Sleep -Seconds 2
        $ni.Dispose()
    } catch {}
}

if ($RegisterBootTask) {
    try {
        $act  = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ProjectDir\watch_cloudflare_tunnel.ps1`"" -WorkingDirectory $ProjectDir
        $trig = New-ScheduledTaskTrigger -AtLogOn
        $set  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 0)
        Register-ScheduledTask -TaskName "OracleSystems_CloudflareTunnel_Watchdog" -Action $act -Trigger $trig -Settings $set -Description "24/7 Cloudflare HTTPS Tunnel self-healing watchdog keeping PUBLIC_BASE_URL live" -Force | Out-Null
        Write-WLog "[PASS] Registered Logon task: OracleSystems_CloudflareTunnel_Watchdog" "Green"
    } catch {
        Write-WLog "[WARN] Boot task needs Admin PS: $($_.Exception.Message)" "Yellow"
    }
    if (-not $RunOnce) { exit 0 }
}

# Single-instance guard for continuous daemon loop
if (-not $RunOnce -and (Test-Path $LockFile)) {
    $old = (Get-Content $LockFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($old -and ($old -ne "$PID") -and (Get-Process -Id $old -ErrorAction SilentlyContinue)) {
        Write-WLog "Watchdog already active (PID $old). Exiting duplicate." "Yellow"
        exit 0
    }
}
if (-not $RunOnce) { [System.IO.File]::WriteAllText($LockFile, "$PID", $Utf8NoBom) }

function Test-TunnelCycle {
    $procAlive = [bool](Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue)
    $curUrl = if (Test-Path $PubUrlFile) { (Get-Content $PubUrlFile -Raw -ErrorAction SilentlyContinue).Trim() } else { "" }
    $httpOk = $false

    if ($procAlive -and $curUrl -match '^https://') {
        try {
            $r = Invoke-WebRequest -Uri "$curUrl/store" -UseBasicParsing -TimeoutSec 8
            $httpOk = ($r.StatusCode -eq 200)
        } catch { $httpOk = $false }
    }

    if ($procAlive -and $httpOk) {
        Write-WLog "[HEALTHY] Tunnel live -> $curUrl/store (HTTP 200)" "Green"
        return
    }

    # Double-check once after 5s before restarting to avoid transient hiccups
    if ($procAlive -and $curUrl -match '^https://') {
        Start-Sleep -Seconds 5
        try {
            $r2 = Invoke-WebRequest -Uri "$curUrl/store" -UseBasicParsing -TimeoutSec 8
            if ($r2.StatusCode -eq 200) {
                Write-WLog "[RECOVERED] Tunnel responded on retry -> $curUrl" "Green"
                return
            }
        } catch {}
    }

    Write-WLog "[HEALING] Tunnel offline or unreachable -> launching fresh Cloudflare HTTPS tunnel..." "Yellow"
    & $StartPs
    $newUrl = if (Test-Path $PubUrlFile) { (Get-Content $PubUrlFile -Raw -ErrorAction SilentlyContinue).Trim() } else { "" }
    if ($newUrl -and ($newUrl -ne $curUrl)) {
        Write-WLog "[ROTATED] New live URL: $newUrl | Stripe Webhook: $newUrl/api/webhook/stripe" "Cyan"
        Show-TunnelNotice $newUrl
        if (Test-Path "$ProjectDir\sync_stripe_webhook.ps1") { & "$ProjectDir\sync_stripe_webhook.ps1" }
        if (Test-Path "$ProjectDir\run_learning_curve.ps1") { & "$ProjectDir\run_learning_curve.ps1" | Out-Null }
    }
}

try {
    if ($RunOnce) {
        Test-TunnelCycle
    } else {
        Write-WLog "Started 24/7 Cloudflare Tunnel Watchdog (PID $PID, interval ${CheckIntervalSec}s)." "Cyan"
        while ($true) {
            Test-TunnelCycle
            Start-Sleep -Seconds $CheckIntervalSec
        }
    }
} finally {
    if (-not $RunOnce) { Remove-Item $LockFile -Force -ErrorAction SilentlyContinue }
}