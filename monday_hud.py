import sys, threading, aiohttp, jwt, asyncio, warnings, traceback
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import pyqtSignal, QObject

warnings.filterwarnings("ignore", category=UserWarning, module='jwt')

class SignalBridge(QObject):
    log_signal = pyqtSignal(str)

class AsyncEngine(threading.Thread):
    def __init__(self, bridge):
        super().__init__(daemon=True)
        self.bridge = bridge
        self.loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def execute_api_call(self, endpoint, method):
        asyncio.run_coroutine_threadsafe(self.api_request(endpoint, method), self.loop)

    async def api_request(self, endpoint, method):
        url = f"http://127.0.0.1:8000{endpoint}" 
        try:
            self.bridge.log_signal.emit(f"Requesting: {method} {url}")
            secret = "SOVEREIGN_OMEGA_PROTOCOL_SECURE_KEY_2026_VERSION_1"
            token = jwt.encode({"commander": "active"}, secret, algorithm="HS256")
            headers = {"Authorization": f"Bearer {token}"}
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.request(method, url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    text = await resp.text()
                    self.bridge.log_signal.emit(f"RESPONSE [{resp.status}]: {text}")
        except Exception:
            self.bridge.log_signal.emit(f"CRITICAL ERROR: {traceback.format_exc()}")

class MondayHUD(QMainWindow):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.setWindowTitle("M.O.N.D.A.Y. // Diagnostic Link Active")
        self.setGeometry(100, 100, 700, 500)
        cw = QWidget()
        self.setCentralWidget(cw)
        layout = QVBoxLayout(cw)
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background-color: #050508; color: #00ff00; font-family: Consolas; font-size: 13px;")
        layout.addWidget(self.console)
        self.btn_ping = QPushButton("PING SWARM")
        self.btn_ping.clicked.connect(lambda: self.engine.execute_api_call("/drones", "GET"))
        layout.addWidget(self.btn_ping)

    def log(self, msg):
        self.console.append(f"> {msg}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    bridge = SignalBridge()
    engine = AsyncEngine(bridge)
    hud = MondayHUD(engine)
    bridge.log_signal.connect(hud.log)
    engine.start()
    hud.show()
    sys.exit(app.exec())
