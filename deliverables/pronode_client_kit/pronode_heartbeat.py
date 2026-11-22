import json, os, platform, socket, time, urllib.request

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
