# ==============================================================================
# Oracle Systems LLC - backup_sovereigncore.ps1 (Pure ASCII / PS 5.1 Safe)
# Creates AES-256-CBC encrypted snapshots of SQLite DBs, .env, TOML/INI configs,
# and CRM/YouTube state using a DPAPI-protected master key, then syncs to
# Google Drive (gdrive:Oracle_Audit_2026/Backups) via rclone.
#
# Examples:
#   .\backup_sovereigncore.ps1
#   .\backup_sovereigncore.ps1 -RegisterWeeklyTask
#   .\backup_sovereigncore.ps1 -RestoreFile ".\backups\encrypted\SovereignCore_Backup_YYYYMMDD_HHMMSS.zip.enc"
# ==============================================================================
param(
    [string]$RestoreFile = "",
    [string]$RestoreDest = "",
    [int]$KeepLocalCount = 10,
    [switch]$SkipCloudSync,
    [switch]$RegisterWeeklyTask
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Security
Add-Type -AssemblyName System.IO.Compression.FileSystem

$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$EncDir     = Join-Path -Path $ProjectDir -ChildPath "backups\encrypted"
$KeyPath    = Join-Path -Path $ProjectDir -ChildPath "config\backup_master.dpapi"
$LogFile    = Join-Path -Path $ProjectDir -ChildPath "logs\backup.log"
New-Item -ItemType Directory -Path $EncDir -Force | Out-Null
New-Item -ItemType Directory -Path (Split-Path $KeyPath) -Force | Out-Null
New-Item -ItemType Directory -Path (Split-Path $LogFile) -Force | Out-Null

function Write-BakLog([string]$msg, [string]$color = "Gray") {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [BACKUP] $msg"
    Add-Content -Path $LogFile -Value $line
    Write-Host $line -ForegroundColor $color
}

# Load or generate 256-bit AES master key protected by Windows DPAPI (CurrentUser)
if (-not (Test-Path $KeyPath)) {
    $rawKey = New-Object byte[] 32
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $rng.GetBytes($rawKey)
    $rng.Dispose()
    $prot = [System.Security.Cryptography.ProtectedData]::Protect($rawKey, $null, [System.Security.Cryptography.DataProtectionScope]::CurrentUser)
    [System.IO.File]::WriteAllBytes($KeyPath, $prot)
    Write-BakLog "Generated new DPAPI-protected AES-256 backup key at $KeyPath" "Green"
}
$KeyBytes = [System.Security.Cryptography.ProtectedData]::Unprotect(
    [System.IO.File]::ReadAllBytes($KeyPath),
    $null,
    [System.Security.Cryptography.DataProtectionScope]::CurrentUser
)

# Register weekly Sunday 02:00 AM automated encrypted backup task if requested
if ($RegisterWeeklyTask) {
    try {
        $selfPath = Join-Path -Path $ProjectDir -ChildPath "backup_sovereigncore.ps1"
        $act  = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$selfPath`"" -WorkingDirectory $ProjectDir
        $trig = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2:00AM
        $set  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        Register-ScheduledTask -TaskName "OracleSystems_WeeklyBackup_Sunday" -Action $act -Trigger $trig -Settings $set -Description "Weekly AES-256 encrypted SovereignCore backup synced to Google Drive" -Force | Out-Null
        Write-BakLog "[PASS] Registered task: OracleSystems_WeeklyBackup_Sunday (Sundays 02:00 AM)" "Green"
    } catch {
        Write-BakLog "[WARN] Scheduled task needs Admin PS: $($_.Exception.Message)" "Yellow"
    }
}

# MODE A: DECRYPT & RESTORE SNAPSHOT
if ($RestoreFile) {
    $resolved = (Resolve-Path $RestoreFile -ErrorAction Stop).Path
    if (-not $RestoreDest) {
        $RestoreDest = Join-Path -Path $ProjectDir -ChildPath ("backups\restored_" + (Get-Date -Format "yyyyMMdd_HHmmss"))
    }
    New-Item -ItemType Directory -Path $RestoreDest -Force | Out-Null

    $allBytes = [System.IO.File]::ReadAllBytes($resolved)
    if ($allBytes.Length -le 16) { throw "Encrypted backup file is corrupted or empty." }

    $iv = New-Object byte[] 16
    $cipherLen = $allBytes.Length - 16
    $cipherBytes = New-Object byte[] $cipherLen
    [Array]::Copy($allBytes, 0, $iv, 0, 16)
    [Array]::Copy($allBytes, 16, $cipherBytes, 0, $cipherLen)

    $aes = [System.Security.Cryptography.Aes]::Create()
    $aes.KeySize = 256
    $aes.Mode    = [System.Security.Cryptography.CipherMode]::CBC
    $aes.Padding = [System.Security.Cryptography.PaddingMode]::PKCS7
    $aes.Key     = $KeyBytes
    $aes.IV      = $iv
    $dec = $aes.CreateDecryptor()
    $plainBytes = $dec.TransformFinalBlock($cipherBytes, 0, $cipherBytes.Length)
    $dec.Dispose()
    $aes.Dispose()

    $tmpZip = Join-Path -Path $env:TEMP -ChildPath ("oracle_restore_" + (Get-Date -Format "yyyyMMddHHmmss") + ".zip")
    try {
        [System.IO.File]::WriteAllBytes($tmpZip, $plainBytes)
        [System.IO.Compression.ZipFile]::ExtractToDirectory($tmpZip, $RestoreDest)
        Write-BakLog "[PASS] Decrypted and restored backup to: $RestoreDest" "Green"
    } finally {
        Remove-Item $tmpZip -Force -ErrorAction SilentlyContinue
    }
    exit 0
}

# MODE B: CREATE ENCRYPTED BACKUP SNAPSHOT
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$stageDir = Join-Path -Path $env:TEMP -ChildPath "oracle_bak_stage_$ts"
$tmpZip   = Join-Path -Path $env:TEMP -ChildPath "SovereignCore_Backup_$ts.zip"
$encFile  = Join-Path -Path $EncDir   -ChildPath "SovereignCore_Backup_$ts.zip.enc"

New-Item -ItemType Directory -Path $stageDir -Force | Out-Null

try {
    $copiedCount = 0
    $copyList = @(
        ".env",
        "pyproject.toml",
        "config\sovereign_block10.toml",
        "config\sovereign_treasury.ini",
        "config\vault.enc.json",
        "logs\block10_state.json",
        "logs\stripe_alert_state.json",
        "data\youtube_publish_state.json"
    )
    foreach ($rel in $copyList) {
        $src = Join-Path -Path $ProjectDir -ChildPath $rel
        if (Test-Path $src) {
            $dst = Join-Path -Path $stageDir -ChildPath $rel
            New-Item -ItemType Directory -Path (Split-Path $dst) -Force | Out-Null
            try { Copy-Item -Path $src -Destination $dst -Force; $copiedCount++ } catch {}
        }
    }

    # Include all active SQLite *.db files (excluding backups/ and venv/)
    $dbFiles = Get-ChildItem -Path $ProjectDir -Recurse -File -Filter "*.db" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch '\\(backups|\.git|venv|\.venv)\\' }
    foreach ($db in $dbFiles) {
        $rel = $db.FullName.Substring($ProjectDir.Length).TrimStart("\")
        $dst = Join-Path -Path $stageDir -ChildPath $rel
        New-Item -ItemType Directory -Path (Split-Path $dst) -Force | Out-Null
        try { Copy-Item -Path $db.FullName -Destination $dst -Force; $copiedCount++ } catch {
            Write-BakLog "[WARN] Skipped locked DB ${rel}: $($_.Exception.Message)" "Yellow"
        }
    }

    # Include recent CRM CSV exports & invoice JSON logs
    foreach ($sub in @("reports\crm", "reports\invoices")) {
        $srcDir = Join-Path -Path $ProjectDir -ChildPath $sub
        if (Test-Path $srcDir) {
            $dstDir = Join-Path -Path $stageDir -ChildPath $sub
            New-Item -ItemType Directory -Path $dstDir -Force | Out-Null
            Get-ChildItem -Path $srcDir -File -ErrorAction SilentlyContinue | ForEach-Object {
                try { Copy-Item -Path $_.FullName -Destination (Join-Path -Path $dstDir -ChildPath $_.Name) -Force; $copiedCount++ } catch {}
            }
        }
    }

    if ($copiedCount -eq 0) { throw "No backup source files found to archive." }

    [System.IO.Compression.ZipFile]::CreateFromDirectory($stageDir, $tmpZip)

    # Encrypt ZIP -> .zip.enc with AES-256-CBC + random 16-byte IV prefix
    $plainBytes = [System.IO.File]::ReadAllBytes($tmpZip)
    $aes = [System.Security.Cryptography.Aes]::Create()
    $aes.KeySize = 256
    $aes.Mode    = [System.Security.Cryptography.CipherMode]::CBC
    $aes.Padding = [System.Security.Cryptography.PaddingMode]::PKCS7
    $aes.Key     = $KeyBytes
    $aes.GenerateIV()
    $iv = $aes.IV
    $enc = $aes.CreateEncryptor()
    $cipherBytes = $enc.TransformFinalBlock($plainBytes, 0, $plainBytes.Length)
    $enc.Dispose()
    $aes.Dispose()

    $outBytes = New-Object byte[] ($iv.Length + $cipherBytes.Length)
    [Array]::Copy($iv, 0, $outBytes, 0, $iv.Length)
    [Array]::Copy($cipherBytes, 0, $outBytes, $iv.Length, $cipherBytes.Length)
    [System.IO.File]::WriteAllBytes($encFile, $outBytes)

    $kb = [math]::Round((Get-Item $encFile).Length / 1KB, 1)
    Write-BakLog "[PASS] Created AES-256 encrypted backup ($copiedCount files, $kb KB) -> $encFile" "Green"

    # Prune old local encrypted snapshots beyond KeepLocalCount
    $oldSnaps = Get-ChildItem -Path $EncDir -Filter "*.zip.enc" | Sort-Object LastWriteTime -Descending | Select-Object -Skip $KeepLocalCount
    foreach ($old in $oldSnaps) { Remove-Item $old.FullName -Force -ErrorAction SilentlyContinue }

    # Sync encrypted snapshots to Google Drive via rclone (never uploads plaintext)
    if (-not $SkipCloudSync) {
        $rcloneCmd = Get-Command rclone -ErrorAction SilentlyContinue
        if ($rcloneCmd) {
            $remotes = & $rcloneCmd.Source listremotes 2>$null
            if ($remotes -contains "gdrive:") {
                & $rcloneCmd.Source copy $EncDir "gdrive:Oracle_Audit_2026/Backups" --update --transfers 2
                if ($LASTEXITCODE -eq 0) {
                    Write-BakLog "[PASS] Synced encrypted backup to Google Drive -> gdrive:Oracle_Audit_2026/Backups" "Green"
                } else {
                    Write-BakLog "[WARN] rclone exited $LASTEXITCODE (re-authorize via .\setup_gdrive_sync.ps1 -ConfigureNow)" "Yellow"
                }
            }
        }
    }
} finally {
    Remove-Item $tmpZip   -Force -ErrorAction SilentlyContinue
    Remove-Item $stageDir -Recurse -Force -ErrorAction SilentlyContinue
}