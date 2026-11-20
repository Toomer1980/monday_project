# ==============================================================================
# Oracle Systems LLC - create_desktop_shortcuts.ps1 (Pure ASCII / PS 5.1 Safe)
# Places one-click policy-bypass Desktop shortcuts for Oracle Hub, Morning
# Briefing, and Executive Matrix using the active Windows Desktop folder.
# ==============================================================================
$ErrorActionPreference = "Stop"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$DesktopDir = [Environment]::GetFolderPath("Desktop")
$WshShell   = New-Object -ComObject WScript.Shell

$Shortcuts = @(
    @{
        Name   = "Oracle Systems Hub.lnk"
        Target = "powershell.exe"
        Args   = "-NoProfile -ExecutionPolicy Bypass -File `"$ProjectDir\oracle_hub.ps1`""
        Icon   = "C:\Windows\System32\shell32.dll,21"
        Desc   = "Launch Oracle Systems LLC SovereignCore Master Command Hub"
    },
    @{
        Name   = "Oracle Morning Briefing.lnk"
        Target = "powershell.exe"
        Args   = "-NoProfile -ExecutionPolicy Bypass -NoExit -File `"$ProjectDir\morning_briefing.ps1`" -RefreshStripe -TrimRamIfHigh"
        Icon   = "C:\Windows\System32\shell32.dll,238"
        Desc   = "Run 1-Screen Morning Executive Briefing (Stripe, Vault, CRM, RAM)"
    },
    @{
        Name   = "Oracle Block 10 Audit.lnk"
        Target = "powershell.exe"
        Args   = "-NoProfile -ExecutionPolicy Bypass -NoExit -File `"$ProjectDir\run_block10_treasury.ps1`""
        Icon   = "C:\Windows\System32\shell32.dll,165"
        Desc   = "Run Block 10 Live Stripe Treasury Audit & Google Drive Sync"
    }
)

Write-Host "=== CREATING ONE-CLICK ORACLE DESKTOP SHORTCUTS ===" -ForegroundColor Cyan
Write-Host "Desktop Path: $DesktopDir" -ForegroundColor Gray

foreach ($s in $Shortcuts) {
    $lnkPath = Join-Path -Path $DesktopDir -ChildPath $s.Name
    $sc = $WshShell.CreateShortcut($lnkPath)
    $sc.TargetPath       = $s.Target
    $sc.Arguments        = $s.Args
    $sc.WorkingDirectory = $ProjectDir
    $sc.IconLocation     = $s.Icon
    $sc.Description      = $s.Desc
    $sc.Save()
    Write-Host "[PASS] Created Desktop shortcut: $($s.Name)" -ForegroundColor Green
}

# Create Executive Matrix web shortcut
$urlPath = Join-Path -Path $DesktopDir -ChildPath "Oracle Executive Matrix.url"
$urlBody = "[InternetShortcut]`r`nURL=http://127.0.0.1:8000/dashboard`r`nIconIndex=13`r`nIconFile=C:\Windows\System32\shell32.dll`r`n"
[System.IO.File]::WriteAllText($urlPath, $urlBody, (New-Object System.Text.UTF8Encoding($false)))
Write-Host "[PASS] Created Desktop web shortcut: Oracle Executive Matrix.url" -ForegroundColor Green