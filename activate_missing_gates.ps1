$ErrorActionPreference = "Continue"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
Set-Location $ProjectDir

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORACLE SYSTEMS LLC // GUIDED GATE ACTIVATION WIZARD (62% -> 100%)" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan

# Gate A: Gmail App Password
$envTxt = if (Test-Path "$ProjectDir\.env") { [IO.File]::ReadAllText("$ProjectDir\.env") } else { "" }
$gmailSet = ($envTxt -match '(?m)^GMAIL_APP_PASSWORD=[A-Za-z0-9]{12,}')
if (-not $gmailSet) {
    $ans = (Read-Host "`n[1/3] Gmail SMTP App Password is missing. Open Google App Passwords & configure now? (Y/N)").Trim().ToUpper()
    if ($ans -eq "Y") {
        Start-Process "https://myaccount.google.com/apppasswords"
        .\setup_gmail_smtp.ps1
    }
} else { Write-Host "[READY] Gate A: Gmail SMTP App Password configured." -ForegroundColor Green }

# Gate B: Google Cloud Desktop OAuth JSON (YouTube API v3 + rclone custom OAuth)
$ytSet = Test-Path "$ProjectDir\config\youtube_client_secret.json"
if (-not $ytSet) {
    $ans = (Read-Host "`n[2/3] YouTube API v3 Desktop OAuth JSON is missing. Open Google Cloud Console & import from Downloads? (Y/N)").Trim().ToUpper()
    if ($ans -eq "Y") {
        Start-Process "https://console.cloud.google.com/apis/credentials"
        Read-Host "Download your Desktop app OAuth JSON to Downloads, then press Enter" | Out-Null
        .\verify_google_oauth.ps1 -AutoImportFromDownloads -TestLiveYouTube
        $rc = (Read-Host "Also switch rclone Drive sync to this custom Client ID & Secret now? (Y/N)").Trim().ToUpper()
        if ($rc -eq "Y") { .\update_rclone_oauth.ps1 }
    }
} else { Write-Host "[READY] Gate B: YouTube API v3 OAuth JSON configured." -ForegroundColor Green }

# Gate C: Pro_Node B2B Leads
$crmCnt = 0
if (Test-Path "$ProjectDir\data\pronode_crm.db") {
    $crmCnt = [int](python -c "import sqlite3; c=sqlite3.connect(r'$ProjectDir\data\pronode_crm.db'); print(c.execute('SELECT COUNT(*) FROM prospects').fetchone()[0]); c.close()" 2>$null)
}
if ($crmCnt -eq 0) {
    $ans = (Read-Host "`n[3/3] Pro_Node CRM has 0 prospects. Enter leads interactively now? (Y/N)").Trim().ToUpper()
    if ($ans -eq "Y") { .\build_pronode_leads.ps1 -InteractiveAdd -ImportToCrm }
} else { Write-Host "[READY] Gate C: Pro_Node CRM has $crmCnt prospect(s)." -ForegroundColor Green }

Write-Host "`n--- Updated Revenue Readiness Scorecard ---" -ForegroundColor Cyan
.\audit_revenue_gaps.ps1