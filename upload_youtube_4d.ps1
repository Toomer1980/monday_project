param(
    [ValidateSet("Short","FullVideo","Both")]
    [string]$UploadType = "Short",
    [ValidateSet("unlisted","private","public")]
    [string]$Privacy = "public",
    [int]$MaxUploads = 1,
    [switch]$UploadNow
)
$ErrorActionPreference = "Continue"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$LogFile    = "$ProjectDir\logs\youtube_uploader.log"
New-Item -ItemType Directory -Path "$ProjectDir\logs" -Force | Out-Null

function Send-AlertBalloon([string]$Title, [string]$Body) {
    try {
        Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
        Add-Type -AssemblyName System.Drawing -ErrorAction Stop
        $ni = New-Object System.Windows.Forms.NotifyIcon
        $ni.Icon = [System.Drawing.SystemIcons]::Warning
        $ni.BalloonTipTitle = $Title
        $ni.BalloonTipText  = $Body
        $ni.Visible = $true
        $ni.ShowBalloonTip(7000)
        Start-Sleep -Seconds 2
        $ni.Dispose()
    } catch {}
}

# Refresh Learning Curve rankings before selecting next video
& "$ProjectDir\run_learning_curve.ps1" | Out-Null

$cfg = (@{
    upload_type = $UploadType
    privacy     = $Privacy
    max_uploads = $MaxUploads
    dry_run     = (-not $UploadNow)
} | ConvertTo-Json -Compress)
$b64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($cfg))

$ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$out = python "$ProjectDir\Modules\youtube_api_uploader.py" $ProjectDir $b64 2>&1
$rc  = $LASTEXITCODE
$out | ForEach-Object {
    Add-Content -Path $LogFile -Value "$ts $_"
    Write-Host $_
}

if ($rc -ne 0 -and $UploadNow) {
    $msg = if ($rc -eq 3) { "Missing config\youtube_client_secret.json for YouTube auto-upload." } else { "YouTube $UploadType upload exited $rc. Check logs\youtube_uploader.log" }
    Send-AlertBalloon "Oracle Systems - YouTube Upload Alert" $msg
}