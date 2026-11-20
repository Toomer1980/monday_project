# ==============================================================================
# Oracle Systems LLC - setup_gdrive_sync.ps1 (Pure ASCII / PS 5.1 Safe)
# Detects Google Drive for Desktop OR installs rclone (winget / portable zip)
# and verifies live cloud sync into Google Drive folder: Oracle_Audit_2026
# ==============================================================================
param(
    [switch]$ConfigureNow
)

$ErrorActionPreference = "Continue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$StagingDir = Join-Path $ProjectDir "Oracle_Audit_2026"
$ToolsDir   = Join-Path $ProjectDir "tools\rclone"
New-Item -ItemType Directory -Path $StagingDir -Force | Out-Null

Write-Host "=== ORACLE SYSTEMS GOOGLE DRIVE SYNC SETUP ===" -ForegroundColor Cyan

# 1. Check for Google Drive for Desktop first
foreach ($cand in @("G:\My Drive", "H:\My Drive", (Join-Path $env:USERPROFILE "Google Drive\My Drive"), (Join-Path $env:USERPROFILE "Google Drive"))) {
    if (Test-Path $cand) {
        $dest = Join-Path $cand "Oracle_Audit_2026"
        New-Item -ItemType Directory -Path $dest -Force | Out-Null
        Copy-Item -Path (Join-Path $StagingDir "*") -Destination $dest -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "[PASS] Google Drive for Desktop detected at $cand -> synced Oracle_Audit_2026!" -ForegroundColor Green
        exit 0
    }
}

# 2. Locate or install rclone
$rcloneExe = $null
$cmd = Get-Command rclone -ErrorAction SilentlyContinue
if ($cmd) {
    $rcloneExe = $cmd.Source
} elseif (Test-Path (Join-Path $ToolsDir "rclone.exe")) {
    $rcloneExe = Join-Path $ToolsDir "rclone.exe"
}

if (-not $rcloneExe) {
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "Installing rclone via winget..." -ForegroundColor Yellow
        & winget install --id Rclone.Rclone --exact --accept-source-agreements --accept-package-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
        $cmd = Get-Command rclone -ErrorAction SilentlyContinue
        if ($cmd) { $rcloneExe = $cmd.Source }
    }
}

if (-not $rcloneExe) {
    Write-Host "Downloading official portable rclone for Windows x64 into $ToolsDir..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $ToolsDir -Force | Out-Null
    $zipFile = Join-Path $ToolsDir "rclone.zip"
    Invoke-WebRequest -Uri "https://downloads.rclone.org/rclone-current-windows-amd64.zip" -OutFile $zipFile -UseBasicParsing
    Expand-Archive -Path $zipFile -DestinationPath $ToolsDir -Force
    $found = Get-ChildItem -Path $ToolsDir -Recurse -Filter "rclone.exe" | Select-Object -First 1
    if ($found) {
        Copy-Item $found.FullName (Join-Path $ToolsDir "rclone.exe") -Force
        $rcloneExe = Join-Path $ToolsDir "rclone.exe"
        Remove-Item $zipFile -Force -ErrorAction SilentlyContinue
    }
}

if (-not $rcloneExe) {
    Write-Host "[FAIL] Could not install rclone automatically. Install Google Drive for Desktop or run: winget install Rclone.Rclone" -ForegroundColor Red
    exit 1
}

Write-Host "[PASS] rclone ready at: $rcloneExe" -ForegroundColor Green
$remotes = & $rcloneExe listremotes 2>$null

if ($remotes -contains "gdrive:") {
    Write-Host "[PASS] Remote 'gdrive:' is already configured. Running live sync to gdrive:Oracle_Audit_2026..." -ForegroundColor Green
    & $rcloneExe copy $StagingDir "gdrive:Oracle_Audit_2026" --update --transfers 2
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[PASS] Synced Oracle_Audit_2026 to Google Drive successfully!" -ForegroundColor Green
    }
} else {
    if ($ConfigureNow) {
        Write-Host "Launching Google Drive OAuth login for remote 'gdrive' (browser window will open)..." -ForegroundColor Cyan
        & $rcloneExe config create gdrive drive scope drive
        if ($LASTEXITCODE -eq 0) {
            & $rcloneExe copy $StagingDir "gdrive:Oracle_Audit_2026" --update --transfers 2
            Write-Host "[PASS] Authorized and synced Oracle_Audit_2026 to Google Drive!" -ForegroundColor Green
        }
    } else {
        Write-Host "[ACTION NEEDED] Run this one command to authorize your Google account in your browser:" -ForegroundColor Yellow
        Write-Host "  .\setup_gdrive_sync.ps1 -ConfigureNow" -ForegroundColor Cyan
    }
}