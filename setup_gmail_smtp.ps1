param(
    [string]$GmailUser = "Toomer1980@gmail.com",
    [string]$TestRecipient = "",
    [switch]$SendTestOnly
)
$ErrorActionPreference = "Stop"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$EnvFile    = "$ProjectDir\.env"
$Utf8NoBom  = New-Object System.Text.UTF8Encoding($false)

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "  ORACLE SYSTEMS LLC // SECURE GMAIL APP PASSWORD SETUP & SMTP TEST" -ForegroundColor White
Write-Host "========================================================================" -ForegroundColor Cyan

if (-not $SendTestOnly) {
    Write-Host "Generate a fresh 16-letter App Password at: https://myaccount.google.com/apppasswords" -ForegroundColor Gray
    $inU = (Read-Host "Gmail Address (PRESS ENTER for $GmailUser)").Trim()
    if ($inU -and $inU -match '^[^@\s]+@[^@\s]+\.[^@\s]+$') { $GmailUser = $inU }
    elseif ($inU) { Write-Host "[GUARD] '$inU' is not an email address -> keeping $GmailUser" -ForegroundColor Yellow }

    $sec = Read-Host "Paste 16-char Google App Password (hidden)" -AsSecureString
    $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
    try { $rawP = [Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr) }
    finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
    $appPass = ($rawP -replace '\s+', '').Trim()
    if ($appPass.Length -lt 12) { throw "App Password too short ($($appPass.Length) chars). Expected 16 letters." }

    $envTxt = if (Test-Path $EnvFile) { [IO.File]::ReadAllText($EnvFile) } else { "" }
    $envTxt = if ($envTxt -match '(?m)^GMAIL_USER=.*$') { [regex]::Replace($envTxt, '(?m)^GMAIL_USER=.*$', "GMAIL_USER=$GmailUser") } else { $envTxt.TrimEnd() + "`r`nGMAIL_USER=$GmailUser`r`n" }
    $envTxt = if ($envTxt -match '(?m)^GMAIL_APP_PASSWORD=.*$') { [regex]::Replace($envTxt, '(?m)^GMAIL_APP_PASSWORD=.*$', "GMAIL_APP_PASSWORD=$appPass") } else { $envTxt.TrimEnd() + "`r`nGMAIL_APP_PASSWORD=$appPass`r`n" }
    [IO.File]::WriteAllText($EnvFile, $envTxt, $Utf8NoBom)
    Write-Host "[PASS] Saved GMAIL_USER=$GmailUser and hidden GMAIL_APP_PASSWORD ($($appPass.Length) chars) into .env" -ForegroundColor Green
}

python "$ProjectDir\Modules\smtp_test_sender.py" $ProjectDir $TestRecipient