#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text

console = Console()
LOG_PATH = r"C:\Users\toome\Desktop\SovereignCore\logs\daemon.log"

def get_recent_logs(lines_to_read=4):
    if not os.path.exists(LOG_PATH):
        return ["[!] Telemetry log file not yet detected."]
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            all_lines = [line.strip() for line in f if line.strip()]
            return all_lines[-lines_to_read:] if all_lines else ["[!] Waiting for initial heartbeat..."]
    except Exception as e:
        return [f"[!] Log read error: {e}"]

def generate_telemetry_dashboard():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    recent_logs = get_recent_logs(4)
    log_display = "\n".join(f"  > {line}" for line in recent_logs)
    
    content = Text()
    content.append(f" [SYSTEM] Node Host: SovereignCore Linked\n", style="bold green")
    content.append(f" [TIME]   Matrix Time: {timestamp}\n\n", style="cyan")
    content.append(" [LIVE DAEMON TELEMETRY STREAM]\n", style="bold yellow")
    content.append(f"{log_display}\n", style="white")
    
    return Panel(
        content,
        title="[bold yellow]Sovereign Industries - Live Operational Matrix[/bold yellow]",
        border_style="cyan"
    )

def main():
    console.print("[bold green] [SECURE] Linked to SovereignCore live daemon feed...[/bold green]")
    try:
        with Live(generate_telemetry_dashboard(), refresh_per_second=2, console=console) as live:
            while True:
                live.update(generate_telemetry_dashboard())
                time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[bold yellow] [NOTICE] Telemetry dashboard suspended. Daemon continues background execution.[/bold yellow]")
        sys.exit(0)

if __name__ == "__main__":
    main()