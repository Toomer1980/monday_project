# Automated Git Synchronizer for monday_project & SovereignCore
$ErrorActionPreference = "Stop"

Write-Host ">>> Initiating Git Sync Sequence..." -ForegroundColor Cyan

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Git executable not found in PATH."
}

$status = git status --porcelain
$timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
$committed = $false
$commitMsg = ""

if (-not $status) {
    Write-Host "[=] Working tree clean. Pushing latest upstream state..." -ForegroundColor Green
} else {
    Write-Host "[*] Changes detected. Staging all files..." -ForegroundColor Yellow
    git add -A
    $commitMsg = "SovereignCore Auto-Sync [$timestamp] Telemetry & Swarm Updates"
    git commit -m $commitMsg
    Write-Host "[+] Committed: $commitMsg" -ForegroundColor Green
    $committed = $true
}

$currentBranch = (git rev-parse --abbrev-ref HEAD).Trim()
Write-Host "[*] Pushing to remote branch: $currentBranch..." -ForegroundColor Yellow

try {
    git push origin $currentBranch
    Write-Host "[+] Push sequence complete. Upstream synchronized." -ForegroundColor Green

    # Webhook Notification to Local Gateway
    $tokenPath = "C:\Users\toome\Desktop\SovereignCore\config\api_key.token"
    if (Test-Path $tokenPath) {
        $key = (Get-Content $tokenPath).Trim()
        $webhookPayload = @{
            branch    = $currentBranch
            timestamp = $timestamp
            commit    = if ($committed) { $commitMsg } else { "Tree was clean - head validated" }
        } | ConvertTo-Json

        $headers = @{
            "X-API-Key"    = $key
            "Content-Type" = "application/json"
        }
        
        Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/webhook/git-sync" -Method POST -Headers $headers -Body $webhookPayload -ErrorAction SilentlyContinue | Out-Null
        Write-Host "[+] Webhook dispatched to SovereignCore gateway." -ForegroundColor Green
    }
} catch {
    Write-Host "[!] Git push or webhook failed: $_" -ForegroundColor Red
}