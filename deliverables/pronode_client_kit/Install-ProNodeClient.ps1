param([string]$NodeId = $env:COMPUTERNAME, [string]$HubUrl = "https://oraclesystemsllc.com")
$ErrorActionPreference = "Continue"
Write-Host "=== ORACLE SYSTEMS PRO_NODE CLIENT PROVISIONER ($NodeId) ===" -ForegroundColor Cyan
[Environment]::SetEnvironmentVariable("ORACLE_NODE_ID", $NodeId, "User")
[Environment]::SetEnvironmentVariable("ORACLE_HUB_URL", $HubUrl, "User")
$env:ORACLE_NODE_ID = $NodeId; $env:ORACLE_HUB_URL = $HubUrl
python "$PSScriptRoot\pronode_heartbeat.py"
Write-Host "[PRO_NODE PROVISIONED] Node $NodeId registered with Oracle Systems Fleet Telemetry." -ForegroundColor Green
