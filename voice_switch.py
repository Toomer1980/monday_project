import sys, json
cfg_path = "C:/Users/toome/Desktop/SovereignCore/VOICE_CONFIG.json"
cfg = json.load(open(cfg_path, "r", encoding="utf-8"))
if len(sys.argv) > 1:
    mode = sys.argv[1].lower()
    if mode in ("neural", "custom"):
        cfg["mode"] = mode
        json.dump(cfg, open(cfg_path, "w", encoding="utf-8"), indent=2)
print(f"[+] Oracle Voice Mode Active: {cfg[\x27mode\x27].upper()} (Run \x27python voice_switch.py neural\x27 anytime to revert)")
