# ==============================================================================
# Oracle Systems LLC - run_block10_treasury.ps1 (Pure ASCII / PS 5.1 Safe)
# 1) Polls Stripe API (/balance, /payouts, /balance_transactions, /account)
#    Separates TEST mode vs LIVE mode so sandbox data never mixes into live audit
# 2) Self-heals Port 8000 + checks RAM + rotates >5MB logs
# 3) Executes Modules\block10_treasury_engine.py
# 4) Auto-syncs Oracle_Audit_2026\ to Google Drive (rclone or Drive for Desktop)
# ==============================================================================
$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
Set-Location $ProjectDir

$Utf8NoBom  = New-Object System.Text.UTF8Encoding($false)
$LogFile    = Join-Path $ProjectDir "logs\block10_weekly.log"
$LockFile   = Join-Path $ProjectDir "logs\run_block10.pid"
$EnvFile    = Join-Path $ProjectDir ".env"
$InboxDir   = Join-Path $ProjectDir "audit_inbox"
$StagingDir = Join-Path $ProjectDir "Oracle_Audit_2026"

foreach ($d in @((Split-Path $LogFile), $InboxDir, $StagingDir)) {
    New-Item -ItemType Directory -Path $d -Force | Out-Null
}

function Write-B10Log([string]$msg, [string]$color = "Gray") {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [BLOCK10] $msg"
    Add-Content -Path $LogFile -Value $line
    Write-Host $line -ForegroundColor $color
}

if (Test-Path $LockFile) {
    $oldPid = (Get-Content $LockFile -ErrorAction SilentlyContinue | Select-Object -First 1)
    if ($oldPid -and ($oldPid -ne "$PID") -and (Get-Process -Id $oldPid -ErrorAction SilentlyContinue)) {
        Write-B10Log "Duplicate run prevented (active PID $oldPid)." "Yellow"
        exit 0
    }
}
[System.IO.File]::WriteAllText($LockFile, "$PID", $Utf8NoBom)

try {
    foreach ($lf in @((Join-Path $ProjectDir "logs\daemon.log"), $LogFile)) {
        if ((Test-Path $lf) -and ((Get-Item $lf).Length -gt 5MB)) {
            Move-Item $lf "$lf.$(Get-Date -Format 'yyyyMMdd_HHmmss').old" -Force
        }
    }

    # Load .env cleanly
    $EnvMap = @{}
    if (Test-Path $EnvFile) {
        foreach ($line in (Get-Content $EnvFile -ErrorAction SilentlyContinue)) {
            $trim = $line.Trim()
            if ($trim -and (-not $trim.StartsWith("#")) -and $trim.Contains("=")) {
                $idx = $trim.IndexOf("=")
                $k = $trim.Substring(0, $idx).Trim()
                $v = $trim.Substring($idx + 1).Trim().Trim('"').Trim("'")
                $EnvMap[$k] = $v
            }
        }
    }

    # Choose LIVE key first if valid; otherwise fall back to TEST key for sandbox telemetry
    $LiveKey = $EnvMap["STRIPE_SECRET_KEY"]
    if (-not $LiveKey) { $LiveKey = $env:STRIPE_SECRET_KEY }
    $TestKey = $EnvMap["STRIPE_TEST_SECRET_KEY"]

    $ActiveKey  = $null
    $ActiveMode = "NONE"
    if ($LiveKey -and ($LiveKey -match '^(sk|rk)_live_[A-Za-z0-9]+$')) {
        $ActiveKey  = $LiveKey
        $ActiveMode = "LIVE"
    } elseif ($TestKey -and ($TestKey -match '^(sk|rk)_test_[A-Za-z0-9]+$')) {
        $ActiveKey  = $TestKey
        $ActiveMode = "TEST"
    }

    # STEP A: STRIPE API POLLING
    $LiveSnapPath = Join-Path $InboxDir "stripe_live_api_snapshot.json"
    $TestSnapPath = Join-Path $InboxDir "stripe_test_api_snapshot.json"
    $CsvPath      = Join-Path $InboxDir ("stripe_" + $ActiveMode.ToLower() + "_api_charges.csv")

    if ($ActiveKey) {
        Write-B10Log "Polling Stripe API in $ActiveMode mode (balance, payouts, balance_transactions, account)..." "Cyan"
        try {
            $authBytes = [System.Text.Encoding]::ASCII.GetBytes("${ActiveKey}:")
            $headers   = @{ Authorization = "Basic $([Convert]::ToBase64String($authBytes))" }

            $bal  = Invoke-RestMethod -Uri "https://api.stripe.com/v1/balance" -Headers $headers -Method Get -TimeoutSec 15
            $pays = Invoke-RestMethod -Uri "https://api.stripe.com/v1/payouts?limit=10" -Headers $headers -Method Get -TimeoutSec 15
            $btx  = Invoke-RestMethod -Uri "https://api.stripe.com/v1/balance_transactions?limit=50&type=charge" -Headers $headers -Method Get -TimeoutSec 15
            $acct = $null
            try { $acct = Invoke-RestMethod -Uri "https://api.stripe.com/v1/account" -Headers $headers -Method Get -TimeoutSec 15 } catch {}

            $availUsd = 0.0
            foreach ($a in $bal.available) { if ($a.currency -eq "usd") { $availUsd += ($a.amount / 100.0) } }
            $pendUsd = 0.0
            foreach ($p in $bal.pending)   { if ($p.currency -eq "usd") { $pendUsd  += ($p.amount / 100.0) } }

            $grossSum = 0.0; $feeSum = 0.0; $netSum = 0.0; $maxSingle = 0.0; $txCount = 0
            $csvLines = @("id,created_utc,amount,fee,net,status")
            foreach ($tx in $btx.data) {
                $g = $tx.amount / 100.0
                $f = $tx.fee / 100.0
                $n = $tx.net / 100.0
                $grossSum += $g; $feeSum += $f; $netSum += $n; $txCount++
                if ($g -gt $maxSingle) { $maxSingle = $g }
                $createdUtc = ([DateTimeOffset]::FromUnixTimeSeconds([long]$tx.created)).UtcDateTime.ToString("yyyy-MM-ddTHH:mm:ssZ")
                $csvLines += "$($tx.id),$createdUtc,$([math]::Round($g,2)),$([math]::Round($f,2)),$([math]::Round($n,2)),$($tx.status)"
            }
            [System.IO.File]::WriteAllText($CsvPath, ($csvLines -join "`r`n") + "`r`n", $Utf8NoBom)

            $nextPayoutDate = $null
            if ($pays.data -and $pays.data.Count -gt 0 -and $pays.data[0].arrival_date) {
                $nextPayoutDate = ([DateTimeOffset]::FromUnixTimeSeconds([long]$pays.data[0].arrival_date)).DateTime.ToString("yyyy-MM-dd")
            }

            $reqDue = @()
            $payoutsEnabled = $null
            if ($acct) {
                $payoutsEnabled = [bool]$acct.payouts_enabled
                if ($acct.requirements -and $acct.requirements.currently_due) {
                    $reqDue = @($acct.requirements.currently_due)
                }
            }

            $snapshotObj = [ordered]@{
                stripe_mode                = $ActiveMode
                live_api_connected         = ($ActiveMode -eq "LIVE")
                polled_utc                 = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
                available_usd              = [math]::Round($availUsd, 2)
                pending_usd                = [math]::Round($pendUsd, 2)
                charge_count               = $txCount
                charges_gross_usd          = [math]::Round($grossSum, 2)
                charges_fees_usd           = [math]::Round($feeSum, 2)
                charges_net_usd            = [math]::Round($netSum, 2)
                max_single_charge_usd      = [math]::Round($maxSingle, 2)
                next_payout_arrival_date   = $nextPayoutDate
                payouts_enabled            = $payoutsEnabled
                requirements_currently_due = $reqDue
            }

            $targetSnap = if ($ActiveMode -eq "LIVE") { $LiveSnapPath } else { $TestSnapPath }
            [System.IO.File]::WriteAllText($targetSnap, ($snapshotObj | ConvertTo-Json -Depth 5), $Utf8NoBom)
            Write-B10Log ("Stripe $ActiveMode API OK -> Available: $" + ("{0:N2}" -f $availUsd) + " | Pending: $" + ("{0:N2}" -f $pendUsd) + " | Charges: $txCount | PayoutsEnabled: $payoutsEnabled") "Green"
            if ($ActiveMode -eq "TEST") {
                Write-B10Log "Note: Sandbox TEST key active (isolated from live revenue audit). Add rk_live_... to .env STRIPE_SECRET_KEY for live payouts." "Yellow"
            } elseif ($reqDue.Count -gt 0) {
                Write-B10Log ("ACTION NEEDED in Stripe Verification -> Currently Due: " + ($reqDue -join ", ")) "Yellow"
            }
        } catch {
            Write-B10Log "Stripe API poll error: $($_.Exception.Message)" "Red"
        }
    } else {
        Write-B10Log "No Stripe API key configured in .env yet - using CSV/Seed fallback." "Yellow"
    }

    # STEP B: SELF-HEAL PORT 8000 DAEMON
    $healthy = $false
    try {
        Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/download/secure-asset?token=HEALTHCHECK" -UseBasicParsing -TimeoutSec 5 | Out-Null
    } catch {
        if ($_.Exception.Response -and ($_.Exception.Response.StatusCode.value__ -eq 403)) { $healthy = $true }
    }
    if (-not $healthy) {
        Write-B10Log "Port 8000 unhealthy -> restarting sovereign_daemon.py..." "Yellow"
        Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue |
            ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
        Start-Sleep -Seconds 2
        Start-Process -FilePath "python" -ArgumentList "sovereign_daemon.py" -WorkingDirectory $ProjectDir -WindowStyle Minimized
        Start-Sleep -Seconds 4
    }

    # STEP C: RUN BLOCK 10 TREASURY ENGINE
    Write-B10Log "Running Modules\block10_treasury_engine.py..." "Cyan"
    python (Join-Path $ProjectDir "Modules\block10_treasury_engine.py")

    # STEP D: AUTOMATIC GOOGLE DRIVE SYNC (rclone -> Drive Desktop -> Local Staging)
    $synced = $false
    $rcloneRemote = if ($EnvMap["RCLONE_GDRIVE_REMOTE"]) { $EnvMap["RCLONE_GDRIVE_REMOTE"] } else { "gdrive:Oracle_Audit_2026" }

    $rcloneExe = $null
    $cmdRclone = Get-Command rclone -ErrorAction SilentlyContinue
    if ($cmdRclone) {
        $rcloneExe = $cmdRclone.Source
    } elseif (Test-Path (Join-Path $ProjectDir "tools\rclone\rclone.exe")) {
        $rcloneExe = Join-Path $ProjectDir "tools\rclone\rclone.exe"
    }

    if ($rcloneExe) {
        $remoteRoot = ($rcloneRemote.Split(":")[0]) + ":"
        $remotes = & $rcloneExe listremotes 2>$null
        if ($remotes -contains $remoteRoot) {
            Write-B10Log "Uploading Oracle_Audit_2026\ via rclone to $rcloneRemote..." "Cyan"
            & $rcloneExe copy $StagingDir $rcloneRemote --update --transfers 2
            if ($LASTEXITCODE -eq 0) {
                Write-B10Log "[PASS] Google Drive synced via rclone -> $rcloneRemote" "Green"
                $synced = $true
            }
        }
    }

    if (-not $synced) {
        $driveCandidates = @(
            "G:\My Drive",
            "H:\My Drive",
            (Join-Path $env:USERPROFILE "Google Drive\My Drive"),
            (Join-Path $env:USERPROFILE "Google Drive"),
            (Join-Path $env:USERPROFILE "My Drive")
        )
        foreach ($cand in $driveCandidates) {
            if (Test-Path $cand) {
                $dest = Join-Path $cand "Oracle_Audit_2026"
                New-Item -ItemType Directory -Path $dest -Force | Out-Null
                Copy-Item -Path (Join-Path $StagingDir "*") -Destination $dest -Recurse -Force -ErrorAction SilentlyContinue
                Write-B10Log "[PASS] Google Drive synced via Drive for Desktop -> $dest" "Green"
                $synced = $true
                break
            }
        }
    }

    if (-not $synced) {
        Write-B10Log "[STAGED] Local reports saved in $StagingDir. Run .\setup_gdrive_sync.ps1 once to authorize automatic Google Drive cloud sync." "Yellow"
    }
}
finally {
    Remove-Item $LockFile -Force -ErrorAction SilentlyContinue
}