param(
    [int]$MaxLeads = 20,
    [int]$SpacingSeconds = 45,
    [switch]$SendLive
)
$ErrorActionPreference = "Stop"
$ProjectDir = "C:\Users\toome\Desktop\SovereignCore"
$mode = if ($SendLive) { "LIVE" } else { "DRYRUN" }
python "$ProjectDir\Modules\pronode_sprint_engine.py" $ProjectDir $MaxLeads $SpacingSeconds $mode