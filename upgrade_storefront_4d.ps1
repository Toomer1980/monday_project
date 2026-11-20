$ErrorActionPreference = "Stop"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$Ts  = Get-Date -Format "yyyyMMdd_HHmmss"
$Bak = "$ProjectDir\backups\store4d_$Ts"
New-Item -ItemType Directory -Path $Bak -Force | Out-Null

python "$ProjectDir\Modules\storefront_4d_patcher.py" $ProjectDir $Bak
if ($LASTEXITCODE -ne 0) { throw "Storefront patcher failed." }

# Restart Port 8000 cleanly and verify HTTP 200 (auto-rollback if unhealthy)
Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue |
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2
Start-Process -FilePath "python" -ArgumentList "sovereign_daemon.py" -WorkingDirectory $ProjectDir -WindowStyle Minimized
Start-Sleep -Seconds 4

$ok = $false
try {
    $r1 = Invoke-WebRequest -Uri "http://127.0.0.1:8000/store"  -UseBasicParsing -TimeoutSec 6
    $r2 = Invoke-WebRequest -Uri "http://127.0.0.1:8000/portal" -UseBasicParsing -TimeoutSec 6
    $ok = ($r1.StatusCode -eq 200 -and $r2.StatusCode -eq 200 -and ($r1.Content -match 'oracle-4d-hero') -and ($r2.Content -match 'oracle-portal-upsell'))
} catch { $ok = $false }

if ($ok) {
    Write-Host "[LIVE PASS] Port 8000 restarted -> /store 4D Hero + /portal Upsell verified HTTP 200!" -ForegroundColor Green
} else {
    Write-Host "[ROLLBACK] Health check failed -> restoring previous sovereign_daemon.py from $Bak" -ForegroundColor Red
    Copy-Item "$Bak\sovereign_daemon.py.bak" "$ProjectDir\sovereign_daemon.py" -Force
    Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue |
        ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Start-Process -FilePath "python" -ArgumentList "sovereign_daemon.py" -WorkingDirectory $ProjectDir -WindowStyle Minimized
    throw "Rolled back sovereign_daemon.py safely."
}