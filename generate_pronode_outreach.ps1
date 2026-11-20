# ==============================================================================
# Oracle Systems LLC - generate_pronode_outreach.ps1 (Pure ASCII / PS 5.1 Safe)
# Reads prospects from data\pronode_crm.db and writes personalized $49,999
# Pro_Node B2B outreach emails + 3-minute live sandbox demo checklist.
#
# Examples:
#   .\generate_pronode_outreach.ps1
#   .\generate_pronode_outreach.ps1 -AllActive
# ==============================================================================
param(
    [switch]$AllActive,
    [string]$Domain = "oraclesystemsllc.com",
    [string]$SenderName = "Thomas Toomer",
    [string]$SenderEmail = "Toomer1980@gmail.com"
)

$ErrorActionPreference = "Stop"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$DbPath     = Join-Path $ProjectDir "data\pronode_crm.db"
$OutDir     = Join-Path $ProjectDir "reports\outreach"
$EnginePy   = Join-Path $ProjectDir "Modules\pronode_outreach_engine.py"

$cfgJson = (@{
    all_active   = [bool]$AllActive
    domain       = $Domain
    sender_name  = $SenderName
    sender_email = $SenderEmail
} | ConvertTo-Json -Compress)
$b64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($cfgJson))

python $EnginePy $DbPath $OutDir $b64