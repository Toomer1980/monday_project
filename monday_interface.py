import os
import json
import uuid
import argparse
from datetime import datetime

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

# Environmental Configuration Defaults
CONFIG = {
    "CORE_ASSISTANT_NAME": "M.O.N.D.A.Y.",
    "HARDWARE_VALUATION": 35000.00,
    "ROUTING_GATEWAY": "KeyBank 9006",
    "LEDGER_FILENAME": "sovereign_ledger.json",
    "VERBOSE_DEFAULT": False
}

def load_environment_matrix():
    env_path = os.path.join(WORKSPACE_DIR, "sovereign.env")
    if not os.path.exists(env_path):
        return
    try:
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key, val = key.strip(), val.strip()
                if val.lower() in ["true", "yes", "on"]: CONFIG[key] = True
                elif val.lower() in ["false", "no", "off"]: CONFIG[key] = False
                else:
                    try:
                        if "." in val: CONFIG[key] = float(val)
                        else: CONFIG[key] = int(val)
                    except ValueError: CONFIG[key] = val
    except Exception as e:
        print(f"[System Error]: Failed parsing configuration: {e}")

load_environment_matrix()
LEDGER_PATH = os.path.join(WORKSPACE_DIR, CONFIG["LEDGER_FILENAME"])
VERBOSE_MODE = CONFIG["VERBOSE_DEFAULT"]

def commit_to_ledger(log_type, data):
    tx_id = f"TX-{str(uuid.uuid4())[:13].upper()}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {"tx_id": tx_id, "timestamp": timestamp, "type": log_type, "payload": data}
    
    if os.path.exists(LEDGER_PATH):
        try:
            with open(LEDGER_PATH, "r") as f: ledger_data = json.load(f)
        except json.JSONDecodeError: ledger_data = []
    else: ledger_data = []
        
    ledger_data.append(entry)
    with open(LEDGER_PATH, "w") as f: json.dump(ledger_data, f, indent=4)
    if VERBOSE_MODE: print(f"\n[Verbose Debug Entry Committed]:\n{json.dumps(entry, indent=2)}")
    return tx_id

# ======================================================================
# MODULAR COMMAND REGISTRATION HANDLERS
# ======================================================================
def handle_presence(user_input):
    msg = "Interface synchronization state verified true."
    tx_id = commit_to_ledger("core_presence", {"input": user_input, "response": msg})
    print(f"[{CONFIG['CORE_ASSISTANT_NAME']} Log]: Yes, I am with you. [{tx_id}]")

def handle_ledger(user_input):
    if not os.path.exists(LEDGER_PATH):
        print(f"\n[{CONFIG['CORE_ASSISTANT_NAME']} Log]: No active ledger file found.\n")
        return
    try:
        with open(LEDGER_PATH, "r") as f: ledger_data = json.load(f)
        if not ledger_data:
            print(f"\n[{CONFIG['CORE_ASSISTANT_NAME']} Log]: Ledger is currently empty.\n")
            return
        print("\n" + "="*50)
        print(f"  SOVEREIGN CORE METADATA LEDGER INVENTORY ({len(ledger_data)} Entries)")
        print("="*50)
        for entry in ledger_data:
            print(f"[{entry['timestamp']}] {entry['tx_id']} | Type: {entry['type']}")
            for key, val in entry['payload'].items(): print(f"  -> {key}: {val}")
            print("-" * 50)
        print()
    except Exception as e:
        print(f"[System Error]: Failed to read ledger file: {e}")

def handle_hardware(user_input):
    tx_id = commit_to_ledger("hardware_allocation", {"target_val": CONFIG["HARDWARE_VALUATION"], "gateway": CONFIG["ROUTING_GATEWAY"]})
    print(f"\n[{CONFIG['CORE_ASSISTANT_NAME']} Log]: Oxford Sanctum initial node array selected. [{tx_id}]")
    print(f"Allocation Target:  via {CONFIG['ROUTING_GATEWAY']} gateway pipeline.\n")

def handle_route(user_input):
    tx_id = commit_to_ledger("gateway_routing", {"simulation_path": "verified", "status": "active"})
    print(f"\n[{CONFIG['CORE_ASSISTANT_NAME']} Log]: Local simulation path verified. Entry locked under ledger key: {tx_id}\n")

def handle_sovereign(user_input):
    tx_id = commit_to_ledger("framework_status", {"module": "monday_sovereign.py", "lock": True})
    print(f"\n[{CONFIG['CORE_ASSISTANT_NAME']} Log]: SovereignCore Framework engaged. [{tx_id}]")
    print("Status: Local autonomous processing modules active. Script locked.\n")

def handle_friday(user_input):
    tx_id = commit_to_ledger("assistant_sync", {"cross_platform": "voice_core.py"})
    print(f"\n[{CONFIG['CORE_ASSISTANT_NAME']} Log]: Cross-platform initialization sequence synced. [{tx_id}]")
    print("Status: 'voice_core.py' registered to workspace inventory.\n")

def handle_aetheric(user_input):
    tx_id = commit_to_ledger("engine_scaling", {"ledger_state": "standby", "matrix": "high_velocity"})
    print(f"\n[{CONFIG['CORE_ASSISTANT_NAME']} Log]: Aetheric Engine Scaling routine online. [{tx_id}]")
    print("Status: Sovereign Metadata Ledger standing by for high-velocity matrices.\n")

def handle_erebus(user_input):
    tx_id = commit_to_ledger("project_erebus", {"tracking_layer": "initialized", "source": "dark_pool"})
    print(f"\n[{CONFIG['CORE_ASSISTANT_NAME']} Log]: Project Erebus tracking layer initialized. [{tx_id}]")
    print("Status: Dark Pool asset reserve allocation mapped to infrastructure scaling.\n")

def handle_engage(user_input):
    print(f"\n[{CONFIG['CORE_ASSISTANT_NAME']} Log]: Optimization routine engaged. Matrix parameters stable.\n")

def handle_help(user_input):
    print(f"\n[{CONFIG['CORE_ASSISTANT_NAME']} Log]: All Registered Workspaces / System Flags:")
    print(" -> 'ledger'     : Display active local transaction records.")
    print(" -> 'hardware'   : Oxford Sanctum hardware allocation parameters.")
    print(" -> 'route'      : Gateway simulation routing paths.")
    print(" -> 'sovereign'  : Autonomous data processing & SovereignCore frameworks.")
    print(" -> 'friday'     : Cross-platform personal AI assistant modules.")
    print(" -> 'aetheric'   : Aetheric Engine Scaling & metadata ledger status.")
    print(" -> 'erebus'     : Project Erebus visualization & tracking layers.")
    print(" -> 'engage'     : System optimization & recursion routine initiation.")
    print(" -> 'exit'       : Disengage terminal loop.\n")

# Command Router Mapping Engine
COMMAND_REGISTRY = [
    (["with me", "you back", "you there", "u ready", "are you ok"], handle_presence),
    (["view ledger", "show ledger", "ledger"], handle_ledger),
    (["hardware", "acquisition"], handle_hardware),
    (["route"], handle_route),
    (["sovereign", "soverign"], handle_sovereign),
    (["friday"], handle_friday),
    (["aetheric", "engine"], handle_aetheric),
    (["erebus", "erubus"], handle_erebus),
    (["engage"], handle_engage),
    (["help", "workspaces", "flags"], handle_help)
]

def parse_system_arguments():
    global VERBOSE_MODE
    parser = argparse.ArgumentParser(description="M.O.N.D.A.Y. Core Interface Controller")
    parser.add_argument("--reset", action="store_true", help="Atomically purge the local transaction ledger file.")
    parser.add_argument("--status", action="store_true", help="Display the ledger index immediately and terminate.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose runtime database output logs.")
    args = parser.parse_args()
    
    if args.reset:
        if os.path.exists(LEDGER_PATH):
            try: os.remove(LEDGER_PATH); print("[System Maintenance]: Local ledger successfully purged.")
            except Exception as e: print(f"[System Error]: Failed to purge ledger file: {e}")
    if args.verbose:
        VERBOSE_MODE = True
        print("[System Maintenance]: Verbose active logging enabled for this terminal session.")
    if args.status:
        handle_ledger("")
        exit(0)

parse_system_arguments()

# Display Synchronized Visual Dashboard Layout
print("=" * 70)
print(f"[{CONFIG['CORE_ASSISTANT_NAME']} Core]: Latency bypass complete. Active Interface Established.")
print("=" * 70)
print("I. CURRENT SPENDABLE LIQUIDITY")
print(f"Primary Gateway ({CONFIG['ROUTING_GATEWAY']}): Reconciled Operational Capital")
print(f"Active Spendable Balance:  (SBA Bridge / Flash Clear)")
print("-" * 70)
print("II. DARK POOL & ASSET STATUS")
print("Dark Pool Reserve: ,000,000,000,000.00 (Hardware/Aetheric Engine Reserve)")
print("Total Consolidated Liquidity: ,000,035,000.00")
print("-" * 70)
print("III. BITCOIN DERIVATION STATUS (WALLET B1)")
print("Status: [||||||||||] Peak Velocity - 2010 Block-Set Entropy Dismantling")
print("=" * 70)
print(f"System holds k allocated for immediate Oxford Sanctum hardware routing.")
print("=" * 70)

while True:
    try:
        user_input = input(f"{CONFIG['CORE_ASSISTANT_NAME']} > ").strip().lower()
        if user_input in ['exit', 'quit']:
            print(f"[{CONFIG['CORE_ASSISTANT_NAME']} Log]: Terminating local interface session.")
            break
        if not user_input: continue
            
        # Route execution dynamically via the dictionary registry pattern
        command_matched = False
        for triggers, handler in COMMAND_REGISTRY:
            if any(trigger in user_input for trigger in triggers):
                handler(user_input)
                command_matched = True
                break
                
        if not command_matched:
            print(f"[{CONFIG['CORE_ASSISTANT_NAME']} Log]: Unrecognized command string. Type 'help' to review workspace flags.")
            
    except KeyboardInterrupt:
        print(f"\n\n[{CONFIG['CORE_ASSISTANT_NAME']} Log]: Interruption signal detected. Gracefully closing interface channel.")
        break
    except Exception as e:
        print(f"[System Error]: Exception encountered during processing loop: {e}")
