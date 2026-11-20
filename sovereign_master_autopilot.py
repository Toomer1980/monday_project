import os, sys, time, json, glob, math, shutil, subprocess, urllib.request
from datetime import datetime

ROOT = "C:/Users/toome/Desktop/SovereignCore"
VAULT = ROOT + "/Content_Vault_52Weeks"
LOG_FILE = ROOT + "/logs/master_autopilot.log"
CF_LOG = os.path.expandvars("%TEMP%/cf_tunnel.log")
URL_FILE = ROOT + "/CURRENT_STORE_URL.txt"
LEDGER_FILE = ROOT + "/uploaded_videos_ledger.json"
os.chdir(ROOT)
os.makedirs(ROOT + "/logs", exist_ok=True)
os.makedirs(VAULT, exist_ok=True)

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        open(LOG_FILE, "a", encoding="utf-8").write(line + chr(10))
    except Exception: pass

def ensure_daemon():
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/api/status", timeout=4) as r:
            if r.status == 200: return True
    except Exception:
        pass
    log("[HEAL] Port 8000 offline. Launching sovereign_daemon.py...")
    subprocess.Popen([sys.executable, ROOT + "/sovereign_daemon.py"], cwd=ROOT, creationflags=0x08000000)
    time.sleep(4)
    return True

def ensure_tunnel():
    cf_running = False
    try:
        out = subprocess.check_output(["tasklist", "/FI", "IMAGENAME eq cloudflared.exe"], text=True, creationflags=0x08000000)
        cf_running = "cloudflared.exe" in out
    except Exception: pass
    if not cf_running and os.path.exists(ROOT + "/cloudflared.exe"):
        log("[HEAL] Cloudflare tunnel down. Restarting cloudflared.exe...")
        try: os.remove(CF_LOG)
        except Exception: pass
        subprocess.Popen([ROOT + "/cloudflared.exe", "tunnel", "--url", "http://127.0.0.1:8000", "--logfile", CF_LOG], cwd=ROOT, creationflags=0x08000000)
        time.sleep(6)
    live_url = ""
    if os.path.exists(CF_LOG):
        for ln in open(CF_LOG, "r", encoding="utf-8", errors="ignore"):
            if ".trycloudflare.com" in ln:
                for part in ln.split():
                    if part.startswith("https://") and ".trycloudflare.com" in part:
                        live_url = part.strip()
    if live_url:
        store_url = live_url + "/store"
        prev = open(URL_FILE, "r", encoding="utf-8").read().strip() if os.path.exists(URL_FILE) else ""
        if store_url != prev:
            open(URL_FILE, "w", encoding="utf-8").write(store_url)
            log(f"[SYNC] Live public storefront URL updated: {store_url}")
            sync_promo_kit(store_url)
    return live_url

def sync_promo_kit(store_url):
    nl = chr(10)
    kit = nl.join([
        "========================================================================",
        "ORACLE SYSTEMS LLC // LIVE STOREFRONT & PROMO KIT (AUTO-SYNCED)",
        "========================================================================",
        "TIMELESS COLLECTIVE TAROT READING & ENERGY ALIGNMENT",
        "If this message found you today, there is no coincidence. Type I CLAIM THIS ALIGNMENT below.",
        "",
        f"- Full Oracle Systems Storefront : {store_url}",
        f"- 52-Week Collective Reading & Media Blueprint ($29.00) : {store_url}",
        f"- SovereignCore Pro Automation Node License ($99.00) : {store_url}",
        f"- Oracle Studio & Merchandising Automation Suite ($249.00) : {store_url}",
        "#TarotReading #CollectiveReading #EnergyUpdate #OracleSystems #SpiritualAwakening"
    ])
    open(ROOT + "/ORACLE_YOUTUBE_DESCRIPTION.txt", "w", encoding="utf-8").write(kit)

def replenish_content_if_low():
    uploaded = json.load(open(LEDGER_FILE, "r", encoding="utf-8")) if os.path.exists(LEDGER_FILE) else {}
    mp4s = sorted(glob.glob(VAULT + "/Week_*.mp4"))
    pending = [f for f in mp4s if os.path.basename(f) not in uploaded]
    if len(pending) >= 5: return
    next_num = len(mp4s) + 1
    slug = f"Week_{next_num:02d}_Sovereign_Alignment"
    log(f"[3D-AI-FACTORY] Queue low ({len(pending)} pending). Producing live 3D animated {slug}...")
    spoken = f"Welcome back to Oracle Systems Collective Tarot for Week {next_num}. If this message found you today, trust the timing. Old resistance is clearing out right now, making room for a tangible financial and spiritual opening over the next few days. Type I claim this alignment in the comments below, and visit our live storefront in the description for your own live 3D personalized reading and the complete fifty-two week blueprint."
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/generate", data=json.dumps({"model": "qwen2.5:0.5b", "prompt": f"Respond strictly in English. Write a warm 120-word collective tarot reading script for Week {next_num} focusing on financial breakthrough and alignment.", "stream": False, "keep_alive": "2m"}).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=25) as r:
            ai_txt = json.loads(r.read().decode("utf-8")).get("response", "").strip()
            clean = "".join(c if (32 <= ord(c) < 127) else " " for c in ai_txt)
            if len(clean) > 150: spoken = " ".join(clean.split())
    except Exception: pass
    try:
        import oracle_3d_renderer
        oracle_3d_renderer.render_3d_video(VAULT + "/" + slug + ".mp4", f"Week {next_num} Sovereign Alignment", "The Magician", "The Star", "Ace of Pentacles", spoken, kicker=f"ORACLE SYSTEMS // WEEK {next_num:02d}", mode="1080p")
        oracle_3d_renderer.render_3d_video(ROOT + "/Content_Vault_Shorts/Short_" + f"{next_num:02d}_Sovereign_Alignment.mp4", "Sovereign Alignment", "The Magician", "The Star", "Ace of Pentacles", spoken, kicker=f"URGENT MESSAGE // WEEK {next_num:02d}", mode="short")
        log(f"[3D-AI-FACTORY] Produced 3D long-form & 3D vertical Short for {slug}")
    except Exception as e:
        log(f"[3D-AI-FACTORY] Render error: {e}")

def backup_and_sync():
    bdir = ROOT + "/storage/backups/" + datetime.now().strftime("%Y%m%d_%H%M")
    os.makedirs(bdir, exist_ok=True)
    for db in glob.glob(ROOT + "/**/*.db", recursive=True):
        if "backups" not in db:
            try: shutil.copy2(db, bdir)
            except Exception: pass
    subprocess.run(["git", "add", "sovereign_daemon.py", "sovereign_master_autopilot.py", "autonomous_youtube_bot.py", "ORACLE_YOUTUBE_DESCRIPTION.txt"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
    subprocess.run(["git", "commit", "-m", "Autopilot self-sync checkpoint"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
    subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=0x08000000)
    log("[SYNC] Ledgers backed up and GitHub synced.")

def run_daily_youtube_drop():
    profile_cookies = ROOT + "/Edge_Autopilot_Profile/Default/Network/Cookies"
    if os.path.exists(profile_cookies) and os.path.exists(ROOT + "/autonomous_youtube_bot.py"):
        log("[PROMO] Triggering scheduled autonomous YouTube upload (2 videos)...")
        subprocess.Popen([sys.executable, ROOT + "/autonomous_youtube_bot.py", "2"], cwd=ROOT)

log("=== SOVEREIGNCORE MASTER AUTOPILOT ONLINE ===")
last_backup = 0
last_upload_day = ""
while True:
    ensure_daemon()
    ensure_tunnel()
    try:
        import sovereign_order_verifier as _sov
        if _sov.sync_recent_stripe_sales() > 0: log('[STRIPE-SYNC] Auto-fulfilled new paid Stripe orders.')
    except Exception: pass
    now = time.time()
    today = datetime.now().strftime("%Y-%m-%d")
    hour = datetime.now().hour
    if now - last_backup > 21600:
        try:
            import sovereign_evolution_engine as _evo
            _eres = _evo.run_evolution_cycle()
            log(f"[EVOLUTION] Gen {_eres.get('generation')} | Node: {_eres.get('compute_node')} | Healed: {_eres.get('healed_files')}")
        except Exception as _ee:
            log(f"[EVOLUTION] Cycle note: {_ee}")
        try:
            import sovereign_revenue_fulfillment as _srf
            _srf.process_pending_orders()
        except Exception: pass
        replenish_content_if_low()
        backup_and_sync()
        last_backup = now
    if hour == 18 and last_upload_day != today:
        run_daily_youtube_drop()
        last_upload_day = today
    time.sleep(30)
