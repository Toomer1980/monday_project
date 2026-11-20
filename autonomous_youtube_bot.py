import os, sys, json, glob, time, subprocess
from playwright.sync_api import sync_playwright

root = "C:/Users/toome/Desktop/SovereignCore"
vault = root + "/Content_Vault_52Weeks"
ledger_file = root + "/uploaded_videos_ledger.json"
channel_id = "UCa-c8zShp_fB8o36nG2zolA"
os.chdir(root)

# 1. Detect live public storefront URL dynamically
store_url = "https://schema-julian-divorce-broadcasting.trycloudflare.com/store"
cf_log = os.path.expandvars("%TEMP%/cf_tunnel.log")
if os.path.exists(cf_log):
    for line in open(cf_log, "r", encoding="utf-8", errors="ignore"):
        if ".trycloudflare.com" in line:
            for part in line.split():
                if "https://" in part and ".trycloudflare.com" in part:
                    store_url = part.strip() + "/store"

# 2. Load upload ledger so we never duplicate a video
uploaded = {}
if os.path.exists(ledger_file):
    try:
        uploaded = json.load(open(ledger_file, "r", encoding="utf-8"))
    except Exception:
        uploaded = {}

mp4_files = sorted(glob.glob(vault + "/Week_*.mp4"))
pending = [f for f in mp4_files if os.path.basename(f) not in uploaded]
print(f"[+] Found {len(mp4_files)} total rendered videos | {len(pending)} pending upload.")
if not pending:
    print("[+] All 52 weeks are already published!")
    sys.exit(0)

# 3. Relaunch Microsoft Edge with Remote Debugging on Port 9222 using your logged-in profile
subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)
edge_paths = [
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "C:/Program Files/Microsoft/Edge/Application/msedge.exe"
]
edge_exe = next((p for p in edge_paths if os.path.exists(p)), "msedge.exe")
user_data = os.path.expandvars("%LOCALAPPDATA%/Microsoft/Edge/User Data")
subprocess.Popen([
    edge_exe,
    "--remote-debugging-port=9222",
    f"--user-data-dir={user_data}",
    "--profile-directory=Default",
    "--restore-last-session"
])
print("[*] Launching Microsoft Edge automation bridge on Port 9222...")
time.sleep(5)

# 4. Connect Playwright to Edge and autonomously upload batch (default: 2 videos per run)
max_per_run = int(sys.argv[1]) if len(sys.argv) > 1 else 2
batch = pending[:max_per_run]

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    context = browser.contexts[0]
    page = context.new_page()

    for mp4_path in batch:
        fn = os.path.basename(mp4_path)
        parts = os.path.splitext(fn)[0].split("_")
        wnum = parts[1]
        slug_title = " ".join(parts[2:])
        yt_title = f"URGENT COLLECTIVE TAROT READING (Week {wnum}): {slug_title} | Timeless Energy Alignment"[:98]
        nl = chr(10)
        yt_desc = nl.join([
            f"TIMELESS COLLECTIVE TAROT READING // WEEK {wnum}: {slug_title.upper()}",
            "If this message found you today, trust that the timing is real. Type I CLAIM THIS ALIGNMENT in the comments below to lock in this shift.",
            "",
            "INSTANT ACCESS & DIGITAL BLUEPRINTS (LIVE STOREFRONT):",
            f"-> Full Oracle Systems Storefront : {store_url}",
            f"-> 52-Week Collective Reading & Media Blueprint ($29.00) : {store_url}",
            f"-> SovereignCore Pro Automation Node License ($99.00) : {store_url}",
            f"-> Oracle Studio & Merchandising Automation Suite ($249.00) : {store_url}",
            "",
            "SUBSCRIBE & TURN ON NOTIFICATIONS for daily collective readings!",
            "#TarotReading #CollectiveReading #EnergyUpdate #OracleSystems #SpiritualAwakening"
        ])

        print(f"[*] Uploading {fn} -> {yt_title}")
        page.goto(f"https://studio.youtube.com/channel/{channel_id}/videos/upload?d=ud", timeout=60000)
        time.sleep(5)

        # Attach MP4 file directly to the hidden file input
        page.locator("input[type=\x27file\x27]").first.set_input_files(mp4_path)
        time.sleep(6)

        # Fill Title and Description boxes
        boxes = page.locator("#textbox")
        boxes.nth(0).click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        boxes.nth(0).fill(yt_title)
        time.sleep(1)

        boxes.nth(1).click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        boxes.nth(1).fill(yt_desc)
        time.sleep(2)

        # Select Not Made For Kids
        try:
            page.locator("tp-yt-paper-radio-button[name=\x27VIDEO_MADE_FOR_KIDS_NOT_MFK\x27]").click(timeout=8000)
        except Exception:
            pass
        time.sleep(1)

        # Click Next 3 times (Details -> Video Elements -> Checks -> Visibility)
        for _ in range(3):
            try:
                page.locator("#next-button").click(timeout=8000)
                time.sleep(2)
            except Exception:
                pass

        # Select Public visibility
        try:
            page.locator("tp-yt-paper-radio-button[name=\x27PUBLIC\x27]").click(timeout=8000)
        except Exception:
            pass
        time.sleep(2)

        # Click Publish / Done
        try:
            page.locator("#done-button").click(timeout=10000)
            print(f"[+] Successfully published {fn} to YouTube!")
            uploaded[fn] = {"title": yt_title, "published_at": time.strftime("%Y-%m-%d %H:%M:%S"), "store_url": store_url}
            json.dump(uploaded, open(ledger_file, "w", encoding="utf-8"), indent=2)
            time.sleep(10)
        except Exception as e:
            print(f"[!] Publish click note on {fn}: {e}")

    print("[+] Autonomous upload batch complete!")
