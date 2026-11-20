param([switch]$SkipLiveStripePoll)
$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$Utf8NoBom  = New-Object System.Text.UTF8Encoding($false)
$SnapPath   = "$ProjectDir\audit_inbox\stripe_live_api_snapshot.json"
$EnvFile    = "$ProjectDir\.env"

if (-not $SkipLiveStripePoll -and (Test-Path $EnvFile)) {
    $m = Select-String -Path $EnvFile -Pattern '^STRIPE_SECRET_KEY\s*=\s*(.+)$' | Select-Object -First 1
    if ($m) {
        $key = $m.Matches[0].Groups[1].Value.Trim().Trim('"').Trim("'")
        if ($key -match '^(sk|rk)_live_[A-Za-z0-9]+$') {
            try {
                $hdr = @{ Authorization = "Basic $([Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("${key}:")))" }
                $bal = Invoke-RestMethod -Uri "https://api.stripe.com/v1/balance" -Headers $hdr -Method Get -TimeoutSec 15
                $acc = Invoke-RestMethod -Uri "https://api.stripe.com/v1/account" -Headers $hdr -Method Get -TimeoutSec 15
                $txs = Invoke-RestMethod -Uri "https://api.stripe.com/v1/balance_transactions?type=charge&limit=100" -Headers $hdr -Method Get -TimeoutSec 15

                $availC = 0; foreach ($a in $bal.available) { if ($a.currency -eq "usd") { $availC += [int64]$a.amount } }
                $pendC  = 0; foreach ($p in $bal.pending)   { if ($p.currency -eq "usd") { $pendC  += [int64]$p.amount } }
                $gC = 0; $fC = 0; $nC = 0; $cnt = 0
                foreach ($tx in $txs.data) { $gC += [int64]$tx.amount; $fC += [int64]$tx.fee; $nC += [int64]$tx.net; $cnt++ }

                $snap = @{
                    live_api_connected = $true
                    polled_utc         = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
                    available_usd      = [math]::Round($availC / 100.0, 2)
                    pending_usd        = [math]::Round($pendC  / 100.0, 2)
                    charge_count       = $cnt
                    charges_gross_usd  = [math]::Round($gC / 100.0, 2)
                    charges_fee_usd    = [math]::Round($fC / 100.0, 2)
                    charges_net_usd    = [math]::Round($nC / 100.0, 2)
                    payouts_enabled    = [bool]$acc.payouts_enabled
                    charges_enabled    = [bool]$acc.charges_enabled
                }
                [System.IO.File]::WriteAllText($SnapPath, ($snap | ConvertTo-Json -Depth 4), $Utf8NoBom)
            } catch {
                Write-Host "[WARN] Live Stripe poll skipped: $($_.Exception.Message)" -ForegroundColor Yellow
            }
        }
    }
}

python "$ProjectDir\Modules\funnel_dashboard_engine.py" $ProjectDir $SnapPath