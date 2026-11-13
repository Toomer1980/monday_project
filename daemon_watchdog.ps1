Set-Location "C:\Users\toome\Desktop\SovereignCore"
New-Item -ItemType Directory -Path ".\logs" -Force | Out-Null
while ($true) {
    try {
        $Check = Invoke-WebRequest -Uri "http://127.0.0.1:8000/dashboard" -UseBasicParsing -TimeoutSec 5
    } catch {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Port 8000 unresponsive! Restarting Waitress daemon..." -ForegroundColor Red
        Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
        Start-Process -FilePath "python" -ArgumentList "sovereign_daemon.py" -WorkingDirectory "C:\Users\toome\Desktop\SovereignCore" -WindowStyle Minimized
    }
    Start-Sleep -Seconds 15
}
