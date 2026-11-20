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
    Write-Host "Generate your 16-char Google App Password at: https://myaccount.google.com/apppasswords" -ForegroundColor Gray
    $inU = (Read-Host "Gmail Address (Enter for $GmailUser)").Trim()
    if ($inU) { $GmailUser = $inU }
    $sec = Read-Host "Paste 16-char Google App Password (hidden)" -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
    try { $rawP = [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
    $appPass = ($rawP -replace '\s+', '').Trim()
    if ($appPass.Length -lt 12) { throw "App Password too short ($($appPass.Length) chars). Expected 16 characters." }

    $envTxt = if (Test-Path $EnvFile) { [IO.File]::ReadAllText($EnvFile) } else { "" }
    $envTxt = if ($envTxt -match '(?m)^GMAIL_USER=.*$') { [regex]::Replace($envTxt, '(?m)^GMAIL_USER=.*$', "GMAIL_USER=$GmailUser") } else { $envTxt.TrimEnd() + "`r`nGMAIL_USER=$GmailUser`r`n" }
    $envTxt = if ($envTxt -match '(?m)^GMAIL_APP_PASSWORD=.*$') { [regex]::Replace($envTxt, '(?m)^GMAIL_APP_PASSWORD=.*$', "GMAIL_APP_PASSWORD=$appPass") } else { $envTxt.TrimEnd() + "`r`nGMAIL_APP_PASSWORD=$appPass`r`n" }
    [IO.File]::WriteAllText($EnvFile, $envTxt, $Utf8NoBom)
    Write-Host "[PASS] Stored GMAIL_USER and hidden GMAIL_APP_PASSWORD into .env" -ForegroundColor Green
} else {
    foreach ($ln in (Get-Content $EnvFile -ErrorAction SilentlyContinue)) {
        if ($ln -match '^GMAIL_USER=(.+)$') { $GmailUser = $Matches[1].Trim().Trim('"').Trim("'") }
        if ($ln -match '^GMAIL_APP_PASSWORD=(.+)$') { $appPass = ($Matches[1].Trim().Trim('"').Trim("'") -replace '\s+', '') }
    }
    if (-not $appPass -or $appPass -match 'PASTE_16_CHAR') { throw "GMAIL_APP_PASSWORD not set yet. Run .\setup_gmail_smtp.ps1" }
}

if (-not $TestRecipient) { $TestRecipient = $GmailUser }
$pubUrl = if (Test-Path "$ProjectDir\config\public_url.txt") { (Get-Content "$ProjectDir\config\public_url.txt" -Raw).Trim() } else { "http://127.0.0.1:8000" }

$mail = New-Object System.Net.Mail.MailMessage
$mail.From    = $GmailUser
$mail.To.Add($TestRecipient)
$mail.Subject = "[SMTP TEST] Oracle Systems Pro_Node (`$49,999) Outreach Pipeline Live"
$mail.Body    = "Hi Thomas,`r`n`r`nYour Gmail SMTP outreach pipeline is verified and ready for 20-lead Pro_Node sprints.`r`nLive 4D Store: $pubUrl/store`r`nLive Portal  : $pubUrl/portal`r`nTimestamp    : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') EST"
$smtp = New-Object System.Net.Mail.SmtpClient("smtp.gmail.com", 587)
$smtp.EnableSsl   = $true
$smtp.Credentials = New-Object System.Net.NetworkCredential($GmailUser, $appPass)
try {
    $smtp.Send($mail)
    Write-Host "[LIVE PASS] Test email delivered to $TestRecipient! Check your inbox." -ForegroundColor Green
} finally {
    $mail.Dispose(); $smtp.Dispose()
}