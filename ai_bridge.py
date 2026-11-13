import os
import subprocess
import json
import shutil

class AIBridge:
    def __init__(self):
        """Initializes the bridge and checks for Android terminal tools."""
        self.has_termux_api = shutil.which("termux-notification") is not None
        
    def send_hud_notification(self, title, message, priority="normal", tag="sovereign_core"):
        """
        Pipes data from your background Python modules into a visible Android alert.
        Falls back to a standard terminal display if API tools are absent.
        """
        if self.has_termux_api:
            # Construct the Android Termux API shell command
            cmd = [
                "termux-notification",
                "--title", str(title),
                "--content", str(message),
                "--id", str(tag),
                "--priority", str(priority),
                "--led-color", "00FF00"  # Visual indicator for data stream activity
            ]
            try:
                subprocess.run(cmd, check=True)
            except Exception as e:
                self._terminal_fallback(f"API Error sending HUD alert: {e}")
        else:
            self._terminal_fallback(f"[{title.upper()}] {message}")

    def stream_to_overlay(self, data_packet):
        """
        Formats real-time streaming data (like BTC liquidations or neural net outputs)
        into compact, readable summaries for the HUD system.
        """
        try:
            parsed_data = json.loads(data_packet) if isinstance(data_packet, str) else data_packet
            topic = parsed_data.get("topic", "SYSTEM EVENT")
            metric = parsed_data.get("value", "")
            status = parsed_data.get("status", "ACTIVE")
            
            hud_msg = f"Status: {status} | Metric: {metric}"
            self.send_hud_notification(title=f"Core Stream: {topic}", message=hud_msg)
        except Exception as e:
            self.send_hud_notification(title="Bridge Stream Error", message=str(e), priority="high")

    def _terminal_fallback(self, text):
        """Logs output to standard standard out when standard notifications are unavailable."""
        print(f"\r[HUD-Fallback] {text}")

# Operational test suite when running the script independently
if __name__ == "__main__":
    bridge = AIBridge()
    # Test a structural notification event
    bridge.send_hud_notification(
        title="SovereignCore Initialization", 
        message="HUD Bridge active. Monitoring 45 sub-modules...",
        priority="high"
    )