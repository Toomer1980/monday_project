# ==============================================================================
# Oracle Systems LLC - pronode_crm.ps1 (Pure ASCII / PS 5.1 Safe / Base64 IPC)
# Local SQLite CRM for $49,999 Pro_Node B2B prospects + Stripe ACH Invoicing
# ==============================================================================
param(
    [ValidateSet("Init","Add","List","Update","Due","Summary","Invoice","ExportCsv")]
    [string]$Action = "Summary",
    [int]$Id = 0,
    [string]$Company = "",
    [string]$Contact = "",
    [string]$Email = "",
    [ValidateSet("Lead","Contacted","DemoBooked","ProposalSent","InvoicedM1","ClosedWon","Lost")]
    [string]$Stage = "Lead",
    [string]$NextFollowUp = "",
    [string]$Notes = "",
    [ValidateSet("M1","M2","Full")]
    [string]$Milestone = "M1",
    [ValidateSet("AUTO","TEST","LIVE")]
    [string]$InvoiceMode = "AUTO",
    [switch]$DryRun,
    [switch]$SendInvoice,
    [switch]$ForceLive
)

$ErrorActionPreference = "Stop"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$DbPath     = Join-Path $ProjectDir "data\pronode_crm.db"
$EnginePy   = Join-Path $ProjectDir "Modules\pronode_crm_engine.py"
$ExportDir  = Join-Path $ProjectDir "reports\crm"
New-Item -ItemType Directory -Path (Split-Path $DbPath) -Force | Out-Null
New-Item -ItemType Directory -Path $ExportDir -Force | Out-Null

if (-not $NextFollowUp) {
    $NextFollowUp = (Get-Date).AddDays(3).ToString("yyyy-MM-dd")
}

function ConvertTo-B64Json([hashtable]$Obj) {
    $json = $Obj | ConvertTo-Json -Compress
    return [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($json))
}

if ($Action -eq "Invoice") {
    if ($Id -le 0) { throw "Specify -Id <prospect_id> for -Action Invoice." }
    $b64 = ConvertTo-B64Json @{ id = $Id }
    $rawRow = python $EnginePy $DbPath "GetForInvoice" $b64
    if ($LASTEXITCODE -ne 0 -or $rawRow -eq "NOT_FOUND") {
        throw "Prospect ID #$Id not found in $DbPath."
    }
    $p = $rawRow | ConvertFrom-Json

    # Safety guard: prevent emailing LIVE $24,999.50 invoices to placeholder domains
    if ($SendInvoice -and ($InvoiceMode -eq "LIVE") -and (-not $ForceLive) -and ($p.email -match '@(example|prospect|test|acme)\.(com|org|net)$')) {
        throw "SAFETY GUARD: Refusing to send a LIVE `$24,999.50 invoice to placeholder email '$($p.email)'. Use -InvoiceMode TEST or pass -ForceLive if real."
    }

    $invScript = Join-Path $ProjectDir "send_pronode_invoice.ps1"
    $clientLabel = if ($p.contact) { "$($p.company) ($($p.contact))" } else { $p.company }
    $invParams = @{
        ClientName  = $clientLabel
        ClientEmail = $p.email
        Milestone   = $Milestone
        Mode        = $InvoiceMode
    }
    if ($DryRun -or (-not $SendInvoice)) { $invParams["DryRun"] = $true }
    if ($SendInvoice) { $invParams["SendInvoice"] = $true }

    $invOutput = & $invScript @invParams
    $invOutput | Out-Host

    if ($SendInvoice) {
        $joined = ($invOutput -join "`n")
        if ($joined -match 'Invoice ID\s*:\s*(in_[A-Za-z0-9]+)') {
            $markB64 = ConvertTo-B64Json @{ id = $Id; milestone = $Milestone; invoice_id = $Matches[1] }
            python $EnginePy $DbPath "MarkInvoiced" $markB64
        }
    }
} else {
    $csvOut = Join-Path $ExportDir ("ProNode_CRM_" + (Get-Date -Format "yyyyMMdd") + ".csv")
    $b64 = ConvertTo-B64Json @{
        id            = $Id
        company       = $Company
        contact       = $Contact
        email         = $Email
        stage         = $Stage
        next_followup = $NextFollowUp
        notes         = $Notes
        export_csv    = $csvOut
    }
    python $EnginePy $DbPath $Action $b64
}