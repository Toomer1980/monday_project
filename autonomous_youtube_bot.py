import os, sys, json, glob, time
from playwright.sync_api import sync_playwright

root = "C:/Users/toome/Desktop/SovereignCore"
vault = root + "/Content_Vault_52Weeks"
shorts_dir = root + "/Content_Vault_Shorts"
ledger_file = root + "/uploaded_videos_ledger.json"
profile_dir = root + "/Edge_Autopilot_Profile"
url_file = root + "/CURRENT_STORE_URL.txt"
channel_id = "UC_UH7CHyWHxIdzsDGm9R4nw"
os.chdir(root)
os.makedirs(profile_dir, exist_ok=True)

store_url = open(url_file, "r", encoding="utf-8").read().strip() if os.path.exists(url_file) else "https://cents-extended-jewellery-samba.trycloudflare.com/store"
uploaded = json.load(open(ledger_file, "r", encoding="utf-8")) if os.path.exists(ledger_file) else {}

def complete_publish_dialog(page, label):
    for dismiss_txt in ["Cancel", "Close", "Dismiss"]:
        try:
            dlg = page.locator("ytcp-dialog").filter(has_text="Verify")
            if dlg.count() > 0:
                dlg.get_by_text(dismiss_txt).first.click(timeout=2000)
                time.sleep(1)
        except Exception: pass
    try:
        nfk = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").first
        nfk.scroll_into_view_if_needed(timeout=8000)
        nfk.click(force=True, timeout=8000)
        time.sleep(1)
    except Exception: pass
    try:
        page.locator("#step-badge-3").click(timeout=6000)
        time.sleep(2)
    except Exception:
        for _ in range(3):
            try:
                page.locator("#next-button").click(timeout=5000)
                time.sleep(1.5)
            except Exception: pass
    try:
        pub = page.locator("tp-yt-paper-radio-button[name='PUBLIC']").first
        pub.scroll_into_view_if_needed(timeout=8000)
        pub.click(force=True, timeout=8000)
        time.sleep(2)
    except Exception: pass
    done = page.locator("#done-button").first
    done.wait_for(state="visible", timeout=20000)
    for _ in range(20):
        if done.get_attribute("aria-disabled") != "true":
            break
        time.sleep(1)
    done.click(timeout=15000)
    print(f"[+] PUBLISHED LIVE: {label}")
    time.sleep(6)
    try: page.locator("#close-button").first.click(timeout=4000)
    except Exception: pass
    time.sleep(2)

def upload_video(page, mp4_path, is_short=False):
    fn = os.path.basename(mp4_path)
    parts = os.path.splitext(fn)[0].split("_")
    wnum = parts[1]
    slug_title = " ".join(parts[2:])
    nl = chr(10)
    if is_short:
        yt_title = f"URGENT TAROT MESSAGE: {slug_title} #shorts #tarot #manifestation"[:98]
    else:
        yt_title = f"URGENT COLLECTIVE TAROT READING (Week {wnum}): {slug_title} | Timeless Energy Alignment"[:98]
    yt_desc = nl.join([
        f"TIMELESS COLLECTIVE TAROT READING // WEEK {wnum}: {slug_title.upper()}",
        "If this message found you today, trust the timing. Type I CLAIM THIS ALIGNMENT below.",
        "",
        "INSTANT ACCESS & DIGITAL BLUEPRINTS (LIVE STOREFRONT):",
        f"-> Full Oracle Systems Storefront : {store_url}",
        f"-> 52-Week Collective Reading & Media Blueprint ($29.00) : {store_url}",
        f"-> SovereignCore Pro Automation Node License ($99.00) : {store_url}",
        f"-> Oracle Studio & Merchandising Automation Suite ($249.00) : {store_url}",
        "",
        "#shorts #TarotReading #CollectiveReading #EnergyUpdate #OracleSystems #SpiritualAwakening"
    ])
    print(f"[*] Uploading {fn} -> {yt_title}")
    page.goto(f"https://studio.youtube.com/channel/{channel_id}/videos/upload?d=ud", wait_until="domcontentloaded", timeout=60000)
    page.locator("input[type='file']").first.wait_for(state="attached", timeout=25000)
    page.locator("input[type='file']").first.set_input_files(mp4_path)
    page.locator("#textbox").first.wait_for(state="visible", timeout=30000)
    time.sleep(3)
    boxes = page.locator("#textbox")
    boxes.nth(0).click(); page.keyboard.press("Control+A"); page.keyboard.press("Backspace"); boxes.nth(0).fill(yt_title)
    time.sleep(1)
    boxes.nth(1).click(); page.keyboard.press("Control+A"); page.keyboard.press("Backspace"); boxes.nth(1).fill(yt_desc)
    time.sleep(2)
    complete_publish_dialog(page, fn)
    uploaded[fn] = {"title": yt_title, "type": "short" if is_short else "long", "channel_id": channel_id, "published_at": time.strftime("%Y-%m-%d %H:%M:%S"), "store_url": store_url}
    json.dump(uploaded, open(ledger_file, "w", encoding="utf-8"), indent=2)

mode = sys.argv[1] if len(sys.argv) > 1 else "daily"
count = int(sys.argv[2]) if len(sys.argv) > 2 else (int(mode) if mode.isdigit() else 2)

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=profile_dir, channel="msedge", headless=False,
        args=["--disable-blink-features=AutomationControlled", "--start-maximized"], no_viewport=True
    )
    page = context.pages[0] if context.pages else context.new_page()
    long_pending = [f for f in sorted(glob.glob(vault + "/Week_*.mp4")) if os.path.basename(f) not in uploaded]
    short_pending = [f for f in sorted(glob.glob(shorts_dir + "/Short_*.mp4")) if os.path.basename(f) not in uploaded]
    if mode == "shorts":
        for sp in short_pending[:count]: upload_video(page, sp, is_short=True)
    elif mode == "daily":
        for lp in long_pending[:1]: upload_video(page, lp, is_short=False)
        for sp in short_pending[:1]: upload_video(page, sp, is_short=True)
    elif mode.isdigit():
        for lp in long_pending[:count]: upload_video(page, lp, is_short=False)
    context.close()
