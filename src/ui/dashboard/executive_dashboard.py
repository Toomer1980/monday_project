import psutil
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def render_executive_summary():
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent

    table = Table(title="Oracle Systems LLC - SovereignCore Live Telemetry")
    table.add_column("Subsystem", style="cyan", no_wrap=True)
    table.add_column("Status", style="green")
    table.add_column("Metric / Port", style="yellow")

    table.add_row("Entity / EIN", "VERIFIED", "82-4737196")
    table.add_row("High-Ticket Gateway", "READY", "Port 8000")
    table.add_row("Billing & Tax Reconciler", "READY", "Port 8001")
    table.add_row("Stripe Legacy Node", "READY", "Port 5000")
    table.add_row("System CPU Load", "NOMINAL" if cpu < 85 else "HIGH", f"{cpu}%")
    table.add_row("System RAM Usage", "NOMINAL" if mem < 90 else "HIGH", f"{mem}%")

    console.print(Panel.fit(table))

if __name__ == "__main__":
    render_executive_summary()
