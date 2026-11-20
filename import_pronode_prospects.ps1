# ==============================================================================
# Oracle Systems LLC - import_pronode_prospects.ps1 (Pure ASCII / PS 5.1 Safe)
# Bulk-imports a CSV list of B2B Pro_Node ($49,999) prospects into pronode_crm.db
# with case-insensitive duplicate-email skipping + automatic outreach drafting.
#
# Examples:
#   .\import_pronode_prospects.ps1 -CsvPath ".\data\my_20_leads.csv" -DryRun
#   .\import_pronode_prospects.ps1 -CsvPath ".\data\my_20_leads.csv" -GenerateDrafts
# ==============================================================================
param(
    [string]$CsvPath = "",
    [ValidateSet("Lead","Contacted","DemoBooked","ProposalSent")]
    [string]$DefaultStage = "Lead",
    [int]$FollowUpDays = 0, [switch]$DryRun,
    [switch]$GenerateDrafts
)

$ErrorActionPreference = "Stop"
$ProjectDir  = "C:\Users\toome\Desktop\SovereignCore"
$DbPath      = Join-Path$ProjectDir "data\pronode_crm.db"
$ImporterPy  = Join-Path$ProjectDir "Modules\pronode_csv_importer.py"
$TemplateCsv = Join-Path$ProjectDir "data\weekly_prospects_template.csv"

if (-not $CsvPath) {
    Write-Host "=== PRO_NODE CSV BULK-IMPORTER ===" -ForegroundColor Cyan
    Write-Host "Template CSV ready at: $TemplateCsv" -ForegroundColor Green
    Write-Host "Columns: company,contact,email,stage,next_followup,notes" -ForegroundColor Gray
    Write-Host "Usage  : .\import_pronode_prospects.ps1 -CsvPath `"$TemplateCsv`" -GenerateDrafts" -ForegroundColor White
    exit 0
}

$resolvedCsv = (Resolve-Path$CsvPath -ErrorAction Stop).Path
Write-Host "=== IMPORTING PRO_NODE B2B PROSPECTS FROM CSV ===" -ForegroundColor Cyan
Write-Host "Source CSV: $resolvedCsv" -ForegroundColor Gray

$cfgJson = (@{
    dry_run       = [bool]$DryRun
    default_stage = $DefaultStage
    followup_days = $FollowUpDays
} | ConvertTo-Json -Compress)
$b64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($cfgJson))

python $ImporterPy$DbPath $resolvedCsv$b64
if ($LASTEXITCODE -ne 0) { throw "CSV import failed with exit code $LASTEXITCODE." }

if ($GenerateDrafts -and (-not$DryRun)) {
    Write-Host "`n--- Generating Personalized Outreach Drafts for Imported Prospects ---" -ForegroundColor Cyan
    & (Join-Path $ProjectDir "generate_pronode_outreach.ps1") -AllActive
}