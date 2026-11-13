Set-Location "C:\Users\toome\Desktop\SovereignCore"
while ($true) {
    $Log = "$env:TEMP\lhr_live.log"
    Remove-Item $Log -Force -ErrorAction SilentlyContinue
    $Proc = Start-Process -FilePath "ssh" -ArgumentList "-o StrictHostKeyChecking=no -o ServerAliveInterval=20 -o ExitOnForwardFailure=yes -R 80:127.0.0.1:8000 nokey@localhost.run" -RedirectStandardOutput $Log -PassThru -WindowStyle Hidden
    Start-Sleep -Seconds 5
    $Url = Select-String -Path $Log -Pattern "https://[a-z0-9]+\.lhr\.life" | Select-Object -ExpandProperty Matches -Last 1
    if ($Url) {
        $Url.Value | Set-Content ".\CURRENT_TUNNEL_URL.txt"
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Active Tunnel: $($Url.Value)" -ForegroundColor Green
    }
    $Proc.WaitForExit()
    Write-Host "[!] Tunnel dropped. Reconnecting in 3 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
}
