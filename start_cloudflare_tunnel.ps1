param(
    [int]$Port = 8000,
    [switch]$StopTunnel
)
$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$Utf8NoBom  = New-Object System.Text.UTF8Encoding($false)
$PidFile    = "$ProjectDir\logs\cloudflared.pid"
$ErrLog     = "$ProjectDir\logs\cloudflared_err.log"
$OutLog     = "$ProjectDir\logs\cloudflared_out.log"
$HistLog    = "$ProjectDir\logs\tunnel_history.log"
$EnvFile    = "$ProjectDir\.env"
$PubUrlFile = "$ProjectDir\config\public_url.txt"
$LocalExe   = "$ProjectDir\tools\cloudflared.exe"

if (Test-Path $PidFile) {
    $oldP = (Get-Content $PidFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($oldP) { Stop-Process -Id $oldP -Force -ErrorAction SilentlyContinue }
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}
Get-Process -Name "cloudflared" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

if ($StopTunnel) {
    Write-Host "[STOPPED] Cloudflare tunnel terminated." -ForegroundColor Yellow
    exit 0
}

$cfExe = $null
$cmd = Get-Command cloudflared -ErrorAction SilentlyContinue
if ($cmd) { $cfExe = $cmd.Source }
elseif (Test-Path $LocalExe) { $cfExe = $LocalExe }
else {
    Write-Host "Downloading official cloudflared binary for Windows x64..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "$ProjectDir\tools" -Force | Out-Null
    Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile $LocalExe -UseBasicParsing
    if (Test-Path $LocalExe) { $cfExe = $LocalExe }
}
if (-not $cfExe) { throw "Could not locate or download cloudflared.exe." }

if (-not (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)) {
    Write-Host "Port $Port offline -> starting sovereign_daemon.py..." -ForegroundColor Yellow
    Start-Process -FilePath "python" -ArgumentList "sovereign_daemon.py" -WorkingDirectory $ProjectDir -WindowStyle Minimized
    Start-Sleep -Seconds 3
}

Remove-Item $ErrLog, $OutLog -Force -ErrorAction SilentlyContinue
Write-Host "Starting free Cloudflare HTTPS tunnel -> http://127.0.0.1:$Port ..." -ForegroundColor Cyan
$proc = Start-Process -FilePath $cfExe -ArgumentList "tunnel --url http://127.0.0.1:$Port --no-autoupdate" -RedirectStandardError $ErrLog -RedirectStandardOutput $OutLog -WindowStyle Hidden -PassThru
[System.IO.File]::WriteAllText($PidFile, "$($proc.Id)", $Utf8NoBom)

$liveUrl = $null
for ($i = 0; $i -lt 25; $i++) {
    Start-Sleep -Seconds 1
    foreach ($lf in @($ErrLog, $OutLog)) {
        if (Test-Path $lf) {
            $txt = Get-Content $lf -Raw -ErrorAction SilentlyContinue
            if ($txt -match 'https://[a-z0-9\-]+\.trycloudflare\.com') { $liveUrl = $Matches[0]; break }
        }
    }
    if ($liveUrl) { break }
}

if (-not $liveUrl) {
    Write-Host "[FAIL] Timed out waiting for Cloudflare URL. Check $ErrLog" -ForegroundColor Red
    exit 1
}

[System.IO.File]::WriteAllText($PubUrlFile, $liveUrl, $Utf8NoBom)
Add-Content -Path $HistLog -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [TUNNEL] LIVE=$liveUrl PID=$($proc.Id) WEBHOOK=$liveUrl/api/webhook/stripe"

if (Test-Path $EnvFile) {
    $envTxt = [System.IO.File]::ReadAllText($EnvFile)
    if ($envTxt -match '(?m)^PUBLIC_BASE_URL=.*$') {
        $envTxt = [regex]::Replace($envTxt, '(?m)^PUBLIC_BASE_URL=.*$', "PUBLIC_BASE_URL=$liveUrl")
    } else {
        $envTxt = $envTxt.TrimEnd() + "`r`nPUBLIC_BASE_URL=$liveUrl`r`n"
    }
    [System.IO.File]::WriteAllText($EnvFile, $envTxt, $Utf8NoBom)
}

Write-Host "[PASS] Cloudflare HTTPS Tunnel LIVE (PID $($proc.Id)): $liveUrl" -ForegroundColor Green
Write-Host "       Updated .env PUBLIC_BASE_URL & config\public_url.txt" -ForegroundColor Gray

$verified = $false
for ($try = 1; $try -le 6; $try++) {
    Start-Sleep -Seconds 3
    try {
        $rStore  = Invoke-WebRequest -Uri "$liveUrl/store"  -UseBasicParsing -TimeoutSec 8
        $rPortal = Invoke-WebRequest -Uri "$liveUrl/portal" -UseBasicParsing -TimeoutSec 8
        Write-Host "[PASS] Public HTTPS Verified -> $liveUrl/store (HTTP $($rStore.StatusCode)) | $liveUrl/portal (HTTP $($rPortal.StatusCode))" -ForegroundColor Green
        $verified = $true
        break
    } catch {
        Write-Host "  Waiting for fresh DNS propagation ($try/6)..." -ForegroundColor DarkGray
    }
}
if (-not $verified) { Write-Host "[INFO] Tunnel live at $liveUrl (ISP DNS may take 20-30s)." -ForegroundColor Yellow }