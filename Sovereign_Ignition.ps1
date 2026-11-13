<#
.SYNOPSIS
    M.O.N.D.A.Y. SovereignCore Total Environment Generator & Executable Wrapper
#>

$ErrorActionPreference = "Stop"
$CoreDir = "C:\Users\toome\Desktop\SovereignCore"

function Write-Log {
    param([string]$Message, [string]$Level="INFO")
    $Colors = @{ "INFO"="Cyan"; "WARN"="Yellow"; "ERROR"="Red"; "SUCCESS"="Green" }
    Write-Host "[M.O.N.D.A.Y. $Level] $Message" -ForegroundColor $Colors[$Level]
}

# 1. Environment Verification
if (-Not (Test-Path $CoreDir)) { New-Item -ItemType Directory -Path $CoreDir | Out-Null }
Set-Location $CoreDir

Write-Log "Sanitizing processes and injecting Python dependencies..." "INFO"
Stop-Process -Name python -ErrorAction SilentlyContinue
python -m pip install --upgrade pip -q
python -m pip install qasync websockets aiohttp PyQt6 pyjwt fastapi uvicorn -q

# 2. Synthesize Python Cores
Write-Log "Synthesizing Neural Codebases..." "INFO"

$ProphetCode = @"
import asyncio, websockets, json, logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [*] %(message)s')
class ProphetEngine:
    async def ingest_entropy(self, data):
        await asyncio.sleep(0.1) 
        return {"status": "resolved", "predictive_value": "calculated"}
    async def pipeline_handler(self, websocket, path):
        async for message in websocket:
            try:
                result = await self.ingest_entropy(json.loads(message))
                await websocket.send(json.dumps(result))
            except Exception as e:
                logging.error(f"Stream collapse: {e}")
async def ignite_engine():
    engine = ProphetEngine()
    logging.info("SovereignCore Framework engaged. Prophet-Engine initializing...")
    async with websockets.serve(engine.pipeline_handler, "0.0.0.0", 8765):
        await asyncio.Future()
if __name__ == "__main__":
    asyncio.run(ignite_engine())
"@
Set-Content -Path ".\prophet_pipeline.py" -Value $ProphetCode -Encoding UTF8

$SwarmApiCode = @"
from fastapi import FastAPI, Depends, HTTPException, Header
import uvicorn, logging, jwt
app = FastAPI(title="M.O.N.D.A.Y. Swarm Commander - SECURE")
logging.basicConfig(level=logging.INFO, format='%(asctime)s [*] %(message)s')
SECRET_KEY = "SOVEREIGN_OMEGA_PROTOCOL"
SWARM_STATE = {"total_drones": 50, "active": 12, "idle": 38, "status": "Operational"}
def verify_jwt(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "): raise HTTPException(status_code=401)
    try: return jwt.decode(authorization.split(" ")[1], SECRET_KEY, algorithms=["HS256"])
    except: raise HTTPException(status_code=401)
@app.get("/drones")
async def get_status(token: dict = Depends(verify_jwt)): return SWARM_STATE
@app.post("/drones/reserve")
async def deploy(token: dict = Depends(verify_jwt)):
    if SWARM_STATE["idle"] > 0:
        SWARM_STATE["idle"] -= 1; SWARM_STATE["active"] += 1
        return {"message": "Drone deployed.", "remaining_idle": SWARM_STATE["idle"]}
    return {"message": "Swarm maximum capacity."}
@app.get("/orders")
async def get_orders(token: dict = Depends(verify_jwt)): return {"directive": "Blockchain Entropy"}
if __name__ == "__main__":
    logging.info("API Online [JWT LOCK ENGAGED]")
    uvicorn.run(app, host="0.0.0.0", port=8000)
"@
Set-Content -Path ".\swarm_api.py" -Value $SwarmApiCode -Encoding UTF8

$DivinationCode = @"
import asyncio, aiohttp, websockets, json, logging
from datetime import datetime
logging.basicConfig(level=logging.INFO, format='%(asctime)s [*] %(message)s')
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
async def divination_stream():
    while True:
        try:
            async with websockets.connect("ws://localhost:8765") as ws:
                logging.info("Connected to Prophet-Engine via WebSocket.")
                while True:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(COINGECKO_URL, timeout=10) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                await ws.send(json.dumps({"type": "entropy", "data": data}))
                                logging.info(f"Entropy Injected: BTC ${data.get('bitcoin',{}).get('usd')} | ETH ${data.get('ethereum',{}).get('usd')}")
                    await asyncio.sleep(15)
        except Exception as e:
            await asyncio.sleep(5)
if __name__ == "__main__": asyncio.run(divination_stream())
"@
Set-Content -Path ".\divination_core.py" -Value $DivinationCode -Encoding UTF8

$HudCode = @"
import sys, json, asyncio, qasync, websockets, aiohttp, jwt
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton
from PyQt6.QtGui import QFont, QColor, QPalette
class MondayHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("M.O.N.D.A.Y. // Command Center")
        self.setGeometry(100, 100, 1000, 650)
        self.init_ui()
    def init_ui(self):
        palette = QPalette(); palette.setColor(QPalette.ColorRole.Window, QColor(10, 10, 15)); self.setPalette(palette)
        cw = QWidget(); self.setCentralWidget(cw); ml = QVBoxLayout(cw); bl = QHBoxLayout(); ml.addLayout(bl)
        self.console = QTextEdit(); self.console.setReadOnly(True)
        self.console.setStyleSheet("background-color: #050508; color: #aaddff; padding: 10px; font-family: Consolas;")
        bl.addWidget(self.console, stretch=3)
        cl = QVBoxLayout(); bl.addLayout(cl, stretch=1)
        self.btn_status = QPushButton("PING SWARM STATUS")
        self.btn_deploy = QPushButton("DEPLOY DRONE")
        self.btn_orders = QPushButton("PULL ORDERS")
        for btn in [self.btn_status, self.btn_deploy, self.btn_orders]:
            btn.setStyleSheet("background-color: #002233; color: #00ffcc; padding: 10px; font-family: Consolas;")
            cl.addWidget(btn)
        self.btn_status.clicked.connect(lambda: asyncio.ensure_future(self.api_request("/drones", "GET")))
        self.btn_deploy.clicked.connect(lambda: asyncio.ensure_future(self.api_request("/drones/reserve", "POST")))
        self.btn_orders.clicked.connect(lambda: asyncio.ensure_future(self.api_request("/orders", "GET")))
    def log_stream(self, msg): self.console.append(f"> {msg}"); self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())
    async def api_request(self, endpoint, method):
        token = jwt.encode({"commander": "active"}, "SOVEREIGN_OMEGA_PROTOCOL", algorithm="HS256")
        headers = {"Authorization": f"Bearer {token}"}
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                url = f"http://localhost:8000{endpoint}"
                async with session.request(method, url) as response: self.log_stream(f"[API] {method} {endpoint} -> {response.status}")
        except Exception as e: self.log_stream(f"[ERROR] API failed: {e}")
    async def connect_prophet(self):
        while True:
            try:
                async with websockets.connect("ws://localhost:8765") as ws:
                    self.log_stream("[SYSTEM] Direct latency bypass engaged.")
                    while True: await ws.send(json.dumps({"id":"alpha", "type":"ping"})); await asyncio.sleep(2.5)
            except: await asyncio.sleep(3)
async def main():
    app = QApplication(sys.argv); loop = qasync.QEventLoop(app); asyncio.set_event_loop(loop)
    hud = MondayHUD(); hud.show(); loop.create_task(hud.connect_prophet())
    with loop: loop.run_forever()
if __name__ == "__main__": asyncio.run(main())
"@
Set-Content -Path ".\monday_hud.py" -Value $HudCode -Encoding UTF8

# 3. Generate Native Executable Wrappers
Write-Log "Generating Windows Batch Executables..." "INFO"
Set-Content -Path ".\prophet.bat" -Value "@echo off`npython prophet_pipeline.py"
Set-Content -Path ".\swarm.bat" -Value "@echo off`npython swarm_api.py"
Set-Content -Path ".\divination.bat" -Value "@echo off`npython divination_core.py"
Set-Content -Path ".\hud.bat" -Value "@echo off`npython monday_hud.py"

# 4. Global Execution Matrix
Write-Log "Igniting Executable Matrix..." "SUCCESS"
Start-Process "cmd.exe" -ArgumentList "/c prophet.bat" -WindowStyle Hidden
Start-Process "cmd.exe" -ArgumentList "/c swarm.bat"
Start-Process "cmd.exe" -ArgumentList "/c divination.bat"
Start-Process "cmd.exe" -ArgumentList "/c hud.bat"

Write-Log "Execution locked. You can now run any component directly in PowerShell by typing its name (e.g., '.\hud.bat')." "SUCCESS"