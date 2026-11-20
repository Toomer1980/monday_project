param(
    [string]$InputCsv = "",
    [int]$MinScore = 50,
    [switch]$InteractiveAdd,
    [switch]$ImportToCrm
)
$ErrorActionPreference = "Stop"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$Utf8NoBom  = New-Object System.Text.UTF8Encoding($false)
$Stamp      = Get-Date -Format "yyyyMMdd"
$RawDefault = "$ProjectDir\data\raw_b2b_leads_$Stamp.csv"
$CleanOut   = "$ProjectDir\data\pronode_leads_formatted_$Stamp.csv"

if ($InteractiveAdd) {
    Write-Host "=== INTERACTIVE PRO_NODE (`$49,999) B2B LEAD BUILDER ===" -ForegroundColor Cyan
    Write-Host "Enter real agency/operator leads (leave Company blank to finish)." -ForegroundColor Gray
    $rows = @()
    while ($true) {
        $co = (Read-Host "Company Name (Enter to finish)").Trim()
        if (-not $co) { break }
        $ct = (Read-Host "Contact Full Name").Trim()
        $em = (Read-Host "Work Email").Trim()
        $ti = (Read-Host "Title (e.g., Founder / CEO / COO)").Trim()
        $in = (Read-Host "Industry (e.g., Digital Agency / Media Studio)").Trim()
        $nt = (Read-Host "Short Note / Angle").Trim()
        $rows += [PSCustomObject]@{ company = $co; contact = $ct; email = $em; title = $ti; industry = $in; notes = $nt }
    }
    if ($rows.Count -eq 0) { Write-Host "[INFO] No leads entered." -ForegroundColor Yellow; exit 0 }
    $rows | Export-Csv -Path $RawDefault -NoTypeInformation -Encoding UTF8
    $InputCsv = $RawDefault
    Write-Host "[SAVED] Wrote $($rows.Count) raw lead(s) to $RawDefault" -ForegroundColor Green
}

if (-not $InputCsv) {
    $tpl = "$ProjectDir\data\raw_b2b_export_template.csv"
    if (-not (Test-Path $tpl)) {
        $hdr = "Company Name,First Name,Last Name,Email Address,Job Title,Industry,Website,Notes`r`n"
        [System.IO.File]::WriteAllText($tpl, $hdr, $Utf8NoBom)
    }
    Write-Host "=== PRO_NODE (`$49,999) B2B LEAD LIST BUILDER & CSV FORMATTER ===" -ForegroundColor Cyan
    Write-Host "Template ready: $tpl" -ForegroundColor Green
    Write-Host "Usage:" -ForegroundColor White
    Write-Host "  1) Format any Apollo/LinkedIn/Maps CSV & preview outreach:" -ForegroundColor Gray
    Write-Host "     .\build_pronode_leads.ps1 -InputCsv `"C:\path\to\leads.csv`" -MinScore 55" -ForegroundColor Cyan
    Write-Host "  2) Format AND auto-import into pronode_crm.db + generate drafts:" -ForegroundColor Gray
    Write-Host "     .\build_pronode_leads.ps1 -InputCsv `"C:\path\to\leads.csv`" -ImportToCrm" -ForegroundColor Cyan
    Write-Host "  3) Type leads directly into PowerShell:" -ForegroundColor Gray
    Write-Host "     .\build_pronode_leads.ps1 -InteractiveAdd -ImportToCrm" -ForegroundColor Cyan
    exit 0
}

python "$ProjectDir\Modules\pronode_lead_formatter.py" $ProjectDir $InputCsv $CleanOut $MinScore
if ($LASTEXITCODE -ne 0) { throw "Lead formatter failed (exit $LASTEXITCODE)." }

if ($ImportToCrm -and (Test-Path $CleanOut)) {
    $rowCount = (Import-Csv $CleanOut).Count
    if ($rowCount -gt 0) {
        Write-Host "`n--- Importing $rowCount Scored Lead(s) into pronode_crm.db + Drafting Outreach ---" -ForegroundColor Cyan
        & "$ProjectDir\import_pronode_prospects.ps1" -CsvPath $CleanOut -GenerateDrafts
    } else {
        Write-Host "[INFO] 0 leads passed qualification filters; skipped CRM import." -ForegroundColor Yellow
    }
}