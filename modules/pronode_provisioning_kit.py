import os
import sqlite3

PDIR = r"C:\Users\toome\Desktop\SovereignCore"
KIT_DIR = os.path.join(PDIR, "deliverables", "pronode_client_kit")
DB_PATH = os.path.join(PDIR, "data", "pronode_fleet.db")
os.makedirs(KIT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

HEARTBEAT_PY = """import json, os, platform, socket, time, urllib.request

HUB_URL = os.environ.get("ORACLE_HUB_URL", "https://oraclesystemsllc.com").rstrip("/")
NODE_ID = os.environ.get("ORACLE_NODE_ID", socket.gethostname())

def send_heartbeat():
    payload = json.dumps({
        "node_id": NODE_ID,
        "os": platform.platform(),
        "python": platform.python_version(),
        "status": "HEALTHY",
        "ts": int(time.time()),
    }).encode("utf-8")
    req = urllib.request.Request(HUB_URL + "/api/pronode/heartbeat", data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        print("[HEARTBEAT]", r.status, r.read().decode("utf-8", "ignore"))

if __name__ == "__main__":
    send_heartbeat()
"""

INSTALL_CLIENT_PS1 = """param([string]$NodeId = $env:COMPUTERNAME, [string]$HubUrl = "https://oraclesystemsllc.com")
$ErrorActionPreference = "Continue"
Write-Host "=== ORACLE SYSTEMS PRO_NODE CLIENT PROVISIONER ($NodeId) ===" -ForegroundColor Cyan
[Environment]::SetEnvironmentVariable("ORACLE_NODE_ID", $NodeId, "User")
[Environment]::SetEnvironmentVariable("ORACLE_HUB_URL", $HubUrl, "User")
$env:ORACLE_NODE_ID = $NodeId; $env:ORACLE_HUB_URL = $HubUrl
python "$PSScriptRoot\\pronode_heartbeat.py"
Write-Host "[PRO_NODE PROVISIONED] Node $NodeId registered with Oracle Systems Fleet Telemetry." -ForegroundColor Green
"""

RUNBOOK_MD = """# Oracle Systems LLC - Pro_Node Client Handover Runbook
1. Deploy SovereignCore stack on client Windows/Ubuntu workstation or server.
2. Run `Install-ProNodeClient.ps1 -NodeId "<CLIENT_SLUG>" -HubUrl "https://oraclesystemsllc.com"`.
3. Verify live node registration inside Oracle Systems Executive Matrix (`data/pronode_fleet.db`).
"""

open(os.path.join(KIT_DIR, "pronode_heartbeat.py"), "w", encoding="utf-8", newline="\n").write(HEARTBEAT_PY)
open(os.path.join(KIT_DIR, "Install-ProNodeClient.ps1"), "w", encoding="ascii", newline="\r\n").write(INSTALL_CLIENT_PS1)
open(os.path.join(KIT_DIR, "CLIENT_HANDOVER_RUNBOOK.md"), "w", encoding="utf-8", newline="\n").write(RUNBOOK_MD)

c = sqlite3.connect(DB_PATH)
c.execute(
    "CREATE TABLE IF NOT EXISTS fleet_nodes ("
    "id INTEGER PRIMARY KEY AUTOINCREMENT, node_id TEXT UNIQUE, os_info TEXT, "
    "status TEXT, last_seen_utc TEXT)"
)
c.commit()
c.close()
print(f"[PHASE 49 PASS] Packaged Pro_Node Client Provisioning Kit -> {KIT_DIR} & initialized pronode_fleet.db")
