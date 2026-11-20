# ==============================================================================
# Oracle Systems LLC - send_pronode_invoice.ps1 (Pure ASCII / PS 5.1 Safe)
# Creates, previews, and sends Stripe ACH Direct Debit invoices for Pro_Node ($49,999).
# Excludes credit cards by default to save $2,990 to $3,192 per contract.
#
# Examples:
#   .\send_pronode_invoice.ps1 -ClientName "Acme Corp" -ClientEmail "cfo@acme.com" -Milestone M1 -DryRun
#   .\send_pronode_invoice.ps1 -ClientName "Acme Corp" -ClientEmail "cfo@acme.com" -Milestone M1 -Mode TEST -SendInvoice
#   .\send_pronode_invoice.ps1 -ClientName "Acme Corp" -ClientEmail "cfo@acme.com" -Milestone M1 -Mode LIVE -SendInvoice
# ==============================================================================
param(
    [Parameter(Mandatory=$true)][string]$ClientName,
    [Parameter(Mandatory=$true)][string]$ClientEmail,
    [ValidateSet("M1","M2","Full")][string]$Milestone = "M1",
    [ValidateSet("AUTO","TEST","LIVE")][string]$Mode = "AUTO",
    [int]$DaysUntilDue = 7,
    [switch]$DryRun,
    [switch]$SendInvoice
)

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$EnvFile    = Join-Path $ProjectDir ".env"
$LogDir     = Join-Path $ProjectDir "reports\invoices"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

# Determine exact amount & description (all amounts in USD cents)
switch ($Milestone) {
    "M1"   { $AmountCents = 2499950; $AmountUsd = 24999.50; $Label = "Pro_Node Enterprise Deployment - Milestone 1 (50% Kickoff Deposit)" }
    "M2"   { $AmountCents = 2499950; $AmountUsd = 24999.50; $Label = "Pro_Node Enterprise Deployment - Milestone 2 (50% Production Handoff)" }
    "Full" { $AmountCents = 4999900; $AmountUsd = 49999.00; $Label = "Pro_Node Enterprise Deployment - Full Contract + 12-Month Dedicated HA Hosting" }
}

$EstInvFee = [math]::Round($AmountUsd * 0.004, 2)
$EstAchFee = [math]::Min([math]::Round($AmountUsd * 0.008, 2), 5.00)
$EstNet    = [math]::Round($AmountUsd - $EstInvFee - $EstAchFee, 2)

# Load .env
$EnvMap = @{}
if (Test-Path $EnvFile) {
    foreach ($line in (Get-Content $EnvFile -ErrorAction SilentlyContinue)) {
        $t = $line.Trim()
        if ($t -and (-not $t.StartsWith("#")) -and $t.Contains("=")) {
            $i = $t.IndexOf("=")
            $EnvMap[$t.Substring(0,$i).Trim()] = $t.Substring($i+1).Trim().Trim('"').Trim("'")
        }
    }
}

$LiveKey = $EnvMap["STRIPE_SECRET_KEY"]
$TestKey = $EnvMap["STRIPE_TEST_SECRET_KEY"]

if ($Mode -eq "AUTO") {
    if ($LiveKey -and ($LiveKey -match '^(sk|rk)_live_[A-Za-z0-9]+$')) { $Mode = "LIVE" }
    elseif ($TestKey -and ($TestKey -match '^(sk|rk)_test_[A-Za-z0-9]+$')) { $Mode = "TEST" }
    else { throw "No valid Stripe key found in $EnvFile." }
}

$ApiKey = if ($Mode -eq "LIVE") { $LiveKey } else { $TestKey }
if (-not $ApiKey -or ($ApiKey -notmatch '^(sk|rk)_(live|test)_[A-Za-z0-9]+$')) {
    throw "Requested Mode=$Mode but no valid $Mode Stripe key is set in $EnvFile."
}

Write-Host "=== PRO_NODE STRIPE ACH INVOICE PREVIEW [$Mode MODE] ===" -ForegroundColor Cyan
Write-Host ("Client       : {0} <{1}>" -f $ClientName, $ClientEmail)
Write-Host ("Line Item    : {0}" -f $Label)
Write-Host ("Amount Due   : `${0:N2} USD (Net {1} days)" -f $AmountUsd, $DaysUntilDue)
Write-Host ("Payment Rail : US Bank Account (ACH Direct Debit ONLY - Credit Card disabled)" ) -ForegroundColor Green
Write-Host ("Est. Fees    : `${0:N2} Invoice (0.4%) + `${1:N2} ACH (capped `$5) -> Est. Net: `${2:N2}" -f $EstInvFee, $EstAchFee, $EstNet) -ForegroundColor Green

if ($DryRun -or (-not $SendInvoice)) {
    Write-Host "`n[DRY RUN COMPLETE] No Stripe invoice was created or emailed." -ForegroundColor Yellow
    Write-Host "To create and send this $Mode invoice, re-run with -SendInvoice." -ForegroundColor Cyan
    exit 0
}

$authBytes = [System.Text.Encoding]::ASCII.GetBytes("${ApiKey}:")
$headers   = @{ Authorization = "Basic $([Convert]::ToBase64String($authBytes))" }

# 1. Create Stripe Customer
Write-Host "`n[1/4] Creating Stripe customer..." -ForegroundColor Cyan
$custBody = @{
    name  = $ClientName
    email = $ClientEmail
    description = "Oracle Systems LLC - Pro_Node Enterprise Client"
}
$cust = Invoke-RestMethod -Uri "https://api.stripe.com/v1/customers" -Headers $headers -Method Post -Body $custBody

# 2. Create Draft Invoice locked to US ACH Direct Debit
Write-Host "[2/4] Creating draft ACH invoice..." -ForegroundColor Cyan
$invBody = @{
    customer          = $cust.id
    collection_method = "send_invoice"
    days_until_due    = $DaysUntilDue
    description       = "Oracle Systems LLC - $Label (ACH Direct Debit saves card surcharges; standard US ACH clears in 4 business days)."
    "payment_settings[payment_method_types][0]" = "us_bank_account"
    "metadata[sku]"       = "pro_node"
    "metadata[milestone]" = $Milestone
}
$inv = Invoke-RestMethod -Uri "https://api.stripe.com/v1/invoices" -Headers $headers -Method Post -Body $invBody

# 3. Attach Invoice Line Item
Write-Host "[3/4] Attaching $Label line item..." -ForegroundColor Cyan
$itemBody = @{
    customer    = $cust.id
    invoice     = $inv.id
    amount      = $AmountCents
    currency    = "usd"
    description = $Label
}
Invoke-RestMethod -Uri "https://api.stripe.com/v1/invoiceitems" -Headers $headers -Method Post -Body $itemBody | Out-Null

# 4. Finalize & Send Invoice
Write-Host "[4/4] Finalizing and sending invoice via Stripe..." -ForegroundColor Cyan
$finalInv = Invoke-RestMethod -Uri "https://api.stripe.com/v1/invoices/$($inv.id)/finalize" -Headers $headers -Method Post
$sentInv  = Invoke-RestMethod -Uri "https://api.stripe.com/v1/invoices/$($inv.id)/send"     -Headers $headers -Method Post

$receipt = [ordered]@{
    mode               = $Mode
    created_utc        = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    invoice_id         = $sentInv.id
    invoice_number     = $sentInv.number
    status             = $sentInv.status
    client_name        = $ClientName
    client_email       = $ClientEmail
    milestone          = $Milestone
    amount_usd         = $AmountUsd
    hosted_invoice_url = $sentInv.hosted_invoice_url
    invoice_pdf        = $sentInv.invoice_pdf
}
$outFile = Join-Path $LogDir ("invoice_" + $Mode.ToLower() + "_" + $sentInv.id + ".json")
[System.IO.File]::WriteAllText($outFile, ($receipt | ConvertTo-Json -Depth 4), (New-Object System.Text.UTF8Encoding($false)))

Write-Host "`n[PASS] $Mode ACH Invoice Sent!" -ForegroundColor Green
Write-Host "  Invoice ID  : $($sentInv.id) (#$($sentInv.number))" -ForegroundColor White
Write-Host "  Pay URL     : $($sentInv.hosted_invoice_url)" -ForegroundColor Cyan
Write-Host "  PDF Receipt : $($sentInv.invoice_pdf)" -ForegroundColor Gray
Write-Host "  Saved Log   : $outFile" -ForegroundColor Gray