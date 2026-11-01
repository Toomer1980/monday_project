#!/usr/bin/env python3
import os
import sys
import time
import msvcrt
import webbrowser
import requests
from datetime import datetime
import psutil
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.live import Live
from rich.text import Text

sys.path.append(r"C:\Users\toome\Desktop\SovereignCore\modules")
import db
import vault

console = Console()
LOG_PATH = r"C:\Users\toome\Desktop\SovereignCore\logs\daemon.log"
TOKEN_PATH = r"C:\Users\toome\Desktop\SovereignCore\config\api_key.token"
API_BASE = "http://127.0.0.1:8000"
LAST_ACTION_MSG = "Ready. Hotkeys: [Q] Quick Job | [A] Run Audits | [T] Custom Job | [P] Purge | [R] CSV | [W] Web UI"

def get_api_headers():
    try:
        with open(TOKEN_PATH, "r", encoding="utf-8") as f:
            token = f.read().strip()
        return {"X-API-Key": token, "Content-Type": "application/json"}
    except Exception:
        return {"Content-Type": "application/json"}

def get_recent_logs(lines_to_read=4):
    if not os.path.exists(LOG_PATH):
        return ["[!] Telemetry log file not yet detected."]
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            all_lines = [line.strip() for line in f if line.strip()]
            return all_lines[-lines_to_read:] if all_lines else ["[!] Waiting for initial heartbeat..."]
    except Exception as e:
        return [f"[!] Log read error: {e}"]

def make_metrics_table():
    table = Table(title="Hardware & DPAPI Vault Telemetry", border_style="cyan", expand=True)
    table.add_column("Resource", style="bold yellow", justify="left")
    table.add_column("Load / State", style="bold white", justify="center")
    table.add_column("Capacity / Details", style="cyan", justify="right")

    cpu_pct = psutil.cpu_percent(interval=None)
    cpu_cores = psutil.cpu_count(logical=True)
    table.add_row("CPU Core", f"{cpu_pct}%", f"{cpu_cores} Logical Threads")

    vmem = psutil.virtual_memory()
    ram_used = round(vmem.used / (1024**3), 2)
    ram_total = round(vmem.total / (1024**3), 2)
    table.add_row("RAM Memory", f"{vmem.percent}%", f"{ram_used} GB / {ram_total} GB")

    disk = psutil.disk_usage("C:\\")
    disk_used = round(disk.used / (1024**3), 1)
    disk_total = round(disk.total / (1024**3), 1)
    vault_count = len(vault.list_secret_keys())
    table.add_row("Disk (C:) & Vault", f"{disk.percent}%", f"{disk_used}/{disk_total} GB | {vault_count} DPAPI Keys")

    return table

def make_task_history_table():
    table = Table(title="Recent Swarm Task History (SQLite: sovereign_tasks.db)", border_style="yellow", expand=True)
    table.add_column("ID", style="bold white", justify="center", width=5)
    table.add_column("Task Identifier", style="bold cyan", justify="left")
    table.add_column("Status", justify="center")
    table.add_column("Runtime", justify="right")
    table.add_column("Queued At", style="dim cyan", justify="right")

    try:
        tasks = db.get_recent_tasks(limit=4)
        if not tasks:
            table.add_row("-", "No tasks logged yet", "IDLE", "0.0s", "-")
        for t in tasks:
            status = t["status"]
            if status == "COMPLETED":
                status_styled = "[bold green]COMPLETED[/bold green]"
            elif status == "FAILED":
                status_styled = "[bold red]FAILED[/bold red]"
            elif status == "CANCELLED":
                status_styled = "[bold magenta]CANCELLED[/bold magenta]"
            else:
                status_styled = "[bold yellow]QUEUED[/bold yellow]"
            
            dur = f"{t['duration_sec']}s" if t["duration_sec"] is not None else "-"
            table.add_row(str(t["id"]), t["task_name"][:32], status_styled, dur, t["queued_at"][11:19])
    except Exception as e:
        table.add_row("!", f"DB query error: {e}", "ERROR", "-", "-")

    return table

def generate_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="metrics", size=7),
        Layout(name="tasks", size=8),
        Layout(name="logs", size=7),
        Layout(name="controls", size=4)
    )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header_panel = Panel(
        Text(f"M.O.N.D.A.Y. SOVEREIGNCORE MATRIX // INTERACTIVE COMMAND CONSOLE // {now}", justify="center", style="bold green"),
        border_style="green"
    )
    layout["header"].update(header_panel)
    layout["metrics"].update(make_metrics_table())
    layout["tasks"].update(make_task_history_table())

    logs = get_recent_logs(4)
    log_text = Text("\n".join(f"  > {line}" for line in logs), style="white")
    logs_panel = Panel(
        log_text,
        title="[bold yellow]Daemon Event Stream[/bold yellow]",
        border_style="cyan"
    )
    layout["logs"].update(logs_panel)

    ctrl_text = Text()
    ctrl_text.append(" [Q] ", style="bold black on cyan")
    ctrl_text.append(" Quick Job ")
    ctrl_text.append(" [A] ", style="bold black on green")
    ctrl_text.append(" Audit Plugins ")
    ctrl_text.append(" [T] ", style="bold black on white")
    ctrl_text.append(" Custom Job ")
    ctrl_text.append(" [P] ", style="bold black on yellow")
    ctrl_text.append(" Purge ")
    ctrl_text.append(" [R] ", style="bold black on magenta")
    ctrl_text.append(" CSV ")
    ctrl_text.append(" [W] ", style="bold white on blue")
    ctrl_text.append(" Web UI\n")
    ctrl_text.append(f" Status: {LAST_ACTION_MSG}", style="bold cyan")

    layout["controls"].update(Panel(ctrl_text, border_style="green"))
    return layout

def handle_keypress(key, live):
    global LAST_ACTION_MSG
    k = key.lower()
    headers = get_api_headers()

    if k == 'q':
        job_name = f"TUI-QuickJob-{int(time.time())}"
        try:
            r = requests.post(f"{API_BASE}/api/task/submit", headers=headers, json={
                "task_name": job_name,
                "payload": {"source": "Dashboard-Hotkey-Q"}
            }, timeout=3)
            if r.status_code == 202:
                LAST_ACTION_MSG = f"Dispatched [{job_name}] (ID: {r.json().get('task_id')})"
        except Exception as e:
            LAST_ACTION_MSG = f"Dispatch error: {e}"

    elif k == 'a':
        try:
            r = requests.post(f"{API_BASE}/api/plugins/audit", headers=headers, timeout=3)
            if r.status_code == 202:
                LAST_ACTION_MSG = f"Queued 3 Audit Plugins (IDs: {r.json().get('queued_plugins')})"
        except Exception as e:
            LAST_ACTION_MSG = f"Audit error: {e}"

    elif k == 'p':
        try:
            r = requests.post(f"{API_BASE}/api/tasks/purge", headers=headers, timeout=3)
            if r.status_code == 200:
                LAST_ACTION_MSG = f"Purged {r.json().get('purged_count')} pending task(s)."
        except Exception as e:
            LAST_ACTION_MSG = f"Purge error: {e}"

    elif k == 'r':
        try:
            r = requests.post(f"{API_BASE}/api/tasks/export-csv", headers=headers, timeout=5)
            if r.status_code == 200:
                LAST_ACTION_MSG = f"Saved CSV: {os.path.basename(r.json().get('report_path', ''))}"
        except Exception as e:
            LAST_ACTION_MSG = f"CSV error: {e}"

    elif k == 'w':
        webbrowser.open(f"{API_BASE}/dashboard")
        LAST_ACTION_MSG = "Opened http://127.0.0.1:8000/dashboard in default browser."

    elif k == 't':
        live.stop()
        console.print("\n[bold cyan]>>> Interactive Task Submission[/bold cyan]")
        custom_name = console.input("[bold yellow]Enter Task Name (or press Enter to cancel): [/bold yellow]").strip()
        if custom_name:
            try:
                r = requests.post(f"{API_BASE}/api/task/submit", headers=headers, json={
                    "task_name": custom_name,
                    "payload": {"source": "Dashboard-TUI"}
                }, timeout=3)
                if r.status_code == 202:
                    LAST_ACTION_MSG = f"Submitted [{custom_name}] (ID: {r.json().get('task_id')})"
            except Exception as e:
                LAST_ACTION_MSG = f"Submission error: {e}"
        else:
            LAST_ACTION_MSG = "Custom task cancelled."
        live.start()

def main():
    console.print("[bold green] [SECURE] Initializing Interactive SovereignCore Matrix...[/bold green]")
    try:
        with Live(generate_layout(), refresh_per_second=4, console=console, screen=False) as live:
            while True:
                for _ in range(10):
                    if msvcrt.kbhit():
                        ch = msvcrt.getwch()
                        handle_keypress(ch, live)
                        live.update(generate_layout())
                    time.sleep(0.1)
                live.update(generate_layout())
    except KeyboardInterrupt:
        console.print("\n[bold yellow] [NOTICE] Matrix dashboard detached. Daemons remain operational.[/bold yellow]")
        sys.exit(0)

if __name__ == "__main__":
    main()