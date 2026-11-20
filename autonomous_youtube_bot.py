import os, sys, json, glob, time
from playwright.sync_api import sync_playwright

root = "C:/Users/toome/Desktop/SovereignCore"
vault = root + "/Content_Vault_52Weeks"
ledger_file = root + "/uploaded_videos_ledger.json"
profile_dir = root + "/Edge_Autopilot_Profile"
url_file = root + "/CURRENT_STORE_URL.txt"
channel_id = "UCa-c8zShp_fB8o36nG2zolA"
os.chdir(root)
os.makedirs(profile_dir, exist_ok=True)

store_url = open(url_file, "r", encoding="utf-8").read().strip() if os.path.exists(url_file) else "https://cents-extended-jewellery-samba.trycloudflare.com/store"
uploaded = json.load(open(ledger_file, "r", encoding="utf-8")) if os.path.exists(ledger_file) else {}
mp4_files = sorted(glob.glob(vault + "/Week_*.mp4"))
pending = [f for f in mp4_files if os.path.basename(f) not in uploaded]
max_per_run = int(sys.argv[1]) if len(sys.argv) > 1 else 5
batch = pending[:max_per_run]
print(f"[+] Storefront: {store_url}")
print(f"[+] Vault: {len(mp4_files)} total | {len(pending)} pending | Publishing {len(batch)} now...")
if not batch:
    sys.exit(0)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir,
        channel="msedge",
        headless=False,
        args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
        no_viewport=True
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto(f"https://studio.youtube.com/channel/{channel_id}/videos/upload?d=ud", timeout=60000)
    time.sleep(4)

    if "accounts.google.com" in page.url or "signin" in page.url.lower():
        print("[!] SIGN IN ONCE inside the open Edge window (do not press Ctrl+C). Waiting up to 5 minutes...")
        for _ in range(150):
            if "studio.youtube.com" in page.url and "signin" not in page.url.lower():
                print("[+] YouTube Studio session authenticated and saved permanently!")
                break
            time.sleep(2)

    for mp4_path in batch:
        fn = os.path.basename(mp4_path)
        thumb_path = mp4_path.replace(".mp4", "_canvas.png")
        parts = os.path.splitext(fn)[0].split("_")
        wnum = parts[1]
        slug_title = " ".join(parts[2:])
        yt_title = f"URGENT COLLECTIVE TAROT READING (Week {wnum}): {slug_title} | Timeless Energy Alignment"[:98]
        nl = chr(10)
        yt_desc = nl.join([
            f"TIMELESS COLLECTIVE TAROT READING // WEEK {wnum}: {slug_title.upper()}",
            "If this message found you today, trust that the timing is real. Type I CLAIM THIS ALIGNMENT in the comments below.",
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
        page.locator("input[type='file']").first.set_input_files(mp4_path)
        time.sleep(8)

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

        if os.path.exists(thumb_path):
            try:
                page.locator("input#file-loader").set_input_files(thumb_path, timeout=6000)
                print(f"    [+] Custom 1080p thumbnail attached: {os.path.basename(thumb_path)}")
                time.sleep(2)
            except Exception: pass

        try: page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").click(timeout=8000)
        except Exception: pass
        time.sleep(1)

        for _ in range(3):
            try:
                page.locator("#next-button").click(timeout=8000)
                time.sleep(2)
            except Exception: pass

        try: page.locator("tp-yt-paper-radio-button[name='PUBLIC']").click(timeout=8000)
        except Exception: pass
        time.sleep(2)

        try:
            page.locator("#done-button").click(timeout=10000)
            print(f"[+] PUBLISHED LIVE: {fn}")
            uploaded[fn] = {"title": yt_title, "published_at": time.strftime("%Y-%m-%d %H:%M:%S"), "store_url": store_url}
            json.dump(uploaded, open(ledger_file, "w", encoding="utf-8"), indent=2)
            time.sleep(10)
        except Exception as e:
            print(f"[!] Publish step note on {fn}: {e}")

    print("[+] Autonomous upload batch complete!")
    context.close()
