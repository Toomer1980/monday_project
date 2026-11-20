# ==============================================================================
# Oracle Systems LLC - upgrade_52week_4d_vault.ps1 (Pure ASCII / PS 5.1 Safe)
# Upgrades all 52 Full Videos + 52 Shorts with 4D Tesseract + Mobius Strip +
# Translucent Fluid Quantum Portal templates, 3D Pop-Out + Movie Thumbnails,
# and Bold 4D Persuasive Descriptions.
#
# Examples:
#   .\upgrade_52week_4d_vault.ps1 -Mode META_ONLY     (All 104 3D JPG thumbs + bold 4D descriptions in ~45s)
#   .\upgrade_52week_4d_vault.ps1 -Mode TEST_FIRST    (Upgrades Week_01 + Short_01 videos & movie-thumbs first)
#   .\upgrade_52week_4d_vault.ps1 -Mode ALL -FullDurationSec 1800 -ShortDurationSec 175
# ==============================================================================
param(
    [ValidateSet("META_ONLY","TEST_FIRST","ALL")]
    [string]$Mode = "META_ONLY",
    [int]$FullDurationSec = 1800,
    [int]$ShortDurationSec = 175,
    [string]$BaseUrl = ""
)

$ErrorActionPreference = "Stop"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$EnginePy   = Join-Path -Path $ProjectDir -ChildPath "Modules\oracle_4d_vault_upgrader.py"

if (-not $BaseUrl) {
    $envFile = Join-Path -Path $ProjectDir -ChildPath ".env"
    if (Test-Path $envFile) {
        $m = Select-String -Path $envFile -Pattern '^PUBLIC_BASE_URL\s*=\s*(.+)$' | Select-Object -First 1
        if ($m) { $BaseUrl = $m.Matches[0].Groups[1].Value.Trim().TrimEnd("/") }
    }
}

# Trim RAM first if rendering full batch on 7.82 GB laptop
if ($Mode -ne "META_ONLY" -and (Test-Path (Join-Path -Path $ProjectDir -ChildPath "optimize_ram_and_boot.ps1"))) {
    & (Join-Path -Path $ProjectDir -ChildPath "optimize_ram_and_boot.ps1") -TrimNow | Out-Null
}

$cfgJson = (@{
    mode               = $Mode
    full_duration_sec  = $FullDurationSec
    short_duration_sec = $ShortDurationSec
    base_url           = $BaseUrl
} | ConvertTo-Json -Compress)
$b64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($cfgJson))

python $EnginePy $ProjectDir $b64
if ($LASTEXITCODE -ne 0) { throw "4D vault upgrader exited with code $LASTEXITCODE." }