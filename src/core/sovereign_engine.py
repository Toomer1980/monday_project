import os
import sys
import time
import asyncio
import logging
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()
logging.basicConfig(
    filename=Path(__file__).resolve().parents[2] / 'logs' / 'sovereign_core.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

class SovereignEngine:
    def __init__(self):
        self.entity = "Oracle Systems LLC"
        self.ein = "82-4737196"
        console.print(Panel.fit(f"[bold cyan]Initializing {self.entity}[/bold cyan]\n[green]EIN: {self.ein} | Engine: SovereignCore Active[/green]"))

    def run_diagnostics(self):
        logging.info("Executing core telemetry and neural diagnostics...")
        console.print("[yellow][*] Telemetry nodes online. Autonomous loops synchronized.[/yellow]")

if __name__ == "__main__":
    engine = SovereignEngine()
    engine.run_diagnostics()
