param(
    [string]$GmailUser = "Toomer1980@gmail.com",
    [string]$TestRecipient = "",
    [switch]$SendTestOnly
)
$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$EnvFile    = "$ProjectDir\.env"
$Utf8NoBom  = New-Object System.Text.UTF8Encoding($false)

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORACLE SYSTEMS LLC // SECURE GMAIL APP PASSWORD SETUP & SMTP TEST" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan

$appPass = ""
if (-not $SendTestOnly) {
    Write-Host "How to get your 16-char Google App Password:" -ForegroundColor Gray
    Write-Host "  1. Open https://myaccount.google.com/apppasswords (requires 2-Step Verification ON)" -ForegroundColor Gray
    Write-Host "  2. App name: 'OracleSystemsSMTP' -> Create -> copy the 16-letter code." -ForegroundColor Gray
    Write-Host ""
    $inUser = (Read-Host "Gmail Address (Enter for $GmailUser)").Trim()
    if ($inUser) { $GmailUser = $inUser }

    $sec = Read-Host "Paste 16-char Google App Password (hidden input)" -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
    try { $rawPass = [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }

    $appPass = ($rawPass -replace '\s+', '').Trim()
    if ($appPass.Length -lt 12) { throw "App Password looks too short ($($appPass.Length) chars). Expected 16 characters." }

    $envTxt = if (Test-Path $EnvFile) { [System.IO.File]::ReadAllText($EnvFile) } else { "" }
    if ($envTxt -match '(?m)^GMAIL_USER=.*$') {
        $envTxt = [regex]::Replace($envTxt, '(?m)^GMAIL_USER=.*$', "GMAIL_USER=$GmailUser")
    } else {
        $envTxt = $envTxt.TrimEnd() + "`r`nGMAIL_USER=$GmailUser`r`n"
    }
    if ($envTxt -match '(?m)^GMAIL_APP_PASSWORD=.*$') {
        $envTxt = [regex]::Replace($envTxt, '(?m)^GMAIL_APP_PASSWORD=.*$', "GMAIL_APP_PASSWORD=$appPass")
    } else {
        $envTxt = $envTxt.TrimEnd() + "`r`nGMAIL_APP_PASSWORD=$appPass`r`n"
    }
    [System.IO.File]::WriteAllText($EnvFile, $envTxt, $Utf8NoBom)
    Write-Host "[PASS] Saved GMAIL_USER and hidden GMAIL_APP_PASSWORD securely into .env" -ForegroundColor Green
} else {
    if (-not (Test-Path $EnvFile)) { throw "Missing $EnvFile" }
    foreach ($ln in (Get-Content $EnvFile)) {
        if ($ln -match '^GMAIL_USER=(.+)$') { $GmailUser = $Matches[1].Trim().Trim('"').Trim("'") }
        if ($ln -match '^GMAIL_APP_PASSWORD=(.+)$') { $appPass = ($Matches[1].Trim().Trim('"').Trim("'") -replace '\s+', '') }
    }
    if (-not $appPass -or $appPass -match 'PASTE_16_CHAR') { throw "GMAIL_APP_PASSWORD is not configured in .env yet. Run .\setup_gmail_smtp.ps1 without -SendTestOnly." }
}

if (-not $TestRecipient) { $TestRecipient = $GmailUser }
$pubUrl = if (Test-Path "$ProjectDir\config\public_url.txt") { (Get-Content "$ProjectDir\config\public_url.txt" -Raw).Trim() } else { "http://127.0.0.1:8000" }

Write-Host "`nSending live Pro_Node (`$49,999) SMTP test email to $TestRecipient ..." -ForegroundColor Cyan
$mail = New-Object System.Net.Mail.MailMessage
$mail.From    = $GmailUser
$mail.To.Add($TestRecipient)
$mail.Subject = "[SMTP TEST] Dedicated Sovereign AI Node - Oracle Systems LLC (3-Min Live Sandbox)"
$mail.Body    = @"
Hi Thomas,

This confirms your Oracle Systems LLC Gmail SMTP outreach pipeline is LIVE and verified.

--- SAMPLE PRO_NODE (`$49,999) B2B OUTREACH ---
We built Oracle Systems Pro_Node so agencies and media teams run autonomous 4D content pipelines, CRM, and local LLM workflows on dedicated hardware with zero per-seat SaaS lock-in (`$24,999.50 Milestone 1 ACH deposit / `$49,999 turnkey).

Live Storefront Preview: $pubUrl/store
Live Member Portal     : $pubUrl/portal

Sent from SovereignCore on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') EST.
"@

$smtp = New-Object System.Net.Mail.SmtpClient("smtp.gmail.com", 587)
$smtp.EnableSsl   = $true
$smtp.Credentials = New-Object System.Net.NetworkCredential($GmailUser, $appPass)
try {
    $smtp.Send($mail)
    Write-Host "[LIVE PASS] Test Pro_Node outreach email delivered to $TestRecipient! Check your inbox." -ForegroundColor Green
} finally {
    $mail.Dispose()
    $smtp.Dispose()
}