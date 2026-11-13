Write-Host "`n=== ORACLE SYSTEMS LLC // EXECUTIVE HEALTH AUDIT ===" -ForegroundColor Cyan
$Port = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
Write-Host "1. Waitress Server (8000) : $(if ($Port) { 'ONLINE (PID ' + $Port.OwningProcess + ')' } else { 'OFFLINE' })" -ForegroundColor $(if ($Port) { 'Green' } else { 'Red' })
$Tunnel = if (Test-Path ".\CURRENT_TUNNEL_URL.txt") { Get-Content ".\CURRENT_TUNNEL_URL.txt" } else { "Check Cloudflare/SSH log" }
Write-Host "2. Public Tunnel Endpoint : $Tunnel" -ForegroundColor Yellow
$Ram = Get-CimInstance Win32_OperatingSystem
$FreeGB = [math]::Round($Ram.FreePhysicalMemory / 1MB, 2)
Write-Host "3. Available System RAM   : $FreeGB GB free" -ForegroundColor Cyan
Write-Host "====================================================`n" -ForegroundColor Cyan
